async def _show_subscriptions_menu_message(message, pool, lang):
    """Message orqali subscription menyu ko'rsatish"""
    _ = get_translator(lang).gettext
    from src.app.database.queries.channels import ChannelDataBaseActions
    from src.app.database.queries.bots import BotDataBaseActions

    channels = await ChannelDataBaseActions(pool).get_all_channels()
    bots = await BotDataBaseActions(pool).get_all_bots()

    await message.answer(
        _("Mandatory subscriptions menu title"),
        reply_markup=create_mandatory_subs_keyboard(channels, bots, lang)
    )


async def _show_referrals_menu_message(message, pool, lang):
    """Message orqali referrals menyu ko'rsatish"""
    _ = get_translator(lang).gettext
    from src.app.database.queries.referals import ReferalDataBaseActions

    referrals = await ReferalDataBaseActions(pool).get_all_referals()

    await message.answer(
        _("Referals menu title") if referrals else _("Empty referals menu title"),
        reply_markup=referals_menu_kbd(referrals, lang)
    )