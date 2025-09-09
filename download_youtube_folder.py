"""
YouTube Video Downloader
========================
Современный инструмент для скачивания видео с YouTube и других платформ
Использует yt-dlp (версия 2025.9.5) - самую актуальную библиотеку

Требования:
- pip install yt-dlp
- pip install auto-py-to-exe (для создания exe)
- pip install PyInstaller (для создания exe)
- ffmpeg (автоматически ищется в PATH)
- pip install --upgrade auto-py-to-exe
- pip install --upgrade pyinstaller
"""

import yt_dlp
import sys
import os
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class YouTubeDownloader:
    """Класс для скачивания видео с YouTube и других платформ"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        
    def _find_ffmpeg(self) -> Optional[str]:
        """Автоматический поиск ffmpeg в системе"""
        # Проверяем стандартные пути
        possible_paths = [
            'C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe',
            'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
            'C:\\ffmpeg\\bin\\ffmpeg.exe'
        ]
        
        # Проверяем ffmpeg в PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
            
        # Проверяем стандартные пути
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        print("⚠️  Предупреждение: ffmpeg не найден. Некоторые видео могут не объединиться.")
        return None
    
    def _progress_hook(self, d):
        """Hook для отображения прогресса загрузки"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                print(f"\r📥 Загрузка: {percent:.1f}% ({d['downloaded_bytes']} / {d['total_bytes']} байт)", end='')
            elif '_percent_str' in d:
                print(f"\r📥 Загрузка: {d['_percent_str']}", end='')
        elif d['status'] == 'finished':
            print(f"\n✅ Загрузка завершена: {d['filename']}")
    
    def get_video_info(self, video_url: str) -> Optional[dict]:
        """Получение информации о видео без загрузки"""
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)
        except Exception as e:
            print(f"❌ Ошибка получения информации о видео: {str(e)}")
            return None

    def download_video(self, video_url: str, output_dir: Optional[str] = None, 
                      quality: str = 'best', audio_only: bool = False) -> bool:
        """
        Скачивание одного видео
        
        Args:
            video_url: URL видео
            output_dir: Папка для сохранения
            quality: Качество видео ('best', 'worst', '720p', '1080p', etc.)
            audio_only: Скачивать только аудио
        """
        try:
            # Настройки загрузчика
            ydl_opts = {
                'outtmpl': os.path.join(output_dir or '', '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'extractaudio': audio_only,
                'audioformat': 'mp3' if audio_only else None,
            }
            
            # Настройка качества и формата
            if audio_only:
                ydl_opts['format'] = 'bestaudio/best'
            else:
                if quality == 'best':
                    ydl_opts['format'] = 'bestvideo[ext=mp4][height<=?2160]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
                elif quality == 'worst':
                    ydl_opts['format'] = 'worst'
                elif quality in ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']:
                    height = quality[:-1]
                    ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                else:
                    ydl_opts['format'] = quality
                
                ydl_opts['merge_output_format'] = 'mp4'
            
            # Путь к ffmpeg если найден
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            
            # Получаем информацию о видео
            info = self.get_video_info(video_url)
            if info:
                title = info.get('title', 'Неизвестно')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Неизвестно')
                
                print(f"\n📺 Название: {title}")
                print(f"👤 Автор: {uploader}")
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    print(f"⏱️  Длительность: {minutes:02d}:{seconds:02d}")
            
            # Скачивание
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
            return True
            1
        except Exception as e:
            print(f"\n❌ Ошибка при скачивании {video_url}: {str(e)}")
            return False

    def get_unique_folder(self, base_folder: str) -> str:
        """Создание уникальной папки с номером, если папка уже существует"""
        folder = base_folder
        counter = 1
        while os.path.exists(folder):
            folder = f"{base_folder}_{counter}"
            counter += 1
        return folder

    def download_from_file(self, file_path: str, quality: str = 'best', 
                          audio_only: bool = False) -> dict:
        """
        Скачивание видео из файла со списком URL
        
        Returns:
            dict: Статистика загрузки (успешно, ошибки, общее количество)
        """
        stats = {'total': 0, 'success': 0, 'errors': 0, 'error_urls': []}
        
        try:
            # Чтение файла
            with open(file_path, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            
            if not urls:
                print("❌ Файл пуст или содержит только пустые строки.")
                return stats
            
            # Создание папки для загрузки
            base_name = Path(file_path).stem
            date_str = datetime.now().strftime("%y-%m-%d_%H-%M")
            base_folder = Path(file_path).parent / f"{base_name}_{date_str}"
            output_dir = self.get_unique_folder(str(base_folder))
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"\n📁 Файлы будут сохранены в: {output_dir}")
            print(f"📋 Найдено {len(urls)} URL-адресов для скачивания.")
            print(f"🎯 Качество: {quality}")
            if audio_only:
                print("🎵 Режим: Только аудио (MP3)")
            print("-" * 60)
            
            stats['total'] = len(urls)
            
            # Скачивание каждого URL
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] 🔗 {url}")
                
                success = self.download_video(url, output_dir, quality, audio_only)
                if success:
                    stats['success'] += 1
                    print("✅ Успешно!")
                else:
                    stats['errors'] += 1
                    stats['error_urls'].append(url)
                    print("❌ Ошибка!")
                    
                # Небольшая пауза между загрузками
                if i < len(urls):
                    print("⏱️  Пауза 2 секунды...")
                    import time
                    time.sleep(2)
            
            # Итоговая статистика
            print("\n" + "="*60)
            print("📊 ИТОГИ ЗАГРУЗКИ:")
            print(f"✅ Успешно загружено: {stats['success']}")
            print(f"❌ Ошибок: {stats['errors']}")
            print(f"📁 Папка загрузки: {output_dir}")
            
            if stats['error_urls']:
                print(f"\n❌ URL с ошибками:")
                for url in stats['error_urls']:
                    print(f"   • {url}")
            
        except FileNotFoundError:
            print(f"❌ Файл {file_path} не найден.")
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {str(e)}")
        
        return stats


