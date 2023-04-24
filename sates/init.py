from aiogram.dispatcher.filters.state import StatesGroup, State


class Init(StatesGroup):
    get_name = State()
    pet_error = State()