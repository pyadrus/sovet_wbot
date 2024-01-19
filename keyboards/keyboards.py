from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def create_greeting_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для приветственного сообщения 👋"""
    greeting_keyboard = InlineKeyboardMarkup()
    ask_anonymous_question_button = InlineKeyboardButton(text='Расписание занятий',
                                                         callback_data='timetable_of_classes')
    sign_up_button = InlineKeyboardButton(text='📝 Записаться на занятия',
                                          callback_data='sign_up_for_classes')

    greeting_keyboard.row(ask_anonymous_question_button)  # Задать анонимный вопрос
    greeting_keyboard.row(sign_up_button)  # Записаться

    return greeting_keyboard


def create_contact_keyboard():
    """Создает клавиатуру для отправки контакта"""
    contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    send_contact_button = KeyboardButton("📱 Отправить", request_contact=True)

    contact_keyboard.add(send_contact_button)
    return contact_keyboard


if __name__ == '__main__':
    create_greeting_keyboard()
