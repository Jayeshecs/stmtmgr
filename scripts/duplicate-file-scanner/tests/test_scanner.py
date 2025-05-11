import os
import unittest
from src.scanner import FileScanner

class TestFileScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = FileScanner()

    def test_scan_empty_directory(self):
        empty_dir = 'test_empty_dir'
        os.makedirs(empty_dir, exist_ok=True)
        result = self.scanner.scan(empty_dir)
        self.assertEqual(result, [])
        os.rmdir(empty_dir)

    def test_scan_directory_with_files(self):
        test_dir = 'test_dir'
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
            f.write('Hello World')
        with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
            f.write('Hello World')
        result = self.scanner.scan(test_dir)
        self.assertGreater(len(result), 0)
        os.remove(os.path.join(test_dir, 'file1.txt'))
        os.remove(os.path.join(test_dir, 'file2.txt'))
        os.rmdir(test_dir)

    def test_identify_exact_duplicates(self):
        test_dir = 'test_duplicate_dir'
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
            f.write('Duplicate Content')
        with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
            f.write('Duplicate Content')
        result = self.scanner.scan(test_dir)
        duplicates = self.scanner.find_duplicates(result)
        self.assertEqual(len(duplicates), 1)
        os.remove(os.path.join(test_dir, 'file1.txt'))
        os.remove(os.path.join(test_dir, 'file2.txt'))
        os.rmdir(test_dir)

    def test_identify_potential_duplicates(self):
        test_dir = 'test_potential_duplicate_dir'
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
            f.write('Hello World')
        with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
            f.write('Hello World!')
        result = self.scanner.scan(test_dir)
        potential_duplicates = self.scanner.find_potential_duplicates(result)
        self.assertGreater(len(potential_duplicates), 0)
        os.remove(os.path.join(test_dir, 'file1.txt'))
        os.remove(os.path.join(test_dir, 'file2.txt'))
        os.rmdir(test_dir)

if __name__ == '__main__':
    unittest.main()