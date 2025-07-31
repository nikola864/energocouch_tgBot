import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, AiohttpWebServer
from aiohttp import web
from config_reader import config
from handlers import INFO_CLIENT

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Порт, который Render передаёт через переменную окружения
PORT = int(config.port.get_secret_value()) if hasattr(config, 'port') else 8080
HOST = "0.0.0.0"

async def on_startup(bot: Bot):
    """
    Вызывается при запуске бота.
    Устанавливает вебхук на URL Render.
    """
    webhook_url = f"https://{config.app_name.get_secret_value()}.onrender.com/webhook"
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    print(f"Webhook установлен на {webhook_url}")

async def on_shutdown(bot: Bot):
    """
    Вызывается при остановке.
    Убирает вебхук (необязательно, но чисто).
    """
    await bot.delete_webhook()

def create_app(bot: Bot, dispatcher: Dispatcher) -> web.Application:
    """
    Создаёт веб-приложение Aiohttp.
    """
    app = web.Application()
    # Обработчик запросов от Telegram
    webhook_handler = SimpleRequestHandler(dispatcher=dispatcher, bot=bot)
    webhook_handler.register(app, path="/webhook")
    return app

async def main():
    # Создаём бота
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем роутер
    dp.include_router(INFO_CLIENT.router)

    # Регистрируем события
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Создаём и запускаем веб-сервер
    app = create_app(bot, dp)
    web.run_app(app, host=HOST, port=PORT)

if __name__ == "__main__":
    asyncio.run(main())