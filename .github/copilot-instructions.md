# Synthesize.io - AI Coding Agent Instructions

## 🏗️ Architecture Overview

**Monorepo Structure** (pnpm workspaces + Turborepo):
- `apps/api` - FastAPI backend (Python 3.11+, SQLAlchemy, Alembic)
- `apps/web` - User-facing Next.js app (port 3000)
- `apps/admin` - Admin portal Next.js app (port 3001)
- `packages/` - Shared code (api-client, ui, types, utils, config)

**Core Architectural Pattern - Lightweight Controller + Heavy Workers**:
- FastAPI acts as the "Brain" - handles HTTP requests, auth, orchestration (< 200ms response)
- Celery workers are the "Muscles" - process heavy data generation tasks asynchronously
- **Critical**: Never block FastAPI with heavy processing. Use Celery tasks in `apps/api/app/tasks/` for:
  - Data generation (`generation.py`)
  - Exports and validation (`generation.py`)
  - Email notifications (`notifications.py`)
  - Scheduled cleanup (`cleanup.py`)

## 🔑 Key Patterns & Conventions

### API Development (FastAPI)

**Dependency Injection Pattern** - All endpoints use FastAPI dependencies from `apps/api/app/api/deps.py`:
```python
from app.api.deps import DBSession, CurrentUser, RequireAdmin

@router.get("/protected")
async def protected_endpoint(
    db: DBSession,                    # Auto-injected database session
    user: CurrentUser,                # Authenticated user (raises 401 if missing)
    current_org: RequireOrganization, # User's active organization
):
    # user, db, org are automatically validated and injected
```

**Exception Handling** - Use custom exceptions from `apps/api/app/core/exceptions.py`:
```python
from app.core.exceptions import AuthorizationError, ResourceNotFoundError

if not user.has_permission("admin"):
    raise AuthorizationError("Admin access required")
```

**Heavy Task Pattern** - FastAPI returns task ID immediately, client polls for results:
```python
# In endpoint:
task = generate_dataset.delay(job_id, request_data)  # Returns immediately
return {"task_id": task.id, "status": "processing"}

# Task definition in apps/api/app/tasks/generation.py:
@celery_app.task(bind=True, name="app.tasks.generation.generate_dataset")
def generate_dataset(self, job_id: str, request_data: dict):
    self.update_state(state='PROCESSING', meta={'progress': 25})
    # ... heavy work here
```

### Database & Models

**Multi-Database Strategy**:
- PostgreSQL (primary) - Transactional data (users, organizations, datasets, billing)
- MongoDB - Utility data (logs, analytics, usage tracking)
- Redis - Caching (db 0), Celery broker (db 1), results (db 2)

**Models Location**: All SQLAlchemy models in single file `apps/api/app/models.py` (1200+ lines)
- Organized by domain with clear ENUM sections
- Always use UUIDs for primary keys: `id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`
- Use relationships with explicit back_populates

**Migrations**: Use Alembic, stored in `apps/api/alembic/versions/`
```bash
# Create migration
pnpm db:migrate:create "description"

# Apply migrations
pnpm db:migrate

# Rollback
pnpm db:rollback
```

### Frontend Development (Next.js)

**Shared Packages Pattern**:
- Import from `@synthesize/api-client` for API calls (typed axios client)
- Import from `@synthesize/types` for shared TypeScript interfaces
- Import from `@synthesize/ui` for shared React components
- Import from `@synthesize/utils` for utility functions

**API Client Usage** (from `packages/api-client/src/index.ts`):
```typescript
import { SynthesizeClient } from '@synthesize/api-client';

const client = new SynthesizeClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  tokenProvider: () => getStoredToken(),
});

const { data } = await client.datasets.list();
```

**File Organization**:
- `src/app/` - Next.js 13+ app router pages
- `src/components/` - React components (co-locate landing page components in subdirs)
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utilities and helpers
- `src/providers/` - React context providers

## 🛠️ Critical Workflows

### Development Setup

**Required tools**: Node.js 20+, pnpm 8.12+, Python 3.11+, Docker 24+

**Fast development** (infrastructure in Docker, apps local with hot reload):
```bash
pnpm dev  # Starts postgres+redis in Docker, API+web+admin locally
```

**Full Docker stack** (tests production setup, slower):
```bash
pnpm dev:full  # Everything in Docker containers
```

**Python environment** - API uses venv in `apps/api/venv/`:
```bash
cd apps/api
source venv/bin/activate  # Always activate before running API commands
```

