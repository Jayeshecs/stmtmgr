import csv
from database import DatabaseManager
from utils import debug

class ReportGenerator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def generate_csv_report(self, output_file):
        """
        Generates a CSV report of exact and potential duplicates.

        :param output_file: The path to the output CSV file.
        """
        exact_duplicates = self.db_manager.get_exact_duplicates()
        potential_duplicates = self.db_manager.get_potential_duplicates()

        with open(output_file, mode='w', newline='') as csvfile:
            fieldnames = ['Relative Full Path', 'Filename', 'Duplicate Type', 'Duplicate File Path', 'Duplicate Filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            # Process exact duplicates
            for record in exact_duplicates:
                filename = record['filename']
                path = record['path']
                hash_value = record['hash']

                debug(f"Looking for exact duplicate of {filename} at {path} with hash {hash_value}")

                # Find duplicates with the same hash
                for drecord in exact_duplicates:
                    dfilename = drecord['filename']
                    dpath = drecord['path']
                    dhash_value = drecord['hash']

                    if dhash_value == hash_value and dpath != path:
                        debug(f"Potential duplicate found: {dhash_value} == {hash_value} ? {dhash_value == hash_value} at {dpath}")
                        writer.writerow({
                            'Relative Full Path': path,
                            'Filename': filename,
                            'Duplicate Type': 'POTENTIAL',
                            'Duplicate File Path': dpath,
                            'Duplicate Filename': dfilename
                        })
                duplicates = [r for r in exact_duplicates if r['hash'] == hash_value and r['path'] != path]
                for duplicate in duplicates:
                    writer.writerow({
                        'Relative Full Path': path,
                        'Filename': filename,
                        'Duplicate Type': 'EXACT',
                        'Duplicate File Path': duplicate['path'],
                        'Duplicate Filename': duplicate['filename']
                    })

            # Process potential duplicates
            for record in potential_duplicates:
                filename = record['filename']
                path = record['path']
                hash_value = record['hash']

                debug(f"Looking for potential duplicate of {filename} at {path} with hash {hash_value}")

                # Find duplicates with the same hash
                duplicates = [r for r in potential_duplicates if r['hash'] == hash_value and r['path'] != path]
                for drecord in potential_duplicates:
                    dfilename = drecord['filename']
                    dpath = drecord['path']
                    dhash_value = drecord['hash']

                    if dhash_value == hash_value and dpath != path:
                        debug(f"Potential duplicate found: {dhash_value} == {hash_value} ? {dhash_value == hash_value} at {dpath}")
                        writer.writerow({
                            'Relative Full Path': path,
                            'Filename': filename,
                            'Duplicate Type': 'POTENTIAL',
                            'Duplicate File Path': dpath,
                            'Duplicate Filename': dfilename
                        })
