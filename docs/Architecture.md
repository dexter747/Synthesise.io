# Synthesize.io - System Architecture Document

**Version:** 1.0  
**Date:** December 30, 2025  
**Status:** Final  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Component Architecture](#3-component-architecture)
4. [Docker Containerization Strategy](#4-docker-containerization-strategy)
5. [Data Flow Architecture](#5-data-flow-architecture)
6. [Database Architecture](#6-database-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Technology Stack](#9-technology-stack)
10. [Integration Architecture](#10-integration-architecture)
11. [Scalability & Performance](#11-scalability--performance)

---

## 1. Architecture Overview

### 1.1 System Purpose

Synthesize.io is an AI-powered synthetic data generation platform that combines Large Language Model (LLM) intelligence with custom algorithmic data generation to produce high-quality, customizable synthetic datasets at scale.

### 1.2 Architecture Principles

- **Microservices-Based**: Loosely coupled services communicating via APIs
- **Monorepo Structure**: All applications managed in single repository with pnpm workspaces
- **Containerized**: All services run in Docker containers for consistency
- **Scalable**: Horizontal scaling capabilities for high load
- **Secure**: End-to-end encryption and secure authentication
- **Cost-Efficient**: LLM used only for small samples; bulk generation via algorithms
- **Cloud-Agnostic**: Runs on local VMs without cloud provider lock-in

### 1.3 Key Design Decisions

| Decision | Rationale |
|---Monorepo with pnpm** | Shared dependencies, consistent tooling, atomic changes across apps |
| **Separate Admin Portal** | Enhanced security, independent deployment, specialized UI/UX |
| **-------|-----------|
| **Local VM Storage** | Cost savings, data sovereignty, no cloud vendor lock-in |
| **Docker Containerization** | Consistency across environments, easy scaling, portability |
| **PayPal + Razorpay** | Global payment coverage without Stripe fees |
| **Nodemailer** | Self-hosted email, no third-party email service costs |
| **No Cloud Monitoring** | Custom logging reduces operational costs |
| **Google OAuth** | Trusted authentication, reduces friction |
| **TanStack Suite** | Modern React patterns, type-safe, performant |

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin Portal │  │ API Clients  │     │
│  │ (User App)   │  │ (Admin App)  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS/TLS 1.3
┌────────────────────────────┴────────────────────────────────┐
│                   CDN / Reverse Proxy                        │
│                     (Nginx/Cloudflare)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │     Next.js Frontend (User-Facing Web App)       │       │
│  │  - Server-Side Rendering (SSR)                   │       │
│  │  - Static Generation (SSG)                       │       │
│  │  - Client-Side Rendering (CSR)                   │       │
│  │  - TanStack Query/Table/Router                   │       │
│  │  - Google Analytics Integration                  │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │     Next.js Admin Portal (Admin Dashboard)       │       │
│  │  - Enhanced Security (2FA, IP Restrictions)      │       │
│  │  - System Monitoring & Management                │       │
│  │  - User & Subscription Management                │       │
│  │  - Analytics & Reporting                         │       │
│  └──────────────────────────────────────────────────┘       │
│                             │                                │
│  ┌──────────────────────────────────────────────────┐       │
│  │           FastAPI Backend (Python)                │       │
│  │  - RESTful API Endpoints                         │       │
│  │  - Authentication & Authorization                │       │
│  │  - Business Logic                                │       │
│  │  - Google OAuth Integration                      │       │
│  │  - Admin API Endpoints     zation                │       │
│  │  - Business Logic                                │       │
│  │  - Google OAuth Integration                      │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────┬───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌─────────▼──────────┐
│   LLM Service     │ │ Data Factory│ │  Job Queue         │
│  (Anthropic API)  │ │  (Custom)   │ │  (Celery+Redis)    │
│                   │ │             │ │                    │
│ - Request         │ │ - Pattern   │ │ - Task Queue       │
│   Refinement      │ │   Analysis  │ │ - Job Scheduling   │
│ - Sample          │ │ - Data Gen  │ │ - Progress Track   │
│   Generation      │ │ - Validation│ │ - Notifications    │
└───────────────────┘ └─────────────┘ └────────────────────┘
                              │
          ┌───────────────────┼─────────────────────┬───────────────────┐
          │                   │                     │                   │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────────▼────────┐ ┌───────▼──────────┐
│   PostgreSQL      │ │    Redis    │ │      MongoDB        │ │  Local VM Storage│
│  (Primary DB)     │ │   (Cache)   │ │   (Utility DB)      │ │  (File Storage)  │
│                   │ │             │ │                     │ │                  │
│ - User Data       │ │ - Sessions  │ │ - Activity Logs     │ │ - Generated Files│
│ - Datasets Meta   │ │ - Job Queue │ │ - Usage Tracking    │ │ - Exports        │
│ - Billing         │ │ - Rate Limit│ │ - Analytics Events  │ │ - Backups        │
│ - Subscriptions   │ │ - Cache     │ │ - API Logs          │ │ - Temp Files     │
└───────────────────┘ └─────────────┘ └─────────────────────┘ └──────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────┐
│              External Services                                │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐                   │
│  │  PayPal  │  │ Razorpay │  │Google OAuth│                   │
│  └──────────┘  └──────────┘  └────────────┘                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐                   │
│  │   SMTP   │  │  Google  │  │   Google   │                   │
│  │ (Email)  │  │ Analytics│  │   Search   │                   │
│  └──────────┘  └──────────┘  └────────────┘                   │
└───────────────────────────────────────────────────────────────┘
```

---

## 2.1 Monorepo Structure with pnpm Workspaces

## 3. Component Architecture

### 3.1 Frontend Applications (Next.js + React)

The platform consists of two separate Next.js applications within the monorepo:

#### 3.1.1 User-Facing Web App (`apps/web`)

**Technology Stack:**
- Next.js 15+ (React framework with SSR/SSG)
- React 19+ (UI library with React Compiler)
- TypeScript 5.7+ (Type safety)
- TailwindCSS 3.4+ (Utility-first styling)
- ShadCN UI (Component library from `packages/ui`)
- TanStack Query 5+ (Server state management)
- TanStack Table 8+ (Advanced data tables)
- TanStack Router 1.x (Type-safe routing)
- Zustand 5+ (Client state management)
- Axios 1.7+ (HTTP client via `packages/api-client`)
- Google Analytics 4 (User tracking)

**Key Modules:**

```
apps/web/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── (auth)/            # Authentication routes
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── reset-password/
│   │   ├── (dashboard)/       # Protected dashboard routes
│   │   │   ├── dashboard/
│   │   │   ├── generate/
│   │   │   ├── datasets/
│   │   │   ├── api-keys/
│   │   │   ├── billing/
│   │   │   └── settings/
│   │   ├── api/               # API routes (OAuth callbacks)
│   │   ├── layout.tsx
│   │   └── page.tsx           # Landing page
│   ├── components/
│   │   ├── auth/              # Login, Register, OAuth
│   │   ├── dashboard/         # Dashboard widgets
│   │   ├── generation/        # Data generation wizard
│   │   ├── datasets/          # Dataset management
│   │   └── layout/            # Layout components
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useDataGeneration.ts
│   │   └── useAnalytics.ts
│   ├── lib/
│   │   ├── api.ts             # API client instance
│   │   ├── auth.ts            # Auth utilities
│   │   └── analytics.ts       # GA4 integration
│   ├── store/                 # State management
│   │   ├── authStore.ts
│   │   └── uiStore.ts
│   └── types/                 # App-specific types
├── public/                    # Static assets
├── next.config.js
├── tailwind.config.js
└── package.json
```

**Responsibilities:**
- User authentication and registration
- Data generation request interface
- Dataset management and downloads
- Billing and subscription management
- User settings and preferences
- API key management
- Usage analytics display

#### 3.1.2 Admin Portal App (`apps/admin`)

**Technology Stack:**
- Same as web app (shared from packages)
- Enhanced security features
- Admin-specific components
- Real-time monitoring dashboards
- Advanced data tables and charts

**Key Modules:**

```
apps/admin/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── admin-login/    # Separate admin auth
│   │   ├── (admin)/            # Protected admin routes
│   │   │   ├── dashboard/      # System overview
│   │   │   ├── users/          # User management
│   │   │   ├── jobs/           # Job queue management
│   │   │   ├── billing/        # Payment management
│   │   │   ├── analytics/      # Business analytics
│   │   │   ├── monitoring/     # System health
│   │   │   ├── config/         # System configuration
│   │   │   ├── audit/          # Audit logs
│   │   │   └── support/        # Support tools
│   │   └── api/
│   ├── components/
│   │   ├── admin/
│   │   │   ├── UserTable.tsx
│   │   │   ├── JobQueue.tsx
│   │   │   ├── SystemHealth.tsx
│   │   │   ├── RevenueChart.tsx
│   │   │   └── AuditLog.tsx
│   │   ├── monitoring/
│   │   │   ├── MetricCard.tsx
│   │   │   ├── LogViewer.tsx
│   │   │   └── AlertPanel.tsx
│   │   └── charts/             # Data visualization
│   ├── hooks/
│   │   ├── useAdminAuth.ts
│   │   ├── useSystemMetrics.ts
│   │   └── useUserManagement.ts
│   └── lib/
│       ├── admin-api.ts        # Admin-specific API calls
│       └── permissions.ts      # Role-based access
├── public/
├── next.config.js
└── package.json
```

**Responsibilities:**
- User account management (view, edit, suspend, delete)
- Subscription management (upgrades, downgrades, refunds)
- Job queue monitoring and management
- System health monitoring (services, resources)
- Payment transaction management
- Business analytics and reporting
- System configuration (feature flags, quotas, rate limits)
- Security audit logs
- Support ticket management
- Admin user management

**Security Features:**
- Separate authentication endpoint
- Two-factor authentication (2FA) required
- IP whitelist restrictions
- Enhanced session security (shorter timeouts)
- Audit logging for all actions
- Role-based access control (Super Admin, Admin, Support, Analyst)ocker-compose up -d",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "@turbo/gen": "^1.11.0",
    "turbo": "^1.11.0",
    "prettier": "^3.1.0",
    "eslint": "^8.55.0",
    "typescript": "^5.3.0"
  },
  "packageManager": "pnpm@8.12.0"
}
```

**turbo.json:**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "type-check": {
      "dependsOn": ["^type-check"]
    }
  }
}
```

### 2.1.3 Benefits of Monorepo Approach

- **Code Sharing**: Shared components, types, and utilities across apps
- **Atomic Changes**: Single PR can update multiple apps simultaneously
- **Consistent Tooling**: Same linting, formatting, and build tools
- **Simplified Dependency Management**: Single lock file for all packages
- **Better Developer Experience**: Single repository to clone and maintain
- **Type Safety**: Shared types ensure consistency across frontend and backend contracts

---

## 3. Component Architecture

### 3.1 Frontend Layer (Next.js + React)

**Technology Stack:**
- Next.js 14+ (React framework with SSR/SSG)
- React 18+ (UI library)
- TypeScript (Type safety)
- TailwindCSS 3+ (Utility-first styling)
- ShadCN UI (Component library)
- TanStack Query (Server state management)
- TanStack Table (Advanced data tables)
- TanStack Router (Type-safe routing)
- Zustand/Redux (Client state management)
- Axios (HTTP client)
- Google Analytics (User tracking)

**Key Modules:**

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── (auth)/            # Authentication routes
│   │   ├── (dashboard)/       # Protected dashboard routes
│   │   └── api/               # API routes
│   ├── components/
│   │   ├── auth/              # Login, Register, OAuth
│   │   ├── dashboard/         # Dashboard widgets
│   │   ├── generation/        # Data generation wizard
│   │   ├── datasets/          # Dataset management
│   │   └── ui/                # ShadCN UI components
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useDataGeneration.ts
│   │   └── useAnalytics.ts    # Google Analytics hooks
│   ├── lib/
│   │   ├── api/               # API client functions
│   │   ├── utils/             # Utility functions
│   │   └── analytics.ts       # GA4 integration
│   ├── store/                 # State management
│   └── types/                 # TypeScript types
├── public/                    # Static assets
└── docker/
    └── Dockerfile
```

**Responsibilities:**
- User interface rendering (SSR/CSR/SSG)
- User authentication flows
- Data generation wizard
- Dataset management interface
- Real-time progress updates
- Analytics tracking
- API communication

### 3.2 Backend Layer (FastAPI)

**Technology Stack:**
- FastAPI 0.100+ (Python web framework)
- Python 3.11+
- Pydantic (Data validation)
- SQLAlchemy 2.0+ (ORM)
- Alembic (Database migrations)
- Celery (Async task queue)
- Redis (Cache and queue backend)
- JWT (Authentication tokens)
- Google OAuth2 Library (authlib/google-auth)
- Docker

**Key Modules:**

```
apps/api/ (FastAPI Backend)
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── users.py          # User management
│   │   │   ├── generation.py     # Data generation endpoints
│   │   │   ├── datasets.py       # Dataset management
│   │   │   ├── billing.py        # Payment processing
│   │   │   ├── webhooks.py       # Webhook endpoints
│   │   │   └── admin/            # Admin-only endpoints
│   │   │       ├── users.py      # Admin user management
│   │   │       ├── jobs.py       # Job management
│   │   │       ├── billing.py    # Admin billing
│   │   │       ├── analytics.py  # Business analytics
│   │   │       ├── system.py     # System monitoring
│   │   │       ├── config.py     # Configuration management
│   │   │       └── audit.py      # Audit logs
│   │   └── deps.py               # Dependencies
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   ├── security.py           # Security utilities
│   │   ├── oauth.py              # Google OAuth handler
│   │   └── permissions.py        # RBAC permissions
│   ├── services/
│   │   ├── llm_service.py        # Anthropic API integration
│   │   ├── data_factory.py       # Data generation engine
│   │   ├── payment_service.py    # PayPal/Razorpay
│   │   ├── email_service.py      # Nodemailer integration
│   │   ├── analytics_service.py  # Usage analytics
│   │   └── admin_service.py      # Admin operations
│   ├── models/
│   │   ├── user.py
│   │   ├── dataset.py
│   │   ├── subscription.py
│   │   ├── generation_job.py
│   │   └── audit_log.py
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user.py
│   │   ├── dataset.py
│   │   ├── admin.py
│   │   └── analytics.py
│   ├── db/
│   │   ├── database.py           # DB connection
│   │   └── session.py
│   └── tasks/
│       └── celery_tasks.py       # Background jobs
├── alembic/                      # Database migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
└── Dockerfile
```

**Responsibilities:**
- RESTful API endpoints for user and admin operations
- Authentication & authorization (JWT + OAuth)
- Business logic orchestration
- LLM API integration
- Payment processing
- Email notifications
- Usage tracking and analytics
- Job queue management
- Admin operations and reporting

### 3.3 Data Generation Factory

**Core Components:**

```python
# Simplified Architecture

class DataFactory:
    """
    Custom algorithm that replicates LLM-generated samples
    into large-scale datasets
    """
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.constraint_validator = ConstraintValidator()
        self.data_generators = {
            'personal': PersonalDataGenerator(),
            'financial': FinancialDataGenerator(),
            'temporal': TemporalDataGenerator(),
            'categorical': CategoricalDataGenerator(),
            'numerical': NumericalDataGenerator(),
            'text': TextDataGenerator(),
        }
    
    def analyze_sample(self, llm_sample: List[Dict]) -> DataSchema:
        """Extract patterns from LLM-generated sample"""
        pass
    
    def generate_dataset(self, schema: DataSchema, row_count: int) -> Dataset:
        """Generate full dataset based on analyzed patterns"""
        pass
    
    def validate_quality(self, dataset: Dataset) -> QualityReport:
        """Ensure data quality meets requirements"""
        pass
```

**Pattern Analysis:**
- Statistical distribution detection
- Data type inference
- Relationship mapping
- Constraint identification
- Uniqueness requirements

**Data Generation:**
- Deterministic algorithms
- Referential integrity maintenance
- Format compliance
- Uniqueness enforcement
- Quality validation

### 3.4 LLM Service (Anthropic Claude Integration)

**Purpose:** AI-powered request refinement and sample generation

**Location:** `apps/api/app/services/llm_service.py`

**Key Features:**
- Refine natural language requests into structured schemas
- Generate realistic sample data (10-50 rows) for user approval
- Analyze data patterns to guide Data Factory
- Suggest schema improvements

**API Model:** Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)

**Usage Pattern:**
```python
# FastAPI uses LLM for quick operations (2-5 seconds)
llm = get_llm_service()

# Step 1: Refine user request
schema = llm.refine_request("I need customer data")
# Returns: {columns, types, constraints}

# Step 2: Generate small sample for approval
sample = llm.generate_sample_data(schema, row_count=10)
# User reviews sample in UI

# Step 3: After approval, Celery generates full dataset
# (Data Factory handles bulk generation, NOT LLM)
```

**Why Not Use LLM for Full Generation?**
- LLM: Expensive, slow (tokens/second limited)
- Data Factory: Fast, free, generates millions of rows
- Strategy: LLM for samples (quality), Data Factory for scale (quantity)

### 3.5 Job Queue System (Celery + Redis)

**Architecture:** FastAPI as Brain 🧠, Celery as Muscles 💪

```
┌─────────────────────────────────────────────────────┐
│  FastAPI (Brain) - Lightweight Controller           │
│  - HTTP requests (< 200ms response)                 │
│  - Authentication & validation                      │
│  - Queue jobs to Celery                             │
│  - Does NOT process heavy work                      │
└──────────────────────┬──────────────────────────────┘
                       │ Queue Tasks
                       ▼
┌─────────────────────────────────────────────────────┐
│  Redis - Message Queue                              │
│  - generation:0 (HIGH priority)                     │
│  - notifications:0 (NORMAL priority)                │
│  - cleanup:0 (LOW priority)                         │
└──────────────────────┬──────────────────────────────┘
                       │ Workers Pick Tasks
                       ▼
┌─────────────────────────────────────────────────────┐
│  Celery Workers (Muscles) - Heavy Processing        │
│  - Scale: 2-100 workers                             │
│  - Concurrency: 4 tasks per worker                  │
│  - Processing: 2-10 minutes per job                 │
│  - Uses Data Factory + LLM Service                  │
└──────────────────────┬──────────────────────────────┘
                       │ Updates Status
                       ▼
┌─────────────────────────────────────────────────────┐
│  PostgreSQL - Job Status Tracking                   │
└─────────────────────────────────────────────────────┘
```

**Celery Tasks** (`apps/api/app/tasks/`):
- `generation.py`: 
  - `generate_dataset` - Main data generation
  - `export_dataset` - Format conversion
  - `validate_dataset` - Quality checks
- `notifications.py`:
  - `send_email` - Email delivery
  - `trigger_webhook` - Webhook calls
  - `send_completion_notification` - Job completion alerts
- `cleanup.py`:
  - `cleanup_old_datasets` - Retention enforcement
  - `calculate_usage_stats` - Analytics aggregation
  - `archive_old_jobs` - Historical data archival

**Queue Configuration:**
- Priority: `generation` (HIGH) > `notifications` (NORMAL) > `cleanup` (LOW)
- Concurrency: 4 tasks per worker
- Timeout: 15 minutes per task
- Retry: Exponential backoff (max 3 retries)
- Dead letter queue for permanent failures

**Scaling:**
```bash
# Development: 2 workers
docker-compose up -d --scale celery-worker=2

# Production: 10 workers
docker-compose up -d --scale celery-worker=10
```

### 3.6 Separation of Concerns

**Critical Architectural Principle:** FastAPI NEVER does heavy processing

| Component | Role | Responsibilities | Does NOT Do |
|-----------|------|------------------|-------------|
| **FastAPI** | Brain 🧠 | HTTP, auth, validation, queuing | Heavy processing, loops, file I/O |
| **Celery** | Muscles 💪 | Data generation, emails, exports | HTTP handling, user sessions |
| **Data Factory** | Algorithm 🏭 | Pure data synthesis logic | API calls, database access |
| **LLM Service** | AI Assistant 🤖 | Refinement, small samples | Bulk generation (too expensive) |

**Benefits:**
- ✅ FastAPI responds in < 200ms (never blocked)
- ✅ Scale API and workers independently
- ✅ Worker crashes don't affect API
- ✅ Failed jobs automatically retry
- ✅ Real-time progress tracking

---

## 4. Docker Containerization Strategy

### 4.1 Container Services

```yaml
# docker-compose.yml (Simplified)

version: '3.8'

services:
  # Frontend Service
  frontend:
    build: ./frontend
    container_name: synthesize-frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_GA_ID=${GA_TRACKING_ID}
    depends_on:
      - backend
    networks:
      - synthesize-network
    restart: unless-stopped

  # Backend API Service
  backend:
    build: ./backend
    container_name: synthesize-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/synthesizedb
      - REDIS_URL=redis://redis:6379
      - LLM_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_OAUTH_CLIENT_ID}
      - GOOGLE_OAUTH_CLIENT_SECRET=${GOOGLE_OAUTH_CLIENT_SECRET}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./data/generated:/app/data/generated
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - synthesize-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: synthesize-postgres
    environment:
      - POSTGRES_DB=synthesizedb
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    networks:
      - synthesize-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache & Queue
  redis:
    image: redis:7-alpine
    container_name: synthesize-redis
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - synthesize-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MongoDB (Utility Data Store)
  mongodb:
    image: mongo:7-jammy
    container_name: synthesize-mongodb
    environment:
      - MONGO_INITDB_DATABASE=synthesize_utility
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - synthesize-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Celery Worker
  celery-worker:
    build: ./backend
    container_name: synthesize-celery-worker
    command: celery -A app.celery worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/synthesizedb
      - REDIS_URL=redis://redis:6379
      - LLM_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data/generated:/app/data/generated
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - synthesize-network
    restart: unless-stopped
    deploy:
      replicas: 2  # Scale as needed

  # Celery Beat (Scheduled Tasks)
  celery-beat:
    build: ./backend
    container_name: synthesize-celery-beat
    command: celery -A app.celery beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/synthesizedb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - synthesize-network
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: synthesize-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./data/generated:/var/www/data:ro
    depends_on:
      - frontend
      - backend
    networks:
      - synthesize-network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  mongodb_data:
    driver: local

networks:
  synthesize-network:
    driver: bridge
```

### 4.2 Container Resource Limits

```yaml
# Production resource constraints

services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  celery-worker:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### 4.3 Docker Benefits

- **Consistency**: Same environment from dev to production
- **Isolation**: Services don't interfere with each other
- **Scalability**: Easy horizontal scaling (replicas)
- **Portability**: Deploy on any VM with Docker
- **Version Control**: Infrastructure as code
- **Resource Management**: CPU/memory limits per container
- **Security**: Network isolation, least privilege

---

## 5. Data Flow Architecture

### 5.1 Data Generation Flow

```
┌──────────────┐
│     User     │
│   (Browser)  │
└──────┬───────┘
       │ 1. Submit Request (Natural Language)
       ▼
┌──────────────┐
│   Next.js    │
│   Frontend   │ ◄───── 2. Input Validation
└──────┬───────┘
       │ 3. POST /api/v1/generate
       ▼
┌──────────────┐
│   FastAPI    │
│   Backend    │ ──► 4. Check Quota & Auth
└──────┬───────┘
       │ 5. Forward to LLM Service
       ▼
┌──────────────┐
│   Anthropic  │
│   Claude API │ ──► 6. Analyze & Generate Sample (10-50 rows)
└──────┬───────┘
       │ 7. Return Sample
       ▼
┌──────────────┐
│   Backend    │ ──► 8. Store Sample, Return to User
└──────┬───────┘
       │ 9. User Approves Sample
       ▼
┌──────────────┐
│   Celery     │ ◄── 10. Queue Generation Job
│    Queue     │
└──────┬───────┘
       │ 11. Worker Picks Job
       ▼
┌──────────────┐
│ Data Factory │
│  (Algorithm) │ ──► 12. Generate Full Dataset
└──────┬───────┘
       │ 13. Validate Quality
       ▼
┌──────────────┐
│  Local VM    │ ◄── 14. Save Dataset File
│   Storage    │
└──────┬───────┘
       │ 15. Save Metadata
       ▼
┌──────────────┐
│  PostgreSQL  │
└──────┬───────┘
       │ 16. Send Notification (Nodemailer)
       ▼
┌──────────────┐
│     User     │ ◄── 17. Download Link
│   (Email)    │
└──────────────┘
```

### 5.2 Authentication Flow

```
┌──────────────┐
│     User     │
│   (Browser)  │
└──────┬───────┘
       │ 1. Click "Sign in with Google"
       ▼
┌──────────────┐
│   Frontend   │ ──► 2. Redirect to Google OAuth
└──────────────┘
       ▲
       │ 3. User authorizes
       │
┌──────────────┐
│    Google    │
│    OAuth     │ ──► 4. Authorization Code
└──────┬───────┘
       │ 5. POST /api/v1/auth/google/callback
       ▼
┌──────────────┐
│   Backend    │ ──► 6. Exchange code for tokens
└──────┬───────┘
       │ 7. Create/Update user in DB
       ▼
┌──────────────┐
│  PostgreSQL  │
└──────┬───────┘
       │ 8. Generate JWT token
       ▼
┌──────────────┐
│    Redis     │ ◄── 9. Store session
└──────┬───────┘
       │ 10. Return JWT to frontend
       ▼
┌──────────────┐
│   Frontend   │ ──► 11. Store in secure cookie
└──────┬───────┘
       │ 12. All subsequent requests include JWT
       ▼
┌──────────────┐
│   Backend    │ ──► 13. Validate JWT on each request
└──────────────┘
```

### 5.3 Payment Flow

```
┌──────────────┐
│     User     │
│  (Dashboard) │
└──────┬───────┘
       │ 1. Select subscription tier
       ▼
┌──────────────┐
│   Frontend   │ ──► 2. POST /api/v1/billing/subscribe
└──────┬───────┘
       │ 3. Create payment session
       ▼
┌──────────────┐
│   Backend    │ ──► 4. Call PayPal/Razorpay API
└──────┬───────┘
       │ 5. Return payment URL
       ▼
┌──────────────┐
│   PayPal /   │ ◄── 6. User completes payment
│  Razorpay    │
└──────┬───────┘
       │ 7. Webhook notification
       ▼
┌──────────────┐
│   Backend    │ ──► 8. Verify webhook signature
└──────┬───────┘
       │ 9. Update subscription status
       ▼
┌──────────────┐
│  PostgreSQL  │
└──────┬───────┘
       │ 10. Send confirmation email (Nodemailer)
       ▼
┌──────────────┐
│     User     │
│   (Email)    │
└──────────────┘
```

---

## 6. Database Architecture

### 6.1 PostgreSQL Schema

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL for OAuth-only users
    full_name VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,  -- 'google', 'github'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations & Teams
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organization_members (
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'admin', 'member', 'viewer'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (org_id, user_id)
);

-- Subscriptions & Billing
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL,  -- 'starter', 'professional', 'business', 'enterprise'
    status VARCHAR(50) NOT NULL,  -- 'active', 'past_due', 'canceled', 'paused'
    payment_provider VARCHAR(50),  -- 'paypal', 'razorpay'
    external_subscription_id VARCHAR(255),
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,  -- 'pending', 'completed', 'failed', 'refunded'
    provider VARCHAR(50) NOT NULL,  -- 'paypal', 'razorpay'
    external_payment_id VARCHAR(255),
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,  -- 'draft', 'open', 'paid', 'void'
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Generation
CREATE TABLE generation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    llm_sample JSONB,  -- LLM-generated sample data
    schema JSONB,  -- Extracted data schema
    status VARCHAR(50) NOT NULL,  -- 'draft', 'pending', 'approved', 'processing'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    request_id UUID REFERENCES generation_requests(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    size_bytes BIGINT NOT NULL,
    row_count INTEGER NOT NULL,
    format VARCHAR(50) NOT NULL,  -- 'csv', 'json', 'sql', 'parquet', 'excel'
    status VARCHAR(50) NOT NULL,  -- 'generating', 'completed', 'failed'
    file_path TEXT,  -- Local VM storage path
    download_url TEXT,  -- Temporary download URL
    quality_score INTEGER,  -- 0-100
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP  -- Based on retention policy
);

CREATE TABLE generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES generation_requests(id),
    dataset_id UUID REFERENCES datasets(id),
    status VARCHAR(50) NOT NULL,  -- 'queued', 'processing', 'completed', 'failed'
    progress INTEGER DEFAULT 0,  -- 0-100
    error_message TEXT,
    celery_task_id VARCHAR(255),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage Tracking
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    data_generated_gb DECIMAL(10, 3) DEFAULT 0,
    dataset_count INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE TABLE quota_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier VARCHAR(50) UNIQUE NOT NULL,
    monthly_gb_limit DECIMAL(10, 3) NOT NULL,
    max_concurrent_jobs INTEGER DEFAULT 5,
    api_rate_limit INTEGER DEFAULT 100,  -- requests per minute
    retention_days INTEGER,  -- NULL for unlimited
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API & Webhooks
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    events TEXT[] NOT NULL,  -- ['job.completed', 'job.failed', etc.]
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics & Events
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_generation_jobs_status ON generation_jobs(status);
CREATE INDEX idx_usage_records_user_date ON usage_records(user_id, date);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_created_at ON events(created_at);
```

### 6.2 Redis Data Structures

```
# Session Storage
session:{token} → {user_id, expires_at, data}
TTL: 24 hours

# Rate Limiting
rate_limit:{user_id}:{endpoint}:{minute} → request_count
TTL: 60 seconds

# Cache
cache:user:{user_id} → user_data
cache:dataset:{dataset_id} → dataset_metadata
TTL: Varies (5-60 minutes)

# Celery Queue
celery-task-meta-{task_id} → {status, result, traceback}
celery → [pending task IDs]

# Distributed Locks
lock:generation:{user_id} → {locked_at, worker_id}
TTL: 15 minutes

# Real-time Progress
progress:{job_id} → {percent, message, updated_at}
TTL: 1 hour
```

### 6.3 MongoDB (Utility Data Store)

MongoDB is used as a secondary database for storing utility data such as logs, analytics events, and usage tracking. This separation allows for better performance optimization and automatic TTL-based cleanup.

**Connection:**
- URI: `mongodb://mongodb:27017`
- Database: `synthesize_utility`
- Driver: Motor (async), PyMongo (sync)

**Collections:**

```javascript
// Activity Logs - Tracks user activities (login, dataset creation, downloads, etc.)
db.activity_logs {
  _id: ObjectId,
  user_id: String (UUID),
  activity_type: String,    // login, logout, dataset_create, dataset_download, etc.
  entity_id: String,        // Related entity UUID
  entity_type: String,      // dataset, job, api_key, etc.
  metadata: Object,         // Additional context data
  ip_address: String,
  user_agent: String,
  timestamp: Date
}
Indexes:
  - { user_id: 1, timestamp: -1 }
  - { activity_type: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 90 days

// Usage Tracking - Tracks API calls, rows generated, storage used
db.usage_tracking {
  _id: ObjectId,
  user_id: String,
  organization_id: String,  // Optional
  metric: String,           // rows_generated, api_call, storage_used, dataset_created
  value: Number,
  metadata: Object,
  timestamp: Date
}
Indexes:
  - { user_id: 1, metric: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 365 days

// Analytics Events - Business intelligence and user behavior tracking
db.analytics_events {
  _id: ObjectId,
  user_id: String,          // Optional (for anonymous events)
  event_name: String,       // page_view, feature_used, button_click, etc.
  properties: Object,
  session_id: String,
  timestamp: Date
}
Indexes:
  - { event_name: 1, timestamp: -1 }
  - { user_id: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 180 days

// API Request Logs - Detailed API call logging
db.api_logs {
  _id: ObjectId,
  user_id: String,
  api_key_id: String,
  endpoint: String,
  method: String,
  status_code: Number,
  response_time_ms: Number,
  ip_address: String,
  timestamp: Date
}
Indexes:
  - { user_id: 1, timestamp: -1 }
  - { endpoint: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 30 days

// Deletion Reminders - Tracks scheduled dataset deletions
db.deletion_reminders {
  _id: ObjectId,
  dataset_id: String,
  user_id: String,
  user_email: String,
  dataset_name: String,
  deletion_date: Date,
  reminder_sent: Boolean,
  reminder_sent_at: Date,
  created_at: Date
}
Indexes:
  - { deletion_date: 1, reminder_sent: 1 }
  - { user_id: 1 }

// Error Logs - Application errors and exceptions
db.error_logs {
  _id: ObjectId,
  service: String,          // api, celery, web, admin
  level: String,            // error, warning, critical
  message: String,
  stack_trace: String,
  context: Object,
  timestamp: Date
}
Indexes:
  - { service: 1, level: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 30 days

// Webhook Logs - Webhook delivery attempts
db.webhook_logs {
  _id: ObjectId,
  webhook_id: String,
  event_type: String,
  payload: Object,
  response_status: Number,
  response_body: String,
  success: Boolean,
  attempt_count: Number,
  timestamp: Date
}
Indexes:
  - { webhook_id: 1, timestamp: -1 }
  - { timestamp: 1 } with TTL: 30 days
```

**TTL Indexes:**
MongoDB TTL (Time-To-Live) indexes automatically delete documents after a specified time:
- Activity logs: 90 days retention
- API logs: 30 days retention
- Error logs: 30 days retention
- Webhook logs: 30 days retention
- Analytics events: 180 days retention
- Usage tracking: 365 days retention

**Why MongoDB for Utility Data:**
1. **Write-Heavy Workloads**: Log data requires high write throughput
2. **Flexible Schema**: Log formats can evolve without migrations
3. **TTL Indexes**: Automatic cleanup of old data
4. **Aggregation Pipeline**: Powerful analytics queries
5. **Separation of Concerns**: Keeps PostgreSQL lean for transactional data

---

## 7. Security Architecture

### 7.1 Authentication & Authorization

**Multi-Layer Security:**

```
Layer 1: Network Security
├── TLS 1.3 encryption
├── Cloudflare DDoS protection
└── Rate limiting at proxy level

Layer 2: Application Security
├── JWT token authentication
├── Google OAuth 2.0 integration
├── Password hashing (bcrypt, cost=12)
└── CSRF protection

Layer 3: API Security
├── API key authentication
├── Rate limiting per tier
├── Request signature verification
└── Input validation (Pydantic)

Layer 4: Data Security
├── Encrypted data at rest (AES-256)
├── Database SSL connections
├── Secure file permissions
└── Audit logging
```

### 7.2 Authentication Flow Security

**JWT Token Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid",
    "email": "user@example.com",
    "tier": "professional",
    "exp": 1704096000,
    "iat": 1704009600
  },
  "signature": "..."
}
```

**Security Measures:**
- Token expiration: 24 hours
- Refresh token rotation
- Session invalidation on logout
- Redis-based session store
- XSS protection via HttpOnly cookies
- CSRF tokens for state-changing operations

### 7.3 Data Protection

**Encryption:**
- TLS 1.3 for all client-server communication
- AES-256 encryption for sensitive data at rest
- Database connection SSL mode: `require`
- Encrypted backups

**Access Control:**
- Role-Based Access Control (RBAC)
- Row-Level Security (RLS) in PostgreSQL
- API key scoping
- OAuth scope validation

**Privacy Compliance:**
- GDPR data export functionality
- CCPA compliance features
- Cookie consent management
- Data anonymization in analytics
- Right to deletion implementation

---

## 8. Deployment Architecture

### 8.1 Environment Overview

```
┌─────────────────────────────────────────────────┐
│           Development Environment                │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  Local Docker Compose                   │    │
│  │  - Hot reload enabled                   │    │
│  │  - Debug mode                           │    │
│  │  - Local volume mounts                  │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│            Staging Environment                   │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  Single VM (4 CPU, 16GB RAM)           │    │
│  │  - Docker Compose                      │    │
│  │  - Mirrors production config           │    │
│  │  - Reduced scale                       │    │
│  │  - Test data only                      │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│           Production Environment                 │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  VM Cluster (3+ VMs)                   │    │
│  │  - Docker Swarm / Kubernetes           │    │
│  │  - Load balancing (Nginx/HAProxy)      │    │
│  │  - Auto-scaling                        │    │
│  │  - High availability                   │    │
│  │  - Monitoring & logging                │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 8.2 Production Infrastructure

**VM Cluster Configuration:**

```
┌──────────────────────────────────────────┐
│          Load Balancer VM                 │
│  - Nginx                                  │
│  - SSL/TLS termination                    │
│  - Request routing                        │
│  - 2 CPU, 4GB RAM                         │
└──────────────┬───────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼────┐  ┌──▼────┐
│ App   │  │ App   │  │ App   │
│ VM 1  │  │ VM 2  │  │ VM 3  │
│       │  │       │  │       │
│ 4 CPU │  │ 4 CPU │  │ 4 CPU │
│ 16 GB │  │ 16 GB │  │ 16 GB │
│       │  │       │  │       │
│ - Frontend  │  - Frontend  │  - Frontend  │
│ - Backend   │  - Backend   │  - Backend   │
│ - Celery    │  - Celery    │  - Celery    │
└─────────────┴─────────────┴──────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼────┐  ┌──▼────┐
│ DB    │  │ Redis │  │ Storage│
│ VM    │  │ VM    │  │ VM     │
│       │  │       │  │        │
│ 8 CPU │  │ 2 CPU │  │ 4 CPU  │
│ 32 GB │  │ 8 GB  │  │ 64 GB  │
│       │  │       │  │ + Disk │
│PostgreSQL│ │ Redis │  │ NFS/   │
│ Master  │  │ Cluster│  │ Local  │
└─────────┘  └────────┘  └────────┘
```

### 8.3 Scaling Strategy

**Horizontal Scaling:**
- Frontend: Scale to 10+ replicas
- Backend: Scale to 10+ replicas
- Celery Workers: Scale to 20+ workers
- Database: Read replicas (1 master, N replicas)

**Auto-Scaling Triggers:**
- CPU usage > 70% for 5 minutes
- Memory usage > 80%
- Queue depth > 100 jobs
- Response time > 2 seconds

**Load Balancing Algorithm:**
- Round-robin for frontend/backend
- Least connections for database reads
- Priority queue for Celery tasks

### 8.4 Backup & Disaster Recovery

**Backup Strategy:**
```
Daily Backups:
├── PostgreSQL full backup (3 AM UTC)
├── Redis snapshot (every 6 hours)
└── File storage incremental backup

Retention:
├── Daily backups: 7 days
├── Weekly backups: 4 weeks
└── Monthly backups: 12 months

Recovery Time Objective (RTO): 1 hour
Recovery Point Objective (RPO): 24 hours
```

**Disaster Recovery Plan:**
1. Detect failure via monitoring
2. Promote read replica to master (DB)
3. Redirect traffic to standby VMs
4. Restore from latest backup
5. Verify data integrity
6. Resume normal operations

---

## 9. Technology Stack

### 9.1 Complete Stack Overview

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** |
| Framework | Next.js | 15+ | React framework with SSR/SSG |
| UI Library | React | 19+ | Component-based UI with Compiler |
| Styling | TailwindCSS | 3.4+ | Utility-first CSS |
| Components | ShadCN UI | Latest | Pre-built components on Radix |
| State | TanStack Query | 5+ | Server state management |
| Tables | TanStack Table | 8+ | Advanced data tables |
| Router | TanStack Router | 1.x | Type-safe routing |
| Client State | Zustand | 5+ | Lightweight state |
| HTTP Client | Axios | 1.7+ | API requests |
| Language | TypeScript | 5.7+ | Type safety |
| **Backend** |
| Framework | FastAPI | 0.115+ | Python web framework |
| Language | Python | 3.11+ | Programming language |
| Validation | Pydantic | 2.10+ | Data validation |
| ORM | SQLAlchemy | 2.0+ | Database ORM |
| Migrations | Alembic | 1.14+ | Schema migrations |
| Task Queue | Celery | 5.4+ | Async job processing |
| Auth | JWT + OAuth2 | Latest | Authentication |
| **Database** |
| Primary DB | PostgreSQL | 15+ | Relational database |
| Utility DB | MongoDB | 7+ | Logs, analytics, usage tracking |
| Cache | Redis | 7+ | Caching & queuing |
| **Storage** |
| File Storage | Local VM | - | Dataset files |
| Backup | rsync/Restic | Latest | Backup solution |
| **External Services** |
| LLM | Anthropic Claude | Latest | AI text generation |
| Payment | PayPal | Latest | Payment processing |
| Payment | Razorpay | Latest | Payment (India) |
| OAuth | Google OAuth2 | Latest | Social login |
| Email | Nodemailer | Latest | Email delivery |
| Analytics | Google Analytics | GA4 | User analytics |
| SEO | Google Search Console | Latest | SEO monitoring |
| **Infrastructure** |
| Containers | Docker | 24+ | Containerization |
| Orchestration | Docker Compose | 2+ | Container management |
| Proxy | Nginx | 1.24+ | Reverse proxy |
| CDN | Cloudflare | Latest | Content delivery |
| SSL | Let's Encrypt | Latest | SSL certificates |
| **Monitoring** |
| Logs | ELK Stack | 8+ | Log aggregation |
| Metrics | Custom | - | Performance metrics |
| Uptime | UptimeRobot | - | Service monitoring |

### 9.2 Development Tools

| Tool | Purpose |
|------|---------|
| VS Code | Primary IDE |
| Git | Version control |
| GitHub | Code repository |
| Docker Desktop | Local containerization |
| Postman | API testing |
| DBeaver | Database management |
| Redis Commander | Redis management |

---

## 10. Integration Architecture

### 10.1 External Service Integrations

**Anthropic Claude API:**
```python
# LLM Integration
import anthropic

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def analyze_request(user_request: str) -> Dict:
    response = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Analyze this data request: {user_request}"
        }]
    )
    return parse_llm_response(response)
```

**Google OAuth Integration:**
```python
# OAuth Flow
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

**PayPal Integration:**
```python
# Payment Processing
import paypalrestsdk

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_subscription(user, plan):
    billing_plan = paypalrestsdk.BillingPlan.find(plan.paypal_plan_id)
    # Create subscription agreement
```

**Razorpay Integration:**
```python
# Payment Processing (India)
import razorpay

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_subscription(user, plan):
    subscription = client.subscription.create({
        "plan_id": plan.razorpay_plan_id,
        "customer_notify": 1,
        "total_count": 12,  # Monthly for 1 year
    })
```

**Nodemailer Integration:**
```javascript
// Email Service (Node.js microservice)
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: process.env.SMTP_PORT,
    secure: true,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASSWORD
    }
});

