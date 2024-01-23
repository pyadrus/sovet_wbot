import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from loguru import logger

from keyboards.keyboards import create_greeting_keyboard
from services.database import recording_data_of_users_who_launched_the_bot
from services.services import load_bot_info, save_bot_info
from system.dispatcher import ADMIN_USER_ID, dp, bot, admin_texts

logger.add("setting/log/log.log")


@dp.message_handler(commands=['start'])
async def send_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.finish()  # Завершаем текущее состояние машины состояний
    await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию
    # Получаем информацию о пользователе
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    join_date = message.date.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Пользователь {username} ({user_id}) запустил бота в {join_date}")

    # Записываем информацию о пользователе в базу данных
    recording_data_of_users_who_launched_the_bot(user_id, username, first_name, last_name, join_date)

    data = load_bot_info(file_name='services/bot_info.json')
    await bot.send_message(message.from_user.id, text=data, parse_mode=ParseMode.HTML, disable_web_page_preview=True,
                           reply_markup=create_greeting_keyboard())


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
    save_bot_info(file_name='services/bot_info.json', data=bot_info)  # Сохраняем информацию в JSON
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


def register_handlers_send_start():
    dp.register_message_handler(send_start)
    dp.register_message_handler(edit_info)
    dp.register_message_handler(update_info)
