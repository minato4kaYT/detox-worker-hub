
import random

from shared import db

ESCORT_SCHEMA = """
CREATE TABLE IF NOT EXISTS escort_settings (
    worker_id     INTEGER PRIMARY KEY,
    code          TEXT,
    min_prepay    INTEGER DEFAULT 3000,    -- мин. предоплата за бронь встречи
    vip_price     INTEGER DEFAULT 10000,   -- стоимость VIP-доступа
    welcome_bonus INTEGER DEFAULT 500,     -- приветственный «бонус» на счёт
    refund_reject INTEGER DEFAULT 1        -- авто-отклонение возврата предоплаты
);

CREATE TABLE IF NOT EXISTS escort_mammoths (
    chat_id    INTEGER PRIMARY KEY,
    worker_id  INTEGER,
    username   TEXT,
    name       TEXT,
    balance    REAL DEFAULT 0,             -- «нарисованный» бонусный баланс
    deposited  REAL DEFAULT 0,             -- реально занесено (= профит воркера)
    status     TEXT DEFAULT 'active',
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS escort_ops (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER,
    worker_id  INTEGER,
    kind       TEXT,                       -- prepay|vip|refund
    amount     REAL,
    result     TEXT,
    created_at INTEGER
);

CREATE TABLE IF NOT EXISTS escort_promo (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER,
    code      TEXT,
    amount    REAL,
    uses_left INTEGER DEFAULT 1
);
"""


MODELS = [
    {"id": "vika",  "name": "Вика, 22",   "city": "Москва",        "tags": "модель, рост 175"},
    {"id": "alina", "name": "Алина, 24",  "city": "Санкт-Петербург", "tags": "фитнес, TDS"},
    {"id": "sofia", "name": "София, 21",  "city": "Москва",        "tags": "студентка, брюнетка"},
    {"id": "kira",  "name": "Кира, 26",   "city": "Казань",        "tags": "инста-модель, блонди"},
    {"id": "milana","name": "Милана, 23", "city": "Сочи",          "tags": "танцовщица"},
]


def model_by_id(mid: str):
    for m in MODELS:
        if m["id"] == mid:
            return m
    return None


async def init_schema() -> None:
    await db.conn().executescript(ESCORT_SCHEMA)
    await db.conn().commit()


def gen_code() -> str:
    return str(random.randint(100000, 999999))


async def get_settings(worker_id: int):
    cur = await db.conn().execute("SELECT * FROM escort_settings WHERE worker_id=?", (worker_id,))
    row = await cur.fetchone()
    if row is None:
        await db.conn().execute(
            "INSERT INTO escort_settings(worker_id, code) VALUES(?,?)", (worker_id, gen_code())
        )
        await db.conn().commit()
        cur = await db.conn().execute("SELECT * FROM escort_settings WHERE worker_id=?", (worker_id,))
        row = await cur.fetchone()
    return row


async def worker_by_code(code: str) -> int | None:
    cur = await db.conn().execute("SELECT worker_id FROM escort_settings WHERE code=?", (code,))
    row = await cur.fetchone()
    return row["worker_id"] if row else None


async def update_setting(worker_id: int, field: str, value) -> None:
    assert field in {"min_prepay", "vip_price", "welcome_bonus", "refund_reject"}
    await db.conn().execute(
        f"UPDATE escort_settings SET {field}=? WHERE worker_id=?", (value, worker_id)
    )
    await db.conn().commit()


async def get_mammoth(chat_id: int):
    cur = await db.conn().execute("SELECT * FROM escort_mammoths WHERE chat_id=?", (chat_id,))
    return await cur.fetchone()


async def register_mammoth(chat_id: int, worker_id: int, username, name) -> bool:
    ex = await get_mammoth(chat_id)
    if ex:
        return False
    await db.conn().execute(
        """INSERT INTO escort_mammoths(chat_id, worker_id, username, name, created_at)
           VALUES(?,?,?,?,?)""",
        (chat_id, worker_id, username, name, db.now()),
    )
    await db.conn().commit()
    await db.link_mammoth(worker_id, chat_id, "escort")
    return True


async def set_balance(chat_id: int, balance: float) -> None:
    await db.conn().execute("UPDATE escort_mammoths SET balance=? WHERE chat_id=?", (balance, chat_id))
    await db.conn().commit()


async def add_prepay(chat_id: int, worker_id: int, amount: float) -> None:

    await db.conn().execute(
        "UPDATE escort_mammoths SET deposited=deposited+? WHERE chat_id=?",
        (amount, chat_id),
    )
    await log_op(chat_id, worker_id, "prepay", amount, "ok")
    await db.conn().commit()
    await db.add_profit(worker_id, chat_id, "escort", int(amount))


async def log_op(chat_id: int, worker_id: int, kind: str, amount: float, result: str) -> None:
    await db.conn().execute(
        "INSERT INTO escort_ops(chat_id, worker_id, kind, amount, result, created_at) VALUES(?,?,?,?,?,?)",
        (chat_id, worker_id, kind, amount, result, db.now()),
    )
    await db.conn().commit()


async def mammoths_of(worker_id: int):
    cur = await db.conn().execute(
        "SELECT * FROM escort_mammoths WHERE worker_id=? ORDER BY created_at DESC", (worker_id,)
    )
    return await cur.fetchall()


async def worker_stats(worker_id: int) -> dict:
    cur = await db.conn().execute(
        """SELECT COUNT(*) AS c, COALESCE(SUM(deposited),0) AS s
           FROM escort_mammoths WHERE worker_id=?""",
        (worker_id,),
    )
    row = await cur.fetchone()
    return {"count": row["c"], "sum": row["s"]}


async def add_promo(worker_id: int, code: str, amount: float, uses: int) -> None:
    await db.conn().execute(
        "INSERT INTO escort_promo(worker_id, code, amount, uses_left) VALUES(?,?,?,?)",
        (worker_id, code, amount, uses),
    )
    await db.conn().commit()


async def redeem_promo(code: str):
    cur = await db.conn().execute(
        "SELECT * FROM escort_promo WHERE code=? AND uses_left>0", (code,)
    )
    row = await cur.fetchone()
    if not row:
        return None
    await db.conn().execute("UPDATE escort_promo SET uses_left=uses_left-1 WHERE id=?", (row["id"],))
    await db.conn().commit()
    return row
