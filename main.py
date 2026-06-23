import os
import sqlite3
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

CHANNEL_URL = "https://t.me/mklochkoua"
CHAT_URL = "https://t.me/+69ABIP-7Ft0yOTEy"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB = "files.db"
pending = {}


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            description TEXT,
            file_id TEXT,
            file_name TEXT
        )
    """)
    conn.commit()
    conn.close()


def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Завантаження", callback_data="downloads")],
        [
            InlineKeyboardButton(text="📱 Android", callback_data="cat_android"),
            InlineKeyboardButton(text="💻 Windows", callback_data="cat_windows")
        ],
        [
            InlineKeyboardButton(text="🐧 Linux", callback_data="cat_linux"),
            InlineKeyboardButton(text="🌐 MikroTik", callback_data="cat_mikrotik")
        ],
        [
            InlineKeyboardButton(text="📢 Канал", url=CHANNEL_URL),
            InlineKeyboardButton(text="💬 Чат", url=CHAT_URL)
        ],
    ])


@dp.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Ваш Telegram ID:\n`{message.from_user.id}`", parse_mode="Markdown")


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🚀 Вітаємо в MKLOCHKO UA Bot!\n\n"
        "Тут буде каталог програм, утиліт та власних розробок.\n\n"
        "Оберіть розділ:",
        reply_markup=menu()
    )


@dp.message(F.document)
async def receive_file(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Завантажувати файли може тільки адміністратор.")
        return

    pending[message.from_user.id] = {
        "file_id": message.document.file_id,
        "file_name": message.document.file_name
    }

    await message.answer(
        "✅ Файл отримано.\n\n"
        "Тепер надішли дані в такому форматі:\n\n"
        "Назва програми\n"
        "Категорія: android/windows/linux/mikrotik/tools\n"
        "Опис програми"
    )


@dp.message(F.text)
async def save_file_info(message: Message):
    uid = message.from_user.id

    if uid not in pending:
        return

    parts = message.text.split("\n", 2)

    if len(parts) < 3:
        await message.answer("❌ Неправильний формат. Треба 3 рядки: назва, категорія, опис.")
        return

    title = parts[0].strip()
    category = parts[1].replace("Категорія:", "").strip().lower()
    description = parts[2].strip()

    data = pending.pop(uid)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (title, category, description, file_id, file_name) VALUES (?, ?, ?, ?, ?)",
        (title, category, description, data["file_id"], data["file_name"])
    )
    conn.commit()
    conn.close()

    await message.answer(f"✅ Додано в каталог:\n\n📦 {title}\n📂 {category}")


@dp.callback_query(F.data.startswith("cat_"))
async def category(call: CallbackQuery):
    category_name = call.data.replace("cat_", "")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM files WHERE category=? ORDER BY id DESC LIMIT 10", (category_name,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await call.message.edit_text("📂 У цьому розділі поки немає файлів.", reply_markup=menu())
        await call.answer()
        return

    buttons = [[InlineKeyboardButton(text=f"📦 {title}", callback_data=f"file_{fid}")] for fid, title in rows]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    await call.message.edit_text(
        f"📂 Розділ: {category_name}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await call.answer()


@dp.callback_query(F.data.startswith("file_"))
async def send_file(call: CallbackQuery):
    file_id = int(call.data.replace("file_", ""))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT title, description, file_id, file_name FROM files WHERE id=?", (file_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await call.answer("Файл не знайдено")
        return

    title, description, telegram_file_id, file_name = row

    await call.message.answer_document(
        telegram_file_id,
        caption=f"📦 {title}\n\n{description}\n\n📁 Файл: {file_name}\n\n#MKLOCHKOUA"
    )
    await call.answer()


@dp.callback_query(F.data == "downloads")
async def downloads(call: CallbackQuery):
    await call.message.edit_text(
        "📥 Оберіть категорію для завантаження:",
        reply_markup=menu()
    )
    await call.answer()


@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.edit_text("🚀 Головне меню MKLOCHKO UA", reply_markup=menu())
    await call.answer()


async def health(request):
    return web.Response(text="MKLOCHKO UA Bot is running")


async def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    init_db()
    await run_web()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
