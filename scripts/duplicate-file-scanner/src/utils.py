import hashlib
import os

debug_enabled = True

def set_debug_mode(enabled):
    """
    Sets the debug mode for the script.

    :param enabled: Boolean value to enable or disable debug mode.
    """
    global debug_enabled
    debug_enabled = enabled
    if debug_enabled:
        info("Debug mode enabled.")
    else:
        info("Debug mode disabled.")

def info(message):
    """
    Prints informational messages to the console.

    :param message: The message to print.
    """
    print(f"INFO: {message}")
def warning(message):
    """
    Prints warning messages to the console.
    :param message: The message to print.
    """
    print(f"WARNING: {message}")

def error(message):
    """
    Prints error messages to the console.
    :param message: The message to print.
    """
    print(f"ERROR: {message}")

def debug(message):
    """
    Prints debug messages to the console.

    :param message: The message to print.
    """
    if debug_enabled:
        print(f"DEBUG: {message}")

def calculate_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_file_metadata(file_path):
    return {
        "size": os.path.getsize(file_path),
        "modified_time": os.path.getmtime(file_path),
        "created_time": os.path.getctime(file_path),
        "filename": os.path.basename(file_path),
    }

def extract_first_n_bytes(file_path, n=10):
    if _is_valid_file(file_path):
        # Read the first n bytes of the file
        with open(file_path, "rb") as f:
            return f.read(n)
    else:
        filename = os.path.basename(file_path)
        return filename.encode('utf-8')
    
def _is_valid_file(file_path):
    """
    Checks if the file is valid for processing.

    :param file_path: The path to the file.
    :return: True if the file is valid, False otherwise.
    """
    # Ensure the file is a regular file and not a Google Drive placeholder
    if not os.path.isfile(file_path):
        return False
    # Skip Google Drive placeholders (e.g., .gdoc, .gsheet, etc.)
    invalid_extensions = ['.gdoc', '.gsheet', '.gslides', '.gform', '.gdraw', '.gscript', '.gmap']
    if any(file_path.endswith(ext) for ext in invalid_extensions):
        return False
    return True