
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B

from . import ddb


def menu() -> InlineKeyboardMarkup:
    rows = [
        [B(text=f"{tpl['emoji']} {tpl['menu']}", callback_data=f"d:{kind}")]
        for kind, tpl in ddb.TEMPLATES.items()
    ]
    rows.append([
        B(text="🧾 История", callback_data="d_history"),
        B(text="📊 Статистика", callback_data="d_stats"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="Отменить", callback_data="d_menu")]])


def back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="⏪ Назад", callback_data="d_menu")]])


def after_render() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text="🔁 Ещё чек", callback_data="d_menu")]])
