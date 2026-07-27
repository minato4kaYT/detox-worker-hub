
import asyncio
import json
from pathlib import Path
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared import db
from .. import tdb

router = Router()

DATA_FILE = Path(__file__).parent.parent.parent / "_extract" / "mexc_proper" / "data.json"
MEDIA_DIR = Path(__file__).parent.parent / "media"

with open(DATA_FILE) as f:
    DATA = json.load(f)
    SCREENS = DATA.get('screens', [])

MEDIA_DIR.mkdir(exist_ok=True)


NAV_MAP = {
    'Новости': 1,
    'Соглашения': 1,
    'Личный кабинет': 1,
}

def build_kb(screen):
    buttons = screen.get('buttons', [])
    if not buttons:
        return None

    kb_list = []
    for row in buttons:
        row_btns = []
        for btn in row:
            text = btn.get('text', '')
            if not text:
                continue

            row_btns.append(InlineKeyboardButton(
                text=text,
                callback_data=f"nav_{text[:40]}"
            ))

        if row_btns:
            kb_list.append(row_btns)

    return InlineKeyboardMarkup(inline_keyboard=kb_list) if kb_list else None

async def send_screen(message: Message, screen: dict):
    text = screen.get('text', '')
    kb = build_kb(screen)

    if screen.get('has_media') and screen.get('media_file'):
        media_path = MEDIA_DIR / screen['media_file']
        if media_path.exists():
            await message.answer_photo(
                FSInputFile(str(media_path)),
                caption=text if text else None,
                reply_markup=kb
            )
            return

    if text or kb:
        await message.answer(text if text else " ", reply_markup=kb)

async def send_screen_cb(cb: CallbackQuery, screen: dict):
    text = screen.get('text', '')
    kb = build_kb(screen)

    if screen.get('has_media') and screen.get('media_file'):
        media_path = MEDIA_DIR / screen['media_file']
        if media_path.exists():
            await cb.message.answer_photo(
                FSInputFile(str(media_path)),
                caption=text if text else None,
                reply_markup=kb
            )
            await cb.answer()
            return

    if text or kb:
        try:
            await cb.message.edit_text(text if text else " ", reply_markup=kb)
        except:
            await cb.message.answer(text if text else " ", reply_markup=kb)

    await cb.answer()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    u = message.from_user
    await db.upsert_user(u.id, u.username, u.first_name)

    if SCREENS:
        await send_screen(message, SCREENS[0])

@router.callback_query()
async def on_callback(cb: CallbackQuery):
    data = cb.data

    if data.startswith("nav_"):
        btn_text = data.replace("nav_", "", 1)
        screen_id = NAV_MAP.get(btn_text)

        if screen_id is not None:
            screen = SCREENS[screen_id]
            await send_screen_cb(cb, screen)
        else:
            await cb.answer("❌")
    else:
        await cb.answer()

@router.message()
async def on_message(message: Message):
    text = message.text or ""
    screen_id = NAV_MAP.get(text)

    if screen_id is not None:
        await send_screen(message, SCREENS[screen_id])
    elif SCREENS:
        await send_screen(message, SCREENS[0])
