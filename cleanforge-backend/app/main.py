from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import io
import math

from app.profiling import generate_profile
from app.scoring import calculate_quality_score
from app.semantic import generate_semantic_analysis
from app.cleaning import clean_dataset

app = FastAPI()


# ---------- JSON SANITIZER ----------
def sanitize_for_json(value):
    if isinstance(value, dict):
        return {key: sanitize_for_json(val) for key, val in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, (np.floating, np.integer)):
        return sanitize_for_json(value.item())
    if isinstance(value, float):
        return None if not math.isfinite(value) else value
    return value


# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- ROOT ----------
@app.get("/")
def read_root():
    return {"message": "CleanForge Backend Running"}


# ---------- UPLOAD ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns)
    }


# ---------- PROFILE ----------
@app.post("/profile")
async def profile_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    profile_result = generate_profile(df)
    quality_score = calculate_quality_score(profile_result)

    return {
        "quality_score": sanitize_for_json(quality_score),
        "profile": sanitize_for_json(profile_result)
    }


# ---------- SEMANTIC ----------
@app.post("/semantic")
async def semantic_analysis(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    semantic_result = generate_semantic_analysis(df)

    return {
        "semantic_analysis": sanitize_for_json(semantic_result)
    }


# ---------- ANALYZE ----------
@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    profile_result = generate_profile(df)
    quality_score = calculate_quality_score(profile_result)
    semantic_result = generate_semantic_analysis(df)

    return {
        "quality_score": sanitize_for_json(quality_score),
        "profile": sanitize_for_json(profile_result),
        "semantic_analysis": sanitize_for_json(semantic_result)
    }


# ---------- CLEAN + QUALITY IMPROVEMENT ----------
@app.post("/clean")
async def clean_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Quality BEFORE cleaning
    profile_before = generate_profile(df)
    quality_before = calculate_quality_score(profile_before)

    # Apply cleaning
    cleaned_df, cleaning_log = clean_dataset(df)

    # Quality AFTER cleaning
    profile_after = generate_profile(cleaned_df)
    quality_after = calculate_quality_score(profile_after)

    # Sanitize dataframe
    cleaned_df = cleaned_df.replace([np.inf, -np.inf], None)
    cleaned_df = cleaned_df.where(pd.notnull(cleaned_df), None)

    cleaned_preview = (
        cleaned_df.head(10)
        .astype(object)
        .to_dict(orient="records")
    )

    # Calculate improvement
    improvement = None
    if quality_before is not None and quality_after is not None:
        improvement = round(quality_after - quality_before, 2)

    return sanitize_for_json({
        "rows_before": int(len(df)),
        "rows_after": int(len(cleaned_df)),
        "quality_before": quality_before,
        "quality_after": quality_after,
        "improvement": improvement,
        "cleaning_log": [str(item) for item in cleaning_log],
        "cleaned_preview": cleaned_preview,
    })