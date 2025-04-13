import { NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';

const uri = process.env.MONGODB_URI || '';
const client = new MongoClient(uri);

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const artistName = searchParams.get('name');

  if (!artistName) {
    return NextResponse.json({ error: 'Artist name is required' }, { status: 400 });
  }

  try {
    await client.connect();
    const database = client.db('artist_db');
    const collection = database.collection('artists');

    const artist = await collection.findOne({ 
      'spotify.name': { 
        $regex: `^${artistName}$`, 
        $options: 'i' 
      } 
    });

    if (!artist) {
      return NextResponse.json({ error: 'Artist not found' }, { status: 404 });
    }

    // Get top 3 albums
    const albums = artist.spotify.albums.slice(0, 3).map((album: any) => ({
      name: album.name,
      spotify_url: album.spotify_url,
      release_date: album.release_date,
    }));

    // Get top 5 tracks
    const songs = artist.spotify.tracks.slice(0, 5).map((track: any) => ({
      name: track.name,
      spotify_url: track.spotify_url,
    }));

    const response = {
      name: artist.spotify.name,
      spotify_url: artist.spotify.spotify_url,
      genres: artist.spotify.genres,
      followers: artist.spotify.followers,
      popularity: artist.spotify.popularity,
      image_url: artist.spotify.images?.[0]?.url || null,
      albums,
      songs,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching artist data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch artist data' },
      { status: 500 }
    );
  } finally {
    await client.close();
  }
}
