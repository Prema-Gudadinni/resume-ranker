import os
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI.
    Returns a list of vectors.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]
