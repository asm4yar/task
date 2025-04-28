import asyncio
import os
import traceback

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from gpt import ChatGptService
from util import load_prompt
from util import (load_message, send_image)

load_dotenv()

storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
chatgpt = ChatGptService(os.getenv('AI_TOKEN'))
dp = Dispatcher(storage=storage)


class GPTMode(StatesGroup):
    active = State()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Старт', callback_data='/start')
    keyboard.button(text='Помощь', callback_data='/help')
    keyboard.button(text='Поделиться контактом', callback_data='/phone')
    keyboard.adjust(2, 1)  # 2 кнопки в первой строке, 1 во второй

    text = load_message('main')
    await send_image(message, 'main')
    await message.answer(text=text, reply_markup=keyboard.as_markup())


@dp.message(Command('random'))
async def cmd_random(message: Message):
    command = 'random'
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Хочу ещё факт', callback_data='more_fact')
    keyboard.button(text='Закончить', callback_data='finish')

    await send_image(message, 'random')
    to_user_message = load_message(command)
    message_answer = await message.answer(to_user_message)

    try:
        prompt = load_prompt(command)
        answer = await chatgpt.send_question(
            prompt,
            'Приведи рандомный факт',
            temperature=1.2,
            top_p=0.95,
        )

        await message_answer.edit_text(
            text=f"Вот интересный факт:\n\n{answer}",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        await message_answer.edit_text("Произошла ошибка при получении факта. Попробуйте позже.")
        print(f"Error in cmd_random: {e}")
        traceback.print_exc()


@dp.message(Command("gpt"))
async def start_gpt_mode(message: types.Message, state: FSMContext):
    await state.set_state(GPTMode.active)
    text = load_message('gpt')
    await send_image(message, 'gpt')
    await message.answer(text=text)


# Обработчик сообщений в режиме GPT
@dp.message(GPTMode.active)
async def handle_gpt_message(message: types.Message):
    if not chatgpt.message_list:
        prompt = load_prompt('gpt')
        chatgpt.set_prompt(prompt)

    await chatgpt.add_message(message.text)
    answer = await chatgpt.send_message_list()
    my_message = await message.answer('Собеседник набирает сообщение...')
    await my_message.edit_text(answer)


# Обработчик команды /exit
@dp.message(Command("exit"), GPTMode.active)
async def exit_gpt_mode(message: types.Message, state: FSMContext):
    await state.clear()
    chatgpt.message_list.clear()
    await message.answer("❌ Режим ChatGPT выключен.")


# Обработчики callback_query для кнопок
@dp.callback_query(F.data == 'more_fact')
async def more_fact_callback(callback: CallbackQuery):
    await callback.answer()
    # Эмулируем команду /random
    await cmd_random(callback.message)


@dp.callback_query(F.data == 'finish')
async def finish_callback(callback: CallbackQuery):
    await callback.answer()
    # Эмулируем команду /start
    await cmd_start(callback.message)


# Обработчики callback_query
@dp.callback_query(F.data == '/start')
async def start_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Запускаем бота...")


@dp.callback_query(F.data == '/help')
async def help_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Список команд: ...")


@dp.callback_query(F.data == '/phone')
async def phome_callback(callback: CallbackQuery):
    await callback.answer("Используйте команду /phome для отправки контакта", show_alert=True)


# Обработчик любого текстового сообщения
@dp.message(F.text)
async def echo_message(message: Message):
    await message.answer(f"Ты написал: {message.text}")


# Запуск бота
async def start_bot():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
