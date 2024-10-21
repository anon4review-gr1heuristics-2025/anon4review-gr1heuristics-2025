import os
import shutil
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo, showerror

def copy_files_to_new_folder(source_dir, dest_dir):
    file_count = 0
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            dest_path = os.path.join(dest_dir, file)            
            shutil.copy2(source_path, dest_path)
            file_count += 1
    return file_count

# Hide the main tkinter window
Tk().withdraw()

# Open dialog to select source directory
source_directory = askdirectory(title="Select source folder")

if source_directory:
    # Open dialog to select destination directory
    dest_directory = askdirectory(title="Select destination folder")
    
    if dest_directory:
        try:
            # Create the destination directory if it doesn't exist
            os.makedirs(dest_directory, exist_ok=True)
            
            # Copy files
            total_files = copy_files_to_new_folder(source_directory, dest_directory)
            
            showinfo("Copy Complete", f"Successfully copied {total_files} files to {dest_directory}")
        except Exception as e:
            showerror("Error", f"An error occurred: {str(e)}")
    else:
        print("No destination directory selected. Exiting.")
else:
    print("No source directory selected. Exiting.")