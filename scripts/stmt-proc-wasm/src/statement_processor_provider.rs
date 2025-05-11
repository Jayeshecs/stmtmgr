use crate::hdfc_bank_acct_processor::HdfcBankAcctStatementProcessor;
use crate::hdfc_credit_card_processor::HdfcCreditCardStatementProcessor;
use crate::statement_processor::StatementProcessor;
use crate::txn_store::TxnStore;

pub struct StatementProcessorProvider;

impl StatementProcessorProvider {
    /// Factory method to get the appropriate statement processor.
    pub fn get_processor(key: &str, txn_store: TxnStore) -> Result<Box<dyn StatementProcessor>, String> {
        match key {
            "hdfc-sa" => Ok(Box::new(HdfcBankAcctStatementProcessor::new(txn_store))),
            "hdfc-cc" => Ok(Box::new(HdfcCreditCardStatementProcessor::new(txn_store))),
            _ => Err(format!("Unsupported statement type: {}", key)),
        }
    }
}