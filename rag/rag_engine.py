from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Tuple

# Load .env and initialize client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_DB: List[Tuple[str, List[float]]] = []

def embed_text(text: str) -> List[float]:
    response = client.embeddings.create(
        input=[text],  # must be a list
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def add_chunk_to_database(chunk: str):
    embedding = embed_text(chunk)
    VECTOR_DB.append((chunk, embedding))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b)

def retrieve_relevant_chunks(query: str, top_n: int = 3) -> List[Tuple[str, float]]:
    query_embedding = embed_text(query)
    ranked = sorted(
        [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB],
        key=lambda x: x[1],
        reverse=True
    )
    return ranked[:top_n]
