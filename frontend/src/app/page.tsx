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
  const [searchQuery, setSearchQuery] = useState('');

  const filteredArtists = artists.filter(artist => 
    artist.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
    setInput(`who is ${artistName}`);
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
          try {
            // Try to parse the error message if it's a JSON string
            const parsedError = JSON.parse(errorData.error);
            setError(parsedError.error);
          } catch {
            // If parsing fails, use the error message as is
            setError(errorData.error);
          }
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
    <div className="flex h-screen w-screen bg-gray-800 overflow-x-hidden">
      {/* Artists Sidebar */}
      <div className={`bg-gray-900 text-white transition-all duration-500 ease-in-out ${isNavOpen ? 'w-64' : 'w-24 overflow-hidden'} h-screen flex flex-col`}>
        <div className="p-4">
          {isNavOpen && (
            <div className="flex items-start justify-between">
              <div className="w-full">
                <div className="flex items-center justify-between w-full mb-4">
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
                <p className="text-sm text-gray-400 mb-4">Searching these artists will result in faster response times</p>
                <div className="relative mb-4">
                  <input
                    type="text"
                    placeholder="Search artists..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full p-2 pl-10 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <svg
                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
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
        <div className="overflow-y-auto flex-1">
          {filteredArtists.map((artist, index) => (
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
        <div className="flex-1 overflow-y-auto">
          {/* Backend Status Indicator */}
          <div className="sticky top-0 z-10 flex justify-between items-center gap-2 p-4 bg-black">
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white">A Musician Expert Bot</h1>
              <div className="flex items-center gap-2 ml-4 bg-gray-800 px-3 py-1 rounded-lg">
                <div className={`w-3 h-3 rounded-full ${backendStatus === 'Connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-400">{backendStatus === 'Connected' ? 'online' : 'offline'}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!isRightNavOpen && (
                <button
                  onClick={() => setIsRightNavOpen(!isRightNavOpen)}
                  className="p-2 rounded-lg hover:bg-gray-600 bg-gray-900 text-white flex items-center gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  <span>Artist Details</span>
                </button>
              )}
            </div>
          </div>

          <div className="px-8 pt-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg max-w-[80%] mb-4 ${
                  message.role === 'user'
                    ? 'bg-gray-700 ml-auto text-white'
                    : 'bg-gray-900 mr-auto text-white'
                }`}
              >
                {message.content}
              </div>
            ))}
            {isLoading && (
              <div className="p-4 rounded-lg max-w-[80%] mb-4 bg-gray-800 mr-auto text-white">
                Loading...
              </div>
            )}
            {error && (
              <div className="p-4 rounded-lg max-w-[80%] mb-4 bg-red-100 text-red-700 mr-auto text-white">
                {error}
              </div>
            )}
          </div>
        </div>

        <form onSubmit={handleQuestionSubmit} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your question..."
              className="flex-1 p-2 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700 bg-gray-700 text-white placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="p-3 bg-green-600 text-white rounded-full hover:bg-green-700 focus:ring-2 focus:ring-green-700 focus:outline-none disabled:bg-gray-400"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
      </div>

      {/* Right Sidebar */}
      <div className={`bg-gray-900 text-white transition-all duration-500 ease-in-out ${isRightNavOpen ? 'w-64' : 'w-0 overflow-hidden'} h-screen flex flex-col`}>
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
                  <h4 className="font-semibold mb-2">Genres</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedArtist.genres.map((genre: string, index: number) => (
                      <div
                        key={index}
                        className="px-2 py-1 bg-gray-800 rounded-full text-xs text-gray-300 hover:bg-gray-700 hover:shadow-[0_0_15px_rgba(34,197,94,0.5)] transition-all duration-200"
                      >
                        {genre.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="mb-4">
                  <h4 className="font-semibold mb-1">Statistics</h4>
                  <p className="text-sm text-gray-300">Followers: {selectedArtist.followers.toLocaleString()}</p>
                  <p className="text-sm text-gray-300">Popularity: {selectedArtist.popularity}/100</p>
                </div>
                <div className="mb-4">
                  <h4 className="font-semibold mb-2">Top Albums</h4>
                  <div className="grid grid-cols-1 gap-2">
                    {selectedArtist.albums.map((album: any, index: number) => (
                      <a
                        key={index}
                        href={album.spotify_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-gray-800 rounded-lg hover:bg-gray-700 hover:shadow-[0_0_15px_rgba(34,197,94,0.5)] transition-all duration-200"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 min-w-0">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-sm font-medium truncate">{album.name}</span>
                          </div>
                          <span className="text-xs text-gray-400 flex-shrink-0">{album.release_date}</span>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Top Songs</h4>
                  <div className="grid grid-cols-1 gap-2">
                    {selectedArtist.songs.map((song: any, index: number) => (
                      <a
                        key={index}
                        href={song.spotify_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-gray-800 rounded-lg hover:bg-gray-700 hover:shadow-[0_0_15px_rgba(34,197,94,0.5)] transition-all duration-200"
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-sm font-medium truncate">{song.name}</span>
                        </div>
                      </a>
                    ))}
                  </div>
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
