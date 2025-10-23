from typing import Dict, List, Any, Optional
from yt_dlp import YoutubeDL
import yt_dlp


class YouTubeSearcher:

    def __init__(self):
        self.yt_dlp = yt_dlp

    def get_media_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)

                if "entries" in info:
                    info = info["entries"][0]

                filesize = info.get("filesize") or info.get("filesize_approx")

                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
                }
        except Exception as e:
            print(f"[YouTubeSearcher] get_media_info error: {e}")
            return None

    def search_music(self, query: str, max_count: int = 5) -> List[Dict[str, Any]] | None:
        ydl_opts = {
            "quiet": True,
            "match_filter": self.yt_dlp.utils.match_filter_func("duration < 600"),
            "skip_download": True,
        }

        search_query = f"ytsearch{max_count}:{query}"
        results = []

        try:
            with YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(search_query, download=False)
                entries = data.get("entries", [])

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

                    duration = entry.get("duration", 0)
                    results.append({
                        "title": entry.get("title", ""),
                        "id": entry.get("id", ""),
                        "duration": f"{duration // 60}:{duration % 60:02d}" if duration else None,
                        "filesize_mb": round(filesize / (1024 * 1024), 2) if filesize else None,
                    })

        except Exception as e:
            print(f"[YouTubeSearcher] search_music error: {e}")
            return None

        return results


