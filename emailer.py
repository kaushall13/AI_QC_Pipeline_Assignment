import smtplib, os, pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT = os.getenv("EMAIL_TO", EMAIL)

def send_email(summary, results, csv_path):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = RECIPIENT
    msg["Subject"] = f"Zipp QC Report: {os.path.basename(csv_path)}"

    df = pd.read_csv(csv_path)
    html = df.to_html(index=False)
    # Build checks table
    checks_table = "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;margin-bottom:20px;'>"
    checks_table += "<tr><th>Check</th><th>Result</th></tr>"
    for k, v in results.items():
        checks_table += f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
    checks_table += "</table>"
    # Add completeness check note if present
    if any('completeness' in k for k in results):
        checks_table += "<div style='font-size:12px;color:#888;margin-bottom:10px;'>Note: The completeness check now flags as missing: NaN/nulls, empty strings, and the string 'MISSING' (case-insensitive).</div>"
    # Show KPI warning if present
    kpi_key = next((k for k in results if 'kpi' in k.lower()), None)
    kpi_warning = ""
    if kpi_key and isinstance(results[kpi_key], dict) and results[kpi_key].get('warning'):
        kpi_warning = f"<div style='color:#b85c00; font-weight:bold; margin-bottom:10px;'>\u26a0 {results[kpi_key]['warning']}</div>"

    # --- Improved summary formatting ---
    # Convert basic markdown to HTML for better email rendering
    def md_to_html(text):
        # Convert headers (##, ###, etc.) to <h3>
        text = re.sub(r"^### (.*)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(r"^## (.*)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^# (.*)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
        # Bold **text**
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        # Italic *text*
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
        # Numbered lists
        text = re.sub(r"(?:^|\n)\s*\d+\. (.*)", r"<li>\1</li>", text)
        text = re.sub(r"(<li>.*?</li>)", r"<ol>\1</ol>", text, flags=re.DOTALL)
        # Bulleted lists
        text = re.sub(r"(?:^|\n)\s*\- (.*)", r"<li>\1</li>", text)
        text = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", text, flags=re.DOTALL)
        # Remove stray markdown headers
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        return text

    summary_html = "<h2>Summary</h2>" + kpi_warning
    summary_html += f"<div style='margin-bottom:20px;'>{md_to_html(summary)}</div>"

    # Full content
    content = f"""
    <h1 style='color:#2d6cdf;'>Zipp QC Report</h1>
    {summary_html}
    <h2>QC Checks</h2>
    {checks_table}
    <h2>Batch Data</h2>
    {html}
    """
    msg.attach(MIMEText(content, "html"))

    with open(csv_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(csv_path)}")
        msg.attach(part)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(EMAIL, PASSWORD)
    s.send_message(msg)
    s.quit()
    print(f"-----Email sent to {RECIPIENT}.-------")
