import asyncio
import os

import aiohttp
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto, InputMediaVideo

from src.app.keyboards.callback_data import MusicCD, SearchMusicInVideoCD, AudioCD, AudioEffectCD
from src.app.keyboards.inline import video_keyboards, music_keyboards
from src.app.services.media_downloaders.all_downloader import AllDownloader
from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.services.media_effects.media_effects import MediaEffects
from src.app.states.user.audio_effect import SendAudioSG
from src.app.texts import (
    media_process_text, user_texts, video_process_texts, music_and_audio_process_texts,
    photo_process_texts
)

media_downloader_router = Router()


@media_downloader_router.callback_query(AudioEffectCD.filter())
async def audio_effect(call: CallbackQuery, callback_data: AudioEffectCD, state: FSMContext, lang: str):
    await state.update_data(
        {
            "audio_effect": callback_data.effect
        }
    )
    await state.set_state(SendAudioSG.send_audio)
    await call.message.edit_text(music_and_audio_process_texts["send_audio"][lang])


@media_downloader_router.message(SendAudioSG.send_audio)
async def audio_effect(message: Message, state: FSMContext, lang: str):
    load_msg = await message.answer(music_and_audio_process_texts["is_being_processed"][lang])
    media = None
    try:
        data = await state.get_data()
        media_effect = MediaEffects(message)
        media = await media_effect.media_effect(data["audio_effect"])
        if message.video:
            await message.answer_video(
                FSInputFile(media),
                caption=media_process_text["downloadin_by"][lang],
                title="effect audio"
            )
        if message.audio or message.voice:
            await message.answer_audio(
                FSInputFile(media),
                caption=media_process_text["downloadin_by"][lang],
                title=f"{message.audio.title} {data["audio_effect"]} remix" or f"voice {data["audio_effect"]} remix"
            )
    except Exception as e:
        print("ERROR", e)
        await message.answer(music_and_audio_process_texts["erro_in_downloading"][lang])
    finally:
        await state.clear()
        if load_msg:
            await load_msg.delete()
        if media and await asyncio.to_thread(os.path.exists, media):
            await asyncio.to_thread(os.remove, media)


@media_downloader_router.message(F.text | F.video | F.video_note | F.voice | F.audio)
async def all_downloader_(message: Message, lang: str):
    for f in [message.audio, message.voice, message.video, message.video_note]:
        if f:
            if f.file_size > 2000 * 1024 * 1024:
                await message.answer(media_process_text["very_big_file"][lang])
                return

    video_path = None
    post_paths = None
    photo_path = None
    highlights_path = None
    load_msg = None
    all_downloader = AllDownloader(message=message, lang=lang)

    try:
        if message.text:
            if "https://" in message.text[:8]:
                if "instagram" in message.text:
                    if "https://www.instagram.com/stories/highlights/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        highlights_path = await all_downloader.instagram_downloaders(message.text, "highlights")
                        for highlight_path in highlights_path:
                            await message.reply_video(
                                FSInputFile(highlight_path),
                                reply_markup=video_keyboards(
                                    lang
                                ),
                                caption=media_process_text["downloadin_by"][lang]
                            )


                    elif "https://www.instagram.com/stories/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path = await all_downloader.instagram_downloaders(message.text, "stories")
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    elif "https://www.instagram.com/" in message.text and "p/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        print(111)
                        post_paths = await all_downloader.instagram_downloaders(message.text, "post")
                        print(photo_path)
                        for post in post_paths:
                            if "/media/videos/" in post["path"]:
                                await message.reply_video(
                                    FSInputFile(post["path"]),
                                    caption=media_process_text["downloadin_by"][lang],
                                    reply_markup=video_keyboards(lang)
                                )

                            elif "/media/photos/" in post or "shifted_media" in post["path"]:
                                media_group = []

                                for i, media in enumerate(post["path"]):
                                    if i == 0:
                                        if "/media/videos/" in media:
                                            media_group.append(
                                                InputMediaVideo(
                                                    media=FSInputFile(media),
                                                    caption=media_process_text["downloadin_by"][lang]
                                                )
                                            )
                                        elif "/media/photos/" in media:
                                            media_group.append(
                                                InputMediaPhoto(
                                                    media=FSInputFile(media),
                                                    caption=media_process_text["downloadin_by"][lang]
                                                )
                                            )

                                    else:
                                        media_group.append(InputMediaPhoto(media=FSInputFile(media)))
                                await message.reply_media_group(media=media_group)
                                break

                    elif "www.instagram.com" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path = await all_downloader.instagram_downloaders(message.text, "reels")
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    else:
                        load_msg = await message.answer(photo_process_texts["downloading"][lang])
                        photo_path = await all_downloader.instagram_downloaders(message.text, "profil_photo")
                        await message.reply_photo(
                            FSInputFile(photo_path),
                            caption=media_process_text["downloadin_by"][lang]
                        )

                elif "www.youtube.com" in message.text:
                    url = message.text
                    if "&" in message.text or "&list=" in message.text:
                        url = message.text.split("&")[0]

                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path = await all_downloader.youtube_downloaders(url)

                    await message.reply_video(
                        FSInputFile(video_path),
                        reply_markup=video_keyboards(
                            lang
                        ),
                        caption=media_process_text["downloadin_by"][lang]
                    )


                elif "www.tiktok.com" in message.text:
                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path = await all_downloader.tiktok_downloaders(message.text)

                    await message.reply_video(
                        FSInputFile(video_path),
                        reply_markup=video_keyboards(
                            lang
                        ),
                        caption=media_process_text["downloadin_by"][lang]
                    )


                else:
                    await message.answer(video_process_texts["wrong_link"][lang])
            else:
                load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    "search_music_by_text_or_avtro_name",
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )

        elif message.video or message.video_note or message.audio or message.voice:
            load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
            if message.video:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    "search_music_by_media",
                    "video"
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )

            if message.video_note:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    "search_music_by_media",
                    "video_note"
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
            if message.audio:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    "search_music_by_media",
                    "audio"
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
            if message.voice:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    "search_music_by_media",
                    "voice"
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
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

        if post_paths:
            for post in post_paths:
                if await asyncio.to_thread(os.path.exists, post["path"]):
                    await asyncio.to_thread(os.remove, post["path"])

        if highlights_path:
            for highlight_path in highlights_path:
                if await asyncio.to_thread(os.path.exists, highlight_path):
                    await asyncio.to_thread(os.remove, highlight_path)


