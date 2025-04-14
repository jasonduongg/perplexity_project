# Perplexity Project

## Dependencies
- **OpenAI API**: Utilizes the OpenAI GPT-3.5-turbo model for generating responses and text-embedding-ada-002 for generating embeddings.
- **Python Libraries**:
  - **Main Libraries**:
    - `spotipy`: Spotify API integration
    - `wikipedia`: Wikipedia data retrieval
    - `lyricsgenius`: Genius lyrics access
  - **Supporting Libraries**: `openai`, `dotenv`, and other packages listed in `requirements.txt`.

## Local Development Setup

### Prerequisites
- Python 3.11
- API Keys for:
  - OpenAI
  - Spotify
  - Genius
  - MongoDB (for artist search caching)

### Running the Project Locally

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd perplexity_project
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in /backend:
   ```
   OPENAI_API_KEY=your_openai_key
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   GENIUS_ACCESS_TOKEN=your_genius_token
   MONGODB_URI=your_mongodb_connection_string
   ```

   Create a `.env.local` file in /frontend:
   ```
   NEXT_PUBLIC_AWS_BACKEND_IP=http://localhost:5000  # For local development
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DB=your_mongodb_db
   ```

5. **Run the backend server**
   ```bash
   cd backend
   python3 server.py
   ```

6. **Run the frontend development server**
   In a new terminal window:
   ```bash
   cd frontend
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:3000 (or the port specified by your frontend)
- Backend: http://localhost:5000 (or the port specified in server.py)

## Development
- **Containerization**: Docker is used to containerize the application, ensuring consistent development and deployment environments.
- **Virtual Environment**: Python virtual environment (venv) is used for local development to manage project dependencies and isolate the project's Python environment.
- **Data Sources**: 
  - Spotify API for music and artist information
  - Wikipedia for general knowledge and artist background
  - Genius for song lyrics and annotations

## Deployment
- **Frontend**: Hosted on Vercel (https://perplexity-project.vercel.app)
- **Backend**: Deployed on AWS EC2

## Other Features
- **Artist Search Caching**: Implements MongoDB for caching previously searched artists to improve response times and reduce API calls.
- **Chunk/Embedding Caching**: 
  - Implements a local caching system for text embeddings to optimize performance
  - Caches embeddings at the chunk level (Wikipedia sections, album info, lyrics, etc.)
  - Generates new embeddings only for modified or new content
  - Cache is stored in the `embeddings` directory with MD5-hashed filenames
  - Helps reduce API calls to OpenAI and improve response times

