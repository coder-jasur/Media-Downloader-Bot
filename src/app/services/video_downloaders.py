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

    def instagram_post_downloader(self, post_url: str) -> str and list:

        post_path = "./media/photos/%(id)s.%(ext)s"
        errors = []
        posts_file_path = []

        ydl_opts = {
            "outtmpl": post_path,
            "format": "mp4",
            "noplaylist": False,
            "quiet": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([post_url])

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([post_url])
                info = ydl.extract_info(post_url)
                if "entries" in info:
                    for item in info["entries"]:
                        file_path = ydl.prepare_filename(item)
                        posts_file_path.append(file_path)
                else:
                    file_path = ydl.prepare_filename(info)
                    posts_file_path.append(file_path)
        except Exception as e:
            errors.append(str(e))

        highlights_data = self.searchs.get_media_info(post_url)

        highlights_filesize = highlights_data.get("filesize_mb")

        if highlights_filesize and highlights_filesize > 2000:
            errors.append("video_file_is_so_big")

        if not highlights_data:
            errors.append("error_in_downloading")

        return posts_file_path, errors


    def instagram_highlights_downloader(self, highlights_url: str):
        errors = []
        highlights_file_path = []
        highlights_path = "./media/videos/%(id)s.%(ext)s"

        ydl_opts = {
            "outtmpl": highlights_path,
            "format": "mp4",
            "noplaylist": False,
            "quiet": False,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([highlights_url])
                info = ydl.extract_info(highlights_url)
                if "entries" in info:
                    for item in info["entries"]:
                        file_path = ydl.prepare_filename(item)
                        highlights_file_path.append(file_path)
                else:
                    file_path = ydl.prepare_filename(info)
                    highlights_file_path.append(file_path)
        except Exception as e:
            errors.append(str(e))

        highlights_data = self.searchs.get_media_info(highlights_url)

        highlights_filesize = highlights_data.get("filesize_mb")

        if highlights_filesize and highlights_filesize > 2000:
            errors.append("video_file_is_so_big")

        if not highlights_data:
            errors.append("error_in_downloading")

        return highlights_file_path, errors


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
        print(1111111)

        ydl_opts = {
            "format": "bestvideo*+bestaudio/best",
            "outtmpl": video_path,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegMetadata"
            }],
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

        save_path = f"./media/videos/{output_file_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    print(f"ERROR: {resp.status}")
                    return
                data = await resp.json()

        error = []

        video_download_url = data.get("non_watermarked_url")
        print(data.get("file_size"))

        file_size = int(data.get("file_size")) / 1024 * 1024


        if not video_download_url:
            error.append("error_in_downloading")
            return video_download_url, error

        if file_size and file_size > 2000:
            error.append("video_file_is_so_big")

        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    async with aiofiles.open(save_path, "wb") as f:
                        await f.write(await response.read())

        return save_path, error
