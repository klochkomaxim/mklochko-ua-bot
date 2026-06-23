import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

BOT_TOKEN = os.getenv("8921304998:AAE5RjCZeU09xAUGnmgYRIDQy_2yaYksTjs")

CHANNEL_URL = "https://t.me/mklochkoua"
CHAT_URL = "https://t.me/+69ABIP-7Ft0yOTEy"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📱 Android", callback_data="android"),
            InlineKeyboardButton(text="💻 Windows", callback_data="windows")
        ],
        [
            InlineKeyboardButton(text="🐧 Linux", callback_data="linux"),
            InlineKeyboardButton(text="🌐 MikroTik", callback_data="mikrotik")
        ],
        [
            InlineKeyboardButton(text="🔧 Ремонт", callback_data="repair"),
            InlineKeyboardButton(text="🤖 Проєкти", callback_data="projects")
        ],
        [
            InlineKeyboardButton(text="📢 Канал", url=CHANNEL_URL),
            InlineKeyboardButton(text="💬 Чат", url=CHAT_URL)
        ],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🚀 Вітаємо в MKLOCHKO UA!\n\n"
        "Український цифровий проєкт:\n\n"
        "📱 Android\n"
        "💻 Windows\n"
        "🐧 Linux\n"
        "🌐 MikroTik та мережі\n"
        "🔧 Ремонт флешок і SSD\n"
        "🤖 Власні розробки\n\n"
        "Оберіть розділ:",
        reply_markup=menu()
    )


@dp.callback_query(F.data)
async def callbacks(call: CallbackQuery):
    texts = {
        "android": "📱 Android\n\nТут будуть APK, програми для старих Android 4–7, утиліти та інструкції.",
        "windows": "💻 Windows\n\nКорисні програми, драйвери, утиліти та інструкції.",
        "linux": "🐧 Linux\n\nLinux Mint, Ubuntu, Debian, Raspberry Pi OS та корисні команди.",
        "mikrotik": "🌐 MikroTik та мережі\n\nНалаштування роутерів, DHCP, VPN, Wi-Fi, WinBox та мережеві команди.",
        "repair": "🔧 Ремонт\n\nВідновлення флешок, SSD, Android-пристроїв та діагностика техніки.",
        "projects": "🤖 Проєкти MKLOCHKO UA\n\nNFC Master Safe, Offline Chat, DLNA Server, USB Recovery Tool та інші розробки.",
    }

    await call.message.edit_text(
        texts.get(call.data, "Розділ у розробці."),
        reply_markup=menu()
    )
    await call.answer()


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не знайдено")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())