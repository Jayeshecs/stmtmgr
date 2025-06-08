import os
import sys
import pandas as pd
import unittest

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from store.txn_store import TxnStore
from classifier.classifier import Classifier

class TestClassifier(unittest.TestCase):
    """
    Unit tests for the Classifier class.

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
        self.classifier = Classifier(self.txn_store)

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
    
if __name__ == "__main__":
    unittest.main()