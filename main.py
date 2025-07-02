"""
Main entry point for the AI QC pipeline.
Supports both folder watching and single-file processing via CLI.
"""
import argparse
import os
from utils.file_watcher import watch_folder
from ocr_engine import run_ocr
from agents.planner_agent import get_required_checks
from check_runner import run_checks
from agents.summary_agent import generate_summary
from emailer import send_email

def process_file(filepath):
    """Process a single batch sheet file through the pipeline."""
    print(f"\nProcessing file: {filepath}")
    try:
        csv_path = run_ocr(filepath)
        if not csv_path:
            print("OCR failed or no valid rows found. Skipping this file.\n" + "=" * 50)
            return

        checks_to_run = get_required_checks(csv_path)
        print(f"LLM Planner selected checks: {checks_to_run}")

        check_results = run_checks(csv_path, checks_to_run)
        print("QC Check Results:")
        for k, v in check_results.items():
            print(f" - {k}: {v}")

        summary = generate_summary(check_results)
        # Save current CSV to history folder for KPI baseline
        import shutil
        history_path = "./data/processed_csv"
        os.makedirs(history_path, exist_ok=True)
        shutil.copy(csv_path, os.path.join(history_path, os.path.basename(csv_path)))

        print("\nSummary Report:")
        print(summary)

        send_email(summary, check_results, csv_path)  # Always send email after processing
        print("Pipeline complete for this file.\n" + "=" * 50)
    except Exception as e:
        print(f"[ERROR] Exception during processing: {e}\n{'='*50}")

def main():
    parser = argparse.ArgumentParser(description="AI QC Pipeline for Batch Production Sheets")
    parser.add_argument('--watch', type=str, help='Folder to watch for new scans')
    parser.add_argument('--file', type=str, help='Process a single file and exit')
    parser.add_argument('--folder', type=str, help='Process all image files in a folder and exit')
    args = parser.parse_args()

    if args.file:
        process_file(args.file)
    elif args.folder:
        import glob
        import itertools
        exts = ('*.png', '*.jpg', '*.jpeg')
        files = list(itertools.chain.from_iterable(glob.glob(os.path.join(args.folder, ext)) for ext in exts))
        if not files:
            print(f"No image files found in {args.folder}")
            return
        for f in files:
            process_file(f)
    else:
        folder = args.watch or "./data/batch_scans"
        print(f" Watching for new handwritten batch sheets in: {folder}")
        for filepath in watch_folder(folder):
            process_file(filepath)

if __name__ == "__main__":
    main()
