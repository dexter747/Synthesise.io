# Data Factory Integration Plan
## Analysis of Synth2size-Setu-Backend

**Date**: January 20, 2026  
**Status**: Integration Planning Phase

---

## 📋 Executive Summary

The Synth2size-Setu-Backend is a **production-grade synthetic data generation engine** built with FastAPI, Celery, and Redis. It supports three generation methods (Faker, Synthcity ML, and LLM) and has been stress-tested for 100+ concurrent users.

### Key Strengths
- ✅ Production-ready with connection limiting & rate limiting
- ✅ Asynchronous task processing via Celery
- ✅ Supports 100K rows, 100 columns per generation
- ✅ Health monitoring with CPU/memory awareness
- ✅ Comprehensive test coverage (52 unit tests, 11 integration tests)
- ✅ Multiple output formats (CSV, JSON, Parquet, Excel)

### Integration Needs
- 🔄 User authentication & authorization
- 🔄 Quota system integration
- 🔄 Usage tracking per user/organization
- 🔄 Billing integration
- 🔄 Database persistence for generated datasets
- 🔄 API key management

---

## 🏗️ Current Architecture Analysis

### 1. Data Generation Engines

#### **Faker Engine** (`app/services/faker_service.py`)
- **Purpose**: Generate realistic fake data using Faker library
- **Providers**: 25+ categories (address, bank, company, internet, etc.)
- **Capabilities**:
  - 300+ provider methods available
  - Locale support (en_US, en_GB, de_DE, etc.)
  - Unique value constraints
  - Custom parameters per column
  - Null value probability control
  - Batch processing (default 1000 rows/batch)

**Example Request**:
```json
{
  "columns": [
    {"name": "full_name", "provider": "name"},
    {"name": "email", "provider": "email", "unique": true},
    {"name": "city", "provider": "city"},
    {"name": "age", "provider": "pyint", "params": {"min_value": 18, "max_value": 80}}
  ],
  "num_rows": 10000,
  "locale": "en_US",
  "output_format": "csv"
}
```

#### **Synthcity Engine** (`app/services/synthcity_service.py`)
- **Purpose**: ML-based synthetic data from real datasets
- **Models Available**:
  - CTGAN (Conditional Tabular GAN)
  - TVAE (Tabular Variational Autoencoder)
  - Bayesian Networks
  - GaussianCopula
  - PrivBayes (differential privacy)
  
- **Process Flow**:
  1. Upload training CSV file
  2. Validate data (columns, dtypes)
  3. Train ML model (epochs configurable)
  4. Generate statistically similar synthetic data
  5. Preserve identifier columns (optional)

**Key Parameters**:
- `epochs`: 100-1000 (training iterations)
- `identifier_columns`: Columns to exclude from training
- Privacy-preserving models available

#### **LLM Engine** (`app/services/llm_service.py`)
- **Purpose**: Creative dataset generation from natural language
- **Provider**: Groq API (Llama 3.3 70B)
- **Use Cases**:
  - Baby names with origins
  - Jokes, quotes, fictional content
  - Custom datasets from text descriptions
  
**Example Prompt**:
> "Generate a list of 30 unique baby names with gender and origin country"

**Creativity Levels**: balanced, creative, precise

---

## 🔧 Current Configuration

### Environment Variables (`.env`)
```bash
# Application
APP_NAME=Synth2Size
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# API
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_POOL_SIZE=20

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_TIME_LIMIT=600  # 10 minutes
CELERY_TASK_SOFT_TIME_LIMIT=300  # 5 minutes

# Groq LLM
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Limits
MAX_ROWS=100000
MAX_COLUMNS=100
DEFAULT_BATCH_SIZE=1000
MAX_UPLOAD_SIZE=52428800  # 50MB

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
MAX_CONCURRENT_CONNECTIONS=100
```

