from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler):
        self.scheduler = scheduler

    async def __call__(self, handler, event: TelegramObject, data):
        data["scheduler"] = self.scheduler
        return await handler(event, data)
