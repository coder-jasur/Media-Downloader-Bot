# # # import asyncio
# # # import subprocess
# # # from pedalboard import Pedalboard, Reverb, HighpassFilter, LowpassFilter, Compressor
# # # from pedalboard.io import AudioFile
# # #
# # # async def add_concert_effect(input_mp3: str, output_wav: str = "concert_hall.wav"):
# # #     """MP3 faylga konsert zal effektini tiniqroq ovoz bilan qo‘shadi."""
# # #     temp_wav = "temp.wav"
# # #
# # #     # MP3 → WAV konvertatsiya
# # #     ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_mp3, temp_wav]
# # #     process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
# # #     await process.wait()
# # #
# # #     # Effektlar
# # #     def process_audio():
# # #         with AudioFile(temp_wav) as f:
# # #             audio = f.read(f.frames)
# # #             samplerate = f.samplerate
# # #
# # #         board = Pedalboard([
# # #             HighpassFilter(cutoff_frequency_hz=180),     # past tovushlarni yumshatadi
# # #             LowpassFilter(cutoff_frequency_hz=9000),     # yuqori chastotalarni tiniq qiladi
# # #             Reverb(room_size=0.82, wet_level=0.55, dry_level=0.5, width=1.0),  # tabiiy zal effekti
# # #             Compressor(threshold_db=-12, ratio=2.5),     # ovozni barqaror, tiniq qiladi
# # #         ])
# # #
# # #         effected = board(audio, samplerate)
# # #         with AudioFile(output_wav, "w", samplerate, effected.shape[0]) as f:
# # #             f.write(effected)
# # #         return output_wav
# # #
# # #     result = await asyncio.to_thread(process_audio)
# # #     return result
# # #
# # #
# # # # Test
# # # async def main():
# # #     file = await add_concert_effect("input.mp3")
# # #     print("✅ Effekt tayyor:", file)
# # #
# # # if __name__ == "__main__":
# # #     asyncio.run(main())
# # #
# # # import asyncio
# # # # import os
# # # #
# # # # async def change_audio_speed(input_file: str, output_file: str, speed: float):
# # # #     # speed < 1 → sekinroq, speed > 1 → tezroq
# # # #     cmd = [
# # # #         "ffmpeg", "-y", "-i", input_file,
# # # #         "-filter:a", f"atempo={speed}",
# # # #         output_file
# # # #     ]
# # # #     process = await asyncio.create_subprocess_exec(*cmd)
# # # #     await process.wait()
# # # #     return output_file
# # # #
# # # # async def main():
# # # #     input_mp3 = "input.mp3"
# # # #
# # # #     slowed = await change_audio_speed(input_mp3, "slowed.mp3", 0.85)
# # # #     speeded = await change_audio_speed(input_mp3, "speeded.mp3", 1.25)
# # # #
# # # #     print("✅ Slowed:", slowed)
# # # #     print("✅ Speeded:", speeded)
# # # #
# # # # if __name__ == "__main__":
# # # #     asyncio.run(main())
# # #
# # #
# # # async def make_slowed_deep(input_file: str, output_file: str):
# # #     cmd = [
# # #         "ffmpeg", "-y", "-i", input_file,
# # #         "-filter_complex", "[0:a]asetrate=44100*0.85,aresample=44100,atempo=1.0,volume=1.05[a]",
# # #         "-map", "[a]", output_file
# # #     ]
# # #     process = await asyncio.create_subprocess_exec(*cmd)
# # #     await process.wait()
# # #     return output_file
# # #
# # # async def main():
# # #     slowed_file = await make_slowed_deep("input.mp3", "slowed_deep.mp3")
# # #     print("✅ Slowed & Deep version:", slowed_file)
# # #
# # # if __name__ == "__main__":
# # #     asyncio.run(main())
# #
# # # import yt_dlp
# # #
# # # url = "https://www.instagram.com/p/DO5y0bMDdT9/?img_index=1"
# # #
# # # ydl_opts = {
# # #     "extract_flat": False,  # playlistni ichidagi fayllarni ham yuklaydi
# # #     "skip_download": False, # agar yuklab olmoqchi bo‘lsang
# # # }
# # #
# # # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# # #     info = ydl.extract_info(url, download=False)
# # #     print(info)
# #
# #
# # #
# # # def get_instagram_profile_pic(profile_url: str) -> str | None:
# # #     # Foydalanuvchi nomini URL'dan ajratamiz
# # #     match = re.search(r"instagram\.com/([^/?]+)", profile_url)
# # #     if not match:
# # #         return None
# # #
# # #     username = match.group(1)
# # #
# # #     # Instagram JSON API manzili
# # #     json_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
# # #
# # #     headers = {
# # #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# # #     }
# # #
# # #     try:
# # #         response = requests.get(json_url, headers=headers)
# # #         if response.status_code == 200:
# # #             data = response.json()
# # #             return data["graphql"]["user"]["profile_pic_url_hd"]
# # #         else:
# # #             print("❌ Instagram qaytardi:", response.status_code)
# # #             return None
# # #     except Exception as e:
# # #         print("Xato:", e)
# # #         return None
# # #
# # #
# # # url = "https://www.instagram.com/botirqodirovofficial/"
# # # pic = get_instagram_profile_pic(url)
# # #
# # # if pic:
# # #     print("Profil rasmi URL:", pic)
# # # else:
# # #     print("Topilmadi yoki xato!")
# #
# # # path = {'path': WindowsPath('D:/Jasur/PycharmProjects/downloader-from-social-networks-bot/media/videos/wellcom.market_3727233407970573565.mp4'), 'type': 'unknown'}
# # #
# # # print(path["path"])
# #
# #
# # import asyncio
# #
# # import aiofiles
# # import aiohttp
# #
# # from src.app.services.media_downloaders.utils.files import get_video_file_name
# #
# #
# # async def tiktok_video_downloader(video_url: str):
# #     file_name = get_video_file_name()
# #
# #     api_url = f"https://tiktok-dl.akalankanime11.workers.dev/?url={video_url}"
# #
# #     video_output_path = f"./media/videos/{file_name}"
# #     try:
# #
# #         async with aiohttp.ClientSession() as session:
# #             async with session.get(api_url) as resp:
# #                 if resp.status != 200:
# #                     print(f"ERROR: {resp.status}")
# #                     return
# #                 data = await resp.json()
# #
# #         error = []
# #
# #         video_download_url = data.get("non_watermarked_url")
# #
# #         file_size = int(data.get("file_size")) / 1024 * 1024
# #
# #         if not video_download_url:
# #             error.append("error_in_downloading")
# #             return video_download_url, error
# #
# #         if file_size and file_size > 2000:
# #             error.append("video_file_is_so_big")
# #
# #         async with aiohttp.ClientSession() as session:
# #             async with session.get(video_download_url) as response:
# #                 if response.status == 200:
# #                     async with aiofiles.open(video_output_path, "wb") as f:
# #                         await f.write(await response.read())
# #
# #         return video_output_path, error
# #     except Exception as e:
# #         print("ERROR", e)
# #
# # if __name__ == "__main__":
# #     asyncio.run(tiktok_video_downloader("https://www.instagram.com/p/DPtQde7jQy6/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=="))
# #
# # import aiohttp
# # import asyncio
# # from bs4 import BeautifulSoup
# #
# # async def get_instagram_media(url: str) -> str | None:
# #     """
# #     ssinsta.io orqali Instagram postdan video yoki rasm linkini olish.
# #     :param url: Instagram post URL
# #     :return: Yuklab olish uchun to‘g‘ridan-to‘g‘ri link yoki None
# #     """
# #     ssinsta_url = "https://ssinsta.io/system/action.php"
# #
# #     headers = {
# #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
# #                       "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
# #         "Referer": "https://ssinsta.io/",
# #         "Accept-Language": "uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7",
# #     }
# #
# #     async with aiohttp.ClientSession() as session:
# #         async with session.post(
# #             ssinsta_url,
# #             data={"url": url, "action": "post"},
# #             headers=headers,
# #         ) as resp:
# #             html = await resp.text()
# #
# #     # HTML dan yuklab olish linkini ajratamiz
# #     soup = BeautifulSoup(html, "html.parser")
# #
# #     # ssinsta sahifasida media link odatda "download-btn" classidagi <a> ichida bo‘ladi
# #     download_link = soup.find("a", class_="download-btn")
# #
# #     if download_link and download_link.get("href"):
# #         return download_link["href"]
# #
# #     return None
# import asyncio
# #_----------------------------vajna---------------------------------------------------------
#
# # import instaloader
# #
# # def download_post(url: str):
# #     loader = instaloader.Instaloader(download_comments=False)
# #     # Login qilish ixtiyoriy
# #     # loader.login("username", "password")
# #
# #     post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
# #     loader.download_post(post, target="downloads")
# #
# # download_post("https://www.instagram.com/p/DJEJgMvCtbs/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==")
#
# #_----------------------------vajna---------------------------------------------------------
#
#
#
# # import os
# # import re
# # import asyncio
# # import aiohttp
# # import aiofiles
# # import instaloader
# # from typing import List, Dict, Optional
# #
# # from instagrapi import Client
# #
# #
# # class InstagramDownloader:
# #     def __init__(self, cookie_path: Optional[str] = None):
# #         self.loader = instaloader.Instaloader(download_comments=False, save_metadata=False)
# #         self.cl = Client()
# #         #
# #
# #     # --- yordamchi: highlight id ajratish ---
# #     def _extract_highlight_id(self, url: str) -> str:
# #         m = re.search(r"highlights/(\d+)", url)
# #         if not m:
# #             raise ValueError("Highlight ID topilmadi")
# #         return m.group(1)
# #
# #     # --- yangi: highlight URL dan username topishga harakat qiladi ---
# #     async def detect_username_from_highlight(self, url: str):
# #         headers = {"User-Agent": "Mozilla/5.0"}
# #         async with aiohttp.ClientSession(headers=headers) as s:
# #             async with s.get(url, timeout=15) as r:
# #                 text = await r.text()
# #         m = re.search(r'/stories/([A-Za-z0-9_.-]+)/', text)
# #         if m:
# #             return m.group(1)
# #         m2 = re.search(r'"owner"\s*:\s*\{[^}]*"username"\s*:\s*"([^"]+)"', text)
# #         if m2:
# #             return m2.group(1)
# #         return None
# #
# #     # --- highlightni yuklash: endi username ni URL dan avtomatik aniqlaydi ---
# #     def get_highlight_medias_from_username_and_id(self, username: str, highlight_id: str) -> List[Dict]:
# #         profile = instaloader.Profile.from_username(self.loader.context, username)
# #         for highlight in self.loader.get_highlights(profile):
# #             if str(highlight.unique_id) == str(highlight_id):
# #                 return [
# #                     {"type": "video" if it.is_video else "image",
# #                      "url": it.video_url if it.is_video else it.url}
# #                     for it in highlight.get_items()
# #                 ]
# #         raise ValueError("Highlight topilmadi (username/ID mos kelmaydi yoki private account).")
# #
# #     async def get_highlight_medias_from_url(self, highlight_url: str) -> List[Dict]:
# #         self.loader.login("toploaderbot", "downloaderbot_009")
# #         print(11111111)
# #         """
# #         Public highlight URL beriladi.
# #         1) highlight id ajratiladi
# #         2) sahifadan username topishga harakat qilinadi
# #         3) agar username topilsa -> instaloader bilan media olishga urinadi
# #         """
# #         highlight_id = self._extract_highlight_id(highlight_url)
# #         print(highlight_id)
# #         username = await self.detect_username_from_highlight(highlight_url)
# #         print(username)
# #         if not username:
# #             raise ValueError("Username topilmadi — highlight sahifasi bloklangan yoki JS orqali yuklanadi.")
# #
# #         # endi instaloader bilan highlightni olamiz
# #         return self.get_highlight_medias_from_username_and_id(username, highlight_id)
# #
# #     # --- post / reel ---
# #     def _extract_shortcode(self, url: str) -> str:
# #         m = re.search(r"/(?:p|reel)/([^/?]+)", url)
# #         if not m:
# #             raise ValueError("Shortcode topilmadi")
# #         return m.group(1)
# #
# #     def get_post_medias(self, post_url: str) -> List[Dict]:
# #         shortcode = self._extract_shortcode(post_url)
# #         post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
# #         medias = []
# #         try:
# #             for node in post.get_sidecar_nodes():
# #                 medias.append({"type": "video" if node.is_video else "image",
# #                                "url": node.video_url if node.is_video else node.display_url})
# #         except Exception:
# #             if post.is_video:
# #                 medias.append({"type": "video", "url": post.video_url})
# #             else:
# #                 medias.append({"type": "image", "url": post.url})
# #         return medias
# #
# #     # --- storylarni olish username orqali (agar cookie bilan login yoq bo'lsa ishlaydi) ---
# #     def get_story_medias(self, url: str) -> List[Dict]:
# #         self.cl.login("toploaderbot", "downloaderbot_009")
# #         self.loader.login("toploaderbot", "downloaderbot_009")
# #         username = url.split("/")[4]
# #         print(username)
# #         profile = instaloader.Profile.from_username(self.loader.context, username)
# #         stories = []
# #         for story in self.loader.get_stories(userids=[profile.userid]):
# #             for item in story.get_items():
# #                 stories.append({"type": "video" if item.is_video else "image",
# #                                 "url": item.video_url if item.is_video else item.url})
# #         return stories
# #
# #     # --- yuklash (async) ---
# #     async def download_all(self, medias: List[Dict], target_dir: str = "./downloads"):
# #         os.makedirs(target_dir, exist_ok=True)
# #         timeout = aiohttp.ClientTimeout(total=120)
# #         headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
# #         async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
# #             for idx, media in enumerate(medias):
# #                 ext = ".mp4" if media["type"] == "video" else ".jpg"
# #                 file_path = os.path.join(target_dir, f"media_{idx}{ext}")
# #                 try:
# #                     async with session.get(media["url"]) as resp:
# #                         if resp.status == 200:
# #                             async with aiofiles.open(file_path, "wb") as f:
# #                                 await f.write(await resp.read())
# #                             print("✅ Saved:", file_path)
# #                         else:
# #                             print("❌ HTTP", resp.status, "for", media["url"])
# #                 except Exception as e:
# #                     print("❌ Download error:", e, "for", media["url"])
#
# import os
# from pathlib import Path
#
# import aiohttp
# import aiofiles
# from instagrapi import Client
#
# from src.app.handlers.user.media_downloader import send_music_results_from_video
# from src.app.services.media_downloaders.utils.files import get_video_file_name
#
#
# class InstagramDownloader:
#     def __init__(self, username: str, password: str):
#         self.client = Client()
#         self.username = username
#         self.password = password
#         self.login()
#
#     def login(self):
#         try:
#             self.client.login(self.username, self.password)
#         except Exception as e:
#             raise Exception(f"Login error: {e}")
#
#     async def _download_file(self, url: str, output_path: str):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as response:
#                 if response.status == 200:
#                     async with aiofiles.open(output_path, "wb") as f:
#                         await f.write(await response.read())
#                 else:
#                     raise Exception(f"Download failed: {response.status}")
#
#     async def download_story(self, url: str, output_dir: str = "./media/videos"):
#         """
#         Berilgan foydalanuvchining aktiv storylarini yuklab oladi.
#         """
#
#         story_pk = self.client.story_pk_from_url(url)
#         output_file_path = self.client.story_download(story_pk, get_video_file_name(), Path(output_dir))
#         print(output_file_path)
#
#     async def download_highlights(self, url: str):
#         try:
#             # 1️⃣ Highlight PK ni URL'dan olish
#             highlight_pk = self.client.highlight_pk_from_url(url)
#             highlight = self.client.highlight_info(highlight_pk)
#             items = highlight["items"]
#             if not items:
#                 print("⚠️ Hech qanday media topilmadi.")
#                 return []
#
#             # 3️⃣ Video URL’larni yig‘ish
#             video_urls = []
#             for item in items:
#                 video_url = getattr(item, "video_url", None)
#                 if video_url:
#                     video_urls.append(str(video_url))
#
#             print(f"🎥 {len(video_urls)} ta video topildi.")
#             print(video_urls)
#
#
#         except Exception as e:
#             print(f"❌ Xatolik: {e}")
#             return []
#
#         #     # 2️⃣ Highlightdagi barcha itemlarni olish
#         #     items = highlight.get('items', [])
#         #     if not items:
#         #         print("⚠️ Highlight bo‘sh yoki mavjud emas.")
#         #         return
#         #
#         #     print(f"📦 '{highlight['title']}' ichida {len(items)} ta media topildi.")
#         #
#         #     # 3️⃣ Har bir itemni yuklab olish
#         #     for i, item in enumerate(items):
#         #         media_url = item.get("video_url") or item.get("image_versions2", {}).get("candidates", [{}])[0].get(
#         #             "url")
#         #         if not media_url:
#         #             continue
#         #
#         #         ext = ".mp4" if item.get("video_url") else ".jpg"
#         #         file_path = Path(output_dir) / f"highlight_{i}{ext}"
#         #
#         #         # 🔽 Yuklab olish
#         #         await self._download_file(media_url, file_path)
#         #         print(f"✅ Saqlandi: {file_path}")
#         #
#         # except Exception as e:
#         #     print(f"❌ Xatolik: {e}")
#         # user_id = self.client.user_id_from_username(username)
#         # highlights = self.client.user_highlights(user_id=user_id)
#         #
#         # if not highlights:
#         #     print(f"{username} da highlight yo‘q.")
#         #     return
#         #
#         # for hl in highlights:
#         #     title = hl.title.replace(" ", "_")
#         #     for i, item in enumerate(hl.items):
#         #         url = item.video_url or item.thumbnail_url
#         #         ext = ".mp4" if item.video_url else ".jpg"
#         #         path = os.path.join(output_dir, f"{username}_{title}_{i}{ext}")
#         #         await self._download_file(str(url), path)
#         #         print(f"✅ Highlight '{title}' saqlandi: {path}")
#
#
# # ==== namuna ishlatish ====
# # async def example_highlight_download():
# #     url = "https://www.instagram.com/stories/jajo_toy/3753483727989963077/"
# #     ig = InstagramDownloader("alphin8877", "downloaderbot009")  # cookie mavjud bo'lsa yaxshiroq
# #     try:
# #         await ig.download_story(url)
# #
# #     except Exception as e:
# #         print("Error:", e)
# #         return
# #
# #
# # if __name__ == "__main__":
# #     asyncio.run(example_highlight_download())
#
#
# import asyncio
# # from instagram_downloader import InstagramDownloader
#
# async def main():
#     insta = InstagramDownloader("alphin8877", "downloaderbot009")
#     # await insta.download_story("https://www.instagram.com/stories/wellcom.market/3753923583232786819/")
#     await insta.download_highlights("https://www.instagram.com/stories/highlights/17893547171368538/")
#
# asyncio.run(main())

