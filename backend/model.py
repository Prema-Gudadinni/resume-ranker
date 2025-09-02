# backend/model.py
import os
import re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2

JOB_DESC = """
We are hiring a Python Developer skilled in Flask, Machine Learning,
and REST APIs. Experience with SQL and cloud is a plus.
"""

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        # return empty string on failure; caller can log/handle
        return ""
    return text

def rank_resumes(folder: str = "resumes") -> List[Dict]:
    # build TF-IDF on job description (fits the small example)
    vec = TfidfVectorizer(stop_words="english")
    jd_vec = vec.fit_transform([JOB_DESC])
    results = []
    for fname in os.listdir(folder):
        if not fname.lower().endswith((".pdf", ".txt")):
            continue
        path = os.path.join(folder, fname)
        text = extract_text(path)
        if not text:
            results.append({"name": fname, "score": 0.0, "note": "no text"})
            continue
        try:
            rv = vec.transform([text])
            score = float(cosine_similarity(jd_vec, rv)[0,0])
            results.append({"name": fname, "score": round(score*100, 2)})
        except ValueError:
            # empty vocab or transform error
            results.append({"name": fname, "score": 0.0, "note": "transform failed"})
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results
