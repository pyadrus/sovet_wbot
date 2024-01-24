from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.keyboards import create_contact_keyboard
from services.database import insert_user_data_to_database
from system.dispatcher import dp, bot


class MakingAnOrder(StatesGroup):
    """Создание класса состояний"""
    write_name = State()  # Имя
    write_surname = State()  # Фамилия
    phone_input = State()  # Передача номера телефона кнопкой
    data_input = State()  # Дата записи


@dp.callback_query_handler(lambda c: c.data == 'sign_up_for_classes')
async def sign_up_for_classes_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик команды /sign_up_for_classes"""
    await state.finish()

    text_mes = ("📅 Введите дату записи в формате дд.мм.гггг:\n"
                "Пример: 01.01.2022")
    await bot.send_message(callback_query.from_user.id, text_mes)
    await MakingAnOrder.data_input.set()


@dp.message_handler(state=MakingAnOrder.data_input)
async def agree_handler(message: types.Message, state: FSMContext):
    data_input = message.text
    await state.update_data({'data_input': data_input})  # Wrap 'data' in a dictionary
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
    data_input = user_data.get('data_input', 'не указан')  # Fix the key here
    user_id = message.from_user.id  # Получение ID аккаунта Telegram
    # Составьте подтверждающее сообщение
    text_mes = (f"🤝 Рады познакомиться {name} {surname}! 🤝\n"
                "Ваши регистрационные данные:\n\n"
                f"✅ Ваше Имя: {name}\n"
                f"✅ Ваша Фамилия: {surname}\n"
                f"✅ Ваш номер телефона: {phone_number}\n"
                f"✅ Ваша Дата записи: {data_input}\n\n"  # Fix the key here
                "Для возврата нажмите /start")

    insert_user_data_to_database(user_id, name, surname, phone_number, data_input)  # Fix the key here
    await state.finish()  # Завершаем текущее состояние машины состояний
    await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию

    await bot.send_message(message.from_user.id, text_mes)  # Сообщение пользователю

    text_mes_admin = (f"Пользователь {name} {surname} записался на занятие\n"
                      "Регистрационные данные пользователя:\n\n"
                      f"✅ Имя: {name}\n"
                      f"✅ Фамилия: {surname}\n"
                      f"✅ Номер телефона: {phone_number}\n"
                      f"✅ Дата записи: {data_input}\n\n")
    await bot.send_message(chat_id=535185511, text=text_mes_admin)  # Отправка данных администратору бота


def register_my_details_handler():
    """Регистрируем handlers для 'Записаться'"""
    dp.register_message_handler(sign_up_for_classes_handler)
