// src/hdfc_credit_card_processor.rs
use std::error::Error;
use std::fs::File;
use std::path::Path;
use std::io::BufReader;
use calamine::{open_workbook, Reader, Xlsx};

use crate::statement_processor::{StatementProcessor, StatementProcessorBase, Transaction};
use crate::txn_store::TxnStore;

pub struct HdfcCreditCardStatementProcessor {
    base: StatementProcessorBase,
}

impl HdfcCreditCardStatementProcessor {
    pub fn new(txn_store: TxnStore) -> Self {
        Self {
            base: StatementProcessorBase::new(txn_store, "hdfc-cc".to_string()),
        }
    }
}

fn calculate_md5(data: &str) -> String {
    let digest = md5::compute(data);
    format!("{:x}", digest)
}

pub fn read_excel(file_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let mut workbook: Xlsx<_> = open_workbook(file_path)?;
    if let Some(Ok(range)) = workbook.worksheet_range("Sheet1") {
        for row in range.rows() {
            println!("{:?}", row);
        }
    }
    Ok(())
}

impl StatementProcessor for HdfcCreditCardStatementProcessor {

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
        let file = File::open(file_path)?;
        let reader = BufReader::new(file);
        let mut rdr = csv::ReaderBuilder::new().has_headers(false).from_reader(reader);

        let txn_source = Path::new(file_path)
            .file_name()
            .unwrap()
            .to_str()
            .unwrap()[..6]
            .to_string();

        let mut transactions: Vec<Transaction> = Vec::new();

        for result in rdr.records() {
            let record = result?;
            let txn_date = &record[17]; // 18th column
            let narration = &record[21]; // 22nd column
            let txn_amount: f64 = record[48].parse()?;
            let debit_credit = &record[54]; // 55th column

            if txn_date.is_empty() {
                break;
            }

            let raw_data = format!("{}|{}|{}|{}", txn_date, narration, txn_amount, debit_credit);
            let row_id = calculate_md5(&raw_data);

            let txn_date = txn_date[..10].to_string(); // Assuming date format is correct
            let credit_indicator = if debit_credit == "Cr" { "Yes" } else { "" };

            let transaction = Transaction {
                row_id,
                txn_source: txn_source.to_string(),
                txn_date,
                narration: narration.to_string(),
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