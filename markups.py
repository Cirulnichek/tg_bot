from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#создание питомца
init_keyboard = [[
        InlineKeyboardButton("Да", callback_data='Yes'),
        InlineKeyboardButton("Нет", callback_data='No'),
    ]]
init_markup = InlineKeyboardMarkup(init_keyboard)
