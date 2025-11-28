# bot/ui.py
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def yes_no_keyboard(yes_data: str, no_data: str = "cancel"):
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=yes_data),
         InlineKeyboardButton("No", callback_data=no_data)],
    ]
    return InlineKeyboardMarkup(keyboard)

def ok_button(text="OK", callback="ok"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=callback)]])
