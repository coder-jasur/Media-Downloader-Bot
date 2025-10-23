from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher


class YouTubeDownloaders:
    def __init__(self):
        self.yt_dlp = YoutubeDL()
        self.searchs = YouTubeSearcher()

    def youtube_video_and_shorts_downloader(self, video_url: str):
        video_path = f"./media/videos/{get_video_file_name()}"
        errors = []
        try:
            ydl_opts = {
                "format": "best[ext=mp4]",
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
            print(222)



            video_data = self.searchs.get_media_info(video_url)
            print(video_data)

            video_filesize = video_data.get("filesize_mb")

            if video_filesize and video_filesize > 2000:
                errors.append("video_file_is_so_big")

            if not video_data:
                errors.append("error_in_downloading")
            print(errors)
            return video_path, errors
        except Exception as e:
            print("ERROR", e)
            return None
