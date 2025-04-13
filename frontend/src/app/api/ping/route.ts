import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_AWS_BACKEND_IP;
    console.log('Backend URL:', backendUrl);
    
    if (!backendUrl) {
      throw new Error('AWS_API_URL is not configured');
    }

    // Remove trailing slash if present and append /ping
    const pingUrl = `${backendUrl.replace(/\/$/, '')}/ping`;
    console.log('Ping URL:', pingUrl);

    const response = await fetch(pingUrl);
    
    if (!response.ok) {
      throw new Error('Failed to connect to backend');
    }

    // Get the text response instead of trying to parse as JSON
    const text = await response.text();
    console.log('Ping response:', text);

    // Return a JSON response with the text
    return NextResponse.json({ status: 'ok', message: text });
    
  } catch (error) {
    console.error('Error in ping route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to connect to backend' },
      { status: 500 }
    );
  }
} 