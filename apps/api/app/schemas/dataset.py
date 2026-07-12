"""
Dataset and data generation schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, PaginatedResponse, TimestampMixin


# =============================================================================
# SCHEMA FIELD DEFINITIONS
# =============================================================================

class FieldConstraint(BaseSchema):
    """Constraints for a schema field."""
    
    required: bool = True
    unique: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum_values: Optional[list[str]] = None
    format: Optional[str] = None  # email, url, uuid, date, etc.
    nullable: bool = False
    default: Optional[Any] = None


class SchemaField(BaseSchema):
    """Definition of a field in a dataset schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    data_type: str = Field(..., pattern="^(string|integer|float|boolean|date|datetime|email|uuid|phone|address|name|company|text|json|array)$")
    description: Optional[str] = Field(None, max_length=500)
    constraints: Optional[FieldConstraint] = None
    example: Optional[Any] = None
    
    # For relationship/reference fields
    reference_dataset: Optional[UUID] = None
    reference_field: Optional[str] = None


class DatasetSchema(BaseSchema):
    """Complete schema definition for a dataset."""
    
    fields: list[SchemaField]
    primary_key: Optional[str] = None
    version: int = 1
    description: Optional[str] = None


# =============================================================================
# DATASET CRUD SCHEMAS
# =============================================================================

class DatasetCreate(BaseSchema):
    """Create a new dataset."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    schema_definition: DatasetSchema
    tags: list[str] = []
    is_template: bool = False
    template_category: Optional[str] = None
    organization_id: Optional[UUID] = None


class DatasetCreateFromDescription(BaseSchema):
    """Create a dataset from a natural language description using AI."""
    
    name: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., min_length=1, max_length=10000)
    sample_data: Optional[str] = Field(None, max_length=50000)
    row_count: Optional[int] = Field(100, ge=1, le=1000000)
    output_format: Optional[str] = Field("csv")
    organization_id: Optional[UUID] = None
    tags: Optional[list[str]] = []


class DatasetUpdate(BaseSchema):
    """Update dataset metadata."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[list[str]] = None
    is_public: Optional[bool] = None


class DatasetSchemaUpdate(BaseSchema):
    """Update dataset schema (creates new version)."""
    
    schema_definition: DatasetSchema
    migration_notes: Optional[str] = None


