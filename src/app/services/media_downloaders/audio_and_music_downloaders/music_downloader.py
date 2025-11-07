import asyncio
from typing import Any, Optional

from shazamio import Shazam
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_audio_file_name


class MusicDownloader:
    def __init__(self):
        self.shazam = Shazam()

    async def find_song_name_by_video_audio_voice_video_note(self, media_path: str) -> str:
        try:
            # Agar recognize sync bo'lsa, asyncio.to_thread ishlatamiz
            out = await asyncio.to_thread(self.shazam.recognize, media_path)
            track = out.get("track", {})
            title = track.get("title", "")
            subtitle = track.get("subtitle", "")
            music_title = f"{title} {subtitle}".strip()
            return music_title
        except Exception as e:
            print("ERROR in Shazam recognize:", e)
            return ""

    async def download_music_from_youtube(self, video_id: str) -> Optional[tuple[str, str]]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        music_output_path = f"./media/audios/{get_audio_file_name()}"
        yt_dlp_opts = {
            "format": "bestaudio/best",
            "outtmpl": music_output_path,
            "quiet": True,
            "no_warnings": True,
        }

        def download_sync():
            with YoutubeDL(yt_dlp_opts) as ydl:
                return ydl.extract_info(video_url, download=True)

        try:
            info = await asyncio.to_thread(download_sync)

            if not info:
                return None

            title = info["entries"][0]["title"] if "entries" in info else info.get("title", "")

            return music_output_path, title
        except Exception as e:
            print("ERROR in YouTube download:", e)
            return None
