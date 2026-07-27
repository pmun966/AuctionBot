import aiosqlite
from config import DATABASE

async def setup_database():

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute("""

        CREATE TABLE IF NOT EXISTS auctions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id INTEGER,
            channel_id INTEGER,
            message_id INTEGER,

            owner_id INTEGER,

            item_name TEXT,
            description TEXT,

            image TEXT,

            start_price INTEGER,
            current_price INTEGER,
            minimum_bid INTEGER,

            highest_bidder INTEGER,

            start_time INTEGER,
            end_time INTEGER,

            status TEXT

        )

        """)

        await db.execute("""

        CREATE TABLE IF NOT EXISTS bids(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            auction_id INTEGER,

            user_id INTEGER,

            amount INTEGER,

            bid_time INTEGER

        )

        """)

        await db.commit()
