import discord
import time

from discord.ext import commands

from database import (
    get_active_auction,
    add_bid,
    update_price
)

from utils.parser import parse_bid
from utils.embeds import auction_embed


class Auction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_auction_embed(
        self,
        channel: discord.TextChannel,
        auction,
        bidder: discord.Member,
        price: int
    ):

        try:
            message = await channel.fetch_message(
                auction["message_id"]
            )
        except:
            return

        bid_count = auction.get("bid_count", 0) + 1
        participant = auction.get("participant_count", 1)

        highest = bidder.mention

        embed = auction_embed(
            item_name=auction["item_name"],
            description=auction["description"],
            image=auction["image"],
            start_price=auction["start_price"],
            current_price=price,
            minimum_bid=auction["minimum_bid"],
            highest_bidder=highest,
            bid_count=bid_count,
            participant_count=participant,
            minutes_left=10,
            percent=80
        )

        await message.edit(embed=embed)
