import os
from typing import IO


def open_fat32_file(filename: str) -> IO:
    file_path = str(filename)
    current_path = os.getcwd()
    full_file_path = os.path.join(current_path, file_path)
    try:
        file = open(full_file_path, 'r+b')
        print(f"File '{full_file_path}' opened successfully.")
        return file
    except Exception as e:
        print(f"Error: {e}")


def close_fat32_file(file: IO):
    print(f"File closed successfully.")
    file.close()
