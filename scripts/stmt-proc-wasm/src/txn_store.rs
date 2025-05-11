// src/txn_store.rs
use wasm_bindgen::prelude::*;
use serde::Serialize;
use wasm_bindgen::JsValue;
use js_sys::eval;

#[wasm_bindgen]
pub struct TxnStore {
    csv_file: String,
}

pub fn execute_js(js_code: &str) -> Result<JsValue, JsValue> {
    eval(js_code)
}

#[wasm_bindgen]
impl TxnStore {
    #[wasm_bindgen(constructor)]
    pub fn new(csv_file: &str) -> Self {
        TxnStore {
            csv_file: csv_file.to_string(),
        }
    }

    #[wasm_bindgen]
    pub fn store_transactions(&self, transactions: JsValue) {
        // Pass the transactions to JavaScript for storage in SQLite
        // `transactions` is expected to be a JSON array of transaction objects
        let transactions_str = transactions.as_string().unwrap_or_else(|| "Invalid JsValue".to_string());
        let js_code = format!(
            r#"
            (async () => {{
                const db = await window.sqlite.open(':memory:');
                await db.exec(`
                    CREATE TABLE IF NOT EXISTS transactions (
                        row_id TEXT PRIMARY KEY,
                        txn_source TEXT,
                        txn_date TEXT,
                        narration TEXT,
                        txn_amount REAL,
                        credit_indicator TEXT,
                        txn_type TEXT,
                        category TEXT,
                        sub_category TEXT,
                        raw_data TEXT
                    )
                `);

                const transactions = {};
                for (const txn of transactions) {{
                    try {{
                        await db.run(`
                            INSERT INTO transactions (
                                row_id, txn_source, txn_date, narration,
                                txn_amount, credit_indicator, txn_type, category, sub_category, raw_data
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        `, [
                            txn.row_id,
                            txn.txn_source,
                            txn.txn_date,
                            txn.narration,
                            txn.txn_amount,
                            txn.credit_indicator,
                            txn.txn_type,
                            txn.category,
                            txn.sub_category,
                            txn.raw_data
                        ]);
                    }} catch (e) {{
                        // Skip duplicate transactions (row_id is the primary key)
                        console.error(e);
                    }}
                }}
            }})();
            "#,
            transactions_str
        );

        // Execute the JavaScript code
        let result = execute_js(&js_code);
        if let Err(e) = result {
            eprintln!("Failed to execute JavaScript code: {:?}", e);
        }
    }

    #[wasm_bindgen]
    pub fn export_transactions(&self) {
        // Export transactions to a CSV file using JavaScript
        let js_code = format!(
            r#"
            (async () => {{
                const db = await window.sqlite.open(':memory:');
                const rows = await db.all(`
                    SELECT row_id, txn_source, txn_date, narration, txn_amount, credit_indicator, txn_type, category, sub_category, raw_data
                    FROM transactions
                `);

                const csvContent = rows.map(row => Object.values(row).join(',')).join('\n');
                const blob = new Blob([csvContent], {{ type: 'text/csv' }});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = '{}';
                a.click();
            }})();
            "#,
            self.csv_file
        );

        // Execute the JavaScript code
        let result = execute_js(&js_code);
        if let Err(e) = result {
            eprintln!("Failed to execute JavaScript code: {:?}", e);
        }
    }
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