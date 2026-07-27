from aiogram.fsm.state import State, StatesGroup


class Draw(StatesGroup):
    amount = State()
    recipient = State()
    sender = State()
