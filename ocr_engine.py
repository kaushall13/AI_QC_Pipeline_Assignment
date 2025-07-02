"""
OCR Engine: Uses Gemini Flash (google-generativeai) to extract a structured table from a batch sheet image.
No Tesseract, TrOCR, or OpenCV used—only Gemini Flash LLM.
"""
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from io import StringIO
load_dotenv()

def run_ocr(filepath, llm="gemini"):
    """
    Uses Gemini Flash to extract a CSV table from a batch sheet image.
    Returns the path to the generated CSV, or None if extraction fails.
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = '''
You are an expert at reading batch production tables from images. Extract the entire table as CSV, using the pipe character (|) as the delimiter between columns. Do not use commas or semicolons as delimiters. If a value is missing or unclear, write 'MISSING'.
'''
    try:
        with Image.open(filepath) as img:
            response = model.generate_content([
                prompt,
                img
            ])
        output = response.text.strip()
        # Only keep the table part (lines with delimiters)
        lines = [l for l in output.splitlines() if '|' in l]
        csv_text = '\n'.join(lines)
        # Try parsing with pipe delimiter first, then fallback to others
        df = None
        for delim in ['|', ';', ',', '\t']:
            try:
                df = pd.read_csv(StringIO(csv_text), delimiter=delim)
                if df.shape[1] > 1:
                    break
            except Exception:
                continue
        if df is None or df.shape[1] <= 1:
            raise ValueError("Failed to parse table with any common delimiter.")
        print("[DEBUG] DataFrame after Gemini Flash:")
        print(df)
        csv_path = filepath.replace(".png", ".csv").replace(".jpg", ".csv")
        df.to_csv(csv_path, index=False)
        print(f"Gemini Flash extraction complete → Structured CSV saved: {csv_path}")
        return csv_path
    except Exception as e:
        print(f"[ERROR] Gemini Flash extraction failed: {e}")
        return None
