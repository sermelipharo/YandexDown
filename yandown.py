import argparse
import requests
import urllib.parse
import os
import sys


class YandexDiskDownloader:
    def __init__(self, link, download_location, custom_name=None):
        self.link = link
        self.download_location = os.path.expanduser(download_location)
        self.custom_name = custom_name

    def download(self):
        def get_file_name_from_link(link):
            return link.split('/')[-1]

        original_file_name = get_file_name_from_link(self.link)

        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)

        if response.status_code == 404:
            print(f"Error: Unable to fetch download URL for {self.link}. Status code: 404. Trying another method.")
            higher_level_link = '/'.join(self.link.split('/')[:-1])
            url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={higher_level_link}"
            response = requests.get(url)
            if response.status_code == 200:
                response_json = response.json()
                items = response_json.get('_embedded', {}).get('items', [])
                if items:
                    for item in items:
                        if item['type'] == 'file' and item['name'] == original_file_name:
                            download_url = item['file']
                            break
                    else:
                        print(f"Error: No downloadable file found with the name {original_file_name} in the provided link: {self.link}")
                        return
                else:
                    print(f"Error: No items found in the provided link: {higher_level_link}")
                    return
            else:
                print(f"Error: Unable to fetch resource details for {higher_level_link}. Status code: {response.status_code}")
                return
        else:
            response_json = response.json()
            download_url = response_json.get("href")
            if not download_url:
                print(f"Error: Download URL not found in the response for {self.link}")
                return

        original_file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
        file_extension = os.path.splitext(original_file_name)[1]
        file_name = self.custom_name + file_extension if self.custom_name else original_file_name
        save_path = os.path.join(self.download_location, file_name)

        # Ensure the download directory exists
        os.makedirs(self.download_location, exist_ok=True)

        with open(save_path, "wb") as file:
            download_response = requests.get(download_url, stream=True)
            for chunk in download_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    file.flush()

        print(f"Download complete: {file_name}")


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
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL')
    parser.add_argument('-d', '--download_location', type=str, help='Download location in PC')
    parser.add_argument('-f', '--file', type=str, help='Path to file with Yandex Disk URLs')

    args = parser.parse_args()

    if args.file:
        if not args.download_location:
            print("Error: You must provide a download location when using a file.")
        else:
            download_from_file(args.file, args.download_location)
    elif args.link:
        download_location = args.download_location if args.download_location else os.getcwd()
        downloader = YandexDiskDownloader(args.link, download_location)
        downloader.download()
    elif len(sys.argv) == 2:
        download_location = os.getcwd()
        link = sys.argv[1]
        downloader = YandexDiskDownloader(link, download_location)
        downloader.download()
    else:
        print("Error: You must provide either a link or a file containing links.")
