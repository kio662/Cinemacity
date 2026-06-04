import asyncio
from pyrogram import Client
from pyrogram.types import Message

from config import AUTO_DELETE_SECONDS, BOT_NAME, BOT_VERSION, FORCE_SUB_INVITE
from database import save_file, search_files, get_languages, save_user, get_total_files, get_total_users
from force_sub import is_subscribed, send_force_sub_message
from auto_delete import auto_delete_media
from keyboards import (
    start_keyboard, language_keyboard, quality_keyboard,
    back_home_keyboard, LANGUAGE_FLAGS, QUALITY_LABELS
)
from lang_detector import parse_movie_info


# ── Start Command ─────────────────────────────────────────────────────────────
async def start_handler(client: Client, message: Message):
    user = message.from_user
    first_name = user.first_name or "Friend"

    save_user(user.id, first_name, user.username)

    await message.reply_photo(
        photo="https://telegra.ph/file/a6a27a4e35a1c3c1e8b17.jpg",
        caption=(
            f"╔══════════════════════╗\n"
            f"║   🎬 CINEMACITYHUB 🎬   ║\n"
            f"╚══════════════════════╝\n\n"
            f"👋 **Hello, {first_name}!**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🍿 **Welcome to CinemaCityHub**\n"
            f"🎥 Your Ultimate Movie Destination!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ **What I Can Do:**\n\n"
            f"🔍 Search any movie instantly\n"
            f"🌐 Filter by language\n"
            f"📽️ Choose your quality\n"
            f"⏳ Auto-delete after timer\n"
            f"🔒 Secure force subscribe\n"
            f"🚀 Always online 24/7\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 **Get started below!**"
        ),
        reply_markup=start_keyboard()
    )


# ── Index Files from DB Channel ───────────────────────────────────────────────
async def index_handler(client: Client, message: Message):
    media = message.document or message.video or message.audio
    if not media:
        return

    raw_name = getattr(media, "file_name", "") or "unknown"
    info = parse_movie_info(raw_name)

    saved = save_file(
        file_id=media.file_id,
        file_name=raw_name,
        file_unique_id=media.file_unique_id,
        language=info["language"],
        quality=info["quality"]
    )

    status = "✅ Indexed" if saved else "⚠️ Duplicate"
    print(f"[{status}] {info['clean_name']} | {info['language']} | {info['quality']}")


# ── Movie Search in Group ─────────────────────────────────────────────────────
async def filter_handler(client: Client, message: Message):
    user_id = message.from_user.id
    query = message.text.strip()

    if not query or len(query) < 3:
        return

    # Force subscribe check
    if not await is_subscribed(client, user_id):
        await send_force_sub_message(client, message)
        return

    # Find available languages
    languages = get_languages(query)

    if not languages:
        no_result = await message.reply(
            f"❌ **No results found for:** `{query}`\n\n"
            f"💡 Try a shorter or different spelling.\n"
            f"— **CinemaCityHub**"
        )
        await asyncio.sleep(10)
        try:
            await no_result.delete()
            await message.delete()
        except Exception:
            pass
        return

    # Show language selection
    await message.reply(
        f"🎬 **{query.title()}**\n\n"
        f"✅ Found in **{len(languages)} language(s)**\n"
        f"👇 Select your preferred language:",
        reply_markup=language_keyboard(query, languages)
    )


# ── Language Button Callback ──────────────────────────────────────────────────
async def language_callback(client: Client, callback_query):
    _, movie_name, language = callback_query.data.split("|", 2)

    results = search_files(movie_name, language)

    if not results:
        await callback_query.answer("❌ No files found!", show_alert=True)
        return

    qualities = sorted(set(r.get("quality", "unknown") for r in results))

    if len(qualities) > 1:
        lang_label = LANGUAGE_FLAGS.get(language, language.title())
        await callback_query.message.edit_text(
            f"🎬 **{movie_name.title()}**\n"
            f"🌐 Language: **{lang_label}**\n\n"
            f"📽️ Select quality:",
            reply_markup=quality_keyboard(movie_name, language, qualities)
        )
    else:
        await callback_query.message.delete()
        await send_movie_files(
            client, callback_query.message,
            results, movie_name, language
        )


