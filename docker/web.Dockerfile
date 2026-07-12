# User Web App Dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@9.15.2

# Copy package files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml turbo.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
COPY packages/types/package.json ./packages/types/
COPY packages/utils/package.json ./packages/utils/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/config/package.json ./packages/config/

# Install dependencies (skip postinstall - we'll build packages in builder stage)
RUN pnpm install --no-frozen-lockfile --ignore-scripts

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@9.15.2

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Install dependencies again to run postinstall scripts now that source is available
RUN pnpm install --prefer-offline

# Build packages first
RUN pnpm --filter @synthesize/ui build
RUN pnpm --filter @synthesize/types build
RUN pnpm --filter @synthesize/utils build
RUN pnpm --filter @synthesize/api-client build

# Build web app
RUN pnpm --filter web build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/apps/web/public ./apps/web/public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "apps/web/server.js"]
