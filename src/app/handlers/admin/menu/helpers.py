from src.app.database.queries.bots import BotDataBaseActions
from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.database.queries.referals import ReferalDataBaseActions
from src.app.keyboards.inline import create_mandatory_subs_keyboard, referals_menu_kbd
from src.app.utils.i18n import get_translator


async def _show_subscriptions_menu_message(message, pool, lang):
    """Message orqali subscription menyu ko'rsatish"""
    _ = get_translator(lang).gettext

    channels = await ChannelDataBaseActions(pool).get_all_channels()
    bots = await BotDataBaseActions(pool).get_all_bots()

    await message.answer(
        _("Mandatory subscriptions menu title"),
        reply_markup=create_mandatory_subs_keyboard(channels, bots, lang)
    )


async def _show_referrals_menu_message(message, pool, lang):
    """Message orqali referrals menyu ko'rsatish"""
    _ = get_translator(lang).gettext

    referrals = await ReferalDataBaseActions(pool).get_all_referals()

    await message.answer(
        _("Referals menu title") if referrals else _("Empty referals menu title"),
        reply_markup=referals_menu_kbd(referrals, lang)
    )