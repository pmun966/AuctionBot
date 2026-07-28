import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
import re
import time
import os
from datetime import datetime, timezone

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("ไม่พบ BOT_TOKEN ใน Environment Variables! กรุณาตั้งค่าใน Railway Settings")

ALLOWED_USER_ID = 933529869487321161  
AUCTION_CATEGORY_ID = 1531512841494855790  
PAYMENT_CATEGORY_ID = 1531512976480403556  
# =======================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------------------------------
# DATABASE INITIALIZATION
# ----------------------------------------------------
async def init_db():
    async with aiosqlite.connect("auctions_v5.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_auctions (
                channel_id INTEGER PRIMARY KEY,
                message_id INTEGER,
                seller_id INTEGER,
                item_name TEXT,
                start_price INTEGER,
                target_price INTEGER,
                min_step INTEGER,
                current_price INTEGER,
                highest_bidder_id INTEGER,
                highest_bidder_name TEXT,
                end_time INTEGER,
                image_url TEXT,
                status TEXT
            )
        """)
        await db.commit()

# Helper Embed สำหรับห้องประมูล
def build_auction_embed(item_name, start_price, target_price, min_step, current_price, seller_id, bidder_name, bidder_id, end_time, image_url=None, status="🟢 กำลังประมูล"):
    embed = discord.Embed(
        title=f"📢 เปิดประมูล: {item_name}",
        color=discord.Color.green() if "กำลัง" in status else discord.Color.red(),
        timestamp=datetime.now(timezone.utc)
    )
    if image_url:
        embed.set_image(url=image_url)
        
    embed.add_field(name="👤 เจ้าของประมูล", value=f"<@{seller_id}>", inline=True)
    embed.add_field(name="🏷️ ราคาเริ่มต้น", value=f"{start_price:,} บาท", inline=True)
    embed.add_field(name="🎯 ยอดที่เล็งไว้ (Target)", value=f"{target_price:,} บาท" if target_price > 0 else "ไม่มี", inline=True)
    
    embed.add_field(name="📈 บิดขั้นต่ำครั้งละ", value=f"+{min_step:,} บาท", inline=True)
    embed.add_field(name="💰 ราคาปัจจุบัน", value=f"**{current_price:,}** บาท", inline=True)
    
    bidder_display = f"{bidder_name} (<@{bidder_id}>)" if bidder_id else "ยังไม่มีผู้ประมูล"
    embed.add_field(name="👑 ผู้นำประมูลปัจจุบัน", value=bidder_display, inline=False)
    
    embed.add_field(name="⏳ เวลาสิ้นสุด", value=f"<t:{end_time}:F> (<t:{end_time}:R>)", inline=False)
    embed.set_footer(text="💬 พิมพ์ '[ชื่อ] [ราคา]' ในห้องนี้เพื่อร่วมประมูล เช่น: เบล 150")
    return embed

# ----------------------------------------------------
# MODAL: แบบฟอร์มกรอกข้อมูลประมูล (Popup)
# ----------------------------------------------------
class CreateAuctionModal(discord.ui.Modal, title="📝 สร้างการประมูลใหม่"):
    item_name = discord.ui.TextInput(label="ชื่อสินค้า", placeholder="เช่น ดาบเพชร / ไอดีเกม", required=True)
    start_price = discord.ui.TextInput(label="ราคาเริ่มต้น (บาท)", placeholder="เช่น 100", required=True)
    min_step = discord.ui.TextInput(label="บิดขั้นต่ำครั้งละ (บาท)", placeholder="เช่น 10", required=True)
    duration_min = discord.ui.TextInput(label="ระยะเวลาประมูล (นาที)", placeholder="เช่น 30", required=True)
    target_price = discord.ui.TextInput(label="ยอดที่เล็งไว้ (ใส่ 0 ถ้าไม่มี)", placeholder="เช่น 500", default="0", required=False)
    image_url = discord.ui.TextInput(label="ลิงก์รูปภาพสินค้า (URL ออปชันเสริม)", placeholder="https://i.imgur.com/...", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            val_start = int(self.start_price.value)
            val_step = int(self.min_step.value)
            val_dur = int(self.duration_min.value)
            val_target = int(self.target_price.value) if self.target_price.value else 0
        except ValueError:
            await interaction.response.send_message("❌ กรุณากรอก ตัวเลข ให้ถูกต้องในช่องราคาและเวลา!", ephemeral=True)
            return

        img = self.image_url.value.strip() if self.image_url.value else None
        guild = interaction.guild
        auction_cat = guild.get_channel(AUCTION_CATEGORY_ID)

        if not auction_cat:
            await interaction.response.send_message("❌ ไม่พบ Category สำหรับสร้างห้องประมูล กรุณาเช็ก ID หมวดหมู่!", ephemeral=True)
            return

        # ตอบกลับชั่วคราวก่อนเริ่มสร้างช่อง
        await interaction.response.send_message("⏳ กำลังสร้างห้องประมูล...", ephemeral=True)

        # 1. สร้างห้องประมูลใหม่ใน Zone ประมูล
        channel_name = f"🔨-{self.item_name.value}"[:30]
        new_channel = await guild.create_text_channel(name=channel_name, category=auction_cat)

        end_time = int(time.time()) + (val_dur * 60)

        # 2. ส่ง Embed ไปยังห้องประมูลใหม่
        embed = build_auction_embed(
            item_name=self.item_name.value,
            start_price=val_start,
            target_price=val_target,
            min_step=val_step,
            current_price=val_start,
            seller_id=interaction.user.id,
            bidder_name="",
            bidder_id=None,
            end_time=end_time,
            image_url=img
        )

        msg = await new_channel.send(content=f"🎉 **เปิดการประมูลสินค้า {self.item_name.value}!**", embed=embed)

        # 3. บันทึกลง SQLite
        async with aiosqlite.connect("auctions_v5.db") as db:
            await db.execute("""
                INSERT INTO active_auctions 
                (channel_id, message_id, seller_id, item_name, start_price, target_price, min_step, current_price, highest_bidder_id, highest_bidder_name, end_time, image_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, '', ?, ?, 'ACTIVE')
            """, (new_channel.id, msg.id, interaction.user.id, self.item_name.value, val_start, val_target, val_step, val_start, end_time, img))
            await db.commit()

        await interaction.edit_original_response(content=f"✅ สร้างห้องประมูลเรียบร้อยแล้วที่ {new_channel.mention}")

# ----------------------------------------------------
# VIEW: ปุ่มกดหน้าแผงควบคุม
# ----------------------------------------------------
class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # persistent view

    @discord.ui.button(label="➕ เปิดการประมูลใหม่", style=discord.ButtonStyle.primary, custom_id="btn_panel_create_v2")
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ส่ง Modal โดยตรงทันที ป้องกัน Interaction Timeout
        await interaction.response.send_modal(CreateAuctionModal())

# ----------------------------------------------------
# EVENT: ดักจับการบิดประมูล (พิมพ์ ชื่อ ราคา)
# ----------------------------------------------------
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    async with aiosqlite.connect("auctions_v5.db") as db:
        async with db.execute("SELECT * FROM active_auctions WHERE channel_id = ? AND status = 'ACTIVE'", (message.channel.id,)) as cursor:
            row = await cursor.fetchone()

    if not row:
        await bot.process_commands(message)
        return

    (channel_id, message_id, seller_id, item_name, start_price, target_price, 
     min_step, current_price, highest_bidder_id, highest_bidder_name, end_time, image_url, status) = row

    now_ts = int(time.time())
    if now_ts >= end_time:
        return

    match = re.search(r"^(.+?)\s+(\d+)$", message.content.strip())
    if match:
        input_name = match.group(1)
        bid_amount = int(match.group(2))

        if message.author.id == seller_id:
            await message.reply("❌ คุณเป็นเจ้าของประมูล ไม่สามารถร่วมบิดได้ครับ", delete_after=5)
            return

        required_price = current_price + min_step if highest_bidder_id else start_price

        if bid_amount < required_price:
            await message.reply(f"❌ ราคาบิดต้องไม่ต่ำกว่า **{required_price:,}** บาท!", delete_after=5)
            return

        previous_bidder_id = highest_bidder_id
        
        time_left = end_time - now_ts
        is_extended = False
        new_end_time = end_time

        if time_left <= 600:
            new_end_time += 600
            is_extended = True

        async with aiosqlite.connect("auctions_v5.db") as db:
            await db.execute("""
                UPDATE active_auctions 
                SET current_price = ?, highest_bidder_id = ?, highest_bidder_name = ?, end_time = ?
                WHERE channel_id = ?
            """, (bid_amount, message.author.id, input_name, new_end_time, channel_id))
            await db.commit()

        reply_msg = f"✅ คุณ **{input_name}** ({message.author.mention}) เสนอราคาที่ **{bid_amount:,}** บาท!"
        if is_extended:
            reply_msg += f"\n⏳ **ต่อเวลาอัตโนมัติ!** เพิ่มให้อีก 10 นาที (ปิดที่ <t:{new_end_time}:t>)"
        if previous_bidder_id and previous_bidder_id != message.author.id:
            reply_msg += f"\n⚠️ <@{previous_bidder_id}> มีคนเสนอราคาสูงกว่าคุณแล้ว!"

        await message.reply(reply_msg)

        try:
            main_msg = await message.channel.fetch_message(message_id)
            updated_embed = build_auction_embed(
                item_name=item_name, start_price=start_price, target_price=target_price,
                min_step=min_step, current_price=bid_amount, seller_id=seller_id,
                bidder_name=input_name, bidder_id=message.author.id,
                end_time=new_end_time, image_url=image_url
            )
            await main_msg.edit(embed=updated_embed)
        except Exception as e:
            print(f"Error updating embed: {e}")

    await bot.process_commands(message)

# ----------------------------------------------------
# LOOP: ปิดประมูล + ย้ายไป Zone จ่ายเงิน
# ----------------------------------------------------
async def auction_checker():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            now = int(time.time())
            async with aiosqlite.connect("auctions_v5.db") as db:
                async with db.execute("SELECT * FROM active_auctions WHERE status = 'ACTIVE' AND end_time <= ?", (now,)) as cursor:
                    expired_auctions = await cursor.fetchall()

            for auction in expired_auctions:
                (channel_id, message_id, seller_id, item_name, start_price, target_price, 
                 min_step, current_price, highest_bidder_id, highest_bidder_name, end_time, image_url, status) = auction

                async with aiosqlite.connect("auctions_v5.db") as db:
                    await db.execute("UPDATE active_auctions SET status = 'ENDED' WHERE channel_id = ?", (channel_id,))
                    await db.commit()

                channel = bot.get_channel(channel_id)
                if channel:
                    guild = channel.guild

                    if highest_bidder_id:
                        winner = guild.get_member(highest_bidder_id)
                        seller = guild.get_member(seller_id)
                        pay_category = guild.get_channel(PAYMENT_CATEGORY_ID)

                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            winner: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        }
                        if seller:
                            overwrites[seller] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

                        pay_room_name = f"💳-{highest_bidder_name}-{item_name}"[:30]
                        pay_channel = await guild.create_text_channel(
                            name=pay_room_name,
                            category=pay_category,
                            overwrites=overwrites
                        )

                        pay_embed = discord.Embed(
                            title=f"💳 สรุปรายการประมูลจบแล้ว: {item_name}",
                            description="ห้องนี้เห็นเฉพาะ **Admin, ผู้ขาย และ ผู้ชนะ** เพื่อส่งมอบของและจ่ายเงินครับ",
                            color=discord.Color.gold(),
                            timestamp=datetime.now(timezone.utc)
                        )
                        if image_url:
                            pay_embed.set_thumbnail(url=image_url)

                        pay_embed.add_field(name="📦 สินค้า", value=item_name, inline=True)
                        pay_embed.add_field(name="💰 ราคาสุดท้าย", value=f"**{current_price:,}** บาท", inline=True)
                        pay_embed.add_field(name="👑 ผู้ชนะ", value=f"{winner.mention} (ชื่อบิด: **{highest_bidder_name}**)", inline=False)
                        pay_embed.add_field(name="👤 เจ้าของประมูล", value=f"<@{seller_id}>", inline=False)

                        await pay_channel.send(content=f"🔔 แจ้งเตือน: {winner.mention} | <@{seller_id}>", embed=pay_embed)

                        await asyncio.sleep(3)
                        await channel.delete(reason="จบการประมูลแล้ว ย้ายไปห้องจ่ายเงิน")
                    else:
                        await channel.send("🔴 **ปิดการประมูล** (ไม่มีผู้เสนอราคา ห้องนี้จะถูกลบใน 10 วินาที)")
                        await asyncio.sleep(10)
                        await channel.delete()

        except Exception as e:
            print(f"Auction loop error: {e}")

        await asyncio.sleep(5)

# ----------------------------------------------------
# COMMAND: ติดตั้งแผงควบคุม (/setup_panel)
# ----------------------------------------------------
@bot.tree.command(name="setup_panel", description="ตั้งค่าแผงควบคุมสร้างประมูลในห้องนี้ (เฉพาะเจ้าของบอท)")
async def setup_panel(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ **คุณไม่มีสิทธิ์ใช้คำสั่งนี้!**", ephemeral=True)
        return

    embed = discord.Embed(
        title="🔨 แผงควบคุมระบบประมูล",
        description="กดปุ่มด้านล่างเพื่อเปิดสร้างห้องประมูลสินค้าใหม่",
        color=discord.Color.blue()
    )
    embed.set_footer(text="ระบบประมูลอัตโนมัติ")
    
    await interaction.response.send_message("✅ ติดตั้งแผงควบคุมสำเร็จ!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=PanelView())

# ----------------------------------------------------
# ON READY
# ----------------------------------------------------
@bot.event
async def on_ready():
    await init_db()
    bot.add_view(PanelView()) # ลงทะเบียน View ปุ่มถาวร
    await bot.tree.sync()
    bot.loop.create_task(auction_checker())
    print(f"✅ บอทประมูลพร้อมทำงานในชื่อ {bot.user}")

bot.run(BOT_TOKEN)
