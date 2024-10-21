from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import Tk
import os
from pathlib import Path
import csv
# Validation
def validate_csv(csv_file):
    """
    Validates the CSV file for required columns.
    Returns a list of dictionaries representing valid rows or None if validation fails.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            # Validate
            required_columns = {'Spec'}

            # Check for required columns
            if not required_columns.issubset(fieldnames):
                missing = required_columns - set(fieldnames)
                print(f"Error: Missing required column(s) in '{csv_file}': {', '.join(missing)}")
                return None

            return list(reader)

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{csv_file}': {e}")
        return None

def remove_all_suffixes(filename):
    """
    Removes all suffixes from the filename, even if the name contains periods.
    Returns the base name without any extensions.
    """
    p = Path(filename)
    while p.suffix:
        p = p.with_suffix('')
    return p.name

def get_all_files(directory):
    """
    Recursively get all files in the directory and its subdirectories.
    Returns a set of base names without suffixes.
    """
    all_files = set()
    for root, _, files in os.walk(directory):
        for file in files:
            base_name = remove_all_suffixes(file)
            all_files.add(base_name)
    return all_files

def count_file_differences(csv_rows, directory):
    """
    Counts the differences between files specified in CSV and files in the directory (recursively).
    Compares only the base names without suffixes.
    """
    csv_filenames = set(remove_all_suffixes(row['Spec']) for row in csv_rows)
    directory_files = get_all_files(directory)

    files_in_csv_not_in_dir = csv_filenames - directory_files
    files_in_dir_not_in_csv = directory_files - csv_filenames

    return files_in_csv_not_in_dir, files_in_dir_not_in_csv

def main():
    root = Tk()
    root.withdraw()

    # Select CSV file
    csv_file = askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        print("No CSV file selected. Exiting.")
        return

    # Validate CSV file
    csv_rows = validate_csv(csv_file)
    if csv_rows is None:
        print("CSV validation failed. Exiting.")
        return

    # Select directory
    directory = askdirectory(title="Select a folder")
    if not directory:
        print("No folder selected. Exiting.")
        return

    print(f"Selected CSV file: {csv_file}")
    print(f"Selected folder: {directory}")
    
    files_in_csv_not_in_dir, files_in_dir_not_in_csv = count_file_differences(csv_rows, directory)
    
    print(f"\nBase names in CSV but not in directory: {len(files_in_csv_not_in_dir)}")
    for file in sorted(files_in_csv_not_in_dir):
        print(f"  {file}")
    
    print(f"\nBase names in directory but not in CSV: {len(files_in_dir_not_in_csv)}")
    for file in sorted(files_in_dir_not_in_csv):
        print(f"  {file}")
    
    total_difference = len(files_in_csv_not_in_dir) + len(files_in_dir_not_in_csv)
    print(f"\nTotal difference: {total_difference}")

if __name__ == "__main__":
    main()
