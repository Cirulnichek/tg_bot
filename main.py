from aiogram import types, Bot

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from sates.init import Init

import logging
import config
import markups as mk

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


@dp.message_handler(Command("start"), state=None)
async def start(message: types.Message):
    await message.answer(
        "Привет. Это бот-тамагоччи!\n"
        "Время завести питомца!\n"
        "Введите имя вашего питомца")
    await Init.get_name.set()


@dp.message_handler(state=Init.get_name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(
        f"Вы подтверждаете имя вашего питомца: {name}",)
    await Init.next()


@dp.message_handler(state=Init.confirm_name)
async def confirm_name(callback_query: types.CallbackQuery, state: FSMContext):
    answer = callback_query.data
    data = await state.get_data()
    name = data.get("name")
    if answer == "Yes":
        await bot.answer_callback_query(callback_query.id)
        await Bot.send_message(callback_query.from_user.id, f"Вы подтвердили имя вашего питомца: {name}")
    if answer == "No":
        await Init.get_name.set()


if __name__ == "__main__":
    executor.start_polling(dp)