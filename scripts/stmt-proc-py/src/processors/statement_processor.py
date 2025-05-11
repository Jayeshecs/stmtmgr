from abc import ABC, abstractmethod
from store.txn_store import TxnStore


class StatementProcessor(ABC):
    """Abstract base class for statement processors."""

    def __init__(self, txn_store: TxnStore):
        """Initialize with a transaction store."""
        if not isinstance(txn_store, TxnStore):
            raise ValueError("txn_store must be an instance of TxnStore")
        self.txn_store = txn_store

    @abstractmethod
    def parse_statement(self, file_path):
        """Abstract method to parse a statement file."""
        pass

    @abstractmethod
    def statement_type(self):
        """Abstract method to get statement type."""
        pass
    
    def store_transactions(self, transactions):
        """Delegate storing transactions to the TxnStore class."""
        self.txn_store.store_transactions(transactions)
        """Export transactions to a CSV file."""
        self.txn_store.export_transactions()




