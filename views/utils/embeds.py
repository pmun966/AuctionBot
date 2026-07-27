import time
import discord
from config import EMBED_COLOR


def progress_bar(percent: int) -> str:
    """สร้าง Progress Bar"""

    total = 20

    percent = max(0, min(percent, 100))

    fill = int((percent / 100) * total)

    return "█" * fill + "░" * (total - fill)


def format_time(seconds: int) -> str:
    """แปลงวินาทีเป็น HH:MM:SS"""

    if seconds < 0:
        seconds = 0

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


def create_auction_embed(
    *,
    item_name: str,
    description: str,
    image: str,
    start_price: int,
    minimum_bid: int,
    duration: int
):

    embed = discord.Embed(
        title=f"🏛️ {item_name}",
        description=description,
        color=EMBED_COLOR
    )

    embed.add_field(
        name="💰 ราคาเริ่มต้น",
        value=f"```{start_price:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="💸 ราคาปัจจุบัน",
        value=f"```{start_price:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="📈 ขั้นต่ำ",
        value=f"```{minimum_bid:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="👤 ผู้นำการประมูล",
        value="```ยังไม่มี```",
        inline=True
    )

    embed.add_field(
        name="🔨 จำนวนครั้งที่บิด",
        value="```0```",
        inline=True
    )

    embed.add_field(
        name="👥 ผู้เข้าร่วม",
        value="```0```",
        inline=True
    )

    embed.add_field(
        name="⏳ เวลาคงเหลือ",
        value=f"```{duration} นาที```",
        inline=True
    )

    embed.add_field(
        name="📊 ความคืบหน้า",
        value=progress_bar(100),
        inline=False
    )

    if image:
        embed.set_image(url=image)

    embed.set_footer(
        text="AuctionBot v2 • เปิดประมูลแล้ว"
    )

    embed.timestamp = discord.utils.utcnow()

    return embed


def update_auction_embed(
    *,
    auction,
    highest_bidder: str,
    bid_count: int,
    participant_count: int,
    time_left: int
):

    total_time = max(
        1,
        auction["end_time"] - auction["start_time"]
    )

    percent = int(
        (time_left / total_time) * 100
    )

    embed = discord.Embed(
        title=f"🏛️ {auction['item_name']}",
        description=auction["description"],
        color=EMBED_COLOR
    )

    embed.add_field(
        name="💰 ราคาเริ่มต้น",
        value=f"```{auction['start_price']:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="💸 ราคาปัจจุบัน",
        value=f"```{auction['current_price']:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="📈 ขั้นต่ำ",
        value=f"```{auction['minimum_bid']:,} บาท```",
        inline=True
    )

    embed.add_field(
        name="👤 ผู้นำการประมูล",
        value=highest_bidder,
        inline=True
    )

    embed.add_field(
        name="🔨 จำนวนครั้งที่บิด",
        value=str(bid_count),
        inline=True
    )

    embed.add_field(
        name="👥 ผู้เข้าร่วม",
        value=str(participant_count),
        inline=True
    )

    embed.add_field(
        name="⏳ เวลาคงเหลือ",
        value=format_time(time_left),
        inline=True
    )

    embed.add_field(
        name="📊 ความคืบหน้า",
        value=progress_bar(percent),
        inline=False
    )

    if auction["image"]:
        embed.set_image(url=auction["image"])

    embed.set_footer(
        text="AuctionBot v2"
    )

    embed.timestamp = discord.utils.utcnow()

    return embed


def winner_embed(
    *,
    item_name: str,
    winner: str,
    price: int
):

    embed = discord.Embed(
        title="🏆 ปิดการประมูล",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="📦 สินค้า",
        value=item_name,
        inline=False
    )

    embed.add_field(
        name="👑 ผู้ชนะ",
        value=winner,
        inline=True
    )

    embed.add_field(
        name="💰 ราคาสุดท้าย",
        value=f"{price:,} บาท",
        inline=True
    )

    embed.description = (
        "🎉 ขอแสดงความยินดีกับผู้ชนะการประมูล!"
    )

    embed.timestamp = discord.utils.utcnow()

    return embed
