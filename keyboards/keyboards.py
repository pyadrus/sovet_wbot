from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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


if __name__ == '__main__':
    create_greeting_keyboard()
