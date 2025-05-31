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

    def update_transactions_from_csv(self, updated_csv_file):
        """Update type, category, and sub-category in transactions from a CSV file."""
        updated_df = pd.read_csv(updated_csv_file)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for _, row in updated_df.iterrows():
                cursor.execute("""
                    UPDATE transactions
                    SET txn_type = ?, category = ?, sub_category = ?
                    WHERE raw_data = ?
                """, (row['type'], row['category'], row['sub-category'], row['raw_data']))
            conn.commit()

    def get_transactions(self):
        """Retrieve all transactions as a DataFrame."""
        query = "SELECT raw_data, txn_source, txn_amount, narration, credit_indicator, txn_date, txn_type, category, sub_category FROM transactions"
        return pd.read_sql_query(query, self.conn)

    def update_transactions(self, raw_data_list, txn_type, category, sub_category):
        """Update transactions with the given classifications."""
        with self.conn as conn:
            cursor = conn.cursor()
            for raw_data in raw_data_list:
                cursor.execute("""
                    UPDATE transactions
                    SET txn_type = ?,
                        category = ?,
                        sub_category = ?
                    WHERE raw_data = ?
                """, (txn_type, category, sub_category, raw_data))
            conn.commit()

    def update_transaction(self, txn_date, narration, txn_amnt, credit_indicator, txn_type, category, sub_category):
        """
        Update a specific transaction based on date, narration, amount, and credit indicator.
        Returns the number of rows updated, or 0 if no matching transaction is found.
        """
        with self.conn as conn:
            cursor = conn.cursor()
            # Ensure that the transaction exists before updating
            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE txn_date = ? AND narration = ? AND (CAST(REPLACE(txn_amount, ',', '') AS REAL) - ?) < 0.01 AND credit_indicator = ?
            """, (txn_date, narration, txn_amnt, credit_indicator))
            count = cursor.fetchone()[0]
            if count == 0:
                print(f"No transaction found for date: {txn_date}, narration: {narration}, amount: {txn_amnt}, credit indicator: {credit_indicator}. Update skipped.")
                return 0
            cursor.execute("""
                UPDATE transactions
                SET txn_type = ?,
                    category = ?,
                    sub_category = ?
                WHERE txn_date = ? AND narration = ? AND (CAST(REPLACE(txn_amount, ',', '') AS REAL) - ?) < 0.01 AND credit_indicator = ?
            """, (txn_type, category, sub_category, txn_date, narration, txn_amnt, credit_indicator))
            updated_count = cursor.rowcount
            conn.commit()
            return updated_count
