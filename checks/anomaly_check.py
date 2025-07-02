"""
Anomaly Check: Flags numeric columns with values > 3 standard deviations from the mean (z-score outliers).
"""
def run(df):
    """
    Returns a dict of columns with outlier counts, or 'No anomalies' if none found.
    """
    import numpy as np
    flagged = {}
    for col in df.select_dtypes(include='number').columns:
        z_scores = (df[col] - df[col].mean()) / df[col].std()
        anomalies = df[abs(z_scores) > 3]
        if not anomalies.empty:
            flagged[col] = f"{len(anomalies)} outlier(s)"
    return flagged if flagged else "No anomalies"
