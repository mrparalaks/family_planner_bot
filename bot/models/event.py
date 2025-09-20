from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from bot.models.base import Base

@dataclass
class Event:
    """Модель события."""
    id: int | None
    date: str
    time: str
    description: str
    author_id: int
    notification_time: str | None

class UserSettings(Base):
    """Модель для таблицы user_settings."""
    __tablename__ = "user_settings"
    user_id = Column(Integer, primary_key=True)
    notification_time = Column(String(5), nullable=False)

class BotSettings(Base):
    """Модель для настроек бота, включая семейный чат."""
    __tablename__ = "bot_settings"
    id = Column(Integer, primary_key=True)
    family_chat_id = Column(Integer, nullable=True)  # Telegram ID семейного чата