import os
import re
import json
import logging

from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

import bot.source.keyboards.reply as rkb
from bot.source.utils.states import UserState, RegState

from bot.source.utils.templates import BUTTONS, MESSAGES

from sqlalchemy.orm import Session
from database.models import User
from database.db_init import get_db

load_dotenv()

router = Router()

# Логирование ошибок
logger = logging.getLogger(__name__)

# Путь к файлам
USER_DATA_PATH = os.getenv('USER_DATA_PATH')


# Сохранение данных пользователя в базу данных
def save_user_to_db(user_data, db: Session):
    try:
        user = User(
            id=user_data["id"],
            name=user_data["name"],
            age=user_data["age"],
            email=user_data["email"],
            phone=user_data["phone"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return True
    except Exception as e:
        logger.error(f"Error saving user to database: {e}")
        db.rollback()
        return False


# Проверка валидности данных
def is_valid_age(age: str) -> bool:
    return age.isdigit() and 0 < int(age) < 120


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    return phone.isdigit() and len(phone) in [10, 11]


# Создание клавиатуры для подтверждения данных
def create_confirmation_markup():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTONS["confirm"]), KeyboardButton(text=BUTTONS["edit"])]
        ],
        resize_keyboard=True
    )


# Шаги регистрации
@router.message(F.text == BUTTONS["registration_button"])
async def start_registration(message: Message, state: FSMContext):
    await message.answer(MESSAGES["name_request"])
    await state.set_state(RegState.name)


@router.message(RegState.name)
async def process_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer(MESSAGES["name_invalid"])
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(RegState.age)
    await message.answer(MESSAGES["age_request"])


@router.message(RegState.age)
async def process_age(message: Message, state: FSMContext):
    user_age = message.text.strip()
    if not is_valid_age(user_age):
        await message.answer(MESSAGES["age_invalid"])
        return
    await state.update_data(age=user_age)
    await message.answer(MESSAGES["email_request"])
    await state.set_state(RegState.email)


@router.message(RegState.email)
async def process_email(message: Message, state: FSMContext):
    user_email = message.text.strip()
    if not is_valid_email(user_email):
        await message.answer(MESSAGES["email_invalid"])
        return
    await state.update_data(email=user_email)
    await state.set_state(RegState.phone)
    await message.answer(MESSAGES["phone_request"])


@router.message(RegState.phone)
async def process_phone(message: Message, state: FSMContext):
    user_phone = message.text.strip()
    if not is_valid_phone(user_phone):
        await message.answer(MESSAGES["phone_invalid"])
        return
    await state.update_data(phone=user_phone)

    user_data = await state.get_data()
    await message.answer(
        f"{MESSAGES['confirmation']}\n\n"
        f"Имя: {user_data['name']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Email: {user_data['email']}\n"
        f"Телефон: {user_data['phone']}",
        reply_markup=create_confirmation_markup()
    )
    await state.set_state(RegState.confirm)


@router.message(RegState.confirm)
async def confirm_data(message: Message, state: FSMContext):
    user_response = message.text.strip()
    user_data = await state.get_data()

    if user_response == BUTTONS["confirm"]:
        user_data["id"] = message.from_user.id

        db: Session = next(get_db())

        if save_user_to_db(user_data, db):
            await message.answer(MESSAGES["registration_complete"], reply_markup=rkb.menu_button)
            await state.clear()
            await state.set_state(UserState.main_menu)
        else:
            await message.answer("Произошла ошибка при сохранении данных. Попробуйте позже.")
    elif user_response == BUTTONS["edit"]:
        await message.answer(MESSAGES["edit_prompt"], reply_markup=rkb.edit_menu)
        await state.set_state(RegState.edit)
    else:
        await message.answer(MESSAGES["confirmation_invalid"])


# Обновление данных
@router.message(RegState.edit)
async def edit_data(message: Message, state: FSMContext):
    edit_choice = message.text.strip()

    if edit_choice == BUTTONS["edit_name"]:
        await message.answer(MESSAGES["name_request"])
        await state.set_state(RegState.edit_name)
    elif edit_choice == BUTTONS["edit_age"]:
        await message.answer(MESSAGES["age_request"])
        await state.set_state(RegState.edit_age)
    elif edit_choice == BUTTONS["edit_email"]:
        await message.answer(MESSAGES["email_request"])
        await state.set_state(RegState.edit_email)
    elif edit_choice == BUTTONS["edit_phone"]:
        await message.answer(MESSAGES["phone_request"])
        await state.set_state(RegState.edit_phone)
    else:
        await message.answer(MESSAGES["edit_invalid"])


# Обновление конкретных данных и возврат к подтверждению
async def return_to_confirmation(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        f"{MESSAGES['confirmation']}\n\n"
        f"Имя: {user_data['name']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Email: {user_data['email']}\n"
        f"Телефон: {user_data['phone']}",
        reply_markup=create_confirmation_markup()
    )
    await state.set_state(RegState.confirm)


# Редактирование данных
@router.message(RegState.edit_name)
async def update_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer(MESSAGES["name_invalid"])
        return
    await state.update_data(name=message.text.strip())
    await return_to_confirmation(message, state)


# Редактирование возраста
@router.message(RegState.edit_age)
async def update_age(message: Message, state: FSMContext):
    user_age = message.text.strip()
    if not is_valid_age(user_age):
        await message.answer(MESSAGES["age_invalid"])
        return
    await state.update_data(age=user_age)
    await return_to_confirmation(message, state)


# Редактирование email
@router.message(RegState.edit_email)
async def update_email(message: Message, state: FSMContext):
    user_email = message.text.strip()
    if not is_valid_email(user_email):
        await message.answer(MESSAGES["email_invalid"])
        return
    await state.update_data(email=user_email)
    await return_to_confirmation(message, state)


# Редактирование телефона
@router.message(RegState.edit_phone)
async def update_phone(message: Message, state: FSMContext):
    user_phone = message.text.strip()
    if not is_valid_phone(user_phone):
        await message.answer(MESSAGES["phone_invalid"])
        return
    await state.update_data(phone=user_phone)
    await return_to_confirmation(message, state)
