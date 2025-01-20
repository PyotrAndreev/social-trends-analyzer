from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import keyboards as kb

router = Router()

class UserState(StatesGroup):
    name = State()
    position = State()
    main_menu = State()
    account_menu = State()
    report_menu = State()
    support_menu = State()

menu_text = (
        "Просто отправьте ссылку на видео и получите детальный отчет по комментариям: "
        "топовые мнения, облако ключевых слов, анализ настроений и многое другое.\n\n"
        "**Выберите нужное действие:**"
)

report_text = (
        "💬 Введите ссылку на YouTube-видео, чтобы получить подробный анализ комментариев.\n\n"
        "Что включает отчет?\n\n"
        "1. ☁️ Облако ключевых слов — визуализация популярных тем.Чем чаще слово встречается, тем крупнее оно отображается.\n\n"
        "2. 🔝 Топ комментариев по вовлеченности — самые обсуждаемые и залайканные мнения.\n\n"
        "3. 📊 График активности по типам — анализ вовлеченности для разных типов комментариев (вопросы, мемы и т.д.).\n\n"
        "4. 🎭 Распределение настроений — оценка настроения комментариев(позитивное, нейтральное, негативное).\n\n"
        "5. 📉 Гистограмма эмоций по категориям — процентное распределение настроений для каждой категории.\n\n"
        "6. 🌐 Карта тем(доступно по подписке) — визуализация взаимосвязей между темами."
)

subscription_text = (
"f'**Подписка**' - открывает доступ к расширенному анализу комментариев и увеличивает дневной лимит запросов для создания отчетов.\n\n"
"Каждая подписка активна в течение 30 дней. Выберите нужный лимит запросов в сутки:"
)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(UserState.main_menu)
    await message.answer(menu_text, reply_markup=kb.main_menu)

@router.message(F.text == "🔎 Получить отчет по видео-ролику")
async def get_report(message: Message, state: FSMContext):
    await state.set_state(UserState.report_menu)
    await message.answer(report_text, reply_markup=kb.report_menu)

@router.message(F.text == "⬅️ Назад")
async def go_back(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == UserState.report_menu.state:
        await state.set_state(UserState.main_menu)
        await message.answer(menu_text, reply_markup=kb.main_menu)

    elif current_state == UserState.account_menu.state:
        await state.set_state(UserState.main_menu)
        await message.answer(menu_text, reply_markup=kb.main_menu)

    elif current_state == UserState.support_menu.state:
        await state.set_state(UserState.main_menu)
        await message.answer(menu_text, reply_markup=kb.main_menu)


@router.message(F.text == "⚙️ Мой аккаунт")
async def account(message: Message, state: FSMContext):
    account_text = (
        f"👤 *Информация о пользователе*\n\n"
        f"ID: {message.from_user.id} \n"
        "Имя: Иван\n"
        "Фамилия: Иванов\n"
        "Email:"
        "Телефон: +7 999 999 99 99\n"
        "Подписка: Базовая\n"
        "Дата окончания подписки: 01.01.2022\n"
        "Баланс: 0 рублей\n"
    )
    await state.set_state(UserState.account_menu)
    await message.answer(account_text, reply_markup=kb.account_menu)

@router.message(F.text == "💎 Управление подпиской")
async def subscription(message: Message):
    await message.answer(subscription_text, reply_markup=kb.subscription_menu)


@router.message(F.text == "Поддедржка")
async def support(message: Message, state: FSMContext):
    await state.set_state(UserState.support_menu)
    await message.answer("", reply_markup=kb.support_menu)

@router.message(F.text == "Управление подпиской")
async def subscription(message: Message):
    await message.answer("")



