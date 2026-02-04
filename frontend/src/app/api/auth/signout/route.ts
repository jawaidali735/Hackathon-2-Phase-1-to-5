import { auth } from '@/lib/auth';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Sign out the user
    await auth.api.signOut({
      headers: Object.fromEntries(request.headers.entries()),
    });

    // Return a response that redirects to the homepage
    return Response.redirect(new URL('/', request.url), 302);
  } catch (error) {
    console.error('Sign out error:', error);
    return Response.json({ error: 'Failed to sign out' }, { status: 500 });
  }
}