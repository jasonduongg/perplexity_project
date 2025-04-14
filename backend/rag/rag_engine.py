from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Tuple
import numpy as np
import faiss

# Load .env and initialize client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"

class VectorDB:
    def __init__(self, dimension=1536):  # OpenAI embeddings are 1536-dimensional
        self.chunks = []
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # Using L2 distance

    def add_chunk(self, chunk: str, embedding: List[float]):
        self.chunks.append(chunk)
        embedding_array = np.array(embedding, dtype=np.float32).reshape(1, -1)
        self.index.add(embedding_array)

    def get_all_chunks(self) -> List[str]:
        return self.chunks

    def clear(self):
        self.chunks.clear()
        self.index = faiss.IndexFlatL2(self.dimension)

    def search(self, query_embedding: List[float], k: int = 3) -> List[Tuple[str, float]]:
        query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):  # Ensure index is valid
                chunk = self.chunks[idx]
                # Convert L2 distance to similarity score (higher is better)
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((chunk, similarity))
        
        return results

vector_db = VectorDB()

def embed_text(text: str) -> List[float]:
    response = client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def add_chunk_to_database(chunk: str):
    embedding = embed_text(chunk)
    vector_db.add_chunk(chunk, embedding)

def retrieve_relevant_chunks(query: str, top_n: int = 3) -> List[Tuple[str, float]]:
    query_embedding = embed_text(query)
    return vector_db.search(query_embedding, k=top_n)
