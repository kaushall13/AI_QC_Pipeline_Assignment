"""
LLM Planner Agent: Decides which quality control checks to run based on OCR output.
Uses Groq Llama-3 to select checks, or defaults to all if uncertain.
"""
import os, json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = '''
You are a QC planner agent. Given the table below, return a JSON list of checks to run:
["completeness_check", "anomaly_check"] or "*" for all.
TABLE:
{table}
'''

def get_required_checks(csv_path):
    """
    Given a CSV file path, use LLM to decide which checks to run.
    Returns a list of check names, or ["*"] for all.
    """
    with open(csv_path) as f:
        table_data = f.read()

    prompt = PROMPT.format(table=table_data)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content.strip()
    try:
        return json.loads(output)
    except Exception:
        # Fallback: run all checks if LLM output is not valid JSON
        return ["*"]