async function sendEmail(to, subject, html) {
    await transporter.sendMail({
        from: '"Synthesize.io" <noreply@synthesize.io>',
        to: to,
        subject: subject,
        html: html
    });
}
```

**Google Analytics Integration:**
```typescript
// Frontend Analytics
import ReactGA from 'react-ga4';

ReactGA.initialize(process.env.NEXT_PUBLIC_GA_ID);

// Track page views
export const trackPageView = (url: string) => {
    ReactGA.send({ hitType: "pageview", page: url });
};

// Track custom events
export const trackEvent = (category: string, action: string, label?: string) => {
    ReactGA.event({
        category: category,
        action: action,
        label: label
    });
};
```

**Google Search Console Integration:**
```python
# Backend SEO Monitoring
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)

service = build('searchconsole', 'v1', credentials=credentials)

def get_search_analytics(site_url: str, start_date: str, end_date: str):
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query', 'page'],
        'rowLimit': 1000
    }
    response = service.searchanalytics().query(
        siteUrl=site_url, body=request
    ).execute()
    return response.get('rows', [])
```

### 10.2 API Endpoints

**RESTful API Structure:**

```
/api/v1
├── /auth
│   ├── POST   /register
│   ├── POST   /login
│   ├── POST   /logout
│   ├── POST   /refresh
│   ├── GET    /google/authorize
│   ├── GET    /google/callback
│   └── POST   /reset-password
├── /users
│   ├── GET    /me
│   ├── PUT    /me
│   └── DELETE /me
├── /generate
│   ├── POST   /             # Create generation request
│   ├── POST   /{id}/approve # Approve sample
│   └── GET    /{id}/sample  # Get LLM sample
├── /datasets
│   ├── GET    /             # List datasets
│   ├── GET    /{id}         # Get dataset details
│   ├── GET    /{id}/download # Download dataset
│   ├── DELETE /{id}         # Delete dataset
│   └── POST   /{id}/share   # Share dataset
├── /jobs
│   ├── GET    /{id}         # Get job status
│   └── POST   /{id}/cancel  # Cancel job
├── /billing
│   ├── GET    /subscriptions
│   ├── POST   /subscribe
│   ├── PUT    /subscription
│   ├── DELETE /subscription
│   ├── GET    /invoices
│   └── GET    /usage
├── /api-keys
│   ├── GET    /             # List API keys
│   ├── POST   /             # Create API key
│   └── DELETE /{id}         # Revoke API key
├── /webhooks
│   ├── GET    /             # List webhooks
│   ├── POST   /             # Create webhook
│   ├── PUT    /{id}         # Update webhook
│   └── DELETE /{id}         # Delete webhook
└── /admin
    ├── GET    /stats
    ├── GET    /users
    └── GET    /system-health
