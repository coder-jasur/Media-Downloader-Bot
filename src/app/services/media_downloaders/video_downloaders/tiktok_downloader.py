import asyncio

import aiohttp
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.utils.enums.error import DownloadError


class TikTokDownloader:
    def __init__(self):
        self.aiohttp = aiohttp

    async def tiktok_video_downloader(self, video_url: str):
        file_name = get_video_file_name()
        video_output_path = f"./media/videos/{file_name}"
        errors = []
        try:
            def tiktok_downloader():
                ydl_opts = {"format": "best", "outtmpl": video_output_path}
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)

                    return info

            data  = await asyncio.to_thread(tiktok_downloader)

            if int(data["filesize"] / 1024 / 1024) > 2000:
                errors.append(DownloadError.FILE_TOO_BIG)
                return None, errors

            if not data:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors



            return video_output_path, errors

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(str(e))
            return None, errors