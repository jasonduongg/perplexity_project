// pages/api/test.js
import { NextResponse } from 'next/server'
import { MongoClient } from 'mongodb'
import clientPromise from '@/app/lib/mongodb'

export async function GET() {
  try {
    console.log('Connecting to MongoDB...')
    const client: MongoClient = await clientPromise
    console.log('Connected to MongoDB')
    
    const db = client.db('artist_db')
    const collection = db.collection('artists')
    
    console.log('Fetching artist names and images...')
    const data = await collection.find({}, { 
      projection: { 
        'spotify.name': 1, 
        'spotify.images': 1, 
        _id: 0 
      } 
    }).toArray()
    
    const artists = data.map(doc => ({
      name: doc.spotify.name,
      imageUrl: doc.spotify.images?.[0]?.url || null // Get the first (largest) image URL
    }))
    
    console.log('Found artists:', artists.length)
    
    return NextResponse.json({ data: artists }, { status: 200 })
  } catch (error) {
    console.error('Error in GET /api/artistdb:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch artists',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const client: MongoClient = await clientPromise
    const db = client.db('artist_db')
    
    const collection = db.collection('artists')
    const result = await collection.insertOne(body)
    
    return NextResponse.json(
      { success: true, insertedId: result.insertedId },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error creating artist:', error)
    return NextResponse.json(
      { error: 'Failed to create artist' },
      { status: 500 }
    )
  }
}
