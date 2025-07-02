"""
Unit Conversion Check: Detects columns with mixed or inconsistent units and suggests conversion.
"""
import re

def run(df):
    """
    Scans all columns for mixed units (e.g., 'mg' vs 'g', 'L' vs 'ml').
    Returns a dict of columns with detected unit inconsistencies, or 'No unit issues' if none found.
    """
    unit_pattern = re.compile(r"([\d\.]+)\s*([a-zA-Z%]+)")
    issues = {}
    for col in df.columns:
        # Only check columns with string/object dtype
        if df[col].dtype == object:
            units = set()
            for val in df[col].dropna():
                match = unit_pattern.search(str(val))
                if match:
                    units.add(match.group(2).lower())
            if len(units) > 1:
                issues[col] = f"Mixed units detected: {', '.join(sorted(units))}"
    return issues if issues else "No unit issues" 