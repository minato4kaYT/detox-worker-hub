
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
from aiogram.utils.keyboard import InlineKeyboardBuilder


def platform() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="💼 Портфель", callback_data="v_portfolio")],
        [B(text="📊 Открыть ECN", callback_data="v_trade")],
        [B(text="📥 Пополнить", callback_data="v_deposit"),
         B(text="📤 Вывести", callback_data="v_withdraw")],
        [B(text="🎁 Промокод", callback_data="v_promo"),
         B(text="🏦 Стейкинг", callback_data="v_staking")],
        [B(text="👨‍💻 Тех. поддержка", callback_data="v_support")],
    ])


def back_platform() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="⏪ Назад", callback_data="v_menu")]])


def cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="Отменить", callback_data="v_menu")]])


def worker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🦣 Мамонты", callback_data="w_mammoths"),
         B(text="🔗 Реф. ссылка", callback_data="w_ref")],
        [B(text="📢 Рассылка", callback_data="w_broadcast"),
         B(text="🎟️ Создать промокод", callback_data="w_promo")],
        [B(text="⚙️ Настройка бота", callback_data="w_settings")],
        [B(text="📊 Статистика", callback_data="w_stats")],
    ])


def settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🍀 Удача", callback_data="ws:luck"),
         B(text="📐 Коэф. min", callback_data="ws:coef_min"),
         B(text="📐 Коэф. max", callback_data="ws:coef_max")],
        [B(text="💵 Мин. сделка", callback_data="ws:min_deal"),
         B(text="📤 Мин. вывод", callback_data="ws:min_withdraw"),
         B(text="📥 Мин. пополн.", callback_data="ws:min_deposit")],
        [B(text="🚫 Авто-отклонение", callback_data="ws_toggle")],
        [B(text="⏪ Назад", callback_data="w_menu")],
    ])


def back_worker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="⏪ Назад", callback_data="w_menu")]])
