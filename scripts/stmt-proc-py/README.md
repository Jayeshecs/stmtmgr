# Statement Processor (stmt-proc-py)

The `stmt-proc-py` module is designed to process bank account and credit card statements, specifically focusing on HDFC bank statements in XLS format. This module provides functionality to parse, store, and manage financial transactions efficiently.

## Key Features

- **Statement Parsing**: Parses HDFC bank account and credit card statements in XLS format.
- **Transaction Storage**: Checks for existing transactions before storing them in a consolidated CSV file.
- **Utility Functions**: Includes helper functions for reading XLS files and managing transaction data.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

1. Import the `StatementProcessor` class from the `processors` module.
2. Create an instance of `StatementProcessor`.
3. Use the `parse_hdfc_account_statement` or `parse_hdfc_credit_card_statement` methods to parse the respective statements.
4. Transactions will be stored in `consolidated_transactions.csv` if they do not already exist.

## Directory Structure

```
stmt-proc-py/
├── src/
│   ├── main.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── statement_processor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── tests/
│       ├── __init__.py
│       └── test_statement_processor.py
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).