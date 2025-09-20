from datetime import datetime, timedelta
from aiogram import Bot
from bot.models.event import Event
from bot.services.db_services import db_service


async def send_weekly_summary(bot: Bot):
    """Отправляет еженедельное резюме событий в семейный чат."""
    family_chat_id = db_service.get_family_chat_id()
    if not family_chat_id:
        print("Семейный чат не настроен.")
        return

    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    events = db_service.get_events()
    weekly_events = [
        event for event in events
        if week_start.date() <= datetime.strptime(event.date, "%d.%m.%Y").date() <= week_end.date()
    ]

    if not weekly_events:
        await bot.send_message(chat_id=family_chat_id, text="На этой неделе нет запланированных событий.")
    else:
        summary = "📅 Еженедельное резюме событий:\n\n"
        for event in weekly_events:
            try:
                user = await bot.get_chat(event.author_id)
                user_name = user.first_name
            except Exception:
                user_name = f"User {event.author_id}"

            summary += f"📌 {event.date} {event.time} | {event.description} (автор: {user_name})\n"

        await bot.send_message(chat_id=family_chat_id, text=summary)

async def notify_new_event(bot: Bot, event: Event):
    """Отправляет уведомление о новом событии в семейный чат."""
    family_chat_id = db_service.get_family_chat_id()
    if family_chat_id:
        try:
            user = await bot.get_chat(event.author_id)
            user_name = user.first_name
        except Exception:
            user_name = f"User {event.author_id}"

        await bot.send_message(
            chat_id=family_chat_id,
            text=f"⚠️ Новое событие от {user_name}:\n"
                 f"📌{event.description}\n"
                 f"📅 Дата: {event.date}\n"
                 f"⏰ Время: {event.time}"
        )