def main():
    """Главная функция программы"""
    parser = argparse.ArgumentParser(
        description="YouTube Video Downloader v2.0 - Современный загрузчик видео",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python download_youtube_folder.py "https://youtube.com/watch?v=..."
  python download_youtube_folder.py --file urls.txt --quality 720p
  python download_youtube_folder.py --file urls.txt --audio-only
  python download_youtube_folder.py "https://youtube.com/watch?v=..." --quality 1080p
        """
    )
    
    parser.add_argument('url', nargs='?', help='URL видео для скачивания')
    parser.add_argument('--file', '-f', type=str, help='Путь к файлу с URL-адресами')
    parser.add_argument('--quality', '-q', type=str, default='best',
                       choices=['best', 'worst', '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'],
                       help='Качество видео (по умолчанию: best)')
    parser.add_argument('--audio-only', '-a', action='store_true',
                       help='Скачивать только аудио в формате MP3')
    
    args = parser.parse_args()
    
    print("🎥 YouTube Video Downloader v2.0")
    print("=" * 40)
    print("📦 Используется yt-dlp версии 2025.9.5")
    print()
    
    downloader = YouTubeDownloader()
    
    try:
        if args.file:
            # Скачивание из файла
            if not os.path.exists(args.file):
                print(f"❌ Файл {args.file} не существует!")
                return
            
            stats = downloader.download_from_file(args.file, args.quality, args.audio_only)
            
        elif args.url:
            # Скачивание одного URL
            print(f"🔗 URL: {args.url}")
            print(f"🎯 Качество: {args.quality}")
            if args.audio_only:
                print("🎵 Режим: Только аудио (MP3)")
            
            success = downloader.download_video(args.url, quality=args.quality, audio_only=args.audio_only)
            if success:
                print("\n✅ Скачивание завершено успешно!")
            else:
                print("\n❌ Ошибка при скачивании!")
                
        else:
            # Интерактивный режим
            print("🔧 Интерактивный режим")
            print("-" * 20)
            
            choice = input("Выберите режим:\n1 - Скачать один URL\n2 - Скачать из файла\nВаш выбор (1/2): ").strip()
            
            if choice == '2':
                file_path = input("📁 Введите путь к файлу с URL: ").strip()
                if not file_path:
                    print("❌ Путь к файлу не указан!")
                    return
                if not os.path.exists(file_path):
                    print(f"❌ Файл {file_path} не существует!")
                    return
                
                # Выбор качества
                print("\n🎯 Доступные качества:")
                qualities = ['best', '1080p', '720p', '480p', '360p', 'worst']
                for i, q in enumerate(qualities, 1):
                    print(f"{i} - {q}")
                
                q_choice = input(f"Выберите качество (1-{len(qualities)}, по умолчанию 1): ").strip()
                try:
                    quality = qualities[int(q_choice)-1] if q_choice else 'best'
                except (ValueError, IndexError):
                    quality = 'best'
                
                # Выбор только аудио
                audio_choice = input("🎵 Скачивать только аудио? (y/n, по умолчанию n): ").strip().lower()
                audio_only = audio_choice in ['y', 'yes', 'да']
                
                stats = downloader.download_from_file(file_path, quality, audio_only)
                
            else:
                video_url = input("🔗 Введите URL YouTube видео: ").strip()
                if not video_url:
                    print("❌ URL не указан!")
                    return
                
                # Выбор качества
                print("\n🎯 Доступные качества:")
                qualities = ['best', '1080p', '720p', '480p', '360p', 'worst']
                for i, q in enumerate(qualities, 1):
                    print(f"{i} - {q}")
                
                q_choice = input(f"Выберите качество (1-{len(qualities)}, по умолчанию 1): ").strip()
                try:
                    quality = qualities[int(q_choice)-1] if q_choice else 'best'
                except (ValueError, IndexError):
                    quality = 'best'
                
                # Выбор только аудио
                audio_choice = input("🎵 Скачивать только аудио? (y/n, по умолчанию n): ").strip().lower()
                audio_only = audio_choice in ['y', 'yes', 'да']
                
                success = downloader.download_video(video_url, quality=quality, audio_only=audio_only)
                if success:
                    print("\n✅ Скачивание завершено успешно!")
                else:
                    print("\n❌ Ошибка при скачивании!")
    
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем!")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {str(e)}")
    finally:
        input("\n⏭️  Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()