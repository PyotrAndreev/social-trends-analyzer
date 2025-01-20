import asyncio

from config import TOKEN

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from handlers import router

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass