// src/lib.rs
use wasm_bindgen::prelude::*;
use web_sys::console;

#[wasm_bindgen]
pub fn greet() {
    // Log a message to the browser's console
    console::log_1(&"Hello from Rust WebAssembly!".into());
}

// Additional exports can be added here to expose functionality from other modules.
pub mod txn_store;
pub mod hdfc_bank_acct_processor;
pub mod hdfc_credit_card_processor;
pub mod statement_processor;
pub mod statement_processor_provider; // Add this line