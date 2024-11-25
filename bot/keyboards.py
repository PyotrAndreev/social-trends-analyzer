from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔎 Получить отчет по видео-ролику")],
    [KeyboardButton(text="⚙️ Мой аккаунт"), KeyboardButton(text="🆘 Поддедржка")],
],
                            resize_keyboard=True,
                            input_field_placeholder="Выберите следующее действие.")

account_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💎 Управление подпиской")],
    [KeyboardButton(text="🧾 Операции"), KeyboardButton(text="💳️ Пополнить счёт")],
    [KeyboardButton(text="📈 История отчетов")],
    [KeyboardButton(text="📠️ Пользовательское соглашение")],
    [KeyboardButton(text="⬅️ Назад")]],
                              resize_keyboard=True,
                              input_field_placeholder="Выберите нужное действие.")

report_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⬅️ Назад", callback_data="go_back")]
])


support_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="??️ Поддержка")],
    [KeyboardButton(text="⬅️ Назад", callback_data="go_back")]
])

subscription_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="100 запросов - 800₽", callback_data="100_requests")],
    [InlineKeyboardButton(text="50 запросов - 500₽", callback_data="50 requests"), InlineKeyboardButton(text="20 запросов - 300₽", callback_data="20_requests")],
    [InlineKeyboardButton(text="10 запросов - 200₽", callback_data="10 requests"), InlineKeyboardButton(text="5 запросов - 100₽", callback_data="5_requests")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back")]
])