```

---

## 11. Scalability & Performance

### 11.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load Time | < 2s | 95th percentile |
| API Response Time | < 500ms | 95th percentile |
| Data Generation | 1GB in 60s | Average |
| Concurrent Users | 1,000+ | Simultaneous |
| Dataset Size Limit | 10GB | Per dataset |
| Uptime | 99.9% | Monthly |

### 11.2 Caching Strategy

**Multi-Layer Caching:**

```
Layer 1: Browser Cache
├── Static assets (JS, CSS, images): 1 year
└── HTML pages: 5 minutes

Layer 2: CDN Cache (Cloudflare)
├── Static assets: 1 year
├── API responses (GET): 5 minutes
└── Dynamic content: No cache

Layer 3: Redis Cache
├── User sessions: 24 hours
├── User profiles: 1 hour
├── Dataset metadata: 30 minutes
├── LLM responses: 1 day
└── Usage stats: 5 minutes

Layer 4: Application Cache
├── Configuration: Until restart
├── Schema templates: Until restart
└── In-memory calculations: Request scope
```

### 11.3 Database Optimization

**Query Optimization:**
- Indexed columns for frequent queries
- Materialized views for analytics
- Connection pooling (max 100 connections)
- Query result caching
- Pagination for large result sets

**Read Replicas:**
```
Master DB (Write)
    │
    ├──► Read Replica 1 (Analytics queries)
    ├──► Read Replica 2 (API reads)
    └──► Read Replica 3 (Background jobs)
