from enum import Enum


class AdminMenuActions(Enum):
    MANDATORY_SUBSCRIPTIONS_MENU = "mandatory_subscriptions_menu"
    REFERALS_MENU = "referals_menu"
    STATISTICS_MENU = "statistics_menu"
    BROADCAST_MENU = "broadcast_menu"
    ADMIN_MANAGMENT_MENU = "admin_managment_menu"


class ChannelActions(Enum):
    CHANNEL_SET_UP_MENU = "channel_set_up_menu"
    DELETE_CHANNEL = "delete_channel"
    ADD_IN_MANDATORY_SUB = "add_in_mandatory_sub"
    DELETE_IN_MANDATORY_SUB = "delete_in_mandatory_sub"
    SURE_DELETE = "sure_delete"
    NOT_SURE_DELETE = "not_sure_delete"



class BotActions(Enum):
    BOT_SET_UP_MENU = "bot_set_up_menu"
    DELETE_BOT = "delete_bot"
    ADD_IN_MANDATORY_SUB = "add_in_mandatory_sub"
    DELETE_IN_MANDATORY_SUB = "delete_in_mandatory_sub"
    SURE_DELETE = "sure_delete"
    NOT_SURE_DELETE = "not_sure_delete"

class ReferalsActions(Enum):
    REFERALS_SET_UP_MENU = "referals_set_up_menu"
    ADD_REFERALS = "add_referals"
    DELETE_REFERAL = "delete_referal"
    SURE_DELETE = "sure_delete"
    NOT_SURE_DELETE = "not_sure_delete"


class AddMandatorySubscriptionActions(Enum):
    ADD_CHANNEL = "add_channel"
    ADD_CHANNEL_URL_DEFULT = "add_channel_url_defult"
    ADD_BOT = "add_bot"
    ADD_BOT_URL_DEFULT = "add_bot_url_defult"