@media_downloader_router.callback_query(SearchMusicInVideoCD.filter())
async def send_music_results_from_video(call: CallbackQuery, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading"][lang])
    all_downloader = AllDownloader(call.message)
    thumbnail_path = None
    try:
        musics_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
            actions="search_music_by_media",
            media_type="video"
        )

        if musics_list:
            if thumbnail_path:
                await call.message.reply_photo(
                    photo=FSInputFile(thumbnail_path),
                    caption=music_title,
                    reply_markup=music_keyboards(musics_list)
                )
            else:
                await call.message.reply(
                    text=music_title,
                    reply_markup=music_keyboards(musics_list)
                )
        else:
            await call.message.edit_text(music_and_audio_process_texts["error_in_downloading"][lang])
    except Exception as e:
        print("ERROR", e)
        await call.message.answer(music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if await asyncio.to_thread(os.path.exists, thumbnail_path):
            await asyncio.to_thread(os.remove, thumbnail_path)
        if load_msg:
            await load_msg.delete()


@media_downloader_router.callback_query(MusicCD.filter())
async def send_music_search_results(call: CallbackQuery, callback_data: MusicCD, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading"][lang])
    download_music = AllDownloader()
    music_path = None
    try:
        music_path, title = await download_music.music_downloaders(
            actions="download_music",
            some_data=callback_data.video_id
        )
        print(music_path)
        print(title)

        await call.message.reply_audio(
            audio=FSInputFile(music_path),
            title=title,
            caption=media_process_text["downloadin_by"][lang],
        )
    except Exception as e:
        print("ERROR", e)
        await call.message.answer(text=music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if load_msg:
            await load_msg.delete()
        if music_path:
            if await asyncio.to_thread(os.path.exists, music_path):
                await asyncio.to_thread(os.remove, music_path)


@media_downloader_router.callback_query(AudioCD.filter())
async def send_video_mp3_audio_version(call: CallbackQuery, lang: str, bot: Bot):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading_audio"][lang])
    downloader_audio = AllDownloader()
    audio_path = None
    video_path = None

    try:
        file = await bot.get_file(call.message.video.file_id)

        file_path = file.file_path
        video_path = f"./media/videos/{get_video_file_name()}"

        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    with open(video_path, "wb") as f:
                        f.write(await response.read())
                else:
                    raise Exception(f"Fayl yuklab olinmadi, status: {response.status}")

        audio_path = await downloader_audio.extract_video_to_audio(video_path)

        await call.message.answer_audio(
            FSInputFile(audio_path),
            caption=media_process_text["downloadin_by"][lang],
            title="mp3"
        )

    except Exception as e:
        print("ERROR", e)
        await call.message.answer(text=music_and_audio_process_texts["error_in_downloading_audio"][lang])

    finally:
        if load_msg:
            await load_msg.delete()
        for file in [audio_path, video_path]:
            if file and await asyncio.to_thread(os.path.exists, file):
                await asyncio.to_thread(os.remove, file)
