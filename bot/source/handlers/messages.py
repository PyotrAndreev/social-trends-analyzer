import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.keyboards.reply import main_menu
from source.utils.states import UserState

def load_messages_and_buttons(language: str):
    with open(f"/Users/savelyev90/Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

MESSAGES = load_messages_and_buttons("ru")["messages"]
BUTTONS = load_messages_and_buttons("ru")["buttons"]

router = Router()



