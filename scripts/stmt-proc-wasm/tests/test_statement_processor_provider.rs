// This file contains unit tests for the statement processor provider.
// It tests the functionality of the various statement processors and ensures they are correctly instantiated and configured.

#[cfg(test)]
mod tests {
    use stmt_proc_wasm::txn_store::TxnStore;
    use stmt_proc_wasm::hdfc_bank_acct_processor::HdfcBankAcctStatementProcessor;
    use stmt_proc_wasm::hdfc_credit_card_processor::HdfcCreditCardStatementProcessor;
    use stmt_proc_wasm::statement_processor::StatementProcessor;
    use stmt_proc_wasm::statement_processor_provider::StatementProcessorProvider;

    #[test]
    fn test_get_hdfc_bank_acct_processor() {
        let txn_store = TxnStore::new(":memory:");
        let processor = StatementProcessorProvider::get_processor("hdfc-sa", txn_store)
            .expect("Failed to get HDFC Bank Account Processor");

        // Check that the processor is of the correct type
        assert!(processor.is::<HdfcBankAcctStatementProcessor>());
        assert_eq!(processor.statement_type(), "hdfc-sa");
    }

    #[test]
    fn test_get_hdfc_credit_card_processor() {
        let txn_store = TxnStore::new(":memory:");
        let processor = StatementProcessorProvider::get_processor("hdfc-cc", txn_store)
            .expect("Failed to get HDFC Credit Card Processor");

        // Check that the processor is of the correct type
        assert!(processor.is::<HdfcCreditCardStatementProcessor>());
        assert_eq!(processor.statement_type(), "hdfc-cc");
    }

    #[test]
    #[should_panic(expected = "Unsupported statement type")]
    fn test_get_unsupported_processor() {
        let txn_store = TxnStore::new(":memory:");
        StatementProcessorProvider::get_processor("unsupported-type", txn_store)
            .expect("Expected panic for unsupported statement type");
    }
}