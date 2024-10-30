from aiogram.fsm.state import StatesGroup, State


class StateStorage(StatesGroup):
    storage_name = State()  # Название хранилища.
    name_product = State()  # Название продукта.
    amount = State()  # Количество продукта.
    amount_update = State()
    confirm = State()
    eject = State()
    notation = State()