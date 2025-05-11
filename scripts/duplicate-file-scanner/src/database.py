import os
import sqlite3
import hashlib
from utils import extract_first_n_bytes, debug, error, info

class DatabaseManager:
    def __init__(self, db_path='db/index.db'):
        info(f"Connecting to database at {db_path}...")
        self.connection = sqlite3.connect(db_path)
        info(f"Connected to database at {db_path}.")

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL,
                    relative_full_path TEXT NOT NULL UNIQUE,
                    file_size INTEGER NOT NULL,
                    creation_time TEXT NOT NULL,
                    first_10_bytes TEXT NOT NULL,
                    exact_match_hash TEXT NOT NULL,
                    potential_match_hash TEXT NOT NULL
                )
            ''')

    def insert_file(self, relative_full_path, metadata):
        """
        Inserts or updates a file record in the database.

        :param relative_full_path: The relative path of the file.
        :param metadata: A dictionary containing file metadata (size, created_time, filename).
        """
        debug(f"Inserting/updating file: {relative_full_path}...")
        # Extract metadata
        filename = metadata["filename"]
        file_size = metadata["size"]
        creation_time = metadata["created_time"]

        # Read the first 10 bytes of the file
        first_10_bytes = extract_first_n_bytes(relative_full_path, 10)

        # Generate hashes
        # Generate exact match hash and potential match hash

        # Generate exact match hash
        # This hash is based on the filename, file size, creation time, and the first 10 bytes
        # This is a simplified example; in a real-world scenario, you might want to use a more complex method
        # to generate a hash.
        # For example, you could use a combination of the filename, file size, creation time, and a hash of the first 10 bytes.
        # The exact match hash is a unique identifier for the file.
        # It should be unique for each file, even if the file is renamed or moved.
        exact_match_hash = hashlib.sha256(
            f"{filename}{file_size}{creation_time}{first_10_bytes}".encode()
        ).hexdigest()

        # Generate potential match hash
        # This hash is based on file size and the first 10 bytes
        # This is a simplified example; in a real-world scenario, you might want to use a more complex method
        # to generate a potential match hash.
        # For example, you could use a combination of file size and a hash of the first 10 bytes.
        potential_match_hash = hashlib.sha256(
            f"{file_size}{first_10_bytes}".encode()
        ).hexdigest()

        # Insert or update the record
        with self.connection:
            debug(f"Inserting/updating file: {filename}, Path: {relative_full_path}")
            self.connection.execute('''
                INSERT INTO files (
                    filename, relative_full_path, file_size, creation_time, 
                    first_10_bytes, exact_match_hash, potential_match_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(relative_full_path) DO UPDATE SET
                    filename=excluded.filename,
                    file_size=excluded.file_size,
                    creation_time=excluded.creation_time,
                    first_10_bytes=excluded.first_10_bytes,
                    exact_match_hash=excluded.exact_match_hash,
                    potential_match_hash=excluded.potential_match_hash
            ''', (filename, relative_full_path, file_size, creation_time,
                  first_10_bytes.hex(), exact_match_hash, potential_match_hash))

    def get_exact_duplicates(self):
        info(f"Fetching exact duplicates from the database...")
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT exact_match_hash, filename, relative_full_path, file_size
            FROM files
            WHERE exact_match_hash IN (
                SELECT exact_match_hash
                FROM files
                GROUP BY exact_match_hash
                HAVING COUNT(*) > 1
            )
            ORDER BY exact_match_hash
        ''')
        results = cursor.fetchall()
        info(f"Found {len(results)} exact duplicates.")
        # Convert results to a list of dictionaries
        return [{'hash': row[0], 'filename': row[1], 'path': row[2], 'size': row[3]} for row in results]
    
    def get_potential_duplicates(self):
        info(f"Fetching potential duplicates from the database...")
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT potential_match_hash, filename, relative_full_path, file_size
            FROM files
            WHERE potential_match_hash IN (
                SELECT potential_match_hash
                FROM files
                GROUP BY potential_match_hash
                HAVING COUNT(*) > 1
            )
            ORDER BY potential_match_hash
        ''')
        results = cursor.fetchall()
        info(f"Found {len(results)} potential duplicates.")
        # Convert results to a list of dictionaries
        return [{'hash': row[0], 'filename': row[1], 'path': row[2], 'size': row[3]} for row in results]

    def close(self):
        info("Closing database connection...")
        self.connection.close()
        info("Closing database connection...done.")
