import asyncio
import logging
import os
import re
import time
from pathlib import Path
from typing import Optional, Tuple, List

import instaloader
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.downlaod_media import download_media_in_internet
from src.app.services.media_downloaders.utils.files import get_video_file_name, get_photo_file_name
from src.app.utils.enums.error import DownloadError
from src.app.utils.enums.general import MediaType

# Setup logging
logger = logging.getLogger(__name__)


class InstagramDownloader:

    def __init__(self):

        self.timeout = 120
        self.loader = instaloader.Instaloader(
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

        self.timeout = 120
        self.max_retries = 5

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
                print("ERROR")
                return None, errors

            file_size = await asyncio.to_thread(os.path.getsize, reels_video_path)
            file_size_mb = file_size / (1024 ** 2)

            if file_size_mb > 2000 * 1024 * 1024:
                errors.append(DownloadError.FILE_TOO_BIG)

            return reels_video_path, errors

        except asyncio.TimeoutError as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

    def setup_driver(self):
        """Headless Chrome driver sozlash"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        return webdriver.Chrome(options=chrome_options)

    def wait_for_download_links(self, driver, timeout=60, check_interval=2):
        """Download buttonlarini kutish"""
        print("⏳ Media linklar kutilmoqda...")
        previous_count = 0
        no_change_count = 0
        max_no_change = 3

        for i in range(0, timeout, check_interval):
            try:
                download_buttons = driver.find_elements(
                    By.CSS_SELECTOR, ".abutton.is-success.is-fullwidth.btn-premium.mt-3"
                )
                current_count = len(download_buttons)

                if current_count > previous_count:
                    print(f"   📥 {current_count} ta link topildi...")
                    previous_count = current_count
                    no_change_count = 0
                elif current_count > 0:
                    no_change_count += 1

                if no_change_count >= max_no_change and current_count > 0:
                    break

                driver.execute_script("window.scrollBy(0, 700);")
                time.sleep(check_interval)

            except Exception as e:
                print(f"ERROR: {e}")
                break

        return previous_count

    def get_instagram_links(self, instagram_url):
        driver = self.setup_driver()
        results = []

        try:
            driver.get("https://snapinsta.to/en2")

            # INPUT FIELD
            fields = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".form-control"))
            )
            input_field = next(f for f in fields if f.is_displayed())

            # JS orqali qiymat berish
            driver.execute_script("""
                var el = document.querySelector('.form-control');
                if (el) {
                    el.value = arguments[0];
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """, instagram_url)

            time.sleep(0.5)

            try:
                input_field.clear()
                input_field.send_keys(instagram_url)
            except:
                driver.execute_script(
                    "arguments[0].value = arguments[1];", input_field, instagram_url
                )

            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-default"))
            )
            driver.execute_script("arguments[0].click();", download_button)

            time.sleep(3)

            media_count = self.wait_for_download_links(driver)
            if media_count == 0:
                return []

            download_buttons = driver.find_elements(
                By.CSS_SELECTOR, ".abutton.is-success.is-fullwidth.btn-premium.mt-3"
            )

            for btn in download_buttons:
                href = btn.get_attribute("href")
                title = btn.get_attribute("title") or ""

                if href:
                    media_type = (
                        "photo" if "photo" in title.lower() else
                        "video" if "video" in title.lower() else
                        "unknown"
                    )
                    results.append({"url": href, "type": media_type})

            return results

        except Exception:
            import traceback
            traceback.print_exc()
            return []

        finally:
            driver.quit()

    def _extract_shortcode(self, url: str) -> str:
        m = re.search(r"/(?:p|reel)/([^/?]+)", url)
        if not m:
            raise ValueError("Shortcode topilmadi")
        return m.group(1)

    async def instagram_post_gettre(self, post_url: str) -> Optional[List]:

        try:
            shortcode = await asyncio.to_thread(self._extract_shortcode, post_url)

            for attempt in range(self.max_retries):
                try:
                    post = await asyncio.wait_for(
                        asyncio.to_thread(
                            instaloader.Post.from_shortcode,
                            self.loader.context,
                            shortcode
                        ),
                        timeout=self.timeout
                    )

                    sidecar_nodes_generator = await asyncio.wait_for(
                        asyncio.to_thread(post.get_sidecar_nodes),
                        timeout=self.timeout
                    )

                    if sidecar_nodes_generator is None:
                        print(f"⚠️ No nodes returned (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            await asyncio.sleep(wait_time)
                        continue

                    try:
                        sidecar_nodes = list(sidecar_nodes_generator)
                    except Exception as e:
                        print(f"ERROR: {e}")
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
            print(f"ERROR: {e}")
            return None
        except Exception as e:
            print(f"ERROR: {e}")
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
                        print(f"ERROR: {e}")
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
                        print(f"ERROR: {e}")
                    except Exception as e:
                        print(f"ERROR: {e}")

                except Exception as e:
                    print(f"ERROR: {e}")
                    continue

            if not medias:
                errors.append(DownloadError.DOWNLOAD_ERROR)
                return None, errors

            print(f"✅ Post download completed: {len(medias)} items")
            return medias, errors

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors

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
                return None, errors

            file_size = await asyncio.to_thread(os.path.getsize, photo_path)
            file_size_mb = file_size / (1024 ** 2)

            if file_size_mb > 2000 * 1024 * 1024:
                errors.append(DownloadError.FILE_TOO_BIG)
            return photo_path, errors

        except asyncio.TimeoutError:
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(DownloadError.DOWNLOAD_ERROR)
            return None, errors
