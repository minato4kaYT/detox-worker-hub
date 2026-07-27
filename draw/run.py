
import asyncio
import logging

from aiogram import Dispatcher

from shared import db, config
from shared.botfactory import make_bot
from . import ddb
from .handlers import worker

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config.require_token(config.DRAW_TOKEN, "DRAW_TOKEN")
    await db.init()
    await ddb.init_schema()

    bot = make_bot(config.DRAW_TOKEN)
    dp = Dispatcher()
    dp.include_router(worker.router)

    logging.info("DETOX draw bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
