
from html import escape


def greet(name: str) -> str:
    return (
        f"💜 Добро пожаловать, {escape(name)}!\n"
        "└ Это бот элитного агентства сопровождения «Violet Agency»"
    )


def cabinet(m) -> str:
    return (
        "👤 Личный кабинет\n\n"
        f"💜 Бонусный баланс: {m['balance']:.2f} ₽\n"
        f"📥 Внесено предоплат: {m['deposited']:.2f} ₽\n"
        f"📌 Статус: {'VIP' if m['deposited'] >= 10000 else 'Гость'}\n\n"
        "Выберите модель в разделе «VIP Модели»."
    )


def model_card(md) -> str:
    return (
        f"💃 {md['name']}\n\n"
        f"📍 Город: {md['city']}\n"
        f"✨ {md['tags']}\n\n"
        "[фото скрыто — заглушка]\n\n"
        "Чтобы забронировать встречу, внесите предоплату."
    )


def ask_prepay(name: str, min_prepay: int) -> str:
    return (
        f"💐 Бронь встречи: {escape(name)}\n\n"
        f"Введите сумму предоплаты (₽).\nМинимум: {min_prepay}"
    )


def ask_search() -> str:
    return "🔎 Введите ваш город — подберём свободных девушек рядом."


def refund_rejected() -> str:
    return (
        "⏳ Заявка на возврат предоплаты создана и отправлена на проверку.\n\n"
        "❗️ Для возврата необходимо пройти верификацию профиля / оплатить сервисный сбор. "
        "Обратитесь к менеджеру."
    )


def refund_ok(amount: float) -> str:
    return f"✅ Возврат {amount:.2f} ₽ одобрен."


def worker_panel(s, stats: dict) -> str:
    return (
        "💜 Violet Agency\n\n"
        f"🔑 Код от сервиса: {s['code']}\n"
        f"🔗 Реф. ссылка: https://t.me/{{bot}}?start={s['code']}\n\n"
        "📊 Ваша статистика:\n"
        f"├︎ Количество профитов: {stats['count']}\n"
        f"└︎ Общая сумма профитов: {stats['sum']:.0f} ₽"
    )


def settings(s) -> str:
    return (
        "⚙️ Настройка бота\n\n"
        f"💐 Мин. предоплата: {s['min_prepay']}\n"
        f"💎 Цена VIP-доступа: {s['vip_price']}\n"
        f"🎁 Приветственный бонус: {s['welcome_bonus']}\n"
        f"🚫 Авто-отклонение возвратов: {'ВКЛ' if s['refund_reject'] else 'ВЫКЛ'}"
    )


NEW_MAMMOTH = (
    "🎉 У вас новый мамонт!\n\n"
    "🧑‍💼 Юзернейм: @{username}\n"
    "🦣 Имя: {name}\n\n"
    "🆔 ChatID: {chat_id}\n\n"
    "ℹ️ Управление мамонтом — /em {chat_id}"
)
