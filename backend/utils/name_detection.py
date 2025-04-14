import spacy
import json
from difflib import SequenceMatcher
from pathlib import Path
from data_provider.main import get_current_data

nlp = spacy.load("en_core_web_sm")

# Load known artists
ARTIST_DB = json.loads(Path("data/artists.json").read_text())

def extract_entities(text: str):
    # First try spaCy NER
    doc = nlp(text)
    entities = [ent.text.lower() for ent in doc.ents if ent.label_ in {"PERSON", "ORG", "WORK_OF_ART"}]
    
    # If no entities found, try splitting the text into words
    if not entities:
        words = text.lower().split()
        # If it's a single word, use it directly
        if len(words) == 1:
            entities = words
        # If multiple words, try combinations
        else:
            entities = [text.lower()]  # Use full text
            entities.extend(words)  # Add individual words
    
    return entities

def is_similar(a: str, b: str, threshold: float = 0.8) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold

def detect_artist_from_query(query: str) -> str:
    # Check for pronouns that should use current artist
    pronouns = {"he", "she", "his", "her", "they", "them", "their"}
    if any(pronoun in query.lower().split() for pronoun in pronouns):
        try:
            current_data = get_current_data()
            return current_data.get("spotify", {}).get("name", "")
        except Exception:
            return ""
    
    candidates = extract_entities(query)
    
    # First try exact matches
    for candidate in candidates:
        for artist in ARTIST_DB:
            all_names = [artist["name"].lower()] + [alias.lower() for alias in artist.get("aliases", [])]
            if candidate in all_names:
                return artist["name"]
    
    # If no exact match, try similarity matching
    for candidate in candidates:
        for artist in ARTIST_DB:
            all_names = [artist["name"].lower()] + [alias.lower() for alias in artist.get("aliases", [])]
            for name in all_names:
                if is_similar(candidate, name):
                    return artist["name"]
    
    return ""
