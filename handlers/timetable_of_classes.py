from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode
from loguru import logger

from services.services import load_bot_info, save_bot_info
from system.dispatcher import ADMIN_USER_ID, admin_texts
from system.dispatcher import dp, bot


@dp.callback_query_handler(lambda c: c.data == 'timetable_of_classes')
async def timetable_of_classes(message: types.Message):
    """Обработчик команды /start"""
    greeting_keyboard = InlineKeyboardMarkup()
    sign_up_button = InlineKeyboardButton(text='📝 Записаться на занятия',
                                          callback_data='sign_up_for_classes')
    greeting_keyboard.row(sign_up_button)  # Записаться
    data = load_bot_info(file_name='services/timetable_info.json')
    await bot.send_message(message.from_user.id,
                           text=data,
                           parse_mode=ParseMode.HTML,
                           disable_web_page_preview=True,
                           reply_markup=greeting_keyboard)


class EDIT(StatesGroup):
    edit = State()


@dp.message_handler(commands=['edit_timetable'])
async def edit_info_timetable(message: types.Message):
    """Обработчик команды /edit (только для админа)"""
    logger.info(f"Админ {ADMIN_USER_ID} попытался редактировать информацию.")
    if message.from_user.id == int(ADMIN_USER_ID):
        await message.answer("Введите новый текст, используя разметку HTML.")
        # admin_texts[message.from_user.id] = True
        await EDIT.edit.set()
    else:
        await message.reply("У вас нет прав на выполнение этой команды.")


@dp.message_handler(state=EDIT.edit)
async def update_info_timetable(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений (для админа, чтобы обновить информацию)"""
    text = message.html_text
    bot_info = text
    admin_texts.pop(message.from_user.id, None)  # Убираем режим редактирования
    save_bot_info(file_name='services/timetable_info.json', data=bot_info)  # Сохраняем информацию в JSON
    await message.reply("Информация обновлена.", parse_mode=ParseMode.HTML)
    await state.finish()


def register_handlers_timetable_of_classes():
    dp.register_message_handler(timetable_of_classes)
    dp.register_message_handler(edit_info_timetable)
