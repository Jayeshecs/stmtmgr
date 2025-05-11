# Duplicate File Scanner

This project is designed to scan a specified folder recursively to identify exact and potential duplicate files based on defined criteria. It generates an index database and produces a CSV report of the findings.

## Features

- Recursively scans directories for files.
- Identifies exact duplicates using file hashes.
- Identifies potential duplicates based on file size and metadata.
- Generates an index database for efficient duplicate tracking.
- Produces a CSV report detailing the findings.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd duplicate-file-scanner
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Configure the target folder to scan in `config.yaml`.
2. Run the scanner:
   ```
   python -m src.scanner
   ```
3. After the scan is complete, generate the report:
   ```
   python -m src.report_generator
   ```

## Configuration

The `config.yaml` file contains settings for the project, including the target folder to scan. Modify this file to set your desired parameters.

## Example

To scan a folder located at `/path/to/your/folder`, update the `config.yaml` as follows:

```yaml
target_folder: /path/to/your/folder
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.