### Current Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/faker/providers` | GET | List all Faker providers |
| `/api/v1/faker/generate` | POST | Generate Faker data (async) |
| `/api/v1/faker/generate/sync` | POST | Generate Faker data (sync, <1000 rows) |
| `/api/v1/synthcity/models` | GET | List ML models |
| `/api/v1/synthcity/validate` | POST | Validate CSV |
| `/api/v1/synthcity/generate` | POST | Train & generate (async) |
| `/api/v1/synthcity/generate-json` | POST | Generate from JSON (async) |
| `/api/v1/llm/status` | GET | Check LLM API status |
| `/api/v1/llm/generate` | POST | Generate LLM data (async) |
| `/api/v1/llm/generate/sync` | POST | Generate LLM data (sync) |
| `/api/v1/tasks/{task_id}` | GET | Get task status |
| `/api/v1/tasks/{task_id}/download` | GET | Download result |
| `/api/v1/tasks/{task_id}` | DELETE | Cancel task |
| `/health` | GET | System health check |

---

## 🔗 Integration Strategy

### Phase 1: Authentication & Authorization (Week 1-2)

#### 1.1 Add JWT Authentication Middleware
**File**: `apps/api/app/api/deps.py` (existing dependency injection system)

```python
from fastapi import Depends, HTTPException, Header
from app.services.user_service import UserService
from app.core.auth import verify_token

async def get_current_user(
    authorization: str = Header(...),
    db: DBSession = Depends(get_db)
):
    """Extract user from JWT token"""
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="Invalid user")
    
    return user

async def get_current_organization(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get user's active organization"""
    if not user.current_organization_id:
        raise HTTPException(status_code=400, detail="No active organization")
    
    org_service = OrganizationService(db)
    org = org_service.get_by_id(user.current_organization_id)
    
    if not org or not org.is_active:
        raise HTTPException(status_code=403, detail="Organization inactive")
    
    return org
```

#### 1.2 Protect Data Factory Endpoints
**Files to modify**:
- `Synth2size-Setu-Backend/app/api/v1/endpoints/faker.py`
- `Synth2size-Setu-Backend/app/api/v1/endpoints/synthcity.py`
- `Synth2size-Setu-Backend/app/api/v1/endpoints/llm.py`

**Pattern**:
```python
from app.api.deps import get_current_user, get_current_organization

@router.post("/generate")
async def generate_faker_data(
    request: FakerGenerateRequest,
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: DBSession = Depends(get_db)
):
    # Check quota before generation
    quota_service = QuotaService(db)
    if not quota_service.check_available(org, request.num_rows):
        raise HTTPException(status_code=429, detail="Quota exceeded")
    
    # Generate data...
    # Track usage...
```

### Phase 2: Quota System Integration (Week 2-3)

#### 2.1 Create Quota Checking Service
**File**: `apps/api/app/services/quota_service.py`

```python
class QuotaService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_rows(self, org: Organization) -> int:
        """Calculate available row generation quota"""
        subscription = org.active_subscription
        
        # Monthly row limit based on tier
        tier_limits = {
            "free": 1000,
            "starter": 50000,
            "professional": 500000,
            "business": 2000000,
            "enterprise": 10000000
        }
        
        monthly_limit = tier_limits.get(subscription.tier, 0)
        
        # Get current month usage
        current_usage = self.get_monthly_usage(org.id)
        
        return max(0, monthly_limit - current_usage)
    
    def check_available(self, org: Organization, requested_rows: int) -> bool:
        """Check if org has quota for requested rows"""
        available = self.get_available_rows(org)
        return available >= requested_rows
    
    def consume_quota(
        self, 
        org_id: UUID, 
        user_id: UUID, 
        rows_generated: int,
        generator_type: str,
        dataset_id: UUID
    ):
        """Record quota usage"""
        usage = DatasetUsage(
            organization_id=org_id,
            user_id=user_id,
            dataset_id=dataset_id,
            rows_generated=rows_generated,
            generator_type=generator_type,
            generated_at=datetime.utcnow()
        )
        self.db.add(usage)
        self.db.commit()
```

#### 2.2 Add Usage Tracking Models
**File**: `apps/api/app/models.py`

```python
class DatasetUsage(Base):
    """Track data generation usage for billing/quota"""
    __tablename__ = "dataset_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    
    rows_generated = Column(Integer, nullable=False)
    generator_type = Column(String(50), nullable=False)  # faker, synthcity, llm
    
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_records")
    user = relationship("User", back_populates="usage_records")
    dataset = relationship("Dataset", back_populates="usage_records")
```

