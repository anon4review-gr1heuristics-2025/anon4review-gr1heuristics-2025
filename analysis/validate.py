import pandas as pd
import numpy as np

def verify_columns_same_in_groups(df, columns, name):
    # Group by Spec and Action
    grouped = df.groupby(['Spec', 'ActionType'])

    def verify_single_column(column):
        def check_group(group):
            non_nan = group.dropna()
            if non_nan.empty:
                return 'all_nan'
            elif non_nan.nunique() == 1:
                return 'consistent'
            else:
                return 'inconsistent'

        # Apply the check to the specified column
        column_result = grouped[column].apply(check_group)

        inconsistencies = column_result[column_result == 'inconsistent']
        all_nan_groups = column_result[column_result == 'all_nan']

        if inconsistencies.empty:
            if all_nan_groups.empty:
                print(f"All values in {column} are the same for each Spec + Action combination.")
            else:
                print(f"All values in {column} are the same for each Spec + Action combination, with some all-NaN groups.")
            return True
        else:
            print(f"In {name}, inconsistencies found for {column} in the following Spec + Action combinations:")
            print(inconsistencies.index.tolist())
            return False

    # Verify each column and store results
    results = {column: verify_single_column(column) for column in columns}

    # Overall result
    if all(results.values()):
        print(f"All specified columns have consistent values within each Spec + Action combination.")
        return True
    else:
        print(f"Inconsistencies found in one or more columns.")
        return False


def verify_columns_permutations_in_groups(df, columns, name):
    # Group by Spec and ActionType
    grouped = df.groupby(['Spec', 'ActionType'])

    def verify_single_column(column):
        def check_group(group):
            non_nan = group.dropna()
            if non_nan.empty:
                return 'all_nan'
            else:
                try:
                    # Convert each list to a sorted tuple for comparison
                    non_nan_sorted = non_nan.apply(lambda x: tuple(sorted(x)) if isinstance(x, list) else x)
                except Exception as e:
                    print(f"Error processing group: {e}")
                    return 'error'

                if non_nan_sorted.nunique() == 1:
                    return 'consistent'
                else:
                    return 'inconsistent'

        # Apply the check to the specified column
        column_result = grouped[column].apply(check_group)

        inconsistencies = column_result[column_result == 'inconsistent']
        all_nan_groups = column_result[column_result == 'all_nan']
        errors = column_result[column_result == 'error']

        if inconsistencies.empty and errors.empty:
            if all_nan_groups.empty:
                print(f"All lists in {column} are permutations of each other for each Spec + ActionType combination.")
            else:
                print(f"All lists in {column} are permutations of each other for each Spec + ActionType combination, with some all-NaN groups.")
            return True
        else:
            print(f"In {name}, inconsistencies found for {column} in the following Spec + ActionType combinations:")
            if not inconsistencies.empty:
                print("Inconsistent groups:", inconsistencies.index.tolist())
            if not errors.empty:
                print("Error groups:", errors.index.tolist())
            return False

    # Verify each column and store results
    results = {column: verify_single_column(column) for column in columns}

    # Overall result
    if all(results.values()):
        print(f"All specified columns have consistent lists (up to permutation) within each Spec + ActionType combination.")
        return True
    else:
        print(f"Inconsistencies found in one or more columns.")
        return False