```

### 11.4 Rate Limiting

**Rate Limits by Tier:**

| Tier | API Rate Limit | Generation Jobs | Concurrent Jobs |
|------|----------------|-----------------|-----------------|
| Starter | 100/min | Unlimited | 2 |
| Professional | 500/min | Unlimited | 5 |
| Business | 2,000/min | Unlimited | 10 |
| Enterprise | 10,000/min | Unlimited | 50 |

**Implementation:**
```python
# Redis-based rate limiting
from redis import Redis
from fastapi import HTTPException

async def rate_limit(user_id: str, tier: str):
    key = f"rate_limit:{user_id}:{current_minute()}"
    current = redis.incr(key)
    redis.expire(key, 60)
    
    limit = TIER_LIMITS[tier]
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **LLM** | Large Language Model (e.g., Claude, GPT) |
| **SSR** | Server-Side Rendering |
| **SSG** | Static Site Generation |
| **CSR** | Client-Side Rendering |
| **JWT** | JSON Web Token |
| **RBAC** | Role-Based Access Control |
| **CORS** | Cross-Origin Resource Sharing |
| **CSRF** | Cross-Site Request Forgery |
| **XSS** | Cross-Site Scripting |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |

### B. References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Next.js Documentation: https://nextjs.org/docs
- Docker Documentation: https://docs.docker.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Redis Documentation: https://redis.io/documentation
- TanStack Query: https://tanstack.com/query/
- Google OAuth2: https://developers.google.com/identity/protocols/oauth2
- PayPal API: https://developer.paypal.com/
- Razorpay API: https://razorpay.com/docs/api/

