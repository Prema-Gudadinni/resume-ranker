# app/embeddings.py
import os
import openai
from typing import List
openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")  # recommended
# Create embedding vector for a list of texts
def get_embeddings(texts: List[str]) -> List[List[float]]:
    # OpenAI Python client: create embeddings
    resp = openai.Embedding.create(model=EMBED_MODEL, input=texts)
    # resp['data'] is a list, keep resp['data'][i]['embedding']
    return [d["embedding"] for d in resp["data"]]