### Testing

**API tests** - pytest with SQLite in-memory database:
```bash
cd apps/api
source venv/bin/activate
pytest                    # Run all tests
pytest -v tests/test_auth.py  # Specific test file
pytest -k "test_create"   # Tests matching pattern
```

**Test fixtures** in `apps/api/tests/conftest.py`:
- `db` - Fresh database session per test
- `client` - TestClient with DB override
- `test_user`, `test_admin` - Pre-created user fixtures
- `auth_headers` - Authorization headers for authenticated requests

**Frontend tests** - Use Turborepo:
```bash
pnpm test              # Run all workspace tests
pnpm test:watch        # Watch mode
```

### Database Workflow

**Schema changes**:
1. Edit models in `apps/api/app/models.py`
2. Generate migration: `pnpm db:migrate:create "add_user_avatar"`
3. Review generated file in `apps/api/alembic/versions/`
4. Apply: `pnpm db:migrate`

**Common Alembic gotchas**:
- Always import new models in `models.py` before generating migrations
- Enum changes require explicit `ALTER TYPE` in migration (Alembic doesn't auto-detect)
- Use `batch_alter_table` for SQLite compatibility in tests

### LLM Integration Pattern

**When to use LLM** (Anthropic Claude via `apps/api/app/services/llm_service.py`):
- Small sample generation (5-10 rows) for user preview
- Schema refinement from natural language
- Data quality validation suggestions

**When NOT to use LLM**:
- Bulk data generation (use algorithmic data factory)
- Real-time endpoints (use cached results)
- Free tier users (too expensive)

**Example** (`apps/api/app/examples/llm_usage.py`):
```python
from app.services.llm_service import get_llm_service

llm = get_llm_service()
sample = llm.generate_sample(schema, rows=5)  # Quick preview
# Then delegate bulk generation to Celery
task = generate_dataset.delay(job_id, schema, rows=10000)
```

## 🔧 Configuration & Environment

**Environment files**:
- Root `.env` - Docker Compose variables
- `apps/web/.env.local` - Web app (NEXT_PUBLIC_* only)
- `apps/admin/.env.local` - Admin portal
- `apps/api/.env` - API secrets (never commit)

**Settings pattern** - Pydantic settings in `apps/api/app/core/config.py`:
```python
from app.core.config import settings

db_url = settings.DATABASE_URL        # Auto-loaded from env
jwt_secret = settings.JWT_SECRET_KEY  # Validates at startup
```

**Common env vars** (see `ENV_VARIABLES_SETUP.md` for complete list):
- `DATABASE_URL` - PostgreSQL connection
- `CELERY_BROKER_URL` - Redis for task queue
- `ANTHROPIC_API_KEY` - Claude API (optional)
- `JWT_SECRET_KEY` - Auth token signing

## 📦 Package Management

**Adding dependencies**:
```bash
# Root workspace dependency
pnpm add -w <package>

# Specific app
pnpm add <package> --filter web

# Shared package
pnpm add <package> --filter @synthesize/types
```

**Python dependencies**:
```bash
cd apps/api
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt  # Update lockfile
```

## 🚨 Common Pitfalls

1. **Don't block FastAPI** - If operation > 5s, use Celery task
2. **Always use DBSession dependency** - Never create Session manually in endpoints
3. **Run migrations before starting API** - Fresh DB needs `pnpm db:migrate`
4. **Activate Python venv** - API commands fail without `source venv/bin/activate`
5. **Check Docker health** - `docker-compose ps` - postgres/redis must be "healthy"
6. **Turborepo caching** - Run `pnpm clean` if seeing stale builds
7. **API client types** - Rebuild `@synthesize/api-client` after API schema changes

## 📂 Key Files Reference

- [apps/api/app/main.py](apps/api/app/main.py) - FastAPI app initialization
- [apps/api/app/api/v1/router.py](apps/api/app/api/v1/router.py) - API route aggregation
- [apps/api/app/models.py](apps/api/app/models.py) - All database models (1200+ lines)
- [apps/api/app/celery_app.py](apps/api/app/celery_app.py) - Celery configuration
- [docker-compose.yml](docker-compose.yml) - Service orchestration with profiles
- [package.json](package.json) - All development scripts
- [turbo.json](turbo.json) - Build pipeline configuration
- [docs/Architecture.md](docs/Architecture.md) - Comprehensive architecture guide (2400 lines)
