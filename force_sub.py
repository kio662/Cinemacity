from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNEL, FORCE_SUB_INVITE


async def is_subscribed(client: Client, user_id: int) -> bool:
    """Returns True if user is a member of the force-sub channel."""
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status.name in ["BANNED", "LEFT"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        # Bot is not admin — skip check
        return True
    except Exception:
        return False


async def send_force_sub_message(client, message):
    """Send join prompt with inline buttons."""
    await message.reply(
        "╔══════════════════════╗\n"
        "║  🔒  ACCESS DENIED  🔒  ║\n"
        "╚══════════════════════╝\n\n"
        "🎬 **CinemaCityHub**\n\n"
        "You must **join our official channel** to use this bot.\n\n"
        "👇 Click below, join, then tap **Try Again**.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Join CinemaCityHub Channel", url=FORCE_SUB_INVITE)],
            [InlineKeyboardButton("🔄 Try Again", callback_data="check_sub")],
        ])
    )
