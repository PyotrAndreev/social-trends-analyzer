import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def load_messages_and_buttons(language: str):
    try:
        with open(f"/Users//Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file for language '{language}' was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file for language '{language}' contains invalid JSON.")
        return {}

data = load_messages_and_buttons("ru")

MESSAGES = data.get("messages", {})
BUTTONS = data.get("buttons", {})

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS.get("report_button", "Report"), callback_data="get_report")
        ],
        [
            InlineKeyboardButton(text=BUTTONS.get("account_button", "Account"), callback_data="account"),
            InlineKeyboardButton(text=BUTTONS.get("support_button", "Support"), callback_data="get_support")
        ]
    ]
)

# Клавиатура для подтверждения
confirm_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS.get("YES", "Yes"), callback_data="confirm_yes")],
        [InlineKeyboardButton(text=BUTTONS.get("NO", "No"), callback_data="confirm_no")]
    ]
)

account_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTONS.get("manage_subscription", "Manage Subscription"), callback_data="manage_subscription")
        ],
        [
            InlineKeyboardButton(text=BUTTONS.get("operations", "Operations"), callback_data="operations"),
            InlineKeyboardButton(text=BUTTONS.get("top_up_balance", "Top Up Balance"), callback_data="top_up_balance")
        ],
        [
            InlineKeyboardButton(text=BUTTONS.get("report_history", "Report History"), callback_data="report_history")
        ],
        [
            InlineKeyboardButton(text=BUTTONS.get("user_agreement", "User Agreement"), callback_data="user_agreement")
        ],
        [
            InlineKeyboardButton(text=BUTTONS.get("back_button", "Back"), callback_data="go_back")
        ]
    ]
)