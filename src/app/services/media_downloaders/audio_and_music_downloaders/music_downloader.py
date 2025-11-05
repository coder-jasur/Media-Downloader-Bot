import asyncio
from typing import Any

from shazamio import Shazam
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_audio_file_name


class MusicDownloader:
    def __init__(self):
        self.shazam = Shazam()
        self.youtubedl = YoutubeDL

    async def find_song_name_by_video_audio_voice_video_note(self, media_path: str) -> str:

        out = await self.shazam.recognize(media_path)
        track = out.get("track", {})
        title = track.get("title", "")
        subtitle = track.get("subtitle", "")
        music_title = f"{title} {subtitle}".strip()

        return music_title


    async def download_music_from_youtube(self, video_id: str) -> tuple[str, Any] | None:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        music_output_path = f"./media/audios/{get_audio_file_name()}"
        yt_dlp_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(music_output_path),
            "quiet": True,
            "no_warnings": True,
        }

        def download_sync():
            with YoutubeDL(yt_dlp_opts) as ydl:
                data = ydl.extract_info(video_url, download=True)
                return data
        try:
            info = await asyncio.to_thread(download_sync)

            if not info:
                return None
            title = info["entries"][0]["title"] if "entries" in info else info["title"]

            return str(music_output_path) , title
        except Exception as e:
            print("ERROR", e)
            return None