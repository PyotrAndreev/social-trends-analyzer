import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from source.utils.states import UserState

import source.keyboards.inline as ikb
import source.keyboards.shared as skb

def load_messages_and_buttons(language: str):
    with open(f"/Users//Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

MESSAGES = load_messages_and_buttons("ru")["messages"]
BUTTONS = load_messages_and_buttons("ru")["buttons"]

router = Router()

@router.callback_query(F.data == "get_report")
async def get_report_command(callback_query: CallbackQuery, state: FSMContext):
    await skb.push_state_stack(state, UserState.report_menu, callback_query.message.message_id)
    await state.set_state(UserState.report_menu)
    await callback_query.message.edit_text(MESSAGES["report_menu"], reply_markup=skb.back_kb)

@router.callback_query(F.data == "account")
async def account_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.account_menu)
    await callback_query.message.edit_text(MESSAGES["account_menu"], reply_markup=ikb.account_menu)

@router.callback_query(F.data == "get_support")
async def get_support_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.support_menu)
    await callback_query.message.edit_text(MESSAGES["support_menu"])

@router.callback_query(F.data == "confirm_yes")
async def confirm_yes(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link", None)

    if link:
        await callback_query.message.answer(MESSAGES["link_confirmed"])
        #request

    await state.clear()

@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(MESSAGES["link_not_confirmed"])
    await state.set_state(UserState.link)

@router.callback_query(F.data == "go_back")
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    if await state.get_state() == UserState.report_menu:
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
        await state.set_state(UserState.main_menu)

    elif await state.get_state() == UserState.account_menu:
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
        await state.set_state(UserState.main_menu)

    elif await state.get_state() == UserState.support_menu:
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
        await state.set_state(UserState.main_menu)



# @router.callback_query(F.data == "go_back")
# async def go_back(callback_query: CallbackQuery, state: FSMContext):
#     previous_state_data = await skb.pop_state_stack(state)
#
#     if previous_state_data:
#         previous_state = previous_state_data["state"]
#         message_id = previous_state_data["message_id"]
#         extra_data = previous_state_data["extra_data"]
#
#         if previous_state == UserState.report_menu:
#             await callback_query.message.edit_text(MESSAGES["previous_message"], reply_markup=None)
#
#         await state.set_state(previous_state)
#
#         await callback_query.message.edit_reply_markup(reply_markup=None)
#     else:
#         await callback_query.message.edit_text(MESSAGES["default_message"], reply_markup=None)


