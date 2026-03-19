# CleanForge — End-to-End Project Documentation

## 1) Project Summary
CleanForge is an AI-assisted data quality and cleaning platform for CSV datasets. It provides a full workflow from file upload to profiling, semantic issue detection, automatic cleaning, quality score comparison, and cleaned CSV export.

The product is designed for self-serve users (analysts, operations teams, and non-technical data owners) who need practical data cleaning without writing scripts.

---

## 2) Problem Statement
Real-world CSV data is often inconsistent (mixed formats, missing values, duplicates, outliers, and semantic errors). Traditional cleanup is manual and repetitive.

CleanForge addresses this by combining:
- Programmatic data profiling and cleaning (Pandas-based)
- AI-powered semantic analysis (LLM suggestions per column)
- A simple web UI for upload, analyze, clean, preview, and export

---

## 3) Product Scope Implemented So Far
### Core Features
1. **CSV Upload and Analyze**
   - Upload a CSV file from browser UI
   - Compute profile and quality score
   - Generate semantic analysis (issues + suggested fixes)

2. **Automatic Cleaning Pipeline**
   - Duplicate removal
   - Text normalization (trim spaces, normalize common null tokens, remove trailing footnote markers)
   - Numeric-like string coercion (currency symbols, commas, percentages, negatives in parentheses)
   - Domain-specific cleanup for common columns (`Email`, `Phone`, `Country`, `Age`)
   - Numeric median imputation
   - IQR-based outlier capping

3. **Before/After Quality Tracking**
   - Quality score before cleaning
   - Quality score after cleaning
   - Improvement delta

4. **Result Delivery UX**
   - Semantic cards by column
   - Cleaning log showing every transformation applied
   - Cleaned preview table
   - CSV download button
   - In-session dataset history (filename, score, timestamp)

---

## 4) Architecture
## Frontend (Next.js)
- Framework: Next.js App Router
- Language: TypeScript + React
- Styling: Tailwind CSS
- Responsibilities:
  - File selection and drag-drop
  - API calls to backend (`/analyze`, `/clean`)
  - Rendering quality score, semantic details, cleaning logs, and preview
  - Downloading cleaned data as CSV

## Backend (FastAPI)
- Framework: FastAPI + Uvicorn
- Language: Python
- Data Layer: Pandas + NumPy
- AI Integration: OpenAI-compatible client targeting Groq endpoint
- Responsibilities:
  - Parse uploaded CSV files
  - Generate profile and robust quality score
  - Run semantic LLM analysis
  - Execute cleaning pipeline
  - Return JSON-safe responses for frontend rendering

## Service Interfaces
- `POST /upload` — file metadata and shape
- `POST /profile` — profile + quality score
- `POST /semantic` — semantic issue analysis
- `POST /analyze` — profile + score + semantic analysis
- `POST /clean` — cleaned preview + cleaning log + before/after quality

---

## 5) Data Quality Methodology
### 5.1 Profiling
For each column:
- dtype
- missing count / percent
- non-missing count
- unique values
- numeric outlier count using IQR rule

### 5.2 Scoring Model (Current)
The quality score is a weighted composite of:
- **Completeness score** (non-linear penalty on average missing ratio)
- **Duplicate score** (non-linear penalty on duplicate ratio)
- **Outlier score** (average outlier ratio across numeric columns, normalized by non-missing counts)

Current weighting in code:
- Completeness: 45%
- Duplicates: 25%
- Outliers: 30%

This model is designed to be more robust than simple linear penalties and less sensitive to moderate missingness spikes.

### 5.3 Cleaning Rules
- Duplicate row removal
- Generic string normalization:
  - whitespace cleanup
  - null token normalization (`""`, `na`, `n/a`, `null`, `none`, `-`)
  - trailing bracket marker cleanup
- Numeric coercion for parseable string columns
- Specific standardizers:
  - Email lowercasing/trim
  - Phone digit-only normalization
  - Country canonicalization (`US`, `U.S.A`, `United States` -> `USA`)
  - Age filtering (`<=100`)
- Numeric median imputation with nullable integer handling
- Outlier capping with dtype-safe logic (Int64 -> Float64 when needed)

---

## 6) AI Semantic Analysis Method
- Per-column sample extraction from non-null values
- Prompted LLM to return strict JSON with:
  - `semantic_type`
  - `issues_detected[]`
  - `suggested_fixes[]`
- Added resilient JSON extraction strategy:
  - Direct parse attempt
  - JSON code block extraction
  - Brace-window extraction fallback

