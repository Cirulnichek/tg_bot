from aiogram.dispatcher.filters.state import StatesGroup, State


class Init(StatesGroup):
    get_name = State()
    confirm_name = State()