# =============================================================================
# Multi-stage Dockerfile for Next.js Frontend
# Stage 1: deps    - Install dependencies
# Stage 2: builder - Build the application
# Stage 3: runner  - Production runtime
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies
# -----------------------------------------------------------------------------
FROM node:22-alpine AS deps

# Check https://github.com/nodejs/docker-node/tree/main#nodealpine for why libc6-compat
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json* ./

# Install dependencies using npm ci for reproducible builds
RUN npm ci --ignore-scripts

# -----------------------------------------------------------------------------
# Stage 2: Builder
# -----------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# BetterAuth requires DATABASE_URL at build time for route collection
# This is a dummy value — the real URL is injected at runtime via env vars
ENV DATABASE_URL="postgresql://placeholder:placeholder@localhost:5432/placeholder"
ENV BETTER_AUTH_SECRET="build-time-placeholder-secret"

# NEXT_PUBLIC_* vars are baked at build time (used by browser/client-side code)
# Backend URL for browser API calls (port-forward maps to this)
ENV NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
# BetterAuth client-side URL
ENV NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000"

# Build the Next.js application (standalone output)
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Runner (Production)
# -----------------------------------------------------------------------------
FROM node:22-alpine AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only the necessary files from the builder stage
# Next.js standalone output includes server.js and required dependencies
COPY --from=builder /app/public ./public

# Set correct permissions for prerender cache
RUN mkdir .next && chown nextjs:nodejs .next

# Copy standalone build output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port 3000
EXPOSE 3000

# Set hostname to listen on all interfaces
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

# Health check for Kubernetes probes
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run the standalone server
CMD ["node", "server.js"]
