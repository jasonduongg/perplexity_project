from ollama import Client

EMBEDDING_MODEL = 'nomic-embed-text'
VECTOR_DB = []

#replys

# ✅ Initialize Ollama client with explicit base URL
client = Client(host='http://localhost:11434')

def load_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

def embed_text(text):
    response = client.embed(model=EMBEDDING_MODEL, input=text)
    return response['embeddings'][0]

def add_chunk_to_database(chunk):
    embedding = embed_text(chunk)
    VECTOR_DB.append((chunk, embedding))

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b)

def retrieve_relevant_chunks(query, top_n=3):
    query_embedding = embed_text(query)
    ranked = sorted(
        [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB],
        key=lambda x: x[1], reverse=True
    )
    return ranked[:top_n]
