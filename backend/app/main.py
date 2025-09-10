import os
import uuid
import traceback
import numpy as np
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from supabase import create_client

# Local modules
from .models import extract_text_from_pdf
from .embeddings import get_embeddings
from .send_email import send_shortlist_email

# ================== ENV & SUPABASE ==================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "resumes"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== FASTAPI ==================
app = FastAPI(title="Resume Ranker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# 🔹 NEW: Supabase test endpoint
@app.get("/test_supabase")
def test_supabase():
    data = supabase.table("users").select("*").limit(1).execute()
    return {"data": data.data}

# ================== MODELS ==================
class RankRequest(BaseModel):
    job_title: str
    job_description: str
    created_by: str | None = None

# ================== UPLOAD RESUME ==================
@app.post("/upload")
async def upload_resume(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        fname = f"{user_id}/{uuid.uuid4()}_{file.filename}"

        # Upload to Supabase Storage
        supabase.storage.from_(SUPABASE_BUCKET).upload(fname, content)

        # Public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(fname)

        # Save local copy
        local_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}_{file.filename}")
        with open(local_path, "wb") as f:
            f.write(content)

        # Extract text
        text, used_ocr = extract_text_from_pdf(local_path)

        # Insert metadata into resumes table (match schema)
        r = supabase.table("resumes").insert({
            "user_id": user_id,
            "filename": file.filename,
            "file_url": public_url,
            "content": text
        }).execute()

        return {"ok": True, "resume": r.data}

    except Exception:
        print("🔥 UPLOAD ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Upload failed")

# ================== INDEX EMBEDDINGS ==================
# ================== INDEX EMBEDDINGS ==================
@app.post("/index-embeddings")
def index_embeddings(resume_ids: List[str]):
    try:
        rows = supabase.table("resumes").select("id, content").in_("id", resume_ids).execute()
        items = rows.data
        texts = [it["content"] or "" for it in items]
        embeddings = get_embeddings(texts)

        for i, it in enumerate(items):
            vec = embeddings[i]
            if isinstance(vec, np.ndarray):   # ensure it's a plain list
                vec = vec.tolist()

            supabase.table("resume_embeddings").insert({
                "resume_id": it["id"],
                "embedding": vec
            }).execute()

        return {"indexed": len(items)}

    except Exception:
        print("🔥 INDEX ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Indexing failed")

# ================== RANK RESUMES ==================
@app.post("/rank")
def rank(req: RankRequest):
    try:
        # Insert into resume_rankings (not rankings)
        r = supabase.table("resume_rankings").insert({
            "job_id": None,  # placeholder until you link jobs
            "resume_id": None,
            "score": 0.0
        }).execute()
        ranking_id = r.data[0]["id"]

        q_vec = get_embeddings([req.job_description])[0]
        rows = supabase.table("resume_embeddings").select("resume_id, embedding").execute()
        items = rows.data

        results = []
        for it in items:
            emb = np.array(it["embedding"], dtype=float)
            q = np.array(q_vec, dtype=float)
            sim = float(np.dot(q, emb) / (np.linalg.norm(q) * np.linalg.norm(emb) + 1e-10))
            results.append((it["resume_id"], sim))

        results.sort(key=lambda x: x[1], reverse=True)

        out = []
        for resume_id, score in results:
            supabase.table("resume_rankings").insert({
                "job_id": None,
                "resume_id": resume_id,
                "score": score
            }).execute()
            meta = supabase.table("resumes").select("id, filename, file_url").eq("id", resume_id).single().execute().data
            out.append({"resume": meta, "score": score})

        return {"ranking_id": ranking_id, "results": out}

    except Exception:
        print("🔥 RANKING ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Ranking failed")

# ================== SHORTLIST ==================
@app.post("/shortlist")
def shortlist(job_id: str, resume_id: str, note: str = ""):
    try:
        resume = supabase.table("resumes").select("id, user_id, filename, content").eq("id", resume_id).single().execute().data
        user = supabase.table("users").select("email, name").eq("id", resume["user_id"]).single().execute().data
        job = supabase.table("job_descriptions").select("title").eq("id", job_id).single().execute().data

        subject = job["title"] if job else "Shortlisted"
        message = f"You have been shortlisted for {subject}. Note: {note}"
        status, body, headers = send_shortlist_email(user["email"], user["name"], subject, message)

        return {"status": status}

    except Exception:
        print("🔥 SHORTLIST ERROR:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Shortlist failed")
