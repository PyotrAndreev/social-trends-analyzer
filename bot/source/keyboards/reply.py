from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.source.utils.templates import BUTTONS

if BUTTONS:
    registration_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS.get("registration_button", "Register"))]
        ],
        resize_keyboard=True
    )

    edit_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS.get("edit_name", "Edit Name")),
             KeyboardButton(text=BUTTONS.get("edit_age", "Edit Age"))],
            [KeyboardButton(text=BUTTONS.get("edit_email", "Edit Email")),
             KeyboardButton(text=BUTTONS.get("edit_phone", "Edit Phone"))]
        ],
        resize_keyboard=True
    )

    menu_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS.get("menu_button", "Menu"))]
        ],
        resize_keyboard=True
    )
else:
    print("Error: Buttons not loaded.")
