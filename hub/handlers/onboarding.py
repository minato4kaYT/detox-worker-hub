
from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from shared import db, config
from .. import texts, keyboards as kb
from ..states import Onboarding

router = Router()


async def show_main_menu(msg: Message) -> None:
    await msg.answer(texts.GREETING, reply_markup=kb.main_menu())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    u = message.from_user
    await db.upsert_user(u.id, u.username, u.first_name)
    w = await db.get_worker(u.id)

    if w is None or w["status"] in ("none", "rejected"):
        await state.set_state(Onboarding.hours)
        await message.answer(texts.ASK_HOURS, reply_markup=kb.cancel())
        return
    if w["status"] == "pending":
        await message.answer(texts.PENDING)
        return

    await show_main_menu(message)


@router.callback_query(F.data == "cancel")
async def cb_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer("Отменено.")
    await cb.answer()


@router.message(Onboarding.hours)
async def st_hours(message: Message, state: FSMContext) -> None:
    txt = (message.text or "").strip()
    if not txt.isdigit():
        await message.answer(texts.ERR_HOURS, reply_markup=kb.cancel())
        return
    await state.update_data(hours=int(txt))
    await state.set_state(Onboarding.source)
    await message.answer(texts.ASK_SOURCE, reply_markup=kb.cancel())


@router.message(Onboarding.source)
async def st_source(message: Message, state: FSMContext) -> None:
    await state.update_data(source=(message.text or "").strip())
    await state.set_state(Onboarding.experience)
    await message.answer(texts.ASK_EXPERIENCE, reply_markup=kb.cancel())


@router.message(Onboarding.experience)
async def st_experience(message: Message, state: FSMContext) -> None:
    experience = (message.text or "").strip()
    await state.update_data(experience=experience)


    curators = await db.list_curators()
    if not curators:

        await _finish_application(message, state, curator_id=None)
        return

    await state.set_state(Onboarding.curator)
    await message.answer(texts.CURATORS_TITLE, reply_markup=kb.curators_kb(curators))


@router.callback_query(Onboarding.curator, F.data.startswith("curc:"))
async def cb_pick_curator_apply(cb: CallbackQuery, state: FSMContext) -> None:

    curator_id = int(cb.data.split(":")[1])
    try:
        await cb.message.delete()
    except Exception:
        pass
    await _finish_application(cb.message, state, curator_id=curator_id,
                             from_user=cb.from_user)
    await cb.answer()


async def _finish_application(message: Message, state: FSMContext,
                             curator_id: int | None, from_user=None) -> None:

    data = await state.get_data()
    u = from_user or message.from_user
    await db.create_application(u.id, data["hours"], data["source"], data["experience"])
    if curator_id is not None:
        await db.request_curator(u.id, curator_id)
    await state.clear()
    await message.answer(texts.APPLICATION_SENT)

    curator_line = "—"
    if curator_id is not None:
        c = await db.get_curator(curator_id)
        if c:
            curator_line = f"{c['name']} [{c['direction']}]"

    card = (
        "🆕 Новая заявка воркера\n\n"
        f"👤 {escape(u.full_name)} @{escape(u.username or '—')}\n"
        f"🆔 {u.id}\n"
        f"⏰ Часов: {data['hours']}\n"
        f"💁 Источник: {escape(data['source'])}\n"
        f"🧠 Опыт: {escape(data['experience'])}\n"
        f"🎓 Куратор: {escape(curator_line)}"
    )
    for admin in config.ADMINS:
        try:
            await message.bot.send_message(admin, card, reply_markup=kb.moderation(u.id))
        except Exception:
            pass


@router.callback_query(F.data.startswith("appr:"))
async def cb_approve(cb: CallbackQuery, bot: Bot) -> None:
    if cb.from_user.id not in config.ADMINS:
        await cb.answer("Нет прав", show_alert=True)
        return
    uid = int(cb.data.split(":")[1])
    await db.set_status(uid, "approved")
    await cb.message.edit_text(escape(cb.message.text) + "\n\n✅ Одобрено")
    try:
        await bot.send_message(uid, texts.APPLICATION_APPROVED)
        await bot.send_message(uid, texts.CONTINUE_START)
    except Exception:
        pass


    await _notify_curator_request(bot, uid)
    await cb.answer("Одобрено")


async def _notify_curator_request(bot: Bot, worker_uid: int) -> None:

    w = await db.get_worker(worker_uid)
    if not w or not w["curator_id"] or w["curator_status"] != "pending":
        return
    c = await db.get_curator(w["curator_id"])
    if not c:
        return
    if not c["tg_id"]:

        await db.confirm_curator(worker_uid, w["curator_id"])
        return
    nick = w["nickname"] or w["member_no"] or str(worker_uid)
    text = (
        "🎓 <b>Запрос на закрепление</b>\n\n"
        f"Воркер <b>{escape(str(nick))}</b> (id {worker_uid}) хочет закрепиться за вами.\n"
        "Подтвердите или отклоните:"
    )
    try:
        await bot.send_message(c["tg_id"], text,
                               reply_markup=kb.curator_decision(worker_uid))
    except Exception:
        pass


@router.callback_query(F.data.startswith("curok:"))
async def cb_curator_confirm(cb: CallbackQuery, bot: Bot) -> None:

    worker_uid = int(cb.data.split(":")[1])
    me = await db.curator_by_tg(cb.from_user.id)
    if not me:
        await cb.answer("Вы не куратор", show_alert=True)
        return
    ok = await db.confirm_curator(worker_uid, me["id"])
    if not ok:
        await cb.answer("Запрос уже неактуален", show_alert=True)
        return
    await cb.message.edit_text(escape(cb.message.text) + "\n\n✅ Закрепление подтверждено")
    try:
        await bot.send_message(worker_uid,
                               f"✅ Куратор {escape(me['name'])} закрепил вас за собой.")
    except Exception:
        pass
    await cb.answer("Подтверждено")


@router.callback_query(F.data.startswith("curno:"))
async def cb_curator_reject(cb: CallbackQuery, bot: Bot) -> None:

    worker_uid = int(cb.data.split(":")[1])
    me = await db.curator_by_tg(cb.from_user.id)
    if not me:
        await cb.answer("Вы не куратор", show_alert=True)
        return
    ok = await db.reject_curator(worker_uid, me["id"])
    if not ok:
        await cb.answer("Запрос уже неактуален", show_alert=True)
        return
    await cb.message.edit_text(escape(cb.message.text) + "\n\n❌ Закрепление отклонено")
    try:
        await bot.send_message(worker_uid,
                               "❌ Куратор отклонил закрепление. Выберите другого в профиле.")
    except Exception:
        pass
    await cb.answer("Отклонено")


@router.callback_query(F.data.startswith("rej:"))
async def cb_reject(cb: CallbackQuery, bot: Bot) -> None:
    if cb.from_user.id not in config.ADMINS:
        await cb.answer("Нет прав", show_alert=True)
        return
    uid = int(cb.data.split(":")[1])
    await db.set_status(uid, "rejected")
    await cb.message.edit_text(escape(cb.message.text) + "\n\n❌ Отклонено")
    try:
        await bot.send_message(uid, texts.APPLICATION_REJECTED)
    except Exception:
        pass
    await cb.answer("Отклонено")
