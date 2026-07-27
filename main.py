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


@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Logged in as {bot.user}")
    print(f"🆔 ID : {bot.user.id}")
    print("=" * 50)

    # สร้างฐานข้อมูล
    await setup_database()

    # โหลด Cogs
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = f"cogs.{file[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"✅ Loaded {extension}")
            except Exception as e:
                print(f"❌ {extension} : {e}")

    # Sync Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} Slash Commands")
    except Exception as e:
        print(f"❌ Sync Error : {e}")

    print("🤖 Auction Bot พร้อมใช้งานแล้ว")


@bot.event
async def on_command_error(ctx, error):
    print(error)


if __name__ == "__main__":
    if TOKEN is None:
        raise ValueError(
            "ไม่พบ DISCORD_TOKEN กรุณาเพิ่มใน .env หรือ Secrets"
        )

    bot.run(TOKEN)
