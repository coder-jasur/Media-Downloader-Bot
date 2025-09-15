from typing import List, Dict

import yt_dlp
from yt_dlp import YoutubeDL


class Searchs:

    def __init__(self):
        self.youtubedl = YoutubeDL
    def get_media_info(self, video_url: str) -> Dict:
        with self.youtubedl({}) as ydl:
            info = ydl.extract_info(video_url, download=False)

            if "entries" in info:
                info = info["entries"][0]

            filesize = info.get("filesize") or info.get("filesize_approx")

            return {
                "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
            }

    def search_music(self, music_text_or_avtor: str, max_count: int = 5) -> List[Dict]:
        ydl_opts = {
            "quiet": True,
            "match_filter": yt_dlp.utils.match_filter_func("duration < 600"),
            "skip_download": True,
        }

        search_query = f"ytsearch{max_count}:{music_text_or_avtor}"
        musics = []

        with self.youtubedl(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            entries = result.get("entries", [])

            for entry in entries:
                filesize = None
                if entry.get("formats"):
                    best_audio = max(
                        (f for f in entry["formats"] if f.get("filesize")),
                        key=lambda f: f["filesize"],
                        default=None
                    )
                    if best_audio:
                        filesize = best_audio["filesize"]

                duration = entry.get("duration")
                musics.append({
                    "title": entry.get("title", ""),
                    "id": entry.get("id", ""),
                    "duration": f"{duration // 60}:{duration % 60:02d}" if duration else None,
                    "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
                })

        return musics