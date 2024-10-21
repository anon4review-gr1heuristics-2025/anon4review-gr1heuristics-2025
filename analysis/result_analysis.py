from scipy.stats import gmean
from statistics import geometric_mean
import pandas as pd
import numpy as np


def pivot(df, columns):
    pivot_df = df.pivot_table(index='Spec', columns='RunConfig', values=columns)
    return pivot_df


def create_relative_df(pivot_df, column, baseline, drop_baseline):
    print(f"Creating relative dataframe for {column}")
    # Divide by the baseline
    relative_df = pivot_df[column].div(pivot_df[column][baseline], axis='rows')
    # Drop baseline
    if drop_baseline:
      relative_df = relative_df.drop(baseline, axis='columns')
    return relative_df

def has_duplicate_index(df):
    return df.index.duplicated().any()

def get_geometric_avg(pivot_df, runconfigs,baseline_config):
    # print(f"columns:{pivot_df.columns}")
    # print(f"configs:{runconfigs}")
    # Calculate geometric mean for each heuristic column
    pivot_df = pivot_df.copy()
    for col in pivot_df.columns.levels[0]:
        pivot_df[col] = pivot_df[col].div(pivot_df[col][baseline_config], axis=0)

    geometric_averages = {}
    for column in pivot_df.columns:
        print(f"is_any_null_or_nonpositive {(pivot_df[column].isna() | (pivot_df[column] <= 0)).any()}")

        geometric_averages[column] = gmean(pivot_df[column])

    # Create a DataFrame with the results
    result_df = pd.DataFrame.from_dict(geometric_averages, orient='index', columns=['Geometric Average'])
    result_df.index.name = 'Heuristic'

    # Display the results
    print(result_df)
    return geometric_averages

def print_headtohead_ratio(geometric_averages, columns, runconfigs, baseline='NOTHING'):
    def baseline_first(x):
        return (0 if x == 'NOTHING' else 1, x)

    # Sort runconfigs using Python's sorted() function
    runconfigs = sorted(runconfigs, key=baseline_first)

    # Rest of your function remains the same
    print("\nComparison:")
    # Extract unique metrics from heuristic_columns
    metrics = set(col[0] for col in columns)

    # Results for each metric
    for metric in metrics:
        print(f"\n{metric}")
        metric_data = {config: geometric_averages[column] for column in columns if column[0] == metric for
                       config in runconfigs if column[1] == config}
        if len(metric_data) > 1:
            base_config = runconfigs[0]  # Use the first config as the base for comparison
            base_value = metric_data[base_config]

            for config in runconfigs[1:]:  # Compare other configs to the base
                if config in metric_data:
                    ratio = metric_data[config] / base_value
                    print(f"  {config} vs {base_config}: {ratio:.4f}")
        else:
            print("  Not enough data for comparison")


def add_label_column(df):
    # Function to process each 'Spec' group
    def process_spec_group(group):
        # Get the baseline 'WORK_TIME' for 'NOTHING' RunConfig
        baseline_work_time = group[group['RunConfig'] == 'NOTHING']['WORK_TIME']
        if baseline_work_time.empty:
            # If 'NOTHING' RunConfig is not present, assign label 0 to all
            group['label'] = 0
        else:
            # Use the mean WORK_TIME if multiple entries exist
            baseline_work_time = baseline_work_time.mean()
            # Assign labels based on comparison
            group['label'] = group.apply(
                lambda row: int(row['WORK_TIME'] < baseline_work_time) if row['RunConfig'] != 'NOTHING' else 0,
                axis=1
            )
        return group

    # Apply the function to each 'Spec' group
    df = df.groupby('Spec', group_keys=False).apply(process_spec_group)

    return df
