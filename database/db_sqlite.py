import sqlite3


class Database:
    def __init__(self, db_name: str):
        try:
            self.connection = sqlite3.connect(db_name)
            self.cursor = self.connection.cursor()
            self._create_table()
        except sqlite3.Error as error:
            print('Ошибка при подключении базы данных:', error)

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS storages (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                storage_id INTEGER REFERENCES storages(id),
                name_product TEXT,
                amount INTEGER NOT NULL,
                notation TEXT
            )
        """)
        self.connection.commit()

    def add_storage(self, name: str):
        self.cursor.execute("INSERT INTO storages (name) VALUES (?)", (name,))
        self.connection.commit()

    def add_product(self, storage_id: int, name: str, amount: int, notation: str):
        self.cursor.execute("INSERT INTO products (storage_id, name_product, amount, notation) VALUES (?, ?, ?, ?)",
                            (storage_id, name, amount, notation))
        self.connection.commit()

    def get_storages(self):
        self.cursor.execute("SELECT * FROM storages")
        return self.cursor.fetchall()

    def delete_storage(self, storage_id: int):
        self.cursor.execute("DELETE FROM storages WHERE id=?", (storage_id,))
        self.connection.commit()

    def eject_product(self, storage_id: int, name: str):
        self.cursor.execute("DELETE FROM products WHERE storage_id=? AND name_product=?", (storage_id, name))
        self.connection.commit()

    def get_product(self, storage_id: int):
        """Получить продукты по storage_id."""
        self.cursor.execute("SELECT storage_id, name_product, amount, notation FROM products WHERE storage_id = ?", (storage_id,))
        return self.cursor.fetchall()

    def update_product_amount(self, storage_id: int, name: str, new_amount: int):
        """Обновить количество продукта в базе данных."""
        self.cursor.execute("""
            UPDATE products 
            SET amount = ? 
            WHERE storage_id = ? AND name_product = ?
        """, (new_amount, storage_id, name))
        self.connection.commit()


class NoteStorage(Database):
    def __init__(self, note_storage: str):
        super().__init__(note_storage)

        # Создаем таблицы для хранения заметок и администраторов
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY ,
                user_id INTEGER, 
                note TEXT
            )
        """)

        self.connection.commit()
