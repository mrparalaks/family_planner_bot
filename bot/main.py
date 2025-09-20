import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from bot.config import Config, load_config
from bot.handlers import common, events
from bot.handlers.notification_settings import router as notification_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.middlewares.scheduler import SchedulerMiddleware
from bot.services.family_chat_service import send_weekly_summary
from bot.services.db_services import db_service

logger = logging.getLogger(__name__)

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    config: Config = load_config()
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(events.router)
    dp.include_router(notification_router)
    dp.include_router(common.router)

    scheduler = AsyncIOScheduler()
    # Задача для еженедельного резюме
    scheduler.add_job(send_weekly_summary, "cron", day_of_week="sun", hour=21, args=[bot])
    # Задача для резервного копирования базы данных (например, каждый день в 3:00)
    scheduler.add_job(
        lambda: [db_service.backup_database(), db_service.cleanup_old_backups()],
        "cron",
        hour=3,
        minute=0
    )
    scheduler.start()

    dp.update.middleware(SchedulerMiddleware(scheduler))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
