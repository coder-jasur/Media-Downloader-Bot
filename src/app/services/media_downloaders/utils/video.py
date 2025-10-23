import aiofiles
from aiogram.client.session import aiohttp


async def download_media_in_internet(url: str, file_name: str, media_type: str) -> str | None:
    save_path = None
    if media_type == "video":
        save_path = f"./media/videos/{file_name}"
    elif media_type == "photo":
        save_path = f"./media/photos/{file_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(await response.read())
                return save_path