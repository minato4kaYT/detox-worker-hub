from aiogram.fsm.state import State, StatesGroup


class Victim(StatesGroup):
    deposit = State()
    trade = State()
    withdraw = State()
    promo = State()


class Worker(StatesGroup):
    set_field = State()
    promo_amount = State()
    broadcast = State()
