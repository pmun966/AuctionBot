import aiosqlite
from config import DATABASE


# =========================
# สร้างฐานข้อมูล
# =========================

async def setup_database():

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute("""

        CREATE TABLE IF NOT EXISTS auctions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,

            owner_id INTEGER NOT NULL,

            item_name TEXT NOT NULL,
            description TEXT,

            image TEXT,

            start_price INTEGER NOT NULL,
            current_price INTEGER NOT NULL,

            minimum_bid INTEGER NOT NULL,

            highest_bidder INTEGER,

            start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL,

            status TEXT DEFAULT 'OPEN'

        )

        """)

        await db.execute("""

        CREATE TABLE IF NOT EXISTS bids(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            auction_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            amount INTEGER NOT NULL,

            bid_time INTEGER NOT NULL

        )

        """)

        await db.commit()


# =========================
# สร้างการประมูล
# =========================

async def create_auction(

    guild_id,
    channel_id,
    message_id,

    owner_id,

    item_name,
    description,
    image,

    start_price,
    minimum_bid,

    end_time

):

    import time

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(

            """

            INSERT INTO auctions(

            guild_id,
            channel_id,
            message_id,

            owner_id,

            item_name,
            description,
            image,

            start_price,
            current_price,

            minimum_bid,

            start_time,
            end_time,

            status

            )

            VALUES(

            ?,?,?,?,
            ?,?,?,
            ?,?,
            ?,
            ?,?,
            'OPEN'

            )

            """,

            (

                guild_id,
                channel_id,
                message_id,

                owner_id,

                item_name,
                description,
                image,

                start_price,
                start_price,

                minimum_bid,

                int(time.time()),
                end_time

            )

        )

        await db.commit()


# =========================
# ดึงประมูลที่เปิดอยู่
# =========================

async def get_active_auction(channel_id):

    async with aiosqlite.connect(DATABASE) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(

            """

            SELECT *

            FROM auctions

            WHERE

            channel_id=?

            AND status='OPEN'

            LIMIT 1

            """,

            (channel_id,)

        )

        return await cursor.fetchone()


# =========================
# บันทึกการบิด
# =========================

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

            VALUES(

            ?,?,?,?

            )

            """,

            (

                auction_id,
                user_id,
                amount,
                bid_time

            )

        )

        await db.commit()


# =========================
# อัปเดตราคา
# =========================

async def update_price(

    auction_id,
    amount,
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

                amount,
                bidder,
                auction_id

            )

        )

        await db.commit()


# =========================
# จำนวนครั้งที่บิด
# =========================

async def get_bid_count(auction_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(

            """

            SELECT COUNT(*)

            FROM bids

            WHERE auction_id=?

            """,

            (auction_id,)

        )

        result = await cursor.fetchone()

        return result[0]


# =========================
# จำนวนผู้เข้าร่วม
# =========================

async def get_participant_count(auction_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(

            """

            SELECT COUNT(DISTINCT user_id)

            FROM bids

            WHERE auction_id=?

            """,

            (auction_id,)

        )

        result = await cursor.fetchone()

        return result[0]


# =========================
# ประวัติการบิด
# =========================

async def get_bid_history(auction_id):

    async with aiosqlite.connect(DATABASE) as db:

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(

            """

            SELECT *

            FROM bids

            WHERE auction_id=?

            ORDER BY amount DESC

            """,

            (auction_id,)

        )

        return await cursor.fetchall()


# =========================
# ปิดประมูล
# =========================

async def close_auction(auction_id):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(

            """

            UPDATE auctions

            SET status='CLOSED'

            WHERE id=?

            """,

            (auction_id,)

        )

        await db.commit()
