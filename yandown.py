import argparse
import requests
import urllib.parse
import os
import sys
import locale
import re
import time
from tqdm import tqdm

class YandexDiskDownloader:
    def __init__(self, link, download_location, custom_name=None):
        self.link = link
        self.download_location = os.path.expanduser(download_location)
        self.custom_name = custom_name

    def safe_file_name(self, name):
        """
        Replaces unsafe characters in the file name and handles Unicode issues.
        """
        safe_name = re.sub(r'[\/:*?"<>|]', '_', name)
        
        try:
            with open(os.path.join(self.download_location, safe_name), 'w') as test_file:
                pass
            os.remove(os.path.join(self.download_location, safe_name))
        except OSError:
            if self.is_ru_locale():
                print(f"Warning: Имя файла {name} содержит неподдерживаемые символы или является недопустимым. Используется безопасное имя: {safe_name}")
            else:
                print(f"Warning: The file name {name} contains unsupported characters or is invalid. Using safe name: {safe_name}")
            return safe_name
        return name

    def set_locale(self):
        """
        Sets the locale to en_US.UTF-8 if the current locale is not UTF-8.
        """
        try:
            current_locale = locale.getdefaultlocale()
            if 'UTF-8' not in current_locale[1]:
                if self.is_ru_locale():
                    print("Текущая локаль не поддерживает UTF-8. Устанавливаю локаль en_US.UTF-8.")
                else:
                    print("Current locale does not support UTF-8. Setting locale to en_US.UTF-8.")
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            if self.is_ru_locale():
                print("Не удалось установить локаль en_US.UTF-8. Убедитесь, что требуемая локаль установлена в вашей системе.")
            else:
                print("Unable to set locale to en_US.UTF-8. Ensure that the required locale is installed on your system.")
            sys.exit(1)

    def is_ru_locale(self):
        """
        Checks if the current locale is Russian (ru_RU).
        """
        current_locale = locale.getdefaultlocale()
        return current_locale[0] == 'ru_RU'

    def download(self):
        self.set_locale()

        def get_file_name_from_link(link):
            return link.split('/')[-1]

        original_file_name = get_file_name_from_link(self.link)

        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)

        if response.status_code == 404:
            if self.is_ru_locale():
                print(f"Error: Не удалось получить URL загрузки для {self.link}. Код состояния: 404. Попробую другой метод.")
            else:
                print(f"Error: Unable to fetch download URL for {self.link}. Status code: 404. Trying another method.")
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
                    if self.is_ru_locale():
                        print(f"Error: Не удалось получить данные ресурса для {higher_level_link}. Код состояния: {response.status_code}")
                    else:
                        print(f"Error: Unable to fetch resource details for {higher_level_link}. Status code: {response.status_code}")
                    return

            if not download_url:
                if self.is_ru_locale():
                    print(f"Error: Не найден файл с именем {original_file_name} в предоставленной ссылке: {self.link}")
                else:
                    print(f"Error: No downloadable file found with the name {original_file_name} in the provided link: {self.link}")
                return
        else:
            response_json = response.json()
            download_url = response_json.get("href")
            if not download_url:
                if self.is_ru_locale():
                    print(f"Error: URL для загрузки не найден в ответе для {self.link}")
                else:
                    print(f"Error: Download URL not found in the response for {self.link}")
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

        if self.is_ru_locale():
            print("Загрузка завершена.")
        else:
            print("Download complete.")

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
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('link', nargs='?', type=str, help='Link for Yandex Disk URL (default)')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL')
    parser.add_argument('-d', '--download_location', type=str, help='Download location on your PC')
    parser.add_argument('-f', '--file', type=str, help='Path to file with Yandex Disk URLs')

    args = parser.parse_args()

    if args.file:
        download_location = args.download_location if args.download_location else os.getcwd()
        download_from_file(args.file, download_location)
    elif args.link or args.link is None:
        link = args.link if args.link else args.link
        download_location = args.download_location if args.download_location else os.getcwd()
        downloader = YandexDiskDownloader(link, download_location)
        downloader.download()
    elif len(sys.argv) == 2:
        link = sys.argv[1]
        download_location = os.getcwd()
        downloader = YandexDiskDownloader(link, download_location)
        downloader.download()
    else:
        if locale.getdefaultlocale()[0] == 'ru_RU':
            print("Ошибка: Вы должны указать либо ссылку, либо файл со ссылками.")
        else:
            print("Error: You must provide either a link or a file containing links.")
