// Import better-auth for middleware with minimal configuration
import { betterAuth } from "better-auth";

// Create auth instance without database adapter for middleware
const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-for-build",
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  trustHost: true,
  // Don't include database adapter for middleware
});

export default auth;

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};