import asyncio
import time
from typing import List, Dict, Optional
from urllib.parse import quote_plus

import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup, Message

API_KEY = "d942dd5ca4c9ee5bd821df58cf8130d4"
API_URL = "http://ws.audioscrobbler.com/2.0/"

bot = Bot(token="7828679913:AAGFggun0tMWEDlGEQjcOIjzyJwG8czBoBA")
dp = Dispatcher()


SUPPORTED_COUNTRIES = {
    "uz": ("🇺🇿", "Uzbekistan"),
    "ru": ("🇷🇺", "Russia"),
    "en": ("🇺🇸", "United States"),
    "kz": ("🇰🇿", "Kazakhstan"),
    "kg": ("🇰🇬", "Kyrgyzstan"),
    "az": ("🇦🇿", "Azerbaijan"),
    "tj": ("🇹🇯", "Tajikistan"),
}

# ====== SIMPLE IN-MEM CACHE ======
_API_CACHE: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 60 * 60  # 1 hour


def cache_get(key: str):
    rec = _API_CACHE.get(key)
    if not rec:
        return None
    ts, value = rec
    if time.time() - ts > CACHE_TTL_SECONDS:
        _API_CACHE.pop(key, None)
        return None
    return value


def cache_set(key: str, value):
    _API_CACHE[key] = (time.time(), value)


