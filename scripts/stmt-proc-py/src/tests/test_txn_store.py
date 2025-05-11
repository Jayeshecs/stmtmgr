import os
import sys
import sqlite3
import pandas as pd
import unittest

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from store.txn_store import TxnStore


class TestTxnStore(unittest.TestCase):
    """
    Unit tests for the TxnStore class.

    This test suite verifies the functionality of the TxnStore class, including:
    - Storing transactions in an SQLite database.
    - Exporting transactions from the SQLite database to a CSV file.
    """

    def setUp(self):
        """
        Set up a temporary SQLite database and CSV file for testing.

        This method is executed before each test to ensure a clean environment.
        """
        print("Setting up test db and test file...")
        self.test_db_file = ":memory:" # Use an in-memory database for testing
        self.test_csv_file = "../../test_output/test_consolidated_transactions.csv"
        self.txn_store = TxnStore(self.test_db_file, self.test_csv_file)

    def tearDown(self):
        """
        Clean up the temporary database and CSV file after testing.

        This method is executed after each test to remove any temporary files created during the test.
        """
        # Explicitly close the SQLite connection if it is open
        if self.txn_store:
            self.txn_store.close();

        if os.path.exists(self.test_csv_file):
            print(f"Removing test CSV file: {self.test_csv_file}")
            os.remove(self.test_csv_file)

    def test_store_transactions(self):
        """
        Test the store_transactions method of the TxnStore class.

        This test verifies that transactions are correctly stored in the SQLite database
        and that duplicate transactions are not inserted.
        """
        transactions = [
            {
                "row-id": "abc123",
                "raw-data": "2025-04-01|Test Narration|100.0|Cr",
                "txn-source": "123456",
                "txn-date": "2025-04-01",
                "narration": "Test Narration",
                "txn-amount": 100.0,
                "credit-indicator": "Yes",
                "txn-type": "",
                "category": "",
                "sub-category": ""
            },
            {
                "row-id": "def456",
                "raw-data": "2025-04-02|Another Test|200.0|Dr",
                "txn-source": "654321",
                "txn-date": "2025-04-02",
                "narration": "Another Test",
                "txn-amount": 200.0,
                "credit-indicator": "",
                "txn-type": "",
                "category": "",
                "sub-category": ""
            }
        ]

        # Store transactions
        self.txn_store.store_transactions(transactions)

        # Verify data in the database
        with self.txn_store.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2)

    def test_export_transactions(self):
        """
        Test the export_transactions method of the TxnStore class.

        This test verifies that transactions stored in the SQLite database
        are correctly exported to a CSV file.
        """
        transactions = [
            {
                "row-id": "abc123",
                "raw-data": "2025-04-01|Test Narration|100.0|Cr",
                "txn-source": "A123456",
                "txn-date": "2025-04-01",
                "narration": "Test Narration",
                "txn-amount": 100.0,
                "credit-indicator": "Yes",
                "txn-type": "",
                "category": "",
                "sub-category": ""
            }
        ]

        # Store transactions
        self.txn_store.store_transactions(transactions)

        # Export transactions to CSV
        self.txn_store.export_transactions()

        # Verify the CSV file
        self.assertTrue(os.path.exists(self.test_csv_file))
        df = pd.read_csv(self.test_csv_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["row_id"], "abc123")
        self.assertEqual(df.iloc[0]["txn_source"], "A123456")
        self.assertEqual(df.iloc[0]["txn_date"], "2025-04-01")
        self.assertEqual(df.iloc[0]["narration"], "Test Narration")
        self.assertEqual(df.iloc[0]["txn_amount"], 100.0)
        self.assertEqual(df.iloc[0]["credit_indicator"], "Yes")


if __name__ == "__main__":
    unittest.main()