import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from config import BOT_TOKEN, CHANNEL_USERNAME, ADMIN_IDS
from database import add_user, get_all_users
from aiogram import Router
from database import init_db


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# 👇 Кнопка "Открыть доступ"
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть доступ", callback_data="check_sub")]
    ])

# 📌 Проверка подписки
async def is_subscribed(user_id: int) -> bool:
    member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

# /start
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    add_user(user_id)
    text = "👋 Привет! Чтобы забрать шаблон навсегда и использовать его уже сейчас - подпишись на мой канал):"
    await message.answer(text, reply_markup=get_main_keyboard())

# Проверка подписки по кнопке
@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed(user_id):
        await callback.message.edit_text(
            "✅ Ты подписан! [Вот твой шаблон)](https://docs.google.com/spreadsheets/d/1WZp0CKb8ZNmsyFofwGolaxKaRZE-VmRp37qiUvMP-lg/edit?usp=sharing)",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("❌ Сначала стоит подписаться на канал.", show_alert=True)

# Рассылка
@router.message(Command("broadcast"))
async def broadcast_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ У вас нет прав на рассылку.")
    
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return await message.answer("❗ Используйте команду: /broadcast ваш_текст")

    text_to_send = parts[1]
    users = get_all_users()
    count = 0

    for uid in users:
        try:
            await bot.send_message(uid, text_to_send)
            count += 1
        except:
            continue

    await message.answer(f"✅ Сообщение отправлено {count} пользователям.")

# 🔁 Запуск бота
async def main():
    await dp.start_polling(bot)
    await init_db()
    # запуск диспетчера

if __name__ == "__main__":
    asyncio.run(main())
