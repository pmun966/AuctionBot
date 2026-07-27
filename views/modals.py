import time
import discord

from discord.ui import Modal, TextInput
from utils.embeds import create_auction_embed
from database import create_auction


class CreateAuctionModal(Modal, title="🏛️ สร้างการประมูล"):

    item_name = TextInput(
        label="ชื่อสินค้า",
        placeholder="เช่น Dragon Skin",
        max_length=100,
        required=True
    )

    description = TextInput(
        label="รายละเอียด",
        style=discord.TextStyle.paragraph,
        placeholder="รายละเอียดสินค้า...",
        max_length=1000,
        required=True
    )

    start_price = TextInput(
        label="ราคาเริ่มต้น",
        placeholder="100",
        required=True
    )

    minimum_bid = TextInput(
        label="ขั้นต่ำในการบิด",
        placeholder="20",
        required=True
    )

    duration = TextInput(
        label="เวลาประมูล (นาที)",
        placeholder="30",
        required=True
    )

    image_url = TextInput(
        label="URL รูปสินค้า (ไม่บังคับ)",
        placeholder="https://...",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            start_price = int(self.start_price.value)
            minimum_bid = int(self.minimum_bid.value)
            duration = int(self.duration.value)

            if start_price <= 0:
                raise ValueError

            if minimum_bid <= 0:
                raise ValueError

            if duration <= 0:
                raise ValueError

        except ValueError:

            return await interaction.response.send_message(
                "❌ ราคาและเวลาต้องเป็นตัวเลขที่มากกว่า 0",
                ephemeral=True
            )

        end_time = int(time.time()) + (duration * 60)

        embed = create_auction_embed(
            item_name=self.item_name.value,
            description=self.description.value,
            image=self.image_url.value.strip(),
            start_price=start_price,
            minimum_bid=minimum_bid,
            duration=duration
        )

        await interaction.response.send_message(
            "✅ กำลังสร้างการประมูล...",
            ephemeral=True
        )

        auction_message = await interaction.channel.send(
            embed=embed
        )

        await create_auction(
            guild_id=interaction.guild.id,
            channel_id=interaction.channel.id,
            message_id=auction_message.id,
            owner_id=interaction.user.id,
            item_name=self.item_name.value,
            description=self.description.value,
            image=self.image_url.value.strip(),
            start_price=start_price,
            minimum_bid=minimum_bid,
            end_time=end_time
        )

        try:
            await auction_message.edit(
                content="🔨 **เปิดประมูลแล้ว!** พิมพ์จำนวนเงินเพื่อบิดราคา"
            )
        except Exception:
            pass
