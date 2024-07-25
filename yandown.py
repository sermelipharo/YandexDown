import argparse
import requests
import urllib.parse
import os


class YandexDiskDownloader:
    def __init__(self, link, download_location):
        self.link = link
        self.download_location = os.path.expanduser(download_location)

    def download(self):
        url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={self.link}"
        response = requests.get(url)
        download_url = response.json()["href"]
        file_name = urllib.parse.unquote(download_url.split("filename=")[1].split("&")[0])
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
        links = file.readlines()
        
    for link in links:
        link = link.strip()
        if link:
            downloader = YandexDiskDownloader(link, download_location)
            downloader.download()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yandex Disk Downloader')
    parser.add_argument('-l', '--link', type=str, help='Link for Yandex Disk URL')
    parser.add_argument('-d', '--download_location', type=str, help='Download location in PC', required=True)
    parser.add_argument('-f', '--file', type=str, help='Path to file with Yandex Disk URLs')

    args = parser.parse_args()

    if args.file:
        download_from_file(args.file, args.download_location)
    elif args.link:
        downloader = YandexDiskDownloader(args.link, args.download_location)
        downloader.download()
    else:
        print("Error: You must provide either a link or a file containing links.")
