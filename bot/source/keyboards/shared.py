import json

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def load_messages_and_buttons(language: str):
    with open(f"/Users/savelyev90/Desktop/my_project/bot/source/messages/{language}.json", "r", encoding="utf-8") as file:
        return json.load(file)

BUTTONS = load_messages_and_buttons("ru")["buttons"]
MESSAGES = load_messages_and_buttons("ru")["messages"]

back_button = InlineKeyboardButton(text=BUTTONS["back_button"], callback_data="go_back")

back_kb = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

async def push_state_stack(state: FSMContext, current_state: str, message_id: int, extra_data: dict = None):
    state_stack = await state.get_data()
    state_stack = state_stack.get("state_stack", [])

    state_stack.append({
        "state": current_state,
        "message_id": message_id,
        "extra_data": extra_data or {}
    })

    await state.update_data(state_stack=state_stack)

async def pop_state_stack(state: FSMContext):
    state_stack = await state.get_data()
    state_stack = state_stack.get("state_stack", [])

    if state_stack:
        return state_stack.pop()
    return None