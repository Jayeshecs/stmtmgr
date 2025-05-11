// src/hdfc_bank_acct_processor.rs
use std::error::Error;
use chrono::NaiveDate;
use md5;
use crate::txn_store::TxnStore;
use crate::statement_processor::{StatementProcessor, StatementProcessorBase, Transaction};
use calamine::{open_workbook, Reader, Xlsx};

pub struct HdfcBankAcctStatementProcessor {
    base: StatementProcessorBase,
}

impl HdfcBankAcctStatementProcessor {
    pub fn new(txn_store: TxnStore) -> Self {
        Self {
            base: StatementProcessorBase::new(txn_store, "hdfc-sa".to_string()),
        }
    }
}

fn calculate_md5(data: &str) -> String {
    let digest = md5::compute(data);
    format!("{:x}", digest)
}

impl StatementProcessor for HdfcBankAcctStatementProcessor {

    fn statement_type(&self) -> String {
        self.base.statement_type().to_string()
    }

    fn txn_store(&self) -> &TxnStore {
        &self.base.txn_store()
    }

    fn store_transactions(&self, transactions: Vec<Transaction>) {
        self.base.store_transactions(transactions);
    }

    fn parse_statement(&self, file_path: &str) -> Result<(), Box<dyn Error>> {
        let df = read_excel(file_path)?; // Implement read_excel to read the XLS file into a DataFrame-like structure

        let file_name = file_path.split('/').last().unwrap();
        let txn_source = &file_name[..6];

        let header_row_index = df.iter().position(|row| row[0] == "Date").ok_or("Header not found")?;
        let start_row_index = header_row_index + 2;

        let mut transactions: Vec<Transaction> = Vec::new();

        for row in df.iter().skip(start_row_index) {
            if row[0].is_empty() {
                break;
            }

            let raw_data = format!("{}|{}|{}|{}|{}|{}", row[0], row[1], row[2], row[3], row[4], row[5]);
            let row_id = calculate_md5(&raw_data);
            let txn_date = NaiveDate::parse_from_str(&row[0], "%d/%m/%y")?.format("%Y-%m-%d").to_string();
            let txn_amount = if !row[3].is_empty() { row[3].parse::<f64>()? } else { row[4].parse::<f64>()? };
            let credit_indicator = if !row[4].is_empty() { "Yes" } else { "" };

            let transaction = Transaction {
                row_id,
                txn_source: txn_source.to_string(),
                txn_date,
                narration: row[1].to_string(),
                txn_amount,
                credit_indicator: credit_indicator.to_string(),
                txn_type: "".to_string(),
                category: "".to_string(),
                sub_category: "".to_string(),
                raw_data,
            };

            transactions.push(transaction);
        }

        self.store_transactions(transactions);
        Ok(())
    }
}

pub fn read_excel(file_path: &str) -> Result<Vec<Vec<String>>, Box<dyn std::error::Error>> {
    let mut workbook: Xlsx<_> = open_workbook(file_path)?;
    let mut data = Vec::new();

    if let Some(Ok(range)) = workbook.worksheet_range("Sheet1") {
        for row in range.rows() {
            data.push(row.iter().map(|cell| cell.to_string()).collect());
        }
    }

    Ok(data)
}