

from datetime import datetime
from typing import Dict, List, Optional

class PaymentSystem:


    WORKER_COMMISSION = 0.15


    WORKERS_DB = {
        1: {
            'id': 1,
            'name': 'Иван',
            'telegram_id': 123456789,
            'balance': 0.0,
            'total_earned': 0.0,
            'clients_brought': 0,
            'status': 'active'
        },
        2: {
            'id': 2,
            'name': 'Петр',
            'telegram_id': 987654321,
            'balance': 0.0,
            'total_earned': 0.0,
            'clients_brought': 0,
            'status': 'active'
        }
    }


    PAYMENTS_HISTORY = []

    @classmethod
    def process_booking(cls, model_id: int, client_id: int, worker_id: int, amount: float) -> Dict:


        commission = amount * cls.WORKER_COMMISSION


        if worker_id in cls.WORKERS_DB:
            worker = cls.WORKERS_DB[worker_id]
            worker['balance'] += commission
            worker['total_earned'] += commission
            worker['clients_brought'] += 1


        payment = {
            'timestamp': datetime.now().isoformat(),
            'model_id': model_id,
            'client_id': client_id,
            'worker_id': worker_id,
            'amount': amount,
            'commission': commission,
            'status': 'completed'
        }
        cls.PAYMENTS_HISTORY.append(payment)

        return payment

    @classmethod
    def get_worker_notification(cls, worker_id: int, payment: Dict) -> str:

        worker = cls.WORKERS_DB.get(worker_id)
        if not worker:
            return ""

        text = f"""🔔 **НОВЫЙ ЗАКАЗ ОТ ВАШЕГО КЛИЕНТА**

👸 Модель: {payment['model_id']}
💰 Сумма заказа: {payment['amount']:.0f}₽
💵 Ваша комиссия: {payment['commission']:.0f}₽

💎 Баланс: {worker['balance']:.0f}₽
📊 Всего заработано: {worker['total_earned']:.0f}₽
👥 Клиентов привлечено: {worker['clients_brought']}

✅ Средства поступят на ваш счет через 24 часа

📲 Спасибо за работу!"""

        return text

    @classmethod
    def get_worker_by_id(cls, worker_id: int) -> Optional[Dict]:

        return cls.WORKERS_DB.get(worker_id)

    @classmethod
    def get_worker_balance(cls, worker_id: int) -> float:

        worker = cls.WORKERS_DB.get(worker_id)
        return worker['balance'] if worker else 0.0

    @classmethod
    def get_all_workers(cls) -> List[Dict]:

        return [w for w in cls.WORKERS_DB.values() if w['status'] == 'active']

    @classmethod
    def withdraw_funds(cls, worker_id: int, amount: float) -> bool:

        worker = cls.WORKERS_DB.get(worker_id)
        if not worker or worker['balance'] < amount:
            return False

        worker['balance'] -= amount
        return True


class NotificationSystem:


    NOTIFICATION_QUEUE = {}

    @classmethod
    async def send_to_worker(cls, worker_id: int, bot, text: str) -> bool:

        try:
            worker = PaymentSystem.WORKERS_DB.get(worker_id)
            if not worker:
                return False

            telegram_id = worker['telegram_id']
            await bot.send_message(telegram_id, text)
            return True
        except:
            return False

    @classmethod
    def queue_notification(cls, user_id: int, text: str):

        if user_id not in cls.NOTIFICATION_QUEUE:
            cls.NOTIFICATION_QUEUE[user_id] = []
        cls.NOTIFICATION_QUEUE[user_id].append(text)

    @classmethod
    def get_notifications(cls, user_id: int) -> List[str]:

        return cls.NOTIFICATION_QUEUE.get(user_id, [])

    @classmethod
    def clear_notifications(cls, user_id: int):

        if user_id in cls.NOTIFICATION_QUEUE:
            cls.NOTIFICATION_QUEUE[user_id] = []
