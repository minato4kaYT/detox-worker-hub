
import asyncio
import logging

from aiogram import Dispatcher

from shared import db, config
from shared.botfactory import make_bot
from . import tdb
from .handlers import victim, worker

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config.require_token(config.TRADE_TOKEN, "TRADE_TOKEN")
    await db.init()
    await tdb.init_schema()

    bot = make_bot(config.TRADE_TOKEN)
    dp = Dispatcher()

    dp.include_router(worker.router)
    dp.include_router(victim.router)

    logging.info("DETOX trade bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
