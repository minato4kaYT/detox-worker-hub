

import asyncio
from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from shared import db, hubauth
from .. import texts, keyboards as kb, ddb, render
from ..states import Draw

router = Router()


async def _guard(user_id: int) -> bool:

    return await hubauth.is_authorized(user_id)


async def _deny(target) -> None:
    msg = "⛔️ Доступ только для одобренных воркеров панели @aOnyxPay_Bot."
    if isinstance(target, CallbackQuery):
        await target.answer(msg, show_alert=True)
    else:
        await target.answer(msg)


@router.message(CommandStart())
@router.message(Command("draw"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db.upsert_user(message.from_user.id, message.from_user.username,
                         message.from_user.first_name)
    if not await _guard(message.from_user.id):
        await _deny(message)
        return
    await message.answer(texts.menu(escape(message.from_user.first_name or "воркер")),
                         reply_markup=kb.menu())


@router.callback_query(F.data == "d_menu")
async def d_menu(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not await _guard(cb.from_user.id):
        await _deny(cb)
        return
    await cb.message.edit_text(texts.menu(escape(cb.from_user.first_name or "воркер")),
                               reply_markup=kb.menu())
    await cb.answer()


@router.callback_query(F.data.startswith("d:"))
async def pick_kind(cb: CallbackQuery, state: FSMContext) -> None:
    if not await _guard(cb.from_user.id):
        await _deny(cb)
        return
    kind = cb.data.split(":", 1)[1]
    if ddb.template(kind) is None:
        await cb.answer("Неизвестный шаблон.", show_alert=True)
        return
    await state.set_state(Draw.amount)
    await state.update_data(kind=kind)
    await cb.message.answer(texts.ask_amount(kind), reply_markup=kb.cancel())
    await cb.answer()


@router.message(Draw.amount)
async def enter_amount(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").replace(" ", "").replace(",", ".").strip()
    try:
        amount = float(raw)
    except ValueError:
        await message.answer(texts.bad_amount(), reply_markup=kb.cancel())
        return
    if amount <= 0:
        await message.answer(texts.bad_amount(), reply_markup=kb.cancel())
        return
    data = await state.get_data()
    tpl = ddb.template(data["kind"]) or ddb.TEMPLATES["card"]
    await state.update_data(amount=amount)
    await state.set_state(Draw.recipient)
    await message.answer(tpl["ask"], reply_markup=kb.cancel())


@router.message(Draw.recipient)
async def enter_recipient(message: Message, state: FSMContext) -> None:
    recipient = (message.text or "").strip()
    if not recipient:
        await message.answer("Введите получателя текстом.", reply_markup=kb.cancel())
        return
    await state.update_data(recipient=recipient)
    await state.set_state(Draw.sender)
    await message.answer(texts.ask_sender(), reply_markup=kb.cancel())


@router.message(Draw.sender)
async def enter_sender(message: Message, state: FSMContext) -> None:
    sender = (message.text or "").strip()
    if not sender:
        await message.answer("Введите ФИО отправителя текстом.", reply_markup=kb.cancel())
        return
    data = await state.get_data()
    kind, amount, recipient = data["kind"], float(data["amount"]), data["recipient"]
    await state.clear()

    note = await message.answer("🖨️ Готовлю образец…")

    png = await asyncio.to_thread(render.render_receipt, kind, amount, recipient, sender)
    await ddb.log_draw(message.from_user.id, kind, amount, recipient)

    tpl = ddb.template(kind) or ddb.TEMPLATES["card"]
    caption = (f"{tpl['emoji']} {tpl['brand']} · образец на {amount:,.0f} {tpl['unit']}\n"
               "⚠️  — не является платёжным документом.").replace(",", " ")
    try:
        await note.delete()
    except Exception:
        pass
    await message.answer_photo(
        BufferedInputFile(png, filename=f"receipt_{kind}.png"),
        caption=caption, reply_markup=kb.after_render(),
    )


@router.callback_query(F.data == "d_history")
async def d_history(cb: CallbackQuery) -> None:
    if not await _guard(cb.from_user.id):
        await _deny(cb)
        return
    rows = await ddb.last_draws(cb.from_user.id, limit=10)
    await cb.message.edit_text(texts.history(rows), reply_markup=kb.back())
    await cb.answer()


@router.callback_query(F.data == "d_stats")
async def d_stats(cb: CallbackQuery) -> None:
    if not await _guard(cb.from_user.id):
        await _deny(cb)
        return
    s = await ddb.worker_stats(cb.from_user.id)
    cur = await db.conn().execute(
        "SELECT kind, COUNT(*) AS c FROM draw_ops WHERE worker_id=? GROUP BY kind",
        (cb.from_user.id,),
    )
    kind_counts = {row["kind"]: row["c"] for row in await cur.fetchall()}
    await cb.message.edit_text(texts.stats(kind_counts, s), reply_markup=kb.back())
    await cb.answer()