---

**Document Status:** Final  
**Last Updated:** December 30, 2025  
**Next Review:** March 30, 2026

---

## 12. Implementation Guide & Quick Start

### 12.1 Complete Data Generation Workflow with LLM

**User Journey:**
```
1. User: "I need customer data for testing"
   ↓
2. POST /api/v1/ai/refine (FastAPI + LLM, 2s)
   Returns: Structured schema with columns/types
   ↓
3. POST /api/v1/ai/generate-sample (FastAPI + LLM, 3s)
   Returns: 10 sample rows for review
   ↓
4. User reviews sample in UI:
   ✓ "Looks good!" or "Modify email format"
   ↓
5. POST /api/v1/ai/approve-and-generate (FastAPI, 100ms)
   Queues job to Celery, returns job_id
   ↓
6. Celery Worker picks up task (Data Factory, 5 min)
   Generates 100K rows based on approved sample
   ↓
7. Webhook/Email notification sent
   User downloads dataset
```

**Key Implementation Files:**
- `apps/api/app/services/llm_service.py` - ✨ Anthropic Claude integration
- `apps/api/app/services/data_factory.py` - Data generation algorithms
- `apps/api/app/tasks/generation.py` - Celery background tasks
- `apps/api/app/examples/llm_usage.py` - Complete usage examples

