import argparse
import requests
import urllib.parse
import os
import sys
import locale
import re
from tqdm import tqdm

class Localization:
    def __init__(self):
        self.set_locale()

    def set_locale(self):
        self.current_locale = locale.getdefaultlocale()[0]

    def is_ru_locale(self):
        return self.current_locale == 'ru_RU'

    def get_message(self, message_key):
        messages = {
            'safe_name_warning': {
                'en': "Warning: The file name {name} contains unsupported characters or is invalid. Using safe name: {safe_name}",
                'ru': "Warning: Имя файла {name} содержит неподдерживаемые символы или является недопустимым. Используется безопасное имя: {safe_name}"
            },
            'locale_not_utf8': {
                'en': "Current locale does not support UTF-8. Setting locale to en_US.UTF-8.",
                'ru': "Текущая локаль не поддерживает UTF-8. Устанавливаю локаль en_US.UTF-8."
            },
            'locale_set_error': {
                'en': "Unable to set locale to en_US.UTF-8. Ensure that the required locale is installed on your system.",
                'ru': "Не удалось установить локаль en_US.UTF-8. Убедитесь, что требуемая локаль установлена в вашей системе."
            },
            'download_url_not_found': {
                'en': "Error: Download URL not found in the response for {link}",
                'ru': "Error: URL для загрузки не найден в ответе для {link}"
            },
            'file_not_found': {
                'en': "Error: No downloadable file found with the name {original_file_name} in the provided link: {link}",
                'ru': "Error: Не найден файл с именем {original_file_name} в предоставленной ссылке: {link}"
            },
            'download_complete': {
                'en': "Download complete.",
                'ru': "Загрузка завершена."
            },
            'provide_link_or_file': {
                'en': "Error: You must provide either a link or a file containing links.",
                'ru': "Ошибка: Вы должны указать либо ссылку, либо файл со ссылками."
            },
            'resource_fetch_error': {
                'en': "Error: Unable to fetch resource details for {higher_level_link}. Status code: {status_code}",
                'ru': "Error: Не удалось получить данные ресурса для {higher_level_link}. Код состояния: {status_code}"
            },
            'arg_help': {
                'en': {
                    'positional_link': 'Link for Yandex Disk URL (optional if -l is used)',
                    'link': 'Link for Yandex Disk URL',
                    'download_location': 'Download location on your PC',
                    'file': 'Path to file with Yandex Disk URLs'
                },
                'ru': {
                    'positional_link': 'Ссылка на Яндекс.Диск (опционально, если используется -l)',
                    'link': 'Ссылка на Яндекс.Диск',
                    'download_location': 'Место сохранения на вашем ПК',
                    'file': 'Путь к файлу со ссылками на Яндекс.Диск'
                }
            }
        }

        language = 'ru' if self.is_ru_locale() else 'en'
        return messages[message_key][language]

if __name__ == "__main__":
    localization = Localization()

    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('positional_link', nargs='?', help=localization.get_message('arg_help')['positional_link'])
    parser.add_argument('-l', '--link', type=str, help=localization.get_message('arg_help')['link'])
    parser.add_argument('-d', '--download_location', type=str, help=localization.get_message('arg_help')['download_location'], default=os.getcwd())
    parser.add_argument('-f', '--file', type=str, help=localization.get_message('arg_help')['file'])

    args = parser.parse_args()

    # Приоритизация ссылки: сначала аргумент -l, затем позиционный аргумент
    link = args.link or args.positional_link

    if args.file:
        download_from_file(args.file, args.download_location)
    elif link:
        downloader = YandexDiskDownloader(link, args.download_location)
        downloader.download()
    else:
        print(localization.get_message('provide_link_or_file'))
