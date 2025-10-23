import asyncio
import json
import os
from pathlib import Path


import aiofiles
from instagrapi import Client
from yt_dlp import YoutubeDL

from src.app.core.config import Settings
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_photo_file_name
from src.app.services.media_downloaders.utils.video import download_media_in_internet


class InstagramDownloaders:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.settings = Settings()
        self.searchs = YouTubeSearcher()
        self.yt_dlp = YoutubeDL
        self.session_file = session_file

    async def login(self):
        """Instagram login with session caching."""
        try:
            # Agar sessiya fayli mavjud bo‘lsa — uni yuklaymiz
            if await asyncio.to_thread(os.path.exists, self.session_file):
                try:
                    await asyncio.to_thread(self.client.load_settings, self.session_file)
                    await asyncio.to_thread(
                        self.client.login,
                        self.settings.instagram_username,
                        self.settings.instagram_password,
                        False,
                        ""
                    )
                    print("✅ Logged in using saved session")
                    return
                except Exception as e:
                    print(f"⚠️ Session file invalid or expired: {e}")
                    # Eski sessiyani o‘chiramiz
                    await asyncio.to_thread(os.remove, self.session_file)

            # Yangi login jarayoni
            print("🔐 Logging in to Instagram...")
            await asyncio.to_thread(
                self.client.login,
                self.settings.instagram_username,
                self.settings.instagram_password,
                False,
                ""
            )

            # Yangi sessiyani saqlaymiz
            settings = await asyncio.to_thread(self.client.get_settings)
            json_data = json.dumps(settings, ensure_ascii=False, indent=2)
            async with aiofiles.open(self.session_file, "w", encoding="utf-8") as f:
                await f.write(json_data)

            print("💾 Session saved successfully")

        except Exception as e:
            print(f"🚫 Login error: {e}")

    async def instagram_reels_downloader(self, reels_url: str):
        reels_file_name = get_video_file_name()
        reels_video_path = f"./media/videos/{reels_file_name}"
        errors = []
        try:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": reels_video_path,
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            with self.yt_dlp(ydl_opts) as ydl:
                ydl.download([reels_url])

            video_data = self.searchs.get_media_info(reels_url)

            video_filesize = video_data.get("filesize_mb")

            if video_filesize and video_filesize > 2000:
                errors.append("file_is_so_big")

            if not video_data:
                errors.append("error_in_downloading")

            return reels_video_path, errors
        except Exception as e:
            print("ERROR", e)

    async def instagram_stories_downloader(self, stories_url: str):
        errors = []

        try:
            parts = stories_url.strip("/").split("/")
            account_username = parts[3]

            # Foydalanuvchi ID sini olish
            user_id = await asyncio.to_thread(self.client.user_id_from_username, account_username)

            # Storylarni olish
            stories = await asyncio.to_thread(self.client.user_stories, user_id, None)

            if not stories:
                errors.append("error_in_downloading")
                return None, errors

            # Storyni URL bo‘yicha topish
            story_data = None
            for story in stories:
                if story.pk == stories_url.split("/")[5]:
                    story_data = story


            if not story_data:
                errors.append("story_not_found")
                return None, errors

            stories_path = get_video_file_name()


            story_path = await download_media_in_internet(stories_url, stories_path, "video")

            # Tekshirish
            if not story_path or not await asyncio.to_thread(os.path.exists, story_path):
                errors.append("error_in_downloading")
            elif await asyncio.to_thread(os.path.getsize, story_path) > 2000 * 1024 * 1024:
                errors.append("file_is_so_big")

            return story_path, errors

        except Exception as e:
            print("ERROR:", e)
            errors.append("error_in_downloading")
            return None, errors

    async def instagram_post_downloader(self, post_url: str):
        errors = []
        results = []

        def download_instagram():
            ydl_opts = {
                "quiet": True,
                "outtmpl": str(Path("./media") / "%(id)s.%(ext)s"),
                "format": "best[ext=mp4]",
                "retries": 3,
                "noplaylist": False,
            }
            with self.yt_dlp(ydl_opts) as ydl:
                return ydl.extract_info(post_url, download=True)

        try:
            info = await asyncio.to_thread(download_instagram)
            print(info)

            if not info:
                errors.append("error_in_downloading")
                return None, errors

            async def process_entry(entry):
                ext = entry.get("ext", "")
                media_type = "video" if ext in ["mp4", "mov", "mkv"] else "photo"

                folder = "./media/videos/" if media_type == "video" else "./media/photos/"
                file_name = get_video_file_name() if media_type == "video" else get_photo_file_name()
                file_path = folder + str(file_name)

                original_path = Path("./media") / f"{entry['id']}.{ext}"
                if original_path.exists():
                    await asyncio.to_thread(os.replace, original_path, file_path)

                if await asyncio.to_thread(os.path.exists, file_path):
                    size = await asyncio.to_thread(os.path.getsize, file_path)
                    if size > 2_000 * 1024 * 1024:
                        errors.append("file_is_so_big")
                    results.append({"path": str(file_path), "type": media_type})
                else:
                    errors.append("error_in_downloading")

            if "entries" in info:
                for entry in info["entries"]:
                    await process_entry(entry)
            else:
                await process_entry(info)

            if not results:
                errors.append("error_in_downloading")

            return results, errors

        except Exception as e:
            print("ERROR", e)
            errors.append("error_in_downloading")
            return None, errors

    async def instagram_highlight_downloader(self, highlight_url: str):
        errors = []
        try:
            highlight_id = await asyncio.to_thread(self.client.highlight_pk_from_url, highlight_url)
            info = await asyncio.to_thread(self.client.highlight_info, highlight_id)

            paths = []
            for item in info.items:
                if item.media_type == 1:
                    path = await asyncio.to_thread(
                        self.client.photo_download, int(info.pk), folder=Path("./media/photos")
                    )
                    if await asyncio.to_thread(os.path.getsize, path) > 2000 * 1024 * 1024:
                        errors.append("file_is_so_big")
                else:
                    path = await asyncio.to_thread(
                        self.client.video_download, int(item.pk), folder=Path("./media/videos")
                    )
                    if await asyncio.to_thread(os.path.getsize, path) > 2000 * 1024 * 1024:
                        errors.append("file_is_so_big")
                paths.append(path)

            download_count = 0

            for path in paths:
                if path and await asyncio.to_thread(os.path.exists, path):
                    download_count += 1

            if download_count == 0:
                errors.append("error_in_downloading")

            return paths, errors

        except Exception as e:
            print("ERROR", e)
            errors.append("error_in_downloading")
            return None, errors

    def instagram_profil_photo_downloader(self, photo_url: str) -> str and list:
        photo_file_name = get_photo_file_name()
        photo_path = f"./media/photos/{photo_file_name}"
        errors = []
        try:

            ydl_opts = {
                "outtmpl": photo_path,
                "skip_download": False
            }
            with self.yt_dlp(ydl_opts) as ydl:
                ydl.download([photo_url])

            photo_data = self.searchs.get_media_info(photo_url)

            photo_filesize = photo_data.get("filesize_mb")

            if photo_filesize and photo_filesize > 2000:
                errors.append("file_is_so_big")

            if not photo_data:
                errors.append("error_in_downloading")

            return photo_path, errors
        except Exception as e:
            print("ERROR", e)
            return None
