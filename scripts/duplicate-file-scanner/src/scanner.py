import os
from utils import read_file_metadata, debug

class FileScanner:
    def __init__(self, target_folder, include_subdirectories=True, exclude_files: []=None):
        self.target_folder = target_folder
        self.include_subdirectories = include_subdirectories
        self.exclude_files = exclude_files if exclude_files is not None else []

    def process_file(self, file_path, callback):
        """
        Processes a file and invokes the callback with the file path and metadata.

        :param file_path: The path to the file.
        :param callback: A function that takes a file path and metadata as arguments.
        """
        # Read the file metadata
        if os.path.basename(file_path) in self.exclude_files:
            debug(f"Skipping excluded file '{file_path}'")
            return
        
        # Read the file metadata
        metadata = read_file_metadata(file_path)

        # check if file_path is a file
        if os.path.isfile(file_path):
            # Invoke the callback with the file path and metadata
            callback(file_path, metadata)
        else:
            debug(f"Skipping non-file '{file_path}'")

    def scan(self, callback):
        """
        Scans the target folder and invokes the callback for each file.

        :param callback: A function that takes a file path and metadata as arguments.
        """
        if self.include_subdirectories:
            # If including subdirectories, walk through the directory tree
            for root, _, files in os.walk(self.target_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.process_file(file_path, callback)
        else:
            # If not including subdirectories, list only the files in the target folder
            for file in os.listdir(self.target_folder):
                file_path = os.path.join(self.target_folder, file)
                self.process_file(file_path, callback)
