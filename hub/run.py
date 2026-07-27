

import asyncio
import logging

from aiogram import Dispatcher

from shared import db, config
from shared.botfactory import make_bot
from .handlers import onboarding, menu

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    config.require_token(config.HUB_TOKEN, "HUB_TOKEN")
    await db.init()

    bot = make_bot(config.HUB_TOKEN)
    dp = Dispatcher()
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)

    logging.info("OnyxHub bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
