import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot.models.event import Event, UserSettings, BotSettings
from bot.models.base import Base



# Модель события для SQLite
class DBEvent(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    time = Column(String(5), nullable=False)   # "HH:MM"
    description = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)
    notification_time = Column(String(5), nullable=True)  # "HH:MM"

# Класс для работы с базой данных
class DatabaseService:
    def __init__(self, db_url: str = "sqlite:///database/family_planner.db"):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # Создаём таблицы, если их нет

    def add_event(self, event: Event) -> int:
        """Добавляет событие в базу данных."""
        with self.Session() as session:
            db_event = DBEvent(
                date=event.date,
                time=event.time,
                description=event.description,
                author_id=event.author_id,
                notification_time=event.notification_time,
            )
            session.add(db_event)
            session.commit()
            return db_event.id  # type: ignore[reportReturnType]

    def get_events(self, author_id: int | None = None) -> list[Event]:
        """Возвращает список событий."""
        with self.Session() as session:
            query = session.query(DBEvent)
            if author_id:
                query = query.filter(DBEvent.author_id == author_id)
            db_events = query.all()
            return [
                Event(
                    id=event.id,  # type: ignore
                    date=event.date,  # type: ignore
                    time=event.time,  # type: ignore
                    description=event.description,  # type: ignore
                    author_id=event.author_id,  # type: ignore
                    notification_time=event.notification_time,  # type: ignore
                )
                for event in db_events
            ]

    def get_event_by_id(self, event_id: int) -> Event | None:
        """Получает событие по ID."""
        with self.Session() as session:
            db_event = session.query(DBEvent).filter(DBEvent.id == event_id).first()
            if db_event:
                return Event(
                    id=db_event.id,
                    date=db_event.date,
                    time=db_event.time,
                    description=db_event.description,
                    author_id=db_event.author_id,
                    notification_time=db_event.notification_time,
                )
            return None

    def update_event(self, event: Event):
        """Обновляет событие в базе данных."""
        with self.Session() as session:
            db_event = session.query(DBEvent).filter(DBEvent.id == event.id).first()
            if db_event:
                db_event.date = event.date
                db_event.time = event.time
                db_event.description = event.description
                session.commit()

    def delete_event(self, event_id: int):
        """Удаляет событие из базы данных."""
        with self.Session() as session:
            db_event = session.query(DBEvent).filter(DBEvent.id == event_id).first()
            if db_event:
                session.delete(db_event)
                session.commit()

    def set_user_notification_time(self, user_id: int, notification_time: str):
        """Сохраняет время уведомлений для пользователя."""
        session = self.Session()
        try:
            user_setting = session.query(UserSettings).get(user_id)
            if not user_setting:
                user_setting = UserSettings(user_id=user_id, notification_time=notification_time)
                session.add(user_setting)
            else:
                user_setting.notification_time = notification_time
            session.commit()
        finally:
            session.close()

    def get_user_notification_time(self, user_id: int) -> str:
        """Получает время уведомлений для пользователя."""
        session = self.Session()
        try:
            user_setting = session.query(UserSettings).get(user_id)
            return user_setting.notification_time if user_setting else "01:00"
        finally:
            session.close()

    def set_family_chat_id(self, chat_id: int):
        """Сохраняет идентификатор семейного чата."""
        session = self.Session()
        try:
            bot_setting = session.query(BotSettings).first()
            if not bot_setting:
                bot_setting = BotSettings(id=1, family_chat_id=chat_id)
                session.add(bot_setting)
            else:
                bot_setting.family_chat_id = chat_id
            session.commit()
        finally:
            session.close()

    def get_family_chat_id(self) -> int | None:
        """Получает идентификатор семейного чата."""
        session = self.Session()
        try:
            bot_setting = session.query(BotSettings).first()
            return bot_setting.family_chat_id if bot_setting else None
        finally:
            session.close() 
            
    def backup_database(self, backup_dir: str = "backups"):
        """Создаёт резервную копию базы данных."""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        db_path = "database/family_planner.db"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(backup_dir, f"family_planner_{timestamp}.db")

        try:
            shutil.copy2(db_path, backup_path)
            print(f"Резервная копия базы данных создана: {backup_path}")
        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")   
    
    def cleanup_old_backups(backup_dir: str = "backups", days_to_keep: int = 30):
        """Удаляет старые резервные копии."""
        now = datetime.now()
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_time).days > days_to_keep:
                os.remove(file_path)
                print(f"Удалена старая резервная копия: {file_path}")

# Создаём экземпляр сервиса
db_service = DatabaseService()
