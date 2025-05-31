import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.multioutput import MultiOutputClassifier
from store.txn_store import TxnStore
from prompt_toolkit import prompt
from classifier.classification_completer import CustomTransactionCompleter

class AutoClassifier:
    """
    A class to automatically classify transaction data into multiple categories.
    It uses a multi-output classifier to predict transaction type, category, and sub-category.
    """

    def __init__(self, txn_store: TxnStore = None):
        """
        Initialize the AutoClassifier.
        """
        self.classification_encoder = LabelEncoder()
        self.pipeline = None
        self.txn_store = txn_store    

    def train(self):
        """
        Train the classifier on the provided DataFrame.
        The DataFrame should contain labeled transaction data.
        """

        # Load transactions from the store
        df = self.txn_store.get_transactions()

        # Separate training data with labels
        train_df = df[df['txn_type'] != ''].copy()

        print(f"Number of training transactions: {len(train_df)}")

        # Prepare raw data
        print("Preparing raw data...")
        train_df = self._prepare_raw_data(train_df)

        # Encode classification labels
        train_df['classification'] = train_df['txn_type'] + '|' + train_df['category'] + '|' + train_df['sub_category']
        train_df['classification_enc'] = self.classification_encoder.fit_transform(train_df['classification'])

        # Define features and targets
        feature_names = ['raw_data']
        y = train_df[['classification_enc']].values

        # Build preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('text', TfidfVectorizer(), 'raw_data')
            ])

        # Create a pipeline with a multi-output classifier
        self.pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('clf', MultiOutputClassifier(RandomForestClassifier(n_estimators=500, random_state=42)))
        ])

        # Train-test split
        X_train, X_val, y_train, y_val = train_test_split(train_df[feature_names], y, test_size=0.2, random_state=42)

        # Train the model
        #self.pipeline.fit(X_train, y_train)
        self.pipeline.fit(train_df[feature_names], y)

        # Evaluate the model on validation set
        val_preds = self.pipeline.predict(X_val)
        val_preds = np.array(val_preds).reshape(-1, 1)  # Reshape to match the target shape

        val_accuracy = np.mean(np.all(val_preds == y_val, axis=1))
        print(f"Validation accuracy: {val_accuracy:.2f}")

    def classify(self):
        """
        Predict transaction classifications for transactions without labels.
        This method retrieves transactions from the store, prepares the data,
        and applies the trained model to predict missing classifications.

        It returns a DataFrame with the predicted classifications.
        Raises:
            ValueError: If the classifier has not been trained yet.
        """
        if self.pipeline is None:
            raise ValueError("The classifier has not been trained yet.")

        # Load transactions from the store
        df = self.txn_store.get_transactions()

        # Filter for transactions without classification
        classify_df = df[df['txn_type'] == ''].copy().head(100)  # Limit to 1000 transactions for classification

        print(f"Number of transactions to classify: {len(classify_df)}")

        # Prepare raw data
        print("Preparing raw data for prediction...")
        classify_df = self._prepare_raw_data(classify_df)

        # Prepare test features
        X_test = classify_df[['raw_data']]

        # Generate predictions
        preds = self.pipeline.predict(X_test)

        # Convert numeric predictions back to original labels
        classify_df['classification'] = self.classification_encoder.inverse_transform(preds[:, 0])

        # Save classified results back to the store
        #self.txn_store.store_transactions(test_df)
        # print first 20 rows of the classified DataFrame
        #print("Classified transactions:")
        #print(classify_df[['raw_data', 'txn_source', 'txn_date', 'narration', 'txn_amount', 'credit_indicator', 'classification']].head(20))
        return classify_df

    def apply_classification(self):
        """
        Apply the classification process interactively.
        This method will give control to user and allow repeatedly train the model, classify transactions.
        It will prompt the user to accept or reject classifications in batches of 10 transactions.

        """
        while True:
            # Perform ML model training
            print("Performing in-memory training...")

            # Train the model
            self.train()
            print("Training completed successfully. Classifying transactions...")

            # Classify transactions
            classify_df = self.classify()
            # If no transactions to classify, exit
            if classify_df.empty:
                print("No transactions to classify. Exiting.")
                break

            # sort classify_df by narration
            classify_df.sort_values(by='narration', inplace=True)
            i = 0
            batch_size = 20
            while i < len(classify_df):
                batch = classify_df.iloc[i:i+batch_size].copy()
                batch_indices = batch.index.tolist()
                # Print with sequence numbers starting from 1 in this batch
                print("\nBatch:")
                for seq, (idx, row) in enumerate(batch.iterrows(), start=1):
                    print(f"{seq}. {row['txn_source']} | {row['txn_date']} | {row['narration']} | {row['txn_amount']} | {row['credit_indicator']} |\n{row['classification']}")
                print("\nPress ENTER to accept all classifications in this batch,")
                print("or enter comma-separated sequence numbers (e.g. 2,4) for records NOT accepted,")
                print("or type 'exit' to stop:")
                user_input = input("Your choice: ").strip()
                if user_input.lower() == 'exit':
                    sys.exit(0)
                not_accepted_seqs = []
                if user_input == '':
                    # Accept all
                    accepted_seqs = list(range(1, len(batch)+1))
                else:
                    try:
                        not_accepted_seqs = [int(x.strip()) for x in user_input.split(',') if x.strip().isdigit()]
                    except Exception:
                        print("Invalid input. Continuing to next batch...")
                        i += batch_size
                        continue
                    accepted_seqs = [seq for seq in range(1, len(batch)+1) if seq not in not_accepted_seqs]
                # Update accepted transactions
                for seq in accepted_seqs:
                    idx = batch_indices[seq-1]
                    row = classify_df.loc[idx]
                    parts = row['classification'].split('|')
                    if len(parts) == 3:
                        txn_type, category, sub_category = parts
                        txn_date = row['txn_date']
                        narration = row['narration']
                        txn_amnt = row['txn_amount']
                        credit_indicator = row['credit_indicator']
                        self.txn_store.update_transaction(txn_date, narration, txn_amnt, credit_indicator, txn_type, category, sub_category)
                    else:
                        print(f"Invalid classification format for row {idx}: {row['classification']}")
                # For not accepted, prompt for manual classification or skip
                for seq in not_accepted_seqs:
                    idx = batch_indices[seq-1]
                    row = classify_df.loc[idx]
                    print(f"\nRecord {seq}:")
                    print(f"{row['raw_data']} | {row['txn_source']} | {row['txn_date']} | {row['narration']} | {row['txn_amount']} | {row['credit_indicator']} | {row['classification']}")
                    # manual_class = input("Enter manual classification as 'txn_type|category|sub_category', or press ENTER to skip: ").strip()
                    manual_class = prompt("Enter manual classification as 'txn_type|category|sub_category', or press ENTER to skip: ", completer=CustomTransactionCompleter()).strip()
                    if manual_class:
                        parts = manual_class.split('|')
                        if len(parts) == 3:
                            txn_type, category, sub_category = parts
                            txn_date = row['txn_date']
                            narration = row['narration']
                            txn_amnt = row['txn_amount']
                            credit_indicator = row['credit_indicator']
                            result = self.txn_store.update_transaction(txn_date, narration, txn_amnt, credit_indicator, txn_type, category, sub_category)
                            if result <= 0:
                                print(f"Failed to update transaction for {txn_date} | {narration} | {txn_amnt} | {credit_indicator}. It may not exist.")
                            # Optionally update classify_df for retraining
                            classify_df.at[idx, 'classification'] = manual_class
                            classify_df.at[idx, 'txn_type'] = txn_type
                            classify_df.at[idx, 'category'] = category
                            classify_df.at[idx, 'sub_category'] = sub_category
                        else:
                            print("Invalid format. Skipping.")
                retrain_input = input("Do you want to retrain and classify again? (y/n): ").strip().lower()
                if retrain_input == 'y':
                    print("Retraining and classifying again...")
                    break
                i += batch_size


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
                # if amount is a string, try to convert it to a float or int
                if isinstance(amount, str):
                    amount = amount.replace(',', '')  # Remove commas for conversion
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
        df['raw_data_orig'] = df['raw_data']

        df['credit_debit'] = df['credit_indicator'].apply(lambda x: 'Credit' if x == 'Yes' else 'Debit')

        # Replace '-' and '_' with space in narration before combining
        df['narration_clean'] = df['narration'].astype(str).str.replace(r'[-_]', ' ', regex=True)
        df['raw_data'] = (
            df['narration_clean'] + " " +
            df['credit_debit'] + " " +
            df['amount_range'] + " " +
            df['date_range']
        ).str.lower()
        return df
