import asyncio
import os
from pathlib import Path
from typing import List

import aiohttp
from aiogram.types import Message
from instagrapi import Client

from src.app.core.config import Settings
from src.app.services.audio_music_downloaders import AudioMusicDownloaders
from src.app.services.searchs import Searchs
from src.app.services.media_downloaders.utils.audio import AudioUtils, MediaEffects
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_audio_file_name
from src.app.services.media_downloaders.utils.video import download_media_in_internet
from src.app.services.video_downloaders import VideoDownloaders
from src.app.texts import video_process_texts, music_and_audio_process_texts, photo_process_texts
from src.app.utils.enums.audio import AudioEffectAction


class AllDownloader:

    def __init__(self, message: Message, lang: str):
        self.message = message
        self.lang = lang
        self.settings = Settings()
        self.video_downloader = VideoDownloaders()
        self.music_downloader = AudioMusicDownloaders()
        self.serch_music = Searchs()
        self.auido_utils = AudioUtils()
        self.media_effect = MediaEffects()

    async def insgtarm_video_music_downloader(self, video_url: str):

        instagram_downloader_errors = []

        video_path = get_video_file_name()
        audio_path = get_audio_file_name()
        video_out_path, video_errors = await asyncio.to_thread(
            self.video_downloader.instagram_video_downloader,
            video_url,
            video_path
        )
        music_title, music_errors = await self.music_downloader.find_song_name_by_video(video_out_path, audio_path)

        for video_error in video_errors:
            instagram_downloader_errors.append(video_error)
        for music_error in music_errors:
            instagram_downloader_errors.append(music_error)

        if "error_in_downloading" in instagram_downloader_errors:
            await self.message.edit_text(video_process_texts["error_in_downloading"][self.lang])
        elif "video_file_is_so_big" in instagram_downloader_errors:
            await self.message.edit_text(video_process_texts["video_file_is_so_big"][self.lang])

        elif "music_not_found" in instagram_downloader_errors:
            music_title = None

        return video_out_path, music_title

    async def instagram_post_downloader(self, post_url: str):

        downloaded_files = []
        errors: List[str] = []

        cl = Client()
        try:

            await asyncio.to_thread(cl.login, self.settings.instagram_username, self.settings.instagram_password)

            media_pk = await asyncio.to_thread(cl.media_pk_from_url, post_url)
            media_info = await asyncio.to_thread(cl.media_info, media_pk, True)

            result_paths = await asyncio.to_thread(cl.album_download, media_info.pk, folder=Path("./media/videos/"))
            if isinstance(result_paths, list):
                downloaded_files.extend([str(p) for p in result_paths])
            else:
                downloaded_files.append(str(result_paths))

        except Exception as e:
            print("ERROR", e)
            return None, errors

        if downloaded_files:
            return downloaded_files, errors
        else:
            return None, errors


    async def insgtarm_highlights_and_music_downloader(self, highlight_url: str):

        try:
            cl = Client()
            await asyncio.to_thread(cl.login, self.settings.instagram_username, self.settings.instagram_password)
            highlight_id = await asyncio.to_thread(self.cl.highlight_pk_from_url, highlight_url)
            info = await asyncio.to_thread(self.cl.highlight_info, highlight_id)

            paths = []
            for item in info.items:
                if item.media_type == 1:
                    path = await asyncio.to_thread(
                        self.cl.photo_download, item.pk, folder="./media/photos"
                    )
                else:
                    path = await asyncio.to_thread(
                        self.cl.video_download, item.pk, folder="./media/videos"
                    )
                paths.append(path)

            print(f"🌟 Highlight yuklandi: {paths}")
            return paths

        except Exception as e:
            print("❌ Xato (highlight):", e)
            return None

    async def instagram_stories_music_downloader(self, stories_url: str):
        instagram_downloader_errors = []

        cl = Client()
        await asyncio.to_thread(cl.login, self.settings.instagram_username, self.settings.instagram_password, False)

        account_username = stories_url.split("/")[4]
        user_id = await asyncio.to_thread(cl.user_id_from_username, account_username)
        stories = await asyncio.to_thread(cl.user_stories, user_id, None)

        if not stories:
            instagram_downloader_errors.append("error_in_downloading")
            return None, None

        story_data = None
        for story in stories:
            if story.pk == stories_url.split("/")[5]:
                story_data = story

        stories_path = get_video_file_name()
        audio_path = get_audio_file_name()

        story_path = await download_media_in_internet(str(story_data.video_url), stories_path, "video")
        print(stories_path)
        print(111111111)
        music_title, music_errors = await self.music_downloader.find_song_name_by_video(story_path, audio_path)

        instagram_downloader_errors.extend(music_errors)

        if "error_in_downloading" in instagram_downloader_errors:
            await self.message.edit_text(video_process_texts["error_in_downloading"][self.lang])
        elif "video_file_is_so_big" in instagram_downloader_errors:
            await self.message.edit_text(video_process_texts["video_file_is_so_big"][self.lang])
        elif "music_not_found" in instagram_downloader_errors:
            music_title = None
        return story_path, music_title

    async def instagram_photo_downloader(self, photo_url: str):
        instagram_downloader_errors = []

        photo_path = get_video_file_name()
        photo_out_path, photo_errors = await asyncio.to_thread(
            self.video_downloader.instagram_photo_downloader,
            photo_url,
            photo_path,
        )

        for video_error in photo_errors:
            instagram_downloader_errors.append(video_error)


        if "error_in_downloading" in instagram_downloader_errors:
            await self.message.edit_text(photo_process_texts["not_fund"][self.lang])
        elif "photo_file_is_so_big" in instagram_downloader_errors:
            await self.message.edit_text(photo_process_texts["photo_file_is_so_big"][self.lang])

        return photo_out_path

    async def youtube_video_music_downloader(self, video_url: str):
        youtube_downloader_errors = []

        video_path = get_video_file_name()
        audio_path = get_audio_file_name()
        video_out_path, video_errors = await asyncio.to_thread(
            self.video_downloader.youtube_video_downloader,
            video_url,
            video_path
        )
        music_title, music_errors = await self.music_downloader.find_song_name_by_video(video_out_path, audio_path)

        for video_error in video_errors:
            youtube_downloader_errors.append(video_error)
        for music_error in music_errors:
            youtube_downloader_errors.append(music_error)

        if "error_in_downloading" in youtube_downloader_errors:
            await self.message.edit_text(video_process_texts["error_in_downloading"][self.lang])
        elif "video_file_is_so_big" in youtube_downloader_errors:
            await self.message.edit_text(video_process_texts["video_file_is_so_big"][self.lang])

        elif "music_not_found" in youtube_downloader_errors:
            music_title = None

        return video_out_path, music_title

    async def tiktok_video_music_downloader(self, video_url: str):
        tiktok_downloader_errors = []

        video_path = get_video_file_name()
        audio_path = get_audio_file_name()
        video_out_path, video_errors = await self.video_downloader.tiktok_video_downloader(
            video_url=video_url,
            output_file_name=video_path
        )

        music_title, music_errors = await self.music_downloader.find_song_name_by_video(video_out_path, audio_path)

        for video_error in video_errors:
            tiktok_downloader_errors.append(video_error)

        for music_error in music_errors:
            tiktok_downloader_errors.append(music_error)

        if "error_in_downloading" in tiktok_downloader_errors:
            await self.message.edit_text(video_process_texts["error_in_downloading"][self.lang])
        elif "video_file_is_so_big" in tiktok_downloader_errors:
            await self.message.edit_text(video_process_texts["video_file_is_so_big"][self.lang])

        elif "music_not_found" in tiktok_downloader_errors:
            music_title = None

        return video_out_path, music_title

    async def download_music_from_audio_video_voice_video_note(self, message: Message, media_type: str):
        errors = []
        if media_type in ["video", "video_note"]:
            if message.video_note:
                media = message.video_note
            else:
                media = message.video

            media_path = get_video_file_name()
            file = await message.bot.get_file(media.file_id)

            file_path = file.file_path
            download_path = f"./media/videos/{media_path}"

            await message.bot.download_file(file_path, download_path)

            music_name = await self.music_downloader.find_song_name_by_video_audio_voice_video_note(download_path)
            if await asyncio.to_thread(os.path.exists, download_path):
                await asyncio.to_thread(os.remove, download_path)
            if music_name:
                musics_data = await asyncio.to_thread(self.serch_music.search_music, music_name, 5)
            else:
                await self.message.answer(music_and_audio_process_texts["not_found"][self.lang])
                return

            if not music_name or not musics_data:
                errors.append("music_not_found")

            if "music_not_found" in errors:
                await self.message.answer(music_and_audio_process_texts["error_in_downloading"][self.lang])

            musics_list = []
            music_title = ""
            i = 1
            if musics_data:
                for music_data in musics_data:
                    if music_data.get("title"):
                        file_size = music_data.get("filesize_mb")
                        duration = str(music_data.get("duration"))

                        if int(file_size) < 2000 and 10 > int(duration.split(":")[0]):
                            musics_list.append(music_data)
                            music_title += f"{i}. {music_data.get("title")} - {duration}\n\n"
                            i += 1

                return musics_list, music_title
            else:
                await self.message.answer(music_and_audio_process_texts["error_in_downloading"][self.lang])

            return

        elif media_type in ["audio", "voice"]:
            if message.voice:
                audio = message.voice
            else:
                audio = message.audio
            media_path_file = get_audio_file_name()
            file = await message.bot.get_file(audio.file_id)

            file_path = file.file_path

            download_path = f"./media/audios/{media_path_file}.mp3"
            await message.bot.download_file(file_path, download_path)

            music_name = await self.music_downloader.find_song_name_by_video_audio_voice_video_note(download_path)
            if await asyncio.to_thread(os.path.exists, download_path):
                await asyncio.to_thread(os.remove, download_path)

            if not music_name:
                return None

            if music_name:
                musics_data = await asyncio.to_thread(self.serch_music.search_music, music_name, 5)
            else:
                await self.message.answer(music_and_audio_process_texts["not_found"][self.lang])
                return

            if not music_name or not musics_data:
                errors.append("music_not_found")

            if "music_not_found" in errors:
                await self.message.answer(music_and_audio_process_texts["error_in_downloading"][self.lang])
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
                return musics_list, music_title
            else:
                await self.message.edit_text(music_and_audio_process_texts["error_in_downloading"][self.lang])

            return
        return

    async def download_music_by_avtor_or_music_text(self, music_text_or_avtor: str, max_count: int = 5):
        musics_data = await asyncio.to_thread(self.serch_music.search_music, music_text_or_avtor, max_count)

        musics_list = []
        music_title = ""
        i = 1
        if musics_data:
            for music_data in musics_data:
                if music_data.get("title"):
                    file_size = music_data.get("filesize_mb")
                    duration = str(music_data.get("duration"))

                    if int(file_size) < 2000 and 10 > int(duration.split(":")[0]):
                        musics_list.append(music_data)
                        music_title += f"{i}. {music_data.get("title")} - {duration}\n\n"
                        i += 1
            return musics_list, music_title
        else:
            await self.message.edit_text(music_and_audio_process_texts["error_in_downloading"][self.lang])

        return

    async def download_music_from_youtube(self, video_id: str):
        music_path = get_audio_file_name()
        music_output_path, title = await asyncio.to_thread(
            self.music_downloader.download_music_from_youtube,
            video_id,
            music_path
        )

        if not title:
            await self.message.answer(music_and_audio_process_texts["not_found"][self.lang])

        return music_output_path, title

    async def extract_video_to_audio(self, video_path: str):
        audio_path_file = f"./media/audios/{get_audio_file_name()}.mp3"

        audio_path = await asyncio.to_thread(self.auido_utils.extract_audio_from_video, video_path, audio_path_file)
        if audio_path:
            return audio_path_file

        return None

    async def media_effect(self, effect_type: AudioEffectAction, message: Message) -> str | None:
        input_media_path = None

        try:
            if message.video:
                media_type = "video"
                file_id = message.video.file_id
            elif message.audio:
                media_type = "audio"
                file_id = message.audio.file_id

            elif message.voice:
                media_type = "audio"
                file_id = message.voice.file_id
            else:
                raise ValueError("Media topilmadi")

            file = await message.bot.get_file(file_id)
            file_path = file.file_path
            print(1)

            if message.voice or message.audio:
                input_media_path = f"./media/audios/{get_audio_file_name()}.mp3"
            else:
                input_media_path = f"./media/videos/{get_video_file_name()}"
            print(2)

            file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        with open(input_media_path, "wb") as f:
                            f.write(await response.read())
                    else:
                        raise Exception(f"Fayl yuklab olinmadi, status: {response.status}")

            output_media_path = await self.media_effect.audio_effects(
                input_media_path,
                effect_type,
            )

            return output_media_path

        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return None

        finally:
            if input_media_path and await asyncio.to_thread(os.path.exists, input_media_path):
                await asyncio.to_thread(os.remove, input_media_path)



