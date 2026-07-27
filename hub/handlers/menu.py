
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from shared import db, config
from .. import texts, keyboards as kb
from ..states import Settings

router = Router()


async def _approved(cb: CallbackQuery):
    w = await db.get_worker(cb.from_user.id)
    if w is None or w["status"] != "approved":
        await cb.answer(texts.NO_ACCESS, show_alert=True)
        return None
    return w


async def _edit(cb: CallbackQuery, text: str, markup, **kw) -> None:

    try:
        await cb.message.edit_text(text, reply_markup=markup, **kw)
    except Exception:
        await cb.message.answer(text, reply_markup=markup, **kw)


def _ref(bot_username: str, worker_id: int) -> str:
    return f"https://t.me/{bot_username}?start={worker_id}"


@router.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not await _approved(cb):
        return
    await _edit(cb, texts.GREETING, kb.main_menu())
    await cb.answer()


@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery) -> None:
    stats = await db.global_stats()
    await _edit(cb, texts.about(stats), kb.about())
    await cb.answer()


@router.callback_query(F.data == "top")
async def cb_top(cb: CallbackQuery) -> None:
    rows = await db.top_workers(10)
    lines = [texts.TOP_TITLE, ""]
    if not rows:
        lines.append("Пока пусто.")
    for i, r in enumerate(rows, 1):
        name = r["nickname"] or r["member_no"] or str(r["user_id"])
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        lines.append(f"{medal} {name} — {r['total']:,}₽".replace(",", " "))
    await _edit(cb, "\n".join(lines), kb.about())
    await cb.answer()


@router.callback_query(F.data == "profile")
async def cb_profile(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    w = await _approved(cb)
    if not w:
        return
    sums = await db.profit_sums(w["user_id"])
    dtc = await db.dtc_balance(w["user_id"])
    await _edit(cb, texts.profile(w, sums, dtc), kb.profile())
    await cb.answer()


@router.callback_query(F.data == "curators")
async def cb_curators(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    rows = await db.list_curators()
    await _edit(cb, texts.CURATORS_TITLE, kb.curators(rows))
    await cb.answer()


@router.callback_query(F.data.startswith("cur:"))
async def cb_pick_curator(cb: CallbackQuery, bot: Bot) -> None:
    w = await _approved(cb)
    if not w:
        return
    cid = int(cb.data.split(":")[1])
    c = await db.get_curator(cid)
    if not c:
        await cb.answer("Куратор не найден", show_alert=True)
        return

    await db.request_curator(cb.from_user.id, cid)

    if not c["tg_id"]:

        await db.confirm_curator(cb.from_user.id, cid)
        await cb.answer(f"✅ Вы закреплены за {c['name']} [{c['direction']}]", show_alert=True)
        return


    nick = w["nickname"] or w["member_no"] or str(cb.from_user.id)
    try:
        await bot.send_message(
            c["tg_id"],
            "🎓 <b>Запрос на закрепление</b>\n\n"
            f"Воркер <b>{nick}</b> (id {cb.from_user.id}) хочет закрепиться за вами.",
            reply_markup=kb.curator_decision(cb.from_user.id),
        )
    except Exception:
        pass
    await cb.answer(f"⏳ Запрос отправлен куратору {c['name']}. Ожидайте подтверждения.",
                    show_alert=True)


@router.callback_query(F.data == "settings")
async def cb_settings(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    await _edit(cb, texts.SETTINGS_TITLE, kb.settings())
    await cb.answer()


@router.callback_query(F.data == "set_nick")
async def cb_set_nick(cb: CallbackQuery, state: FSMContext) -> None:
    if not await _approved(cb):
        return
    await state.set_state(Settings.nickname)
    await cb.message.answer(texts.ASK_NICKNAME, reply_markup=kb.cancel())
    await cb.answer()


@router.message(Settings.nickname)
async def st_nickname(message: Message, state: FSMContext) -> None:
    nick = (message.text or "").strip()[:32]
    await db.set_nickname(message.from_user.id, nick)
    await state.clear()
    await message.answer(texts.NICKNAME_SET.format(nick=nick))
    await message.answer(texts.GREETING, reply_markup=kb.main_menu())


@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    bal = await db.dtc_balance(cb.from_user.id)
    await _edit(cb, texts.SHOP.format(balance=bal), kb.shop())
    await cb.answer()


@router.callback_query(F.data.startswith("shopcat:"))
async def cb_shopcat(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    idx = int(cb.data.split(":")[1])
    icon, name, price = kb.SHOP_CATS[idx]
    bal = await db.dtc_balance(cb.from_user.id)
    status = "🪙 Хватает баланса ✅" if bal >= price else "❌ Недостаточно DTC"
    await _edit(cb, texts.SHOP_ITEM.format(icon=icon, name=name, price=price, status=status),
                kb.shop_item(idx))
    await cb.answer()


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    idx = int(cb.data.split(":")[1])
    _icon, name, price = kb.SHOP_CATS[idx]
    bal = await db.dtc_balance(cb.from_user.id)
    if bal < price:
        await cb.answer(texts.SHOP_NOT_ENOUGH, show_alert=True)
        return
    await db.dtc_add(cb.from_user.id, -price, f"shop:{name}")
    await cb.answer(texts.SHOP_BOUGHT.format(price=price), show_alert=True)


@router.callback_query(F.data == "bots")
async def cb_bots(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    await _edit(cb, texts.BOTS_MENU, kb.bots())
    await cb.answer()


@router.callback_query(F.data == "trade")
async def cb_trade(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    link = _ref(config.TRADE_BOT_USERNAME, cb.from_user.id)
    await _edit(cb, texts.trade_section(link), kb.trade_section())
    await cb.answer()


@router.callback_query(F.data == "escort")
async def cb_escort(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    link = _ref(config.ESCORT_BOT_USERNAME, cb.from_user.id)
    await _edit(cb, texts.escort_section(link), kb.escort_section())
    await cb.answer()


@router.callback_query(F.data == "tools")
async def cb_tools(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    await _edit(cb, texts.TOOLS_MENU, kb.tools())
    await cb.answer()


@router.callback_query(F.data == "card")
async def cb_card(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    await _edit(cb, texts.CARD, kb.card())
    await cb.answer()


@router.callback_query(F.data == "get_card")
async def cb_get_card(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return

    req = "2200 7001 0000 0000 (DEMO / фин.отдел)"
    await db.conn().execute(
        "INSERT INTO card_requests(user_id, status, requisites, created_at) VALUES(?,?,?,?)",
        (cb.from_user.id, "issued", req, db.now()),
    )
    await db.conn().commit()
    await cb.answer("💳 Реквизиты выданы ", show_alert=True)
    await cb.message.answer(texts.CARD_ISSUED.format(req=req), parse_mode="HTML")


@router.callback_query(F.data == "draw")
async def cb_draw(cb: CallbackQuery) -> None:
    if not await _approved(cb):
        return
    await _edit(cb, texts.DRAW, kb.draw())
    await cb.answer()
