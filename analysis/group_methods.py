import pandas as pd
import numpy as np
from helper_methods import get_df_rows_timeout, get_df_rows_no_timeout

# Different columns get different grouping treatment

null_columns = ['PRE_ROYBDD_ORDER', 'POST_HEURISTICS_ORDER', 'POST_SECOND_STEP_ORDER', 'POST_WORK_ORDER']
mean_columns = ['INITIAL_BDD_TIME', 'HEURISTICS_TIME', 'SECOND_STEP_TIME',
                'PARALLEL_OVERHEAD_TIME', 'WORK_TIME', 'TOTAL_TIME', 'PRE_ROYBDD_NODE_SIZE',
                'POST_HEURISTICS_NODE_SIZE', 'POST_SECOND_STEP_NODE_SIZE',
                'POST_WORK_NODE_SIZE', 'TOTAL_REORDER_TIME', 'REORDER_CALL_AMOUNT', 'AVERAGE_REORDER_TIME',
                'AVERAGE_REORDER_GAIN','X_FIXPOINTS','Y_FIXPOINTS','Z_FIXPOINTS']
equal_columns = ['Result','TIMEOUT', 'UNIQUE_PATTERNS', 'PATTERN_INSTANCES',
                 'TRIGGER_INSTANCES', 'REDUCED_PATTERN',
                 'REDUCED_TRIGGER', 'ADDITIONAL']
OR_relation_columns = ['SWAPPED_TO_ORIGINAL'] # OR relation between all the values
AND_relation_columns = []
any_no_nan_columns = ['CLUSTER_INC_DATA']


def group(df):

  # Define custom aggregation functions
  def check_all_equal(series):
      if series.nunique() == 1:
          return series.iloc[0]
      else:
          return 'INCONSISTENT'


  def any_non_nan(series):
      return next((x for x in series if pd.notna(x) and x is not None), None)

  def custom_null_agg(series):
      non_null = series.dropna()
      if non_null.empty:
          return np.nan
      elif non_null.nunique() == 1:
          return non_null.iloc[0]
      else:
          return 'INCONSISTENT'


  def and_relation(series):
      if series.isin([0, 1, True, False]).all():
          return all(series)
      else:
          return 'INCONSISTENT'

  def or_relation(series):
      if series.isin([0, 1, True, False]).all():
          return any(series)
      else:
          return 'INCONSISTENT'
      
  # Split based on timeout
  df_no_timeout = get_df_rows_no_timeout(df)
  df_timeout = get_df_rows_timeout(df)

  # Create the aggregation dictionary
  agg_dict = {col: custom_null_agg for col in null_columns}
  agg_dict.update({col: 'mean' for col in mean_columns})
  agg_dict.update({col: check_all_equal for col in equal_columns})
  agg_dict.update({col: and_relation for col in AND_relation_columns})
  agg_dict.update({col: or_relation for col in OR_relation_columns})

  # Perform the groupby operation with the specified aggregations on df_no_timeout
  df_aggregated_no_timeout = df_no_timeout.groupby(['Spec', 'RunConfig']).agg(agg_dict).reset_index()

  # For df_timeout, we'll keep all rows
  df_timeout_reset = df_timeout

  # Combine the aggregated no-timeout data with the timeout data
  df_combined = pd.concat([df_aggregated_no_timeout, df_timeout_reset], ignore_index=True)

  # Sort the combined dataframe by Spec and RunConfig.
  df_combined = df_combined.sort_values(['Spec', 'RunConfig']).reset_index(drop=True)

  return df_combined



