import sys
import os
from database import DatabaseManager
from scanner import FileScanner
from report_generator import ReportGenerator
from utils import info, debug, error, set_debug_mode

def main():
    # Load configuration
    import yaml
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    target_folder = config.get("target_folder")
    include_subdirectories = config.get("include_subdirectories", True)
    report_format = config.get("report_format", "csv")
    set_debug_mode(config.get("debug", True))
    exclude_files = config.get("exclude_files", [])

    if not target_folder:
        print("Error: Target folder is not specified in config.yaml.")
        sys.exit(1)

    # Normalize and check the path
    target_folder = os.path.abspath(target_folder.strip())
    debug(f"Target folder is '{target_folder}'")  # Debugging line
    if not os.path.exists(target_folder):
        error(f"Target folder {target_folder} does not exist.")
        sys.exit(1)

    db_manager: DatabaseManager = None  # Initialize db_manager to None

    try:
        
        # Step 1: Initialize the database
        info("Initializing database...")
        db_manager = DatabaseManager()
        db_manager.create_table()  # Ensure the database table is created
        info("Initializing database...done.")

        # Step 2: Initialize the report generator
        info("Initializing report generator...")
        report_generator = ReportGenerator(db_manager)
        info("Initializing report generator...done.")

        # Step 3: Initialize the file scanner
        info("Initializing file scanner...")
        scanner = FileScanner(target_folder, include_subdirectories, exclude_files)
        info("Initializing file scanner...done.")
        info(f"Target folder: {target_folder}")
        info(f"Include subdirectories: {include_subdirectories}")

        # Step 4: Scan the target folder and update database with individual entries along with exact match and potential match hashes
        scanner.scan(lambda file_path, metadata: db_manager.insert_file(file_path, metadata))

        # Step 5: Generate the report
        info("Generating report...")
        if report_format == "csv":
            report_generator.generate_csv_report("report.csv")
            info("CSV report generated: report.csv")
        else:
            error(f"Unsupported report format: {report_format}. Supported formats are: csv.")

        info("Process completed successfully.")

    except Exception as e:
        error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        if db_manager != None:
            db_manager.close()

if __name__ == "__main__":
    main()