import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from util import (load_message, send_image)

load_dotenv()

bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text='/start',
    )
    keyboard.button(
        text='/help',
    )

    keyboard.button(
        text='/phome',
        request_contact=True
    )

    text = load_message('main')
    await send_image(chat_id=message.chat.id, name='main', bot=message.bot)
    await message.answer(text=text, reply_markup=keyboard.as_markup())


# Обработчик любого текстового сообщения
@dp.message(F.text)
async def echo_message(message: Message):
    await message.answer(f"Ты написал: {message.text}")


# Запуск бота
async def start_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
