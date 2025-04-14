import json
import os
from typing import Dict
from datetime import datetime, timedelta

from .spotify_provider import get_info as get_spotify_info
from .wikipedia_provider import get_info as get_wikipedia_info
from .genius_provider import get_info as get_genius_info
# from .lastfm_provider import get_info as get_lastfm_info
from data.db import save_artist_data, get_artist_data

def is_data_fresh(data: Dict) -> bool:
    """Check if the data is less than 24 hours old"""
    if not data or 'last_updated' not in data:
        return False
    
    last_updated = datetime.fromisoformat(data['last_updated'])
    return datetime.now() - last_updated < timedelta(hours=24)

def save_to_file(data: dict, path: str = "data/current.txt"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_current_data(artist_name: str) -> Dict:
    """Get current artist data from MongoDB or fetch new data if needed"""
    # Try to get existing data from MongoDB
    data = get_artist_data(artist_name)
    
    # If we have fresh data, return it
    if data and is_data_fresh(data):
        print(f"✅ Using cached data for: {artist_name}")
        return data
    
    # If no data or data is stale, fetch new data
    print(f"🔍 Fetching new data for: {artist_name}")
    new_data = compile_all(artist_name)
    save_artist_data(new_data)
    return new_data

def compile_all(query: str) -> Dict:
    """Compile data from all sources"""
    spotify_data = get_spotify_info(query)
    wikipedia_data = get_wikipedia_info(query)
    
    # Get top track names from Spotify data to use for Genius
    top_tracks = spotify_data.get("top_track_names", [])[:5]  # Get top 5 tracks
    genius_data = get_genius_info(query, songs=top_tracks)
    
    return {
        "query": query,
        "spotify": spotify_data,
        "wikipedia": wikipedia_data,
        "genius": genius_data,
        "last_updated": datetime.now().isoformat()
    }

def run(query: str):
    """Main function to process a query"""
    compiled = compile_all(query)
    save_artist_data(compiled)
    print(f"Saved data for '{query}' to MongoDB")

def query_provider(query: str) -> dict:
    compiled = compile_all(query)
    save_to_file(compiled)
    return compiled

# Optional CLI entry point
if __name__ == "__main__":
    query = input("Enter an artist or topic: ")
    run(query)
