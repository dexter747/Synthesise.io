"""
Data Factory Endpoints - Synthetic Data Generation API
=======================================================
REST API for generating synthetic data using Faker, Synthcity, and LLM generators.

Endpoints:
- /data-factory/providers - List available Faker providers
- /data-factory/models - List available Synthcity models
- /data-factory/faker/preview - Generate preview data
- /data-factory/faker/generate - Start Faker generation job
- /data-factory/synthcity/validate - Validate uploaded CSV
- /data-factory/synthcity/generate - Start Synthcity generation job
- /data-factory/llm/generate - Start LLM generation job
"""
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from app.api.deps import DBSession, CurrentUser
from app.core.exceptions import ValidationError, GenerationError
from app.models import GenerationRequest, GenerationJob, JobStatus, DataFormat, JobPriority, User
from app.services.faker_service import get_faker_service, FakerColumnConfig, FakerProviderInfo
from app.services.synthcity_service import get_synthcity_service, SynthcityColumnConfig, SYNTHCITY_MODELS
from app.services.llm_service import get_llm_service, LLMColumnConfig
from app.services.quota_service import get_quota_service


router = APIRouter()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_user_organization_id(user: User) -> Optional[UUID]:
    """Safely get the user's active organization ID."""
    org_id = getattr(user, 'active_organization_id', None)
    if org_id:
        return org_id
    # Fallback: check organization memberships
    if hasattr(user, 'organization_memberships') and user.organization_memberships:
        return user.organization_memberships[0].organization_id
    return None


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class FakerPreviewRequest(BaseModel):
    """Request for Faker preview generation."""
    columns: List[FakerColumnConfig]
    num_rows: int = Field(default=5, ge=1, le=50)
    locale: str = Field(default="en_US")


class FakerPreviewResponse(BaseModel):
    """Response with preview data."""
    data: List[dict]
    columns: List[str]
    row_count: int


class FakerGenerateRequest(BaseModel):
    """Request to start Faker generation job."""
    columns: List[FakerColumnConfig]
    num_rows: int = Field(..., ge=1, le=100000)
    locale: str = Field(default="en_US")
    output_format: str = Field(default="csv")
    dataset_name: Optional[str] = None


class SynthcityValidateResponse(BaseModel):
    """Response from CSV validation."""
    valid: bool
    filename: str
    rows: int
    columns: List[str]
    column_types: dict
    null_counts: dict
    memory_usage: int
    warnings: List[str] = []


class SynthcityGenerateRequest(BaseModel):
    """Request to start Synthcity generation job."""
    num_rows: int = Field(..., ge=100, le=100000)
    model: str = Field(default="ctgan")
    epochs: int = Field(default=300, ge=10, le=1000)
    columns_config: Optional[List[SynthcityColumnConfig]] = None
    output_format: str = Field(default="csv")
    save_model: bool = Field(default=True)
    dataset_name: Optional[str] = None


class LLMGenerateRequest(BaseModel):
    """Request to start LLM generation job."""
    columns: List[LLMColumnConfig]
    num_rows: int = Field(..., ge=1, le=1000)
    context: Optional[str] = None
    style: str = Field(default="realistic")
    domain: Optional[str] = None
    output_format: str = Field(default="csv")
    dataset_name: Optional[str] = None


class GenerationJobCreatedResponse(BaseModel):
    """Response when a generation job is created."""
    job_id: UUID
    request_id: Optional[UUID] = None
    status: str
    message: str
    estimated_time: Optional[int] = None


class ProviderListResponse(BaseModel):
    """Response with all Faker providers."""
    providers: dict
    total_categories: int
    total_methods: int


class ModelListResponse(BaseModel):
    """Response with available Synthcity models."""
    models: dict
    recommended: str


# =============================================================================
# PROVIDER/MODEL INFO ENDPOINTS
# =============================================================================

@router.get(
    "/providers",
    response_model=ProviderListResponse,
    summary="List Faker providers",
)
async def list_faker_providers():
    """
    Get all available Faker providers grouped by category.
    
    Returns provider methods like `address.city`, `person.name`, etc.
    that can be used in generation requests.
    """
    faker_service = get_faker_service()
    providers = faker_service.get_all_providers()
    
    total_methods = sum(len(methods) for methods in providers.values())
    
    return ProviderListResponse(
        providers=providers,
        total_categories=len(providers),
        total_methods=total_methods,
    )


