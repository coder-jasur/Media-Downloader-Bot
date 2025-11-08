import asyncio
import os

import aiofiles
import aiohttp
from aiogram import Bot
from aiogram.types import Message

from src.app.services.media_downloaders.utils.files import get_video_file_name, get_audio_file_name
from src.app.services.media_effects.utils.media_effects import MediaEffectsTools
from src.app.utils.enums.general import GeneralEffectAction, MediaType


class MediaEffects:
    def __init__(self, message: Message, bot: Bot):
        self.bot = bot
        self.message = message
        self.media_effect_obj = MediaEffectsTools()


    async def media_effect(
            self,
            effect_type: GeneralEffectAction,
            media_type: MediaType,
    ) -> str | None:
        out_put_media_path = None
        media_input_path = None
        print(f"{effect_type} 22222222222222222221111111111111")
        print(f"{media_type} 22222222222222222222222111111111111111")

        try:
            if media_type == MediaType.VIDEO:
                media_file_id = self.message.video.file_id
                media_input_path = f"./media/videos/{effect_type.value}-{get_video_file_name()}"

            elif media_type == MediaType.AUDIO:
                media_file_id = self.message.audio.file_id
                media_input_path = f"./media/audios/{effect_type.value}-{get_audio_file_name()}"

            elif media_type == MediaType.VOICE:
                media_file_id = self.message.voice.file_id
                media_input_path = f"./media/audios/{effect_type.value}-{get_audio_file_name()}"

            else:
                return None
            file_info = await self.bot.get_file(media_file_id)

            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.message.bot.token}/getFile?file_id={file_info.file_id}"
                async with session.get(url) as resp:
                    file_info = await resp.json()
                    file_path = file_info['result']['file_path']

                file_url = f"https://api.telegram.org/file/bot{self.message.bot.token}/{file_path}"
                async with session.get(file_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(media_input_path, "wb") as f:
                            await f.write(await response.read())

            print(f"{effect_type} 22222222222222222221111111111111")
            print(f"{media_type} 22222222222222222222222111111111111111")

            if media_type in [MediaType.AUDIO, MediaType.VOICE]:
                out_put_media_path = await self.media_effect_obj.audio_effects(media_input_path, effect_type)

            elif media_type == MediaType.VIDEO:
                out_put_media_path = await self.media_effect_obj.video_effects(media_input_path, effect_type)

            return out_put_media_path

        except Exception as e:
            print("ERROR in media_effect:", e)
            return None

        finally:
            try:
                if media_input_path and await asyncio.to_thread(os.path.exists, media_input_path):
                    await asyncio.to_thread(os.remove, media_input_path)
            except Exception as ex:
                print("Cleanup error:", ex)