# ── Quality Button Callback ───────────────────────────────────────────────────
async def quality_callback(client: Client, callback_query):
    _, movie_name, language, quality = callback_query.data.split("|", 3)

    results = search_files(movie_name, language)
    filtered = [r for r in results if r.get("quality") == quality]

    if not filtered:
        await callback_query.answer("❌ Files not found!", show_alert=True)
        return

    await callback_query.message.delete()
    await send_movie_files(
        client, callback_query.message,
        filtered, movie_name, language, quality
    )


# ── Back Button Callback ──────────────────────────────────────────────────────
async def back_callback(client: Client, callback_query):
    _, movie_name = callback_query.data.split("|", 1)
    languages = get_languages(movie_name)
    await callback_query.message.edit_text(
        f"🎬 **{movie_name.title()}** — Select language:",
        reply_markup=language_keyboard(movie_name, languages)
    )


# ── Back Home Callback ────────────────────────────────────────────────────────
async def back_home_callback(client: Client, callback_query):
    user = callback_query.from_user
    first_name = user.first_name or "Friend"
    await callback_query.message.edit_caption(
        caption=(
            f"╔══════════════════════╗\n"
            f"║   🎬 CINEMACITYHUB 🎬   ║\n"
            f"╚══════════════════════╝\n\n"
            f"👋 **Hello, {first_name}!**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🍿 **Welcome to CinemaCityHub**\n"
            f"🎥 Your Ultimate Movie Destination!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ **What I Can Do:**\n\n"
            f"🔍 Search any movie instantly\n"
            f"🌐 Filter by language\n"
            f"📽️ Choose your quality\n"
            f"⏳ Auto-delete after timer\n"
            f"🔒 Secure force subscribe\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 **Get started below!**"
        ),
        reply_markup=start_keyboard()
    )


# ── How to Use Callback ───────────────────────────────────────────────────────
async def how_to_use_callback(client: Client, callback_query):
    await callback_query.message.edit_caption(
        caption=(
            "╔══════════════════════╗\n"
            "║      ❓ HOW TO USE      ║\n"
            "╚══════════════════════╝\n\n"
            "**Step 1️⃣** — Join our channel 📢\n\n"
            "**Step 2️⃣** — Go to our movie group 👥\n\n"
            "**Step 3️⃣** — Type the movie name 🔍\n"
            "   Example: `KGF` or `RRR` or `Pushpa`\n\n"
            "**Step 4️⃣** — Pick your language 🌐\n"
            "   Tamil | Hindi | English | Telugu...\n\n"
            "**Step 5️⃣** — Pick your quality 📽️\n"
            "   4K | 1080p | 720p | 480p\n\n"
            "**Step 6️⃣** — Download before auto-delete ⏳\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ Files delete after **{AUTO_DELETE_SECONDS // 60} minutes!**\n"
            "📥 **Save immediately after receiving!**"
        ),
        reply_markup=back_home_keyboard()
    )


# ── About Bot Callback ────────────────────────────────────────────────────────
async def about_bot_callback(client: Client, callback_query):
    total_files = get_total_files()
    total_users = get_total_users()
    await callback_query.message.edit_caption(
        caption=(
            "╔══════════════════════╗\n"
            "║    ℹ️ ABOUT CINEMACITYHUB   ║\n"
            "╚══════════════════════╝\n\n"
            f"🤖 **{BOT_NAME}**\n"
            f"💡 Version: **{BOT_VERSION}**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🛠️ **Built With:**\n"
            "   ⚡ Pyrogram Framework\n"
            "   🍃 MongoDB Database\n"
            "   ☁️ Render Cloud Hosting\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ **Features:**\n"
            "   🔍 Instant movie search\n"
            "   🌐 Multi-language support\n"
            "   📽️ Quality filter\n"
            "   ⏳ Auto-delete timer\n"
            "   🔒 Force subscribe\n"
            "   🚀 Always online 24/7\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 **Total Movies:** `{total_files}`\n"
            f"👥 **Total Users:** `{total_users}`"
        ),
        reply_markup=back_home_keyboard()
    )


