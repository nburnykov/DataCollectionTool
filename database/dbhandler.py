import sqlite3
from typing import List
import logging

logger = logging.getLogger('main')


class DataBaseHandler:
    def __init__(self, db_name: str):
        self._connection = None
        self._cursor = None

        self._connection = sqlite3.connect(db_name)
        self._cursor = self._connection.cursor()
        logger.debug(f'Database created: {db_name}')

    def _is_database_empty(self) -> bool:
        result = self._cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
        return len(result.fetchall()) == 0

    def _table_exists(self, table_name: str) -> bool:
        result = self._cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
        for row in result.fetchall():
            if row[0] == table_name:
                return True
        return False

    def _create_table(self, table_name: str):
        self._cursor.execute("CREATE TABLE IF NOT EXISTS {} (__ID INTEGER PRIMARY KEY AUTOINCREMENT, __IP TEXT);"
                             .format(table_name))
        self._connection.commit()

    def _drop_table(self, table_name: str):
        self._cursor.execute("DROP TABLE IF EXISTS {};".format(table_name))
        self._connection.commit()

    def _get_column_list(self, table_name: str) -> List:
        result = self._cursor.execute("SELECT * FROM {};".format(table_name))
        return [row[0] for row in result.description if row[0] not in ['__ID', '__IP']]

    def add_data(self, table_name: str, columns: List, data: List[List], ip: str):
        self._create_table(table_name)
        existed_columns = self._get_column_list(table_name)

        logger.debug(f'Add data to database table {table_name}')

        col_diff = [column for column in columns if column not in existed_columns]
        for c in col_diff:
            query = "ALTER TABLE {} ADD COLUMN {} TEXT;".format(table_name, c)
            logger.debug(query)
            self._cursor.execute(query)

        column_str = '__IP, '+", ".join(columns)
        for row in data:
            escaped_row = ["\'" + str(r) + "\'" for r in row]
            row_str = '\'{}\', '.format(ip) + ", ".join(escaped_row)
            query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table_name, column_str, row_str)
            logger.debug(query)
            self._cursor.execute(query)

        self._connection.commit()

    def disconnect(self):
        self._connection.close()
