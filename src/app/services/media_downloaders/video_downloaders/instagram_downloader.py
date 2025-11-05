import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple, List

import aiofiles
from instagrapi import Client
from instaloader import instaloader
from yt_dlp import YoutubeDL

from src.app.core.config import Settings
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher
from src.app.services.media_downloaders.utils.downlaod_media import download_media_in_internet
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_photo_file_name
from src.app.utils.enums.error import DownloadError
from src.app.utils.enums.general import MediaType

# Setup logging
logger = logging.getLogger(__name__)


class InstagramDownloaders:

    def __init__(self, session_file: str = "session.json"):
        self.client = Client()
        self.settings = Settings()
        self.searchs = YouTubeSearcher()
        self.yt_dlp = YoutubeDL
        self.session_file = session_file
        self.loader = instaloader.Instaloader(
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

        self.timeout = 120
        self.overall_timeout = 600
        self.max_retries = 5
        self.delay_between_items = 0.5


    async def login(self) -> None:
        try:
            session_exists = await asyncio.to_thread(os.path.exists, self.session_file)

            if session_exists:
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
                    await asyncio.to_thread(os.remove, self.session_file)

            print("🔐 Logging in to Instagram...")
            await asyncio.to_thread(
                self.client.login,
                self.settings.instagram_username,
                self.settings.instagram_password,
                False,
            )

            settings = await asyncio.to_thread(self.client.get_settings)
            json_data = json.dumps(settings, ensure_ascii=False, indent=2)
            async with aiofiles.open(self.session_file, "w", encoding="utf-8") as f:
                await f.write(json_data)

            print("💾 Session saved successfully")

        except Exception as e:
            print(f"🚫 Login error: {e}")

    async def instagram_reels_downloader(
            self,
            reels_url: str
    ) -> Tuple[Optional[str], list]:

        reels_file_name = get_video_file_name()
        reels_video_path = f"./media/videos/{reels_file_name}"
        errors = []

        try:
            await asyncio.to_thread(
                Path("./media/videos").mkdir,
                parents=True,
                exist_ok=True
            )

            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": reels_video_path,
                "socket_timeout": self.timeout,
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4"
                }]
            }

            await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: YoutubeDL(ydl_opts).download([reels_url])
                ),
                timeout=self.timeout
            )

            file_exists = await asyncio.to_thread(os.path.exists, reels_video_path)
            if not file_exists:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                print(f"❌ File not found after download")
                return None, errors

            file_size = await asyncio.to_thread(os.path.getsize, reels_video_path)
            file_size_mb = file_size / (1024 ** 2)

            if file_size > 2000 * 1024 * 1024:
                errors.append(DownloadError.FILE_TOO_BIG)
                print(f"⚠️ File too big: {file_size_mb:.2f}MB")

            print(f"✅ Reels downloaded: {file_size_mb:.2f}MB")
            return reels_video_path, errors

        except asyncio.TimeoutError:
            print("❌ Timeout downloading reels")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

    async def instagram_stories_downloader(
            self,
            stories_url: str
    ) -> Tuple[Optional[Path], list]:

        errors = []

        try:
            story_pk = await asyncio.wait_for(
                asyncio.to_thread(self.client.story_pk_from_url, stories_url),
                timeout=self.timeout
            )

            # Story haqida ma'lumot olish (photo/video aniqlash uchun)
            story = await asyncio.to_thread(self.client.story_info, story_pk)
            media_type = story.media_type  # 1=photo, 2=video

            # Papka tanlash
            if media_type == 1:  # PHOTO
                save_dir = Path("./media/photos/")
                file_name = get_photo_file_name()
            else:  # VIDEO
                save_dir = Path("./media/videos/")
                file_name = get_video_file_name()

            # Papkani yaratish
            await asyncio.to_thread(save_dir.mkdir, parents=True, exist_ok=True)

            # Yuklash
            story_path = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.story_download,
                    story_pk,
                    file_name,
                    save_dir
                ),
                timeout=self.timeout
            )

            # Yuklanmagan bo‘lsa
            if not story_path or not await asyncio.to_thread(os.path.exists, story_path):
                errors.append(DownloadError.DOWNLOAD_ERROR)
                print("❌ Story file not found")
                return None, errors

            # Fayl o‘lchami
            file_size = await asyncio.to_thread(os.path.getsize, story_path)
            print(f"✅ Story downloaded ({'PHOTO' if media_type == 1 else 'VIDEO'}) → {file_size / (1024 ** 2):.2f}MB")

            return story_path, errors

        except Exception as e:
            print(f"❌ Error downloading story: {e}")
            errors.append(DownloadError.UNKNOWN_ERROR)
            return None, errors

        except asyncio.TimeoutError:
            print("❌ Timeout downloading story")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

    def _extract_shortcode(self, url: str) -> str:
        m = re.search(r"/(?:p|reel)/([^/?]+)", url)
        if not m:
            raise ValueError("Shortcode topilmadi")
        return m.group(1)

    async def instagram_post_gettre(self, post_url: str) -> Optional[List]:

        try:
            shortcode = self._extract_shortcode(post_url)

            for attempt in range(self.max_retries):
                try:
                    print(f"📥 Getting post info (attempt {attempt + 1}/{self.max_retries})...")

                    post = await asyncio.wait_for(
                        asyncio.to_thread(
                            instaloader.Post.from_shortcode,
                            self.loader.context,
                            shortcode
                        ),
                        timeout=self.timeout
                    )

                    print(f"📥 Fetching post nodes...")

                    # Get sidecar nodes - returns a GENERATOR
                    sidecar_nodes_generator = await asyncio.wait_for(
                        asyncio.to_thread(post.get_sidecar_nodes),
                        timeout=self.timeout
                    )

                    if sidecar_nodes_generator is None:
                        print(f"⚠️ No nodes returned (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            print(f"⏳ Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                        continue

                    try:
                        sidecar_nodes = list(sidecar_nodes_generator)
                    except Exception as e:
                        print(f"⚠️ Error converting generator to list: {e}")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            await asyncio.sleep(wait_time)
                        continue

                    if not sidecar_nodes:
                        print(f"⚠️ Empty nodes list (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            await asyncio.sleep(wait_time)
                        continue

                    print(f"✅ Got {len(sidecar_nodes)} nodes from post")
                    return sidecar_nodes

                except asyncio.TimeoutError:
                    print(f"⏱️ Timeout (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)

                except Exception as e:
                    error_msg = str(e)

                    if "403" in error_msg or "Forbidden" in error_msg:
                        print(f"⚠️ 403 Forbidden (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            wait_time = (2 ** attempt) * 5
                            print(f"⏳ Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                    else:
                        print(f"❌ Error (attempt {attempt + 1}/{self.max_retries}): {e}")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            await asyncio.sleep(wait_time)

            print(f"❌ Failed to get post after {self.max_retries} attempts")
            return None

        except ValueError as e:
            print(f"❌ Invalid URL: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

    async def instagram_post_downloader(
            self,
            post_url: str
    ) -> Tuple[Optional[list], list]:


        medias = []
        errors = []

        try:
            print(f"📥 Starting post download: {post_url}")

            post_nodes = await self.instagram_post_gettre(post_url)

            if not post_nodes:
                print("❌ No post nodes retrieved")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            total_items = len(post_nodes)
            print(f"📊 Post has {total_items} items")

            for idx, node in enumerate(post_nodes):
                try:
                    is_video = node.is_video
                    media_type_str = "video" if is_video else "photo"

                    print(f"📥 Item {idx + 1}/{total_items}: Downloading {media_type_str}...")

                    try:
                        media_url = node.video_url if is_video else node.display_url

                        if not media_url:
                            print(f"⚠️ Item {idx + 1}: No media URL found")
                            continue
                    except Exception as e:
                        print(f"⚠️ Item {idx + 1}: Error getting media URL: {e}")
                        continue

                    try:
                        file_name = get_video_file_name() if is_video else get_photo_file_name()

                        path = await asyncio.wait_for(
                            download_media_in_internet(
                                url=media_url,
                                file_name=file_name,
                                media_type=MediaType.VIDEO if is_video else MediaType.PHOTO
                            ),
                            timeout=self.timeout
                        )

                        if path:
                            medias.append({
                                "type": "video" if is_video else "photo",
                                "media_path": path,
                                "order": idx
                            })
                            print(f"✅ Item {idx + 1}: Downloaded successfully")
                        else:
                            print(f"⚠️ Item {idx + 1}: Download returned None")

                    except asyncio.TimeoutError:
                        print(f"⏱️ Item {idx + 1}: Download timeout")
                    except Exception as e:
                        print(f"⚠️ Item {idx + 1}: Download error: {e}")

                except Exception as e:
                    print(f"❌ Item {idx + 1}: Error: {e}")
                    continue

            if not medias:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            print(f"✅ Post download completed: {len(medias)} items")
            return medias, errors

        except Exception as e:
            print(f"❌ Post download error: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

    async def instagram_highlight_downloader(
            self,
            highlight_url: str
    ) -> Tuple[Optional[list], list]:


        errors = []
        paths = []
        failed_items = []

        try:
            print(f"📥 Starting highlight download: {highlight_url}")

            try:
                highlight_pk = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.highlight_pk_from_url,
                        highlight_url
                    ),
                    timeout=self.timeout
                )
                print(f"✅ Got highlight PK: {highlight_pk}")
            except asyncio.TimeoutError:
                print("❌ Timeout getting highlight PK")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors
            except Exception as e:
                print(f"❌ Error getting highlight PK: {e}")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors


            try:
                info = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.highlight_info,
                        highlight_pk
                    ),
                    timeout=self.timeout
                )
                print(f"✅ Got highlight info with {len(info.items)} items")
            except asyncio.TimeoutError:
                print("❌ Timeout getting highlight info")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors
            except Exception as e:
                print(f"❌ Error getting highlight info: {e}")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            if not info or not info.items:
                print("❌ No items in highlight")
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            total_items = len(info.items)
            print(f"📊 Total items to download: {total_items}")

            for item_idx, item in enumerate(info.items):
                print(f"📥 Processing item {item_idx + 1}/{total_items}...")

                path = await self._download_single_highlight_item(
                    item=item,
                    item_idx=item_idx,
                    total_items=total_items
                )

                if path:
                    paths.append(path)
                    print(f"✅ Item {item_idx + 1}: Success")
                else:
                    failed_items.append(item_idx + 1)
                    print(f"❌ Item {item_idx + 1}: Failed")

                if item_idx < total_items - 1:
                    await asyncio.sleep(self.delay_between_items)

            if failed_items:
                print(f"⚠️ Failed items: {failed_items}")

            if not paths:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            return paths, errors

        except Exception as e:
            print(f"❌ Highlight download error: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

    async def _download_single_highlight_item(
            self,
            item,
            item_idx: int,
            total_items: int
    ) -> Optional[str]:

        for attempt in range(self.max_retries):
            try:
                is_video = item.media_type != 1
                media_type_str = "video" if is_video else "photo"

                folder_path = Path("./media/videos" if is_video else "./media/photos")

                try:
                    await asyncio.to_thread(
                        folder_path.mkdir,
                        parents=True,
                        exist_ok=True
                    )
                except Exception as e:
                    print(f"❌ Item {item_idx + 1}: Can't create folder: {e}")
                    return None

                print(f"📥 Item {item_idx + 1}/{total_items}: Downloading {media_type_str}...")

                try:
                    if is_video:
                        path = await asyncio.wait_for(
                            asyncio.to_thread(
                                self.client.video_download,
                                int(item.pk),
                                folder=folder_path
                            ),
                            timeout=self.timeout
                        )
                    else:
                        path = await asyncio.wait_for(
                            asyncio.to_thread(
                                self.client.photo_download,
                                int(item.pk),
                                folder=folder_path
                            ),
                            timeout=self.timeout
                        )

                except asyncio.TimeoutError:
                    print(f"⏱️ Item {item_idx + 1}: Timeout (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"⏳ Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    continue

                if path is None:
                    print(f"⚠️ Item {item_idx + 1}: Download returned None")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue

                file_exists = await asyncio.to_thread(os.path.exists, path)
                if not file_exists:
                    print(f"⚠️ Item {item_idx + 1}: File doesn't exist: {path}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue

                try:
                    file_size = await asyncio.to_thread(os.path.getsize, path)
                    file_size_mb = file_size / (1024 ** 2)
                    file_size_gb = file_size / (1024 ** 3)

                    if file_size == 0:
                        print(f"⚠️ Item {item_idx + 1}: File is empty (0 bytes)")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                        continue

                    if file_size > 2000 * 1024 * 1024:
                        print(f"❌ Item {item_idx + 1}: File too large: {file_size_gb:.2f}GB (max 2GB)")
                        return None

                    print(f"✅ Item {item_idx + 1}: Downloaded {file_size_mb:.2f}MB")
                    return path

                except Exception as e:
                    print(f"⚠️ Item {item_idx + 1}: Error checking file size: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue

            except Exception as e:
                print(f"❌ Item {item_idx + 1}: Download error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                continue

        print(f"❌ Item {item_idx + 1}: Failed after {self.max_retries} attempts")
        return None

    async def instagram_profil_photo_downloader(
            self,
            photo_url: str
    ) -> Tuple[Optional[str], list]:

        photo_file_name = get_photo_file_name()
        photo_path = f"./media/photos/{photo_file_name}"
        errors = []

        try:
            await asyncio.to_thread(
                Path("./media/photos").mkdir,
                parents=True,
                exist_ok=True
            )

            ydl_opts = {
                "outtmpl": photo_path,
                "skip_download": False,
                "socket_timeout": self.timeout
            }

            await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: YoutubeDL(ydl_opts).download([photo_url])
                ),
                timeout=self.timeout
            )

            file_exists = await asyncio.to_thread(os.path.exists, photo_path)
            if not file_exists:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                print(f"❌ Profile photo not found")
                return None, errors

            file_size = await asyncio.to_thread(os.path.getsize, photo_path)
            file_size_mb = file_size / (1024 ** 2)

            if file_size > 2000 * 1024 * 1024:
                errors.append(DownloadError.FILE_TOO_BIG)
                print(f"⚠️ Profile photo too big: {file_size_mb:.2f}MB")

            print(f"✅ Profile photo downloaded: {file_size_mb:.2f}MB")
            return photo_path, errors

        except asyncio.TimeoutError:
            print("❌ Timeout downloading profile photo")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
