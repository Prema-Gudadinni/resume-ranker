import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

USE_MOCK = os.getenv("USE_MOCK_EMBEDDINGS", "false").lower() == "true"

# Load sentence-transformers model once (free + offline)
_model = None
if not USE_MOCK:
    _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    - If USE_MOCK_EMBEDDINGS=true → returns deterministic fake vectors for testing.
    - Else → uses SentenceTransformers (free local model).
    """
    if isinstance(texts, str):
        texts = [texts]

    if USE_MOCK:
        print("⚠️ MOCK MODE ACTIVE: Using fake embeddings.")
        vectors = []
        for t in texts:
            np.random.seed(abs(hash(t)) % (2**32))  # deterministic per text
            vectors.append(np.random.rand(384).tolist())  # MiniLM-L6 has 384 dims
        return vectors
    else:
        embeddings = _model.encode(texts, convert_to_numpy=True).tolist()
        return embeddings
