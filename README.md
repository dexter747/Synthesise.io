<div align="center">

# Synthesize.io

### AI-Powered Synthetic Data Generation Platform

Generate high-quality, privacy-safe synthetic datasets on demand — with a web
app, admin console, and an API backend with async generation workers.

![Status](https://img.shields.io/badge/status-archived-orange)
![License](https://img.shields.io/badge/license-MIT-blue)
![Web](https://img.shields.io/badge/web-Next.js-000000)
![API](https://img.shields.io/badge/api-FastAPI%20%2B%20Celery-009688)

</div>

---

> [!NOTE]
> **Archived project, open-sourced as-is under MIT.** Credentials were removed and
> internal business/marketing strategy docs stripped. Copy `.env.example` to
> configure your own instance.

## Overview

Synthesize.io lets teams generate synthetic data that preserves the statistical
shape of real data without exposing sensitive records — useful for testing, ML
training, and sharing data safely. It's a monorepo with a customer web app, an
admin console, and a Python API with background workers.

## Features

- 🧪 **Synthetic data generation** — configurable generation jobs (the "Data Factory")
- ⚙️ **Async workers** — long-running generation via Celery
- 👤 **Auth** — email + Google OAuth
- 💳 **Billing & quotas** — usage quotas and payment integration
- 🛠️ **Admin console** — manage users, jobs, and platform settings
- 🔑 **API keys** — programmatic access for data generation

## Monorepo Layout

```
Synthesise.io/
├── apps/
│   ├── web/     # Customer web app (Next.js)
│   ├── admin/   # Admin console
│   └── api/     # FastAPI backend + Celery workers
├── docker/      # Dockerfiles per service
└── docs/        # Architecture, setup, API, testing docs
```

## Tech Stack

- **Web / Admin:** Next.js, React, TypeScript, Tailwind CSS
- **API:** Python, FastAPI, Celery, SQLAlchemy
- **Infra:** Docker / docker-compose
- **Auth & Billing:** Google OAuth, Stripe

## Getting Started

> Requires **Node.js 18+**, **Python 3.10+**, and **Docker**.

```bash
git clone https://github.com/dexter747/Synthesise.io.git
cd Synthesise.io
cp .env.example .env        # fill in your values
npm install
npm run docker:services:up  # Postgres/Redis, etc.
npm run dev                 # web + admin + api + celery
```

See [`docs/`](./docs) for architecture, setup, API, and testing guides.

## License

Released under the [MIT License](./LICENSE) © 2026 Maitreya Kulkarni.
