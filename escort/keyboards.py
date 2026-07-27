
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B

from . import edb


def platform() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="💃 VIP Модели", callback_data="v_models")],
        [B(text="🔎 Найти девушку", callback_data="v_search")],
        [B(text="👤 Личный кабинет", callback_data="v_cabinet")],
        [B(text="💎 VIP-доступ", callback_data="v_vip"),
         B(text="🎁 Промокод", callback_data="v_promo")],
        [B(text="👨‍💻 Менеджер", callback_data="v_support")],
    ])


def models_list() -> InlineKeyboardMarkup:
    rows = [[B(text=f"💃 {m['name']} · {m['city']}", callback_data=f"vm:{m['id']}")]
            for m in edb.MODELS]
    rows.append([B(text="⏪ Назад", callback_data="v_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def model_card(mid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="💐 Забронировать встречу", callback_data=f"vbook:{mid}")],
        [B(text="⏪ К списку", callback_data="v_models")],
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
        [B(text="💐 Мин. предоплата", callback_data="ws:min_prepay"),
         B(text="💎 Цена VIP", callback_data="ws:vip_price")],
        [B(text="🎁 Бонус", callback_data="ws:welcome_bonus")],
        [B(text="🚫 Авто-отклонение возвратов", callback_data="ws_toggle")],
        [B(text="⏪ Назад", callback_data="w_menu")],
    ])


def back_worker() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="⏪ Назад", callback_data="w_menu")]])
