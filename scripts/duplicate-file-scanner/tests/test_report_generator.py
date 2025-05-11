import unittest
import os
import csv
from src.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.report_generator = ReportGenerator()
        self.test_data = [
            {'file_path': 'path/to/file1.txt', 'duplicate_type': 'exact'},
            {'file_path': 'path/to/file2.txt', 'duplicate_type': 'potential'},
        ]
        self.output_csv = 'test_report.csv'

    def test_generate_csv_report(self):
        self.report_generator.generate_csv_report(self.test_data, self.output_csv)
        self.assertTrue(os.path.exists(self.output_csv))

        with open(self.output_csv, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            self.assertEqual(len(rows), len(self.test_data))
            for i, row in enumerate(rows):
                self.assertEqual(row['file_path'], self.test_data[i]['file_path'])
                self.assertEqual(row['duplicate_type'], self.test_data[i]['duplicate_type'])

    def tearDown(self):
        if os.path.exists(self.output_csv):
            os.remove(self.output_csv)

if __name__ == '__main__':
    unittest.main()