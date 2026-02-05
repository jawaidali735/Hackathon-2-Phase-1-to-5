import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "@/db/drizzle";
import * as schema from "@/db/schema"

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  database: drizzleAdapter(db, { provider: "pg",
    schema: {
      ...schema,
    },
  }),
  secret: process.env.BETTER_AUTH_SECRET!, // Shared secret - also used by backend to verify JWT
  baseURL: process.env.BETTER_AUTH_URL,
  trustHost: true,
  // No JWT plugin needed - we create our own JWT tokens with HS256 in get-jwt.ts
});