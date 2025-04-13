from rag.rag_engine import add_chunk_to_database, retrieve_relevant_chunks
from rag.llm_engine import get_response
from data_provider.main import get_current_data, compile_all, save_to_file
from utils.name_detection import detect_artist_from_query
from typing import List, Dict

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
        print(f"Loaded {len(dataset)} valid chunks.")

        for i, chunk in enumerate(dataset):
            try:
                add_chunk_to_database(chunk)
                print(f'Embedded chunk {i+1}/{len(dataset)}')
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
