import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

def count_files(directory):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        # Only count the files, not the directories
        file_count += len(files)
    return file_count

# Hide the main tkinter window
Tk().withdraw()

# Open dialog to select directory
selected_directory = askdirectory(title="Select a folder")

if selected_directory:
    total_files = count_files(selected_directory)
    print(f"Total number of files in the selected directory and its subfolders: {total_files}")
else:
    print("No directory selected.")
