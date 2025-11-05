from typing import List, Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.app.keyboards.callback_data import MusicCD, SearchMusicInVideoCD, AudioCD, MediaEffectsCD, AdminMainMenuCD, \
    ChannelCD, BotCD, AddMandatorySubscriptionCD, ReferralCD, TopPopularMusicCD
from src.app.utils.enums.actions import AdminMenuActions, ChannelActions, BotActions, AddMandatorySubscriptionActions, \
    ReferalsActions
from src.app.utils.enums.general import GeneralEffectAction
from src.app.utils.i18n import get_translator


def video_keyboards(lang: str):
    _ = get_translator(lang).gettext

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Download Music"),
            callback_data=SearchMusicInVideoCD(
                action="search_music",
            ).pack()
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="🔊 mp3",
            callback_data=AudioCD(
                action="download_audio"
            ).pack()
        )
    )
    return keyboard_builder.as_markup()


def music_keyboards(music_list: list):
    keyboard_builder = InlineKeyboardBuilder()
    i = 1

    for music in music_list:
        keyboard_builder.add(
            InlineKeyboardButton(
                text=str(i),
                callback_data=MusicCD(video_id=music["id"]).pack()
            )
        )
        i += 1

    keyboard_builder.adjust(5)

    keyboard_builder.row(
        InlineKeyboardButton(
            text="❌",
            callback_data="delete_list_music"
        )
    )

    return keyboard_builder.as_markup()


