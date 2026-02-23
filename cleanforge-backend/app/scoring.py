def calculate_quality_score(profile_data):

    total_columns = len(profile_data["columns"])
    total_rows = profile_data["total_rows"]

    # Completeness Score (less harsh on moderate missing values)
    missing_percent_total = 0
    for col in profile_data["columns"].values():
        missing_percent_total += col["missing_percent"]

    avg_missing_percent = missing_percent_total / total_columns
    missing_ratio = max(min(avg_missing_percent / 100, 1), 0)
    completeness_score = 100 * (1 - missing_ratio) ** 0.6

    # Duplicate Penalty
    duplicate_rows = profile_data["duplicate_rows"]
    duplicate_percent = (duplicate_rows / total_rows) * 100
    duplicate_ratio = max(min(duplicate_percent / 100, 1), 0)
    duplicate_score = 100 * (1 - duplicate_ratio) ** 0.8

    # Outlier Penalty
    total_outlier_ratio = 0
    numeric_columns = 0

    for col in profile_data["columns"].values():
        if "outliers" in col:
            non_missing = col.get("non_missing_count", total_rows)
            if non_missing > 0:
                total_outlier_ratio += col["outliers"] / non_missing
                numeric_columns += 1

    if numeric_columns > 0:
        outlier_ratio = total_outlier_ratio / numeric_columns
        outlier_ratio = max(min(outlier_ratio, 1), 0)
        outlier_score = 100 * (1 - outlier_ratio) ** 0.7
    else:
        outlier_score = 100

    # Final Weighted Score
    final_score = (
        0.45 * completeness_score +
        0.25 * duplicate_score +
        0.30 * outlier_score
    )

    return round(final_score, 2)
