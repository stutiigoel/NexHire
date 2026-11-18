# AI-Driven Resume–Job Vacancy Matching Chatbot

A runnable college project using Streamlit, PDF/DOCX parsing, TF-IDF NLP similarity, skill coverage, SQLite and a transparent rule-based career chatbot. **This prototype is not an LLM-powered generative chatbot.** The seeded companies and jobs are fictional examples, not live vacancies.

## Windows installation

Install Python 3.11 or 3.12. Open PowerShell in this extracted folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If Python 3.11 is not installed, use `py -3.12` if available. If PowerShell prevents activation, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py` instead.

## Test

```powershell
python -m pytest -q
```

## Demo

1. Upload a text-based PDF or DOCX resume (max 5 MB).
2. Review detected skills and job rankings.
3. Expand job cards to see matching and missing skills.
4. Ask “What is my best job match?”, “What skills should I learn?”, or “Why this score?”
5. Add a job through the sidebar and compare again.

## Methodology

- Extract PDF text with PyMuPDF or DOCX paragraphs with python-docx.
- Detect skills with a small predefined dictionary and word-boundary matching.
- Fit a TF-IDF vectorizer over the resume and job descriptions, then calculate cosine similarity.
- Rank with `score = 100 × (0.6 × cosine_similarity + 0.4 × required_skill_coverage)`.
- Respond to selected career questions using computed results; unknown questions get a guided fallback.

## Limitations and ethics

This is an educational demonstration, not a validated hiring system. Scores are heuristic and may be biased by wording, resume length, and the skill dictionary. The system does not verify qualifications, determine eligibility, infer protected attributes, or retrieve live job openings. A missing skill means it was not detected in the resume, not that the applicant lacks it. Resume contents are processed locally in the running app and not intentionally persisted to SQLite; job records are persisted in `data/jobs.db`. Avoid using real personal resumes during public demonstrations. Scanned PDFs need OCR, which is not included. Do not expose the app publicly without security and privacy improvements.
