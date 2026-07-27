
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .premium_emoji import PremiumEmojiMiddleware


def make_bot(token: str) -> Bot:
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot.session.middleware(PremiumEmojiMiddleware())
    return bot
