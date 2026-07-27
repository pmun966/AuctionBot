import os
import discord

from discord.ext import commands

from config import TOKEN
from database import setup_database

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


async def load_extensions():

    for file in os.listdir("cogs"):

        if file.endswith(".py"):

            await bot.load_extension(
                f"cogs.{file[:-3]}"
            )


@bot.event
async def on_ready():

    await setup_database()

    print("=" * 40)
    print(bot.user)
    print("=" * 40)

    try:

        synced = await bot.tree.sync()

        print(f"Synced {len(synced)} Commands")

    except Exception as e:

        print(e)


async def main():

    async with bot:

        await load_extensions()

        await bot.start(TOKEN)


import asyncio
asyncio.run(main())
