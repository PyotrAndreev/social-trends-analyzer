import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import bot.source.keyboards.inline as ikb
from bot.source.utils.states import UserState
from bot.source.utils.templates import BUTTONS, MESSAGES


router = Router()


@router.message(F.text == BUTTONS["menu_button"])
async def main_menu_command(message: Message, state: FSMContext):
    await state.set_state(UserState.main_menu)
    await message.answer(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
