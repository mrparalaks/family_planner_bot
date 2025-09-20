from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создаёт клавиатуру главного меню."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новое событие")],
            [KeyboardButton(text="Мой календарь"), KeyboardButton(text="Семейный календарь")],
            [KeyboardButton(text="Настройки")]
        ],
        resize_keyboard=True,
    )
    return keyboard

def get_period_keyboard():
    """Создает клавиатуру для выбора периода."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="День"), KeyboardButton(text="Неделя"), KeyboardButton(text="Месяц")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )
    return keyboard

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру для настроек."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Настройки уведомлений", callback_data="notification_settings"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu"),
            ]
        ]
    )
    return keyboard

def get_notification_time_keyboard():
    """Создает клавиатуру для выбора времени уведомлений."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10 минут"), KeyboardButton(text="30 минут")],
            [KeyboardButton(text="1 час"), KeyboardButton(text="1 день")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )
    return keyboard

def get_quick_access_keyboard() -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру для быстрого доступа к функциям."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Новое событие", callback_data="quick_new_event"),
                InlineKeyboardButton(text="🔄 Мои события", callback_data="quick_my_events"),
            ],
            [
                InlineKeyboardButton(text="👨‍👩‍👧‍👦 Семейный календарь", callback_data="quick_family_events"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="quick_settings"),
            ]
        ]
    )
    return keyboard

def get_period_switch_keyboard() -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру для переключения между режимами просмотра."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 День", callback_data="view_day"),
                InlineKeyboardButton(text="📆 Неделя", callback_data="view_week"),
                InlineKeyboardButton(text="🗓️ Месяц", callback_data="view_month"),
            ]
        ]
    )
    return keyboard

def get_event_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру для работы с событием."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Редактировать", callback_data=f"edit_event_{event_id}"),
                InlineKeyboardButton(text="Удалить", callback_data=f"delete_event_{event_id}"),
            ]
        ]
    )
    return keyboard

def get_notification_time_inline_keyboard() -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру для выбора времени уведомлений."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="10 минут", callback_data="notification_10_min"),
                InlineKeyboardButton(text="30 минут", callback_data="notification_30_min"),
            ],
            [
                InlineKeyboardButton(text="1 час", callback_data="notification_1_hour"),
                InlineKeyboardButton(text="1 день", callback_data="notification_1_day"),
            ]
        ]
    )
    return keyboard
