import pathlib
import sys

from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from database.db_sqlite import Database, NoteStorage
from database.modules import StateStorage
from keyboards.usr_kbd_builder import notes_menu

user_handler_router = Router()

script_dir = pathlib.Path(sys.argv[0]).parent
database = Database(script_dir / 'storage.db')
note_storage = NoteStorage(script_dir / 'note_storage.db')


@user_handler_router.message(CommandStart())
async def process_create_storage(message: types.Message, state: FSMContext):
    await message.answer(text='Начинаю работу! ')
    await message.answer(text='Для создания хранилища, введите команду /create. \nДля вызова списка доступных команд '
                              'введите /help')


# Инициализируем создание хранилища
@user_handler_router.message(StateFilter(None), Command('create'))
async def process_create_storage(message: types.Message, state: FSMContext):
    await message.answer(text='Введите название: ')
    await state.set_state(StateStorage.storage_name)


# Создание списка покупок
@user_handler_router.message(Command('notes'))
async def process_create_notes(message: types.Message):
    user_id = message.from_user.id
    note_text = message.text[6:].strip()

    if not note_text:
        await message.answer("Пожалуйста, укажите текст заметки после команды /notes.")
        return

    with note_storage.connection:
        note_storage.cursor.execute("INSERT INTO notes (user_id, note) VALUES (?, ?)", (user_id, note_text))

    await message.answer("Список покупок создан!")


@user_handler_router.message(Command('show_note'))
async def process_show_notes(message: types.Message):
    await message.answer("Список покупок:\n", reply_markup=notes_menu(message))


@user_handler_router.message(Command('clear_notes'))
async def process_clear_notes(message: types.Message):
    user_id = message.from_user.id
    note_id = message.text[13:].strip()

    if not note_id.isdigit():
        await message.answer("Пожалуйста, укажите ID заметки для удаления.")
        return

    note_id = int(note_id)

    with note_storage.connection:
        note_storage.cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))

        if note_storage.cursor.rowcount > 0:
            await message.answer("Список покупок очищен!")
        else:
            await message.answer("Список покупок не найден.")


@user_handler_router.message(Command('show'))
async def process_show_storage(message: types.Message):
    storages = database.get_storages()

    if storages:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=storage[1], callback_data=f'show_products_{storage[0]}')]
            for storage in storages
        ])
        await message.answer("Выберите хранилище:", reply_markup=keyboard)
    else:
        await message.answer('Нет доступных хранилищ с продуктами.')


# Добавить продукт в хранилище
@user_handler_router.message(Command('add'))
async def process_add_product(message: types.Message):
    storages = database.get_storages()

    if not storages:
        await message.answer(text='Сначала создайте хранилище с помощью команды /create.')
        return

    buttons = [types.InlineKeyboardButton(text=s[1], callback_data=f'add_product_{s[0]}') for s in storages]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.answer('Выберите хранилище:', reply_markup=keyboard)


@user_handler_router.message(Command('eject'))
async def process_eject_product(message: types.Message):
    storages = database.get_storages()

    if not storages:
        await message.answer(text='Сначала создайте хранилище с помощью команды /create.')
        return

    buttons = [types.InlineKeyboardButton(text=s[1], callback_data=f'eject_product_{s[0]}') for s in storages]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.answer('Выберите хранилище для изъятия/изменения продукта:', reply_markup=keyboard)


# Удалить хранилище
@user_handler_router.message(Command('delete'))
async def process_delete_storage(message: types.Message):
    storages = database.get_storages()

    if storages:
        buttons = [types.InlineKeyboardButton(text=s[1], callback_data=f'delete_storage_{s[0]}') for s in storages]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        await message.answer('Выберите хранилище для удаления:', reply_markup=keyboard)
    else:
        await message.answer('Нет доступных хранилищ для удаления.')


# Добавить продукт в хранилище.
@user_handler_router.message(Command('help'))
async def process_help(message: types.Message):
    help_text = """/create - Создать новое хранилище.
/show - Все созданные хранилища.
/add - Добавить продукт в хранилище.
/eject - Изменить продукт.
/delete - Удалить хранилище.
/notes - Создать список покупок.
/show_note - Показать список покупок.
/clear_notes - Очистить список покупок.

"""
    await message.answer(help_text)
