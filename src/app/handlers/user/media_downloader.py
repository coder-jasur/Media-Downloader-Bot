import asyncio
import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery

from src.app.keyboards.callback_data import MusicCD, VideoMusicCD
from src.app.keyboards.inline import video_keyboards, music_keyboards
from src.app.services.searchs import Searchs
from src.app.texts import (
    media_process_text, user_texts, video_process_texts, music_and_audio_process_texts,
    photo_process_texts
)
from src.app.utils.downloader.all_downloader import AllDownloader

media_downloader_router = Router()


@media_downloader_router.message(F.text | F.video | F.voice | F.audio)
async def all_downloader_(message: Message, lang: str):
    for f in [message.audio, message.voice, message.video]:
        if f:
            if f.file_size > 20 * 1024 * 1024:
                await message.answer(media_process_text["very_big_file"][lang])
                return



    video_path = None
    photo_path = None
    load_msg = None
    all_downloader = AllDownloader(message=message, lang=lang)

    try:
        if message.text:
            if "https://" in message.text[:8]:
                if "instagram" in message.text:
                    if "https://www.instagram.com/stories/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path, music_name = await all_downloader.instagram_stories_music_downloader(message.text)
                        if music_name:
                            await message.reply_video(
                                FSInputFile(video_path),
                                reply_markup=video_keyboards(
                                    music_name,
                                    lang
                                ),
                                caption=media_process_text["downloadin_by"][lang]
                            )
                        else:
                            await message.reply_video(
                                FSInputFile(video_path),
                                caption=media_process_text["downloadin_by"][lang]
                            )

                    elif "www.instagram.com" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path, music_name = await all_downloader.insgtarm_video_music_downloader(message.text)
                        if music_name:
                            await message.reply_video(
                                FSInputFile(video_path),
                                reply_markup=video_keyboards(
                                    music_name,
                                    lang
                                ),
                                caption=media_process_text["downloadin_by"][lang]
                            )
                        else:
                            await message.reply_video(
                                FSInputFile(video_path),
                                caption=media_process_text["downloadin_by"][lang]
                            )
                    else:
                        load_msg = await message.answer(photo_process_texts["downloading"][lang])
                        photo_path = await all_downloader.instagram_photo_downloader(message.text)
                        await message.reply_photo(
                            FSInputFile(photo_path),
                            caption=media_process_text["downloadin_by"][lang]
                        )

                elif "www.youtube.com" in message.text:
                    url = message.text
                    if "&" in message.text or  "&list=" in message.text:
                        url = message.text.split("&")[0]


                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path, music_name = await all_downloader.youtube_video_music_downloader(url)
                    print(video_path)

                    if music_name:
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                music_name,
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    else:
                        await message.reply_video(
                            FSInputFile(video_path),
                            caption=media_process_text["downloadin_by"][lang]
                        )

                elif "www.tiktok.com" in message.text:
                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path, music_name = await all_downloader.tiktok_video_music_downloader(message.text)

                    if music_name:
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                music_name,
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    else:
                        await message.reply_video(
                            FSInputFile(video_path),
                            caption=media_process_text["downloadin_by"][lang]
                        )

                else:
                    await message.answer(video_process_texts["wrong_link"][lang])
            else:
                load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
                music_list, music_title = await all_downloader.download_music_by_avtor_or_music_text(message.text, 5)
                if music_list:
                    await message.reply(
                        text=music_title,
                        reply_markup=music_keyboards(music_list)
                    )

        elif message.video or message.audio or message.voice:
            load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
            if message.video:
                music_list, music_title = await all_downloader.download_music_from_audio_video_voice(message, "video")
                if music_list:
                    print(music_list)
                    await message.reply(
                        text=music_title,
                        reply_markup=music_keyboards(music_list)
                    )
            if message.audio:
                music_list, music_title = await all_downloader.download_music_from_audio_video_voice(message, "audio")
                if music_list:
                    await message.reply(
                        text=music_title,
                        reply_markup=music_keyboards(music_list)
                    )
            if message.voice:
                music_list, music_title = await all_downloader.download_music_from_audio_video_voice(message, "voice")
                if music_list:
                    await message.reply(
                        text=music_title,
                        reply_markup=music_keyboards(music_list)
                    )
    except Exception as e:
        print("ERROR", e)
        await message.answer(user_texts["error"][lang])
    finally:
        if load_msg:
            await load_msg.delete()

        for path in [video_path, photo_path]:
            if path:
                if await asyncio.to_thread(os.path.exists, path):
                    await asyncio.to_thread(os.remove, path)


@media_downloader_router.callback_query(VideoMusicCD.filter())
async def send_music_results_from_video(call: CallbackQuery, callback_data: VideoMusicCD, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["music_is_loading"][lang])
    search_music = Searchs()
    try:
        musics_data = await asyncio.to_thread(search_music.search_music, callback_data.music_name, 5)

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
                        music_title += f"{i}. {music_data.get("title")} - {music_data.get("duration_str")}\n\n"
                        i += 1
            await call.message.answer(text=music_title, reply_markup=music_keyboards(musics_list))
        else:
            await call.message.edit_text(music_and_audio_process_texts["error_in_downloading"][lang])
    except Exception as e:
        print("ERROR", e)
        await call.message.answer(music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if load_msg:
            await load_msg.delete()


@media_downloader_router.callback_query(MusicCD.filter())
async def send_music_search_results(call: CallbackQuery, callback_data: MusicCD, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading"][lang])
    download_music = AllDownloader(call.message, lang)
    music_path = None
    try:

        music_path, title = await download_music.download_music_from_youtube(callback_data.video_id)
        await call.message.reply_audio(
            FSInputFile(music_path),
            caption=media_process_text["downloadin_by"][lang],
            title=title
        )
    except Exception as e:
        print(e)
        await call.message.answer(text=music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if load_msg:
            await load_msg.delete()
        if await asyncio.to_thread(os.path.exists, music_path):
            await asyncio.to_thread(os.remove, music_path)
