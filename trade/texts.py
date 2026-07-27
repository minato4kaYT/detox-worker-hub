
from html import escape


def greet(name: str) -> str:
    return (
        f"👋 Приветствую, {escape(name)}!\n"
        "└ Это телеграм бот криптоплатформы MEXC для торговли на фьючерсах"
    )


def portfolio(m) -> str:
    return (
        "💼 Ваш портфель\n\n"
        f"💰 Баланс: {m['balance']:.2f} USDT\n"
        f"📥 Внесено: {m['deposited']:.2f} USDT\n\n"
        "Откройте сделку в разделе «Открыть ECN»."
    )


def trade_win(coef: float, profit: float, balance: float) -> str:
    return (
        "📈 Сделка закрыта в ПЛЮС!\n\n"
        f"Коэффициент: x{coef:.2f}\n"
        f"Прибыль: +{profit:.2f} USDT\n"
        f"💰 Баланс: {balance:.2f} USDT"
    )


def trade_lose(amount: float, balance: float) -> str:
    return (
        "📉 Сделка закрыта в МИНУС.\n\n"
        f"Убыток: -{amount:.2f} USDT\n"
        f"💰 Баланс: {balance:.2f} USDT"
    )


def ask_deposit(min_dep: int) -> str:
    return f"📥 Введите сумму пополнения (USDT).\nМинимум: {min_dep}"


def ask_trade(min_deal: int, balance: float) -> str:
    return (
        f"📊 Введите сумму сделки (USDT).\n"
        f"Минимум: {min_deal}\nДоступно: {balance:.2f}"
    )


def withdraw_rejected() -> str:
    return (
        "⏳ Заявка на вывод создана и отправлена на проверку.\n\n"
        "❗️ Для вывода необходимо пройти верификацию аккаунта / оплатить комиссию сети. "
        "Обратитесь в тех. поддержку."
    )


def withdraw_ok(amount: float) -> str:
    return f"✅ Вывод {amount:.2f} USDT одобрен."


def worker_panel(s, stats: dict) -> str:
    return (
        "🐾 Trade\n\n"
        f"🔑 Код от сервиса: {s['code']}\n"
        f"🔗 Реф. ссылка: https://t.me/{{bot}}?start={s['code']}\n\n"
        "📊 Ваша статистика:\n"
        f"├︎ Количество профитов: {stats['count']}\n"
        f"└︎ Общая сумма профитов: {stats['sum']:.0f} USDT"
    )


def settings(s) -> str:
    return (
        "⚙️ Настройка бота\n\n"
        f"🍀 Удача: {s['luck']:.1f}%\n"
        f"📐 Коэффициент: {s['coef_min']} – {s['coef_max']}\n"
        f"💵 Мин. сделка: {s['min_deal']}\n"
        f"📤 Мин. вывод: {s['min_withdraw']}\n"
        f"📥 Мин. пополнение: {s['min_deposit']}\n"
        f"🚫 Авто-отклонение выводов: {'ВКЛ' if s['auto_reject'] else 'ВЫКЛ'}"
    )


NEW_MAMMOTH = (
    "🎉 У вас новый мамонт!\n\n"
    "🧑‍💼 Юзернейм: @{username}\n"
    "🦣 Имя: {name}\n\n"
    "🆔 ChatID: {chat_id}\n\n"
    "ℹ️ Управление мамонтом — /em {chat_id}"
)
