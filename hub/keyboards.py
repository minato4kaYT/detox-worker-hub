
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
from aiogram.utils.keyboard import InlineKeyboardBuilder

from shared import config


def cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="Отменить", callback_data="cancel")]])


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="👤 Профиль", callback_data="profile")],
        [B(text="🤖 Боты", callback_data="bots")],
        [B(text="🛠️ Инструменты", callback_data="tools")],
        [B(text="ℹ️ О проекте", callback_data="about")],
    ])


def about() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🏆 Топ воркеров", callback_data="top")],
        [B(text="💬 Общий чат", url=config.LINK_CHAT),
         B(text="📌 Инфо-канал", url=config.LINK_INFO)],
        [B(text="📕 Правила", url=config.LINK_RULES),
         B(text="💸 Профиты", url=config.LINK_PROFITS)],
        [B(text="⏪ Назад в меню", callback_data="menu")],
    ])


def profile() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🎓 Кураторы", callback_data="curators"),
         B(text="⚙️ Настройки", callback_data="settings")],
        [B(text="💸 Профиты", url=config.LINK_PROFITS),
         B(text="🛒 Магазин", callback_data="shop")],
        [B(text="⏪ Назад в меню", callback_data="menu")],
    ])


def curators(rows) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in rows:
        kb.row(B(text=f"🎓 {c['name']} [{c['direction']}]", callback_data=f"cur:{c['id']}"))
    kb.row(B(text="⏪ Назад", callback_data="profile"))
    return kb.as_markup()


def settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🏷️ Никнейм", callback_data="set_nick")],
        [B(text="⏪ Назад", callback_data="profile")],
    ])


SHOP_CATS = [
    ("📱", "Аккаунты", 5.0), ("⭐", "Звёзды Telegram", 3.0),
    ("📈", "Накрутка", 2.0), ("📸", "Модели", 8.0),
    ("👑", "Премиум", 10.0), ("⚡", "Бустеры", 4.0),
]


def shop() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, (icon, name, _price) in enumerate(SHOP_CATS):
        kb.button(text=f"{icon} {name}", callback_data=f"shopcat:{i}")
    kb.adjust(2)
    kb.row(B(text="⏪ Назад", callback_data="profile"))
    return kb.as_markup()


def shop_item(idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="✅ Купить", callback_data=f"buy:{idx}")],
        [B(text="⏪ Назад", callback_data="shop")],
    ])


def bots() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🪭 Эскорт", callback_data="escort")],
        [B(text="📊 Трейд", callback_data="trade")],
        [B(text="⏪ Назад в меню", callback_data="menu")],
    ])


def trade_section() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="📊 MEXC (трейд)", url=f"https://t.me/{config.TRADE_BOT_USERNAME}")],
        [B(text="📕 Мануал", url=config.LINK_MANUALS)],
        [B(text="⏪ Назад", callback_data="bots")],
    ])


def escort_section() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="🪭 Violet Agency", url=f"https://t.me/{config.ESCORT_BOT_USERNAME}")],
        [B(text="📕 Мануал", url=config.LINK_MANUALS),
         B(text="💳 Реквизиты", callback_data="card")],
        [B(text="⏪ Назад", callback_data="bots")],
    ])


def tools() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="💳 Карта", callback_data="card")],
        [B(text="✍️ Отрисовщик", callback_data="draw")],
        [B(text="⏪ Назад в меню", callback_data="menu")],
    ])


def card() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="💳 Получить Карту", callback_data="get_card")],
        [B(text="💰 Фин. Отдел", url=config.LINK_FINANCE)],
        [B(text="⏪ Назад", callback_data="tools")],
    ])


def draw() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="✍️ Отрисовщик", url=f"https://t.me/{config.DRAW_BOT_USERNAME}")],
        [B(text="⏪ Назад", callback_data="tools")],
    ])


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="⏪ Назад в меню", callback_data="menu")]])


def moderation(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        B(text="✅ Одобрить", callback_data=f"appr:{user_id}"),
        B(text="❌ Отклонить", callback_data=f"rej:{user_id}"),
    ]])


def curators_kb(rows) -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    for c in rows:
        kb.row(B(text=f"🎓 {c['name']} [{c['direction']}]", callback_data=f"curc:{c['id']}"))
    return kb.as_markup()


def curator_decision(worker_uid: int) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(inline_keyboard=[[
        B(text="✅ Подтвердить", callback_data=f"curok:{worker_uid}"),
        B(text="❌ Отклонить", callback_data=f"curno:{worker_uid}"),
    ]])
