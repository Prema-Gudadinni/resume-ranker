from fastapi import FastAPI
from supabase_client import supabase  # centralized client

app = FastAPI()

@app.get("/resumes")  # GET method at /resumes
def get_resumes():
    try:
        response = supabase.table("resumes").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        return {"error": str(e)}
