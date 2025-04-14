import os
from typing import Dict, List
import lyricsgenius
from dotenv import load_dotenv
import re
import html
import unicodedata
import string


load_dotenv()

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(
    GENIUS_ACCESS_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    timeout=10,
    retries=3
)

def clean_lyrics(raw: str) -> str:
    if not raw:
        return ""

    # Decode HTML entities like &amp;
    raw = html.unescape(raw)

    # Remove the first line if it's a "Read More" or "Contributors/Translations" line
    lines = raw.splitlines()
    if lines and ("Read More" in lines[0] or "Contributors" in lines[0] or "Translations" in lines[0]):
        lines = lines[1:]
    raw = " ".join(lines)  # Join with space instead of newline

    # Remove text in brackets like [Chorus], [Intro], etc.
    raw = re.sub(r'\[.*?\]', '', raw)

    # Remove weird invisible Unicode whitespace characters
    raw = re.sub(r'[\u2000-\u206F\u00A0\u2028\u2029\uFEFF]', ' ', raw)

    # Normalize unicode (e.g., é → e + ́ becomes é)
    raw = unicodedata.normalize('NFKD', raw)

    # Remove empty lines and join everything with spaces
    lines = raw.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Only keep non-empty lines
            cleaned_lines.append(line)

    # Join everything with spaces and collapse multiple spaces
    raw = " ".join(cleaned_lines)
    raw = re.sub(r'[ \t]{2,}', ' ', raw)

    return raw.strip()


def get_info(artist: str, songs: List[str]) -> Dict:
    """Fetch lyrics for a list of songs from Genius."""
    results = {
        "source": "genius",
        "artist": artist,
        "lyrics": {}
    }

    for song in songs[:5]:
        try:
            result = genius.search_song(title=song, artist=artist)
            if result and result.lyrics:
                cleaned = clean_lyrics(result.lyrics)
                results["lyrics"][song] = cleaned
            else:
                results["lyrics"][song] = "Lyrics not found."
        except Exception as e:
            results["lyrics"][song] = f"Error: {str(e)}"

    return results
