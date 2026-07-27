

import asyncio

from shared import db, config


_ADMIN0 = config.ADMINS[0] if config.ADMINS else None
CURATORS = [
    ("TheGodscm", "Escort", _ADMIN0),
    ("blessscm", "Трейд", None),
    ("Пешка", "Шантаж", None),
    ("Chrome", "Escort", None),
]


async def main() -> None:
    await db.init()

    cur = await db.conn().execute("SELECT COUNT(*) AS c FROM curators")
    if (await cur.fetchone())["c"] == 0:
        for name, direction, tg_id in CURATORS:
            await db.conn().execute(
                "INSERT INTO curators(name, direction, tg_id) VALUES(?,?,?)",
                (name, direction, tg_id),
            )
        await db.conn().commit()
        print(f"seeded {len(CURATORS)} curators")


    await db.set_setting("base_profit_count", "1758")
    await db.set_setting("base_profit_sum", "16456109")
    print("seeded base stats")
    await db.close()
    print("done")


if __name__ == "__main__":
    asyncio.run(main())
