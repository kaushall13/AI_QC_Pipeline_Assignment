# Modular AI QC Pipeline for Batch Production Sheets

## Overview
This project is a modular, agent-centric AI pipeline for automating quality control (QC) on hand-written batch-production sheets. It watches a folder for new scans, extracts structured data via OCR, uses LLM agents to plan and summarize QC checks, and (optionally) sends rich email reports.

**Design Philosophy:** Plug-and-play. Add new checks or agents by editing a config or dropping in a new file—no pipeline edits needed.

---

## Features
- **Folder Watcher & CLI:** Watches for new scans or processes a single file or folder via CLI.
- **OCR Engine:** Converts hand-written/printed batch sheets to structured CSV using **Gemini Flash LLM** (no Tesseract/OpenCV required).
- **LLM Planner Agent:** Decides which QC checks to run (**Groq Llama-3**).
- **Deterministic Checks:** Completeness, anomaly detection, KPI summary, and more—easy to extend.
- **LLM Summary Agent:** Summarizes results and recommends actions (**Groq Llama-3**).
- **Rich Email Reports:** (Commented out by default) Sends HTML summary + CSV attachment.
- **Config-Driven:** Checks and agents are loaded from YAML config for easy extensibility. Use `*` in config to auto-discover all checks.

---

## Setup
1. **Clone the repo** and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your Gemini API key, Groq API key (and email creds if enabling email).
3. **Prepare folders:**
   - Place input images in `data/batch_scans/`.
   - Processed CSVs will be saved to `data/processed_csv/`.

---

## Usage
### Watch Mode (default)
```bash
python main.py --watch data/batch_scans
```
Watches for new image files and processes them automatically.

### Single File Mode
```bash
python main.py --file data/batch_scans/sample_001.png
```
Processes a single file and exits (useful for testing/demo).

### Folder Mode
```bash
python main.py --folder data/batch_scans
```
Processes all image files in a folder and exits.

---

## Adding New Checks or Agents
- **Checks:**
  1. Create a new Python file in `checks/` with a `run(df)` function.
  2. Add the check name to `config/checks.yml` (or use `*` to auto-discover all checks).
  3. The completeness check flags as missing: NaN/nulls, empty strings, and the string 'MISSING' (case-insensitive).
- **Agents:**
  1. Add your agent logic in `agents/`.
  2. Update the pipeline to use your agent if needed (minimal changes).

---

## Email Reports (Optional)
- The email sending feature is implemented but commented out by default for safety.
- To enable, fill in your email credentials in `.env` and uncomment the relevant line in `main.py`.

---

## Error Handling & Fallbacks
- If OCR extraction fails, the file is skipped with a clear error message.
- If the LLM planner output is not valid JSON, all checks are run by default.
- If a check fails, the error is captured and reported in the results.
- If not enough historical data is available for KPI summary, a warning is included.
- Email sending is disabled by default for safety; can be enabled as needed.

---

## Contact
For questions or support, contact: [hr@zipp-ai.com](mailto:hr@zipp-ai.com) 