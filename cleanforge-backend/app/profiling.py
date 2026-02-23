import pandas as pd
import numpy as np


def generate_profile(df: pd.DataFrame):

    profile = {}
    total_rows = len(df)
    duplicate_count = df.duplicated().sum()

    for col in df.columns:
        column_data = df[col]

        missing_count = column_data.isnull().sum()
        non_missing_count = int(column_data.notnull().sum())
        missing_percent = round((missing_count / total_rows) * 100, 2)

        col_info = {
            "dtype": str(column_data.dtype),
            "missing_count": int(missing_count),
            "non_missing_count": non_missing_count,
            "missing_percent": missing_percent,
            "unique_values": int(column_data.nunique())
        }

        # Numeric outlier detection using IQR
        if pd.api.types.is_numeric_dtype(column_data):
            q1 = column_data.quantile(0.25)
            q3 = column_data.quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = column_data[
                (column_data < lower_bound) |
                (column_data > upper_bound)
            ].count()

            col_info["outliers"] = int(outliers)

        profile[col] = col_info

    return {
        "total_rows": total_rows,
        "duplicate_rows": int(duplicate_count),
        "columns": profile
    }
