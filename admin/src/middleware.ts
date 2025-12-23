import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const allowedOrigins = [
  'https://75b0aa88-92c4-4424-ab49-9d1664b48129-00-1g9yoro9o3zfq.sisko.replit.dev',
  'http://localhost:5000',
  'http://127.0.0.1:5000',
]

export function middleware(request: NextRequest) {
  const origin = request.headers.get('origin') || ''
  const isAllowed = allowedOrigins.some(o => origin.includes(o.replace(/https?:\/\//, '')))
  
  if (request.method === 'OPTIONS') {
    return new NextResponse(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': origin || '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true',
      },
    })
  }

  const response = NextResponse.next()
  
  if (origin) {
    response.headers.set('Access-Control-Allow-Origin', origin)
    response.headers.set('Access-Control-Allow-Credentials', 'true')
  }
  
  return response
}

export const config = {
  matcher: '/api/:path*',
}
