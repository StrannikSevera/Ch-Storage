import pathlib
import sys

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from database.db_sqlite import Database, NoteStorage
from database.modules import StateStorage
from aiogram.fsm.context import FSMContext


fsm_router = Router()
script_dir = pathlib.Path(sys.argv[0]).parent
database = Database(script_dir / 'storage.db')
note_storage = NoteStorage(script_dir / 'note_storage.db')


@fsm_router.message(StateStorage.storage_name, F.text)
async def add_name_storage(message: types.Message, state: FSMContext):
    storage_name = message.text
    database.add_storage(storage_name)  # Добавляем в базу данных
    await message.answer(text=f'Хранилище "{storage_name}" было создано.')
    await state.clear()


@fsm_router.message(StateStorage.name_product, F.text)
async def add_name_product(message: types.Message, state: FSMContext):
    storage_id = (await state.get_data()).get('storage_id')
    await state.update_data(name_product=message.text)
    await message.answer(text='Укажите количество продукта:')
    await state.set_state(StateStorage.amount)


@fsm_router.message(StateStorage.amount, F.text)
async def add_notation_product(message: types.Message, state: FSMContext):
    storage_id = (await state.get_data()).get('storage_id')
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")
        return
    await state.update_data(amount=message.text)
    await message.answer(text='Укажите единицу измерения(Например "кг" или "л"):')
    await state.set_state(StateStorage.notation)


@fsm_router.message(StateStorage.notation, F.text)
async def add_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()

    storage_id = data.get('storage_id')
    name_product = data.get('name_product')
    amount = data.get('amount')
    notation = message.text

    database.add_product(storage_id, name_product, amount, notation)
    await message.answer(text='Товар добавлен!')
    await state.clear()


@fsm_router.message(StateStorage.eject, F.text)
async def confirm_eject_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    storage_id = data.get('storage_id')
    product_name = message.text

    # Запрашиваем новое количество
    await message.answer(text='Введите новое количество продукта (введите 0 для удаления):')
    await state.update_data(product_name=product_name)  # Сохраняем имя продукта в состоянии
    await state.set_state(StateStorage.amount_update)


@fsm_router.message(StateStorage.amount_update, F.text)
async def handle_eject_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    storage_id = data.get('storage_id')
    product_name = data.get('product_name')

    try:
        new_amount = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")
        return

    if new_amount == 0:
        database.eject_product(storage_id, product_name)
        await message.answer(text='Продукт был успешно удален.')
    else:
        # Логика для обновления количества продукта в базе данных
        database.update_product_amount(storage_id, product_name, new_amount)
        await message.answer(text='Количество продукта было обновлено.')

    await state.clear()


@fsm_router.message(StateStorage.confirm, F.text)
async def handle_storage_deletion_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    storage_id = data.get('storage_id')
    confirmation = message.text.lower()

    if confirmation == "да":
        database.delete_storage(storage_id)
        await message.answer('Хранилище удалено!')
    else:
        await message.answer('Удаление отменено.')

    await state.clear()