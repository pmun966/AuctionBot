import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ใส่ Discord User ID ของเจ้าของ
OWNER_IDS = {
    123456789012345678
}

EMBED_COLOR = 0x5865F2
SUCCESS_COLOR = 0x57F287
ERROR_COLOR = 0xED4245

DEFAULT_EXTENSION = 30
DEFAULT_COOLDOWN = 3
