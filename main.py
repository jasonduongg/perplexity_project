import os
import time
import hashlib
import json
from pathlib import Path
from typing import List, Dict

import psutil

from rag.rag_engine import add_chunk_to_database, retrieve_relevant_chunks
from rag.llm_engine import get_response
from data_provider.main import get_current_data, compile_all, save_to_file
from utils.name_detection import detect_artist_from_query

# === CONFIG ===
MAX_CHUNKS = 40
ENABLE_MEMORY_CHECK = True
MEMORY_THRESHOLD_MB = 400
EMBEDDING_CACHE_DIR = Path("embeddings")
EMBEDDING_CACHE_DIR.mkdir(exist_ok=True)

# === UTILS ===

def get_chunk_hash(chunk: str) -> str:
    return hashlib.md5(chunk.encode()).hexdigest()

def is_cached(chunk_hash: str) -> bool:
    return (EMBEDDING_CACHE_DIR / f"{chunk_hash}.json").exists()

def save_embedding(chunk_hash: str, vector: dict):
    with open(EMBEDDING_CACHE_DIR / f"{chunk_hash}.json", "w") as f:
        json.dump(vector, f)

def has_enough_memory(threshold_mb=MEMORY_THRESHOLD_MB) -> bool:
    return psutil.virtual_memory().available > threshold_mb * 1024 * 1024

def load_dataset_from_dict(data: Dict) -> List[str]:
    chunks = []

    if "wikipedia" in data:
        wiki = data["wikipedia"]
        if summary := wiki.get("summary"):
            chunks.append(summary)
        for section in wiki.get("sections", []):
            if content := section.get("content"):
                chunks.append(content)

    if "spotify" in data:
        spotify = data["spotify"]
        if genres := spotify.get("genres"):
            chunks.append("Genres: " + ", ".join(genres))
        if tracks := spotify.get("top_track_names"):
            chunks.append("Top tracks: " + ", ".join(tracks))
        for album in spotify.get("albums", []):
            chunks.append(f"Album: {album['name']} ({album['release_date']})")

    if "genius" in data and "lyrics" in data["genius"]:
        for title, lyrics in data["genius"]["lyrics"].items():
            if lyrics and "Error" not in lyrics:
                snippet = lyrics[:1000]
                chunks.append(f"Lyrics for {title}:\n{snippet}")

    return [c.strip() for c in chunks if c.strip() and len(c.strip()) > 20]

# === MAIN ===

if __name__ == "__main__":
    print("Ask me anything about an artist (type 'exit' to quit):")

    while True:
        query = input("\n> ")
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        artist_name = detect_artist_from_query(query)
        if not artist_name:
            print("❌ Could not detect an artist name in your query.")
            continue

        try:
            current_data = get_current_data()
            current_artist = current_data.get("spotify", {}).get("name", "")
            if current_artist.lower() != artist_name.lower():
                print(f"🔍 Fetching new data for: {artist_name}")
                new_data = compile_all(artist_name)
                save_to_file(new_data)
                data = new_data
            else:
                print(f"✅ Using existing data for: {artist_name}")
                data = current_data
        except Exception as e:
            print(f"❌ Error accessing current data: {e}")
            print(f"🔍 Fetching new data for: {artist_name}")
            new_data = compile_all(artist_name)
            save_to_file(new_data)
            data = new_data

        dataset = load_dataset_from_dict(data)
        print(f"Loaded {len(dataset)} valid chunks. Embedding max {MAX_CHUNKS}...")

        for i, chunk in enumerate(dataset[:MAX_CHUNKS]):
            chunk_hash = get_chunk_hash(chunk)
            if is_cached(chunk_hash):
                print(f"✅ Skipping cached chunk {i+1}")
                continue

            if ENABLE_MEMORY_CHECK and not has_enough_memory():
                print(f"⚠️ Skipping chunk {i+1} due to low memory.")
                continue

            try:
                start = time.time()
                add_chunk_to_database(chunk)
                duration = time.time() - start
                save_embedding(chunk_hash, {"cached": True})
                print(f"✅ Embedded chunk {i+1}/{MAX_CHUNKS} in {duration:.2f}s")
            except Exception as e:
                print(f"❌ Failed on chunk {i+1}: {e}")

        top_chunks = retrieve_relevant_chunks(query, top_n=3)

        print("\nRetrieved knowledge:")
        for chunk, sim in top_chunks:
            print(f" - (similarity: {sim:.2f}) {chunk[:100]}...")

        print("\nChatbot response:")
        stream = get_response(query, [chunk for chunk, _ in top_chunks])
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print()
