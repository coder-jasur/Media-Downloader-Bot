from aiogram import Dispatcher, Router

from src.app.core.config import Settings
from src.app.handlers.admin import register_admin_routers
from src.app.handlers.chek_sub import check_sub_router
from src.app.handlers.chek_sub_subscription import check_channel_sub_router
from src.app.handlers.start import start_router
from src.app.handlers.user.commands import user_commands_router
from src.app.handlers.user.language_selection import language_selection_router
from src.app.handlers.user.media_downloader import media_downloader_router


def register_all_router(dp: Dispatcher, settings: Settings):
    main_router = Router()
    register_admin_routers(main_router, settings)
    main_router.include_router(check_sub_router)
    main_router.include_router(check_channel_sub_router)
    main_router.include_router(start_router)
    main_router.include_router(language_selection_router)
    main_router.include_router(user_commands_router)
    main_router.include_router(media_downloader_router)


    dp.include_router(main_router)