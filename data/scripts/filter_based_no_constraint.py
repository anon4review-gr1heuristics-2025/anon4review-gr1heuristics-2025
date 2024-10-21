from tkinter.filedialog import askdirectory
from tkinter import Tk
import os
from pathlib import Path
# Used for filtering SYNTECH23 specs

def find_and_remove_files_without_keywords(directory):
    keywords = ["asm", "assumption"]
    files_to_remove = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not any(keyword in content for keyword in keywords):
                    print(f"{file_path} doesn't have any of the keywords.")
                    files_to_remove.append(file_path)
            except UnicodeDecodeError:
                print(f"Skipping file {file_path} due to encoding error.")
            except Exception as e:
                print(f"An error occurred with file {file_path}: {e}")
    print(f"Found {len(files_to_remove)} files without the specified keywords.")

    if files_to_remove:
        confirm = input("Do you want to remove these files? (yes/no): ").strip().lower()
        if confirm == 'yes':
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    print(f"Removed {file_path}")
                except Exception as e:
                    print(f"Failed to remove {file_path}: {e}")
            print("All specified files have been removed.")
        else:
            print("No files were removed.")
    else:
        print("No files to remove.")

def main():
    root = Tk()
    root.withdraw()
    directory = askdirectory(title="Select a folder")
    if directory:
        print(f"Selected folder: {directory}")
        find_and_remove_files_without_keywords(directory)
    else:
        print("No folder selected. Exiting.")

if __name__ == "__main__":
    main()
