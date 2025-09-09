#  pip install auto-py-to-exe
import yt_dlp
import sys

def download_video(video_url):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'ffmpeg_location': 'C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            print(f"Скачивание завершено: {info['title']}")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    else:
        video_url = input("Введите URL YouTube видео: ")
    download_video(video_url)
    input("Нажмите Enter, чтобы выйти...")