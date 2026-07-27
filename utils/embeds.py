import discord
from config import EMBED_COLOR

def progress_bar(percent: int) -> str:
    total = 10
    fill = max(0, min(total, int(percent / 10)))
    return "█" * fill + "░" * (total - fill)


def auction_embed(
    item_name: str,
    description: str,
    image: str,
    start_price: int,
    current_price: int,
    minimum_bid: int,
    highest_bidder: str,
    bid_count: int,
    participant_count: int,
    minutes_left: int,
    percent: int
):

    embed = discord.Embed(
        title=f"🏛️ {item_name}",
        description=description,
        color=EMBED_COLOR
    )

    embed.add_field(
        name="💰 ราคาเริ่มต้น",
        value=f"{start_price:,} บาท",
        inline=True
    )

    embed.add_field(
        name="💸 ราคาปัจจุบัน",
        value=f"{current_price:,} บาท",
        inline=True
    )

    embed.add_field(
        name="📈 ขั้นต่ำ",
        value=f"{minimum_bid:,} บาท",
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
        value=f"{minutes_left} นาที\n{progress_bar(percent)}",
        inline=False
    )

    if image:
        embed.set_image(url=image)

    embed.set_footer(text="Auction Bot")

    return embed