# ── Languages Callback ────────────────────────────────────────────────────────
async def languages_callback(client: Client, callback_query):
    await callback_query.message.edit_caption(
        caption=(
            "╔══════════════════════╗\n"
            "║  🌐 SUPPORTED LANGUAGES  ║\n"
            "╚══════════════════════╝\n\n"
            "🎭 **Tamil**\n"
            "🇮🇳 **Hindi**\n"
            "🇺🇸 **English**\n"
            "🌺 **Telugu**\n"
            "🌴 **Malayalam**\n"
            "🌟 **Kannada**\n"
            "🎨 **Bengali**\n"
            "🏔️ **Marathi**\n"
            "🌾 **Punjabi**\n"
            "🔊 **Dual Audio**\n"
            "🌐 **Multi Audio**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 More languages added regularly!"
        ),
        reply_markup=back_home_keyboard()
    )


# ── Qualities Callback ────────────────────────────────────────────────────────
async def qualities_callback(client: Client, callback_query):
    await callback_query.message.edit_caption(
        caption=(
            "╔══════════════════════╗\n"
            "║   📽️ VIDEO QUALITIES    ║\n"
            "╚══════════════════════╝\n\n"
            "🔵 **4K UHD** — Ultra HD 2160p\n"
            "   Best quality, large file size\n\n"
            "🟢 **1080p FHD** — Full HD\n"
            "   Excellent quality\n\n"
            "🟡 **720p HD** — High Definition\n"
            "   Great quality, medium size\n\n"
            "🟠 **480p SD** — Standard\n"
            "   Good quality, small size\n\n"
            "🔴 **360p CAM** — Low Quality\n"
            "   Basic quality, tiny size\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Availability depends on uploads!"
        ),
        reply_markup=back_home_keyboard()
    )


# ── Send Movie Files ──────────────────────────────────────────────────────────
async def send_movie_files(client, message, results, movie_name, language, quality=None):
    chat_id = message.chat.id
    sent_messages = []

    lang_label = LANGUAGE_FLAGS.get(language, language.title()) if language != "all" else "🌍 All Languages"
    quality_label = f" • {QUALITY_LABELS.get(quality, quality.upper())}" if quality and quality != "unknown" else ""

    header = await client.send_message(
        chat_id,
        f"🎬 **{movie_name.title()}**\n"
        f"🌐 Language: **{lang_label}**{quality_label}\n"
        f"📦 Files: **{len(results)}**\n\n"
        f"⚠️ Files auto-delete in **{AUTO_DELETE_SECONDS // 60} min** — save now!\n"
        f"— **CinemaCityHub**"
    )
    sent_messages.append(header)

    for movie in results:
        try:
            info = parse_movie_info(movie["file_name"])
            sent = await client.send_cached_media(
                chat_id=chat_id,
                file_id=movie["file_id"],
                caption=(
                    f"🎞️ **{info['clean_name']}**\n"
                    f"🌐 {movie.get('language', '?').title()} "
                    f"| 📽️ {movie.get('quality', '?').upper()}\n"
                    f"🗑️ Auto-deletes in {AUTO_DELETE_SECONDS // 60}m\n"
                    f"— **CinemaCityHub**"
                )
            )
            sent_messages.append(sent)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Failed to send {movie.get('file_name', '?')}: {e}")

    notice = await client.send_message(
        chat_id,
        f"⏳ **Auto-Delete Timer Started**\n\n"
        f"Files will be deleted in **{AUTO_DELETE_SECONDS // 60} minutes**.\n"
        f"📥 Save them now!\n"
        f"— **CinemaCityHub**"
    )

    asyncio.create_task(auto_delete_media(client, sent_messages, notice))
