import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_MOCK = os.getenv("USE_MOCK_EMBEDDINGS", "false").lower() == "true"

client = None
if not USE_MOCK:
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY is not set in .env")
    client = OpenAI(api_key=OPENAI_API_KEY)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    If USE_MOCK_EMBEDDINGS=true, returns deterministic fake vectors for testing.
    """
    if USE_MOCK:
        print("⚠️ MOCK MODE ACTIVE: Using fake embeddings.")
        vectors = []
        for t in texts:
            np.random.seed(abs(hash(t)) % (2**32))  # deterministic per text
            vectors.append(np.random.rand(1536).tolist())
        return vectors
    else:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
