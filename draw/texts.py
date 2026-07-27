

from datetime import datetime

from . import ddb


def menu(name: str) -> str:
    kinds = " · ".join(t["brand"] for t in ddb.TEMPLATES.values())
    return (
        f"🖼️ Отрисовщик, {name}\n"
        "└ Генератор чеков для создания визуальных образцов\n\n"
        f"Доступные шаблоны: {kinds}\n\n"
        "Выберите тип транзакции ниже и создайте визуальный образец."
    )


def ask_amount(kind: str) -> str:
    tpl = ddb.template(kind) or ddb.TEMPLATES["card"]
    return (
        f"{tpl['emoji']} {tpl['menu']}\n\n"
        f"Введите сумму перевода в {tpl['unit']} (например: 15000):"
    )


def bad_amount() -> str:
    return "❌ Введите положительное число, например 12500."


def ask_sender() -> str:
    return "🧾 Введите ФИО отправителя (как показать в «чеке»), например: Иванов Иван Иванович."


def stats(kind_counts: dict, s: dict) -> str:
    by_kind = "\n".join(
        f"├︎ {ddb.TEMPLATES[k]['brand']}: {kind_counts.get(k, 0)}"
        for k in ddb.TEMPLATES
    ) or "├︎ —"
    return (
        "📊 Статистика отрисовок \n\n"
        f"🧾 Всего чеков: {s['count']}\n"
        f"💰 Суммарный «оборот»: {s['sum']:,.0f}\n\n"
        "По шаблонам:\n"
        f"{by_kind}"
    ).replace(",", " ")


def history(rows) -> str:
    if not rows:
        return "🧾 История пуста — вы ещё не сформировали ни одного образца."
    lines = ["🧾 Последние отрисовки :\n"]
    for r in rows:
        tpl = ddb.template(r["kind"]) or {"emoji": "•", "unit": ""}
        when = datetime.fromtimestamp(r["created_at"]).strftime("%d.%m %H:%M")
        lines.append(
            f"{tpl['emoji']} {r['amount']:,.0f} {tpl['unit']} → {r['recipient'][:24]}  ·  {when}"
        )
    return "\n".join(lines).replace(",", " ")