class DatasetResponse(BaseSchema, TimestampMixin):
    """Dataset response."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    schema_definition: Optional[dict] = None
    schema_version: Optional[int] = 1
    row_count: Optional[int] = 0
    status: Optional[str] = None
    tags: Optional[list[str]] = []
    is_template: Optional[bool] = False
    template_category: Optional[str] = None
    is_public: Optional[bool] = False
    last_generated_at: Optional[datetime] = None


class DatasetListResponse(PaginatedResponse[DatasetResponse]):
    """Paginated list of datasets."""
    pass


class DatasetDetailResponse(DatasetResponse):
    """Detailed dataset info."""
    
    # Generation stats
    total_rows_generated: int = 0
    generation_count: int = 0
    
    # Storage
    storage_size_bytes: int = 0
    
    # Recent jobs
    recent_jobs: list[dict] = []
    
    # Permissions
    can_edit: bool = True
    can_delete: bool = True
    can_generate: bool = True


# =============================================================================
# GENERATION REQUEST SCHEMAS
# =============================================================================

class GenerationOptions(BaseSchema):
    """Options for data generation."""
    
    locale: str = "en_US"
    seed: Optional[int] = None
    consistency_level: str = Field("high", pattern="^(low|medium|high)$")
    use_ai_enhancement: bool = True
    preserve_relationships: bool = True
    null_percentage: float = Field(0.0, ge=0.0, le=100.0)


class GenerationRequest(BaseSchema):
    """Request to generate data."""
    
    dataset_id: Optional[UUID] = None  # Set by endpoint from path param
    row_count: int = Field(..., ge=1, le=1000000)
    output_format: str = Field("json", pattern="^(json|csv|parquet|xml|sql)$")
    options: Optional[GenerationOptions] = None
    webhook_url: Optional[str] = None
    priority: str = Field("normal", pattern="^(low|normal|high)$")


class GenerationPreviewRequest(BaseSchema):
    """Request a preview of generated data."""
    
    row_count: int = Field(10, ge=1, le=100)
    options: Optional[GenerationOptions] = None


class SchemaInferRequest(BaseSchema):
    """Request to infer schema from sample data."""
    
    sample_data: list[dict]
    name: Optional[str] = None
    description: Optional[str] = None


class SchemaFromPromptRequest(BaseSchema):
    """Generate schema from natural language prompt."""
    
    prompt: str = Field(..., min_length=10, max_length=5000)
    context: Optional[str] = None
    example_data: Optional[list[dict]] = None


# =============================================================================
# GENERATION JOB SCHEMAS
# =============================================================================

class GenerationJobResponse(BaseSchema, TimestampMixin):
    """Generation job response."""
    
    id: UUID
    dataset_id: Optional[UUID] = None
    dataset_name: Optional[str] = None
    user_id: Optional[UUID] = None
    status: str
    row_count: int = 0
    rows_generated: int = 0
    output_format: Optional[str] = None
    priority: Optional[str] = None
    progress: float = 0  # 0-100
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    download_expires_at: Optional[datetime] = None


class GenerationJobListResponse(PaginatedResponse[GenerationJobResponse]):
    """Paginated list of generation jobs."""
    pass


class GenerationJobDetailResponse(GenerationJobResponse):
    """Detailed job info."""
    
    error_details: Optional[dict] = None
    file_path: Optional[str] = None
    generation_options: Optional[dict] = None
    llm_model: Optional[str] = None
    llm_tokens_used: Optional[int] = None
    credits_used: Optional[float] = None
    duration_seconds: Optional[float] = None
    options: Optional[GenerationOptions] = None
    schema_snapshot: Optional[DatasetSchema] = None
    generation_logs: list[dict] = []
    metrics: Optional[dict] = None


class DatasetWithJobResponse(BaseSchema):
    """Response containing dataset and auto-started generation job."""
    
    dataset: "DatasetDetailResponse"
    job: Optional[GenerationJobResponse] = None
    message: str = "Dataset created"


# =============================================================================
# DATA PREVIEW SCHEMAS
# =============================================================================

class DataPreviewResponse(BaseSchema):
    """Preview of generated data."""
    
    dataset_id: UUID
    row_count: int
    data: list[dict]
    schema_definition: DatasetSchema


class DataSampleResponse(BaseSchema):
    """Sample data from a dataset."""
    
    dataset_id: UUID
    total_rows: int
    sample_size: int
    data: list[dict]


# =============================================================================
# TEMPLATE SCHEMAS
# =============================================================================

class TemplateResponse(BaseSchema, TimestampMixin):
    """Dataset template."""
    
    id: UUID
    name: str
    description: Optional[str]
    category: str
    schema_definition: DatasetSchema
    usage_count: int
    is_featured: bool
    preview_data: list[dict] = []


class TemplateListResponse(PaginatedResponse[TemplateResponse]):
    """List of templates."""
    pass


class TemplateCategoryResponse(BaseSchema):
    """Template category."""
    
    name: str
    slug: str
    description: Optional[str]
    template_count: int
    icon: Optional[str]


class TemplateCategoriesResponse(BaseSchema):
    """List of template categories."""
    
    categories: list[TemplateCategoryResponse]


# =============================================================================
# IMPORT/EXPORT SCHEMAS
# =============================================================================

class ImportSchemaRequest(BaseSchema):
    """Import schema from various sources."""
    
    source_type: str = Field(..., pattern="^(json|csv|sql|openapi|jsonschema)$")
    source_data: str  # Raw data or URL
    name: Optional[str] = None
    description: Optional[str] = None


class ExportSchemaResponse(BaseSchema):
    """Exported schema."""
    
    format: str
    content: str
    filename: str


# =============================================================================
# ADDITIONAL ENDPOINT SCHEMAS
# =============================================================================

class SchemaFieldCreate(BaseSchema):
    """Create a new schema field."""
    
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    data_type: str
    constraints: Optional[dict] = None
    llm_guidance: Optional[str] = None
    order_index: Optional[int] = None


class SchemaFieldUpdate(BaseSchema):
    """Update a schema field."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    data_type: Optional[str] = None
    constraints: Optional[dict] = None
    llm_guidance: Optional[str] = None
    order_index: Optional[int] = None


class SchemaFieldResponse(BaseSchema):
    """Schema field response."""
    
    id: UUID
    name: str
    display_name: Optional[str] = None
    data_type: str
    constraints: dict = {}
    llm_guidance: Optional[str] = None
    order_index: int = 0


class GenerationPreviewResponse(BaseSchema):
    """Preview generation response."""
    
    data: list[dict]
    row_count: int
    format: str


class DatasetTemplateResponse(BaseSchema):
    """Dataset template for the templates list."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    fields: list[SchemaFieldResponse] = []
    preview_data: Optional[dict] = None

