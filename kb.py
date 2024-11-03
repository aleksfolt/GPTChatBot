from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def clear_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Очистить чат", callback_data="clear_chat"))
    return builder.as_markup()