import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config
from aiogram.client.default import DefaultBotProperties
from aiogram import F

from handlers import INFO_CLIENT


logging.basicConfig(level=logging.INFO)
async def main():
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    dp = Dispatcher()
    dp.include_router(INFO_CLIENT.router)

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)




if __name__ == "__main__":
    asyncio.run(main())