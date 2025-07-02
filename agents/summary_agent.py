"""
LLM Summary Agent: Summarizes QC check results and provides recommendations.
Uses Groq Llama-3 to generate a concise, actionable summary.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(results):
    """
    Given a dict of check results, use LLM to generate a summary and recommendation.
    Returns a string summary.
    """
    # If KPI summary is a dict with a warning, prepend the warning to the text
    kpi_key = next((k for k in results if 'kpi' in k.lower()), None)
    warning_text = ""
    if kpi_key and isinstance(results[kpi_key], dict) and results[kpi_key].get('warning'):
        warning_text = f"[KPI WARNING]: {results[kpi_key]['warning']}\n"
        # Replace stats dict with just the stats for LLM readability
        results[kpi_key] = results[kpi_key]['stats']
    text = "\n".join(f"{k}:\n{v}" for k, v in results.items())
    prompt = f"""
You are a Quality Control (QC) analyst.

Below are the results of various checks on a batch production record, including:
- Completeness Check
- Anomaly Detection
- KPI Summary (with mean, std, and outliers for the last 30 batches)
- Unit Conversion Check (flags columns with mixed or inconsistent units)

{'There is a warning about the KPI statistics: ' + warning_text if warning_text else ''}
Your task:
1. Summarize any issues or anomalies found, including unit conversion issues.
2. Mention KPI trends, such as abnormal values or deviations.
3. Suggest whether the batch is acceptable, should be reviewed, or rejected.

QC Check Results:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
