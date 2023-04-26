from aiogram import types, Bot

from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
from random import choice

from states.init import Init

import logging
import config
import markups as mk

from data import db_session
from data.users import User
from data.pets import Pets

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


def add_user(username, chat_id):
    session = db_session.create_session()
    if not session.query(User).filter(User.name == username).all():
        user = User()
        user.name = username
        user.chat_id = chat_id
        session.add(user)
        session.commit()


@dp.message_handler(commands='start', state=None)
async def start(message: types.Message):
    add_user(message.from_user.username, message.from_user.id)
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


async def add_pet(name, username):
    session = db_session.create_session()
    pet = Pets()
    pet.name = name
    pet.master_username = username
    session.add(pet)
    session.commit()


async def check_pet(name, username, chat_id):
    global bot
    session = db_session.create_session()
    names = session.query(Pets).filter(Pets.master_username == username).all()
    if names:
        await bot.send_message(chat_id=chat_id, text='Ошибка: у вас уже есть питомец')
    else:
        await add_pet(name, username)
        scheduler.add_job(check_status, "interval", minutes=1, args=(username, ))


@dp.callback_query_handler(text='Yes', state=None)
async def yes(callback: types.CallbackQuery):
    await callback.message.answer('Вы подтвердили имя вашего питомца')
    await check_pet(name, callback.from_user.username, callback.from_user.id)
    await callback.answer()


@dp.callback_query_handler(text='No', state=None)
async def no(callback: types.CallbackQuery):
    await callback.message.answer('Введите новое имя для вашего питомца')
    await callback.answer()
    await Init.get_name.set()


async def check_status(master_username):
    global bot
    session = db_session.create_session()
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    chat_id = session.query(User).filter(User.name == master_username).first()
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    age = current_datetime - pet.birthday
    # возраст
    pet.age = age.days // 2
    if pet.age >= 20:
        await bot.send_message(chat_id=chat_id, text='До свидания, хозяин!!!')
        session.delete(pet)
    # кормёжка
    pet.feed -= 1
    #   завтрак
    if current_time == datetime.time(hour=9):
        pet.hunger = True
    if current_time == datetime.time(hour=10):
        if pet.hunger:
            await bot.send_message(chat_id=chat_id, text='Вы пропустили завтрак')
        pet.hunger = False
    #   обед
    if current_time == datetime.time(hour=14):
        pet.hunger = True
    if current_time == datetime.time(hour=15):
        if pet.hunger:
            await bot.send_message(chat_id=chat_id, text='Вы пропустили обед')
        pet.hunger = False
    #   ужин
    if current_time == datetime.time(hour=19):
        pet.hunger = True
    if current_time == datetime.time(hour=20):
        if pet.hunger:
            await bot.send_message(chat_id=chat_id, text='Вы пропустили ужин')
        pet.hunger = False
    #   смерть
    if pet.feed <= -100:
        await bot.send_message(chat_id=chat_id, text='К сожалению ваш питомец умер от голода(')
        session.delete(pet)
    if pet.feed > 500:
        await bot.send_message(chat_id=chat_id, text='Вы перекормили своего питомца и он умер от ожирения')
        session.delete(pet)
    # счастье
    pet.happiness -= 1
    if pet.happiness <= -2880:
        await bot.send_message(chat_id=chat_id, text='К сожалению ваш питомец серьезно заболел и умер(')
        session.delete(pet)
    # сон
    pet.sleep -= 1
    if pet.sleep <= -600:
        await bot.send_message(chat_id=chat_id, text='Ваш питомец погиб от переутомления')
        session.delete(pet)
    session.commit()


@dp.message_handler(commands='sleep', state=None)
async def sleep(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    if pet.sleep > 200:
        await message.answer('Питомец еще не утомился')
    else:
        pet.sleep += 1700
        await message.answer('Питомец выспался')
    session.commit()


@dp.message_handler(commands='play', state=None)
async def play(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    if pet.happiness <= -720:
        pet.happiness += 720
    pet.sleep -= 100
    activities = [
        'Вы поиграли с питомцем в мяч',
        'Вы покатались с питомцем на скейте',
        'Вы сходили с питомцем в парк аттракционов',
        'вы сходили с питомцем в музей',
        'Вы сходили с питомцем на концерт',
        'Вы пробежали марафон вместе с питомцем'
    ]
    await message.answer(choice(activities))
    session.commit()


@dp.message_handler(commands='feed', state=None)
async def feed(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    if pet.hunger:
        pet.feed += 480
        pet.hunger = False
        await message.answer('Вы накормили питомца вовремя')
    else:
        pet.feed += 120
        await message.answer('Вы дали питомцу перекусить')
    session.commit()


@dp.message_handler(commands='kill', state=None)
async def kill(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    await message.answer('Игра закончена, вы можете создать нового питомца с помощью кманды /start')
    session.delete(pet)
    session.commit()


@dp.message_handler(commands='static', state=None)
async def static(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    await message.answer(f'Статистика:\n'
                         f'Возраст: {pet.age}\n'
                         f'Кормление: {pet.feed}\n'
                         f'Сон: {pet.sleep}\n'
                         f'Счастье: {pet.happiness}')
    session.commit()


@dp.message_handler(commands='help', state=None)
async def help(message: types.Message):
    await message.answer('Команды:\n'
                         'start - создание нового питомца\n'
                         'sleep - сон питомца\n'
                         'play - игра с питомцем\n'
                         'feed - кормление\n'
                         'static - статистика\n'
                         'kill - убить питомца')


@dp.message_handler(commands='change_hunger', state=None)
async def change_hunger(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.hunger = not pet.hunger
    session.commit()


@dp.message_handler(commands='hunger', state=None)
async def hunger(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    await message.answer(pet.hunger)
    session.commit()


@dp.message_handler(commands='minus_feed', state=None)
async def minus_feed(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.feed -= 150
    session.commit()


@dp.message_handler(commands='plus_feed', state=None)
async def plus_feed(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.feed += 150
    session.commit()


@dp.message_handler(commands='minus_sleep', state=None)
async def minus_sleep(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.sleep -= 150
    session.commit()


@dp.message_handler(commands='plus_sleep', state=None)
async def plus_sleep(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.sleep += 150
    session.commit()


@dp.message_handler(commands='minus_happiness', state=None)
async def minus_happiness(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.happiness -= 150
    session.commit()


@dp.message_handler(commands='plus_happiness', state=None)
async def plus_happiness(message: types.Message):
    session = db_session.create_session()
    master_username = message.from_user.username
    pet = session.query(Pets).filter(Pets.master_username == master_username).first()
    pet.happiness += 150
    session.commit()


if __name__ == "__main__":
    scheduler.start()
    db_session.global_init("db/pets.db")
    executor.start_polling(dp)
