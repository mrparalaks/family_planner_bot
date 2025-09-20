from datetime import datetime, timedelta
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar
from bot.keyboards.event_keyboard import calendar, get_time_keyboard
from bot.services.db_services import db_service
from bot.models.event import Event
from bot.services.google_calendar import add_event_to_google_calendar, delete_event_from_google_calendar
from bot.services.notification_service import send_notification
from bot.keyboards.main_menu import get_main_menu_keyboard, get_period_keyboard, get_period_switch_keyboard, get_event_keyboard
from bot.config import load_config
from bot.handlers.utils import send_main_menu_with_quick_access
from bot.services.family_chat_service import notify_new_event


router = Router()

class EventForm(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    entering_description = State()

class MyCalendarStates(StatesGroup):
    choosing_period = State()

class FamilyCalendarStates(StatesGroup):
    choosing_period = State()

@router.message(F.text == "Новое событие")
async def new_event_start(message: types.Message, state: FSMContext):
    """Начало добавления нового события."""
    calendar_markup = await calendar.start_calendar()
    await message.answer("Выберите дату события:", reply_markup=calendar_markup)
    await state.set_state(EventForm.choosing_date)

@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """Обработка выбора даты."""
    # Проверяем, нажали ли на Cancel
    if hasattr(callback_data, 'act') and callback_data.act == "CANCEL":
        await callback.message.answer("Добавление события отменено.")
        await state.clear()
        await send_main_menu_with_quick_access(callback.message)  # Возвращаемся в главное меню с инлайн-кнопками
        await callback.answer()
        return
    # Если выбрана дата
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        selected_date = date.strftime("%d.%m.%Y")
        await callback.message.edit_text(f"Вы выбрали дату: {selected_date}\nТеперь выберите время:")
        await callback.message.answer("Выберите время:", reply_markup=get_time_keyboard())
        await state.update_data(date=selected_date)
        await state.set_state(EventForm.choosing_time)
    await callback.answer()

@router.callback_query(F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора времени."""
    selected_time = callback.data.split("_")[1]
    await callback.message.edit_text(f"Вы выбрали время: {selected_time}\nВведите описание события:")
    await state.update_data(time=selected_time)
    await state.set_state(EventForm.entering_description)
    await callback.answer()

@router.message(EventForm.entering_description)
async def process_description(message: types.Message, state: FSMContext, scheduler: AsyncIOScheduler):
    """Обработка описания события (добавление или редактирование)."""
    description = message.text
    state_data = await state.get_data()
    date = state_data["date"]
    time = state_data["time"]

    # Получаем время уведомлений пользователя
    notification_time_delta = db_service.get_user_notification_time(message.from_user.id)
    hours, minutes = map(int, notification_time_delta.split(":"))
    notification_delta = timedelta(hours=hours, minutes=minutes)

    event_id = state_data.get("event_id")
    if event_id:
        # Редактирование существующего события
        event = Event(
            id=event_id,
            date=date,
            time=time,
            description=description,
            author_id=message.from_user.id,
            notification_time=notification_time_delta
        )
        db_service.update_event(event)
        await message.answer(f"Событие отредактировано!\nДата: {date}\nВремя: {time}\nОписание: {description}")
    else:
        # Добавление нового события
        event = Event(
            id=None,
            date=date,
            time=time,
            description=description,
            author_id=message.from_user.id,
            notification_time=notification_time_delta
        )
        event_id = db_service.add_event(event)
        google_event_link = add_event_to_google_calendar(event)

        event_datetime = datetime.strptime(f"{event.date} {event.time}", "%d.%m.%Y %H:%M")
        notification_time = event_datetime - notification_delta

        scheduler.add_job(
            send_notification,
            "date",
            run_date=notification_time,
            args=[message.from_user.id, event.description],
        )

        await message.answer(
            f"Событие добавлено!\nДата: {date}\nВремя: {time}\nОписание: {description}\n"
            f"Ссылка на событие в Google Calendar: {google_event_link}\n"
            f"Уведомление будет отправлено за {notification_time_delta} до события."
        )
        
        # Отправляем уведомление в семейный чат
        await notify_new_event(message.bot, event)

    await send_main_menu_with_quick_access(message)
    await state.clear()

@router.message(F.text == "Мои события")
async def list_my_events(message: types.Message):
    """Отображает события пользователя в удобном формате."""
    events = db_service.get_events(message.from_user.id)
    if not events:
        await message.answer("У вас нет запланированных событий.")
    else:
        # Сортируем события по дате и времени
        sorted_events = sorted(
            events,
            key=lambda event: datetime.strptime(f"{event.date} {event.time}", "%d.%m.%Y %H:%M")
        )
        await show_events(message, sorted_events, "все события")

@router.message(F.text.in_(["Мой календарь", "Семейный календарь"]))
async def calendar_handler(message: types.Message, state: FSMContext):
    """Обработчик кнопок 'Мой календарь' и 'Семейный календарь'."""
    await message.answer("Выберите период для просмотра:", reply_markup=get_period_keyboard())
    await state.set_state(MyCalendarStates.choosing_period if message.text == "Мой календарь" else FamilyCalendarStates.choosing_period)


def get_event_keyboard(event_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для управления событием."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Редактировать", callback_data=f"edit_event_{event_id}"),
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_event_{event_id}")
        ]
    ])
    return keyboard

@router.callback_query(F.data.startswith("edit_event_"))
async def edit_event(callback: CallbackQuery, state: FSMContext):
    """Обработка запроса на редактирование события."""
    event_id = int(callback.data.split("_")[2])
    event = db_service.get_event_by_id(event_id)

    if event.author_id != callback.from_user.id:
        await callback.answer("Вы не можете редактировать это событие.", show_alert=True)
        return

    # Удаляем старое событие из Google Calendar
    delete_event_from_google_calendar(event)

    await state.update_data(event_id=event_id, date=event.date, time=event.time, description=event.description)
    await callback.message.answer(f"Редактирование события: {event.description}\nВыберите новую дату:")
    calendar_markup = await calendar.start_calendar()
    await callback.message.answer("Выберите новую дату:", reply_markup=calendar_markup)
    await state.set_state(EventForm.choosing_date)
    await callback.answer()

@router.callback_query(F.data.startswith("delete_event_"))
async def delete_event(callback: CallbackQuery):
    """Обработка запроса на удаление события."""
    event_id = int(callback.data.split("_")[2])
    event = db_service.get_event_by_id(event_id)

    if event.author_id != callback.from_user.id:
        await callback.answer("Вы не можете удалить это событие.", show_alert=True)
        return

    # Удаляем событие из Google Calendar
    delete_event_from_google_calendar(event)

    db_service.delete_event(event_id)
    await callback.message.answer(f"Событие '{event.description}' удалено.")
    await callback.answer()

@router.message(MyCalendarStates.choosing_period)
async def my_calendar_period_handler(message: types.Message, state: FSMContext):
    """Обработчик выбора периода для личного календаря."""
    period = message.text
    events = db_service.get_events(message.from_user.id)
    filtered_events = filter_events_by_period(events, period)
    await show_events(message, filtered_events, period)
    await state.clear()
    await send_main_menu_with_quick_access(message)
#    await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard())

@router.message(FamilyCalendarStates.choosing_period)
async def family_calendar_period_handler(message: types.Message, state: FSMContext):
    """Обработчик выбора периода для семейного календаря."""
    period = message.text
    events = db_service.get_events()
    filtered_events = filter_events_by_period(events, period)
    await show_events(message, filtered_events, period)
    await state.clear()
    await send_main_menu_with_quick_access(message)
#    await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard())

def filter_events_by_period(events: list[Event], period: str) -> list[Event]:
    """Фильтрует события по выбранному периоду."""
    now = datetime.now()
    filtered_events = []

    for event in events:
        event_datetime = datetime.strptime(f"{event.date} {event.time}", "%d.%m.%Y %H:%M")

        if period == "День":
            if event_datetime.date() == now.date():
                filtered_events.append(event)
        elif period == "Неделя":
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            if week_start.date() <= event_datetime.date() <= week_end.date():
                filtered_events.append(event)
        elif period == "Месяц":
            if event_datetime.month == now.month and event_datetime.year == now.year:
                filtered_events.append(event)

    return sorted(
        filtered_events,
        key=lambda event: datetime.strptime(f"{event.date} {event.time}", "%d.%m.%Y %H:%M")
    )

@router.message(F.text == "Назад")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    """Возвращает пользователя в главное меню."""
    await state.clear()
    await send_main_menu_with_quick_access(message) 
#    await message.answer("Выберите действие:", reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data.in_(["view_day", "view_week", "view_month"]))
async def view_period(callback: CallbackQuery):
    """Обработчик кнопок переключения режимов просмотра."""
    period_mapping = {
        "view_day": "День",
        "view_week": "Неделя",
        "view_month": "Месяц"
    }
    period = period_mapping[callback.data]
    events = db_service.get_events()
    if not events:
        await callback.message.answer(f"Нет событий за выбранный период: {period}.")
        return
    filtered_events = filter_events_by_period(events, period)
    if not filtered_events:
        await callback.message.answer(f"Нет событий за выбранный период: {period}.")
    else:
        await show_events(callback.message, filtered_events, period)
    await send_main_menu_with_quick_access(callback.message)
    await callback.answer()


async def show_events(message: types.Message, events: list[Event], period: str):
    """Отображает события отдельными сообщениями с кнопками управления."""
    if not events:
        await message.answer(f"Нет событий за {period}.")
        return

    for event in events:
        keyboard = get_event_keyboard(event.id)  # Кнопки "Редактировать" и "Удалить"
        await message.answer(
            f"📅 <b>{event.description}</b>\n"
            f"🗓 Дата: {event.date}\n"
            f"⏰ Время: {event.time}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )