# Contents of /stmt-proc-py/stmt-proc-py/src/main.py

import sys
import os
from processors.statement_processor_provider import StatementProcessorProvider
from store.txn_store import TxnStore
from classifier.classifier import Classifier
from classifier.auto_classifier import AutoClassifier

def detect_statement_type(file_name):
    """Detect statement type based on file name."""
    if file_name.startswith("SA"):
        return "hdfc-sa"
    elif file_name.startswith("CC"):
        return "hdfc-cc"
    else:
        raise ValueError("Unable to detect statement type from file name. Ensure the file name starts with 'SA' or 'CC'.")

def process_file(file_path, txn_store: TxnStore):
    """Process a single statement file."""
    try:
        file_name = os.path.basename(file_path)
        statement_type = detect_statement_type(file_name)
        print(f"Detected statement type: {statement_type} for file: {file_name}")

        # Get the appropriate processor instance
        processor = StatementProcessorProvider.get_processor(statement_type, txn_store)
        processor.parse_statement(file_path)
        print(f"Processed {statement_type} statement: {file_name}")
    except ValueError as e:
        print(f"Skipping file {file_path}: {e}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def classify(txn_store: TxnStore):
    """Classify transactions using the Classifier module."""
    print("Initializing classifier...")
    classifier = Classifier(txn_store)

    print("Classifying transactions...")
    classifier.classify_transactions()
    print("Classification completed successfully.")

def import_classification(txn_store: TxnStore, csv_file: str):
    """Import classification from a CSV file."""
    print("Importing classification...")
    classifier = Classifier(txn_store)

    # Prompt user for CSV file path
    
    if not os.path.isfile(csv_file):
        print(f"Error: {csv_file} is not a valid file.")
        return

    try:
        classifier.import_classification(csv_file)
        print("Classification imported successfully.")
    except Exception as e:
        print(f"Error importing classification: {e}")

def auto_classify(txn_store: TxnStore):
    """
    Automatically classify transactions using the AutoClassifier module.
    This function initializes the AutoClassifier, trains it on the transaction data,
    and applies the classification to the transactions in the store.
    It assumes that the transactions have been preprocessed and stored in the TxnStore.
    This function does not take any parameters and uses the TxnStore instance to access the transactions.
    It prints messages to indicate the progress of the auto-classification process.
    It is designed to be called from the command line interface of the application.
    It is expected to be used after the transactions have been processed and stored in the TxnStore.
    It does not return any value.
    """

    print("Auto-classifying transactions...")
    auto_classifier = AutoClassifier(txn_store)    
    auto_classifier.apply_classification()
    print("Auto-classification completed successfully.")

def auto_classify_csv_export(txn_store: TxnStore):
    """
    Export auto-classified transactions to a CSV file.
    This function retrieves the auto-classified transactions from the TxnStore
    and writes them to a CSV file for further analysis or reporting.
    It assumes that the transactions have been auto-classified using the AutoClassifier.
    It does not take any parameters and uses the TxnStore instance to access the transactions.
    It prints messages to indicate the progress of the export process.
    It is designed to be called from the command line interface of the application.
    It does not return any value.
    """
    
    print("Exporting auto-classified transactions to CSV...")
    auto_classifier = AutoClassifier(txn_store)
    auto_classifier.export_classification_to_csv('../export/auto-classification-transactions.csv')
    print("Auto-classified transactions exported successfully.")

def auto_classify_csv_import(txn_store: TxnStore):
    """
    Import updated auto-classified transactions from a CSV file.
    This function reads the auto-classified transactions from a CSV file
    and updates the TxnStore with the new classifications.
    It assumes that the CSV file contains the necessary fields for classification.
    It does not take any parameters and uses the TxnStore instance to access the transactions.
    It prints messages to indicate the progress of the import process.
    It is designed to be called from the command line interface of the application.
    It does not return any value.
    """
    
    print("Importing updated auto-classified transactions from CSV...")
    auto_classifier = AutoClassifier(txn_store)
    auto_classifier.import_classification_from_csv('../import/auto-classification-transactions.csv')
    print("Updated auto-classified transactions imported successfully.")

def main():
    # Check command line arguments for operation type
    if len(sys.argv) < 2:
        print("Usage: python main.py <operation> [additional arguments]")
        print("operation: 'process' or 'classify'")
        print("For 'process': python main.py process <statement_type> <path_to_statement_file_or_folder>")
        print("             : statement_type possible values are 'hdfc-sa', 'hdfc-cc', 'auto' or 'folder'")
        print("For 'classify': python main.py classify")
        sys.exit(1)

    operation = sys.argv[1]

    # Initialize the transaction store
    print("Initializing transaction store...")
    txn_store = TxnStore('./transaction.db', './consolidated_transactions.csv')

    if operation == "process":
        if len(sys.argv) < 4:
            print("Usage: python main.py process <statement_type> <path_to_statement_file_or_folder>")
            sys.exit(1)

        statement_type = sys.argv[2]
        input_path = sys.argv[3]

        if statement_type == "folder":
            # Process all files in the folder
            if not os.path.isdir(input_path):
                print(f"Error: {input_path} is not a valid folder.")
                sys.exit(1)

            for file_name in os.listdir(input_path):
                file_path = os.path.join(input_path, file_name)
                if os.path.isfile(file_path):
                    process_file(file_path, txn_store)
        else:
            # Process a single file
            if statement_type == "auto":
                try:
                    file_name = os.path.basename(input_path)
                    statement_type = detect_statement_type(file_name)
                    print(f"Detected statement type: {statement_type}")
                except ValueError as e:
                    print(f"Error: {e}")
                    sys.exit(1)

            try:
                # Get the appropriate processor instance
                processor = StatementProcessorProvider.get_processor(statement_type, txn_store)
                processor.parse_statement(input_path)
                print(f"{statement_type} statement processed successfully.")
            except Exception as e:
                print(f"Error processing statement: {e}")

    elif operation == "classify":
        classify(txn_store)

    elif operation == "import":
        if len(sys.argv) < 2:
            print("Usage: python main.py import <path_to_csv_file>")
            sys.exit(1)

        input_path = sys.argv[2]
        import_classification(txn_store, input_path)
    
    elif operation == "auto-classify":
        print("Auto-classifying transactions...")
        auto_classify(txn_store)

    elif operation == "classify-csv-export":
        print("Exporting auto-classification transactions and in csv file...")
        auto_classify_csv_export(txn_store)

    elif operation == "classify-csv-import":
        print("Importing updated auto-classification transactions csv file...")
        auto_classify_csv_import(txn_store)

    else:
        print(f"Unknown operation: {operation}")
        print("Valid operations are 'process' and 'classify'.")
        sys.exit(1)

if __name__ == "__main__":
    main()