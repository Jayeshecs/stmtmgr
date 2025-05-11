import os
import pandas as pd
import hashlib
from .statement_processor import StatementProcessor


class HdfcBankAcctStatementProcessor(StatementProcessor):
    """Processor for HDFC Bank Account Statements."""

    def __init__(self, txn_store):
        """Initialize with a transaction store."""
        super().__init__(txn_store)
        
    def statement_type(self):
        """Return the statement type."""
        return "hdfc-sa"

    def parse_statement(self, file_path):
        # Read the XLS file
        df = pd.read_excel(file_path, header=None)

        # Extract txn-source from the first 6 digits of the filename
        file_name = os.path.basename(file_path)
        txn_source = file_name[:6]

        # Find the header row where the first column value is "Date"
        header_row_index = df[df[0] == "Date"].index[0]
        start_row_index = header_row_index + 2
        df.columns = df.iloc[header_row_index]
        df = df.loc[start_row_index:].reset_index(drop=True)

        print(f"Header Row Index: {header_row_index}, Start Row Index: {start_row_index}")

        # Rename columns for easier access
        df.rename(columns={
            "Date": "txn_date",
            "Narration": "narration",
            "Chq./Ref.No.": "chq_ref_no",
            "Withdrawal Amt.": "withdrawal_amt",
            "Deposit Amt.": "deposit_amt",
            "Closing Balance": "closing_balance"
        }, inplace=True)

        # Process each transaction record
        transactions = []
        for _, row in df.iterrows():
            if pd.isna(row['txn_date']) or pd.isnull(row['txn_date']):
                break
            raw_data = f"{row['txn_date']}|{row['narration']}|{row['chq_ref_no']}|{row['withdrawal_amt']}|{row['deposit_amt']}|{row['closing_balance']}"
            row_id = hashlib.md5(raw_data.encode()).hexdigest()
            txn_date = pd.to_datetime(row['txn_date'], format='%d/%m/%y').strftime('%Y-%m-%d')
            txn_amount = row['withdrawal_amt'] if not pd.isna(row['withdrawal_amt']) else row['deposit_amt']
            credit_indicator = "Yes" if not pd.isna(row['deposit_amt']) else ""

            transaction = {
                "row-id": row_id,
                "txn-source": txn_source,
                "txn-date": txn_date,
                "narration": row['narration'],
                "txn-amount": txn_amount,
                "credit-indicator": credit_indicator,
                "txn-type": "",
                "category": "",
                "sub-category": "",
                "raw-data": raw_data
            }
            transactions.append(transaction)

        # Store transactions in the consolidated CSV file
        self.store_transactions(transactions)
