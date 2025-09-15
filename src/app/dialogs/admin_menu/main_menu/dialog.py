from aiogram_dialog import Window, StartMode, Dialog
from aiogram_dialog.widgets.kbd import Group, Button, Start
from aiogram_dialog.widgets.text import Format

from src.app.dialogs.admin_menu.main_menu.getters import admin_menu_text_getter
from src.app.states.admin.admin import AdminSG
from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionsSG

admin_menu_dialog = Dialog(
    Window(
        Format("{title}"),
        Group(
            Start(
                Format("{mandatory_subscriptions_menu}"),
                id="set_up_bot",
                state=MandatorySubscriptionsSG.menu,
                mode=StartMode.RESET_STACK
            ),
            Button(Format("{referrals}"), id="referrals"),
            Button(Format("{statistics}"), id="statistics"),
            Button(Format("{broadcast}"), id="broadcast"),
            Button(Format("{user_management}"), id="user_management"),
            Button(Format("{admins_management}"), id="admins_management"),
            Button(Format("{quit}"), id="quit"),
            width=1,
        ),
        getter=admin_menu_text_getter,
        state=AdminSG.menu,
    )
)
