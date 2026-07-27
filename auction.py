import discord
import time

from discord.ext import commands

from database import (
    get_active_auction,
    add_bid,
    update_price
)

from utils.parser import parse_bid
from utils.embeds import auction_embed


class Auction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_auction_embed(
        self,
        channel: discord.TextChannel,
        auction,
        bidder: discord.Member,
        price: int
    ):

        try:
            message = await channel.fetch_message(
                auction["message_id"]
            )
        except:
            return

        bid_count = auction.get("bid_count", 0) + 1
        participant = auction.get("participant_count", 1)

        highest = bidder.mention

        embed = auction_embed(
            item_name=auction["item_name"],
            description=auction["description"],
            image=auction["image"],
            start_price=auction["start_price"],
            current_price=price,
            minimum_bid=auction["minimum_bid"],
            highest_bidder=highest,
            bid_count=bid_count,
            participant_count=participant,
            minutes_left=10,
            percent=80
        )

        await message.edit(embed=embed)
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # ไม่อ่านข้อความจากบอท
        if message.author.bot:
            return

        # ตรวจว่าข้อความเป็นตัวเลขหรือไม่
        bid = parse_bid(message.content)

        if bid is None:
            return

        # ดึงการประมูลที่เปิดอยู่ในห้องนี้
        auction = await get_active_auction(message.channel.id)

        if auction is None:
            return

        # ลบข้อความการบิดราคา
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        # ห้ามบิดต่อราคาตัวเอง
        if auction["highest_bidder"] == message.author.id:

            return await message.channel.send(
                f"❌ {message.author.mention} คุณเป็นผู้นำการประมูลอยู่แล้ว",
                delete_after=5
            )

        # ราคาขั้นต่ำที่ต้องบิด
        minimum_price = (
            auction["current_price"] +
            auction["minimum_bid"]
        )

        # ตรวจขั้นต่ำ
        if bid < minimum_price:

            return await message.channel.send(
                f"❌ ราคาต้องไม่น้อยกว่า **{minimum_price:,} บาท**",
                delete_after=5
            )

        # กันบิดเกินหลักล้าน (แก้ไขได้ภายหลัง)
        if bid > 999999999:

            return await message.channel.send(
                "❌ ราคาเกินกำหนด",
                delete_after=5
            )

        # บันทึกการบิด
        await add_bid(
            auction["id"],
            message.author.id,
            bid,
            int(time.time())
        )

        # อัปเดตราคา
        await update_price(
            auction["id"],
            bid,
            message.author.id
        )

        # อัปเดต Embed
        await self.update_auction_embed(
            message.channel,
            auction,
            message.author,
            bid
        )

        # แจ้งผล
        await message.channel.send(
            f"🔨 {message.author.mention} บิดราคา **{bid:,} บาท** สำเร็จ!",
            delete_after=8
        )    async def send_outbid_notification(
        self,
        old_bidder_id: int,
        guild: discord.Guild,
        item_name: str,
        old_price: int,
        new_price: int
    ):
        """แจ้งเตือนผู้ที่ถูกบิดแซง"""

        if old_bidder_id in (None, 0):
            return

        member = guild.get_member(old_bidder_id)

        if member is None:
            return

        embed = discord.Embed(
            title="🔔 คุณถูกบิดแซงแล้ว",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="📦 สินค้า",
            value=item_name,
            inline=False
        )

        embed.add_field(
            name="💰 ราคาของคุณ",
            value=f"{old_price:,} บาท",
            inline=True
        )

        embed.add_field(
            name="💸 ราคาปัจจุบัน",
            value=f"{new_price:,} บาท",
            inline=True
        )

        embed.set_footer(
            text="รีบกลับไปบิดก่อนหมดเวลานะ!"
        )

        try:
            await member.send(embed=embed)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Auction(bot))
