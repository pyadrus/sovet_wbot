from aiogram import executor
from loguru import logger

from handlers.admin_handlers.admin_handlers import register_admin_greeting_handler
from handlers.my_details_handlers import register_my_details_handler
from handlers.send_start import register_handlers_send_start
from handlers.timetable_of_classes import register_handlers_timetable_of_classes
from system.dispatcher import dp

logger.add("setting/log/log.log")


def main() -> None:
    """Запуск бота https://t.me/oxy_center_krd_bot"""
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as error:
        logger.exception(error)

    register_handlers_timetable_of_classes()
    register_handlers_send_start()
    register_my_details_handler()
    register_admin_greeting_handler()


if __name__ == '__main__':
    try:
        main()  # Запуск бота
    except Exception as e:
        logger.exception(e)
