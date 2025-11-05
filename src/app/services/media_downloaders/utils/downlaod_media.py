import aiofiles
from aiogram.client.session import aiohttp

from src.app.utils.enums.general import MediaType


async def download_media_in_internet(url: str, file_name: str, media_type: MediaType) -> str | None:
    save_path = None
    if media_type == MediaType.VIDEO:
        save_path = f"./media/videos/{file_name}"
    elif media_type == MediaType.PHOTO:
        save_path = f"./media/photos/{file_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(await response.read())
                return save_path