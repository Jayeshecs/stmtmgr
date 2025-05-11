# Statement Manager (stmtmgr)

Statement Manager (stmtmgr) is a project designed to manage bank account statements and credit card statements. The project provides tools for processing, classifying, and analyzing financial transactions to deliver insights and streamline financial management.

## Key Features

- **Statement Processing**: Converts raw statements into a columnar data store with the following data points:
  - **Account**: Source of the transaction
  - **Date**: The transaction date
  - **Narration**: The narration of the transaction
  - **Amount**: The transaction amount
  - **Cr**: Indicator of credit or debit transaction (`Yes` for credit, otherwise debit)
  - **Type**: The type of transaction
  - **Category**: The category of the transaction
  - **Sub-category**: The sub-category of the transaction

- **Statement Classification**: Classifies transactions and assigns values for `Type`, `Category`, and `Sub-category`. Includes a web application for user interaction to refine classifications and apply them to similar transactions.

- **Statement Analysis**: Analyzes categorized transactions to generate cashflow statements:
  - **Income**: Monthly & Yearly
  - **Expense**: Monthly & Yearly
  - **Savings**: Monthly & Yearly

- **Customizable Month Start Date**: Allows setting a custom start date for a month (e.g., 25th as the 1st day of the month and 24th as the last day).

## Components

### 1. Statement Processors
- **`stmt-proc-py`**: A Python-based processor for server-side processing of statements, ideal for handling large volumes of transactions.
- **`stmt-proc-wasm`**: A Rust-based WebAssembly processor for in-browser processing, ensuring no financial data is uploaded to a server.

### 2. Statement Classifier
A web application that:
- Displays transactions processed by the statement processor.
- Allows users to set `Type`, `Category`, and `Sub-category` values for transactions.
- Automatically scans for similar transactions and suggests applying the same values.

### 3. Statement Analyzer
Analyzes categorized transactions to prepare detailed cashflow statements:
- **Income**: Monthly & Yearly
- **Expense**: Monthly & Yearly
- **Savings**: Monthly & Yearly

## Usage Scenarios

- **In-Browser Processing**: Use `stmt-proc-wasm` for secure, client-side processing of statements.
- **Server-Side Processing**: Use `stmt-proc-py` for efficient processing of large statements.
- **Transaction Classification**: Use the `stmt-classifier` web application to refine and categorize transactions.
- **Financial Analysis**: Use `stmt-analyzer` to generate cashflow insights.

## Getting Started

1. Clone the repository.
2. Follow the setup instructions for the desired component (`stmt-proc-py`, `stmt-proc-wasm`, `stmt-classifier`, or `stmt-analyzer`).
3. Process, classify, and analyze your financial statements.

## License

This project is licensed under the [MIT License](LICENSE).

---