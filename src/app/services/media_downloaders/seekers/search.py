import asyncio
import time
from typing import Dict, List, Any, Optional

import aiohttp
from yt_dlp import YoutubeDL

from src.app.core.config import Settings
from src.app.utils.enums.error import DownloadError

LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"

_API_CACHE: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 60 * 60


class YouTubeSearcher:

    def __init__(self):
        self.settings = Settings()

    async def get_media_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        try:
            def extract_info():
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

            return await asyncio.to_thread(extract_info)

        except Exception as e:
            print("ERROR", e)
            return None

    async def search_music(
            self,
            query: str,
            max_count: int = 5
    ) -> tuple[List[Dict[str, Any]], Any, List[str]] | None:

        def extract_search():
            ydl_opts = {
                "quiet": True,
                "match_filter": lambda info: info.get('duration', 0) < 600,
                "skip_download": True,
            }

            search_query = f"ytsearch{max_count}:{query}"
            results = []
            errors = []

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    data = ydl.extract_info(search_query, download=False)

                    if not data:
                        errors.append(DownloadError.MUSIC_NOT_FOUND)
                        return [], [], errors

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

                return results, entries, errors

            except Exception as e:
                print("ERROR", e)
                return [], [], [str(e)]

        return await asyncio.to_thread(extract_search)

    def cache_get(self, key: str):
        rec = _API_CACHE.get(key)
        if not rec:
            return None
        ts, value = rec
        if time.time() - ts > CACHE_TTL_SECONDS:
            _API_CACHE.pop(key, None)
            return None
        return value

    def cache_set(self, key: str, value):
        _API_CACHE[key] = (time.time(), value)

    async def get_top_music(self, limit: int = 50) -> List[Dict[str, str]]:
        cache_key = f"lastfm:global:{limit}"
        cached = self.cache_get(cache_key)
        if cached is not None:
            return cached

        params = {
            "method": "chart.gettoptracks",
            "api_key": self.settings.lastfm_api_key,
            "format": "json",
            "limit": limit
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(LASTFM_API_URL, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
        except Exception:
            return []

        tracks = data.get("tracks", {}).get("track", []) or []
        result: List[Dict[str, str]] = []
        for t in tracks:
            artist_obj = t.get("artist")
            artist = artist_obj.get("name") if isinstance(artist_obj, dict) else (artist_obj or "")
            title = t.get("name") or ""
            result.append({"artist": artist, "title": title})

        self.cache_set(cache_key, result)
        return result
