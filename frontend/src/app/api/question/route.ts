import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_AWS_BACKEND_IP;
    console.log('Backend URL:', backendUrl);
    
    if (!backendUrl) {
      throw new Error('AWS_API_URL is not configured');
    }

    const body = await request.json();
    console.log('Request body:', body);
    
    const response = await fetch(`${backendUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: body.question,
      }),
    });

    console.log('Response status:', response.status);
    console.log('Response status text:', response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      return NextResponse.json(
        { error: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Response data:', data);
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Detailed error in question route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}
