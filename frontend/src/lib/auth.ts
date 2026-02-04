import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "@/db/drizzle";
import * as schema from "@/db/schema"

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  ...(process.env.DATABASE_URL ? {
    database: drizzleAdapter(db, { provider: "pg",
      schema: {
        ...schema,
      },
    }),
  } : {}),
  secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-for-build", // Shared secret - also used by backend to verify JWT
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  trustHost: true,
  // No JWT plugin needed - we create our own JWT tokens with HS256 in get-jwt.ts
});
