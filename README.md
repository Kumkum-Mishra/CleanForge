# CleanForge

AI-native data profiling and cleaning platform for CSV files.

CleanForge helps you upload messy datasets, detect quality issues, get semantic recommendations, apply cleaning transformations, compare quality before/after, and download cleaned output.

---

## Features

- Upload CSV data from a web UI
- Compute dataset profile (missing values, duplicates, outliers)
- Generate AI semantic analysis by column
- Apply automated cleaning pipeline
- Compare quality score before vs after cleaning
- Preview cleaned rows and download as CSV
- Track analyzed datasets in session history

---

## Tech Stack

### Frontend
- Next.js (App Router)
- React + TypeScript
- Tailwind CSS

### Backend
- FastAPI + Uvicorn
- Pandas + NumPy
- OpenAI-compatible SDK with Groq endpoint (semantic analysis)

### Deployment
- Frontend: Vercel
- Backend: Render

---

## Repository Structure

```text
cleanforge-backend/
  app/
    main.py         # FastAPI routes
    profiling.py    # Dataset profiling logic
    scoring.py      # Quality score calculation
    semantic.py     # AI semantic analysis
    cleaning.py     # Data cleaning pipeline
  requirements.txt

cleanforge-frontend/
  app/
    page.tsx        # Main UI workflow
  package.json

PROJECT_DOCUMENTATION.md # Detailed project report
README.md                # This file
```

---

## How It Works

1. User uploads a CSV in frontend.
2. Frontend sends file to backend `/analyze` endpoint.
3. Backend computes:
   - Profile (`profiling.py`)
   - Quality score (`scoring.py`)
   - Semantic suggestions (`semantic.py`)
4. Frontend displays score + semantic issue cards.
5. User clicks **Apply Cleaning**.
6. Frontend sends same file to `/clean` endpoint.
7. Backend runs cleaning pipeline (`cleaning.py`), recomputes score, and returns:
   - cleaned preview
   - cleaning log
   - quality before/after + improvement
8. Frontend allows cleaned CSV download.

---

## Cleaning Pipeline (Current)

- Remove duplicate rows
- Normalize text values:
  - trim spaces
  - normalize null-like tokens (`""`, `na`, `n/a`, `null`, `none`, `-`)
  - remove trailing bracket markers
- Convert numeric-like text to numbers (currency, commas, `%`, parenthesis negatives)
- Column-specific normalizers:
  - Email -> lowercase/trim
  - Phone -> digits only
  - Country normalization (`US`, `U.S.A`, `United States` -> `USA`)
  - Remove ages > 100
- Fill missing numeric values with median (dtype-safe for nullable integer columns)
- Cap numeric outliers using IQR bounds (dtype-safe casting when needed)

---

## Quality Score (Current)

Composite score out of 100 built from:
- Completeness
- Duplicate ratio
- Outlier ratio

Uses non-linear penalties and weighted components for better robustness on real-world data.

---

## API Endpoints

- `GET /` -> Health message
- `POST /upload` -> File metadata (rows, columns, names)
- `POST /profile` -> Profile + quality score
- `POST /semantic` -> Semantic analysis only
- `POST /analyze` -> Profile + quality + semantic analysis
- `POST /clean` -> Cleaned preview + cleaning log + before/after quality

---

## Local Setup

## 1) Backend Setup

```powershell
cd cleanforge-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `cleanforge-backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Run backend:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

> Open locally at `http://127.0.0.1:10000`

## 2) Frontend Setup

```powershell
cd cleanforge-frontend
npm install
```

Create `cleanforge-frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:10000
```

Run frontend:

```powershell
npm run dev
```

Open:
- Frontend: `http://localhost:3000`

---

## Production Deployment

## Backend on Render

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables on Render:
- `GROQ_API_KEY`

## Frontend on Vercel

Set environment variable in Vercel project settings:
- `NEXT_PUBLIC_API_URL=https://<your-render-backend>.onrender.com`

Redeploy frontend after setting env var.

---

## Common Issues and Fixes

### 1) `POST /undefined/analyze` or analyze fails on frontend
Cause: `NEXT_PUBLIC_API_URL` is missing.
Fix: set env var and restart frontend.

### 2) Browser cannot open `http://0.0.0.0:<port>`
Cause: `0.0.0.0` is bind host, not browser URL.
Fix: use `http://localhost:<port>` or `http://127.0.0.1:<port>`.

### 3) Semantic analysis shows `raw_output`
Cause: model returned non-strict JSON.
Fix: parser includes fallback extraction, but quality improves with better input sample and stable API key/model output.


## License

This project is currently for personal/portfolio use. Add a formal license if distributing publicly.