### 12.2 Development Setup

```bash
# 1. Install dependencies
pnpm install

# 2. Start databases
docker-compose up -d postgres redis

# 3. Setup Python (use 3.13, not 3.14)
cd apps/api
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add ANTHROPIC_API_KEY=sk-ant-...

# 5. Run services
uvicorn app.main:app --reload --port 8000  # Terminal 1
celery -A app.celery_app worker --loglevel=info  # Terminal 2
pnpm dev  # Terminal 3
```

### 12.3 Production Deployment

```bash
# Full stack with all services
./scripts/start-full-stack.sh

# Services running:
# ✅ postgres:5432 - Database
# ✅ redis:6379 - Cache + Queue
# ✅ web:3000 - User Portal
# ✅ admin:3001 - Admin Portal
# ✅ api:8000 - FastAPI Backend
# ✅ celery-worker x2 - Background Workers
# ✅ celery-beat - Task Scheduler
# ✅ nginx:80/443 - Reverse Proxy

# Scale workers for production
docker-compose up -d --scale celery-worker=10
```

---

## 13. Architecture Separation Details

### 13.1 Component Responsibilities

| Component | FastAPI (Brain 🧠) | Celery Workers (Muscles 💪) | Data Factory (Algorithm 🏭) | LLM Service (AI 🤖) |
|-----------|:------------------:|:---------------------------:|:---------------------------:|:-------------------:|
| **HTTP Request Handling** | ✅ | ❌ | ❌ | ❌ |
| **Authentication** | ✅ | ❌ | ❌ | ❌ |
| **Request Validation** | ✅ | ❌ | ❌ | ❌ |
| **Job Queuing** | ✅ | ❌ | ❌ | ❌ |
| **Data Generation (Bulk)** | ❌ | ✅ | ✅ | ❌ |
| **Sample Generation (10-50 rows)** | ✅ | ❌ | ❌ | ✅ |
| **File I/O (Large)** | ❌ | ✅ | ✅ | ❌ |
| **Email Sending** | ❌ | ✅ | ❌ | ❌ |
| **Scheduled Tasks** | ❌ | ✅ (Beat) | ❌ | ❌ |
| **Business Logic** | ❌ | ❌ | ✅ | ❌ |
| **Pattern Analysis** | ❌ | ❌ | ✅ | ✅ |
| **Natural Language Processing** | ❌ | ❌ | ❌ | ✅ |
| **Response Time** | < 200ms | 2-10 min | N/A | 2-5s |
| **Scaling Strategy** | Vertical | Horizontal (2-100) | N/A | API Limit |

