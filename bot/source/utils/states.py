from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    start = State()
    main_menu = State()
    help = State()
    cloud_menu = State()
    spy_service_menu = State()
    analyze_youtube_channel = State()
    search_company_advertising = State()
    account_menu = State()
    subscription_menu = State()
    balance_menu = State()
    support_menu = State()
    link = State()


class RegState(StatesGroup):
    name = State()
    age = State()
    email = State()
    phone = State()
    edit = State()
    confirm = State()
    edit_name = State()
    edit_age = State()
    edit_email = State()
    edit_phone = State()
