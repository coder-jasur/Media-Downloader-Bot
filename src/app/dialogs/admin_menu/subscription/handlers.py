from aiogram_dialog import DialogManager

from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionChannelMenuSG


async def on_click_set_up_channel(_, __, dialog_manager: DialogManager, chanenl_id: str):
    await dialog_manager.start(MandatorySubscriptionChannelMenuSG.channel_menu, data=chanenl_id)