import configparser
import json
import logging
import os

from aiogram import Bot
from aiogram import executor
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from loguru import logger

logger.add("setting/log/log.log")

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

# Словарь для хранения текста от админа
admin_texts = {}


def load_bot_info():
    """Загрузка информации из JSON-файла"""
    with open("bot_info.json", 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # bot_info = data.get('bot_info', bot_info)
    return data


def save_bot_info(data):
    """Сохранение информации в JSON-файл"""
    with open("bot_info.json", 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    """Обработчик команды /start"""
    # global bot_info
    # with open("media/photos/greeting.jpg", "rb") as photo_file:  # Загружаем фото для поста
    data = load_bot_info()
    await bot.send_message(message.from_user.id, text=data, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.message_handler(commands=['edit'])
async def edit_info(message: types.Message):
    """Обработчик команды /edit (только для админа)"""
    logger.info(f"Админ {ADMIN_USER_ID} попытался редактировать информацию.")
    if message.from_user.id == int(ADMIN_USER_ID):
        await message.answer("Введите новый текст, используя разметку HTML.")
        admin_texts[message.from_user.id] = True
    else:
        await message.reply("У вас нет прав на выполнение этой команды.")


@dp.message_handler(lambda message: message.from_user.id == ADMIN_USER_ID and message.from_user.id in admin_texts)
async def update_info(message: types.Message):
    """Обработчик текстовых сообщений (для админа, чтобы обновить информацию)"""
    text = message.html_text
    bot_info = text
    admin_texts.pop(message.from_user.id, None)  # Убираем режим редактирования
    save_bot_info(bot_info)  # Сохраняем информацию в JSON
    await message.reply("Информация обновлена.", parse_mode=ParseMode.HTML)


PHOTO_FOLDER = 'media/photos/'  # Путь к папке, где будет храниться фото


@dp.message_handler(commands=['edit_photo'])
async def edit_photo_command(message: types.Message):
    await message.answer("Пожалуйста, отправьте новое фото для замены greeting.jpg")


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def replace_photo(message: types.Message):
    # Сохраняем присланное фото в папку с тем же именем
    new_photo_path = os.path.join(PHOTO_FOLDER, 'greeting.jpg')
    await message.photo[-1].download(new_photo_path)
    await message.answer("Фото успешно заменено!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
