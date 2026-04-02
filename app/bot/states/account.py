from aiogram.fsm.state import State, StatesGroup


class AddAccountState(StatesGroup):
    phone = State()
    api_id = State()
    api_hash = State()
    bot_username = State()
    order_time = State()
