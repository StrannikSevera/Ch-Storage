import pathlib
import sys
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import BUTTONS
from database.db_sqlite import Database, NoteStorage

script_dir = pathlib.Path(sys.argv[0]).parent
note_storage = NoteStorage(script_dir / 'note_storage.db')


def create_button(text_key: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=BUTTONS[text_key], callback_data=callback_data)


# Клавиатура отображения хранилища.
def create_storage_show() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        create_button('btn_1', 'btn1_pressed'),  # Кнопка "Добавить позицию"
        create_button('btn_2', 'btn2_pressed'),  # Кнопка "Изменить"
        create_button('btn_3', 'btn3_pressed'),  # Кнопка "В главное меню"
        width=2
    )

    return kb_builder.as_markup()


def main_menu() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        create_button('btn_4', 'btn4_pressed'),  # Кнопка "К списку хранилищ."
        create_button('btn_5', 'btn5_pressed'),  # Кнопка "К списку покупок."
        create_button('btn_8', 'btn8_pressed'),  # Кнопка "Новое хранилище."
        width=2
    )

    return kb_builder.as_markup()


def notes_menu(message: types.Message):
    user_id = message.from_user.id
    note_storage.cursor.execute("SELECT id, note FROM notes WHERE user_id = ?", (user_id,))
    notes = note_storage.cursor.fetchall()

    # if not notes:
    #     await message.answer("Созданных списков покупок нет.")
    #     return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"Созданные списки{note_id}", callback_data=f"show_note_{note_id}")
            for note_id, _ in notes
        ]
    ])

    return keyboard
