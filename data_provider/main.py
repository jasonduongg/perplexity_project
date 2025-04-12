import json
import os

from .spotify_provider import get_info as get_spotify_info
from .wikipedia_provider import get_info as get_wikipedia_info
from .genius_provider import get_info as get_genius_info
# from .lastfm_provider import get_info as get_lastfm_info

def save_to_file(data: dict, path: str = "data/current.txt"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_current_data(path: str = "data/current.txt") -> dict:
    with open(path, "r") as f:
        return json.load(f)

def compile_all(query: str) -> dict:
    spotify_data = get_spotify_info(query)
    artist_name = spotify_data.get("name", query)
    
    wikipedia_data = get_wikipedia_info(query, override_query=artist_name)
    genius_lyrics = get_genius_info(artist_name, spotify_data["top_track_names"])

    result = {
        "query": query,
        "spotify": spotify_data,
        "wikipedia": wikipedia_data,
        "genius": genius_lyrics,
        # "lastfm": get_lastfm_info(query),
    }
    return result

def run(query: str):
    compiled = compile_all(query)
    save_to_file(compiled)
    print(f"Saved data for '{query}' to data/current.txt")

def query_provider(query: str) -> dict:
    compiled = compile_all(query)
    save_to_file(compiled)
    return compiled

# Optional CLI entry point
if __name__ == "__main__":
    query = input("Enter an artist or topic: ")
    run(query)
