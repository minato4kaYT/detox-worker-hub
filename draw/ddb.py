

import random

from shared import db

DRAW_SCHEMA = """
CREATE TABLE IF NOT EXISTS draw_ops (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id  INTEGER,
    kind       TEXT,        -- card|sbp|crypto
    amount     REAL,
    recipient  TEXT,
    created_at INTEGER
);
"""


TEMPLATES = {
    "card": {
        "emoji": "💳", "menu": "Перевод на карту",
        "title": "OnyxBank Online", "brand": "OnyxBank",
        "accent": (33, 150, 83), "unit": "₽",
        "recipient_label": "Получатель",
        "ask": "Введите получателя (имя и/или маскированную карта •• 1234):",
    },
    "sbp": {
        "emoji": "🏦", "menu": "СБП · перевод по телефону",
        "title": "Система быстрых платежей", "brand": "СБП",
        "accent": (108, 58, 168), "unit": "₽",
        "recipient_label": "Телефон получателя",
        "ask": "Введите номер телефона получателя (например +7 900 000-00-00):",
    },
    "crypto": {
        "emoji": "💎", "menu": "Крипто-перевод TON",
        "title": "TON Space", "brand": "TON",
        "accent": (0, 136, 204), "unit": "TON",
        "recipient_label": "Кошелёк",
        "ask": "Введите адрес кошелька получателя (UQ...):",
    },
}


def template(kind: str) -> dict | None:
    return TEMPLATES.get(kind)


async def init_schema() -> None:
    await db.conn().executescript(DRAW_SCHEMA)
    await db.conn().commit()


def gen_ref() -> str:
    return f"{random.randint(10**11, 10**12 - 1)}"


async def log_draw(worker_id: int, kind: str, amount: float, recipient: str) -> None:
    await db.conn().execute(
        "INSERT INTO draw_ops(worker_id, kind, amount, recipient, created_at) VALUES(?,?,?,?,?)",
        (worker_id, kind, amount, recipient, db.now()),
    )
    await db.conn().commit()


async def worker_stats(worker_id: int) -> dict:
    cur = await db.conn().execute(
        "SELECT COUNT(*) AS c, COALESCE(SUM(amount),0) AS s FROM draw_ops WHERE worker_id=?",
        (worker_id,),
    )
    row = await cur.fetchone()
    return {"count": row["c"], "sum": row["s"]}


async def last_draws(worker_id: int, limit: int = 10):
    cur = await db.conn().execute(
        "SELECT * FROM draw_ops WHERE worker_id=? ORDER BY id DESC LIMIT ?",
        (worker_id, limit),
    )
    return await cur.fetchall()
