from rag.rag_engine import add_chunk_to_database, retrieve_relevant_chunks
from rag.llm_engine import get_response
from data_provider.main import get_current_data
from typing import List, Dict


def load_dataset_from_dict(data: Dict) -> List[str]:
    chunks = []

    # Wikipedia summary and sections
    if "wikipedia" in data:
        wiki = data["wikipedia"]
        if summary := wiki.get("summary"):
            chunks.append(summary)
        for section in wiki.get("sections", []):
            if content := section.get("content"):
                chunks.append(content)

    # Spotify genres, top tracks, and albums
    if "spotify" in data:
        spotify = data["spotify"]
        if genres := spotify.get("genres"):
            chunks.append("Genres: " + ", ".join(genres))
        if tracks := spotify.get("top_track_names"):
            chunks.append("Top tracks: " + ", ".join(tracks))
        for album in spotify.get("albums", []):
            chunks.append(f"Album: {album['name']} ({album['release_date']})")

    # Genius lyrics
    if "genius" in data and "lyrics" in data["genius"]:
        for title, lyrics in data["genius"]["lyrics"].items():
            if lyrics and "Error" not in lyrics:
                snippet = lyrics[:1000]  # limit length if needed
                chunks.append(f"Lyrics for {title}:\n{snippet}")

    return [c.strip() for c in chunks if c.strip() and len(c.strip()) > 20]


# === MAIN ===

if __name__ == "__main__":
    # Step 1: Load and embed data
    data = get_current_data()
    dataset = load_dataset_from_dict(data)
    print(f'Loaded {len(dataset)} valid chunks.')

    for i, chunk in enumerate(dataset):
        try:
            add_chunk_to_database(chunk)
            print(f'Embedded chunk {i+1}/{len(dataset)}')
        except Exception as e:
            print(f"❌ Failed on chunk {i+1}: {e}")

    # Step 2: Chat loop
    print("\nAsk me anything about the artist (type 'exit' to quit):")
    while True:
        query = input("\n> ")
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        top_chunks = retrieve_relevant_chunks(query, top_n=3)

        print("\nRetrieved knowledge:")
        for chunk, sim in top_chunks:
            print(f" - (similarity: {sim:.2f}) {chunk[:100]}...")

        print("\nChatbot response:")
        stream = get_response(query, [chunk for chunk, _ in top_chunks])
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print()  # newline after response
