import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from yt_dlp import YoutubeDL

from src.app.services.media_downloaders.utils.files import get_video_file_name, get_photo_file_name
from src.app.utils.enums.error import DownloadError

logger = logging.getLogger(__name__)


class InstagramDownloader:

    def __init__(self):
        self.timeout = 120
        self.download_path = Path("media")
        self.selenium_url = os.getenv('SELENIUM_REMOTE_URL', 'http://selenium:4444')

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

            if file_size > 2000 * 1024 * 1024:
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
        """Chrome driverini sozlash - REMOTE Selenium Grid bilan"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # REMOTE Selenium Grid ga ulanish
        try:
            driver = webdriver.Remote(
                command_executor=self.selenium_url,
                options=chrome_options
            )
            print(f"✅ Remote Selenium ga ulandi: {self.selenium_url}")
            return driver
        except Exception as e:
            print(f"❌ Remote Selenium ga ulanishda xato: {e}")
            raise

    def get_downloaded_urls(self, instagram_url):
        """Instagram URL larini olish"""
        driver = None
        urls = []

        try:
            print("🌐 Selenium Grid ga ulanish...")
            driver = self.setup_driver()

            print("🌐 Sayt ochilmoqda...")
            driver.get("https://sssinstagram.com/ru")

            # Sahifa to'liq yuklanishini kutish

            print("📝 URL kiritilmoqda...")

            # JavaScript orqali input topish va yozish (eng ishonchli)
            wait = WebDriverWait(driver, 10)

            # Input field ni kutish
            input_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.form__input"))
            )

            # JavaScript orqali to'g'ridan-to'g'ri yozish
            driver.execute_script(f"""
                var input = document.querySelector('input.form__input');
                if (input) {{
                    input.value = '{instagram_url}';
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            """)

            print("✅ URL kiritildi")
            time.sleep(1)

            print("🔽 Yuklash tugmasini bosish...")

            # Submit button ni topish va bosish
            download_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.form__submit"))
            )

            # JavaScript orqali click
            driver.execute_script("arguments[0].click();", download_button)
            print("✅ Tugma bosildi")

            time.sleep(5)

            print("⏳ Media yuklanishi kutilmoqda...")
            previous_count = 0
            no_change_count = 0

            for i in range(0, 60, 2):
                try:
                    download_buttons = driver.find_elements(By.CLASS_NAME, "button__download")
                    current_count = len(download_buttons)

                    if current_count > previous_count:
                        print(f"   📥 {current_count} ta media topildi...")
                        previous_count = current_count
                        no_change_count = 0
                    elif current_count > 0:
                        no_change_count += 1

                    if no_change_count >= 3 and current_count > 0:
                        break

                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)

                except Exception as e:
                    print(f"ERROR: {e}")
                    break

            download_buttons = driver.find_elements(By.CLASS_NAME, "button__download")

            for btn in download_buttons:
                href = btn.get_attribute("href")
                if href:
                    urls.append(href)

            print(f"✅ Jami {len(urls)} ta URL topildi")
            return urls

        except TimeoutException as e:
            print(f"❌ Timeout: {e}")
            # Screenshot olish (debug uchun)
            if driver:
                try:
                    driver.save_screenshot("/usr/src/app/tg_bot/media/error_screenshot.png")
                    print("📸 Screenshot saqlandi")
                except:
                    pass
            return []
        except NoSuchElementException as e:
            print(f"❌ Element topilmadi: {e}")
            return []
        except Exception as e:
            print(f"❌ Xato: {e}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            if driver:
                driver.quit()
                print("\n🔒 Brauzer yopildi")

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