import csv
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import json
from utils.helpers import parse_date_util

class Classifier:
    """Class to classify transactions based on similarity and user input."""

    def __init__(self, txn_store, config_file='./config.json'):
        self.txn_store = txn_store
        print("Loading configuration...")
        self.config = self._load_config(config_file)
        print("Loading classifier metadata...")
        self.classifier_metadata = self._load_classifier_metadata()
        print(f"Classifier metadata loaded with {len(self.classifier_metadata)} entries.")
        print(f"Loaded distinct categories: {len(self._get_distinct_categories())} and distinct sub-categories: {len(self._get_distinct_sub_categories())}")
        self.vectorizer = TfidfVectorizer()

    def _load_config(self, config_file):
        """Load configuration from a JSON file."""
        with open(config_file, 'r') as file:
            return json.load(file)

    def _load_classifier_metadata(self):
        """
        Load classifier metadata from a CSV file.

        The method attempts to load a CSV file specified by the configuration key
        'classifier_metadata_file' (default: './classifier_metadata.csv'). The file must contain
        three columns: 'txn_type', 'category', and 'sub_category'. If the file is missing or does not
        contain the required columns, an empty DataFrame with these columns is returned.

        Returns:
            pd.DataFrame: DataFrame containing classifier metadata with columns
                  ['txn_type', 'category', 'sub_category'].
        """
        metadata_file = self.config.get('classifier_metadata_file', './classifier_metadata.csv')
        try:
            df = pd.read_csv(metadata_file)
            print(f"Columns in metadata file: {df.columns.tolist()}")
            if not all(col in df.columns for col in ['txn_type', 'category', 'sub_category']):
                raise ValueError("Metadata file must contain txn_type, category, and sub_category columns.")
            return df
        except FileNotFoundError:
            print(f"Metadata file {metadata_file} not found. Please check the path.")
            return pd.DataFrame(columns=['txn_type', 'category', 'sub_category'])
        except Exception as e:
            print(f"Error loading metadata file: {e}")
            return pd.DataFrame(columns=['txn_type', 'category', 'sub_category'])
        
    def _save_classifier_metadata(self):
        """
        Saves the classifier metadata to a CSV file specified in the configuration.

        The method retrieves the file path from the configuration using the key
        'classifier_metadata_file'. If the key is not present, it defaults to
        './classifier_metadata.csv'. The classifier metadata is then written to this
        CSV file without including the DataFrame index. If an error occurs during
        the save operation, an error message is printed.

        Raises:
            Prints an error message if saving the metadata file fails.
        """
        metadata_file = self.config.get('classifier_metadata_file', './classifier_metadata.csv')
        try:
            self.classifier_metadata.to_csv(metadata_file, index=False)
            print(f"Classifier metadata saved to {metadata_file}.")
        except Exception as e:
            print(f"Error saving metadata file: {e}")

    def _add_classifier_metadata(self, txn_type, category, sub_category):
        """
        Adds a new classifier metadata entry if it does not already exist.

        Checks if a combination of txn_type, category, and sub_category is already present
        in the classifier_metadata DataFrame. If not, appends the new entry and saves the updated metadata.

        Args:
            txn_type (str): The transaction type to add.
            category (str): The category associated with the transaction type.
            sub_category (str): The sub-category associated with the transaction type.

        Returns:
            None
        """
        new_entry = pd.DataFrame({
            'txn_type': [txn_type],
            'category': [category],
            'sub_category': [sub_category]
        })
        # Check if the entry already exists
        if not self.classifier_metadata[(self.classifier_metadata['txn_type'] == txn_type) &
                                        (self.classifier_metadata['category'] == category) &
                                        (self.classifier_metadata['sub_category'] == sub_category)].empty:
            #print("Entry already exists in classifier metadata.")
            return
        self.classifier_metadata = pd.concat([self.classifier_metadata, new_entry], ignore_index=True)
        self._save_classifier_metadata()
    
    def _get_distinct_sub_categories(self):
        """
        Returns a list of unique sub-categories from the 'sub_category' column in the classifier metadata, excluding any missing values.

        Returns:
            list: A list of unique sub-category values.
        """
        return sorted(self.classifier_metadata['sub_category'].dropna().unique().tolist())
    
    def _get_distinct_categories_for_sub_category(self, sub_category):
        """
        Retrieve a list of distinct categories associated with a given sub-category from the classifier metadata.
        If no sub-category is provided or if the specified sub-category is not found in the metadata,
        returns the list of all distinct categories.
        Args:
            sub_category (str or None): The sub-category for which to retrieve associated categories.
                If None or not found, returns all distinct categories.
        Returns:
            list: A list of distinct category names associated with the given sub-category,
                or all categories if sub-category is None or not found.
        """
        if sub_category is None:
            return self._get_distinct_categories()
        
        if sub_category not in self.classifier_metadata['sub_category'].dropna().unique():
            print(f"Sub-category '{sub_category}' not found in metadata.")
            return self._get_distinct_categories()
        
        return self.classifier_metadata[self.classifier_metadata['sub_category'] == sub_category]['category'].dropna().unique().tolist()
    
    def _get_distinct_categories(self):
        """
        Returns a list of unique, non-null category values from the classifier metadata.

        Returns:
            list: A list containing the distinct category values present in the 'category' column of the classifier metadata.
        """
        return sorted(self.classifier_metadata['category'].dropna().unique().tolist())
    
    def _get_txn_type(self, category):
        """
        Get transaction type for a given category from the classifier metadata.

        Args:
            category (str): The category for which to retrieve the transaction type.

        Returns:
            str or None: The first transaction type associated with the given category,
                 or None if no match is found.
        """
        txn_types = self.classifier_metadata[self.classifier_metadata['category'] == category]['txn_type'].dropna().unique().tolist()
        return txn_types[0] if txn_types else None
    
    def _get_distinct_txn_types(self):
        """
        Returns a list of unique, non-null transaction types from the classifier metadata.

        Returns:
            list: A list containing the distinct transaction types present in the 'txn_type' column
                  of the classifier metadata, with any missing values excluded.
        """
        return self.classifier_metadata['txn_type'].dropna().unique().tolist()

    def _vectorize_transactions(self, raw_data_list):
        """
        Transforms a list of raw transaction data into TF-IDF feature vectors.

        Args:
            raw_data_list (list of str): List containing raw transaction data as strings.

        Returns:
            scipy.sparse.csr_matrix: TF-IDF feature matrix representing the input transactions.
        """
        return self.vectorizer.fit_transform(raw_data_list)

    def _cluster_transactions(self, tfidf_matrix):
        """
        Clusters transactions based on their TF-IDF representations using the DBSCAN algorithm.

        This method computes a pairwise cosine similarity matrix from the input TF-IDF matrix,
        converts it to a distance matrix, and applies DBSCAN clustering with a configurable
        similarity threshold. Transactions with a cosine similarity above the threshold are
        grouped together.

        Args:
            tfidf_matrix (numpy.ndarray): A 2D array representing the TF-IDF features of transactions.

        Returns:
            numpy.ndarray: An array of cluster labels assigned to each transaction. Transactions
            labeled as -1 are considered noise (not assigned to any cluster).
        """
        threshold = self.config.get('similarity_threshold', 0.7)
        distance_matrix = 1 - cosine_similarity(tfidf_matrix)
        # Ensure no negative values in the distance matrix
        distance_matrix = np.clip(distance_matrix, 0, None)
        clustering = DBSCAN(eps=1 - threshold, min_samples=2, metric='precomputed')
        return clustering.fit_predict(distance_matrix)

    def _prepare_raw_data(self, df):
        """
        Prepare and enrich the input DataFrame by generating new features for transaction classification.
        This method performs the following steps:
        1. Categorizes the 'txn_amount' column into predefined amount ranges and stores the result in a new 'amount_range' column.
        2. Converts the 'txn_date' column to datetime format (YYYY-MM-DD), coercing errors to NaT.
        3. Extracts the day from 'txn_date' and categorizes it into predefined date ranges, storing the result in a new 'date_range' column.
        4. Combines the 'txn_source', 'credit_indicator', 'narration', 'amount_range', and 'date_range' columns into a single 'raw_data' string for each row.
        Args:
            df (pandas.DataFrame): Input DataFrame containing at least the following columns:
                - 'txn_source'
                - 'credit_indicator'
                - 'narration'
                - 'txn_amount'
                - 'txn_date'
        Returns:
            pandas.DataFrame: The input DataFrame with additional 'amount_range', 'date_range', 'raw_data' and 'raw_data_orig' columns.
        """
        def get_amount_range(amount):
            try:
                amount = float(amount)  # Attempt to convert to float
            except (ValueError, TypeError):
                try:
                    amount = int(amount)  # Attempt to convert to integer
                except (ValueError, TypeError):
                    return "unknown"  # Handle invalid or missing amounts
            ranges = [
                (1, 100), (101, 500), (501, 1000), (1001, 5000), (5001, 10000),
                (10001, 25000), (25001, 50000), (50001, 100000), (100001, 500000),
                (500001, 1000000)
            ]
            for lower, upper in ranges:
                if lower <= amount <= upper:
                    return f"{lower}-{upper}"
            return "1000001+"

        def get_date_range(day):
            ranges = [(1, 7), (8, 14), (15, 21), (22, 31)]
            for lower, upper in ranges:
                if lower <= day <= upper:
                    return f"{lower}-{upper}"
            return "unknown"

        df['amount_range'] = df['txn_amount'].apply(get_amount_range)

        # Ensure txn_date is in datetime format
        df['txn_date'] = pd.to_datetime(df['txn_date'], format='%Y-%m-%d', errors='coerce')
        df['date_range'] = df['txn_date'].dt.day.apply(get_date_range)

        # Backup original raw_data
        df['raw_data_orig'] = df['raw_data'];

        df['raw_data'] = df['txn_source'] + " " + df['credit_indicator'] + " " + \
                         df['narration'] + " " + df['amount_range'] + " " + df['date_range']
        return df

    def classify_transactions(self):
        """
        Interactively classify transactions by clustering similar transactions and assigning user-defined categories.
        Workflow:
        1. Loads transactions from the transaction store.
        2. Prepares and vectorizes transaction data for clustering.
        3. Clusters transactions based on similarity.
        4. For each cluster (excluding noise):
            - Displays sample transactions.
            - Prompts the user to select or enter a sub-category, category, and transaction type.
            - Fetches existing classifications to assist user selection.
            - Updates the classification metadata for the cluster.
            - Applies the selected classification to all transactions in the cluster.
        5. Updates the transaction store with the new classifications.
        User input is required to assign or create sub-categories, categories, and transaction types for each cluster.
        """
        # Load transactions from the store
        df = self.txn_store.get_transactions()

        # Prepare raw data
        print("Preparing raw data...")
        df = self._prepare_raw_data(df)

        # Split into credit and debit transactions
        credit_mask = df['credit_indicator'].fillna('').str.strip().str.lower() == 'yes'
        df_credit = df[credit_mask].copy()
        df_debit = df[~credit_mask].copy()

        # Vectorize and cluster credit transactions
        print("Vectorizing credit transactions...")
        if not df_credit.empty:
            tfidf_matrix_credit = self._vectorize_transactions(df_credit['raw_data'].tolist())
            print("Clustering credit transactions...")
            clusters_credit = self._cluster_transactions(tfidf_matrix_credit)
            df_credit['cluster'] = clusters_credit
            # Offset cluster ids to avoid overlap with debit clusters
            max_credit_cluster = clusters_credit.max() if len(clusters_credit) > 0 else -1
        else:
            df_credit['cluster'] = []

        # Vectorize and cluster debit transactions
        print("Vectorizing debit transactions...")
        if not df_debit.empty:
            tfidf_matrix_debit = self._vectorize_transactions(df_debit['raw_data'].tolist())
            print("Clustering debit transactions...")
            clusters_debit = self._cluster_transactions(tfidf_matrix_debit)
            # Offset debit cluster ids by max_credit_cluster + 1 (except for noise -1)
            offset = (max_credit_cluster + 1) if df_credit.shape[0] > 0 else 0
            clusters_debit_offset = [
                (c if c == -1 else c + offset) for c in clusters_debit
            ]
            df_debit['cluster'] = clusters_debit_offset
        else:
            df_debit['cluster'] = []

        # Merge credit and debit DataFrames
        df = pd.concat([df_credit, df_debit], ignore_index=True)

        # Process each cluster
        for cluster_id in set(df['cluster']):
            if cluster_id == -1:
                continue  # Skip noise points

            cluster_df = df[df['cluster'] == cluster_id]
            
            # check if the cluster has at least 1 transaction with no associated txn_type or category or sub_category
            if cluster_df.empty:
                print(f"Cluster {cluster_id} is empty. Skipping...")
                continue

            print(f"\nCluster {cluster_id}: {len(cluster_df)} transactions")

            # Display sample transactions
            print("\nFirst 10 transactions in this cluster:")
            print(cluster_df[['txn_source', 'credit_indicator', 'txn_date', 'txn_amount', 'narration', 'txn_type', 'category', 'sub_category']].head(10).to_string(index=False))  # Show 10 samples

            # Only proceed if at least one record is missing a classification (null or empty string)
            if not (
                cluster_df['txn_type'].isna().any() or (cluster_df['txn_type'] == '').any() or
                cluster_df['category'].isna().any() or (cluster_df['category'] == '').any() or
                cluster_df['sub_category'].isna().any() or (cluster_df['sub_category'] == '').any()
            ):
                print(f"Cluster {cluster_id} already has classifications. Skipping...")
                continue

            # Fetch unique existing classifications from the current cluster
            existing_types = self._get_distinct_txn_types()
            existing_categories = self._get_distinct_categories()
            existing_sub_categories = self._get_distinct_sub_categories()

            category = None
            sub_category = None
            txn_type = None

            # Display list of sub-categories
            while True:
                if existing_sub_categories:
                    print("\nExisting sub-categories:")
                    # Print 10 sub-categories per row, separated by tabs
                    for i in range(0, len(existing_sub_categories), 10):
                        row = existing_sub_categories[i:i+10]
                        print("\t".join([f"{i+j+1}. {sub_category}" for j, sub_category in enumerate(row)]))
                    sub_category_input = input("Select a sub-category (or enter a new one): ")

                    # Remove leading and trailing whitespace
                    sub_category_input = sub_category_input.strip()

                    if sub_category_input.isdigit():
                        index = int(sub_category_input) - 1
                        if 0 <= index < len(existing_sub_categories):
                            sub_category = existing_sub_categories[index]
                            break
                        else:
                            print("Invalid sub-category selection. Please enter a valid index or a new sub-category name.")
                            continue
                    elif sub_category_input:
                        sub_category = sub_category_input
                        break
                    else:
                        print("Please enter a sub-category.")
                        continue
                else:
                    sub_category_input = input("Enter a new sub-category: ").strip()
                    if sub_category_input:
                        sub_category = sub_category_input
                        break
                    else:
                        print("Please enter a sub-category.")
                        continue
            
            # Fetch existing classifications based on the selected sub-category
            available_categories = self._get_distinct_categories_for_sub_category(sub_category)
            
            # Display list of categories
            while True:
                if available_categories:
                    # Append all existing categories to available_categories if not already present
                    for cat in existing_categories:
                        if cat not in available_categories:
                            available_categories.append(cat)
                    print("\nExisting categories:")
                    # Print 10 categories per row, separated by tabs
                    for i in range(0, len(available_categories), 10):
                        row = available_categories[i:i+10]
                        print("\t".join([f"{i+j+1}. {category}" for j, category in enumerate(row)]))
                    category_input = input("Select a category (or enter a new one): ").strip()
                    if category_input.isdigit():
                        index = int(category_input) - 1
                        if 0 <= index < len(available_categories):
                            category = available_categories[index]
                            break
                        else:
                            print("Invalid category selection. Please enter a valid index or a new category name.")
                            continue
                    elif category_input:
                        category = category_input
                        break
                    else:
                        print("Please enter a category.")
                        continue
                else:
                    print("\nExisting categories:")
                    # Print 10 categories per row, separated by tabs
                    for i in range(0, len(existing_categories), 10):
                        row = existing_categories[i:i+10]
                        print("\t".join([f"{i+j+1}. {category}" for j, category in enumerate(row)]))
                    category_input = input("Select a category (or enter a new one): ").strip()
                    if category_input.isdigit():
                        index = int(category_input) - 1
                        if 0 <= index < len(existing_categories):
                            category = existing_categories[index]
                            break
                        else:
                            print("Invalid category selection. Please enter a valid index or a new category name.")
                            continue
                    elif category_input:
                        category = category_input
                        break
                    else:
                        print("Please enter a category.")
                        continue
            
            # Display list of transaction types
            while True:
                if category:
                    txn_type_default = self._get_txn_type(category)
                    if txn_type_default:
                        print(f"\nExisting transaction type: {txn_type_default}")
                    print(", ".join([f"{i}. {t}" for i, t in enumerate(existing_types, 1)]))
                    txn_type_input = input(f"Press enter for {txn_type_default} (or select a transaction type): ").strip()
                    if txn_type_input == '':
                        txn_type = txn_type_default
                        break
                    elif txn_type_input.isdigit():
                        index = int(txn_type_input) - 1
                        if 0 <= index < len(existing_types):
                            txn_type = existing_types[index]
                            break
                        else:
                            print("Invalid transaction type selection. Please enter a valid index or a new transaction type.")
                            continue
                    else:
                        print("New transaction type cannot be entered. Please select a valid transaction type.")
                        continue
                else:
                    print("No category selected. Please select a category first.")
                    break

            self._add_classifier_metadata(txn_type, category, sub_category)

            # Update classifications
            if txn_type and category and sub_category:
                print(f"Updating classifications with type: {txn_type}, category: {category}, sub-category: {sub_category}...")
                self.txn_store.update_transactions(cluster_df['raw_data_orig'].tolist(), txn_type, category, sub_category)
                print("Classifications updated successfully.")

    def import_classification(self, csv_file):
        """
        Import classifications from a CSV file and apply them to transactions.
        The CSV file should contain columns for date, narration, debit amount, and credit amount.
        The user will be prompted to provide the column indices for these fields.
        Args:
            csv_file (str): Path to the CSV file containing transaction data.
        Returns:
            None
        """

        print("Please provide the column index (starting from 0) for the following fields:")
        date_idx = int(input("Date column index: "))
        narration_idx = int(input("Narration column index: "))
        amnt_idx = int(input("Amount column index: "))
        credit_ind_idx = int(input("Credit indicator column index: "))
        type_idx = int(input("Type column index: "))
        category_idx = int(input("Category column index: "))
        sub_category_idx = int(input("Sub-category column index: "))

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            total_counter = 0
            total_errors = 0
            
            for row in reader:
                total_counter += 1
                date_str = row[date_idx]
                txn_date = parse_date_util(date_str)
                if txn_date is None:
                    print(f"Invalid date format in row: {row}. Skipping this transaction.")
                    continue
                narration = row[narration_idx]
                amnt = float(row[amnt_idx])
                credit_indicator = 'Yes' if row[credit_ind_idx].strip().lower() == 'cr' else ''
                txn_type = row[type_idx]
                category = row[category_idx]
                sub_category = row[sub_category_idx]
                result = self.apply_classification(txn_date, narration, amnt, credit_indicator, txn_type, category, sub_category)
                if result <= 0:
                    total_errors += 1
            
            print(f"Processed {total_counter} transactions with {total_errors} errors.")

    def apply_classification(self, txn_date, narration, amnt, credit_indicator, txn_type, category, sub_category):
        """
        Apply classification to a single transaction based on user input.

        Args:
            txn_date (Date): Transaction date in YYYY-MM-DD format.
            narration (str): Transaction narration or description.
            amnt (float): Transaction amount as a string.
            credit_indicator (str): Credit indicator as a string.
            type (str): Transaction type.
            category (str): Transaction category.
            sub_category (str): Transaction sub-category.

        Returns:
            int: The number of transactions updated in the store, or None if no transaction was updated.
        """

        narration = narration.strip()  # Remove leading and trailing whitespace

        # Display the transaction details
        #print(f"Transaction Details: Date: {txn_date}, Narration: {narration}, Amount: {amnt}, Credit Indicator: {credit_indicator}\n")

        self._add_classifier_metadata(txn_type, category, sub_category)

        # Update the transaction store with the new classification
        result = self.txn_store.update_transaction(txn_date, narration, amnt, credit_indicator, txn_type, category, sub_category)
        return result
