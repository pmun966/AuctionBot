import discord
from config import EMBED_COLOR

def auction_embed(
    item,
    desc,
    image,
    start_price,
    minimum,
    minutes
):

    embed = discord.Embed(
        title=f"🏛️ {item}",
        description=desc,
        color=EMBED_COLOR
    )

    embed.add_field(
        name="💰 ราคาเริ่มต้น",
        value=f"{start_price:,} บาท",
        inline=True
    )

    embed.add_field(
        name="📈 ขั้นต่ำ",
        value=f"{minimum:,} บาท",
        inline=True
    )

    embed.add_field(
        name="👤 ผู้นำ",
        value="-",
        inline=True
    )

    embed.add_field(
        name="💸 ราคาปัจจุบัน",
        value=f"{start_price:,} บาท",
        inline=False
    )

    embed.add_field(
        name="⏰ เวลาประมูล",
        value=f"{minutes} นาที",
        inline=False
    )

    if image:
        embed.set_image(url=image)

    embed.set_footer(text="Auction Bot")

    return embed
