from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode

from keyboards.keyboards import create_contact_keyboard
from services.database import count_users_by_order, insert_user_data_to_database
from system.dispatcher import dp, bot


class MakingAnOrder(StatesGroup):
    """Создание класса состояний"""
    write_name = State()  # Имя
    write_surname = State()  # Фамилия
    phone_input = State()  # Передача номера телефона кнопкой
    data_input = State()  # Дата записи


@dp.callback_query_handler(lambda c: c.data == 'sign_up_for_classes')
async def data_input(message: types.Message, state: FSMContext):
    """Обработчик команды /sign_up_for_classes"""
    await state.reset_state()
    await MakingAnOrder.data_input.set()
    text_mes = ("📅 Введите дату записи в формате дд.мм.гггг:\n"
                "Пример: 01.01.2022")
    await bot.send_message(message.from_user.id, text_mes)


@dp.message_handler(state=MakingAnOrder.data_input)
async def agree_handler(message: types.Message, state: FSMContext):
    await state.reset_state()
    await MakingAnOrder.write_surname.set()
    text_mes = ("👥 Введите вашу фамилию (желательно кириллицей):\n"
                "Пример: Петров, Иванова, Сидоренко")
    await bot.send_message(message.from_user.id, text_mes)


@dp.message_handler(state=MakingAnOrder.write_surname)
async def write_surname_handler(message: types.Message, state: FSMContext):
    surname = message.text
    await state.update_data(surname=surname)
    await MakingAnOrder.write_name.set()
    text_mes = ("👤 Введите ваше имя (желательно кириллицей):\n"
                "Пример: Иван, Ольга, Анастасия")
    await bot.send_message(message.from_user.id, text_mes)


@dp.message_handler(state=MakingAnOrder.write_name)
async def write_name_handler(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    sign_up_texts = (
        "Для ввода номера телефона вы можете поделиться номером телефона, нажав на кнопку или ввести его вручную.\n\n"
        "Чтобы ввести номер вручную, просто отправьте его в текстовом поле.")
    contact_keyboard = create_contact_keyboard()
    await bot.send_message(message.from_user.id, sign_up_texts,
                           reply_markup=contact_keyboard,  # Set the custom keyboard
                           parse_mode=types.ParseMode.HTML,
                           disable_web_page_preview=True)
    await MakingAnOrder.phone_input.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=MakingAnOrder.phone_input)
async def handle_contact(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await handle_confirmation(message, state)


@dp.message_handler(lambda message: message.text and not message.contact, state=MakingAnOrder.phone_input)
async def handle_phone_text(message: types.Message, state: FSMContext):
    phone_number = message.text
    await state.update_data(phone_number=phone_number)
    await handle_confirmation(message, state)


async def handle_confirmation(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove(selective=False)  # Remove the keyboard
    await message.answer("Спасибо за предоставленные данные.", reply_markup=markup)
    user_data = await state.get_data()  # Извлечение пользовательских данных из состояния
    surname = user_data.get('surname', 'не указан')
    name = user_data.get('name', 'не указан')
    phone_number = user_data.get('phone_number', 'не указан')
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = message.from_user.id  # Получение ID аккаунта Telegram
    # Составьте подтверждающее сообщение
    text_mes = (f"🤝 Рады познакомиться {name} {surname}! 🤝\n"
                "Ваши регистрационные данные:\n\n"
                f"✅ <b>Ваше Имя:</b> {name}\n"
                f"✅ <b>Ваша Фамилия:</b> {surname}\n"
                f"✅ <b>Ваш номер телефона:</b> {phone_number}\n"
                f"✅ <b>Ваша Дата регистрации:</b> {registration_date}\n\n"
                "Вы можете изменить свои данные в меню \"Мои данные\".\n\n"
                "Для возврата нажмите /start")
    count = count_users_by_order()
    insert_user_data_to_database(count + 1, user_id, name, surname, phone_number, registration_date)
    await state.finish()  # Завершаем текущее состояние машины состояний
    await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию
    # Создаем клавиатуру с помощью my_details() (предполагается, что она существует)
    await bot.send_message(message.from_user.id, text_mes)


def register_my_details_handler():
    """Регистрируем handlers для 'Записаться'"""
    dp.register_message_handler(data_input)
