# Development Commands

## Quick Start

```bash
# Recommended for daily development (fast & flexible)
pnpm dev
```

This will:
1. Start **core Docker services** (postgres, redis) - infrastructure only
2. Start **FastAPI backend** locally (port 8000) - hot reload enabled
3. Start **Web app** locally (port 3000) - fast refresh enabled
4. Start **Admin portal** locally (port 3001) - fast refresh enabled

```bash
# Full stack with all Docker services (for production testing)
pnpm dev:full
```

Th🚀 Recommended: Fast development (only infra in Docker, apps run locally)
pnpm dev

# 🐳 Full stack: All services in Docker (slower, tests production setup)
pnpm dev:full

# Individual services (run locally with hot reload)
# Start ALL services (Docker + API + Frontends)
pnpm dev

# Start only core Docker + API + Frontends (faster, no workers/monitoring)
pnpm dev:quick

# Start individual services
pnpm dev:web         # Web app only (3000)
pnpm dev:admin       # Admin portal only (3001)
pnpm dev:api         # FastAPI backend only (8000)
pnpm dev:celery      # Celery worker only (background tasks)
```

### Docker Services - Modular Approach

```bash
# 🎯 Core infrastructure only (recommended for dev)
pnpm docker:dev:up
docker-compose up -d postgres redis

# 📊 Add monitoring tools when needed
pnpm docker:monitoring
docker-compose up -d flower pgadmin

# 💪 Add background workers when needed
pnpm docker:workers
docker-compose up -d celery-worker celery-beat

# 🐳 Full stack (everything in Docker)
pnpm docker:full:up
docker-compose --profile full up -d

# 🛑 Stop services
pnpm docker:full:down           # Stop all
docker-compose stop postgres    # Stop specific service
docker-compose down             # Stop and remove containers

# 📝 View logs
pnpm docker:logs                # All services
docker-compose logs -f api      # Specific service

# 🔨 Build containers (builds everything, but doesn't start)
pnpm docker:build               # Build all containers
pnpm docker:build:quick         # Build only postgres + redis
docker-compose build api        # Build specific service
```

### Build & Deploy

```bash
# Build all apps
pnpm build

# Build specific apps
pnpm build:web
pnpm build:admin

# Production deployment
./scripts/start-full-stack.sh
```

### Database

```bash
# Run migrations
pnpm db:migrate

# Create new migration
pnpm db:migrate:create "migration_name"

# Rollback last migration
pnpm db:rollback

# Reset database (danger!)
pnpm db:reset
```

## Service URLs

### Frontend
- **Web App:** http://localhost:3000
- **Admin Portal:** http://localhost:3001

### Backend
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Redoc:** http://localhost:8000/redoc

### Infrastructure
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

### Monitoring (when using `pnpm dev` or `docker:full:up`)
- **Flower** (Celery monitoring): http://localhost:5555
  - Username: `admin`
  - Password: `admin` (change in .env)
- **pgAdmin** (Database management): http://localhost:5050
  - Email: `admin@synthesize.io`
  - Password: `admin` (change in .env)

## Docker Services Breakdown

### Core Infrastructure
- **postgres** - PostgreSQL database (port 5432)
- **redis** - Redis cache & message queue (port 6379)

### Application Services (with `--profile full`)
- **web** - Next.js user portal (port 3000)
- **admin** - Next.js admin portal (port 3001)
- **api** - FastAPI backend (port 8000)

### Background Processing (with `--profile full`)
- **celery-worker** (x2) - Background task processors
- **celery-beat** - Task scheduler (cron jobs)

### Monitoring & Management (with `--profile full`)
- **flower** - Celery monitoring dashboard (port 5555)
- **pgadmin** - PostgreSQL web interface (port 5050)

### Networking (with `--profile full`)
- **nginx** - Reverse proxy & load balancer (port 80/443)

## Troubleshooting

### Services not starting?
```bash
# Check Docker is running
docker info

# Check service status
docker-compose ps

# View service logs
docker-compose logs -f [service-name]
```

### Port already in use?
```bash
# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or change ports in .env
WEB_PORT=3001
ADMIN_PORT=3002
API_PORT=8001
```

### Fresh start?
```bash
# Stop everything and clean
docker-compose down -v
pnpm clean
pnpm install

# Start fresh
pnpm dev
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  Development Environment (pnpm dev)         │
├─────────────────────────────────────────────┤
│                                             │
│  🐳 Docker Services                         │
│   ├─ postgres:5432                          │
│   ├─ redis:6379                             │
│   ├─ celery-worker x2                       │
│   ├─ celery-beat                            │
│   ├─ flower:5555                            │
│   ├─ pgadmin:5050                           │
│   └─ nginx:80                               │
│                                             │
│  💻 Local Development Servers               │
│   ├─ FastAPI (apps/api) :8000              │
│   ├─ Web (apps/web) :3000                  │
│   └─ Admin (apps/admin) :3001              │
│                                             │
└─────────────────────────────────────────────┘
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Set required environment variables:
   ```bash
   # Critical
   DATABASE_URL=postgresql://synthesize:synthesize_password@localhost:5432/synthesizedb
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET_KEY=your-secret-key
   
   # Optional (for LLM features)
   ANTHROPIC_API_KEY=sk-ant-...
   
   # Optional (for monitoring)
   FLOWER_USER=admin
   FLOWER_PASSWORD=admin
   PGADMIN_EMAIL=admin@synthesize.io
   PGADMIN_PASSWORD=admin
   ```

3. Setup Python environment:
   ```bash
   cd apps/api
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Development Strategies

### Strategy 1: Minimal Docker (Recommended for Daily Dev) ⚡
```bash
pnpm dev
```
- ✅ Fastest startup
- ✅ Easy debugging (all logs in terminal)
- ✅ Hot reload for all apps
- ✅ Only runs what you need

### Strategy 2: Incremental Docker (Testing Features) 🔧
```bash
# Start with basics
pnpm docker:dev:up

# Add services as needed
docker-compose up -d flower      # Need to monitor Celery tasks?
docker-compose up -d pgadmin     # Need to query database?
docker-compose up -d celery-worker  # Testing background jobs?

# Run apps locally
pnpm dev:api
pnpm dev:web
```

### Strategy 3: Full Docker (Pre-Production Testing) 🐳
```bash
pnpm dev:full
# or
pnpm docker:full:up
```
- ✅ Tests production-like environment
- ✅ Tests all integrations
- ⚠️ Slower iteration (rebuild containers)

## Tips

- 🏗️ Build all containers once: `pnpm docker:build` (they're ready when needed)
- 🎯 Use `pnpm dev` for daily development (fastest)
- 📊 Add monitoring only when needed: `pnpm docker:monitoring`
- 🐛 Debug with: `docker-compose logs -f [service]`
- 🔄 Flower dashboard shows real-time Celery task status (http://localhost:5555)
- 💾 pgAdmin provides full database management (http://localhost:5050)
- ⚡ All frontend/backend changes hot-reload automatically
   ```

## Tips

- Use `pnpm dev:quick` for faster startup (no Celery workers/monitoring)
- Use `docker-compose logs -f [service]` to debug specific services
- Flower dashboard shows real-time Celery task status
- pgAdmin provides full database management interface
- All frontend changes hot-reload automatically
- Backend changes auto-reload with `--reload` flag

## Production Deployment

See [docs/Architecture.md](docs/Architecture.md) for complete production deployment guide.

Quick production start:
```bash
./scripts/start-full-stack.sh
```