#### 2.3 Migration Script
```bash
cd apps/api
alembic revision -m "add_dataset_usage_tracking"
# Edit migration file to create dataset_usage table
alembic upgrade head
```

### Phase 3: Database Integration (Week 3-4)

#### 3.1 Store Generated Datasets
**File**: `apps/api/app/services/generation_service.py` (existing)

**Modifications needed**:
```python
class GenerationService:
    def create_job(
        self,
        user_id: UUID,
        organization_id: UUID,
        generator_type: str,
        config: dict,
        num_rows: int
    ) -> GenerationJob:
        """Create generation job in database"""
        job = GenerationJob(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            dataset_id=None,  # Will be set after generation
            job_type=generator_type,
            status="pending",
            config=config,
            num_rows=num_rows,
            created_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        
        # Trigger Celery task (from Synth2size-Setu-Backend)
        from Synth2size_Setu_Backend.app.tasks import generate_faker_data_task
        
        task = generate_faker_data_task.delay(str(job.id), config)
        
        job.task_id = task.id
        self.db.commit()
        
        return job
    
    def handle_generation_complete(
        self,
        job_id: UUID,
        result_file_path: str,
        rows_generated: int
    ):
        """Called when Celery task completes"""
        job = self.get_job(job_id)
        
        # Create dataset record
        dataset = Dataset(
            id=uuid.uuid4(),
            user_id=job.user_id,
            organization_id=job.organization_id,
            name=f"Generated_{job.job_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description=f"Generated via {job.job_type}",
            schema=job.config.get("columns", []),
            row_count=rows_generated,
            file_path=result_file_path,
            file_size=os.path.getsize(result_file_path),
            created_at=datetime.utcnow()
        )
        self.db.add(dataset)
        
        # Update job
        job.dataset_id = dataset.id
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        
        # Record usage for quota
        quota_service = QuotaService(self.db)
        quota_service.consume_quota(
            org_id=job.organization_id,
            user_id=job.user_id,
            rows_generated=rows_generated,
            generator_type=job.job_type,
            dataset_id=dataset.id
        )
        
        self.db.commit()
```

#### 3.2 File Storage Strategy

**Option A: Local Filesystem** (current approach)
```python
# Store in organized structure
OUTPUT_DIR = "/app/data/generated/"
file_path = f"{OUTPUT_DIR}/{org_id}/{dataset_id}.{format}"
```

**Option B: S3/Cloud Storage** (recommended for production)
```python
import boto3

s3_client = boto3.client('s3')
s3_key = f"datasets/{org_id}/{dataset_id}.csv"
s3_client.upload_file(local_path, settings.S3_BUCKET, s3_key)
```

### Phase 4: API Integration (Week 4-5)

#### 4.1 Create Unified Generation Endpoint
**File**: `apps/api/app/api/v1/endpoints/generation.py`

```python
@router.post("/generate", response_model=GenerationJobResponse)
async def create_generation_job(
    request: GenerationRequest,
    user: CurrentUser,
    org: RequireOrganization,
    db: DBSession
):
    """
    Unified endpoint for all data generation types.
    Delegates to Synth2size-Setu-Backend services.
    """
    # Validate quota
    quota_service = QuotaService(db)
    if not quota_service.check_available(org, request.num_rows):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "QUOTA_EXCEEDED",
                "available_rows": quota_service.get_available_rows(org),
                "requested_rows": request.num_rows
            }
        )
    
    # Create job in database
    generation_service = GenerationService(db)
    job = generation_service.create_job(
        user_id=user.id,
        organization_id=org.id,
        generator_type=request.generator_type,
        config=request.config,
        num_rows=request.num_rows
    )
    
    # Trigger appropriate Celery task based on type
    if request.generator_type == "faker":
        from Synth2size_Setu_Backend.app.tasks.faker_tasks import generate_faker_data_task
        task = generate_faker_data_task.delay(str(job.id), request.config)
    elif request.generator_type == "synthcity":
        from Synth2size_Setu_Backend.app.tasks.synthcity_tasks import generate_synthcity_data_task
        task = generate_synthcity_data_task.delay(str(job.id), request.config)
    elif request.generator_type == "llm":
        from Synth2size_Setu_Backend.app.tasks.llm_tasks import generate_llm_data_task
        task = generate_llm_data_task.delay(str(job.id), request.config)
    
    # Update job with task ID
    job.task_id = task.id
    db.commit()
    
    return GenerationJobResponse(
        job_id=job.id,
        task_id=task.id,
        status="pending",
        message="Generation job created successfully"
    )
```

