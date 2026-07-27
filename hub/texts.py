
from html import escape
from shared import config


ASK_HOURS = "⏰ Сколько времени Вы готовы уделять работе?\n └ Пример: 3 (время в часах)."
ERR_HOURS = "Время должно быть числом ❗️"
ASK_SOURCE = "💁‍♂️ Откуда Вы узнали о нас?\n  └ Если от друга, укажите его @username."
ASK_EXPERIENCE = "🧠 Был ли у вас опыт в похожем проекте?\n  └ Если да, укажите какой."
APPLICATION_SENT = "✅ Ваша заявка отправлена, ожидайте ответа!"
APPLICATION_APPROVED = "✅ Ваша заявка была одобренна.\n └ Нажмите /start, для продолжения."
APPLICATION_REJECTED = "❌ К сожалению, ваша заявка отклонена."
CONTINUE_START = "Спасибо! Пропишите снова /start, чтобы пользоваться всем функционалом."
PENDING = "⌛️ Ваша заявка на рассмотрении, ожидайте ответа."

GREETING = "👨‍💻"


def worker_menu(ref_link: str) -> str:
    return (
        "🖥 Меню воркера\n\n"
        f"🔗 Ваша реферальная ссылка для трейд бота:\n{ref_link}"
    )


def about(stats: dict) -> str:
    return (
        "ℹ️ Информация о проекте:\n\n"
        f"💵 Количество профитов: {stats['count']}\n"
        f"🏦 Общая сумма профитов: {stats['sum']:,}₽\n\n".replace(",", " ")
        + "💱 Выплаты:\n"
        f"💳 Пополнение: {config.PAYOUT_DEPOSIT}%\n"
        f"👨‍💻 Пополнение с ТП: {config.PAYOUT_WITH_TP}%\n\n"
        f"📆 Мы открылись: {config.PROJECT_OPENED}"
    )


def profile(w, sums: dict, dtc: float) -> str:
    nick = escape(w["nickname"]) if w["nickname"] else "не задан"
    return (
        "👨‍💻Ваш профиль:\n"
        f"┌ ID: {w['user_id']}\n"
        f"├ Имя в выплатах: {w['member_no']}\n"
        f"├ Ник: {nick}\n"
        f"└ LVL: {w['lvl']}\n\n"
        "💸 Сумма профитов:\n"
        f"┌ День: {sums['day']:,}₽\n".replace(",", " ")
        + f"├ Месяц: {sums['month']:,}₽\n".replace(",", " ")
        + f"└ Все время: {sums['all']:,}₽\n\n".replace(",", " ")
        + "🪙 OnyxCoin (DTC):\n"
        f"└ Баланс: {dtc:.2f}"
    )


CURATORS_TITLE = "🎓 Выберите куратора, за которым хотите закрепиться"
SETTINGS_TITLE = "⚙️ Управление настройками"
ASK_NICKNAME = "🏷️ Введите новый никнейм:"
NICKNAME_SET = "✅ Никнейм обновлён: {nick}"

SHOP = (
    "🛒 Магазин OnyxCoin\n\n"
    "Добро пожаловать в магазин! Здесь вы можете приобрести различные товары "
    "и услуги за коины проекта.\n\n"
    "Категории товаров:\n"
    "📱 Аккаунты\n⭐ Звёзды Telegram\n📈 Накрутка\n📸 Модели\n👑 Премиум\n⚡ Бустеры\n\n"
    "🪙 Ваш баланс: {balance:.2f} DTC"
)
SHOP_ITEM = (
    "{icon} {name}\n\n"
    "Цена: {price:.2f} DTC\n\n"
    "{status}"
)
SHOP_NOT_ENOUGH = "❌ Недостаточно DTC для покупки. Зарабатывайте профиты!"
SHOP_BOUGHT = "✅ Покупка оформлена . Списано {price:.2f} DTC."

BOTS_MENU = "🤖 Выберите направление:"


def trade_section(ref_link: str) -> str:
    return (
        "📊 Трейд — MEXC\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        f"{ref_link}\n\n"
        "👨‍💻 Управление вашими мамонтами — внутри трейд-бота командой /worker"
    )


def escort_section(ref_link: str) -> str:
    return (
        "🪭 Эскорт — Violet Agency\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        f"{ref_link}\n\n"
        "👨‍💻 Меню воркера — внутри бота Violet Agency"
    )


TOOLS_MENU = "🛠️ Инструменты воркера:"
CARD = (
    "На данный момент реквизиты для прямого перевода отсутствуют. 💳\n\n"
    "Вы можете получить их в фин. отделе, нажав кнопку ниже:"
)
CARD_ISSUED = "💳 Ваши реквизиты :\n<code>{req}</code>\n\nОтправляйте профиты только на них."
DRAW = (
    "✨ Бот отрисовки — за пару секунд нарисует скрин (чек, баланс, перевод). "
    "Нажмите кнопку ниже, чтобы перейти."
)

TOP_TITLE = "🏆 Топ воркеров:"
NO_ACCESS = "⛔️ Сначала пройдите анкету через /start."
