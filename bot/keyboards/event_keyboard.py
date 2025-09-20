from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

def get_time_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора времени с шагом в 15 минут."""
    keyboard_buttons = []

    # Генерируем кнопки времени с 7:00 до 23:00 с шагом в 15 минут
    for hour in range(7, 24):
        for minute in [0, 15, 30, 45]:
            time_str = f"{hour:02d}:{minute:02d}"
            keyboard_buttons.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))

    # Делим кнопки на ряды по 4 штуки
    keyboard_rows = []
    for i in range(0, len(keyboard_buttons), 4):
        row = keyboard_buttons[i:i + 4]
        keyboard_rows.append(row)

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    return keyboard
# Календарь
calendar = SimpleCalendar()
