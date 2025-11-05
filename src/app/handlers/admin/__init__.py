from aiogram import Router, F

from src.app.core.config import Settings
from src.app.handlers.admin.menu.bot import bots_router
from src.app.handlers.admin.menu.broadcasting import broadcaster_router
from src.app.handlers.admin.menu.channel import channels_router
from src.app.handlers.admin.commands import admin_commands_router
from src.app.handlers.admin.menu.menu import admin_menu_router
from src.app.handlers.admin.menu.referal import referrals_router


def register_admin_routers(router: Router, settings: Settings):
    admins_id = []
    for admin in settings.admins_ids:
        admins_id.append(int(admin))
    admin_register_router = Router()
    admin_register_router.message.filter(F.from_user.id.in_(admins_id))
    admin_register_router.callback_query.filter(F.from_user.id.in_(admins_id))

    admin_register_router.include_router(admin_commands_router)
    admin_register_router.include_router(broadcaster_router)
    admin_register_router.include_router(admin_menu_router)
    admin_register_router.include_router(channels_router)
    admin_register_router.include_router(bots_router)
    admin_register_router.include_router(referrals_router)
    router.include_router(admin_register_router)