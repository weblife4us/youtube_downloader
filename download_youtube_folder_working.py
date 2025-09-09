# auto-py-to-exe
#  pip install auto-py-to-exe
#  pip install yt-dlp
#  pip install PyInstaller

import yt_dlp
import sys
import os
import argparse
from datetime import datetime

def get_unique_folder(base_folder):
    folder = base_folder
    counter = 1
    while os.path.exists(folder):
        folder = f"{base_folder}_{counter}"
        counter += 1
    return folder

def download_video(video_url, output_dir=None):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',  # Максимальное качество с аудио
            'outtmpl': os.path.join(output_dir if output_dir else '', '%(title)s.%(ext)s'),                         # Имя файла
            'merge_output_format': 'mp4',                           # Объединять в MP4
            'ffmpeg_location':'C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe',                         # Путь к ffmpeg
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            print(f"Скачивание завершено: {info['title']}")
    except Exception as e:
        print(f"Ошибка при скачивании {video_url}: {str(e)}")
        print("Продолжаем со следующим URL...")

def download_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file if line.strip()]
        if not urls:
            print("Файл пуст или содержит только пустые строки.")
            return
        # Создание папки для загрузки с текущей датой и временем
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        date_str = datetime.now().strftime("%y-%m-%d %H-%M")
        base_folder = os.path.join(os.path.dirname(file_path), f"{base_name}_{date_str}")
        output_dir = get_unique_folder(base_folder)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Файлы будут сохранены в папку: {output_dir}")
        print(f"Найдено {len(urls)} URL-адресов для скачивания.")
        for i, url in enumerate(urls, 1):
            print(f"\nСкачивание {i}/{len(urls)}: {url}")
            download_video(url, output_dir=output_dir)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скачивание YouTube видео")
    parser.add_argument('--file', type=str, help="Путь к файлу с URL-адресами")
    parser.add_argument('url', type=str, nargs='?', help="Один URL для скачивания")
    args = parser.parse_args()

    if args.file:
        download_from_file(args.file)
    elif args.url:
        download_video(args.url)
    else:
        file_path = input("Введите путь к файлу с URL (или оставьте пустым для одного URL): ")
        if file_path:
            download_from_file(file_path)
        else:
            video_url = input("Введите URL YouTube видео: ")
            if video_url:
                download_video(video_url)
            else:
                print("URL не указан. Завершение работы.")

    input("Нажмите Enter, чтобы выйти...")