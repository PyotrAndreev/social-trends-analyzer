from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.source.utils.states import UserState

import bot.source.keyboards.inline as ikb
import bot.source.keyboards.shared as skb

from bot.source.utils.templates import MESSAGES

router = Router()


@router.callback_query(F.data == "get_spy")
async def get_spy_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.spy_service_menu)
    await callback_query.message.edit_text(MESSAGES["spy_service"], reply_markup=ikb.spy_service_keyboard)


@router.callback_query(F.data == "analyze_youtube_channel")
async def analyze_youtube_channel(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.analyze_youtube_channel)
    await callback_query.message.edit_text(MESSAGES["analyze_youtube_channel"], reply_markup=skb.back_kb)


@router.callback_query(F.data == "search_company_advertising")
async def search_company_advertising(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.search_company_advertising)
    await callback_query.message.edit_text(MESSAGES["search_company_advertising"], reply_markup=skb.back_kb)


@router.callback_query(F.data == "get_cloud")
async def get_cloud_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.cloud_menu)
    await callback_query.message.edit_text(MESSAGES["cloud_of_meanings"], reply_markup=skb.back_kb)


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
        # request

    await state.clear()


@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(MESSAGES["link_not_confirmed"])
    await state.set_state(UserState.link)


@router.callback_query(F.data == "go_back")
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    if await state.get_state() == UserState.cloud_menu:
        await state.set_state(UserState.main_menu)
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)

    elif await state.get_state() == UserState.spy_service_menu:
        await state.set_state(UserState.main_menu)
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)

    elif await state.get_state() == UserState.analyze_youtube_channel:
        await state.set_state(UserState.spy_service_menu)
        await callback_query.message.edit_text(MESSAGES["spy_service"], reply_markup=ikb.spy_service_keyboard)

    elif await state.get_state() == UserState.search_company_advertising:
        await state.set_state(UserState.spy_service_menu)
        await callback_query.message.edit_text(MESSAGES["spy_service"], reply_markup=ikb.spy_service_keyboard)

    elif await state.get_state() == UserState.account_menu:
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
        await state.set_state(UserState.main_menu)

    elif await state.get_state() == UserState.support_menu:
        await callback_query.message.edit_text(MESSAGES["main_menu"], reply_markup=ikb.main_menu)
        await state.set_state(UserState.main_menu)
