import re
import json
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import source.keyboards.reply as rkb
import source.keyboards.inline as ikb
import source.keyboards.shared as skb
from source.utils.states import UserState

def load_messages_and_buttons(language: str):
    with open(f"/Users//Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

MESSAGES = load_messages_and_buttons("ru")["messages"]
BUTTONS = load_messages_and_buttons("ru")["buttons"]

router = Router()

def is_valid_youtube_url(url: str) -> bool:
    youtube_regex = r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=[\w-]+|embed/[\w-]+|shorts/[\w-]+|[^?&]*$)"
    return re.match(youtube_regex, url) is not None


@router.message(UserState.main_menu)
async def main_menu_command(message: Message, state: FSMContext):
    await message.answer(MESSAGES["main_menu"], reply_markup=ikb.main_menu)

@router.message(UserState.report_menu)
async def report_menu_command(message: Message, state: FSMContext):
    await message.answer(MESSAGES["report_menu"], reply_markup=skb.back_kb)
    await state.set_state(UserState.link)

@router.message(UserState.link)
async def link_command(message: Message, state: FSMContext):
    url = message.text.strip()
    if not is_valid_youtube_url(url):
        await message.answer(MESSAGES["invalid_link"])
        return
    await state.update_data(link=url)
    await message.reply(MESSAGES["link_saved"], reply_markup=ikb.confirm_buttons)

@router.message(UserState.account_menu)
async def account_menu_command(message: Message, state: FSMContext):
    await message.answer(MESSAGES["account_menu"], reply_markup=ikb.account_menu)

