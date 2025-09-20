import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from bot.models.event import Event
from datetime import datetime, timedelta

# Путь к файлу с учётными данными
CREDENTIALS_FILE = "bot/google/credentials.json"
TOKEN_FILE = "bot/google/token.json"

# Области доступа
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    """Получает учётные данные для доступа к Google Calendar."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds

def add_event_to_google_calendar(event: Event):
    """Добавляет событие в Google Calendar."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Преобразуем дату и время в формат ISO 8601
    date_format = "%d.%m.%Y"
    time_format = "%H:%M"
    date_obj = datetime.strptime(event.date, date_format)
    time_obj = datetime.strptime(event.time, time_format)

    # Формируем дату и время начала и окончания
    start_datetime = datetime.combine(date_obj.date(), time_obj.time())
    end_datetime = start_datetime + timedelta(hours=1)

    # Формируем событие
    google_event = {
        "summary": event.description,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Europe/Moscow",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Europe/Moscow",
        },
    }

    # Добавляем событие в календарь
    event_result = (
        service.events()
        .insert(calendarId="primary", body=google_event)
        .execute()
    )
    return event_result.get("htmlLink")

def delete_event_from_google_calendar(event: Event):
    """Удаляет событие из Google Calendar."""
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)

    # Получаем список всех событий из календаря
    events_result = service.events().list(
        calendarId='primary',
        q=event.description,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if events:
        # Удаляем первое найденное событие с таким описанием
        event_id = events[0]['id']
        service.events().delete(calendarId='primary', eventId=event_id).execute()