import pathlib
import sys
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F, types
from database.db_sqlite import NoteStorage, Database
from database.modules import StateStorage
from aiogram.fsm.context import FSMContext
from lexicon.lexicon import BUTTONS

callback_router = Router()
script_dir = pathlib.Path(sys.argv[0]).parent
database = Database(script_dir / 'storage.db')
note_storage = NoteStorage(script_dir / 'note_storage.db')


@callback_router.callback_query(lambda cb: cb.data.startswith('show_products_'))
async def process_show_products(callback: types.CallbackQuery):

    storage_id = callback.data.split('_')[2]
    products = database.get_product(storage_id)

    product_list = "\n".join(
        [f" • {product[1]} : {product[2]} {product[3]}" for product in
         products]) if products else "Нет доступных продуктов."

    keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить позицию", callback_data=f'add_product_{storage_id}'),
            InlineKeyboardButton(text="Изменить/удалить позицию", callback_data=f'eject_product_{storage_id}')
        ],
        [
            InlineKeyboardButton(text=BUTTONS['btn_4'], callback_data='btn4_pressed')
        ]
    ])

    await callback.message.edit_text(
        f"\nПродукты:\n{product_list}",
        reply_markup=keyboard
    )


@callback_router.callback_query(lambda cb: cb.data.startswith('add_product_'))
async def process_add_product_select(callback: types.CallbackQuery, state: FSMContext):
    storage_id = callback.data.split('_')[2]
    await state.update_data(storage_id=storage_id)
    await callback.message.answer(text='Что добавить в хранилище?')
    await state.set_state(StateStorage.name_product)


@callback_router.callback_query(lambda cb: cb.data.startswith('eject_product_'))
async def process_delete_product_select(callback: types.CallbackQuery, state: FSMContext):
    storage_id = callback.data.split('_')[2]
    await state.update_data(storage_id=storage_id)
    await callback.message.answer(text='Что удалить/изменить?')
    await state.set_state(StateStorage.eject)  # Переиспользуем состояние для удаления товара


@callback_router.callback_query(lambda cb: cb.data.startswith('delete_storage_'))
async def confirm_delete_storage(callback: types.CallbackQuery, state: FSMContext):
    storage_id = callback.data.split('_')[2]  # Получаем storage_id из callback.data
    await state.update_data(storage_id=storage_id)  # Сохраняем в состоянии
    await callback.message.answer(
        'Вы уверены, что хотите удалить это хранилище? Напишите "Да" для подтверждения или "Нет" для отмены.'
    )
    await state.set_state(StateStorage.confirm)


@callback_router.callback_query(F.data == 'btn4_pressed')
async def callback_btn2(callback: CallbackQuery):
    storages = database.get_storages()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=storage[1], callback_data=f'show_products_{storage[0]}')]
        for storage in storages
    ])
    await callback.message.edit_text("Выберите хранилище:", reply_markup=keyboard)


@callback_router.callback_query(F.data.startswith("show_note_"))
async def show_note_callback(callback: CallbackQuery):
    try:
        note_id = int(callback.data.split("_")[2])  # Извлекаем ID заметки
        note_storage.cursor.execute("SELECT note FROM notes WHERE id = ?", (note_id,))
        note = note_storage.cursor.fetchone()

        if note:
            await callback.message.answer(note[0])  # Отправляем заметку в качестве сообщения в чат
        else:
            await callback.message.answer("Заметка не найдена!")
    except (IndexError, ValueError):
        await callback.message.answer("Произошла ошибка при извлечении заметки. Попробуйте еще раз.")