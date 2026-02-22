def calculate_quality_score(profile_data):

    total_columns = len(profile_data["columns"])
    total_rows = profile_data["total_rows"]

    # Completeness Score
    missing_percent_total = 0
    for col in profile_data["columns"].values():
        missing_percent_total += col["missing_percent"]

    avg_missing_percent = missing_percent_total / total_columns
    completeness_score = 100 - avg_missing_percent

    # Duplicate Penalty
    duplicate_rows = profile_data["duplicate_rows"]
    duplicate_percent = (duplicate_rows / total_rows) * 100
    duplicate_score = 100 - duplicate_percent

    # Outlier Penalty
    total_outliers = 0
    numeric_columns = 0

    for col in profile_data["columns"].values():
        if "outliers" in col:
            total_outliers += col["outliers"]
            numeric_columns += 1

    if numeric_columns > 0:
        outlier_percent = (total_outliers / total_rows) * 100
        outlier_score = 100 - outlier_percent
    else:
        outlier_score = 100

    # Final Weighted Score
    final_score = (
        0.5 * completeness_score +
        0.3 * duplicate_score +
        0.2 * outlier_score
    )

    return round(final_score, 2)
