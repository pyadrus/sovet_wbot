import json


def load_bot_info(file_name):
    """Загрузка информации из JSON-файла"""
    with open(file_name, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def save_bot_info(file_name, data):
    """Сохранение информации в JSON-файл"""
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
