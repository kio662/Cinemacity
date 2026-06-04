import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram Credentials ──────────────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ── MongoDB ───────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "")

# ── Channels ──────────────────────────────────────────────────────────────────
DB_CHANNEL = int(os.getenv("DB_CHANNEL", "0"))
FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "0"))
FORCE_SUB_INVITE = os.getenv("FORCE_SUB_INVITE", "https://t.me/your_channel")

# ── Auto Delete ───────────────────────────────────────────────────────────────
AUTO_DELETE_SECONDS = int(os.getenv("AUTO_DELETE_SECONDS", "300"))

# ── Render Keep-Alive ─────────────────────────────────────────────────────────
RENDER_URL = os.getenv("RENDER_URL", "")

# ── Bot Info ──────────────────────────────────────────────────────────────────
BOT_NAME = "CinemaCityHub"
BOT_USERNAME = os.getenv("BOT_USERNAME", "CinemaCityHubBot")
BOT_VERSION = "2.0"
