

import aiosqlite

from . import config


async def is_authorized(user_id: int) -> bool:
    if user_id in config.OWNERS:
        return True
    try:
        async with aiosqlite.connect(
            f"file:{config.HUB_DB_PATH}?mode=ro", uri=True
        ) as conn:
            async with conn.execute(
                "SELECT approved, role FROM users WHERE user_id=?", (user_id,)
            ) as cur:
                row = await cur.fetchone()
    except Exception:
        return False
    if not row:
        return False
    approved, role = row[0], row[1]
    return approved == 1 or role == "admin"
