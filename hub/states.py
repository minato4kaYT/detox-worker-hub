from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    hours = State()
    source = State()
    experience = State()
    curator = State()


class Settings(StatesGroup):
    nickname = State()
