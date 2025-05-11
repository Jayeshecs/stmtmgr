import os
import sys
import unittest

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from processors.statement_processor_provider import StatementProcessorProvider
from processors.hdfc_bank_acct_processor import HdfcBankAcctStatementProcessor
from processors.hdfc_credit_card_processor import HdfcCreditCardStatementProcessor
from store.txn_store import TxnStore

class TestStatementProcessorProvider(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary SQLite database and CSV file for testing.

        This method is executed before each test to ensure a clean environment.
        """
        print("Setting up test db and test file...")
        self.test_db_file = ":memory:" # Use an in-memory database for testing
        self.test_csv_file = "../../test_output/test_consolidated_transactions2.csv"
        self.txn_store = TxnStore(self.test_db_file, self.test_csv_file)
        self.provider = StatementProcessorProvider()

    def tearDown(self):
        """
        Clean up the temporary database and CSV file after testing.

        This method is executed after each test to remove any temporary files created during the test.
        """
        print("Cleaning up test files...")
        # Explicitly close the SQLite connection if it is open
        if self.txn_store:
            self.txn_store.close()
            
        # Remove the test database and CSV file if they exist
        # (this is a good practice to avoid cluttering the file system with test artifacts)
        if os.path.exists(self.test_csv_file):
            print(f"Removing test CSV file: {self.test_csv_file}")
            os.remove(self.test_csv_file)

    def test_get_hdfc_bank_acct_processor(self):
        processor = self.provider.get_processor("hdfc-sa", self.txn_store)
        self.assertIsInstance(processor, HdfcBankAcctStatementProcessor)
        self.assertEqual(processor.statement_type(), "hdfc-sa")
        self.assertIsNotNone(processor.txn_store)
        self.assertEqual(processor.txn_store, self.txn_store)
    
    def test_get_hdfc_credit_card_processor(self):
        processor = self.provider.get_processor("hdfc-cc", self.txn_store)
        self.assertIsInstance(processor, HdfcCreditCardStatementProcessor)
        self.assertEqual(processor.statement_type(), "hdfc-cc")
        self.assertIsNotNone(processor.txn_store)
        self.assertEqual(processor.txn_store, self.txn_store)


if __name__ == '__main__':
    unittest.main()