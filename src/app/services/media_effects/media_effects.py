import asyncio
import os

import aiohttp
from aiogram.types import Message

from src.app.services.media_downloaders.utils.audio import AudioUtils
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_audio_file_name


class MediaEffects:
    def __init__(self, message: Message):
        self.message = message
        self.audio_utils = AudioUtils()


    async def media_effect(self, effect_type: str) -> str | None:
        input_media_path = None
        media_type = None
        file_id = None

        try:
            if self.message.video:
                media_type = "video"
                file_id = self.message.video.file_id
            elif self.message.audio:
                media_type = "audio"
                file_id = self.message.audio.file_id

            elif self.message.voice:
                media_type = "audio"
                file_id = self.message.voice.file_id


            file = await self.message.bot.get_file(file_id)
            file_path = file.file_path

            if self.message.voice or self.message.audio:
                input_media_path = f"./media/audios/{get_audio_file_name()}.mp3"
                output_media_path = f"./media/audios/{get_audio_file_name()}_{effect_type}.mp3"
            else:
                input_media_path = f"./media/videos/{get_video_file_name()}"
                output_media_path = f"./media/videos/{effect_type}_{get_video_file_name()}"

            file_url = f"https://api.telegram.org/file/bot{self.message.bot.token}/{file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status == 200:
                        with open(input_media_path, "wb") as f:
                            f.write(await response.read())
                    else:
                        print("ERROR")

            output_media_path = await asyncio.to_thread(
                self.audio_utils.apply_effect,
                input_media_path,
                output_media_path,
                effect_type,
                media_type
            )

            return output_media_path

        except Exception as e:
            print(f"ERROR", e)
            return None

        finally:
            if input_media_path and await asyncio.to_thread(os.path.exists, input_media_path):
                await asyncio.to_thread(os.remove, input_media_path)