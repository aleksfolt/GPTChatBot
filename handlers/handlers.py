import json
import os
import aiofiles
import requests
from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database import set_user_model, get_user_model
from kb import clear_button

router = Router()

CHAT_FOLDER = "chats"
os.makedirs(CHAT_FOLDER, exist_ok=True)


async def load_chat_history(user_id):
    chat_path = os.path.join(CHAT_FOLDER, f"{user_id}_chat.json")
    if os.path.exists(chat_path):
        async with aiofiles.open(chat_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    return []


async def save_chat_history(user_id, messages):
    chat_path = os.path.join(CHAT_FOLDER, f"{user_id}_chat.json")
    async with aiofiles.open(chat_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(messages, ensure_ascii=False, indent=4))


async def delete_chat_history(user_id):
    chat_path = os.path.join(CHAT_FOLDER, f"{user_id}_chat.json")
    if os.path.exists(chat_path):
        os.remove(chat_path)


@router.message(Command("model"))
async def select_model(message: Message):
    models = ["gpt-4", "BlackBox", "Qwen"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=model, callback_data=f"select_model:{model}")]
            for model in models
        ]
    )
    await message.answer("Выберите модель:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("select_model:"))
async def set_model_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    selected_model = callback_query.data.split(":")[1]
    await set_user_model(user_id, selected_model)
    await callback_query.answer(f"Модель {selected_model} выбрана.")


@router.message(F.text)
async def ask_question(msg: Message):
    user_id = msg.from_user.id
    user_message = msg.text

    selected_model = await get_user_model(user_id)
    if selected_model is None:
        selected_model = "gpt-4"

    chat_history = await load_chat_history(user_id)
    chat_history.append({"role": "user", "content": user_message})

    try:
        if selected_model == "gpt-4":
            response = requests.post('http://api.onlysq.ru/ai/v1', json=chat_history)
            response_data = response.json()

        elif selected_model == "BlackBox":
            request_data = {
                "model": "blackbox",
                "request": {
                    "object": "bot",
                    "messages": chat_history
                }
            }
            response = requests.post('http://api.onlysq.ru/ai/v2', json=request_data)
            response_data = response.json()
        elif selected_model == "Qwen":
            request_data = {
                "model": "qwen",
                "request": {
                    "object": "bot",
                    "messages": chat_history
                }
            }
            response = requests.post('http://api.onlysq.ru/ai/v2', json=request_data)
            response_data = response.json()

        assistant_answer = response_data.get("answer", "")
        if assistant_answer:
            chat_history.append({"role": "assistant", "content": assistant_answer})
            await save_chat_history(user_id, chat_history)
            try:
                await msg.answer(assistant_answer, parse_mode=ParseMode.MARKDOWN, reply_markup=await clear_button())
            except Exception:
                await msg.answer(assistant_answer, reply_markup=await clear_button())
        else:
            await msg.answer("Произошла ошибка: Пустой ответ от ассистента.", reply_markup=await clear_button())

    except Exception as e:
        print(f"Произошла ошибка при обработке запроса: {e}")
        await msg.answer("Произошла ошибка при обработке вашего запроса.", reply_markup=await clear_button())


@router.callback_query(F.data == "clear_chat")
async def clear_chat_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await delete_chat_history(user_id)
    await callback_query.answer("История чата очищена.")
