import asyncio
from pyrogram.errors import MessageDeleteForbidden, FloodWait
from config import AUTO_DELETE_SECONDS


async def auto_delete_media(client, sent_messages: list, notice_message):
    """
    Auto-delete sent movie files after AUTO_DELETE_SECONDS.
    Updates the notice message with a countdown at key intervals.
    """
    total = AUTO_DELETE_SECONDS

    # Countdown checkpoints (seconds remaining)
    checkpoints = sorted(
        set(t for t in [total, total // 2, 60, 30, 10] if 0 < t < total),
        reverse=True
    )

    elapsed = 0

    for checkpoint in checkpoints:
        wait = total - checkpoint - elapsed
        if wait > 0:
            await asyncio.sleep(wait)
            elapsed += wait

        minutes = checkpoint // 60
        seconds = checkpoint % 60
        time_str = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"

        try:
            await notice_message.edit_text(
                f"⚠️ **CinemaCityHub — Auto Delete**\n\n"
                f"🗑️ Files will be deleted in **{time_str}**\n"
                f"📥 **Save them before they're gone!**"
            )
        except Exception:
            pass

    # Wait remaining time after last checkpoint
    remaining = total - elapsed - checkpoints[-1] if checkpoints else total
    if remaining > 0:
        await asyncio.sleep(remaining)

    # Delete all movie messages
    for msg in sent_messages:
        try:
            await msg.delete()
        except MessageDeleteForbidden:
            pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

    # Update notice to deleted status
    try:
        await notice_message.edit_text(
            "🗑️ **Files have been deleted.**\n\n"
            "🔍 Search again if you need them.\n"
            "— **CinemaCityHub**"
        )
    except Exception:
        pass

    # Delete the notice itself after 30 seconds
    await asyncio.sleep(30)
    try:
        await notice_message.delete()
    except Exception:
        pass
