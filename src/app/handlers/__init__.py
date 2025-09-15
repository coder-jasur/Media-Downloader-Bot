from aiogram import Dispatcher, Router

from src.app.core.config import Settings
from src.app.handlers.admin import register_admin_routers
from src.app.handlers.start import start_router
from src.app.handlers.user.media_downloader import media_downloader_router


def register_all_router(dp: Dispatcher, settings: Settings):
    main_router = Router()
    register_admin_routers(main_router, settings)
    main_router.include_router(start_router)
    main_router.include_router(media_downloader_router)


    dp.include_router(main_router)