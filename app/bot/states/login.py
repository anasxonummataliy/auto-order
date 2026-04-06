from aiogram.fsm.state import State, StatesGroup


class LoginState(StatesGroup):
    waiting_code = State()
    waiting_password = State()
