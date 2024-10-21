# Keep only rows with Specs that no runconfig run for them has TIMEOUT
import pandas as pd
import numpy as np


def get_df_specs_no_timeout(df):
    spec_timeout_mask = df.groupby(['Spec'])['TIMEOUT'].transform('any')
    return df[~spec_timeout_mask]

def get_df_specs_timeout(df):
    spec_timeout_mask = df.groupby(['Spec'])['TIMEOUT'].transform('any')
    return df[spec_timeout_mask]


# Keep only rows that are \ are not timeout
def get_df_rows_no_timeout(df):
  return df[df['TIMEOUT']==0]

def get_df_rows_timeout(df):
  return df[df['TIMEOUT']==1]


def custom_cumcount(group):
    out = pd.Series(index=group.index, dtype=int)  # Initialize an empty Series with the same index
    count = 0

    for idx, row in group.iterrows():
        if row['TIMEOUT'] == 1:
            out.at[idx] = count
            count += 1
        else:
            out.at[idx] = -1

    return out


def retain_complete_runs(df):
    # Filter rows where TIMEOUT is 0
    df_filtered = df[df['TIMEOUT'] == 0]

    # Identify groups where all entries have 'TIMEOUT' (to be removed)
    mask = df_filtered.groupby(['Spec', 'RunConfig'])['TIMEOUT'].transform(lambda x: (x == 'TIMEOUT').all())

    # Filter out rows where its all TIMEOUT
    df_filtered = df_filtered[~mask]

    return df_filtered


def get_df_specs_same_column(df, column):
    # Check if the dataframe is empty
    if df.empty:
        return df

    # Check if 'Spec' and the given column exist in the dataframe
    if 'Spec' not in df.columns or column not in df.columns:
        raise ValueError(f"Columns 'Spec' or '{column}' not found in the dataframe")

    # Handle potential NaN values
    df_clean = df.dropna(subset=['Spec', column])

    def all_equal(s):
        return len(s.unique()) == 1

    # Group by 'Spec', check if all values in the given column are the same
    specs_with_same_value = df_clean.groupby('Spec')[column].agg(all_equal)

    # Filter the original dataframe to keep only the rows where 'Spec' has the same value for all entries
    df_filtered = df[df['Spec'].isin(specs_with_same_value[specs_with_same_value].index)]

    # If the result is empty, return an empty dataframe with the same columns as the input
    if df_filtered.empty:
        return pd.DataFrame(columns=df.columns)

    return df_filtered

def get_df_specs_value_in_column(df, column):
    # Check if the dataframe is empty
    if df.empty:
        return df

    # Check if 'Spec' and the given column exist in the dataframe
    if 'Spec' not in df.columns or column not in df.columns:
        raise ValueError(f"Columns 'Spec' or '{column}' not found in the dataframe")

    # Handle potential NaN values
    df_clean = df.dropna(subset=['Spec', column])

    def all_equal(s):
        return len(s.unique()) == 1

    # Group by 'Spec', check if all values in the given column are the same
    specs_with_same_value = df_clean.groupby('Spec')[column].agg(all_equal)

    # Filter the original dataframe to keep only the rows where 'Spec' has the same value for all entries
    df_filtered = df[df['Spec'].isin(specs_with_same_value[specs_with_same_value].index)]

    # If the result is empty, return an empty dataframe with the same columns as the input
    if df_filtered.empty:
        return pd.DataFrame(columns=df.columns)

    return df_filtered

def filter_groups_containing_value(df, group_column, value_column, target_value):
    return df[df.groupby(group_column)[value_column].transform(lambda x: target_value in x.values)]

def explore_amount_of_configs(df):
    # Count RunConfigs per Spec
    config_counts = df.groupby('Spec')['RunConfig'].count()
    print(f"\nUnique counts of RunConfigs per Spec: {config_counts.unique()}")


def text_boolean_to_boolean(df):
    cols = ['SWAPPED_TO_ORIGINAL']
    for col in cols:
        df[col] = df[col].fillna('FALSE')
        df[col] = df[col].replace({'TRUE': 1, 'FALSE': 0, 'True': 1, True: 1, False:0})
    return df