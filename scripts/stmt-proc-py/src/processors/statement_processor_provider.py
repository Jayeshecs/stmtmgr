from .hdfc_bank_acct_processor import HdfcBankAcctStatementProcessor
from .hdfc_credit_card_processor import HdfcCreditCardStatementProcessor
from store.txn_store import TxnStore


class StatementProcessorProvider:
    """Factory class to provide the appropriate statement processor."""

    @staticmethod
    def get_processor(key, txn_store: TxnStore):
        if key == "hdfc-sa":
            return HdfcBankAcctStatementProcessor(txn_store)
        elif key == "hdfc-cc":
            return HdfcCreditCardStatementProcessor(txn_store)
        else:
            raise ValueError(f"Unsupported statement type: {key}")