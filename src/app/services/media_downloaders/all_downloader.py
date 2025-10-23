import asyncio
import os.path

from aiogram.types import Message

from src.app.services.media_downloaders.utils.video import download_media_in_internet
from src.app.services.searchs import Searchs
from src.app.services.media_downloaders.utils.audio import AudioUtils
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_audio_file_name, get_photo_file_name
from src.app.services.media_downloaders.video_downloaders.instagram_downloader import InstagramDownloaders
from src.app.services.media_downloaders.audio_and_music_downloaders.music_downloader import MusicDownloader
from src.app.services.media_downloaders.video_downloaders.tiktok_downloader import TikTokDownloaders
from src.app.services.media_downloaders.video_downloaders.youtube_downloader import YouTubeDownloaders


class AllDownloader:
    def __init__(self, message: Message = None, lang: str = None):
        self.message = message
        self.lang = lang
        self.instagram_downloader = InstagramDownloaders()
        self.youtube_downloader = YouTubeDownloaders()
        self.tiktok_downloader = TikTokDownloaders()
        self.music_downloader = MusicDownloader()
        self.search = Searchs()
        self.auido_utils = AudioUtils()

    async def instagram_downloaders(self, url: str, media_type: str):
        errors = []
        file_path = None
        if media_type == "reels":
            file_path, error = await self.instagram_downloader.instagram_reels_downloader(url)
        elif media_type == "post":
            print(222)
            file_path, error = await self.instagram_downloader.instagram_post_downloader(url)
            print(file_path, error)
        elif media_type == "stories":
            await self.instagram_downloader.login()
            file_path, error = await self.instagram_downloader.instagram_stories_downloader(url)
        elif media_type == "highlight":
            await self.instagram_downloader.login()
            file_path, error = await self.instagram_downloader.instagram_highlight_downloader(url)
        elif media_type == "profil_photo":
            file_path, error = await self.instagram_downloader.instagram_profil_photo_downloader(url)
        else:
            error = "invalid_media_type"

        errors.append(error)

        if "file_is_so_big" in errors:
            await self.message.answer("fayl hajmi 2 gb dan oshganligi uchun yuklash to'qtatildi")
        elif "error_in_downloading" in errors:
            await self.message.answer("faylni yuklab olishda xatolik yuz berdi")

        return file_path

    async def youtube_downloaders(self, url: str):
        print(111)
        file_path, errors = await asyncio.to_thread(self.youtube_downloader.youtube_video_and_shorts_downloader, url)

        if "file_is_so_big" in errors:
            await self.message.answer("fayl hajmi 2 gb dan oshganligi uchun yuklash to'qtatildi")
        elif "error_in_downloading" in errors:
            await self.message.answer("faylni yuklab olishda xatolik yuz berdi")

        return file_path

    async def tiktok_downloaders(self, url: str):
        file_path, errors = await self.tiktok_downloader.tiktok_video_downloader(url)

        if "file_is_so_big" in errors:
            await self.message.answer("fayl hajmi 2 gb dan oshganligi uchun yuklash to'qtatildi")
        elif "error_in_downloading" in errors:
            await self.message.answer("faylni yuklab olishda xatolik yuz berdi")

        return file_path

    async def music_downloaders(self, actions: str, media_type: str = None, some_data: str = None):
        media_file_id = None
        media_path = None
        thumbnail_path = None
        try:

            if actions == "search_music_by_text_or_avtro_name":
                musics_data, entries, errors = await asyncio.to_thread(self.search.search_music, self.message.text, 5)
                for entry in entries:
                    print(entry.get("thumbnail", ""))
                    thumbnail_path = await download_media_in_internet(
                        entry.get("thumbnail", ""),
                        get_photo_file_name(),
                        "photo"
                    )
                    break

                if "music_not_found" in errors:
                    await self.message.answer("musiqa topilmadi")

                musics_list = []
                music_title = ""
                if musics_data:
                    for i, music_data in enumerate(musics_data, start=1):
                        if music_data.get("title"):
                            file_size = music_data.get("filesize_mb")
                            duration = str(music_data.get("duration"))

                            if int(file_size) < 2000 and 10 > int(duration.split(":")[0]):
                                musics_list.append(music_data)
                                music_title += f"{i}. {music_data.get("title")} - {duration}\n\n"
                                i += 1

                return musics_list, music_title, thumbnail_path

            if actions == "download_music":
                music_output_path, title = await self.music_downloader.download_music_from_youtube(some_data)

                if not music_output_path and not await asyncio.to_thread(os.path.exists, music_output_path):
                    await self.message.answer("musiqa yuklab olinmadi")
                    return
                return music_output_path, title

            if actions == "search_music_by_media":
                if media_type == "video":
                    media_file_id = self.message.video.file_id
                elif media_type == "video_note":
                    media_file_id = self.message.video_note.file_id
                elif media_type == "audio":
                    media_file_id = self.message.audio.file_id
                elif media_type == "voice":
                    media_file_id = self.message.voice.file_id

                file_info = await self.message.bot.get_file(media_file_id)
                file_path = file_info.file_path
                if media_type == "video":
                    media_path = f"./media/videos/{get_video_file_name()}"
                elif media_type == "video_note":
                    media_path = f"./media/videos/{get_video_file_name()}"
                elif media_type == "audio":
                    media_path = f"./media/audios/{get_audio_file_name()}"
                elif media_type == "voice":
                    media_path = f"./media/audios/{get_audio_file_name()}"

                await self.message.bot.download_file(file_path, media_path)

                music_name = await self.music_downloader.find_song_name_by_video_audio_voice_video_note(media_path)

                if not music_name:
                    await self.message.answer("musiqa topilmadi")

                musics_data, entries, errors = await asyncio.to_thread(self.search.search_music, music_name, 5)

                for entry in entries:
                    print(entry.get("thumbnail", ""))
                    thumbnail_path = await download_media_in_internet(
                        entry.get("thumbnail", ""),
                        get_photo_file_name(),
                        "photo"
                    )
                    break

                if "music_not_found" in errors:
                    await self.message.answer("musiqa topilmadi")

                if media_path and await asyncio.to_thread(os.path.exists, media_path):
                    await asyncio.to_thread(os.remove, media_path)

                musics_list = []
                music_title = ""

                if musics_data:
                    for i, music_text in enumerate(musics_data, start=1):
                        if int(str(music_text["duration"]).split(":")[0]) <= 10:
                            musics_list.append(music_text)
                            music_title += f"{i}. {music_text["title"]} - {music_text["duration"]}\n\n"

                return musics_list, music_title, thumbnail_path


        except Exception as e:
            print("ERROR", e)

    async def extract_video_to_audio(self, video_path: str):
        audio_path_file = f"./media/audios/{get_audio_file_name()}.mp3"

        audio_path = await asyncio.to_thread(self.auido_utils.extract_audio_from_video, video_path, audio_path_file)
        if audio_path:
            return audio_path_file

        return None
