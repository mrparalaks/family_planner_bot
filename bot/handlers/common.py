from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import (
    get_main_menu_keyboard,
    get_settings_keyboard,
    get_quick_access_keyboard,
    get_period_switch_keyboard,
    get_notification_time_inline_keyboard
)
from bot.handlers.events import new_event_start
from bot.services.db_services import db_service
from bot.config import load_config
from bot.handlers.utils import send_main_menu_with_quick_access

router = Router()
config = load_config()

@router.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start."""
    main_menu_message = await message.answer(
        "📅 Добро пожаловать в семейный планировщик!",
        reply_markup=get_main_menu_keyboard()
    )
    await main_menu_message.answer(
        "🚀 Главное меню",
        reply_markup=get_quick_access_keyboard()
    )


@router.message(F.text == "Новое событие")
async def new_event_handler(message: Message, state: FSMContext):
    """Перенаправляем в логику добавления события."""
    await new_event_start(message, state)

@router.message(F.text == "Настройки")
async def settings_handler(message: Message):
    """Обработчик кнопки 'Настройки'."""
    await message.answer("Выберите настройку:", reply_markup=get_settings_keyboard())

@router.callback_query(F.data == "notification_settings")
async def notification_settings_callback(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Настройки уведомлений'."""
    await callback.message.answer(
        "Выберите время уведомлений:",
        reply_markup=get_notification_time_inline_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("notification_"))
async def notification_time_handler(callback: CallbackQuery):
    """Обработчик выбора времени уведомлений."""
    notification_time_mapping = {
        "notification_10_min": "00:10",
        "notification_30_min": "00:30",
        "notification_1_hour": "01:00",
        "notification_1_day": "24:00"
    }
    notification_time = notification_time_mapping[callback.data]
    db_service.set_user_notification_time(callback.from_user.id, notification_time)
    await callback.message.answer(
        f"Время уведомлений установлено: за {notification_time} до события."
    )
    await send_main_menu_with_quick_access(callback.message)
    await callback.answer()

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_callback(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Назад'."""
    await send_main_menu_with_quick_access(callback.message)
    await callback.answer()

@router.message(Command("set_family_chat"))
async def set_family_chat(message: Message):
    """Устанавливает идентификатор семейного чата."""
    if message.from_user.id in config.bot.admin_ids:
        chat_id = message.chat.id
        db_service.set_family_chat_id(chat_id)
        await message.answer(f"Семейный чат установлен: {chat_id}")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")

@router.callback_query(F.data == "quick_new_event")
async def quick_new_event(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки 'Новое событие'."""
    from bot.handlers.events import new_event_start
    await new_event_start(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "quick_my_events")
async def quick_my_events(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Мои события'."""
    await callback.message.answer("Выберите период для просмотра:", reply_markup=get_period_switch_keyboard())
    await callback.answer()

@router.callback_query(F.data == "quick_family_events")
async def quick_family_events(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Семейный календарь'."""
    await callback.message.answer("Выберите период для просмотра:", reply_markup=get_period_switch_keyboard())
    await callback.answer()

@router.callback_query(F.data == "quick_settings")
async def quick_settings(callback: CallbackQuery):
    """Обработчик инлайн-кнопки 'Настройки'."""
    await callback.message.answer(
        "Выберите настройку:",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer()
