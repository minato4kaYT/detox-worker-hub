
import asyncio
import logging

from aiogram import Dispatcher

from shared import db, config
from shared.botfactory import make_bot
from . import edb
from .handlers import victim, worker

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config.require_token(config.ESCORT_TOKEN, "ESCORT_TOKEN")
    await db.init()
    await edb.init_schema()

    bot = make_bot(config.ESCORT_TOKEN)
    dp = Dispatcher()

    dp.include_router(worker.router)
    dp.include_router(victim.router)

    logging.info("DETOX escort bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
