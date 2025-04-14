# utils/dataset_loader.py
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
