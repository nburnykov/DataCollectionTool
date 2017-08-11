import sqlite3
from typing import List


class DataBaseHandler:
    def __init__(self, db_name: str):
        self._connection = None

        conn = sqlite3.connect(db_name)
        self._connection = conn.cursor()
        # self._connection.row_factory = sqlite3.Row

    def _is_database_empty(self) -> bool:
        result = self._connection.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
        return len(result.fetchall()) == 0

    def _table_exists(self, table_name: str) -> bool:
        result = self._connection.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
        for row in result.fetchall():
            if row[0] == table_name:
                return True
        return False

    def _create_table(self, table_name: str):
        self._connection.execute("CREATE TABLE IF NOT EXISTS {} (ID_ INTEGER PRIMARY KEY AUTOINCREMENT);"
                                 .format(table_name))

    def _drop_table(self, table_name: str):
        self._connection.execute("DROP TABLE IF EXISTS {};".format(table_name))

    def _get_column_list(self, table_name: str) -> List:
        result = self._connection.execute("SELECT * FROM {};".format(table_name))
        return [row[0] for row in result.description if row != 'ID_']

    def add_data(self, table_name: str, columns: List, data: List):
        self._create_table(table_name)
        col = self._get_column_list(table_name)

        col_diff = list(set(columns).difference(col))
        for c in col_diff:
            self._connection.execute("ALTER TABLE {} ADD COLUMN {} TEXT;".format(table_name, c))

        column_str = ", ".join(columns)
        for row in data:
            row_str = ", ".join(row)
            self._connection.execute("INSERT INTO {} ({}) VALUES ({})".format(table_name, column_str, row_str))

    def disconnect(self):
        self._connection.close()