@router.get(
    "/models",
    response_model=ModelListResponse,
    summary="List Synthcity models",
)
async def list_synthcity_models():
    """
    Get available ML models for Synthcity generation.
    
    Each model has different strengths:
    - **ctgan**: Best for complex relationships, mixed data types
    - **tvae**: Fast, good for large datasets
    - **copulagan**: Best for correlated features
    - **gaussiancopula**: Fastest, good baseline
    """
    return ModelListResponse(
        models=SYNTHCITY_MODELS,
        recommended="ctgan",
    )


# =============================================================================
# FAKER ENDPOINTS
# =============================================================================

@router.post(
    "/faker/preview",
    response_model=FakerPreviewResponse,
    summary="Generate Faker preview",
)
async def faker_preview(
    request: FakerPreviewRequest,
    user: CurrentUser,
):
    """
    Generate a small preview of Faker data.
    
    Use this to test column configurations before starting a full generation job.
    Limited to 50 rows.
    """
    faker_service = get_faker_service()
    
    # Validate all providers - use effective_method which handles method field
    for col in request.columns:
        method_to_validate = col.method if col.method else col.provider
        if not faker_service.validate_provider(method_to_validate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Faker provider: {method_to_validate}",
            )
    
    try:
        df = faker_service.generate_preview(
            columns=request.columns,
            locale=request.locale,
            num_rows=request.num_rows,
        )
        
        # Convert DataFrame to list of dicts
        data = df.to_dict(orient='records')
        
        return FakerPreviewResponse(
            data=data,
            columns=[col.name for col in request.columns],
            row_count=len(data),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview generation failed: {str(e)}",
        )