# ====== Last.fm helpers ======
async def get_top_tracks_by_country(country_fullname: str, limit: int = 50) -> List[Dict[str, str]]:
    """
    Return list of tracks: [{'artist': '...', 'title': '...'}, ...]
    country_fullname should be full name accepted by Last.fm (e.g. 'Uzbekistan').
    """
    cache_key = f"lastfm:geo:{country_fullname}:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params = {
        "method": "geo.gettoptracks",
        "country": country_fullname,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, timeout=15) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
    except Exception:
        return []

    tracks = data.get("tracks", {}).get("track", []) or []
    result: List[Dict[str, str]] = []
    for t in tracks:
        # artist in Last.fm response is usually dict with 'name'
        artist_obj = t.get("artist")
        artist = artist_obj.get("name") if isinstance(artist_obj, dict) else (artist_obj or "")
        title = t.get("name") or ""
        result.append({"artist": artist, "title": title})

    cache_set(cache_key, result)
    return result


# ====== UI helpers ======
PAGE_SIZE = 10


def country_row(selected: Optional[str] = None) -> List[InlineKeyboardButton]:
    """Return list of InlineKeyboardButton for one row of country flags (selected marked)."""
    row = []
    for code, (flag, _) in SUPPORTED_COUNTRIES.items():
        suffix = " ✅" if code == selected else ""
        row.append(InlineKeyboardButton(text=f"{flag}{suffix}", callback_data=f"country:{code}:1"))
    return row


