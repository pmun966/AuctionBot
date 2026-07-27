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


async def get_active_auction(channel_id):

    async with aiosqlite.connect(DATABASE) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM auctions WHERE channel_id=? AND status='OPEN'",
            (channel_id,)
        )

        return await cursor.fetchone()


async def add_bid(
    auction_id,
    user_id,
    amount,
    bid_time
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT INTO bids(
                auction_id,
                user_id,
                amount,
                bid_time
            )
            VALUES(?,?,?,?)
            """,
            (
                auction_id,
                user_id,
                amount,
                bid_time
            )
        )

        await db.commit()


async def update_price(
    auction_id,
    price,
    bidder
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE auctions
            SET
                current_price=?,
                highest_bidder=?
            WHERE id=?
            """,
            (
                price,
                bidder,
                auction_id
            )
        )

        await db.commit()
