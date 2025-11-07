import asyncio
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher
from src.app.utils.enums.error import DownloadError


class YouTubeDownloaders:
    def __init__(self):
        self.searchs = YouTubeSearcher()

    async def youtube_video_and_shorts_downloader(self, video_url: str):
        video_path = f"./media/videos/{get_video_file_name()}"
        errors = []

        try:
            ydl_opts = {
                "format": "best[ext=mp4]",
                "outtmpl": video_path,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [{"key": "FFmpegMetadata"}],
            }

            # yt_dlp ni async qilib ishga tushirish
            def download_video():
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

            await asyncio.to_thread(download_video)

            # media info olishni ham async qilish
            video_data = await asyncio.to_thread(self.searchs.get_media_info, video_url)

            video_filesize = video_data.get("filesize_mb") if video_data else None

            if video_filesize and video_filesize > 2000:
                errors.append(DownloadError.FILE_TOO_BIG)

            if not video_data:
                errors.append(DownloadError.DOWNLOAD_ERROR)

            return video_path, errors

        except Exception as e:
            print("ERROR in youtube_video_and_shorts_downloader:", e)
            return None, [DownloadError.DOWNLOAD_ERROR]
