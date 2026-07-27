

import json
import os
from pathlib import Path
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import FSInputFile


DATA_FILE = Path("/root/detox/_extract/violet/data.json")
MEDIA_DIR = Path("/root/detox/escort/media")

with open(DATA_FILE) as f:
    BOT_DATA = json.load(f)

SCREENS = BOT_DATA.get('screens', [])
MEDIA_DIR.mkdir(exist_ok=True)

class VioletStates(StatesGroup):
    browsing = State()
    cabinet = State()
    search = State()
    booking = State()

router = Router()

def find_screen(via_text: str) -> dict:

    for screen in SCREENS:
        if screen.get('_via') == via_text:
            return screen
    return SCREENS[1] if len(SCREENS) > 1 else {}

def build_kb(buttons_data: list, is_inline: bool = False):

    if not buttons_data:
        return None

    if is_inline:
        kb_list = []
        for row in buttons_data:
            row_btns = []
            for btn in row:
                text = btn.get('text', '')
                if btn.get('cls') == 'KeyboardButtonCallback':
                    data = btn.get('data', '')
                    row_btns.append(InlineKeyboardButton(text=text, callback_data=data))
                elif btn.get('cls') == 'KeyboardButtonUrl':
                    url = btn.get('url', '')
                    row_btns.append(InlineKeyboardButton(text=text, url=url))
            if row_btns:
                kb_list.append(row_btns)
        return InlineKeyboardMarkup(inline_keyboard=kb_list) if kb_list else None
    else:
        kb_list = []
        for row in buttons_data:
            row_btns = []
            for btn in row:
                text = btn.get('text', '')
                row_btns.append(KeyboardButton(text=text))
            if row_btns:
                kb_list.append(row_btns)
        return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True) if kb_list else None

async def send_screen(screen: dict, message_or_cb, is_edit: bool = False):

    text = screen.get('text', '')
    buttons = screen.get('buttons', [])
    kb_type = screen.get('kb_type', '')
    is_inline = 'Inline' in kb_type

    kb = build_kb(buttons, is_inline) if buttons else None


    if screen.get('has_media'):
        media_id = screen.get('media_id')
        media_kind = screen.get('media_kind')
        media_path = MEDIA_DIR / str(media_id)

        if media_path.exists() and hasattr(message_or_cb, 'message'):

            if media_kind == 'photo':
                await message_or_cb.message.answer_photo(
                    FSInputFile(str(media_path)),
                    caption=text,
                    reply_markup=kb
                )
            elif media_kind == 'doc':
                await message_or_cb.message.answer_document(
                    FSInputFile(str(media_path)),
                    caption=text,
                    reply_markup=kb
                )
            return


        if media_kind == 'photo':
            await message_or_cb.answer_photo(
                FSInputFile(str(media_path)) if media_path.exists() else None,
                caption=text,
                reply_markup=kb
            )
        elif media_kind == 'doc':
            await message_or_cb.answer_document(
                FSInputFile(str(media_path)) if media_path.exists() else None,
                caption=text,
                reply_markup=kb
            )
        return


    if hasattr(message_or_cb, 'message'):
        if is_edit:
            await message_or_cb.message.edit_text(text, reply_markup=kb)
        else:
            await message_or_cb.message.answer(text, reply_markup=kb)
    else:
        await message_or_cb.answer(text, reply_markup=kb)

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    await state.clear()

    if len(SCREENS) > 1:
        await send_screen(SCREENS[1], message)
        await state.set_state(VioletStates.browsing)

@router.message(VioletStates.browsing)
async def on_menu(message: types.Message, state: FSMContext):

    text = message.text

    for screen in SCREENS:
        for row in screen.get('buttons', []):
            for btn in row:
                if btn.get('text') == text:

                    for next_screen in SCREENS:
                        if next_screen.get('_via', '').endswith(text):
                            await send_screen(next_screen, message)
                            return


    if len(SCREENS) > 1:
        await send_screen(SCREENS[1], message)

@router.callback_query(VioletStates.browsing)
async def on_callback(cb: types.CallbackQuery, state: FSMContext):

    data = cb.data

    for screen in SCREENS:
        for row in screen.get('buttons', []):
            for btn in row:
                if btn.get('data') == data:

                    for next_screen in SCREENS:
                        if next_screen.get('_via', '').endswith(btn.get('text', '')):
                            await send_screen(next_screen, cb)
                            await cb.answer()
                            return

    await cb.answer()
