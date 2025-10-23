import aiofiles
import aiohttp

from src.app.services.media_downloaders.utils.files import get_video_file_name


class TikTokDownloaders:
    def __init__(self):
        self.aiohttp = aiohttp


    async def tiktok_video_downloader(self, video_url: str):
        file_name = get_video_file_name()

        api_url = f"https://tiktok-dl.akalankanime11.workers.dev/?url={video_url}"

        video_output_path = f"./media/videos/{file_name}"
        try:

            async with self.aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status != 200:
                        print(f"ERROR: {resp.status}")
                        return
                    data = await resp.json()

            error = []

            video_download_url = data.get("non_watermarked_url")

            file_size = int(data.get("file_size")) / 1024 * 1024

            if not video_download_url:
                error.append("error_in_downloading")
                return video_download_url, error

            if file_size and file_size > 2000:
                error.append("video_file_is_so_big")

            async with self.aiohttp.ClientSession() as session:
                async with session.get(video_download_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(video_output_path, "wb") as f:
                            await f.write(await response.read())

            return video_output_path, error
        except Exception as e:
            print("ERROR", e)
