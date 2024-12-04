import json
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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

BUTTONS = load_messages_and_buttons("ru").get("buttons", {})

if BUTTONS:
    registration_button = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS.get("registration_button", "Register"))]
        ],
        resize_keyboard=True
    )

    edit_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS.get("edit_name", "Edit Name")), KeyboardButton(text=BUTTONS.get("edit_age", "Edit Age"))],
            [KeyboardButton(text=BUTTONS.get("edit_email", "Edit Email")), KeyboardButton(text=BUTTONS.get("edit_phone", "Edit Phone"))]
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

