import pandas as pd
import re


def clean_dataset(df: pd.DataFrame):

    cleaning_log = []

    original_rows = len(df)

    # Remove duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        df = df.drop_duplicates()
        cleaning_log.append(f"Removed {duplicate_count} duplicate rows")

    # Standardize email
    if "Email" in df.columns:
        df["Email"] = df["Email"].str.lower().str.strip()
        cleaning_log.append("Standardized email format (lowercase + trimmed)")

    # Fix phone format (simple normalization)
    if "Phone" in df.columns:
        df["Phone"] = df["Phone"].astype(str)
        df["Phone"] = df["Phone"].str.replace(r"[^\d]", "", regex=True)
        cleaning_log.append("Normalized phone numbers to digits only")

    # Fix country names
    if "Country" in df.columns:
        df["Country"] = df["Country"].replace({
            "US": "USA",
            "U.S.A": "USA",
            "United States": "USA"
        })
        cleaning_log.append("Standardized country values")

    # Remove unrealistic age
    if "Age" in df.columns:
        df = df[df["Age"] <= 100]
        cleaning_log.append("Removed unrealistic age values (>100)")

    # Fill missing numeric values with median
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        if df[col].isnull().sum() > 0:
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            cleaning_log.append(f"Filled missing values in {col} with median")

    final_rows = len(df)

    return df, cleaning_log
