"""
Check Runner: Dynamically loads and executes quality control checks on the parsed CSV.
Checks are listed in config/checks.yml, but if '*' is given or checks is None, all .py files in checks/ are auto-discovered (plug-and-play).
"""
import importlib
import yaml
import pandas as pd
import os

def discover_checks():
    """
    Auto-discovers all check modules in the checks/ directory (excluding __init__.py and __pycache__).
    Returns a list of check module names (without .py).
    """
    check_dir = "checks"
    files = [f for f in os.listdir(check_dir) if f.endswith(".py") and not f.startswith("__")]
    return [os.path.splitext(f)[0] for f in files]

# Load available checks from config
with open("config/checks.yml") as f:
    config = yaml.safe_load(f)

def run_checks(csv_path, checks):
    """
    Run the specified checks (or all if '*' or None is given) on the CSV at csv_path.
    Dynamically imports each check module from checks/ and calls its run(df) method.
    Returns a dict of check results.
    """
    if not checks or checks == "*" or "*" in checks:
        checks = config.get("available_checks") or discover_checks()
        # If config is empty, auto-discover
        if not checks:
            checks = discover_checks()
    df = pd.read_csv(csv_path)
    results = {}
    for check in checks:
        try:
            mod = importlib.import_module(f"checks.{check}")
            results[check] = mod.run(df)
        except Exception as e:
            results[check] = f"[ERROR] Check failed: {e}"
    return results
