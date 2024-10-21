import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

def print_file_names(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_name_without_extension = os.path.splitext(file)[0]
            print(file_name_without_extension)

# Hide the main tkinter window
Tk().withdraw()

# Open dialog to select the directory
selected_directory = askdirectory(title="Select folder to list file names")

if selected_directory:
    print_file_names(selected_directory)
else:
    print("No directory selected. Exiting.")
