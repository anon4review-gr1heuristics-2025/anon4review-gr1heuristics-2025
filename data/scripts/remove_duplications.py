from tkinter.filedialog import askdirectory
from tkinter import Tk
import os
import hashlib
from pathlib import Path

def remove_duplications(file_path):
    list_of_files = os.walk(file_path)
    unique_files = dict()
    for root, folders, files in list_of_files:
        # Running a for loop on all the files
        for file in files:
            # Finding complete file path
            file_path = Path(os.path.join(root, file))

            # Converting all the content of
            # our file into md5 hash.
            Hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

            # If file hash has already
            # been added we'll simply delete that file
            if Hash_file not in unique_files:
                unique_files[Hash_file] = file_path
            else:
                os.remove(file_path)
                print(f"{file_path} has been deleted")

    print(f"Removed {len(files) - len(unique_files)} duplicate files.")
    print(f"{len(unique_files)} unique files remain.")

def main():
    root = Tk()
    root.withdraw()

    # Dialog box for selecting a folder.
    file_path = askdirectory(title="Select a folder")

    if file_path:
        print(f"Selected folder: {file_path}")
        remove_duplications(file_path)
    else:
        print("No folder selected. Exiting.")

if __name__ == "__main__":
    main()