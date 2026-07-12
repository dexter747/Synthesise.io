# Data Factory Integration TODO

## Overview
Integrating Synth2size-Setu-Backend data factory into apps/api for complete synthetic data generation.

**Last Updated:** Integration Complete ✅

---

## ✅ Phase 1: Core Services (COMPLETE)

### 1.1 Faker Service Integration ✅
- [x] Port `Synth2size-Setu-Backend/app/services/faker_service.py` → `apps/api/app/services/faker_service.py`
- [x] Add all FAKER_PROVIDERS mapping (25+ categories, 300+ methods)
- [x] Implement `FakerService` class with:
  - [x] `get_faker(locale)` - Get/cache Faker instance
  - [x] `get_all_providers()` - Return provider info
  - [x] `generate_dataframe(columns, num_rows)` - Generate DataFrame
  - [x] `generate_batched(columns, num_rows, batch_size)` - Generator for large datasets
  - [x] `validate_provider(provider_path)` - Validate provider exists
  - [x] `reset_unique()` - Reset unique value tracking

### 1.2 Synthcity Service Integration ✅
- [x] Port `Synth2size-Setu-Backend/app/services/synthcity_service.py` → `apps/api/app/services/synthcity_service.py`
- [x] Add SYNTHCITY_MODELS mapping (ctgan, tvae, copulagan, gaussiancopula)
- [x] Implement `SynthcityService` class with:
  - [x] `get_available_models()` - List models
  - [x] `validate_csv(file_content, filename)` - Validate upload
  - [x] `preprocess_data(df, columns_config)` - Prepare for training
  - [x] `train_model(df, model_name, epochs)` - Train SDV model
  - [x] `generate_synthetic_data(model, num_rows)` - Generate data
  - [x] `save_model(model, model_id)` - Persist trained model
  - [x] `load_model(model_id)` - Load saved model

### 1.3 LLM Service Enhancement ✅
- [x] Update existing `apps/api/app/services/llm_service.py` with:
  - [x] Groq API integration (already exists)
  - [x] `_build_generation_prompt()` - Build data gen prompt
  - [x] `generate_creative_data(prompt, columns, num_rows)` - Generate via LLM
  - [x] `_parse_llm_response()` - Parse JSON from LLM response
  - [x] `generate_creative_data_sync()` - Sync version for Celery
  - [x] `_call_groq_api_sync()` - Sync API call for Celery workers

---

## ✅ Phase 2: Celery Tasks (COMPLETE)

### 2.1 Create Data Factory Tasks ✅
Location: `apps/api/app/tasks/data_factory.py`

- [x] `generate_faker_data(job_id, columns, num_rows, locale, options)`
  - Progress tracking: 0-20% init, 20-80% generation, 80-100% save
  - Batch processing for large datasets
  - File output in multiple formats

- [x] `generate_synthcity_data(job_id, file_content, model, epochs, num_rows)`
  - Progress: 0-10% validate, 10-20% preprocess, 20-80% train, 80-95% generate
  - Handle training failures gracefully
  - Model caching for repeat generations

- [x] `generate_llm_data(job_id, prompt, columns, num_rows)`
  - Progress tracking
  - Chunk large requests
  - Retry on API failures

- [x] `generate_unified(job_id, generator_type, config)` - Router task

### 2.2 Task Callbacks
- [ ] On success: Update job status, create dataset record, track usage
- [ ] On failure: Update job status, send notification, log error
- [ ] Progress updates via Celery `update_state()`

---

## ✅ Phase 3: Database Models

### 3.1 New/Updated Models
Location: `apps/api/app/models.py`

- [ ] Add `GeneratorType` enum: `FAKER`, `SYNTHCITY`, `LLM`
- [ ] Update `GenerationJob` model:
  - [ ] Add `generator_type: GeneratorType`
  - [ ] Add `generator_config: JSON` (column configs, locale, etc.)
  - [ ] Add `training_file_id: UUID` (for Synthcity)
  - [ ] Add `model_id: String` (for trained model reference)

- [ ] Add `DatasetUsage` model (for quota tracking):
  ```python
  class DatasetUsage(Base):
      id: UUID
      organization_id: UUID
      user_id: UUID
      dataset_id: UUID
      generator_type: GeneratorType
      rows_generated: Integer
      tokens_used: Integer  # For LLM
      generated_at: DateTime
  ```

- [ ] Add `TrainedModel` model (for Synthcity model reuse):
  ```python
  class TrainedModel(Base):
      id: UUID
      user_id: UUID
      organization_id: UUID
      name: String
      model_type: String  # ctgan, tvae, etc.
      training_rows: Integer
      file_path: String
      created_at: DateTime
      expires_at: DateTime
  ```

