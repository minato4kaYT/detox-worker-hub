

import time
import random
import aiosqlite

from . import config

_db: aiosqlite.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    created_at  INTEGER
);

-- Воркеры хаба (анкета -> модерация -> доступ)
CREATE TABLE IF NOT EXISTS workers (
    user_id       INTEGER PRIMARY KEY,
    member_no     TEXT,
    nickname      TEXT,
    lvl           INTEGER DEFAULT 0,
    curator_id    INTEGER,
    curator_status TEXT DEFAULT 'none',      -- none|pending|confirmed (подтверждение куратором)
    status        TEXT DEFAULT 'none',       -- none|pending|approved|rejected (заявка в команду)
    hours         INTEGER,
    source        TEXT,
    experience    TEXT,
    applied_at    INTEGER,
    approved_at   INTEGER
);

-- Кураторы (справочник)
CREATE TABLE IF NOT EXISTS curators (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT,
    direction TEXT,
    tg_id     INTEGER                        -- telegram id куратора (для подтверждения закрепления)
);

-- Реферальная привязка жертвы к воркеру (общая для саб-ботов)
CREATE TABLE IF NOT EXISTS referrals (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id  INTEGER,
    mammoth_id INTEGER,
    bot        TEXT,                          -- trade|escort
    created_at INTEGER,
    UNIQUE(mammoth_id, bot)
);

-- Профиты (учёт заработка воркера)
CREATE TABLE IF NOT EXISTS profits (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id          INTEGER,
    mammoth_id         INTEGER,
    bot                TEXT,
    amount_rub         INTEGER,
    dtc                REAL,
    curator_id         INTEGER,           -- куратор, получивший комиссию (если был)
    curator_commission INTEGER DEFAULT 0, -- 15% с первых 5 профитов воркера
    created_at         INTEGER
);

-- Леджер DetoxCoin
CREATE TABLE IF NOT EXISTS dtc_ledger (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    delta      REAL,
    reason     TEXT,
    created_at INTEGER
);

