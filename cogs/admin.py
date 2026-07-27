import discord
from discord.ext import commands
from discord import app_commands

from utils.checks import owner_only


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="ping",
        description="ทดสอบบอท"
    )
    async def ping(self, interaction: discord.Interaction):

        if not owner_only(interaction):
            return await interaction.response.send_message(
                "❌ เฉพาะเจ้าของบอทเท่านั้น",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency*1000)} ms`"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
