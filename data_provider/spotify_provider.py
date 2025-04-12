import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_artist_id(query: str):
    results = sp.search(q=query, limit=1, type='artist')
    artists = results.get('artists', {}).get('items', [])
    return artists[0] if artists else None

def get_all_albums(artist_id):
    albums = []
    seen = set()
    offset = 0

    while True:
        result = sp.artist_albums(artist_id, album_type='album,single', limit=50, offset=offset)
        items = result.get('items', [])
        if not items:
            break

        for album in items:
            name_key = album['name'].lower()
            if name_key not in seen:
                seen.add(name_key)
                albums.append(album)

        offset += len(items)
        if len(items) < 50:
            break

    return albums

def get_all_tracks(album_ids, limit=30):
    all_tracks = []
    seen_track_ids = set()

    for album_id in album_ids:
        tracks = sp.album_tracks(album_id)
        for track in tracks['items']:
            track_id = track['id']
            if track_id and track_id not in seen_track_ids:
                seen_track_ids.add(track_id)
                all_tracks.append(track_id)

    # Fetch full track metadata in batches to get popularity
    enriched_tracks = []
    for i in range(0, len(all_tracks), 50):
        batch_ids = all_tracks[i:i+50]
        batch_info = sp.tracks(batch_ids)['tracks']
        for track in batch_info:
            enriched_tracks.append({
                'name': track['name'],
                'id': track['id'],
                'duration_ms': track['duration_ms'],
                'explicit': track['explicit'],
                'track_number': track['track_number'],
                'popularity': track['popularity'],
                'preview_url': track['preview_url'],
                'spotify_url': track['external_urls']['spotify'],
                'album_name': track['album']['name']
            })

    # Sort by popularity descending and return top N
    enriched_tracks.sort(key=lambda t: t['popularity'], reverse=True)
    return enriched_tracks[:limit]

def get_info(query: str) -> dict:
    artist_search = get_artist_id(query)
    if not artist_search:
        return {"error": f"No artist found for query '{query}'"}

    artist_id = artist_search['id']
    artist = sp.artist(artist_id)  # ✅ Full metadata with genres, followers, etc.

    albums = get_all_albums(artist_id)
    album_ids = [album['id'] for album in albums]
    tracks = get_all_tracks(album_ids)

    return {
        "source": "spotify",
        "query": query,
        "type": "artist",
        "id": artist_id,
        "name": artist.get('name'),
        "genres": artist.get('genres', []),
        "followers": artist.get('followers', {}).get('total'),
        "popularity": artist.get('popularity'),
        "spotify_url": artist.get('external_urls', {}).get('spotify'),
        "images": artist.get('images', []),
        "albums": [
            {
                "name": album['name'],
                "release_date": album['release_date'],
                "total_tracks": album['total_tracks'],
                "spotify_url": album['external_urls']['spotify']
            } for album in albums
        ],
        "top_track_names": [track["name"] for track in tracks],
        "tracks": tracks
    }
