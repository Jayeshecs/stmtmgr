// src/statement_processor.rs
use crate::txn_store::TxnStore;
use serde_json::to_string;
use serde::Serialize;
use wasm_bindgen::JsValue;

pub struct StatementProcessorBase {
    txn_store: TxnStore,
    statement_type: String,
}

impl StatementProcessorBase {
    pub fn new(txn_store: TxnStore, statement_type: String) -> Self {
        Self { txn_store, statement_type }
    }

    pub fn statement_type(&self) -> String {
        self.statement_type.clone()
    }

    pub fn txn_store(&self) -> &TxnStore {
        &self.txn_store
    }

    pub fn store_transactions(&self, transactions: Vec<Transaction>) {
        let json = to_string(&transactions).expect("Failed to serialize transactions");
        let js_value = JsValue::from_str(&json);
        self.txn_store.store_transactions(js_value);
        self.txn_store.export_transactions();
    }
}

pub trait StatementProcessor {
    fn statement_type(&self) -> String;
    fn txn_store(&self) -> &TxnStore;
    fn parse_statement(&self, file_path: &str) -> Result<(), Box<dyn std::error::Error>>;
    fn store_transactions(&self, transactions: Vec<Transaction>);
}

#[derive(Serialize)]
pub struct Transaction {
    pub row_id: String,
    pub txn_source: String,
    pub txn_date: String,
    pub narration: String,
    pub txn_amount: f64,
    pub credit_indicator: String,
    pub txn_type: String,
    pub category: String,
    pub sub_category: String,
    pub raw_data: String,
}