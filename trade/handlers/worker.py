
from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from shared import db, hubauth
from .. import texts, keyboards as kb, tdb
from ..states import Worker

router = Router()

FIELD_LABELS = {
    "luck": "Удача (%)", "coef_min": "Коэффициент min", "coef_max": "Коэффициент max",
    "min_deal": "Мин. сделка", "min_withdraw": "Мин. вывод", "min_deposit": "Мин. пополнение",
}


async def _guard(user_id: int) -> bool:

    return await hubauth.is_authorized(user_id)


async def _panel_text(worker_id: int, bot_username: str) -> str:
    s = await tdb.get_settings(worker_id)
    stats = await tdb.worker_stats(worker_id)
    return texts.worker_panel(s, stats).replace("{bot}", bot_username)


@router.message(Command("worker"))
async def cmd_worker(message: Message, bot: Bot) -> None:
    if not await _guard(message.from_user.id):
        await message.answer("⛔️ Доступ только для одобренных воркеров панели @aOnyxPay_Bot.")
        return
    me = await bot.get_me()
    await message.answer(await _panel_text(message.from_user.id, me.username),
                         reply_markup=kb.worker())


@router.callback_query(F.data == "w_menu")
async def w_menu(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    me = await bot.get_me()
    await cb.message.edit_text(await _panel_text(cb.from_user.id, me.username),
                               reply_markup=kb.worker())
    await cb.answer()


@router.callback_query(F.data == "w_ref")
async def w_ref(cb: CallbackQuery, bot: Bot) -> None:
    s = await tdb.get_settings(cb.from_user.id)
    me = await bot.get_me()
    await cb.answer()
    await cb.message.answer(f"🔗 Ваша реф. ссылка:\nhttps://t.me/{me.username}?start={s['code']}")


@router.callback_query(F.data == "w_mammoths")
async def w_mammoths(cb: CallbackQuery) -> None:
    rows = await tdb.mammoths_of(cb.from_user.id)
    if not rows:
        await cb.answer("Мамонтов пока нет.", show_alert=True)
        return
    lines = ["🦣 Ваши мамонты:\n"]
    for m in rows[:30]:
        lines.append(f"• {escape(m['name'] or '')} (@{escape(m['username'] or '—')}) | id {m['chat_id']} | "
                     f"внесено {m['deposited']:.0f} | /em {m['chat_id']}")
    await cb.message.edit_text("\n".join(lines), reply_markup=kb.back_worker())
    await cb.answer()


@router.callback_query(F.data == "w_stats")
async def w_stats(cb: CallbackQuery) -> None:
    stats = await tdb.worker_stats(cb.from_user.id)
    sums = await db.profit_sums(cb.from_user.id)
    await cb.message.edit_text(
        "📊 Статистика трейда:\n\n"
        f"🦣 Мамонтов: {stats['count']}\n"
        f"💰 Всего внесено: {stats['sum']:.0f} USDT\n\n"
        f"💸 Профит (₽ в хабе): день {sums['day']:,} / месяц {sums['month']:,} / всё {sums['all']:,}".replace(",", " "),
        reply_markup=kb.back_worker())
    await cb.answer()


@router.callback_query(F.data == "w_settings")
async def w_settings(cb: CallbackQuery) -> None:
    s = await tdb.get_settings(cb.from_user.id)
    await cb.message.edit_text(texts.settings(s), reply_markup=kb.settings())
    await cb.answer()


@router.callback_query(F.data == "ws_toggle")
async def ws_toggle(cb: CallbackQuery) -> None:
    s = await tdb.get_settings(cb.from_user.id)
    await tdb.update_setting(cb.from_user.id, "auto_reject", 0 if s["auto_reject"] else 1)
    s = await tdb.get_settings(cb.from_user.id)
    await cb.message.edit_text(texts.settings(s), reply_markup=kb.settings())
    await cb.answer("Переключено")


@router.callback_query(F.data.startswith("ws:"))
async def ws_field(cb: CallbackQuery, state: FSMContext) -> None:
    field = cb.data.split(":")[1]
    await state.set_state(Worker.set_field)
    await state.update_data(field=field)
    await cb.message.answer(f"Введите новое значение — {FIELD_LABELS[field]}:")
    await cb.answer()


@router.message(Worker.set_field)
async def set_field(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data["field"]
    txt = (message.text or "").replace(",", ".").strip()
    try:
        value = float(txt) if field in ("luck", "coef_min", "coef_max") else int(txt)
    except ValueError:
        await message.answer("Введите число.")
        return
    if field == "luck":
        value = max(0.0, min(100.0, value))
    await tdb.update_setting(message.from_user.id, field, value)
    await state.clear()
    s = await tdb.get_settings(message.from_user.id)
    await message.answer("✅ Сохранено.\n\n" + texts.settings(s), reply_markup=kb.settings())


@router.callback_query(F.data == "w_promo")
async def w_promo(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Worker.promo_amount)
    await cb.message.answer("🎟️ Введите номинал промокода (USDT):")
    await cb.answer()


@router.message(Worker.promo_amount)
async def make_promo(message: Message, state: FSMContext) -> None:
    txt = (message.text or "").replace(",", ".").strip()
    try:
        amount = float(txt)
    except ValueError:
        await message.answer("Введите число.")
        return
    code = tdb.gen_code()
    await tdb.add_promo(message.from_user.id, code, amount, uses=1)
    await state.clear()
    await message.answer(f"✅ Промокод создан:\n<code>{code}</code> на {amount:.0f} USDT",
                         parse_mode="HTML", reply_markup=kb.back_worker())


@router.callback_query(F.data == "w_broadcast")
async def w_broadcast(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Worker.broadcast)
    await cb.message.answer("📢 Пришлите текст рассылки для ваших мамонтов:")
    await cb.answer()


@router.message(Worker.broadcast)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    rows = await tdb.mammoths_of(message.from_user.id)
    sent = 0
    body = escape(message.text or "")
    for m in rows:
        try:
            await bot.send_message(m["chat_id"], body)
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ Рассылка отправлена: {sent}/{len(rows)}", reply_markup=kb.back_worker())


@router.message(Command("em"))
async def cmd_em(message: Message, command: CommandObject) -> None:
    if not await _guard(message.from_user.id):
        return
    arg = (command.args or "").strip()
    if not arg.isdigit():
        await message.answer("Использование: /em <chat_id>")
        return
    m = await tdb.get_mammoth(int(arg))
    if not m or m["worker_id"] != message.from_user.id:
        await message.answer("Мамонт не найден среди ваших.")
        return
    await message.answer(
        f"🦣 Управление мамонтом\n\n"
        f"Имя: {escape(m['name'] or '')} (@{escape(m['username'] or '—')})\n"
        f"ChatID: {m['chat_id']}\n"
        f"💰 Баланс: {m['balance']:.2f} USDT\n"
        f"📥 Внесено: {m['deposited']:.2f} USDT\n"
        f"Статус: {m['status']}"
    )