-- Глобальные настройки/статы (key-value)
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- Заявки на реквизиты (Карта / Фин.отдел)
CREATE TABLE IF NOT EXISTS card_requests (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    status     TEXT DEFAULT 'pending',        -- pending|issued|rejected
    requisites TEXT,
    created_at INTEGER
);
"""


async def init() -> None:
    global _db
    _db = await aiosqlite.connect(config.DB_PATH)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL;")
    await _db.execute("PRAGMA foreign_keys=ON;")
    await _db.executescript(SCHEMA)
    await _migrate()
    await _db.commit()


async def _migrate() -> None:

    alters = [
        "ALTER TABLE workers ADD COLUMN curator_status TEXT DEFAULT 'none'",
        "ALTER TABLE curators ADD COLUMN tg_id INTEGER",
        "ALTER TABLE profits ADD COLUMN curator_id INTEGER",
        "ALTER TABLE profits ADD COLUMN curator_commission INTEGER DEFAULT 0",
    ]
    for sql in alters:
        try:
            await _db.execute(sql)
        except Exception:
            pass


async def close() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


def conn() -> aiosqlite.Connection:
    assert _db is not None, "db.init() не вызван"
    return _db


def now() -> int:
    return int(time.time())


async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> None:
    await conn().execute(
        """INSERT INTO users(user_id, username, first_name, created_at)
           VALUES(?,?,?,?)
           ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,
                                              first_name=excluded.first_name""",
        (user_id, username, first_name, now()),
    )
    await conn().commit()


async def get_worker(user_id: int) -> aiosqlite.Row | None:
    cur = await conn().execute("SELECT * FROM workers WHERE user_id=?", (user_id,))
    return await cur.fetchone()


async def create_application(user_id: int, hours: int, source: str, experience: str) -> None:
    await conn().execute(
        """INSERT INTO workers(user_id, status, hours, source, experience, applied_at, member_no)
           VALUES(?, 'pending', ?, ?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET status='pending', hours=excluded.hours,
               source=excluded.source, experience=excluded.experience, applied_at=excluded.applied_at""",
        (user_id, hours, source, experience, now(), _member_no()),
    )
    await conn().commit()


def _member_no() -> str:
    return f"#member{random.randint(10000, 99999)}"


async def set_status(user_id: int, status: str) -> None:
    ts = now() if status == "approved" else None
    await conn().execute(
        "UPDATE workers SET status=?, approved_at=COALESCE(?, approved_at) WHERE user_id=?",
        (status, ts, user_id),
    )
    await conn().commit()


async def set_nickname(user_id: int, nickname: str) -> None:
    await conn().execute("UPDATE workers SET nickname=? WHERE user_id=?", (nickname, user_id))
    await conn().commit()


async def set_curator(user_id: int, curator_id: int) -> None:

    await conn().execute(
        "UPDATE workers SET curator_id=?, curator_status='confirmed' WHERE user_id=?",
        (curator_id, user_id),
    )
    await conn().commit()


async def request_curator(user_id: int, curator_id: int) -> None:

    await conn().execute(
        "UPDATE workers SET curator_id=?, curator_status='pending' WHERE user_id=?",
        (curator_id, user_id),
    )
    await conn().commit()


async def confirm_curator(user_id: int, curator_id: int) -> bool:

    cur = await conn().execute(
        "SELECT curator_id, curator_status FROM workers WHERE user_id=?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or row["curator_id"] != curator_id or row["curator_status"] != "pending":
        return False
    await conn().execute(
        "UPDATE workers SET curator_status='confirmed' WHERE user_id=?", (user_id,)
    )
    await conn().commit()
    return True


async def reject_curator(user_id: int, curator_id: int) -> bool:

    cur = await conn().execute(
        "SELECT curator_id, curator_status FROM workers WHERE user_id=?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or row["curator_id"] != curator_id or row["curator_status"] != "pending":
        return False
    await conn().execute(
        "UPDATE workers SET curator_id=NULL, curator_status='none' WHERE user_id=?",
        (user_id,),
    )
    await conn().commit()
    return True


async def list_pending() -> list[aiosqlite.Row]:
    cur = await conn().execute(
        "SELECT * FROM workers WHERE status='pending' ORDER BY applied_at ASC"
    )
    return await cur.fetchall()


async def list_curators() -> list[aiosqlite.Row]:
    cur = await conn().execute("SELECT * FROM curators ORDER BY id")
    return await cur.fetchall()


async def get_curator(cid: int) -> aiosqlite.Row | None:
    cur = await conn().execute("SELECT * FROM curators WHERE id=?", (cid,))
    return await cur.fetchone()


async def curator_by_tg(tg_id: int) -> aiosqlite.Row | None:
    cur = await conn().execute("SELECT * FROM curators WHERE tg_id=?", (tg_id,))
    return await cur.fetchone()


async def dtc_balance(user_id: int) -> float:
    cur = await conn().execute(
        "SELECT COALESCE(SUM(delta),0) AS b FROM dtc_ledger WHERE user_id=?", (user_id,)
    )
    row = await cur.fetchone()
    return round(row["b"], 2)


async def dtc_add(user_id: int, delta: float, reason: str) -> None:
    await conn().execute(
        "INSERT INTO dtc_ledger(user_id, delta, reason, created_at) VALUES(?,?,?,?)",
        (user_id, delta, reason, now()),
    )
    await conn().commit()


CURATOR_PCT = 0.15
CURATOR_FIRST_N = 5


async def add_profit(worker_id: int, mammoth_id: int, bot: str, amount_rub: int) -> float:
    dtc = round(amount_rub / 1000 * config.DTC_PER_1000_RUB, 2)


    curator_id = None
    commission = 0
    w = await get_worker(worker_id)
    if w and w["curator_id"] and w["curator_status"] == "confirmed":
        cur = await conn().execute(
            "SELECT COUNT(*) AS c FROM profits WHERE worker_id=?", (worker_id,)
        )
        profit_no = (await cur.fetchone())["c"] + 1
        if profit_no <= CURATOR_FIRST_N:
            curator_id = w["curator_id"]
            commission = round(amount_rub * CURATOR_PCT)

    await conn().execute(
        """INSERT INTO profits(worker_id, mammoth_id, bot, amount_rub, dtc,
                               curator_id, curator_commission, created_at)
           VALUES(?,?,?,?,?,?,?,?)""",
        (worker_id, mammoth_id, bot, amount_rub, dtc, curator_id, commission, now()),
    )
    await conn().execute(
        "INSERT INTO dtc_ledger(user_id, delta, reason, created_at) VALUES(?,?,?,?)",
        (worker_id, dtc, f"profit:{bot}", now()),
    )


    if curator_id and commission > 0:
        c = await get_curator(curator_id)
        if c and c["tg_id"]:
            cur_dtc = round(commission / 1000 * config.DTC_PER_1000_RUB, 2)
            await conn().execute(
                "INSERT INTO dtc_ledger(user_id, delta, reason, created_at) VALUES(?,?,?,?)",
                (c["tg_id"], cur_dtc, f"curator_commission:{worker_id}", now()),
            )

    await conn().commit()
    return dtc


async def profit_sums(worker_id: int) -> dict:
    t = now()
    day = t - 86400
    month = t - 30 * 86400
    cur = await conn().execute(
        """SELECT
             COALESCE(SUM(CASE WHEN created_at>=? THEN amount_rub END),0) AS d,
             COALESCE(SUM(CASE WHEN created_at>=? THEN amount_rub END),0) AS m,
             COALESCE(SUM(amount_rub),0) AS a
           FROM profits WHERE worker_id=?""",
        (day, month, worker_id),
    )
    row = await cur.fetchone()
    return {"day": row["d"], "month": row["m"], "all": row["a"]}


async def global_stats() -> dict:
    cur = await conn().execute(
        "SELECT COUNT(*) AS c, COALESCE(SUM(amount_rub),0) AS s FROM profits"
    )
    row = await cur.fetchone()
    base_c = int(await get_setting("base_profit_count", "0"))
    base_s = int(await get_setting("base_profit_sum", "0"))
    return {"count": row["c"] + base_c, "sum": row["s"] + base_s}


async def top_workers(limit: int = 10) -> list[aiosqlite.Row]:
    cur = await conn().execute(
        """SELECT w.user_id, w.nickname, w.member_no,
                  COALESCE(SUM(p.amount_rub),0) AS total
           FROM workers w LEFT JOIN profits p ON p.worker_id=w.user_id
           WHERE w.status='approved'
           GROUP BY w.user_id ORDER BY total DESC LIMIT ?""",
        (limit,),
    )
    return await cur.fetchall()


async def link_mammoth(worker_id: int, mammoth_id: int, bot: str) -> bool:
    try:
        await conn().execute(
            "INSERT INTO referrals(worker_id, mammoth_id, bot, created_at) VALUES(?,?,?,?)",
            (worker_id, mammoth_id, bot, now()),
        )
        await conn().commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def mammoths_of(worker_id: int, bot: str | None = None) -> list[aiosqlite.Row]:
    q = "SELECT * FROM referrals WHERE worker_id=?"
    args: list = [worker_id]
    if bot:
        q += " AND bot=?"
        args.append(bot)
    cur = await conn().execute(q + " ORDER BY created_at DESC", args)
    return await cur.fetchall()


async def get_setting(key: str, default: str = "") -> str:
    cur = await conn().execute("SELECT value FROM settings WHERE key=?", (key,))
    row = await cur.fetchone()
    return row["value"] if row else default


async def set_setting(key: str, value: str) -> None:
    await conn().execute(
        "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    await conn().commit()
