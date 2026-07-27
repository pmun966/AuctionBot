import time
import discord

from discord.ext import commands

from database import (
    get_active_auction,
    add_bid,
    update_price
)

from utils.parser import parse_bid


class Auction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # กันบอท
        if message.author.bot:
            return

        # ตรวจว่าพิมพ์เป็นตัวเลขหรือไม่
        bid = parse_bid(message.content)

        if bid is None:
            return

        # ตรวจว่าห้องนี้มีประมูลอยู่หรือไม่
        auction = await get_active_auction(message.channel.id)

        if auction is None:
            return

        # ลบข้อความการบิดเพื่อให้ห้องสะอาด
        try:
            await message.delete()
        except:
            pass

        # ห้ามบิดต่อราคาตัวเอง
        if auction["highest_bidder"] == message.author.id:

            return await message.channel.send(
                f"❌ {message.author.mention} คุณเป็นผู้นำอยู่แล้ว",
                delete_after=5
            )

        # ตรวจขั้นต่ำ
        minimum_price = auction["current_price"] + auction["minimum_bid"]

        if bid < minimum_price:

            return await message.channel.send(
                f"❌ ต้องบิดอย่างน้อย **{minimum_price:,} บาท**",
                delete_after=5
            )

        # บันทึกข้อมูล
        await add_bid(
            auction["id"],
            message.author.id,
            bid,
            int(time.time())
        )

        # อัปเดตราคาปัจจุบัน
        await update_price(
            auction["id"],
            bid,
            message.author.id
        )

        # แจ้งผล
        await message.channel.send(
            f"🔨 {message.author.mention} บิด **{bid:,} บาท** สำเร็จ!",
            delete_after=8
        )


async def setup(bot):
    await bot.add_cog(Auction(bot))
