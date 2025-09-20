from aiogram import Bot
from datetime import datetime

async def send_notification(user_id: int, event_description: str):
    """Отправляет уведомление пользователю."""
    bot = Bot.get_current()
    await bot.send_message(
        user_id,
        f"⏰ Напоминание: через час начнётся событие: {event_description}"
    )
