import os
import pandas as pd
import numpy as np

def load_data_mult(csv_dir = './analysis_csv/'):
    dataframes = []
    all_specs = set()

    # Get a list of all CSV files in the 'analysis_csv' directory
    csv_files = [file for file in os.listdir(csv_dir) if file.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the 'analysis_csv' directory.")
        return None

    print(f"Found {len(csv_files)} CSV file(s) in the 'analysis_csv' directory.")

    for filename in csv_files:
        file_path = os.path.join(csv_dir, filename)
        df = pd.read_csv(file_path)

        if 'Spec' not in df.columns:
            raise ValueError(f"Error: {filename} does not contain a 'Spec' column. All files must have a 'Spec' column.")

        current_specs = set(df['Spec'])
        if all_specs.intersection(current_specs):
            raise ValueError(f"{filename} contains 'Spec' values that are already present in other files. {all_specs.intersection(current_specs)}")

        all_specs.update(current_specs)
        dataframes.append(df)
        print(f"Loaded: {filename}")
        print(f"Number of specs in this file: {len(current_specs)}")

    if not dataframes:
        print("No valid files were loaded.")
        return None

    final_df = pd.concat(dataframes, ignore_index=True)
    print(f"Total number of files loaded: {len(dataframes)}")
    print(f"Total Specs: {len(set(final_df['Spec']))}")
    print(f"Final DataFrame shape: {final_df.shape}")

    return final_df

def load_data(name):
    file_path = os.path.join('.', name)

    if not os.path.exists(file_path):
        print(f"Error: {name} does not exist in the validation_csv folder.")
        return None

    try:
        df = pd.read_csv(file_path)
        print(f"Loaded: {name}")
        print(f"DataFrame shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading {name}: {str(e)}")
        return None