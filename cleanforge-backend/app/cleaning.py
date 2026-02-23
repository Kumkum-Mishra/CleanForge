import pandas as pd
import re


NUMERIC_EXCLUDE_PATTERN = re.compile(r"\b(id|code|zip|postal|phone|ssn)\b", re.IGNORECASE)


def normalize_string_series(series: pd.Series):
    cleaned = series.astype("string")
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True).str.strip()
    cleaned = cleaned.replace({
        "": pd.NA,
        "nan": pd.NA,
        "na": pd.NA,
        "n/a": pd.NA,
        "null": pd.NA,
        "none": pd.NA,
        "-": pd.NA,
    })
    cleaned = cleaned.str.replace(r"\s*\[[^\]]+\]\s*$", "", regex=True)
    return cleaned


def try_parse_numeric(series: pd.Series):
    cleaned = series.astype("string")
    cleaned = cleaned.str.replace(r"[,$€£¥]", "", regex=True)
    cleaned = cleaned.str.replace(r"\(([^)]+)\)", r"-\1", regex=True)
    cleaned = cleaned.str.replace(r"%", "", regex=True)
    cleaned = cleaned.str.replace(r"\s+", "", regex=True)

    parsed = pd.to_numeric(cleaned, errors="coerce")
    non_null = series.notna().sum()
    if non_null == 0:
        return None

    success_ratio = parsed.notna().sum() / non_null
    if success_ratio >= 0.85:
        return parsed
    return None


def clean_dataset(df: pd.DataFrame):

    cleaning_log = []

    original_rows = len(df)

    # Remove duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        df = df.drop_duplicates()
        cleaning_log.append(f"Removed {duplicate_count} duplicate rows")

    # Normalize strings and coerce numeric-like columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        before = df[col]
        normalized = normalize_string_series(before)
        if normalized.ne(before).fillna(False).any():
            df[col] = normalized
            cleaning_log.append(f"Normalized text in {col}")

        if not NUMERIC_EXCLUDE_PATTERN.search(str(col)):
            numeric_parsed = try_parse_numeric(df[col])
            if numeric_parsed is not None:
                df[col] = numeric_parsed
                cleaning_log.append(f"Converted numeric-like strings in {col}")

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
    for col in df.select_dtypes(include=["number"]).columns:
        if df[col].isnull().sum() > 0:
            median_value = df[col].median()
            if pd.isna(median_value):
                continue

            fill_value = median_value
            if pd.api.types.is_integer_dtype(df[col].dtype):
                if float(median_value).is_integer():
                    fill_value = int(median_value)
                else:
                    df[col] = df[col].astype("Float64")
                    fill_value = float(median_value)
                    cleaning_log.append(
                        f"Converted {col} to float for median fill"
                    )

            df[col] = df[col].fillna(fill_value)
            cleaning_log.append(f"Filled missing values in {col} with median")

    # Cap extreme outliers (IQR) to reduce skew
    for col in df.select_dtypes(include=["number"]).columns:
        series = df[col]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_count = ((series < lower_bound) | (series > upper_bound)).sum()
        if outlier_count > 0:
            if pd.api.types.is_integer_dtype(series.dtype):
                if float(lower_bound).is_integer() and float(upper_bound).is_integer():
                    df[col] = series.clip(
                        lower=int(lower_bound),
                        upper=int(upper_bound)
                    )
                else:
                    df[col] = series.astype("Float64").clip(
                        lower=float(lower_bound),
                        upper=float(upper_bound)
                    )
                    cleaning_log.append(
                        f"Converted {col} to float for outlier capping"
                    )
            else:
                df[col] = series.clip(lower=lower_bound, upper=upper_bound)
            cleaning_log.append(f"Capped {int(outlier_count)} outliers in {col}")

    final_rows = len(df)

    return df, cleaning_log
