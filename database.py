import aiosqlite

DATABASE = "data/auction.db"

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

            end_time INTEGER,

            status TEXT
        )
        """)

        await db.commit()
