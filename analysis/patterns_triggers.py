import pandas as pd
import numpy as np

def string_to_set(s):
    try:
        if isinstance(s, str):
            s_clean = s.strip('{}').replace("'", "").replace('[','').replace(']','').split(',')
            return set(item.strip() for item in s_clean)
        elif isinstance(s, set):
            return s
        else:
            raise ValueError("Input must be a string or a set")
    except Exception as e:
        raise ValueError(f"Error parsing string to set: {e}")

def get_prop(df, column, values):
    pattern_set_col = df[column].apply(string_to_set)
    total_rows = len(df)

    for val in values:
        specs_with_value = pattern_set_col.apply(lambda x: val in x)
        count = specs_with_value.sum()
        if total_rows == 0:
            prop = 0
        else:
            prop = count / total_rows
        print(f"Proportion of specs with {val}: {prop:.2%} ({count}/{total_rows})")
