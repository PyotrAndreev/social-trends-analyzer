import json
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import source.keyboards.reply as rkb
import source.keyboards.inline as ikb
import source.keyboards.shared as skb

from source.utils.states import UserState

router = Router()

def load_messages_and_buttons(language: str):
    with open(f"/Users//Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

BUTTONS = load_messages_and_buttons("ru")["buttons"]
MESSAGES = load_messages_and_buttons("ru")["messages"]

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await state.set_state(UserState.start)
    await message.answer(MESSAGES["start"], reply_markup=rkb.registration_button)

@router.message(Command("menu"))
async def menu_command(message: Message, state: FSMContext):
    await state.set_state(UserState.main_menu)
    await message.answer(MESSAGES["main_menu"], reply_markup=ikb.main_menu)

@router.message(Command("report"))
async def report_command(state: FSMContext, message: Message):
    await state.set_state(UserState.report_menu)
    await message.answer(MESSAGES["report_menu"], reply_markup=skb.back_kb)

@router.message(Command("account"))
async def account_command(state: FSMContext, message: Message):
    await state.set_state(UserState.account_menu)
    await message.answer(MESSAGES["account_menu"], reply_markup=ikb.account_menu)
#
# @router.message(Command("subscription"))
# async def subscription_command(state: FSMContext, message: Message):
#     await state.set_state(UserState.subscription_menu)
#     await message.answer(MESSAGES["subscription_menu"], reply_markup=)
#
# @router.message(Command("balance"))
# async def balance_command(state: FSMContext, message: Message):
#     await state.set_state(UserState.balance_menu)
#     await message.answer(MESSAGES["balance_menu"], reply_markup=)
#
# @router.message(Command("help"))
# async def help_command(state: FSMContext, message: Message):
#     await state.set_state(UserState.support_menu)
#     await message.answer(MESSAGES["support_menu"], reply_markup=)
