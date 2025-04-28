from aiogram.types import FSInputFile
from aiogram.types import Message


# посылает в чат фото
async def send_image(message: Message, name: str) -> Message:
    photo = FSInputFile(f'resources/images/{name}.jpg')
    return await message.bot.send_photo(chat_id=message.chat.id, photo=photo)


# загружает сообщение из папки  /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# загружает промпт из папки  /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()
