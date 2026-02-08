import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Validate session via BetterAuth API
  let session = null;
  try {
    const response = await fetch(new URL("/api/auth/get-session", request.url), {
      headers: {
        cookie: request.headers.get("cookie") || ""
      }
    });
    if (response.ok) {
      session = await response.json();
    }
  } catch {
    // Session fetch failed - treat as not logged in
    session = null;
  }

  const isLoggedIn = !!session?.user;

  // Logged-in user trying to access login/signup → redirect to dashboard
  if (isLoggedIn && ["/login", "/signup"].includes(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Not logged in trying to access dashboard → redirect to login
  if (!isLoggedIn && pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/signup"],
};
