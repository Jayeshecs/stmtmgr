import pandas as pd
import os
import sqlite3


class TxnStore:
    """Class to handle storing transactions in an SQLite database and exporting to a CSV file."""

    def __init__(self, db_file, csv_file):
        self.db_file = db_file
        self.csv_file = csv_file
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the SQLite database with the required table if it doesn't exist."""
        print(f"Initializing database at {self.db_file}...")
        if (self.db_file == ":memory:"):
            print("Using in-memory database for testing.")
        else:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        # Connect to the SQLite database (it will be created if it doesn't exist)
        # Create the transactions table if it doesn't exist
        print(f"Creating transactions table in {self.db_file}...")
        # Connect to the SQLite database
        # (it will be created if it doesn't exist)    
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Create the transactions table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    row_id TEXT PRIMARY KEY,
                    raw_data TEXT,
                    txn_source TEXT,
                    txn_date TEXT,
                    narration TEXT,
                    txn_amount REAL,
                    credit_indicator TEXT,
                    txn_type TEXT,
                    category TEXT,
                    sub_category TEXT
                )
            """)
            conn.commit()
    
    def get_connection(self):
        """Get the SQLite database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
        return self.conn
    
    def close(self):
        """Close the database connection."""
        if self.conn is not None:
            print("Closing database connection...")
            # Close the SQLite connection
            self.conn.commit()
            self.conn.close()
            self.conn = None
            print("Database connection closed.")

    def store_transactions(self, transactions):
        """Store transactions in the SQLite database."""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for transaction in transactions:
                try:
                    cursor.execute("""
                        INSERT INTO transactions (
                            row_id, txn_source, txn_date, narration,
                            txn_amount, credit_indicator, txn_type, category, sub_category, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        transaction["row-id"],
                        transaction["txn-source"],
                        transaction["txn-date"],
                        transaction["narration"],
                        transaction["txn-amount"],
                        transaction["credit-indicator"],
                        transaction["txn-type"],
                        transaction["category"],
                        transaction["sub-category"],
                        transaction["raw-data"]
                    ))
                except sqlite3.IntegrityError:
                    # Skip duplicate transactions (row_id is the primary key)
                    pass
            conn.commit()

    def export_transactions(self):
        """Export transactions from the SQLite database to a CSV file."""
        with self.conn as conn:
            df = pd.read_sql_query("SELECT row_id, txn_source, txn_date, narration, txn_amount, credit_indicator, txn_type, category, sub_category, raw_data FROM transactions", conn)
            df.to_csv(self.csv_file, index=False)