from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import Tk
import os
from pathlib import Path
import csv
# The code used to filter the SYNTECH dataset
def remove_all_suffixes(filename):
    """
    Removes all suffixes from the filename, even if the name contains periods.
    Returns the base name without any extensions.
    """
    p = Path(filename)
    while p.suffix:
        p = p.with_suffix('')
    return p.name

def validate_csv(csv_file):
    """
    Validates the CSV file for required columns and valid 'keep' values.
    Returns a dictionary mapping base filenames to 'keep' values, or None if validation fails.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            # Validate
            required_columns = {'Spec', 'keep'}

            # Check for required columns
            if not required_columns.issubset(fieldnames):
                missing = required_columns - set(fieldnames)
                print(f"Error: Missing required column(s) in '{csv_file}': {', '.join(missing)}")
                return None

            csv_files = {}
            invalid_keep_values = []
            for i, row in enumerate(reader, start=1):
                keep_value = row['keep']
                filename = row['Spec']
                base_filename = remove_all_suffixes(filename)

                # Check if 'keep' value is valid
                if keep_value not in ('0', '1'):
                    invalid_keep_values.append((i, keep_value, filename))
                    continue

                if base_filename in csv_files:
                    print(f"Warning: Duplicate filename '{filename}' in CSV at row {i}. Overwriting previous 'keep' value.")

                csv_files[base_filename] = keep_value

            if invalid_keep_values:
                print("Error: Invalid 'keep' values found in CSV:")
                for idx, keep_value, filename in invalid_keep_values:
                    print(f"  Row {idx}: 'keep'='{keep_value}' for file '{filename}' (expected '0' or '1')")
                return None

            return csv_files

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{csv_file}': {e}")
        return None

def get_files_to_remove(csv_files, directory):
    """
    Returns a list of file paths to remove based on the 'keep' column.
    Compares file base names without suffixes recursively.
    """
    files_in_directory = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            file_base_name = remove_all_suffixes(file)
            files_in_directory[file_base_name] = file_path

    files_to_remove = []
    missing_files = []
    for base_filename, keep_value in csv_files.items():
        if base_filename in files_in_directory:
            if keep_value == '0':
                files_to_remove.append(files_in_directory[base_filename])
        else:
            missing_files.append(base_filename)

    if missing_files:
        print(f"Warning: The following files from the CSV were not found in the directory:")
        for missing in missing_files:
            print(f"  - {missing}")

    # Optionally, list extra files in the directory not in CSV
    extra_files = set(files_in_directory.keys()) - set(csv_files.keys())
    if extra_files:
        print(f"Note: The following files are in the directory but not listed in the CSV:")
        for extra in extra_files:
            print(f"  - {extra}")

    return files_to_remove

def remove_files(files_to_remove):
    """
    Prompts the user to confirm and removes the files.
    """
    print(f"\nFound {len(files_to_remove)} file(s) to remove based on the CSV file.")
    if files_to_remove:
        print("Files to be removed:")
        for file_path in files_to_remove:
            print(f"  - {file_path}")
        confirm = input("\nDo you want to remove these files? (yes/no): ").strip().lower()
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

    # Select CSV file
    csv_file = askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if not csv_file:
        print("No CSV file selected. Exiting.")
        return

    # Validate CSV file
    csv_files = validate_csv(csv_file)
    if csv_files is None:
        print("CSV validation failed. Exiting.")
        return

    # Select directory
    directory = askdirectory(title="Select a folder")
    if directory:
        print(f"Selected folder: {directory}")
        files_to_remove = get_files_to_remove(csv_files, directory)
        remove_files(files_to_remove)
    else:
        print("No folder selected. Exiting.")

if __name__ == "__main__":
    main()
