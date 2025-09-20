from aiogram.types import Message
from bot.keyboards.main_menu import get_main_menu_keyboard, get_quick_access_keyboard

async def send_main_menu_with_quick_access(message: Message):
    """Отправляет главное меню с инлайн-кнопками быстрого доступа."""
    await message.answer(
        "Для продолжения работы выберите действие",
        reply_markup=get_main_menu_keyboard()
    )
    await message.answer(
        "🚀 Главное меню",
        reply_markup=get_quick_access_keyboard()
    )