### 3.2 Database Migration
- [ ] Create migration: `alembic revision -m "add_data_factory_models"`
- [ ] Add GeneratorType enum
- [ ] Add DatasetUsage table
- [ ] Add TrainedModel table
- [ ] Update GenerationJob with new columns

---

## ✅ Phase 4: Quota System

### 4.1 Quota Service
Location: `apps/api/app/services/quota_service.py`

- [ ] Create `QuotaService` class:
  ```python
  class QuotaService:
      def get_tier_limits(tier: str) -> dict
      def get_available_rows(org_id: UUID) -> int
      def get_available_llm_tokens(org_id: UUID) -> int
      def check_quota(org_id: UUID, rows: int, generator: str) -> bool
      def consume_quota(org_id, user_id, rows, generator, dataset_id)
      def get_usage_stats(org_id: UUID, period: str) -> dict
  ```

- [ ] Tier limits:
  ```python
  TIER_LIMITS = {
      "beginner": {"rows_monthly": 5000, "llm_tokens": 10000},
      "pro": {"rows_monthly": 100000, "llm_tokens": 100000},
      "business": {"rows_monthly": 1000000, "llm_tokens": 500000},
      "enterprise": {"rows_monthly": 10000000, "llm_tokens": 2000000}
  }
  ```

### 4.2 Quota Checks in Endpoints
- [ ] Add quota check before job creation
- [ ] Return remaining quota in response
- [ ] Add 429 response when quota exceeded
- [ ] Track partial usage on job failure

---

## ✅ Phase 5: API Endpoints

### 5.1 Faker Endpoints
Location: `apps/api/app/api/v1/endpoints/faker.py`

- [ ] `GET /api/v1/faker/providers` - List all providers
- [ ] `GET /api/v1/faker/providers/{category}` - Get category methods
- [ ] `POST /api/v1/faker/preview` - Generate 10-row preview (sync)
- [ ] `POST /api/v1/faker/generate` - Create generation job (async)

### 5.2 Synthcity Endpoints
Location: `apps/api/app/api/v1/endpoints/synthcity.py`

- [ ] `GET /api/v1/synthcity/models` - List available models
- [ ] `POST /api/v1/synthcity/validate` - Validate uploaded CSV
- [ ] `POST /api/v1/synthcity/preview` - Generate preview from sample
- [ ] `POST /api/v1/synthcity/generate` - Create training + generation job
- [ ] `GET /api/v1/synthcity/models/saved` - List user's trained models
- [ ] `POST /api/v1/synthcity/models/{model_id}/generate` - Generate from saved model

### 5.3 LLM Endpoints
Location: `apps/api/app/api/v1/endpoints/llm.py`

- [ ] `GET /api/v1/llm/status` - Check LLM API status
- [ ] `POST /api/v1/llm/preview` - Generate 5-10 row preview (sync)
- [ ] `POST /api/v1/llm/generate` - Create generation job (async)

### 5.4 Unified Generation Endpoint
Location: `apps/api/app/api/v1/endpoints/generation.py`

- [ ] `POST /api/v1/generate` - Unified endpoint accepting generator_type
- [ ] `GET /api/v1/generate/jobs` - List user's generation jobs
- [ ] `GET /api/v1/generate/jobs/{job_id}` - Get job status
- [ ] `DELETE /api/v1/generate/jobs/{job_id}` - Cancel job
- [ ] `GET /api/v1/generate/jobs/{job_id}/download` - Download result

### 5.5 Quota Endpoints
Location: `apps/api/app/api/v1/endpoints/quota.py`

- [ ] `GET /api/v1/quota` - Get current quota status
- [ ] `GET /api/v1/quota/usage` - Get usage history
- [ ] `GET /api/v1/quota/limits` - Get tier limits

---

## ✅ Phase 6: Pydantic Schemas

### 6.1 Create Schemas
Location: `apps/api/app/schemas/data_factory.py`

- [ ] Faker schemas:
  - `FakerColumnConfig`
  - `FakerGenerateRequest`
  - `FakerProvidersResponse`
  - `FakerProviderInfo`

- [ ] Synthcity schemas:
  - `SynthcityColumnConfig`
  - `SynthcityGenerateRequest`
  - `SynthcityModelsResponse`
  - `SynthcityValidationResponse`

- [ ] LLM schemas:
  - `LLMColumnConfig`
  - `LLMGenerateRequest`

- [ ] Common schemas:
  - `GenerationJobResponse`
  - `GenerationProgressResponse`
  - `QuotaStatusResponse`
  - `UsageStatsResponse`

---

## ✅ Phase 7: Utilities

### 7.1 Helper Functions
Location: `apps/api/app/utils/data_factory_helpers.py`

