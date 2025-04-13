export async function getArtistId(artistName: string) {
  try {
    const response = await fetch(
      `https://api.spotify.com/v1/search?q=${encodeURIComponent(artistName)}&type=artist&limit=1`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.SPOTIFY_ACCESS_TOKEN}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch artist');
    }

    const data = await response.json();
    const artist = data.artists.items[0];
    return artist;
  } catch (error) {
    console.error('Error fetching artist:', error);
    return null;
  }
} 