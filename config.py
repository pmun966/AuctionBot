import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Discord User ID ของเจ้าของบอท
OWNER_IDS = {
    123456789012345678
}

EMBED_COLOR = 0x5865F2
SUCCESS_COLOR = 0x57F287
ERROR_COLOR = 0xED4245

ANTI_SNIPER_SECONDS = 30
BID_COOLDOWN = 3

DATABASE = "data/auction.db"
