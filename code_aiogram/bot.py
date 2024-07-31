from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import request

crud_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Create')],
        [KeyboardButton(text='Retrieve')],
        [KeyboardButton(text='Update')],
        [KeyboardButton(text='Delete')],
    ],
    resize_keyboard=True
)

bot = Bot(token='7282232490:AAEjq4oUSjwvigtXjhgKAr3hUrVMuNvi7k0')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
API_URL = 'http://127.0.0.1:8000/api/todos/'


class TodoStates(StatesGroup):
    waiting_for_title_description = State()
    waiting_for_todo_id = State()
    waiting_for_update_data = State()


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    await message.answer('Kerakli tugmani tanlang:', reply_markup=crud_button)


@dp.message_handler(Text(equals='Create'))
async def title_description(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = text.split('\n', 1)

    if len(data) == 2:
        title, description = data
        resource = request.post(API_URL, json={'title': title, 'description': description})
        if resource.status_code == 201:
            await message.answer('Yangi malumot yaratildi')
        else:
            await message.answer('Malumot yaratishga xatolik yuz berdi')
    else:
        await message.answer('Title va descriptionni namunada ko\'rsatilgandek yozing')

    await state.finish()


@dp.message_handler(Text(equals='Retrieve'))
async def read_todos(message: types.Message):
    response = requests.get(API_URL)
    if response.status_code == 200:
        todos = response.json()
        if todos:
            todos_list = "\n".join([f"{todo['id']}. {todo['title']}: {todo['description']}" for todo in todos])
            await message.answer(f"TODO List:\n{todos_list}")
        else:
            await message.answer("No TODO items found.")
    else:
        await message.answer(f"Error fetching TODO items: {response.status_code} {response.text}")


# Update
@dp.message_handler(Text(equals='Update'))
async def update_todo_prompt(message: types.Message):
    await message.answer(
        "Send me the ID of the TODO item you want to update, followed by the new title and description in the format:\nID\nNew Title\nNew Description")
    await TodoStates.waiting_for_update_data.set()


@dp.message_handler(state=TodoStates.waiting_for_update_data, content_types=types.ContentTypes.TEXT)
async def update_todo_receive_data(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = text.split('\n', 2)

    if len(data) == 3:
        todo_id, new_title, new_description = data
        response = requests.put(f"{API_URL}{todo_id}/", json={'title': new_title, 'description': new_description})
        if response.status_code == 200:
            await message.answer("TODO item updated successfully!")
        else:
            await message.answer(f"Error updating TODO item: {response.status_code} {response.text}")
    else:
        await message.answer("Please send the ID, new title, and new description in the correct format.")

    await state.finish()


# Delete
@dp.message_handler(Text(equals='Delete'))
async def delete_todo_prompt(message: types.Message):
    await message.answer("Send me the ID of the TODO item you want to delete.")
    await TodoStates.waiting_for_todo_id.set()


@dp.message_handler(state=TodoStates.waiting_for_todo_id, content_types=types.ContentTypes.TEXT)
async def delete_todo_receive_id(message: types.Message, state: FSMContext):
    todo_id = message.text.strip()
    response = requests.delete(f"{API_URL}{todo_id}/")
    if response.status_code == 204:
        await message.answer("TODO item deleted successfully!")
    else:
        await message.answer(f"Error deleting TODO item: {response.status_code} {response.text}")

    await state.finish()


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=T)