def songs_keyboard(tracks: List[Dict[str, str]], country_code: str, page: int = 1) -> InlineKeyboardMarkup:
    """Build full inline keyboard: country row, then tracks, pagination, close."""
    inline_keyboard: List[List[InlineKeyboardButton]] = []

    # top: one row with country flags
    inline_keyboard.append(country_row(selected=country_code))

    # tracks (one per row)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    sliced = tracks[start:end]
    for i, t in enumerate(sliced, start=start):
        label = f"{i+1}. {t.get('artist','Unknown')} — {t.get('title','Unknown')}"
        if len(label) > 64:
            label = label[:61] + "..."
        inline_keyboard.append([InlineKeyboardButton(text=label, callback_data=f"track:{country_code}:{i}")])

    # pagination row
    total = len(tracks)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total else 1
    nav_buttons: List[InlineKeyboardButton] = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"page:{country_code}:{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"page:{country_code}:{page+1}"))
    if nav_buttons:
        inline_keyboard.append(nav_buttons)

    # close
    inline_keyboard.append([InlineKeyboardButton(text="❌ Close", callback_data="close")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def make_tracks_text(tracks: List[Dict[str, str]], page: int) -> str:
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    sliced = tracks[start:end]
    if not sliced:
        return "Hech nima topilmadi."
    lines = [f"{i+1}. {t.get('artist','Unknown')} — {t.get('title','Unknown')}" for i, t in enumerate(sliced, start=start)]
    return "\n".join(lines)


# ====== Handlers ======
@dp.message(Command("music"))
async def cmd_music(message: Message):
    """
    On /music show immediately Uzbekistan trending tracks (no language selection).
    """
    code = "uz"
    _, full_country = SUPPORTED_COUNTRIES[code]
    page = 1

    tracks = await get_top_tracks_by_country(full_country, limit=50)
    if not tracks:
        await message.answer("Qo‘shiq ma’lumotlarini olishda xatolik yoki maʼlumot topilmadi.")
        return

    text = f"🎧 Top qo‘shiqlar — {full_country} (sahifa {page}):\n\n" + make_tracks_text(tracks, page)
    kb = songs_keyboard(tracks, country_code=code, page=page)
    await message.answer(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("country:"))
async def choose_country(callback: CallbackQuery):
    # country:{code}:{page}
    try:
        _, code, page_s = callback.data.split(":")
        page = int(page_s)
    except Exception:
        return await callback.answer("Noto'g'ri callback!", show_alert=True)

    if code not in SUPPORTED_COUNTRIES:
        return await callback.answer("Qo'llab-quvvatlanmaydigan davlat.", show_alert=True)

    _, full_country = SUPPORTED_COUNTRIES[code]
    tracks = await get_top_tracks_by_country(full_country, limit=50)
    if not tracks:
        return await callback.answer("Ma'lumot topilmadi ❗", show_alert=True)

    text = f"🎧 TOP qo‘shiqlar — {full_country} (sahifa {page}):\n\n" + make_tracks_text(tracks, page)
    kb = songs_keyboard(tracks, country_code=code, page=page)
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        # agar edit mumkin bo'lmasa, yangi message yuborish
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data.startswith("page:"))
async def page_handler(callback: CallbackQuery):
    # page:{code}:{page}
    try:
        _, code, page_s = callback.data.split(":")
        page = int(page_s)
    except Exception:
        return await callback.answer("Noto'g'ri callback!", show_alert=True)

    if code not in SUPPORTED_COUNTRIES:
        return await callback.answer("Qo'llab-quvvatlanmaydigan davlat.", show_alert=True)

    _, full_country = SUPPORTED_COUNTRIES[code]
    tracks = await get_top_tracks_by_country(full_country, limit=50)
    if not tracks:
        return await callback.answer("Ma'lumot topilmadi ❗", show_alert=True)

    text = f"🎧 TOP qo‘shiqlar — {full_country} (sahifa {page}):\n\n" + make_tracks_text(tracks, page)
    kb = songs_keyboard(tracks, country_code=code, page=page)
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data.startswith("track:"))
async def track_handler(callback: CallbackQuery):
    # track:{code}:{index}
    try:
        _, code, idx_s = callback.data.split(":")
        idx = int(idx_s)
    except Exception:
        return await callback.answer("Noto'g'ri callback!", show_alert=True)

    if code not in SUPPORTED_COUNTRIES:
        return await callback.answer("Qo'llab-quvvatlanmaydigan davlat.", show_alert=True)

    _, full_country = SUPPORTED_COUNTRIES[code]
    tracks = await get_top_tracks_by_country(full_country, limit=50)
    if not tracks or idx < 0 or idx >= len(tracks):
        return await callback.answer("Qo'shiq topilmadi.", show_alert=True)

    t = tracks[idx]
    artist = t.get("artist", "Unknown")
    title = t.get("title", "Unknown")
    query = quote_plus(f"{artist} {title}")
    yt_link = f"https://www.youtube.com/results?search_query={query}"
    text = f"🎵 <b>{artist} — {title}</b>\n\n🔎 YouTube qidiruv: {yt_link}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "close")
async def close_handler(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


# small safety handler
@dp.callback_query(F.data == "ignore")
async def ignore_cb(callback: CallbackQuery):
    await callback.answer()


# ====== Runner ======
async def main():
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
