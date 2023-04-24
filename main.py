from aiogram import types, Bot

from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from sates.init import Init

import logging
import config
import markups as mk

from data import db_session
from data.users import User
from data.pets import Pets

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


def add_user(username):
    session = db_session.create_session()
    if not [user for user in session.query(User).filter(User.name == username)]:
        user = User()
        user.name = username
        session.add(user)
        session.commit()


@dp.message_handler(commands='start', state=None)
async def start(message: types.Message):
    add_user(message.from_user.username)
    await message.answer(
        "Привет. Это бот-тамагоччи!\n"
        "Время завести питомца!\n"
        "Введите имя вашего питомца")
    await Init.get_name.set()


name = ''


@dp.message_handler(state=Init.get_name)
async def get_name(message: types.Message, state: FSMContext):
    global name
    name = message.text
    await state.reset_state()
    await message.answer(
        text=f"Вы подтверждаете имя вашего питомца: {name}?", reply_markup=mk.init_keyboard)


chat_id = None


def add_pet(name, username):
    session = db_session.create_session()
    pet = Pets()
    pet.name = name
    pet.username = username
    session.add(pet)
    session.commit()


def check_pet(name, username):
    session = db_session.create_session()
    names = [pet for pet in session.query(Pets).filter(Pets.master_username == username)]
    if names:
        Init.pet_error.set()
    else:
        add_pet(name, username)


@dp.message_handler(state=Init.pet_error)
async def pet_error(state: FSMContext):
    await Bot.send_message(chat_id=chat_id, text='Ошибка: у вас уже есть питомец')
    await state.reset_state()


@dp.callback_query_handler(text='Yes', state=None)
async def yes(callback: types.CallbackQuery):
    global chat_id
    chat_id = callback.id
    await callback.message.answer('Вы подтвердили имя вашего питомца')
    check_pet(name, callback.from_user.username)
    await callback.answer()


@dp.callback_query_handler(text='No', state=None)
async def no(callback: types.CallbackQuery):
    await callback.message.answer('Введите новое имя для вашего питомца')
    await callback.answer()
    await Init.get_name.set()


if __name__ == "__main__":
    db_session.global_init("db/pets.db")
    executor.start_polling(dp)