### 13.2 Data Flow Example

**Complete User Journey: "I need customer data for testing"**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Input (Natural Language)                                │
│    "I need customer data for testing"                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. POST /api/v1/ai/refine (FastAPI + LLM, 2s)                  │
│    LLMService.refine_request()                                  │
│    ├─> Claude analyzes intent                                   │
│    └─> Returns structured schema                                │
│        {                                                         │
│          "columns": [                                            │
│            {"name": "customer_id", "type": "uuid"},             │
│            {"name": "full_name", "type": "full_name"},          │
│            {"name": "email", "type": "email"},                  │
│            {"name": "phone", "type": "phone"},                  │
│            {"name": "signup_date", "type": "date"}              │
│          ]                                                       │
│        }                                                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. POST /api/v1/ai/generate-sample (FastAPI + LLM, 3s)         │
│    LLMService.generate_sample_data(10 rows)                     │
│    Returns: 10 realistic sample rows for user review            │
│    [                                                             │
│      {                                                           │
│        "customer_id": "550e8400-e29b-41d4-a716-446655440000",  │
│        "full_name": "Sarah Johnson",                            │
│        "email": "sarah.johnson@email.com",                      │
│        "phone": "+1-555-0123",                                  │
│        "signup_date": "2024-03-15"                              │
│      }, ...                                                      │
│    ]                                                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. User Reviews Sample in UI                                    │
│    ✓ "Looks good!" or "Modify email format"                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. POST /api/v1/ai/approve-and-generate (FastAPI, 100ms)       │
│    FastAPI validates, creates job, queues to Celery             │
│    Returns: {"job_id": "abc123", "status": "queued"}           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼ Queue via Redis
┌─────────────────────────────────────────────────────────────────┐
│ 6. Celery Worker Picks Task (5 min)                            │
│    generate_dataset(job_id="abc123", schema={...}, count=100K) │
│    ├─> DataFactory.analyze_sample(approved_sample)             │
│    ├─> DataFactory.generate_dataset(100,000 rows)              │
│    ├─> Save to /data/generated/abc123.csv                      │
│    └─> Update job status to "completed"                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Notification Worker (Async)                                  │
│    send_email(user.email, "Dataset ready!")                     │
│    trigger_webhook(user.webhook_url, {job_id, status})         │
└─────────────────────────────────────────────────────────────────┘
```

### 13.3 System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║              SYNTHESIZE.IO ARCHITECTURE                          ║
║         FastAPI as Brain, Celery as Muscles                      ║
╚══════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────┐
│                       USER LAYER                                │
├────────────┬────────────┬────────────┬─────────────────────────┤
│ Web App    │ Admin      │ API Client │ External                 │
│ :3000      │ :3001      │ (Mobile)   │ Integrations            │
└────────────┴────────────┴────────────┴─────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API LAYER (BRAIN 🧠)                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │           FastAPI Backend :8000                           │ │
│  │  ┌─────────────┬──────────────┬────────────────┐         │ │
│  │  │ HTTP Routes │ Auth & OAuth │ Validation     │         │ │
│  │  │ /auth       │ JWT + Google │ Pydantic       │         │ │
│  │  │ /datasets   │              │                │         │ │
│  │  │ /generation │              │                │         │ │
│  │  └─────────────┴──────────────┴────────────────┘         │ │
│  │  Response Time: < 200ms (Queues work, no processing)     │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                         │ Queue Tasks via Redis
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MESSAGE QUEUE (REDIS)                           │
│  ┌────────────┬─────────────┬──────────────┐                   │
│  │generation:0│notifications│   cleanup    │                   │
│  │Priority:   │Priority:    │Priority: LOW │                   │
│  │   HIGH     │   NORMAL    │              │                   │
│  └────────────┴─────────────┴──────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                         │ Workers Pick Tasks
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 WORKER LAYER (MUSCLES 💪)                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         Celery Workers (Scale 2-100)                      │ │
│  │  ┌───────────┬───────────┬───────────┬──────────┐        │ │
│  │  │ Worker #1 │ Worker #2 │ Worker #3 │ Worker N │        │ │
│  │  │ Concur: 4 │ Concur: 4 │ Concur: 4 │ ...      │        │ │
│  │  │ Generate  │ Export    │ Send      │          │        │ │
│  │  │ 100K rows │ CSV       │ Email     │          │        │ │
│  │  └───────────┴───────────┴───────────┴──────────┘        │ │
│  │  Processing Time: 2-10 minutes                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         Celery Beat (Scheduler)                           │ │
│  │  🕐 Hourly: cleanup_old_datasets()                       │ │
│  │  🕐 30min:  calculate_usage_stats()                      │ │
│  │  🕐 Daily:  archive_old_jobs()                           │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                         │ Uses Business Logic
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
│  ┌──────────────────┐  ┌────────────────────────────┐          │
│  │ Data Factory 🏭  │  │  LLM Service 🤖            │          │
│  │                  │  │                            │          │
│  │ • analyze_sample │  │ • refine_request           │          │
│  │ • generate_data  │  │ • generate_sample          │          │
│  │ • validate       │  │ • analyze_patterns         │          │
│  │ • apply_dist.    │  │ • suggest_improvements     │          │
│  │                  │  │                            │          │
│  │ Pure logic       │  │ Anthropic Claude API       │          │
│  └──────────────────┘  └────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                         │ Reads/Writes
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────┬──────────┬──────────────┬───────────────┐        │
│  │PostgreSQL│  Redis   │ File Storage │ Monitoring    │        │
│  │  :5432   │  :6379   │/data/gener.  │ (Flower:5555) │        │
│  │          │          │              │               │        │
│  │ • Users  │ •Sessions│ •dataset.csv │ • Worker stat │        │
│  │ • Jobs   │ • Cache  │ •dataset.json│ • Queue depth │        │
│  │ • Datasets│•Progress│ •dataset.sql │ • Task history│        │
│  │ • Billing│•Limits   │              │               │        │
│  └──────────┴──────────┴──────────────┴───────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 13.4 Key Separation Principles

✅ **FastAPI (Brain) - Responsibilities:**
- HTTP request handling only
- Authentication & authorization
- Request validation
- Job queuing (delegate to Celery)
- Response time: < 200ms

❌ **FastAPI (Brain) - Does NOT:**
- Generate data (no loops creating rows)
- File I/O operations
- Send emails
- Long computations
- Heavy CPU/memory tasks

✅ **Celery Workers (Muscles) - Responsibilities:**
- Data generation (bulk processing)
- File conversions & exports
- Email/webhook delivery
- Scheduled maintenance tasks
- Independent horizontal scaling

✅ **Data Factory (Algorithm) - Responsibilities:**
- Pure business logic (no dependencies)
- Pattern analysis
- Data synthesis algorithms
- Constraint validation
- Testable in isolation

✅ **LLM Service (AI Assistant) - Responsibilities:**
- Natural language understanding
- Schema refinement
- Sample generation (10-50 rows)
- Pattern analysis assistance
- NOT used for bulk generation (cost-prohibitive)

---

## 14. Docker Services Reference

### 14.1 Core Infrastructure
| Service | Container | Port | Role | Scaling |
|---------|-----------|------|------|---------|
| **postgres** | synthesize-postgres | 5432 | Database | 1 instance |
| **redis** | synthesize-redis | 6379 | Cache + Queue | 1 instance |

### 14.2 Application Services
| Service | Container | Port | Role | Scaling |
|---------|-----------|------|------|---------|
| **web** | synthesize-web | 3000 | User Portal | 1-4 instances |
| **admin** | synthesize-admin | 3001 | Admin Portal | 1 instance |
| **api** | synthesize-api | 8000 | FastAPI Backend | 2-4 instances |

### 14.3 Background Processing
| Service | Container | Port | Role | Scaling |
|---------|-----------|------|------|---------|
| **celery-worker** | synthesize-celery-worker | - | Background Jobs | 2-100 instances |
| **celery-beat** | synthesize-celery-beat | - | Task Scheduler | 1 instance |

### 14.4 Monitoring & Management (NEW ✨)
| Service | Container | Port | Role | Scaling |
|---------|-----------|------|------|---------|
| **flower** | synthesize-flower | 5555 | Celery Monitoring | 1 instance |
| **pgadmin** | synthesize-pgadmin | 5050 | DB Management | 1 instance |

### 14.5 Reverse Proxy
| Service | Container | Port | Role | Scaling |
|---------|-----------|------|------|---------|
| **nginx** | synthesize-nginx | 80/443 | Reverse Proxy | 1 instance |

### 14.6 Service Dependencies

```
┌────────────────┐
│   Nginx :80    │  ← Entry point
└───────┬────────┘
        │
    ┌───┴───┬───────┬──────────┐
    │       │       │          │
