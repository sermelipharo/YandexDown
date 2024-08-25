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

class YandexDiskDownloader:
    def __init__(self, link, download_location, custom_name=None):
        self.link = link
        self.download_location = os.path.expanduser(download_location)
        self.custom_name = custom_name
        self.localization = Localization()

    def safe_file_name(self, name):
        safe_name = re.sub(r'[\/:*?"<>|]', '_', name)
        
        try:
            with open(os.path.join(self.download_location, safe_name), 'w') as test_file:
                pass
            os.remove(os.path.join(self.download_location, safe_name))
        except OSError:
            print(self.localization.get_message('safe_name_warning').format(name=name, safe_name=safe_name))
            return safe_name
        return name

    def set_locale(self):
        """
        Sets the locale to en_US.UTF-8 if the current locale is not UTF-8.
        """
        try:
            current_locale = locale.getdefaultlocale()
            if 'UTF-8' not in current_locale[1]:
                print(self.localization.get_message('locale_not_utf8'))
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            print(self.localization.get_message('locale_set_error'))
            sys.exit(1)

    def download(self):
        self.set_locale()

        def get_file_name_from_link(link):
            return link.split('/')[-1]

        original_file_name = get_file_name_from_link(self.link)

        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)

        if response.status_code == 404:
            higher_level_link = '/'.join(self.link.split('/')[:-1])
            offset = 0
            limit = 100
            download_url = None

            while True:
                url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={higher_level_link}&limit={limit}&offset={offset}"
                response = requests.get(url)
                if response.status_code == 200:
                    response_json = response.json()
                    items = response_json.get('_embedded', {}).get('items', [])
                    if not items:
                        break

                    for item in items:
                        if item['type'] == 'file' and item['name'] == original_file_name:
                            download_url = item['file']
                            break

                    if download_url:
                        break

                    offset += limit
                else:
                    print(self.localization.get_message('resource_fetch_error').format(higher_level_link=higher_level_link, status_code=response.status_code))
                    return

            if not download_url:
                print(self.localization.get_message('file_not_found').format(original_file_name=original_file_name, link=self.link))
                return
        else:
            response_json = response.json()
            download_url = response_json.get("href")
            if not download_url:
                print(self.localization.get_message('download_url_not_found').format(link=self.link))
                return

        original_file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
        file_extension = os.path.splitext(original_file_name)[1]
        file_name = self.custom_name + file_extension if self.custom_name else original_file_name
        safe_file_name = self.safe_file_name(file_name)
        save_path = os.path.join(self.download_location, safe_file_name)

        # Create download directory if it does not exist
        os.makedirs(self.download_location, exist_ok=True)

        # Start the download with progress tracking
        download_response = requests.get(download_url, stream=True)
        total_size = int(download_response.headers.get('content-length', 0))  # Get file size from headers (if available)

        if total_size == 0:
            # Если общий объем неизвестен, создаем бесконечный прогресс-бар
            with open(save_path, "wb") as file, tqdm(unit='B', unit_scale=True, desc=safe_file_name, dynamic_ncols=True, miniters=1) as pbar:
                for chunk in download_response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        file.flush()
                        pbar.update(len(chunk))
        else:
            # Если общий объем известен, показываем прогресс
            with open(save_path, "wb") as file, tqdm(total=total_size, unit='B', unit_scale=True, desc=safe_file_name, dynamic_ncols=True, miniters=1) as pbar:
                for chunk in download_response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        file.flush()
                        pbar.update(len(chunk))

        print(self.localization.get_message('download_complete'))

def download_from_file(file_path, download_location):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line:
            if ' ' in line:
                link, custom_name = line.split(maxsplit=1)
            elif ',' in line:
                link, custom_name = line.split(',', maxsplit=1)
            elif ';' in line:
                link, custom_name = line.split(';', maxsplit=1)
            else:
                link, custom_name = line, None

            custom_name = custom_name.strip() if custom_name else None
            downloader = YandexDiskDownloader(link, download_location, custom_name)
            downloader.download()

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

