from aiogram import Router

from src.app.dialogs.admin_menu.main_menu.dialog import admin_menu_dialog
from src.app.dialogs.admin_menu.subscription.channels.add_channel.dialog import add_channel_dialog
from src.app.dialogs.admin_menu.subscription.channels.set_up_channel.dialog import channel_set_up_menu
from src.app.dialogs.admin_menu.subscription.dialog import mandatory_subscriptions_dialog


def register_admin_dialogs(main_router: Router):
    main_router.include_router(admin_menu_dialog)
    main_router.include_router(mandatory_subscriptions_dialog)
    main_router.include_router(add_channel_dialog)
    main_router.include_router(channel_set_up_menu)