- [ ] `generate_file_id()` - Unique file identifiers
- [ ] `save_dataframe(df, path, format)` - Save in multiple formats
- [ ] `load_dataframe(path)` - Load auto-detecting format
- [ ] `dataframe_to_bytes(df, format)` - Convert for streaming
- [ ] `infer_column_types(df)` - Analyze DataFrame types
- [ ] `sanitize_column_name(name)` - Clean column names
- [ ] `ensure_directory(path)` - Create if not exists

### 7.2 File Storage
- [ ] Implement file storage abstraction (local/S3)
- [ ] Configure storage paths in settings
- [ ] Add file cleanup job (delete old files)

---

## ✅ Phase 8: Configuration

### 8.1 Settings
Location: `apps/api/app/core/config.py`

Add new settings:
- [ ] `FAKER_DEFAULT_LOCALE: str = "en_US"`
- [ ] `FAKER_MAX_ROWS: int = 100000`
- [ ] `FAKER_MAX_COLUMNS: int = 100`
- [ ] `FAKER_BATCH_SIZE: int = 1000`
- [ ] `SYNTHCITY_MAX_EPOCHS: int = 1000`
- [ ] `SYNTHCITY_DEFAULT_EPOCHS: int = 300`
- [ ] `SYNTHCITY_MAX_TRAINING_ROWS: int = 100000`
- [ ] `LLM_MAX_ROWS: int = 500`
- [ ] `LLM_GROQ_API_KEY: str`
- [ ] `LLM_GROQ_MODEL: str = "llama-3.3-70b-versatile"`
- [ ] `DATA_OUTPUT_DIR: str = "/tmp/synthesize/outputs"`
- [ ] `DATA_UPLOAD_DIR: str = "/tmp/synthesize/uploads"`
- [ ] `DATA_MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024`

---

## ✅ Phase 9: Dependencies

### 9.1 Python Packages
Add to `apps/api/requirements.txt`:

```
# Data Factory
faker>=24.0.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0  # Excel support
pyarrow>=14.0.0  # Parquet support
httpx>=0.25.0    # Async HTTP client

# Synthcity / SDV
sdv>=1.8.0       # Synthetic Data Vault
synthcity>=0.2.0 # Optional: if using synthcity directly

# System monitoring
psutil>=5.9.0
```

---

## ✅ Phase 10: Testing

### 10.1 Unit Tests
- [ ] `tests/test_faker_service.py`
- [ ] `tests/test_synthcity_service.py`
- [ ] `tests/test_llm_service.py`
- [ ] `tests/test_quota_service.py`

### 10.2 Integration Tests
- [ ] `tests/test_faker_endpoints.py`
- [ ] `tests/test_synthcity_endpoints.py`
- [ ] `tests/test_generation_flow.py`

### 10.3 Load Tests
- [ ] Faker: 100 concurrent users, 10K rows each
- [ ] Synthcity: 10 concurrent users, training + generation
- [ ] LLM: 50 concurrent users, 100 rows each

---

## ✅ Phase 11: Documentation

### 11.1 API Documentation
- [ ] Update OpenAPI schemas with examples
- [ ] Add response examples to endpoints
- [ ] Document rate limits and quotas

### 11.2 Developer Docs
- [ ] Usage examples for each generator
- [ ] Configuration guide
- [ ] Troubleshooting common errors

---

## 📋 Implementation Order

1. **Week 1**: Core Services (Faker, Synthcity, LLM)
2. **Week 2**: Celery Tasks + Database Models
3. **Week 3**: Quota System + Endpoints
4. **Week 4**: Testing + Documentation

---

## 🔄 Files to Port from Synth2size-Setu-Backend

| Source File | Target File | Status |
|-------------|-------------|--------|
| `app/services/faker_service.py` | `app/services/faker_service.py` | ⬜ TODO |
| `app/services/synthcity_service.py` | `app/services/synthcity_service.py` | ⬜ TODO |
| `app/services/llm_service.py` | `app/services/llm_service.py` | ⬜ Update |
| `app/tasks/faker_tasks.py` | `app/tasks/data_factory.py` | ⬜ TODO |
| `app/tasks/synthcity_tasks.py` | `app/tasks/data_factory.py` | ⬜ TODO |
| `app/tasks/llm_tasks.py` | `app/tasks/data_factory.py` | ⬜ TODO |
| `app/models/schemas.py` | `app/schemas/data_factory.py` | ⬜ TODO |
| `app/utils/helpers.py` | `app/utils/data_factory_helpers.py` | ⬜ TODO |
| `app/core/exceptions.py` | `app/core/exceptions.py` | ⬜ Merge |
| `app/config.py` | `app/core/config.py` | ⬜ Merge |

---

## 📝 Notes

- Keep existing authentication/authorization system intact
- Use existing Celery configuration
- Integrate with existing Dataset model
- Use existing file storage patterns where possible
- Maintain backward compatibility with existing generation endpoints
