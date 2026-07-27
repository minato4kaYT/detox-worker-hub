
import json
from pathlib import Path
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared import db
from .. import edb
from ..models_db import get_all_models, get_vip_models, get_model_by_id
from ..payments_system import PaymentSystem, NotificationSystem

router = Router()

DATA_FILE = Path(__file__).parent.parent.parent / "_extract" / "violet_proper" / "data.json"
MEDIA_DIR = Path(__file__).parent.parent / "media"

with open(DATA_FILE) as f:
    DATA = json.load(f)
    SCREENS = DATA.get('screens', [])

MEDIA_DIR.mkdir(exist_ok=True)


CALLBACK_MAP = {
    'profile': 1,
    'vip_models': 2,
    'search_model': 3,
    'information': 5,
    'top_up_balance': 6,
    'favorite_models': 8,
    'back_to_menu': 0,
}


BUTTON_TARGETS = {
    '🧑‍💼 Личный кабинет': 1,
    '💎 VIP Модели': 2,
    '👧 Найти девушку': 3,
    '👨‍💻 Тех. поддержка': 4,
    '📌 Информация': 5,
    '💳 Пополнить баланс': 6,
    '💎 Купить подписку': 7,
    '👩🏼 Избранные модели': 8,
    '🧩 Акт. промокод': 9,
    '⬅️ Вернуться в меню': 0,
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
            data = btn.get('data', '')

            if not text:
                continue

            if data:
                cb_data = data[:63]
            else:
                cb_data = f"btn_{text[:40]}"

            row_btns.append(InlineKeyboardButton(text=text, callback_data=cb_data))

        if row_btns:
            kb_list.append(row_btns)

    return InlineKeyboardMarkup(inline_keyboard=kb_list) if kb_list else None

def build_models_kb(models=None, page=0):

    if models is None:
        models = get_all_models()

    kb_list = []

    for model in models:
        text = f"{model['name']} ({model['age']}) ⭐{model['rating']} | {model['price']}"
        kb_list.append([InlineKeyboardButton(
            text=text,
            callback_data=f"model_{model['id']}"
        )])


    kb_list.append([InlineKeyboardButton(text="⬅️ Вернуться в меню", callback_data="btn_⬅️ Вернуться в меню")])

    return InlineKeyboardMarkup(inline_keyboard=kb_list)

async def send_screen(message: Message, screen: dict):

    text = screen.get('text', '')
    kb = build_kb(screen)


    if text.startswith('💎 VIP'):
        models = get_vip_models()
        vip_text = f"""💎 **VIP МОДЕЛИ** ({len(models)})

👑 Премиум сервис
⭐ Рейтинг 4.8+
🌟 Проверенные

Выбирайте:"""
        kb = build_models_kb(models)
        await message.answer(vip_text, reply_markup=kb)
        return


    if text.startswith('👧 Найти'):
        models = get_all_models()
        find_text = f"""👧 **ПОИСК МОДЕЛЕЙ** ({len(models)})

🔥 Доступные девушки
💬 Онлайн
😍 На любой вкус

Выбирайте:"""
        kb = build_models_kb(models)
        await message.answer(find_text, reply_markup=kb)
        return


    if text.startswith('📌'):
        info_text = '''📌 **ИНФОРМАЦИЯ О СЕРВИСЕ**

🏆 Violet Agency
🛡️ 100% конфиденциальность
⚡ Доступ 24/7
💎 Проверенные девушки
✅ Безопасность гарантирована

📞 Служба поддержки: @VioletAgencyHelpBot'''
        await message.answer(info_text)
        return


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


    if text.startswith('💎 VIP'):
        models = get_vip_models()
        vip_text = f"""💎 **VIP МОДЕЛИ** ({len(models)})

👑 Премиум сервис
⭐ Рейтинг 4.8+
🌟 Проверенные

Выбирайте:"""
        kb = build_models_kb(models)
        await cb.message.answer(vip_text, reply_markup=kb)
        await cb.answer()
        return


    if text.startswith('👧 Найти'):
        models = get_all_models()
        find_text = f"""👧 **ПОИСК МОДЕЛЕЙ** ({len(models)})

🔥 Доступные девушки
💬 Онлайн
😍 На любой вкус

Выбирайте:"""
        kb = build_models_kb(models)
        await cb.message.answer(find_text, reply_markup=kb)
        await cb.answer()
        return


    if text.startswith('📌'):
        info_text = '''📌 **ИНФОРМАЦИЯ О СЕРВИСЕ**

🏆 Violet Agency
🛡️ 100% конфиденциальность
⚡ Доступ 24/7
💎 Проверенные девушки
✅ Безопасность гарантирована

📞 Служба поддержки: @VioletAgencyHelpBot'''
        await cb.message.answer(info_text)
        await cb.answer()
        return


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


    if data.startswith("model_"):
        model_id = int(data.split("_")[1])
        model = get_model_by_id(model_id)

        if model:
            text = f"""👸 **{model['name'].upper()}**

📍 {model['city']}
🎂 {model['age']} лет | ⭐ {model['rating']}/5 ({model['reviews']} отзывов)
💵 {model['price']}

{model['bio']}

📞 **Забронировать:**"""


            media_files = list(MEDIA_DIR.glob('media_*'))
            if media_files:
                await cb.message.answer_photo(
                    FSInputFile(str(media_files[0])),
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="📞 Забронировать", callback_data=f"book_{model_id}"),
                        InlineKeyboardButton(text="⬅️ К моделям", callback_data="search_model")
                    ]])
                )
            else:
                await cb.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📞 Забронировать", callback_data=f"book_{model_id}"),
                    InlineKeyboardButton(text="⬅️ К моделям", callback_data="search_model")
                ]]))

        await cb.answer()
        return


    if data.startswith("book_"):
        model_id = int(data.split("_")[1])
        model = get_model_by_id(model_id)
        if model:

            price_str = model['price'].replace('₽/ч', '').replace('₽', '').strip()
            try:
                amount = float(price_str)
            except:
                amount = 2500.0


            worker_id = 1
            payment = PaymentSystem.process_booking(
                model_id=model_id,
                client_id=cb.from_user.id,
                worker_id=worker_id,
                amount=amount
            )


            worker = PaymentSystem.get_worker_by_id(worker_id)
            if worker:
                notification_text = PaymentSystem.get_worker_notification(worker_id, payment)

                NotificationSystem.queue_notification(worker['telegram_id'], notification_text)

            await cb.message.answer(f"""✅ **ЗАЯВКА ПРИНЯТА**

Вы выбрали: **{model['name']}** ({model['age']} лет)
💵 Цена: {model['price']}

📞 Оператор свяжется с вами в течение 5 минут
🕐 Время прибытия: 15-30 минут

🔔 Убедитесь, что номер верный""")
        await cb.answer()
        return


    screen_id = CALLBACK_MAP.get(data)
    if screen_id is not None:
        screen = SCREENS[screen_id]
        await send_screen_cb(cb, screen)
        return


    await cb.answer("❌")

@router.message()
async def on_message(message: Message):

    text = message.text or ""

    screen_id = BUTTON_TARGETS.get(text)

    if screen_id is not None:
        screen = SCREENS[screen_id]
        await send_screen(message, screen)
    elif SCREENS:
        await send_screen(message, SCREENS[0])
