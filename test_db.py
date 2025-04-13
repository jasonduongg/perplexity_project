from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')

def test_connection():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        
        # Test the connection
        print("Testing MongoDB connection...")
        print("Server info:", client.server_info())
        
        # Get the database
        db = client['artist_db']
        print("\nConnected to database:", db.name)
        
        # Get the collection
        collection = db['artists']
        print("Using collection:", collection.name)
        
        # Test data
        test_artist = {
            "query": "Test Artist",
            "spotify": {
                "name": "Test Artist",
                "genres": ["pop", "rock"],
                "followers": 1000,
                "popularity": 50
            },
            "wikipedia": {
                "summary": "This is a test artist",
                "url": "https://example.com"
            }
        }
        
        # Test inserting data
        print("\nInserting test data...")
        result = collection.insert_one(test_artist)
        print("Inserted document ID:", result.inserted_id)
        
        # Test retrieving data
        print("\nRetrieving test data...")
        retrieved_data = collection.find_one({"spotify.name": "Test Artist"})
        if retrieved_data:
            print("Data retrieved successfully!")
            print("Artist name:", retrieved_data["spotify"]["name"])
            print("Genres:", retrieved_data["spotify"]["genres"])
        else:
            print("Failed to retrieve data!")
        
        # Clean up test data
        print("\nCleaning up test data...")
        collection.delete_one({"spotify.name": "Test Artist"})
        print("Test data removed")
        
        # Close the connection
        client.close()
        print("\nConnection closed successfully!")
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_connection()