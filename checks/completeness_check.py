"""
Completeness Check: Verifies that all fields in the batch sheet are filled (no missing values, including 'MISSING' and empty strings).
"""
def run(df):
    """
    Returns the number of missing fields, or 'All fields complete' if none are missing.
    Flags as missing: NaN/null, empty strings, and the string 'MISSING' (case-insensitive).
    """
    import numpy as np
    # Replace 'MISSING' (case-insensitive) and empty strings with np.nan
    df_clean = df.replace(r'^\s*$|(?i)^missing$', np.nan, regex=True)
    missing = df_clean.isnull().sum().sum()
    return f"{missing} missing fields" if missing else "All fields complete"
