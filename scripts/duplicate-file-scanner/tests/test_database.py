import unittest
from src.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseManager('test_index.db')
        self.db_manager.create_table()

    def tearDown(self):
        self.db_manager.close()
        import os
        if os.path.exists('test_index.db'):
            os.remove('test_index.db')

    def test_insert_file_data(self):
        file_data = {
            'file_path': 'test_file.txt',
            'file_hash': 'abc123',
            'file_size': 1024
        }
        self.db_manager.insert_file_data(file_data)
        result = self.db_manager.retrieve_duplicates('abc123')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['file_path'], 'test_file.txt')

    def test_retrieve_duplicates(self):
        file_data_1 = {
            'file_path': 'test_file_1.txt',
            'file_hash': 'abc123',
            'file_size': 1024
        }
        file_data_2 = {
            'file_path': 'test_file_2.txt',
            'file_hash': 'abc123',
            'file_size': 2048
        }
        self.db_manager.insert_file_data(file_data_1)
        self.db_manager.insert_file_data(file_data_2)
        duplicates = self.db_manager.retrieve_duplicates('abc123')
        self.assertEqual(len(duplicates), 2)

    def test_no_duplicates(self):
        file_data = {
            'file_path': 'unique_file.txt',
            'file_hash': 'xyz789',
            'file_size': 512
        }
        self.db_manager.insert_file_data(file_data)
        result = self.db_manager.retrieve_duplicates('abc123')
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()