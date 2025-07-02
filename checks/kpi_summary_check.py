"""
KPI Summary Check: Computes mean, std, min, max, and outlier count for key KPIs using last 30 records.
Flags values > 3σ as outliers.
"""
import os
import pandas as pd
import numpy as np

def clean_numeric(series):
    # Remove % and convert to float if needed
    return pd.to_numeric(series.astype(str).str.replace('%', ''), errors='coerce')

def run(current_df):
    """
    Computes summary statistics for key KPIs using historical data (last 30 CSVs).
    Returns a dict of stats per KPI, or a message if not enough data.
    """
    history_dir = "./data/processed_csv"
    kpis = ["Temperature", "Pressure", "pH", "Volume", "Yield"]

    # Normalize column names for matching (case-insensitive, strip spaces)
    def normalize(col):
        return col.strip().lower()
    current_cols = {normalize(c): c for c in current_df.columns}
    # Print debug info
    print("Current DataFrame columns:", list(current_df.columns))

    # Collect last 30 valid CSV files
    if not os.path.exists(history_dir):
        return "No historical data directory found."

    history_files = sorted([
        os.path.join(history_dir, f)
        for f in os.listdir(history_dir)
        if f.endswith(".csv")
    ])[-30:]

    if len(history_files) < 3:
        return "Not enough historical data (need ≥ 3)."

    # Load historical CSVs
    history_df = pd.concat(
        [pd.read_csv(f) for f in history_files],
        ignore_index=True
    )
    history_cols = {normalize(c): c for c in history_df.columns}
    print("History DataFrame columns:", list(history_df.columns))

    stats = {}
    for kpi in kpis:
        kpi_norm = normalize(kpi)
        if kpi_norm not in current_cols or kpi_norm not in history_cols:
            continue
        cur_col = current_cols[kpi_norm]
        hist_col = history_cols[kpi_norm]
        try:
            hist_values = clean_numeric(history_df[hist_col]).dropna()
            current_values = clean_numeric(current_df[cur_col]).dropna()
            print(f"KPI: {kpi} | Current cleaned values: {list(current_values)} | History cleaned values: {list(hist_values)}")
        except Exception as e:
            print(f"Error cleaning KPI {kpi}: {e}")
            continue
        if hist_values.empty or current_values.empty:
            continue
        mean = hist_values.mean()
        std = hist_values.std()
        min_val = hist_values.min()
        max_val = hist_values.max()
        # Flag outliers in current batch (> 3σ from mean)
        z_scores = (current_values - mean) / std
        outliers = current_values[abs(z_scores) > 3]
        stats[kpi] = {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "outliers": len(outliers)
        }
    if not stats:
        return "No KPI statistics generated."
    warning = ""
    if len(history_files) < 30:
        warning = f"Warning: Only {len(history_files)} historical records found (expected 30). Statistics are based on available data. "
    return {"warning": warning, "stats": stats} if warning else stats
