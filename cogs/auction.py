import discord

from discord.ext import commands
from discord import app_commands

from utils.checks import owner_only
from utils.embeds import auction_embed


class Auction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="auction_create",
        description="สร้างการประมูล"
    )

    async def auction_create(

        self,
        interaction: discord.Interaction,

        item: str,

        description: str,

        price: app_commands.Range[int,1],

        minimum: app_commands.Range[int,1],

        minutes: app_commands.Range[int,1,1440],

        image: str = None

    ):

        if not owner_only(interaction):

            return await interaction.response.send_message(
                "❌ ไม่มีสิทธิ์",
                ephemeral=True
            )

        embed = auction_embed(
            item,
            description,
            image,
            price,
            minimum,
            minutes
        )

        await interaction.channel.send(
            embed=embed
        )

        await interaction.response.send_message(
            "✅ สร้างประมูลเรียบร้อย",
            ephemeral=True
        )


async def setup(bot):

    await bot.add_cog(Auction(bot))
