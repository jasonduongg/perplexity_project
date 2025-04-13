'use client';

import { useState, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Artist {
  name: string;
  imageUrl: string | null;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isNavOpen, setIsNavOpen] = useState(true);
  const [isRightNavOpen, setIsRightNavOpen] = useState(true);
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');
  const [isLoading, setIsLoading] = useState(false);
  const [isRightSidebarLoading, setIsRightSidebarLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [selectedArtist, setSelectedArtist] = useState<any>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/ping', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          setBackendStatus('Connected');
        } else {
          setBackendStatus('Disconnected');
        }
      } catch (error) {
        setBackendStatus('Disconnected');
      }
    };
    checkBackend();
  }, []);

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        const response = await fetch('/api/artistdb', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          const data = await response.json();
          setArtists(data.data);
        }
      } catch (error) {
        console.error('Error fetching artists:', error);
      }
    };
    fetchArtists();
  }, []);

  const fetchArtistData = async (artistName: string) => {
    setError(null);
    setIsRightSidebarLoading(true);
    try {
      console.log(`Fetching data for artist: ${artistName}`);
      // First, get the exact artist name from the database
      const artistResponse = await fetch('/api/artistdb');
      if (!artistResponse.ok) {
        throw new Error('Failed to fetch artist list');
      }
      const artistData = await artistResponse.json();
      const exactArtist = artistData.data.find((a: Artist) => 
        a.name.toLowerCase() === artistName.toLowerCase()
      );
      
      if (!exactArtist) {
        throw new Error(`Artist "${artistName}" not found in database`);
      }

      // Now fetch the detailed data using the exact name
      const response = await fetch(`/api/artistdb/brief?name=${encodeURIComponent(exactArtist.name)}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch artist data');
      }
      const data = await response.json();
      console.log('Received artist data:', data);
      
      if (!data || !data.name) {
        throw new Error('No artist data found');
      }
      
      // Update the selected artist data
      setSelectedArtist(data);
      
      // Refresh the artist list to include any new artists
      const updatedArtistResponse = await fetch('/api/artistdb');
      if (updatedArtistResponse.ok) {
        const updatedData = await updatedArtistResponse.json();
        setArtists(updatedData.data);
      }
      
    } catch (err) {
      console.error('Error fetching artist data:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while fetching artist data');
    } finally {
      setIsRightSidebarLoading(false);
    }
  };

  const handleQuestionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages([...messages, newMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input.trim() }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer
        }]);
        
        // Refresh the artist list after receiving a response
        const artistResponse = await fetch('/api/artistdb');
        if (artistResponse.ok) {
          const artistData = await artistResponse.json();
          setArtists(artistData.data);
        }
      } else {
        const errorData = await response.json();
        console.log('Error data:', errorData);
        if (errorData.error) {
          setError(errorData.error);
        } else {
          setError('Failed to get response from server');
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-gray-800">
      {/* Artists Sidebar */}
      <div className={`bg-gray-900 text-white transition-all duration-300 ${isNavOpen ? 'w-64' : 'w-auto'}`}>
        <div className="p-4">
          {isNavOpen && (
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center justify-between w-full">
                  <span className="text-xl font-bold">Cached Artists</span>
                  <button
                    onClick={() => setIsNavOpen(!isNavOpen)}
                    className="p-1 rounded-lg hover:bg-gray-600"
                  >
                    {isNavOpen ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                      </svg>
                    )}
                  </button>
                </div>
                <p className="text-sm text-gray-400 mt-1">Searching these artists will result in faster response times</p>
              </div>
            </div>
          )}
          {!isNavOpen && (
            <div className="flex justify-center mb-2">
              <button
                onClick={() => setIsNavOpen(!isNavOpen)}
                className="p-2 rounded-lg hover:bg-gray-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          )}
        </div>
        <div className="overflow-y-auto h-[calc(100vh-8rem)]">
          {artists.map((artist, index) => (
            <div
              key={index}
              className="flex items-center p-4 bg-gray-800 hover:bg-gray-600 cursor-pointer rounded-lg shadow-md hover:shadow-[0_0_15px_rgba(34,197,94,0.5)] transition-all duration-200 mx-4 my-2"
              onClick={() => fetchArtistData(artist.name)}
            >
              {artist.imageUrl ? (
                <img
                  src={artist.imageUrl}
                  alt={artist.name}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center">
                  <span className="text-lg font-bold">{artist.name.charAt(0)}</span>
                </div>
              )}
              {isNavOpen && <span className="ml-3">{artist.name}</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-gray-800">
        <div className="flex-1 overflow-y-auto p-4">
          {/* Backend Status Indicator */}
          <div className="flex justify-end items-center gap-2 mb-4">
            <div className="bg-white px-3 py-1 rounded-lg shadow-lg text-sm">
              <span className="font-semibold">Backend Status: </span>
              <span className={backendStatus === 'Connected' ? 'text-green-500' : 'text-red-500'}>
                {backendStatus}
              </span>
            </div>
            {!isRightNavOpen && (
              <button
                onClick={() => setIsRightNavOpen(!isRightNavOpen)}
                className="p-2 rounded-lg hover:bg-gray-600 bg-gray-900 text-white"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {messages.map((message, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg max-w-[80%] mb-4 ${
                message.role === 'user'
                  ? 'bg-white ml-auto'
                  : 'bg-white mr-auto'
              }`}
            >
              {message.content}
            </div>
          ))}
          {isLoading && (
            <div className="p-4 rounded-lg max-w-[80%] mb-4 bg-white mr-auto">
              Loading...
            </div>
          )}
          {error && (
            <div className="p-4 rounded-lg max-w-[80%] mb-4 bg-red-100 text-red-700 mr-auto">
              {error}
            </div>
          )}
        </div>

        <form onSubmit={handleQuestionSubmit} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question..."
              className="flex-1 p-2 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-700 text-white placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {/* Right Sidebar */}
      <div className={`bg-gray-900 text-white transition-all duration-300 ${isRightNavOpen ? 'w-64' : 'w-0'}`}>
        <div className="p-4">
          {isRightNavOpen && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsRightNavOpen(!isRightNavOpen)}
                className="p-1 rounded-lg hover:bg-gray-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <span className="text-xl font-bold">Artist Details</span>
            </div>
          )}
        </div>
        {isRightNavOpen && (
          <div className="overflow-y-auto h-[calc(100vh-8rem)]">
            {isRightSidebarLoading ? (
              <div className="p-4 text-center">Loading artist data...</div>
            ) : error ? (
              <div className="p-4 text-red-500">{error}</div>
            ) : selectedArtist ? (
              <div className="p-4">
                <div className="mb-4">
                  <div className="flex items-center gap-4">
                    {selectedArtist.image_url && (
                      <img 
                        src={selectedArtist.image_url} 
                        alt={selectedArtist.name}
                        className="w-16 h-16 rounded-full object-cover border-2 border-gray-700"
                      />
                    )}
                    <div>
                      <h3 className="text-lg font-semibold">{selectedArtist.name}</h3>
                      <a href={selectedArtist.spotify_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-sm">
                        View on Spotify
                      </a>
                    </div>
                  </div>
                </div>
                <div className="mb-4">
                  <h4 className="font-semibold mb-1">Genres</h4>
                  <p className="text-sm text-gray-300">{selectedArtist.genres.join(', ')}</p>
                </div>
                <div className="mb-4">
                  <h4 className="font-semibold mb-1">Statistics</h4>
                  <p className="text-sm text-gray-300">Followers: {selectedArtist.followers.toLocaleString()}</p>
                  <p className="text-sm text-gray-300">Popularity: {selectedArtist.popularity}/100</p>
                </div>
                <div className="mb-4">
                  <h4 className="font-semibold mb-1">Top Albums</h4>
                  <ul className="list-disc list-inside text-sm text-gray-300">
                    {selectedArtist.albums.map((album: any, index: number) => (
                      <li key={index}>
                        <a href={album.spotify_url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-400">
                          {album.name}
                        </a>
                        <span className="text-gray-500 ml-2">({album.release_date})</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Top Songs</h4>
                  <ul className="list-disc list-inside text-sm text-gray-300">
                    {selectedArtist.songs.map((song: any, index: number) => (
                      <li key={index}>
                        <a href={song.spotify_url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-400">
                          {song.name}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-400">
                Select an artist to view details
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
