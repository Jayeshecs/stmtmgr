import pandas as pd
import os
import sqlite3
import enum

"""
txn_store.py
This module provides a class to handle storing transactions in an SQLite database and exporting them to a CSV file.
"""
class TxnState:
    """Enum-like class to represent the state of a transaction."""
    PENDING_CLASSIFICATION = "PENDING_CLASSIFICATION"
    PENDING_REVIEW = "PENDING_REVIEW"
    ACCEPTED = "ACCEPTED"

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
            cursor.execute(f"""
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
                    state TEXT DEFAULT '{TxnState.PENDING_CLASSIFICATION}'
                )
            """)
            # Add column 'state' if it doesn't exist
            # Check if 'state' column exists before adding
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'state' not in columns:
                cursor.execute(f"""
                           ALTER TABLE transactions
                           ADD COLUMN state TEXT DEFAULT '{TxnState.PENDING_CLASSIFICATION}'
                           """)
            
            # Update state for existing transactions if txn_type is not empty
            cursor.execute("""
                UPDATE transactions
                SET state = ?
                WHERE state = ? and txn_type IS NOT NULL AND txn_type != ''
            """, (TxnState.PENDING_REVIEW, TxnState.PENDING_CLASSIFICATION))
            # Commit the changes
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
                            txn_amount, credit_indicator, txn_type, category, sub_category, raw_data, state
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        transaction["raw-data"],
                        TxnState.PENDING_CLASSIFICATION  # Default state
                    ))
                except sqlite3.IntegrityError:
                    # Skip duplicate transactions (row_id is the primary key)
                    pass
            conn.commit()

    def export_transactions(self):
        """Export transactions from the SQLite database to a CSV file."""
        with self.conn as conn:
            df = pd.read_sql_query("SELECT row_id, txn_source, txn_date, narration, txn_amount, credit_indicator, txn_type, category, sub_category, raw_data, state FROM transactions", conn)
            df.to_csv(self.csv_file, index=False)

    def update_transactions_from_csv(self, updated_csv_file):
        """Update type, category, and sub-category in transactions from a CSV file."""
        updated_df = pd.read_csv(updated_csv_file)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for _, row in updated_df.iterrows():
                state = TxnState.PENDING_REVIEW
                # Check if the transaction is accepted
                if row['state'] == TxnState.ACCEPTED:
                    state = TxnState.ACCEPTED
                # Update the transaction in the database
                cursor.execute("""
                    UPDATE transactions
                    SET txn_type = ?, category = ?, sub_category = ?, state = ?
                    WHERE raw_data = ?
                """, (row['type'], row['category'], row['sub-category'], state, row['raw_data']))
            conn.commit()

    def get_transactions(self):
        """Retrieve all transactions as a DataFrame."""
        query = "SELECT raw_data, txn_source, txn_amount, narration, credit_indicator, txn_date, txn_type, category, sub_category, state FROM transactions"
        return pd.read_sql_query(query, self.conn)

    def update_transactions(self, raw_data_list, txn_type, category, sub_category, state = TxnState.PENDING_REVIEW):
        """Update transactions with the given classifications."""
        with self.conn as conn:
            cursor = conn.cursor()
            for raw_data in raw_data_list:
                cursor.execute("""
                    UPDATE transactions
                    SET txn_type = ?,
                        category = ?,
                        sub_category = ?,
                        state = ?
                    WHERE raw_data = ?
                """, (txn_type, category, sub_category, state, raw_data))
            conn.commit()

    def update_transaction(self, txn_date, narration, txn_amnt, credit_indicator, txn_type, category, sub_category, state=TxnState.PENDING_REVIEW):
        """
        Update a specific transaction based on date, narration, amount, and credit indicator.
        Returns the number of rows updated, or 0 if no matching transaction is found.
        """
        # Convert txn_date to string if it's a pandas Timestamp
        if hasattr(txn_date, 'strftime'):
            txn_date = txn_date.strftime('%Y-%m-%d')
        elif not isinstance(txn_date, str):
            txn_date = str(txn_date)
        # Convert txn_amnt to float if it's a string with commas
        if isinstance(txn_amnt, str):
            txn_amnt = txn_amnt.replace(',', '')
            try:
                txn_amnt = float(txn_amnt)
            except ValueError:
                print(f"Invalid transaction amount: {txn_amnt}. Update skipped.")
                return 0
        # Ensure credit_indicator is a string
        if credit_indicator is None:
            credit_indicator = ''
        if not isinstance(credit_indicator, str):
            credit_indicator = ''
        
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
                    sub_category = ?,
                    state = ?
                WHERE txn_date = ? AND narration = ? AND (CAST(REPLACE(txn_amount, ',', '') AS REAL) - ?) < 0.01 AND credit_indicator = ?
            """, (txn_type, category, sub_category, state, txn_date, narration, txn_amnt, credit_indicator))
            updated_count = cursor.rowcount
            conn.commit()
            return updated_count