#### 4.2 Webhook Integration for Task Completion
**File**: Modify Celery tasks to callback to main API

```python
# In Synth2size-Setu-Backend/app/tasks/faker_tasks.py

@celery_app.task(bind=True)
def generate_faker_data_task(self, job_id: str, config: dict):
    """Generate Faker data and notify main API"""
    try:
        # Generate data (existing logic)
        result = faker_service.generate_data(config)
        
        # Notify main API of completion
        import requests
        requests.post(
            f"{MAIN_API_URL}/api/v1/internal/jobs/{job_id}/complete",
            json={
                "status": "success",
                "rows_generated": result["rows_generated"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            },
            headers={"X-Internal-Key": settings.INTERNAL_API_KEY}
        )
        
        return {"status": "success", "job_id": job_id}
    
    except Exception as e:
        # Notify main API of failure
        requests.post(
            f"{MAIN_API_URL}/api/v1/internal/jobs/{job_id}/failed",
            json={"error": str(e)},
            headers={"X-Internal-Key": settings.INTERNAL_API_KEY}
        )
        raise
```

---

## 📊 Frontend Integration

### Dataset Creation UI Flow

**1. Generator Selection Page** (`apps/web/src/app/datasets/new/page.tsx`)
```tsx
// User selects: Faker, Synthcity, or LLM
<GeneratorSelector 
  onSelect={(type) => router.push(`/datasets/new/${type}`)}
/>
```

**2. Faker Configuration** (`apps/web/src/app/datasets/new/faker/page.tsx`)
```tsx
// Show Faker provider categories
const { data: providers } = useQuery({
  queryKey: ['faker-providers'],
  queryFn: () => getAPI().getFakerProviders()
});

// Build column configuration
const [columns, setColumns] = useState<FakerColumn[]>([]);

// Submit generation request
const createJob = useMutation({
  mutationFn: (config) => getAPI().createGenerationJob({
    generator_type: 'faker',
    num_rows: rowCount,
    config: { columns, locale, format }
  })
});
```

**3. Progress Tracking** (`apps/web/src/app/datasets/jobs/[id]/page.tsx`)
```tsx
// Poll for job status
const { data: job } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => getAPI().getGenerationJob(jobId),
  refetchInterval: (data) => 
    data?.status === 'pending' || data?.status === 'processing' 
      ? 2000 
      : false
});

// Show progress
<ProgressBar 
  percent={job?.progress || 0}
  status={job?.status}
/>

// On completion, show download button
{job?.status === 'completed' && (
  <Button onClick={() => downloadDataset(job.dataset_id)}>
    Download CSV
  </Button>
)}
```

---

## 🔐 Security Considerations

### 1. Rate Limiting Per User
```python
# Add to existing rate limiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=lambda: get_current_user().id,  # Rate limit by user
    default_limits=["100/minute", "1000/hour"]
)

@router.post("/generate")
@limiter.limit("10/minute")  # Additional limit for expensive operations
async def generate_data(...):
    pass
```

### 2. Input Validation
- Sanitize all user inputs (column names, prompts)
- Validate file uploads (MIME type, size, malware scan)
- Limit complexity (max columns, max rows)

### 3. Resource Protection
- Keep connection limiting (current: 100 concurrent)
- Add queue priority (paid users > free users)
- Implement job timeouts (current: 10 minutes max)

### 4. Data Isolation
- Store user data in separate directories/buckets
- Use organization ID in file paths
- Implement auto-deletion after 30 days (configurable)

---

## 📈 Monitoring & Analytics

### Metrics to Track

