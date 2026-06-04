from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ── Language Display Labels ───────────────────────────────────────────────────
LANGUAGE_FLAGS = {
    "tamil":     "🎭 Tamil",
    "hindi":     "🇮🇳 Hindi",
    "english":   "🇺🇸 English",
    "telugu":    "🌺 Telugu",
    "malayalam": "🌴 Malayalam",
    "kannada":   "🌟 Kannada",
    "bengali":   "🎨 Bengali",
    "marathi":   "🏔️ Marathi",
    "punjabi":   "🌾 Punjabi",
    "dual":      "🔊 Dual Audio",
    "multi":     "🌐 Multi Audio",
    "unknown":   "🎬 Unknown",
}

# ── Quality Display Labels ────────────────────────────────────────────────────
QUALITY_LABELS = {
    "4k":      "🔵 4K UHD",
    "1080p":   "🟢 1080p FHD",
    "720p":    "🟡 720p HD",
    "480p":    "🟠 480p SD",
    "360p":    "🔴 360p CAM",
    "unknown": "❓ Unknown",
}


# ── Start Keyboard ────────────────────────────────────────────────────────────
def start_keyboard(support_url: str = "https://t.me/your_group",
                   channel_url: str = "https://t.me/your_channel",
                   bot_username: str = "CinemaCityHubBot") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Search Movie", switch_inline_query_current_chat=""),
        ],
        [
            InlineKeyboardButton("📢 Updates Channel", url=channel_url),
            InlineKeyboardButton("👥 Support Group", url=support_url),
        ],
        [
            InlineKeyboardButton("❓ How to use", callback_data="how_to_use"),
            InlineKeyboardButton("ℹ️ About bot", callback_data="about_bot"),
        ],
        [
            InlineKeyboardButton("🌐 Languages", callback_data="languages"),
            InlineKeyboardButton("📽️ Qualities", callback_data="qualities"),
        ],
        [
            InlineKeyboardButton(
                "🚀 Share CinemaCityHub",
                url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=🎬 Best Movie Bot!"
            ),
        ],
    ])


# ── Language Selection Keyboard ───────────────────────────────────────────────
def language_keyboard(movie_name: str, languages: list) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, lang in enumerate(languages):
        label = LANGUAGE_FLAGS.get(lang, f"🎬 {lang.title()}")
        callback = f"lang|{movie_name[:30]}|{lang}"
        row.append(InlineKeyboardButton(label, callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton("🌍 All Languages", callback_data=f"lang|{movie_name[:30]}|all")
    ])
    return InlineKeyboardMarkup(buttons)


# ── Quality Selection Keyboard ────────────────────────────────────────────────
def quality_keyboard(movie_name: str, language: str, qualities: list) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, q in enumerate(qualities):
        label = QUALITY_LABELS.get(q, f"📽️ {q.upper()}")
        callback = f"quality|{movie_name[:25]}|{language}|{q}"
        row.append(InlineKeyboardButton(label, callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data=f"back|{movie_name[:30]}")
    ])
    return InlineKeyboardMarkup(buttons)


# ── Back to Home Keyboard ─────────────────────────────────────────────────────
def back_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back to home", callback_data="back_home")]
    ])