┌───▼──┐ ┌──▼──┐ ┌─▼────┐  ┌──▼───────┐
│ Web  │ │Admin│ │ API  │  │ Flower   │
│ :3000│ │:3001│ │:8000 │  │ :5555    │
└──┬───┘ └──┬──┘ └─┬────┘  └──┬───────┘
   │        │      │           │
   └────────┴──────┼───────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼─────┐      ┌──────▼─────┐
    │ Postgres │      │   Redis    │
    │  :5432   │      │   :6379    │
    └──────────┘      └──┬─────┬───┘
                         │     │
                    ┌────▼─┐  │
                    │Celery│  │
                    │Worker├──┘
                    └──────┘
                    ┌──────┐
                    │Celery│
                    │ Beat │
                    └──────┘
```

---

## 15. Documentation Index

**Primary Documentation (in `/docs` folder):**
- ✅ `Architecture.md` - **This file** - Complete system architecture with LLM, Celery, Docker services
- ✅ `SRS.md` - Software Requirements Specification
- ✅ `Whitepaper.md` - Platform overview & vision
- ✅ `CompetitorAnalysis.md` - Market analysis

**Code Examples:**
- ✅ `apps/api/app/examples/celery_integration.py` - FastAPI + Celery integration patterns
- ✅ `apps/api/app/examples/llm_usage.py` - LLM Service usage examples

**Integration Tests:**
- ✅ `apps/api/test_celery.py` - Celery integration test suite

**Deployment Scripts:**
- ✅ `scripts/start-full-stack.sh` - Start all services with Docker
- ✅ `scripts/test-services.sh` - Test service connectivity

---

**Status:** ✅ Complete - Architecture + LLM + Celery + Monitoring Services  
**Last Updated:** December 30, 2025


https://chatpilot-template.webflow.io/