**Usage Metrics** (add to existing admin dashboard):
```sql
-- Daily generation stats
SELECT 
    DATE(generated_at) as date,
    generator_type,
    COUNT(*) as job_count,
    SUM(rows_generated) as total_rows,
    AVG(rows_generated) as avg_rows_per_job
FROM dataset_usage
WHERE generated_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(generated_at), generator_type;

-- Top users by generation volume
SELECT 
    u.email,
    o.name as organization,
    COUNT(*) as job_count,
    SUM(du.rows_generated) as total_rows
FROM dataset_usage du
JOIN users u ON du.user_id = u.id
JOIN organizations o ON du.organization_id = o.id
WHERE du.generated_at >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.email, o.name
ORDER BY total_rows DESC
LIMIT 20;
```

**Performance Metrics**:
- Average job completion time by type
- Queue depth (pending jobs)
- Worker utilization
- Error rates by generator type

---

## 🚀 Deployment Plan

### Step 1: Add Data Factory as Microservice

**Update docker-compose.yml**:
```yaml
services:
  # Existing services...
  
  # Data Factory API
  data-factory-api:
    build:
      context: ./Synth2size-Setu-Backend
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/1
      - MAIN_API_URL=http://api:8000
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
    depends_on:
      - redis
      - postgres
    networks:
      - synthesize-network
  
  # Data Factory Workers (Celery)
  data-factory-worker:
    build:
      context: ./Synth2size-Setu-Backend
      dockerfile: Dockerfile.celery
    command: celery -A app.celery_app worker --loglevel=info --concurrency=4
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
      - data-factory-api
    deploy:
      replicas: 2  # Scale as needed
    networks:
      - synthesize-network
```

### Step 2: Update Nginx Routing

**nginx/nginx.conf**:
```nginx
upstream data_factory_api {
    server data-factory-api:8000;
}

server {
    # Main API routes
    location /api/ {
        proxy_pass http://api:8000;
    }
    
    # Data Factory routes (internal only)
    location /internal/data-factory/ {
        proxy_pass http://data_factory_api:8000/api/v1/;
        # Block external access
        allow 172.16.0.0/12;  # Docker network
        deny all;
    }
}
```

### Step 3: Environment Variables

**Add to `.env`**:
```bash
# Data Factory Integration
DATA_FACTORY_API_URL=http://data-factory-api:8000
INTERNAL_API_KEY=<generate-secure-key>
GROQ_API_KEY=<your-groq-key>

# Storage
AWS_S3_BUCKET=synthesize-datasets
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

---

## 📝 Migration Checklist

- [ ] **Week 1**: Add authentication to data factory endpoints
- [ ] **Week 1**: Create internal API endpoints for job callbacks
- [ ] **Week 2**: Implement quota checking service
- [ ] **Week 2**: Add dataset_usage table and migration
- [ ] **Week 3**: Integrate generation_service with data factory
- [ ] **Week 3**: Implement file storage (S3 or local)
- [ ] **Week 4**: Build frontend UI for each generator type
- [ ] **Week 4**: Add job status polling and progress tracking
- [ ] **Week 5**: Testing (unit, integration, load testing)
- [ ] **Week 5**: Documentation and admin dashboard updates
- [ ] **Week 6**: Production deployment and monitoring

---

## 🎯 Success Metrics

**Phase 1 Complete**:
- ✅ Users can authenticate and generate data
- ✅ Quota system enforces limits
- ✅ Usage tracked in database

**Phase 2 Complete**:
- ✅ All three generators (Faker, Synthcity, LLM) available via UI
- ✅ Real-time job progress tracking
- ✅ Dataset library populated

**Production Ready**:
- ✅ 100+ concurrent users supported
- ✅ <5s API response time for job creation
- ✅ 95%+ success rate for generation jobs
- ✅ Admin dashboard shows usage metrics
- ✅ Automated quota enforcement and billing integration

---

## 📚 Next Steps

1. **Review this plan** with backend developer
2. **Prioritize integration phases** based on launch timeline
3. **Set up development environment** with data factory
4. **Create detailed API contract** between services
5. **Begin Phase 1 implementation** (authentication)

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2026  
**Author**: AI Development Team
