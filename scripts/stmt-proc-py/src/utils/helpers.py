def read_xls_file(file_path):
    # Function to read an XLS file and return its contents
    import pandas as pd
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        print(f"Error reading XLS file: {e}")
        return None

def check_transaction_exists(transaction_id, csv_file):
    # Function to check if a transaction already exists in the CSV file
    import pandas as pd
    try:
        transactions = pd.read_csv(csv_file)
        return transaction_id in transactions['transaction_id'].values
    except FileNotFoundError:
        return False

def write_transaction_to_csv(transaction, csv_file):
    # Function to write a new transaction to the CSV file
    import pandas as pd
    try:
        transactions = pd.read_csv(csv_file)
        transactions = transactions.append(transaction, ignore_index=True)
        transactions.to_csv(csv_file, index=False)
    except FileNotFoundError:
        # If the file does not exist, create it and write the transaction
        pd.DataFrame([transaction]).to_csv(csv_file, index=False)

def parse_date_util(date_str):
    """
    Parse a date string in the format 'yyyy-mm-dd' into a standard date object.
    Args:
        date_str (str): The date string to parse.
    Returns:
        datetime.date: The parsed date object, or None if parsing fails.
    """
    # Function to parse a date string into a standard format
    from datetime import datetime
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return None
    
