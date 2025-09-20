from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import get_notification_time_keyboard, get_settings_keyboard, get_main_menu_keyboard
from bot.services.db_services import db_service

router = Router()

@router.message(F.text == "Настройки уведомлений")
async def notification_settings_handler(message: Message):
    """Обработчик кнопки 'Настройки уведомлений'."""
    await message.answer("Выберите время уведомления:", reply_markup=get_notification_time_keyboard())

@router.message(F.text.in_(["10 минут", "30 минут", "1 час", "1 день"]))
async def set_notification_time_handler(message: Message):
    """Обработчик выбора времени уведомлений."""
    notification_time = message.text
    time_delta = {
        "10 минут": "00:10",
        "30 минут": "00:30",
        "1 час": "01:00",
        "1 день": "24:00"
    }.get(notification_time, "01:00")

    db_service.set_user_notification_time(message.from_user.id, time_delta)
    await message.answer(f"Время уведомлений установлено: {notification_time} до события.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "Назад")
async def back_to_settings_handler(message: Message):
    """Обработчик кнопки 'Назад' в настройках."""
    await message.answer("Выберите настройку:", reply_markup=get_settings_keyboard())
