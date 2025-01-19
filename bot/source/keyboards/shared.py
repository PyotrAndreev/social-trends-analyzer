from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.source.utils.templates import BUTTONS

back_button = InlineKeyboardButton(text=BUTTONS["back_button"], callback_data="go_back")

back_kb = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
