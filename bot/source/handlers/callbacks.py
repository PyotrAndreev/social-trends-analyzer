from aiogram import Router, F
from aiogram.types import CallbackQuery
import aiofiles

from bot.source.utils.states import UserState
import logging
import bot.source.keyboards.inline as ikb
import bot.source.keyboards.shared as skb

from bot.source.utils.templates import MESSAGES
import httpx
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile, InputFile

from comments_analyze import get_youtube_comments, get_embeddings, extract_keywords, generate_wordcloud, \
    cluster_embeddings_with_progress

router = Router()


@router.callback_query(F.data == "get_spy")
async def get_spy_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.spy_service_menu)
    await callback_query.message.edit_text(MESSAGES["spy_service"], reply_markup=ikb.spy_service_keyboard)


@router.callback_query(F.data == "analyze_youtube_channel")
async def analyze_youtube_channel(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.analyze_youtube_channel)
    await callback_query.message.edit_text(MESSAGES["analyze_youtube_channel"], reply_markup=skb.back_kb)
    # user_data = await state.get_data()
    # link = user_data.get("link", None)
    link = 'https://www.youtube.com/@faib'

    if link:
        await callback_query.message.answer(MESSAGES["link_confirmed"])

        bot = callback_query.bot

        try:
            await bot.send_message(callback_query.from_user.id, "Запрашиваю данные с сервера...")

            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:8000/channels/fetch-ads/", params={"channel_url": link})

            logging.info(f"Ответ сервера: {response.status_code}")

            if response.status_code == 200:
                file_path = "/tmp/temp_ads.xlsx"

                async with aiofiles.open(file_path, "wb") as file:
                    await file.write(response.content)

                await bot.send_message(callback_query.from_user.id, "Файл успешно сохранен, отправляю...")

                document = FSInputFile(file_path)
                await bot.send_document(
                    chat_id=callback_query.from_user.id,
                    document=document,
                    caption="Ваш файл с рекламными данными"
                )

                logging.info("Файл успешно отправлен пользователю")
            else:
                await bot.send_message(callback_query.from_user.id,
                                       f"Ошибка при получении файла: {response.status_code}")
                logging.error(f"Ошибка сервера: {response.text}")

        except Exception as e:
            logging.error(f"Ошибка обработки запроса: {e}")
            await bot.send_message(callback_query.from_user.id, f"Ошибка обработки: {e}")

        await state.clear()


@router.callback_query(F.data == "search_company_advertising")
async def search_company_advertising(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.search_company_advertising)
    await callback_query.message.edit_text(MESSAGES["search_company_advertising"], reply_markup=skb.back_kb)


@router.callback_query(F.data == "get_cloud")
async def get_cloud_command(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.cloud_menu)
    await callback_query.message.edit_text(MESSAGES["cloud_of_meanings"], reply_markup=skb.back_kb)
    video_id = 'b--nRgmCvrY'
    comments = await get_youtube_comments(video_id, max_comments=100)
    embeddings = await get_embeddings(comments)
    labels = cluster_embeddings_with_progress(embeddings, n_clusters=10, method="hierarchical")
    cluster_keywords = await extract_keywords(comments, embeddings, labels)
    image_path = await generate_wordcloud(cluster_keywords)
    await callback_query.message.answer_photo(InputFile(image_path))


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
    # user_data = await state.get_data()
    # link = user_data.get("link", None)
    link = 'https://www.youtube.com/@faib'

    if link:
        await callback_query.message.answer(MESSAGES["link_confirmed"])

        bot = callback_query.bot

        try:
            await bot.send_message(callback_query.from_user.id, "Запрашиваю данные с сервера...")

            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:8000/channels/fetch-ads/", params={"channel_url": link})

            if response.status_code == 200:
                file_path = "/tmp/temp_ads.xlsx"

                async with aiofiles.open(file_path, "wb") as file:
                    await file.write(response.content)

                document = FSInputFile(file_path)
                await bot.send_document(
                    chat_id=callback_query.from_user.id,
                    document=document,
                    caption="Ваш файл с рекламными данными"
                )

            else:
                await bot.send_message(callback_query.from_user.id,
                                       f"Ошибка при получении файла: {response.status_code}")

        except Exception as e:
            await bot.send_message(callback_query.from_user.id, f"Ошибка обработки: {e}")

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
