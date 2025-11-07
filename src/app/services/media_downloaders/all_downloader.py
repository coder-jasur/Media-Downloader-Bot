import asyncio
import os.path
from typing import Optional, Union

import aiofiles
import aiohttp
from aiogram.types import Message

from src.app.services.media_downloaders.audio_and_music_downloaders.music_downloader import MusicDownloader
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher
from src.app.services.media_downloaders.utils.audio import AudioUtils
from src.app.services.media_downloaders.utils.downlaod_media import download_media_in_internet
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_audio_file_name, get_photo_file_name
from src.app.services.media_downloaders.video_downloaders.instagram_downloader import InstagramDownloaders
from src.app.services.media_downloaders.video_downloaders.tiktok_downloader import TikTokDownloaders
from src.app.services.media_downloaders.video_downloaders.youtube_downloader import YouTubeDownloaders
from src.app.utils.enums.audio import MusicAction
from src.app.utils.enums.error import DownloadError
from src.app.utils.enums.general import MediaType
from src.app.utils.enums.video import InstagramMediaType
from src.app.utils.i18n import get_translator


class AllDownloader:
    def __init__(self, message: Message = None, lang: str = None):
        self.message = message
        self.lang = lang
        self.instagram_downloader = InstagramDownloaders()
        self.youtube_downloader = YouTubeDownloaders()
        self.tiktok_downloader = TikTokDownloaders()
        self.music_downloader = MusicDownloader()
        self.search = YouTubeSearcher()
        self.audio_utils = AudioUtils()
        self._ = get_translator(lang).gettext

    async def instagram_downloaders(
            self,
            url: str,
            media_type: InstagramMediaType
    ) -> Optional[Union[str, list[dict]]]:

        errors = []
        file_path = None


        if media_type == InstagramMediaType.REELS:
            file_path, errors = await self.instagram_downloader.instagram_reels_downloader(url)
        elif media_type == InstagramMediaType.POST:
            file_path, errors = await self.instagram_downloader.instagram_post_downloader(url)
        elif media_type == InstagramMediaType.PROFILE_PHOTO:
            file_path, errors = await self.instagram_downloader.instagram_profil_photo_downloader(url)
        elif media_type == InstagramMediaType.HIGHLIGHT:
            await self.instagram_downloader.login(False)
            file_path, errors = await self.instagram_downloader.instagram_highlight_downloader(url)
        elif media_type == InstagramMediaType.STORIES:
            await self.instagram_downloader.login(False)
            file_path, errors = await self.instagram_downloader.instagram_stories_downloader(url)


        if DownloadError.LOGIN_REQUIRED in errors and media_type in [
            InstagramMediaType.STORIES,
            InstagramMediaType.HIGHLIGHT
        ]:
            if media_type == InstagramMediaType.STORIES:
                await self.instagram_downloader.login(re_login=True)
                file_path, errors = await self.instagram_downloader.instagram_stories_downloader(url)
            else:
                await self.instagram_downloader.login(re_login=True)
                file_path, errors = await self.instagram_downloader.instagram_highlight_downloader(url)
        if DownloadError.FILE_TOO_BIG in errors:
            if self.message:
                await self.message.answer(self._("File size bigger than 2GB"))
            return None

        if not file_path or DownloadError.DOWNLOAD_ERROR in errors:
            if self.message:
                await self.message.answer(self._("Error in loading file"))
            return None
        return file_path



    async def youtube_downloaders(self, url: str):
        file_path, errors = await asyncio.to_thread(self.youtube_downloader.youtube_video_and_shorts_downloader, url)

        if DownloadError.FILE_TOO_BIG in errors:
            await self.message.answer(self._("File size big to 2 gb"))
        elif DownloadError.DOWNLOAD_ERROR in errors:
            await self.message.answer(self._("Error in loading file"))

        return file_path

    async def tiktok_downloaders(self, url: str):
        file_path, errors = await self.tiktok_downloader.tiktok_video_downloader(url)

        if DownloadError.FILE_TOO_BIG in errors:
            await self.message.answer(self._("File size big to 2 gb"))
        elif DownloadError.DOWNLOAD_ERROR in errors:
            await self.message.answer(self._("Error in loading file"))

        return file_path

    async def music_downloaders(
            self,
            actions: MusicAction,
            media_type: MediaType = None,
            some_data: str = None
    ):

        media_file_id = None
        media_path = None
        thumbnail_path = None
        try:

            if actions == MusicAction.SEARCH_BY_TEXT:
                musics_data, entries, errors = await self.search.search_music(some_data, 10)
                for entry in entries:
                    thumbnail_path = await download_media_in_internet(
                        entry.get("thumbnail", ""),
                        get_photo_file_name(),
                        MediaType.PHOTO
                    )
                    break

                if DownloadError.MUSIC_NOT_FOUND in errors:
                    await self.message.answer(self._("Music not found"))

                musics_list = []
                music_title = ""
                if musics_data:
                    for i, music_data in enumerate(musics_data, start=1):
                        if music_data.get("title"):
                            file_size = music_data.get("filesize_mb")
                            duration = str(music_data.get("duration"))

                            if int(file_size) < 2000 and 10 > int(duration.split(":")[0]):
                                musics_list.append(music_data)
                                title = ""
                                for text in str(music_data.get("title")).split(" "):
                                    if not text.startswith("#") and not text.startswith("@") :
                                        title += text + " "
                                music_title += f"{i}. {title} - {duration}\n\n"
                                i += 1

                return musics_list, music_title, thumbnail_path

            if actions == MusicAction.DOWNLOAD:
                music_output_path, title = await self.music_downloader.download_music_from_youtube(some_data)

                if not music_output_path and not await asyncio.to_thread(os.path.exists, music_output_path):
                    await self.message.answer(self._("Error in loading music"))
                    return
                return music_output_path, title

            if actions == MusicAction.SEARCH_BY_MEDIA:
                if media_type == MediaType.VIDEO:
                    media_file_id = self.message.video.file_id
                elif media_type == MediaType.VIDEO_NOTE:
                    media_file_id = self.message.video_note.file_id
                elif media_type == MediaType.AUDIO:
                    media_file_id = self.message.audio.file_id
                elif media_type == MediaType.VOICE:
                    media_file_id = self.message.voice.file_id

                file_info = await self.message.bot.get_file(media_file_id)
                if media_type == MediaType.VIDEO:
                    media_path = f"./media/videos/{get_video_file_name()}"
                elif media_type == MediaType.VIDEO_NOTE:
                    media_path = f"./media/videos/{get_video_file_name()}"
                elif media_type == MediaType.AUDIO:
                    media_path = f"./media/audios/{get_audio_file_name()}"
                elif media_type == MediaType.VOICE:
                    media_path = f"./media/audios/{get_audio_file_name()}"

                async with aiohttp.ClientSession() as session:
                    url = f"https://api.telegram.org/bot{self.message.bot.token}/getFile?file_id={file_info.file_id}"
                    async with session.get(url) as resp:
                        file_info = await resp.json()
                        file_path = file_info['result']['file_path']

                    file_url = f"https://api.telegram.org/file/bot{self.message.bot.token}/{file_path}"
                    async with session.get(file_url) as response:
                        if response.status == 200:
                            async with aiofiles.open(media_path, "wb") as f:
                                await f.write(await response.read())

                if media_type in [MediaType.VOICE, MediaType.VIDEO_NOTE]:
                    audio_path = None
                    if MediaType.VIDEO_NOTE:
                        audio_path = f"./media/audios/{get_audio_file_name()}"
                        await asyncio.to_thread(
                            self.audio_utils.extract_audio_from_video,
                            media_path,
                            audio_path
                        )

                    music_texts = await self.audio_utils.speech_to_text(media_path or audio_path, some_data)

                    musics_data, entries, errors = await self.search.search_music(music_texts, 10)

                    for entry in entries:
                        thumbnail_path = await download_media_in_internet(
                            entry.get("thumbnail", ""),
                            get_photo_file_name(),
                            MediaType.PHOTO
                        )
                        break

                    if DownloadError.MUSIC_NOT_FOUND in errors:
                        await self.message.answer(self._("Music not found"))

                    musics_list = []
                    music_title = ""
                    if musics_data:
                        for i, music_data in enumerate(musics_data, start=1):
                            if music_data.get("title"):
                                file_size = music_data.get("filesize_mb")
                                duration = str(music_data.get("duration"))

                                if int(file_size) < 2000 and 10 > int(duration.split(":")[0]):
                                    musics_list.append(music_data)
                                    title = ""
                                    for text in str(music_data.get("title")).split(" "):
                                        if not text.startswith("#") and not text.startswith("@"):
                                            title += text + " "
                                    music_title += f"{i}. {title.strip()} - {duration}\n\n"
                                    i += 1
                    for file in [audio_path, media_path]:
                        if await asyncio.to_thread(os.path.exists, file):
                            await asyncio.to_thread(os.remove, file)

                    return musics_list, music_title, thumbnail_path

                music_name = await self.music_downloader.find_song_name_by_video_audio_voice_video_note(media_path)

                if not music_name:
                    await self.message.answer(self._("Music not found"))

                musics_data, entries, errors = await self.search.search_music(music_name, 10)

                for entry in entries:
                    thumbnail_path = await download_media_in_internet(
                        entry.get("thumbnail", ""),
                        get_photo_file_name(),
                        MediaType.PHOTO
                    )
                    break

                if DownloadError.MUSIC_NOT_FOUND in errors:
                    await self.message.answer(self._("Music not found"))

                if await asyncio.to_thread(os.path.exists, media_path):
                    await asyncio.to_thread(os.remove, media_path)

                musics_list = []
                music_title = ""

                if musics_data:
                    for i, music_text in enumerate(musics_data, start=1):
                        if int(str(music_text["duration"]).split(":")[0]) <= 10:
                            musics_list.append(music_text)
                            title = ""
                            for text in str(music_text["title"]).split(" "):
                                if not text.startswith("#") and not text.startswith("@"):
                                    title += text + " "

                            music_title += f"{i}. {title.strip()} - {music_text["duration"]}\n\n"


                return musics_list, music_title, thumbnail_path


        except Exception as e:
            print("ERROR", e)
            return None, None, None

    async def extract_video_to_audio(self, video_path: str):
        audio_path_file = f"./media/audios/{get_audio_file_name()}.mp3"

        audio_path = await asyncio.to_thread(self.audio_utils.extract_audio_from_video, video_path, audio_path_file)
        if audio_path:
            return audio_path_file

        return None
