import argparse
import requests
import urllib.parse
import os
import re
from tqdm import tqdm

class YandexDiskDownloader:
    def __init__(self, link, download_location, custom_name=None):
        self.link = link
        self.download_location = os.path.expanduser(download_location)
        self.custom_name = custom_name

    def safe_file_name(self, name):
        safe_name = re.sub(r'[\/:*?"<>|]', '_', name)
        try:
            with open(os.path.join(self.download_location, safe_name), 'w') as test_file:
                pass
            os.remove(os.path.join(self.download_location, safe_name))
        except OSError:
            print(f"Warning: The file name {name} contains unsupported characters or is invalid. Using safe name: {safe_name}")
            return safe_name
        return name

    def download(self):
        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)

        if response.status_code == 404:
            print(f"Error: Unable to fetch download URL for {self.link}. Status code: 404.")
            return

        response_json = response.json()
        download_url = response_json.get("href")
        if not download_url:
            print(f"Error: Download URL not found in the response for {self.link}")
            return

        original_file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
        file_extension = os.path.splitext(original_file_name)[1]
        file_name = self.custom_name + file_extension if self.custom_name else original_file_name
        safe_file_name = self.safe_file_name(file_name)
        save_path = os.path.join(self.download_location, safe_file_name)

        os.makedirs(self.download_location, exist_ok=True)

        download_response = requests.get(download_url, stream=True)
        total_size = int(download_response.headers.get('content-length', 0))

        with open(save_path, "wb") as file, tqdm(total=total_size, unit='B', unit_scale=True, desc=safe_file_name, dynamic_ncols=True) as pbar:
            for chunk in download_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))

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
    parser.add_argument('positional_link', nargs='?', help='Link for Yandex Disk URL (optional if -l is used)')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL')
    parser.add_argument('-d', '--download_location', type=str, help='Download location on your PC', default=os.getcwd())
    parser.add_argument('-f', '--file', type=str, help='Path to file with Yandex Disk URLs')

    args = parser.parse_args()

    # Приоритизация ссылки: сначала аргумент -l, затем позиционный аргумент
    link = args.link or args.positional_link

    if args.file:
        download_from_file(args.file, args.download_location)
    elif link:
        downloader = YandexDiskDownloader(link, args.download_location)
        downloader.download()
    else:
        print("Error: You must provide either a link or a file containing links.")
