# Design Document: Modular AI QC Pipeline

## 1. Architecture Overview
- **Folder Watcher/CLI:** Detects new batch sheet scans (images) for processing. Supports folder watching, single-file, or batch processing via CLI.
- **OCR Engine:** Converts images to structured CSV using **Gemini Flash LLM** (no Tesseract/OpenCV/TrOCR).
- **LLM Planner Agent:** Inspects OCR output and selects which QC checks to run (**Groq Llama-3**).
- **Check Runner:** Dynamically loads and executes checks listed in `config/checks.yml` from the `checks/` directory. If `*` is specified, auto-discovers all checks.
- **Deterministic Checks:** Each check is a plug-in Python module (completeness, anomaly, KPI summary, etc.), with a `run(df)` function.
- **LLM Summary Agent:** Summarizes check results and recommends actions (**Groq Llama-3**).
- **Emailer (Optional):** Composes and sends rich HTML email with summary and CSV (commented out by default for safety).

**Tech Stack:**
- Built in Python for rapid prototyping and extensibility.
- Compatible with modern LLM APIs (Gemini, Groq, etc.).

**Data Flow:**
```
[Image] → [Gemini OCR] → [CSV] → [Llama-3 Planner] → [Check Runner] → [Llama-3 Summary] → [Email/Output]
```

---

## 2. Trade-offs & Design Choices
- **Plug-and-Play Extensibility:**
  - Checks and agents are loaded via config and dynamic import—no pipeline edits needed to add new ones.
- **LLM for Planning & Summarization:**
  - LLMs (Groq Llama-3) provide flexible, context-aware check selection and human-like summaries.
  - Fallbacks ensure robustness if LLM output is invalid (e.g., run all checks if planner output is not valid JSON).
- **Deterministic Checks:**
  - Each check is a simple, testable Python module—easy to extend and maintain.
  - The completeness check flags as missing: NaN/nulls, empty strings, and the string 'MISSING' (case-insensitive).
- **Config-Driven:**
  - `config/checks.yml` controls which checks are available and their order. If `*` is specified, all checks in `checks/` are auto-discovered.
- **Email Sending:**
  - Implemented but commented out for security/testing; easy to enable later.
- **Error Handling:**
  - Robust try/except blocks and clear error messages throughout. Fallbacks for LLM failures.
- **LLM API Flexibility:**
  - The architecture is designed to be compatible with a range of modern LLM APIs (Gemini, Groq, etc.), making it future-proof and easy to adapt.

---

## 3. LLM Planner Prompt/Logic
- **Prompt Example:**
  ```
  You are a QC planner agent. Given the table below, return a JSON list of checks to run:
  ["completeness_check", "anomaly_check"] or "*" for all.
  TABLE:
  {table}
  ```
- **Logic:**
  - LLM (Groq Llama-3) inspects the OCR'd table and outputs a JSON list of check names (or "*" for all).
  - If output is not valid JSON, pipeline defaults to running all checks.

---

## 4. Adding New Checks or Agents
### To Add a New Check:
1. Create a new Python file in `checks/` with a `run(df)` function.
2. Add the check name to `config/checks.yml` (or use `*` to auto-discover all checks).
3. (Optional) Update the LLM planner prompt to mention the new check.

### To Add a New Agent:
1. Add your agent logic in `agents/` (e.g., a new summary or planner agent).
2. Update the pipeline to use your agent if needed (minimal changes).

**Note:** No changes to the main pipeline logic are needed to add new checks or agents—just drop in a new file and update the config.

---

## 5. Extensibility Example
- **Adding a Unit Conversion Check:**
  1. Create `checks/unit_conversion_check.py` with a `run(df)` function.
  2. Add `unit_conversion_check` to `config/checks.yml` (or use `*`).
  3. No changes needed to the pipeline logic.

---

## 6. Error Handling & Fallbacks
- If OCR extraction fails, the file is skipped with a clear error message.
- If the LLM planner output is not valid JSON, all checks are run by default.
- If a check fails, the error is captured and reported in the results.
- If not enough historical data is available for KPI summary, a warning is included.
- Email sending is disabled by default for safety; can be enabled as needed.

---

## 7. Contact & Support
For questions or support, contact: [hr@zipp-ai.com](mailto:hr@zipp-ai.com) 