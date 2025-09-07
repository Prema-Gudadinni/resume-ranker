# app/main.py
from dotenv import load_dotenv
load_dotenv()
import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import extract_text_from_pdf
from .embeddings import get_embeddings
from .send_email import send_shortlist_email
from supabase import create_client
import numpy as np
import uuid
from pydantic import BaseModel

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Resume Ranker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

class RankRequest(BaseModel):
    job_title: str
    job_description: str
    created_by: str = None  # optional supabase profile id uuid

@app.post("/upload")
async def upload_resume(user_id: str = Form(...), file: UploadFile = File(...)):
    # save to Supabase Storage
    content = await file.read()
    fname = f"resumes/{uuid.uuid4()}_{file.filename}"
    # upload to supabase storage (bucket 'resumes' must exist)
    res = supabase.storage.from_('resumes').upload(fname, io.BytesIO(content), content_type=file.content_type)
    if res.get('error'):
        raise HTTPException(status_code=500, detail=res['error'])
    # extract text (requires saving locally)
    local_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(local_path, "wb") as f:
        f.write(content)
    text, used_ocr = extract_text_from_pdf(local_path)
    # insert resume metadata
    r = supabase.table('resumes').insert({
        "user_id": user_id,
        "filename": file.filename,
        "storage_path": fname,
        "text_content": text,
        "is_ocr": used_ocr
    }).execute()
    return {"ok": True, "resume": r.data}

@app.post("/index-embeddings")
def index_embeddings(resume_ids: List[str]):
    # fetch resumes by ids, compute embeddings and store
    rows = supabase.table('resumes').select('id, text_content').in_('id', resume_ids).execute()
    items = rows.data
    texts = [it['text_content'] or "" for it in items]
    embeddings = get_embeddings(texts)
    # insert into resume_embeddings
    for i, it in enumerate(items):
        supabase.table('resume_embeddings').insert({
            "resume_id": it['id'],
            "embedding": embeddings[i]
        }).execute()
    return {"indexed": len(items)}

@app.post("/rank")
def rank(req: RankRequest):
    # 1) create ranking record
    r = supabase.table('rankings').insert({
        "job_title": req.job_title,
        "job_description": req.job_description,
        "created_by": req.created_by
    }).execute()
    ranking_id = r.data[0]['id']
    # 2) compute embedding for job description
    q_vec = get_embeddings([req.job_description])[0]
    # 3) fetch resume embeddings from DB
    rows = supabase.table('resume_embeddings').select('resume_id, embedding').execute()
    items = rows.data
    results = []
    for it in items:
        emb = np.array(it['embedding'], dtype=float)
        q = np.array(q_vec, dtype=float)
        # cosine similarity
        sim = float(np.dot(q, emb) / (np.linalg.norm(q) * np.linalg.norm(emb) + 1e-10))
        results.append((it['resume_id'], sim))
    # sort desc
    results.sort(key=lambda x: x[1], reverse=True)
    # store ranking_items and return top results with resume metadata
    out = []
    for resume_id, score in results:
        supabase.table('ranking_items').insert({
            "ranking_id": ranking_id,
            "resume_id": resume_id,
            "score": float(score)
        }).execute()
        # fetch resume metadata
        meta = supabase.table('resumes').select('id, filename, storage_path').eq('id', resume_id).single().execute().data
        out.append({"resume": meta, "score": float(score)})
    return {"ranking_id": ranking_id, "results": out}

@app.post("/shortlist")
def shortlist(ranking_id: str, resume_id: str, note: str = ""):
    # fetch resume metadata to get uploader / email
    resume = supabase.table('resumes').select('id, user_id, filename, text_content').eq('id', resume_id).single().execute().data
    # fetch profile to get email
    profile = supabase.table('profiles').select('email, full_name').eq('id', resume['user_id']).single().execute().data
    # send email
    job = supabase.table('rankings').select('job_title').eq('id', ranking_id).single().execute().data
    subject = job['job_title'] if job else "Shortlisted"
    message = f"You have been shortlisted for {subject}. Note: {note}"
    status, body, headers = send_shortlist_email(profile['email'], profile['full_name'], subject, message)
    return {"status": status}