def songs_keyboard(tracks: List[Dict[str, str]], page: int = 1) -> InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]] = []

    start = (page - 1) * 10
    end = start + 10
    sliced = tracks[start:end]
    for i, t in enumerate(sliced, start=start):
        label = f"{i + 1}. {t.get('artist', 'Unknown')} — {t.get('title', 'Unknown')}"
        if len(label) > 64:
            label = label[:61] + "..."
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=TopPopularMusicCD(
                        music_name=label[:40]
                    ).pack()
                )
            ]
        )

    total = len(tracks)
    total_pages = (total + 10 - 1) // 10 if total else 1
    nav_buttons: List[InlineKeyboardButton] = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page:{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page:{page + 1}"))
    if nav_buttons:
        inline_keyboard.append(nav_buttons)

    # close
    inline_keyboard.append([InlineKeyboardButton(text="❌", callback_data="close")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def audio_keyboard(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(InlineKeyboardButton(text=_("effektlar"), callback_data="effects"))
    return keyboard_builder.as_markup()


def auido_effect_kbd(actions: str, lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Konsert"),
            callback_data=MediaEffectsCD(
                actions=actions,
                effect=GeneralEffectAction.EFFECT_CONCERT_HALL
            ).pack()
        ),
        InlineKeyboardButton(
            text=_("8D"),
            callback_data=MediaEffectsCD(
                actions=actions,
                effect=GeneralEffectAction.EFFECT_8D
            ).pack()
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Slowed"),
            callback_data=MediaEffectsCD(
                actions=actions,
                effect=GeneralEffectAction.EFFECT_SLOWED
            ).pack()
        ),
        InlineKeyboardButton(
            text=_("Speed"),
            callback_data=MediaEffectsCD(
                actions=actions,
                effect=GeneralEffectAction.EFFECT_SPEED
            ).pack()
        )
    )
    return keyboard_builder.as_markup()


def admin_main_menu(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Mandatory subscription"),
            callback_data=AdminMainMenuCD(
                actions=AdminMenuActions.MANDATORY_SUBSCRIPTIONS_MENU
            ).pack()
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Referals"),
            callback_data=AdminMainMenuCD(
                actions=AdminMenuActions.REFERALS_MENU
            ).pack()
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Statistics"),
            callback_data=AdminMainMenuCD(
                actions=AdminMenuActions.STATISTICS_MENU
            ).pack()
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Broadcast"),
            callback_data="boroadcasting"
        )
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text=_("Quit from admin menu"),
            callback_data="quit_from_admin_menu"
        )
    )
    return keyboard_builder.as_markup()


def create_mandatory_subs_keyboard(channels: list, bots: list, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    buttons = []

    if channels:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=_("Channels start border"),
                    callback_data="some_data"
                )
            ]
        )
        for channel in channels:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=channel[1],
                        callback_data=ChannelCD(
                            id=channel[0], action=ChannelActions.CHANNEL_SET_UP_MENU
                        ).pack(),
                    )
                ]
            )

    if bots:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=_("Bots start border"),
                    callback_data="some_data"
                )
            ]
        )
        for bot in bots:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=bot[0],
                        callback_data=BotCD(
                            username=bot[1],
                            action=BotActions.BOT_SET_UP_MENU
                        ).pack(),
                    )
                ]
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text=_("Add channel"),
                callback_data=AddMandatorySubscriptionCD(
                    actions=AddMandatorySubscriptionActions.ADD_CHANNEL
                ).pack()
            ),
            InlineKeyboardButton(
                text=_("Add bot"),
                callback_data=AddMandatorySubscriptionCD(
                    actions=AddMandatorySubscriptionActions.ADD_BOT
                ).pack()
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(text=_("Back to admin menu"), callback_data="back_to_admin_menu")
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def referals_menu_kbd(referals: list, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    buttons = []

    for referal in referals:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=referal[1] + " - " + str(referal[2]),
                    callback_data=ReferralCD(
                        referral_id=referal[0], action=ReferalsActions.REFERALS_SET_UP_MENU
                    ).pack(),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=_("Add referal"),
                callback_data=ReferralCD(
                    referral_id="some_id",
                    action=ReferalsActions.ADD_REFERALS
                ).pack()
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=_("Back to admin menu"),
                callback_data="back_to_admin_menu"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def modified_channel_menu(channel_id: int, is_mandatory: bool, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    if is_mandatory:
        remove_for_op = InlineKeyboardButton(
            text=_("Delete in mandatory sub"),
            callback_data=ChannelCD(
                id=channel_id, action=ChannelActions.DELETE_IN_MANDATORY_SUB
            ).pack(),
        )
    else:
        remove_for_op = InlineKeyboardButton(
            text=_("Add in mandatry sub"),
            callback_data=ChannelCD(
                id=channel_id, action=ChannelActions.ADD_IN_MANDATORY_SUB
            ).pack(),
        )

    delete_channel = InlineKeyboardButton(
        text=_("Delete channel"),
        callback_data=ChannelCD(
            id=channel_id, action=ChannelActions.DELETE_CHANNEL
        ).pack(),
    )
    back = InlineKeyboardButton(
        text=_("Back"),
        callback_data="back_to_menu",
    )
    keyboard_builder.row(delete_channel, remove_for_op)
    keyboard_builder.row(back)

    return keyboard_builder.as_markup()


def modified_bot_menu(is_op: bool, username: str, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    if is_op:
        remove_for_op = InlineKeyboardButton(
            text=_("Delete in mandatory sub"),
            callback_data=BotCD(
                username=username,
                action=BotActions.DELETE_IN_MANDATORY_SUB
            ).pack(),
        )
    else:
        remove_for_op = InlineKeyboardButton(
            text=_("Add in mandatory sub"),
            callback_data=BotCD(
                username=username,
                action=BotActions.ADD_IN_MANDATORY_SUB
            ).pack(),
        )

    delete_channel = InlineKeyboardButton(
        text=_("Delete bot"),
        callback_data=BotCD(username=username, action=BotActions.DELETE_BOT).pack(),
    )
    back = InlineKeyboardButton(
        text=_("Back"),
        callback_data="back_to_menu",
    )
    keyboard_builder.row(remove_for_op, delete_channel)
    keyboard_builder.row(back)

    return keyboard_builder.as_markup()


def delite_channel_menu(channel_id: int, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    sure = InlineKeyboardButton(
        text=_("Delete"),
        callback_data=ChannelCD(
            id=channel_id, action=ChannelActions.SURE_DELETE
        ).pack(),
    )
    not_sure = InlineKeyboardButton(
        text=_("Not delete"),
        callback_data=ChannelCD(
            id=channel_id, action=ChannelActions.NOT_SURE_DELETE
        ).pack(),
    )

    keyboard_builder.row(sure, not_sure)

    return keyboard_builder.as_markup()


def delite_referral_menu(referral_id: str, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    inline_keyboard = InlineKeyboardBuilder()

    sure = InlineKeyboardButton(
        text=_("Delete"),
        callback_data=ReferralCD(referral_id=referral_id, action=ReferalsActions.SURE_DELETE).pack(),
    )
    not_sure = InlineKeyboardButton(
        text=_("Not delete"),
        callback_data=ReferralCD(referral_id=referral_id, action=ReferalsActions.NOT_SURE_DELETE).pack(),
    )

    inline_keyboard.row(sure, not_sure)
    return inline_keyboard.as_markup()


def menu_referrals_kb(refferal_id: str, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    inline_keyboard = InlineKeyboardBuilder()

    delite = InlineKeyboardButton(
        text=_("Delete"),
        callback_data=ReferralCD(
            referral_id=refferal_id, action=ReferalsActions.DELETE_REFERAL
        ).pack(),
    )

    back = InlineKeyboardButton(text=_("back"), callback_data="back_to_menu_referrals")

    inline_keyboard.row(delite)
    inline_keyboard.row(back)

    return inline_keyboard.as_markup()


def delite_bot_menu(username: str, lang: str) -> InlineKeyboardMarkup:
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()

    sure = InlineKeyboardButton(
        text=_("Delete"),
        callback_data=BotCD(
            username=username,
            action=BotActions.SURE_DELETE
        ).pack(),
    )
    not_sure = InlineKeyboardButton(
        text=_("Not delete"),
        callback_data=BotCD(
            username=username,
            action=BotActions.NOT_SURE_DELETE
        ).pack(),
    )

    keyboard_builder.row(sure, not_sure)

    return keyboard_builder.as_markup()


def back_to_channel_menu(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(text=_("Back"), callback_data="back_to_admin_menu"))
    return keyboard_builder.as_markup()


def back_to_subscription_menu(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(
            text=_("Back to subscriptions menu"),
            callback_data="back_to_subscriptions_menu"
        )
    )
    return keyboard_builder.as_markup()


def add_chanel_url_defult(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(
            text=_("Defult Channel Url"),
            callback_data=AddMandatorySubscriptionCD(
                actions=AddMandatorySubscriptionActions.ADD_CHANNEL_URL_DEFULT
            ).pack()
        )
    )
    return keyboard_builder.as_markup()


def add_bot_url_defult(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(
            text=_("Defult Bot Url"),
            callback_data=AddMandatorySubscriptionCD(
                actions=AddMandatorySubscriptionActions.ADD_BOT_URL_DEFULT
            ).pack()
        )
    )
    return keyboard_builder.as_markup()


def back_to_admin_menu_keyboards(lang: str):
    _ = get_translator(lang).gettext
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(
            text=_("Back to admin menu"),
            callback_data="back_to_admin_menu"
        )
    )
    return keyboard_builder.as_markup()

def not_channels_button(channel_data):
    builder_button = InlineKeyboardBuilder()
    for channel in channel_data:

        builder_button.row(
            InlineKeyboardButton(text=channel[1], url=channel[5])
        )

    builder_button.row(InlineKeyboardButton(text="✅", callback_data="check_sub"))
    return builder_button.as_markup()
