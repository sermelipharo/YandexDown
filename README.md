# Yandex Disk Downloader

[![Yandex Disk](https://img.shields.io/badge/Я.Диск-Unofficial-red.svg?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nNDQnIGhlaWdodD0nNDQnIGZpbGw9J25vbmUnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zyc+PHBhdGggZD0nTTIyIDQzYTIxIDIxIDAgMSAwIDAtNDIgMjEgMjEgMCAwIDAgMCA0MlonIGZpbGw9JyNGODYwNEEnLz48cGF0aCBkPSdNMjUuMyAzNS4xM2g0LjU3VjguODZoLTYuNjZjLTYuNyAwLTEwLjIyIDMuNDQtMTAuMjIgOC41IDAgNC4wMiAxLjkzIDYuNDMgNS4zNyA4Ljg4bC01Ljk5IDguODhoNC45N0wyNCAyNS4xOGwtMi4zMi0xLjU0Yy0yLjgtMS45LTQuMTctMy4zNi00LjE3LTYuNTQgMC0yLjc5IDEuOTctNC42OCA1LjcyLTQuNjhoMi4wNXYyMi43aC4wMVonIGZpbGw9JyNmZmYnLz48L3N2Zz4=)](#) [![Static Badge](https://img.shields.io/badge/python3-grey?style=flat&logo=python&logoColor=white)](#) [![en](https://img.shields.io/badge/lang-en-FF8002.svg)](#english) [![ru](https://img.shields.io/badge/lang-ru-00E153.svg)](#русский)

## English

This script allows downloading files from Yandex Disk using public links. The script can work with a single link or with a text file containing a list of links and file names.

### Requirements

- Python 3.x
- Libraries: `requests`

### Installation

1. Clone the repository or download the script.
2. Install the required libraries:
    ```bash
    pip install requests
    ```

### Usage

#### Download a single file

To download a single file from Yandex Disk, use the following command:

```bash
python yandown.py -l <link> -d <download_location>
```

Or simply:

```bash
python yandown.py <link>
```

#### Download from a file

To download files from a list contained in a text file, use the following command:

```bash
python yandown.py -f <file_path> -d <download_location>
```

The format of the text file should be as follows: one link per line, followed by the file name, separated by a space, comma, or semicolon.

Example `links.txt` file:
```
https://disk.yandex.ru/i/example1 Square
https://disk.yandex.ru/i/example2, Circle
https://disk.yandex.ru/i/example3; Triangle
https://disk.yandex.ru/d/example4
https://disk.yandex.ru/d/example_folder/file.jpg CustomFileName
```

### Command line arguments

- `-l, --link`: Link to a Yandex Disk file.
- `-f, --file`: Path to a text file with Yandex Disk links.
- `-d, --download_location`: Path to save the downloaded files (optional, default is the current directory).

### Examples

#### Download a single file

```bash
python yandown.py -l "https://disk.yandex.ru/i/example1" -d "/path/to/save"
```

#### Download from a file

```bash
python yandown.py -f "/path/to/links.txt" -d "/path/to/save"
```

#### Download a single file to the current directory

```bash
python yandown.py "https://disk.yandex.ru/i/example1"
```

---

## Русский

Этот скрипт позволяет загружать файлы с Яндекс.Диска по публичным ссылкам. Скрипт может работать как с одной ссылкой, так и с текстовым файлом, содержащим список ссылок и названий файлов.

### Требования

- Python 3.x
- Библиотеки: `requests`

### Установка

1. Склонируйте репозиторий или скачайте скрипт.
2. Установите необходимые библиотеки:
    ```bash
    pip install requests
    ```

### Использование

#### Загрузка одного файла

Для загрузки одного файла с Яндекс.Диска используйте следующую команду:

```bash
python yandown.py -l <ссылка> -d <путь_для_сохранения>
```

Или просто:

```bash
python yandown.py <ссылка>
```

#### Загрузка из файла

Для загрузки файлов из списка, содержащегося в текстовом файле, используйте следующую команду:

```bash
python yandown.py -f <путь_к_файлу> -d <путь_для_сохранения>
```

Формат текстового файла должен быть следующим: одна ссылка на строку, за которой может следовать название файла, разделенное пробелом, запятой или точкой с запятой.

Пример файла `links.txt`:
```
https://disk.yandex.ru/i/example1 Квадратик
https://disk.yandex.ru/i/example2, Шарик
https://disk.yandex.ru/i/example3; Треугольник
https://disk.yandex.ru/d/example4
https://disk.yandex.ru/d/example_folder/file.jpg НазваниеФайла
```

### Аргументы командной строки

- `-l, --link`: Ссылка на файл Яндекс.Диска.
- `-f, --file`: Путь к текстовому файлу с ссылками на файлы Яндекс.Диска.
- `-d, --download_location`: Путь для сохранения загруженных файлов (необязательно, по умолчанию текущая директория).

### Примеры

#### Загрузка одного файла

```bash
python yandown.py -l "https://disk.yandex.ru/i/example1" -d "/path/to/save"
```

#### Загрузка из файла

```bash
python yandown.py -f "/path/to/links.txt" -d "/path/to/save"
```

#### Загрузка одного файла в текущую папку

```bash
python yandown.py "https://disk.yandex.ru/i/example1"
```
