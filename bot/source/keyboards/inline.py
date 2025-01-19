from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import bot.source.keyboards.shared as skb

from bot.source.utils.templates import BUTTONS

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS["cloud_button"], callback_data="get_cloud"),
            InlineKeyboardButton(text=BUTTONS["spy_button"], callback_data="get_spy")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["account_button"], callback_data="account"),
            InlineKeyboardButton(text=BUTTONS["support_button"], callback_data="get_support")
        ]
    ]
)

spy_service_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS["analyze_ad"], callback_data="analyze_youtube_channel")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["search_ad"], callback_data="search_company_advertising")
        ],
        [
            skb.back_button
        ]
    ]
)

confirm_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS["YES"], callback_data="confirm_yes")],
        [InlineKeyboardButton(text=BUTTONS["NO"], callback_data="confirm_no")]
    ]
)

account_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS["manage_subscription"], callback_data="manage_subscription")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["operations"], callback_data="operations"),
            InlineKeyboardButton(text=BUTTONS["top_up_balance"], callback_data="top_up_balance")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["report_history"], callback_data="report_history")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["user_agreement"], callback_data="user_agreement")
        ],
        [
            InlineKeyboardButton(text=BUTTONS["back_button"], callback_data="go_back")
        ]
    ]
)
