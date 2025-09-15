import aiofiles
import aiohttp
from yt_dlp import YoutubeDL

from src.app.services.searchs import Searchs


class VideoDownloaders:

    def __init__(self):
        self.searchs = Searchs()

    def instagram_video_downloader(self, video_url: str, output_file_name: str) -> str and list:

        video_path = f"./media/videos/{output_file_name}"

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": video_path,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }]
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        error = []

        video_data = self.searchs.get_media_info(video_url)

        video_filesize = video_data.get("filesize_mb")

        if video_filesize and video_filesize > 2000:
            error.append("video_file_is_so_big")

        if not video_data:
            error.append("error_in_downloading")

        return video_path, error


    def instagram_photo_downloader(self, photo_url: str, output_file_name: str) -> str and list:

        photo_path = f"./media/photos/{output_file_name}"

        ydl_opts = {
            "outtmpl": photo_path,
            "skip_download": False
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([photo_url])

        error = []

        photo_data = self.searchs.get_media_info(photo_url)

        photo_filesize = photo_data.get("filesize_mb")

        if photo_filesize and photo_filesize > 2000:
            error.append("photo_file_is_so_big")

        if not photo_data:
            error.append("error_in_downloading")

        return photo_path, error

    def youtube_video_downloader(self, video_url: str, output_file_name: str) -> str and list:

        video_path = f"./media/videos/{output_file_name}"

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": video_path,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }]
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        error = []

        video_data = self.searchs.get_media_info(video_url)

        video_filesize = video_data.get("filesize_mb")

        if video_filesize and video_filesize > 2000:
            error.append("video_file_is_so_big")

        if not video_data:
            error.append("error_in_downloading")

        return video_path, error

    async def tiktok_video_downloader(self, video_url: str, output_file_name: str) -> str and list:
        api_url = f"https://tiktok-dl.akalankanime11.workers.dev/?url={video_url}"
        print(1)
        save_path = f"./media/videos/{output_file_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    print(f"ERROR: {resp.status}")
                    return
                data = await resp.json()
        print(2)

        error = []

        video_download_url = data.get("non_watermarked_url")
        print(data.get("file_size"))

        file_size = int(data.get("file_size")) / 1024 * 1024

        print(3)

        if not video_download_url:
            error.append("error_in_downloading")
            return video_download_url, error

        if file_size and file_size > 2000:
            error.append("video_file_is_so_big")
        print(3)

        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, "wb") as f:
                        await f.write(await response.read())

        print(44)
        return save_path, error