This reduces failures where model output includes extra wrappers or formatting.

---

## 7) Engineering Challenges Solved
1. **JSON serialization crashes** due to `NaN/Inf` in API responses
   - Added recursive JSON sanitizer in backend

2. **Schema drift across datasets**
   - Moved from fixed-column cleanup to universal heuristics

3. **Pandas nullable integer dtype errors** during fill/cap steps
   - Added dtype-aware casting logic for `Int64` and float median/bounds

4. **LLM structured output instability**
   - Added robust parsing fallback strategy for semantic analysis

5. **Frontend production API misconfiguration**
   - Replaced hardcoded localhost URLs with `NEXT_PUBLIC_API_URL`
   - Enabled deployment-safe frontend/backend decoupling

---

## 8) Tooling and Tech Stack
## Languages
- Python
- TypeScript

## Frameworks & Libraries
- FastAPI, Uvicorn
- Pandas, NumPy
- OpenAI Python SDK (Groq-compatible endpoint)
- Next.js, React, Tailwind CSS

## Deployment Platforms
- Backend target: Render
- Frontend target: Vercel

## Environment Variables
- Backend: `GROQ_API_KEY`
- Frontend: `NEXT_PUBLIC_API_URL`

---

## 9) Local Development Workflow
## Backend
1. Go to `cleanforge-backend`
2. Create/activate virtual env
3. Install dependencies
4. Run API server

Example commands:
```bash
cd cleanforge-backend
python -m venv venv
# PowerShell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend
1. Go to `cleanforge-frontend`
2. Install dependencies
3. Set frontend env var
4. Run dev server

Example:
```bash
cd cleanforge-frontend
npm install
# .env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:10000
npm run dev
```

---

## 10) Deployment Flow (Resume-Ready)
## Backend on Render
- Runtime: Python
- Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- Set `GROQ_API_KEY` in Render environment settings
- Verify health via root endpoint

## Frontend on Vercel
- Framework preset: Next.js
- Set environment variable:
  - `NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com`
- Redeploy after env update

## Important Deployment Note
`0.0.0.0` is a server bind address, not a browser URL. Local browser testing should use `localhost` or `127.0.0.1`.

---

## 11) Innovation Highlights
1. **Hybrid AI + deterministic cleaning**
   - Combines LLM semantic intelligence with reproducible Pandas transformations

2. **Universal-first cleaning strategy**
   - Dynamic coercion/normalization across varied schemas

3. **Score-aware cleaning feedback loop**
   - Measures quality before and after cleaning in one API flow

4. **Robust fault handling for real-world data**
   - JSON-safe API output and dtype-safe numerical operations

---

## 12) Resume Section (Copy-Ready)
### Project: CleanForge — AI-Native Data Profiling & Cleaning Platform
- Built a full-stack data quality platform (FastAPI + Next.js) to analyze, clean, and export CSV datasets end-to-end.
- Implemented a robust cleaning pipeline with duplicate removal, text normalization, numeric coercion, median imputation, and IQR-based outlier capping.
- Designed a composite data quality scoring model balancing completeness, duplicate ratio, and outlier density with non-linear penalties.
- Integrated LLM-based semantic analysis to auto-detect column-level issues and recommend targeted cleaning strategies.
- Added production-ready deployment flow across Render (backend) and Vercel (frontend) with environment-driven API routing.
- Improved reliability by handling `NaN/Inf` JSON serialization, nullable integer dtype edge cases, and non-strict LLM JSON outputs.

---

## 13) Current Status and Next Milestones
### Current Status
- Core MVP is implemented and working for heterogeneous CSV data.
- Frontend and backend are deployable with environment configuration.

### Suggested Next Milestones
1. Semantic-fix execution layer (apply selected AI suggestions automatically)
2. Date/time normalization and schema-specific rule packs
3. Column-level confidence and rule impact metrics
4. User auth + project history persistence
5. Batch processing and larger-file performance optimization

---

## 14) Repository Paths
- Frontend UI: `cleanforge-frontend/app/page.tsx`
- Backend API: `cleanforge-backend/app/main.py`
- Profiling: `cleanforge-backend/app/profiling.py`
- Scoring: `cleanforge-backend/app/scoring.py`
- Cleaning engine: `cleanforge-backend/app/cleaning.py`
- Semantic analysis: `cleanforge-backend/app/semantic.py`

---

Prepared as a portfolio/resume-ready project brief for CleanForge (current implementation state).