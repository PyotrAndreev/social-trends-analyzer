import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI
from config_reader import settings
from source.handlers import callbacks
from source.handlers import commands
from source.handlers import messages
from source.handlers import states
from source.utils import registration
from database.db_init import init_db
from SPY_service.database.database import init_ads_db
from uvicorn import Config, Server
from SPY_service.api.endpoints import channel

bot = Bot(token=settings.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
app = FastAPI()
app.include_router(channel.router, prefix="/channels", tags=["channels"])


async def start_fastapi():
    config = Config(app=app, host="127.0.0.1", port=8000, log_level="info")
    server = Server(config)
    await server.serve()


def include_all_routers(dp):
    dp.include_router(callbacks.router)
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    dp.include_router(states.router)
    dp.include_router(registration.router)


async def main():
    init_db()
    init_ads_db()

    try:
        if await bot.get_webhook_info():
            await bot.delete_webhook(drop_pending_updates=True)

        include_all_routers(dp)

        await asyncio.gather(
            start_fastapi(),
            dp.start_polling(bot)
        )
    except Exception as e:
        print(f"Ошибка при запуске: {e}")


if __name__ == "__main__":
    asyncio.run(main())
