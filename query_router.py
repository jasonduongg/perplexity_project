# query_router.py

import spacy
import json

nlp = spacy.load("en_core_web_sm")

def detect_artist_from_query(query: str, known_artists: list[str]) -> str:
    query_lower = query.lower()
    for artist in known_artists:
        if artist.lower() in query_lower:
            return artist
    return detect_entity_as_fallback(query)

def detect_entity_as_fallback(query: str) -> str:
    doc = nlp(query)
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG"):
            return ent.text
    return ""

def get_current_artist_name() -> str:
    try:
        with open("data/current.txt") as f:
            data = json.load(f)
            return data.get("spotify", {}).get("name", "").lower()
    except Exception:
        return ""

def should_reload_artist(new_artist: str) -> bool:
    current_artist = get_current_artist_name()
    return new_artist.lower() not in current_artist
