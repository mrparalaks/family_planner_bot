from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новое событие")],
        [KeyboardButton(text="Мои события"), KeyboardButton(text="Семейный календарь")],
    ],
    resize_keyboard=True,
)