@router.post(
    "/faker/generate",
    response_model=GenerationJobCreatedResponse,
    summary="Start Faker generation job",
)
async def faker_generate(
    request: FakerGenerateRequest,
    db: DBSession,
    user: CurrentUser,
):
    """
    Start an asynchronous Faker data generation job.
    
    The job runs in the background. Use the returned job_id to:
    - Check status: GET /jobs/{job_id}
    - Download result when completed
    
    **Limits**: Max 100,000 rows, max 100 columns.
    """
    from app.tasks.data_factory import generate_faker_data
    
    faker_service = get_faker_service()
    quota_service = get_quota_service(db)
    
    # Validate providers - use method field if present
    for col in request.columns:
        method_to_validate = col.method if col.method else col.provider
        if not faker_service.validate_provider(method_to_validate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Faker provider: {method_to_validate}",
            )
    
    # Check column limit
    if len(request.columns) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 columns allowed",
        )
    
    # Check quota
    allowed, message = quota_service.check_row_quota(user.id, request.num_rows)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=message,
        )
    
    # Check feature access
    allowed, message = quota_service.check_feature_access(user.id, "faker")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
    
    # Get user's organization ID if available
    organization_id = get_user_organization_id(user)
    
    # Parse output format - DataFormat enum values are lowercase
    try:
        output_fmt = DataFormat(request.output_format.lower())
    except ValueError:
        output_fmt = DataFormat.CSV
    
    # Create GenerationRequest first
    gen_request = GenerationRequest(
        id=uuid4(),
        user_id=user.id,
        organization_id=organization_id,
        name=request.dataset_name or f"Faker Dataset {request.num_rows} rows",
        description=f"Faker generation with {len(request.columns)} columns, locale: {request.locale}",
        row_count=request.num_rows,
        output_format=output_fmt,
        settings={
            "generator": "faker",
            "locale": request.locale,
            "columns": [col.model_dump() for col in request.columns],
        },
        status=JobStatus.PENDING,
    )
    db.add(gen_request)
    db.flush()
    
    # Create GenerationJob linked to request
    job = GenerationJob(
        id=uuid4(),
        request_id=gen_request.id,
        user_id=user.id,
        organization_id=organization_id,
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        queue_name="generation",
    )
    db.add(job)
    db.commit()
    
    # Queue Celery task
    generate_faker_data.delay(
        job_id=str(job.id),
        columns_config=[col.model_dump() for col in request.columns],
        num_rows=request.num_rows,
        locale=request.locale,
        output_format=request.output_format,
    )
    
    # Estimate time (rough: 10k rows/sec)
    estimated_seconds = max(5, request.num_rows // 10000)
    
    return GenerationJobCreatedResponse(
        job_id=job.id,
        request_id=gen_request.id,
        status="pending",
        message="Generation job queued successfully",
        estimated_time=estimated_seconds,
    )


# =============================================================================
# SYNTHCITY ENDPOINTS
# =============================================================================

@router.post(
    "/synthcity/validate",
    response_model=SynthcityValidateResponse,
    summary="Validate CSV for Synthcity",
)
async def synthcity_validate(
    user: CurrentUser,
    file: UploadFile = File(..., description="CSV file to validate"),
):
    """
    Validate and analyze an uploaded CSV file for Synthcity training.
    
    Returns column types, null counts, and any warnings about the data.
    Max file size: 50MB. Max rows for training: 100,000.
    """
    # Check file size (50MB limit)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 50MB.",
        )
    
    synthcity_service = get_synthcity_service()
    
    try:
        df, validation = synthcity_service.validate_csv(content, file.filename)
        
        return SynthcityValidateResponse(
            valid=validation.valid,
            filename=validation.filename,
            rows=validation.rows,
            columns=validation.columns,
            column_types=validation.column_types,
            null_counts=validation.null_counts,
            memory_usage=validation.memory_usage,
            warnings=validation.warnings,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/synthcity/generate",
    response_model=GenerationJobCreatedResponse,
    summary="Start Synthcity generation job",
)
async def synthcity_generate(
    request: SynthcityGenerateRequest,
    db: DBSession,
    user: CurrentUser,
    file: UploadFile = File(..., description="Training CSV file"),
):
    """
    Start an ML-based synthetic data generation job.
    
    This will:
    1. Upload and validate your training data
    2. Train a ML model (CTGAN, TVAE, etc.)
    3. Generate synthetic data that matches your data's patterns
    
    **Note**: Training takes 5-30 minutes depending on data size and model.
    """
    import os
    from app.tasks.data_factory import generate_synthcity_data
    from app.core.config import settings
    
    quota_service = get_quota_service(db)
    
    # Check feature access
    allowed, message = quota_service.check_feature_access(user.id, "synthcity")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
    
    # Check quota
    allowed, message = quota_service.check_row_quota(user.id, request.num_rows)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=message,
        )
    
    # Validate model
    if request.model not in SYNTHCITY_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model: {request.model}. Available: {list(SYNTHCITY_MODELS.keys())}",
        )
    
    # Save uploaded file temporarily
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 50MB.",
        )
    
    upload_dir = getattr(settings, 'DATA_UPLOAD_DIR', '/tmp/synthesize/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create GenerationRequest
    organization_id = get_user_organization_id(user)
    gen_request = GenerationRequest(
        id=uuid4(),
        user_id=user.id,
        organization_id=organization_id,
        name=request.dataset_name or f"Synthcity {request.model.upper()} Dataset",
        description=f"Synthcity {request.model} generation from {file.filename}",
        row_count=request.num_rows,
        output_format=DataFormat(request.output_format.upper()) if hasattr(DataFormat, request.output_format.upper()) else DataFormat.CSV,
        settings={
            "generator": "synthcity",
            "model": request.model,
            "epochs": request.epochs,
            "training_file": file.filename,
        },
        status=JobStatus.PENDING,
    )
    db.add(gen_request)
    db.flush()
    
    # Create GenerationJob
    job = GenerationJob(
        id=uuid4(),
        request_id=gen_request.id,
        user_id=user.id,
        organization_id=user.organization_memberships[0].organization_id if user.organization_memberships else None,
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        queue_name="generation",
    )
    db.add(job)
    db.commit()
    
    # Queue Celery task
    columns_config = None
    if request.columns_config:
        columns_config = [col.model_dump() for col in request.columns_config]
    
    generate_synthcity_data.delay(
        job_id=str(job.id),
        training_file_path=file_path,
        num_rows=request.num_rows,
        model_name=request.model,
        epochs=request.epochs,
        columns_config=columns_config,
        output_format=request.output_format,
        save_model=request.save_model,
    )
    
    # Estimate time based on model
    time_estimates = {
        "gaussiancopula": 60,
        "tvae": 300,
        "ctgan": 600,
        "copulagan": 600,
    }
    estimated_seconds = time_estimates.get(request.model, 300)
    
    return GenerationJobCreatedResponse(
        job_id=job.id,
        request_id=gen_request.id,
        status="pending",
        message=f"Synthcity {request.model} job queued. Training may take several minutes.",
        estimated_time=estimated_seconds,
    )


# =============================================================================
# LLM ENDPOINTS
# =============================================================================

@router.post(
    "/llm/generate",
    response_model=GenerationJobCreatedResponse,
    summary="Start LLM generation job",
)
async def llm_generate(
    request: LLMGenerateRequest,
    db: DBSession,
    user: CurrentUser,
):
    """
    Start an LLM-powered data generation job.
    
    Best for creative/narrative content like:
    - Product descriptions
    - User reviews
    - Bio/profile text
    - Article summaries
    
    **Limits**: Max 1,000 rows (LLM generation is expensive).
    
    **Styles**: realistic, creative, formal, casual
    
    **Domains**: healthcare, finance, ecommerce, education, technology, etc.
    """
    from app.tasks.data_factory import generate_llm_data
    
    quota_service = get_quota_service(db)
    
    # Check feature access
    allowed, message = quota_service.check_feature_access(user.id, "llm")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
    
    # LLM has lower limits
    if request.num_rows > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LLM generation limited to 1,000 rows. Use Faker for larger datasets.",
        )
    
    # Check quota
    allowed, message = quota_service.check_row_quota(user.id, request.num_rows)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=message,
        )
    
    llm_service = get_llm_service()
    
    if not llm_service.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available. Check API key configuration.",
        )
    
    # Create GenerationRequest
    organization_id = get_user_organization_id(user)
    gen_request = GenerationRequest(
        id=uuid4(),
        user_id=user.id,
        organization_id=organization_id,
        name=request.dataset_name or f"LLM Dataset ({request.style})",
        description=f"LLM generation with {len(request.columns)} columns, style: {request.style}",
        row_count=request.num_rows,
        output_format=DataFormat(request.output_format.upper()) if hasattr(DataFormat, request.output_format.upper()) else DataFormat.CSV,
        settings={
            "generator": "llm",
            "style": request.style,
            "domain": request.domain,
            "context": request.context,
            "columns": [col.model_dump() for col in request.columns],
        },
        status=JobStatus.PENDING,
    )
    db.add(gen_request)
    db.flush()
    
    # Create GenerationJob
    job = GenerationJob(
        id=uuid4(),
        request_id=gen_request.id,
        user_id=user.id,
        organization_id=organization_id,
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        queue_name="generation",
    )
    db.add(job)
    db.commit()
    
    # Queue Celery task
    generate_llm_data.delay(
        job_id=str(job.id),
        columns_config=[col.model_dump() for col in request.columns],
        num_rows=request.num_rows,
        context=request.context,
        style=request.style,
        domain=request.domain,
        output_format=request.output_format,
    )
    
    # Estimate time (roughly 1 row/sec for LLM)
    estimated_seconds = max(10, request.num_rows)
    
    return GenerationJobCreatedResponse(
        job_id=job.id,
        request_id=gen_request.id,
        status="pending",
        message="LLM generation job queued",
        estimated_time=estimated_seconds,
    )


# =============================================================================
# LLM SCHEMA REFINEMENT (Utility endpoint)
# =============================================================================

class RefineSchemaRequest(BaseModel):
    """Request to refine a natural language description into schema."""
    description: str = Field(..., min_length=10, max_length=2000)


class RefineSchemaResponse(BaseModel):
    """Refined schema from LLM."""
    columns: List[str]
    types: dict
    constraints: dict
    suggested_row_count: int
    description: str


@router.post(
    "/llm/refine",
    response_model=RefineSchemaResponse,
    summary="Refine description to schema",
)
async def llm_refine_schema(
    request: RefineSchemaRequest,
    user: CurrentUser,
):
    """
    Use LLM to convert a natural language description into a data schema.
    
    Example input: "I need customer data for an e-commerce store"
    
    Returns suggested columns, types, and constraints.
    """
    llm_service = get_llm_service()
    
    if not llm_service.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available",
        )
    
    try:
        result = llm_service.refine_request(request.description)
        
        return RefineSchemaResponse(
            columns=result.get("columns", []),
            types=result.get("types", {}),
            constraints=result.get("constraints", {}),
            suggested_row_count=result.get("suggested_row_count", 1000),
            description=result.get("description", request.description),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema refinement failed: {str(e)}",
        )
