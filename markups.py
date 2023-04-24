from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#создание питомца
init_keyboard = InlineKeyboardMarkup(row_width=2)
ikb1 = InlineKeyboardButton(text="Да", callback_data='Yes')
ikb2 = InlineKeyboardButton(text="Нет", callback_data='No')
init_keyboard.add(ikb1, ikb2)
