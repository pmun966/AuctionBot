import discord

from discord.ext import commands
from discord import app_commands

from utils.checks import owner_only
from views.modals import CreateAuctionModal


class Auction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -----------------------------
    # Slash Command Group
    # -----------------------------

    auction = app_commands.Group(
        name="auction",
        description="ระบบประมูล"
    )

    # -----------------------------
    # /auction create
    # -----------------------------

    @auction.command(
        name="create",
        description="สร้างการประมูล"
    )

    async def create(
        self,
        interaction: discord.Interaction
    ):

        # ตรวจสอบสิทธิ์
        if not owner_only(interaction):

            return await interaction.response.send_message(
                "❌ เฉพาะเจ้าของบอทเท่านั้น",
                ephemeral=True
            )

        # เปิด Modal
        await interaction.response.send_modal(
            CreateAuctionModal()
        )

    # -----------------------------
    # /auction ping
    # -----------------------------

    @auction.command(
        name="ping",
        description="ทดสอบระบบประมูล"
    )

    async def ping(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency * 1000)} ms`",
            ephemeral=True
        )

    # -----------------------------
    # Helper
    # -----------------------------

    async def get_auction_channel(
        self,
        interaction: discord.Interaction
    ):

        return interaction.channel

    async def send_error(
        self,
        interaction: discord.Interaction,
        text: str
    ):

        if interaction.response.is_done():

            await interaction.followup.send(
                text,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                text,
                ephemeral=True
            )


async def setup(bot):

    await bot.add_cog(
        Auction(bot)
    )
