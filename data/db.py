from pymongo import MongoClient
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)
db = client['artist_db']
collection = db['artists']

def save_artist_data(data: Dict) -> None:
    """Save artist data to MongoDB"""
    # Use the artist name as the unique identifier
    artist_name = data.get("spotify", {}).get("name", "").lower()
    if artist_name:
        # Add or update last_updated timestamp
        data['last_updated'] = datetime.now().isoformat()
        
        # Update or insert the document
        collection.update_one(
            {"spotify.name": {"$regex": f"^{artist_name}$", "$options": "i"}},
            {"$set": data},
            upsert=True
        )

def get_artist_data(artist_name: str) -> Optional[Dict]:
    """Get artist data from MongoDB"""
    # Convert both the search term and stored name to lowercase for case-insensitive matching
    return collection.find_one({"spotify.name": {"$regex": f"^{artist_name}$", "$options": "i"}})