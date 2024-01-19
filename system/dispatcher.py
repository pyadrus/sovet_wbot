import configparser
import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена
ADMIN_USER_ID = config.get('ADMIN_USER_ID', 'ADMIN_USER_ID')

# Инициализация бота и диспетчера
bot = Bot(token=bot_token)
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования
dp.middleware.setup(LoggingMiddleware())

admin_texts = {}  # Словарь для хранения текста от админа
