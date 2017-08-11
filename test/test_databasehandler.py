import unittest
from database.dbhandler import DataBaseHandler


class TestDatabaseHandler(unittest.TestCase):
    def setUp(self):
        self.dbname1 = 'testing_database/test1.db'
        self.dbname2 = 'testing_database/test2.db'
        self.dbname3 = 'testing_database/test3.db'
        self.dbname4 = 'testing_database/test4.db'

    def test_empty_db(self):
        dbh1 = DataBaseHandler(self.dbname1)
        self.assertTrue(dbh1._is_database_empty())

    def test_not_empty_db(self):
        dbh2 = DataBaseHandler(self.dbname2)
        self.assertFalse(dbh2._is_database_empty())

    def test_add_check_delete_table(self):
        dbh3 = DataBaseHandler(self.dbname3)
        table_name = 'test'
        with self.subTest(line='empty'):
            self.assertFalse(dbh3._table_exists(table_name))

        dbh3._create_table(table_name)
        with self.subTest(line='table created'):
            self.assertTrue(dbh3._table_exists(table_name))

        dbh3._drop_table(table_name)
        with self.subTest(line='table dropped'):
            self.assertFalse(dbh3._table_exists(table_name))

    def test_get_column_list(self):
        dbh4 = DataBaseHandler(self.dbname4)
        dbh4._drop_table('test')
        dbh4._create_table('test')
        print(dbh4._get_column_list('test'))
