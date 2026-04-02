import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers.start import router as start_router
from app.bot.handlers.account_manage import router as account_manage_router
from app.bot.middlewares.admin import AdminMiddleware
from app.core.config import settings


async def start_bot():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())

    dp.include_router(start_router)
    dp.include_router(account_manage_router)

    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
