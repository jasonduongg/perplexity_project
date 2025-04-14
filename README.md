# Perplexity Project

## Dependencies
- **OpenAI API**: Utilizes the OpenAI GPT-3.5-turbo model for generating responses and text-embedding-ada-002 for generating embeddings.
- **Python Libraries**:
  - **Main Libraries**:
    - `spotipy`: Spotify API integration
    - `wikipedia`: Wikipedia data retrieval
    - `lyricsgenius`: Genius lyrics access
  - **Supporting Libraries**: `openai`, `dotenv`, and other packages listed in `requirements.txt`.

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

