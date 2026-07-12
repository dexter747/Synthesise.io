"""
Dataset endpoints for Synthesize.io API.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
    Sorting,
    UserSubscription,
    rate_limit,
)
from app.services.dataset_service import DatasetService
from app.services.generation_service import GenerationService
from app.services.llm_service import LLMService
from app.models import Dataset
from app.schemas.dataset import (
    DatasetCreate,
    DatasetCreateFromDescription,
    DatasetUpdate,
    DatasetResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    SchemaFieldCreate,
    SchemaFieldUpdate,
    SchemaFieldResponse,
    GenerationRequest,
    GenerationPreviewRequest,
    GenerationPreviewResponse,
    GenerationJobResponse,
    DatasetTemplateResponse,
    DatasetSchema,
    SchemaField,
    DatasetWithJobResponse,
)
from app.schemas.base import MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _generate_fallback_schema(description: str) -> tuple[list[str], dict[str, str]]:
    """Generate intelligent fallback schema based on description keywords."""
    desc_lower = description.lower()
    
    # Healthcare/Patient data
    if any(word in desc_lower for word in ['patient', 'medical', 'healthcare', 'hospital', 'clinical']):
        return (
            ["patient_id", "first_name", "last_name", "date_of_birth", "gender", 
             "blood_type", "phone", "email", "address", "emergency_contact", 
             "insurance_provider", "medical_record_number", "admission_date", 
             "diagnosis", "treatment", "medications", "allergies", "doctor_assigned"],
            {"patient_id": "uuid", "first_name": "string", "last_name": "string",
             "date_of_birth": "date", "gender": "string", "blood_type": "string",
             "phone": "phone", "email": "email", "address": "address",
             "emergency_contact": "phone", "insurance_provider": "string",
             "medical_record_number": "string", "admission_date": "datetime",
             "diagnosis": "text", "treatment": "text", "medications": "text",
             "allergies": "text", "doctor_assigned": "string"}
        )
    
    # E-commerce/Product data
    if any(word in desc_lower for word in ['product', 'ecommerce', 'shop', 'store', 'inventory']):
        return (
            ["product_id", "name", "description", "category", "price", "stock_quantity",
             "sku", "brand", "rating", "reviews_count", "created_at", "updated_at"],
            {"product_id": "uuid", "name": "string", "description": "text",
             "category": "string", "price": "float", "stock_quantity": "integer",
             "sku": "string", "brand": "string", "rating": "float",
             "reviews_count": "integer", "created_at": "datetime", "updated_at": "datetime"}
        )
    
    # Customer/User data
    if any(word in desc_lower for word in ['customer', 'user', 'member', 'subscriber']):
        return (
            ["user_id", "username", "email", "first_name", "last_name", "phone",
             "address", "city", "state", "zip_code", "country", "date_joined", "last_login"],
            {"user_id": "uuid", "username": "string", "email": "email",
             "first_name": "string", "last_name": "string", "phone": "phone",
             "address": "address", "city": "string", "state": "string",
             "zip_code": "string", "country": "string", "date_joined": "datetime",
             "last_login": "datetime"}
        )
    
    # Financial/Transaction data
    if any(word in desc_lower for word in ['transaction', 'payment', 'invoice', 'billing', 'finance']):
        return (
            ["transaction_id", "user_id", "amount", "currency", "status",
             "payment_method", "transaction_date", "description", "created_at"],
            {"transaction_id": "uuid", "user_id": "uuid", "amount": "float",
             "currency": "string", "status": "string", "payment_method": "string",
             "transaction_date": "datetime", "description": "text", "created_at": "datetime"}
        )
    
    # Default generic fallback
    return (
        ["id", "name", "email", "created_at"],
        {"id": "uuid", "name": "string", "email": "email", "created_at": "datetime"}
    )


def _build_schema_fields(columns: list[str], types: dict[str, str]) -> list[SchemaField]:
    """Build and validate schema fields with type mapping."""
    type_mapping = {
        "string": "string", "str": "string", "text": "text",
        "integer": "integer", "int": "integer",
        "float": "float", "number": "float", "decimal": "float",
        "boolean": "boolean", "bool": "boolean",
        "date": "date", "datetime": "datetime", "timestamp": "datetime",
        "email": "email", "phone": "phone", "address": "address",
        "name": "name", "company": "company", "uuid": "uuid",
        "json": "json", "array": "array",
    }
    
    schema_fields = []
    for col in columns:
        raw_type = types.get(col, "string").lower()
        mapped_type = type_mapping.get(raw_type, "string")
        
        schema_fields.append(SchemaField(
            name=col,
            data_type=mapped_type,
            description=None,
            constraints=None,
            example=None,
        ))
    
    return schema_fields


def _make_dataset_detail_response(dataset: Dataset) -> DatasetDetailResponse:
    """Helper to create DatasetDetailResponse from a Dataset model."""
    # Ensure schema_definition is valid
    schema = dataset.schema_definition
    if not schema or not isinstance(schema, dict):
        schema = {"fields": [], "version": 1}
    elif "fields" not in schema:
        schema = {"fields": [], "version": 1, **schema}
    
    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        user_id=dataset.user_id,
        organization_id=dataset.organization_id,
        schema_definition=schema,
        schema_version=schema.get("version", 1) if isinstance(schema, dict) else 1,
        row_count=dataset.row_count or 0,
        status=dataset.status.value if dataset.status else "ready",
        tags=dataset.tags or [],
        is_template=False,
        template_category=None,
        is_public=dataset.is_public or False,
        last_generated_at=getattr(dataset, 'last_generated_at', None),
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
    )


# =============================================================================
# DATASET CRUD
# =============================================================================

@router.get(
    "/",
    response_model=DatasetListResponse,
    summary="List datasets",
)
def list_datasets(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    sorting: Sorting,
    search: Optional[str] = Query(None, description="Search in name and description"),
    is_template: Optional[bool] = Query(None, description="Filter by template status"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
):
    """List current user's datasets with optional filters."""
    dataset_service = DatasetService(db)
    datasets, total = dataset_service.list_datasets(
        user_id=user.id,
        page=pagination.page,
        per_page=pagination.per_page,
        search=search,
        sort_by=sorting.sort_by,
        sort_order=sorting.sort_order,
    )
    
    return DatasetListResponse(
        items=[
            DatasetResponse(
                id=d.id,
                name=d.name,
                description=d.description,
                user_id=d.user_id,
                organization_id=d.organization_id,
                schema_definition=d.schema_definition or {},
                schema_version=1,
                row_count=d.row_count or 0,
                status=d.status.value if d.status else "ready",
                tags=d.tags or [],
                is_template=False,
                template_category=None,
                is_public=d.is_public or False,
                last_generated_at=None,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in datasets
        ],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=(total + pagination.per_page - 1) // pagination.per_page,
        has_next=pagination.page < (total + pagination.per_page - 1) // pagination.per_page,
        has_prev=pagination.page > 1,
    )


@router.post(
    "/",
    response_model=DatasetDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dataset",
)
def create_dataset(
    data: DatasetCreate,
    db: DBSession,
    user: CurrentUser,
    subscription: UserSubscription,
):
    """Create a new dataset with schema fields."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.create(data, user.id)
    
    return _make_dataset_detail_response(dataset)


@router.post(
    "/preview-schema",
    response_model=dict,
    summary="Preview generated schema before creating dataset",
)
def preview_dataset_schema(
    data: DatasetCreateFromDescription,
    user: CurrentUser,
):
    """
    Preview the AI-generated schema without creating the dataset.
    Allows users to review and edit the schema before final creation.
    """
    llm_service = LLMService()
    
    try:
        # Use LLM to refine the description into a structured schema
        # Pass sample_data if provided to help LLM understand the structure
        refined = llm_service.refine_request(data.description, sample_data=data.sample_data)
        
        # Convert LLM output to our schema format
        columns = refined.get("columns", [])
        types = refined.get("types", {})
        
        # Intelligent fallback based on description keywords
        if not columns:
            logger.warning("LLM returned no columns, using intelligent fallback")
            columns, types = _generate_fallback_schema(data.description)
        
        # Map and validate types
        schema_fields = _build_schema_fields(columns, types)
        
        return {
            "schema": {
                "fields": [{
                    "name": f.name,
                    "data_type": f.data_type,
                    "description": f.description,
                } for f in schema_fields],
                "description": refined.get("description", data.description),
            },
            "llm_used": len(columns) > 0,
            "suggested_row_count": refined.get("suggested_row_count", 1000),
        }
    except Exception as e:
        logger.error(f"Schema preview failed: {e}")
        # Return fallback schema even on error
        columns, types = _generate_fallback_schema(data.description)
        schema_fields = _build_schema_fields(columns, types)
        return {
            "schema": {
                "fields": [{
                    "name": f.name,
                    "data_type": f.data_type,
                } for f in schema_fields],
                "description": data.description,
            },
            "llm_used": False,
            "error": str(e),
        }


@router.post(
    "/generate",
    response_model=DatasetWithJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dataset from natural language description",
)
def create_dataset_from_description(
    data: DatasetCreateFromDescription,
    db: DBSession,
    user: CurrentUser,
    subscription: UserSubscription,
):
    """
    Create a new dataset using AI to generate the schema from a natural language description.
    
    This endpoint:
    1. Uses LLM to analyze your description and generate a structured schema
    2. Creates the dataset with the AI-generated schema
    3. Auto-starts a generation job if row_count is provided
    4. Returns the dataset and job (if started)
    
    Example:
        POST /api/v1/datasets/generate
        {
            "name": "Customer Data",
            "description": "I need realistic customer data including names, emails, phone numbers, addresses, and signup dates",
            "row_count": 1000,
            "output_format": "csv"
        }
    """
    llm_service = LLMService()
    dataset_service = DatasetService(db)
    generation_service = GenerationService(db)
    
    try:
        # Use LLM to refine the description into a structured schema
        # Pass sample_data if provided to help LLM understand the structure
        refined = llm_service.refine_request(data.description, sample_data=data.sample_data)
        
        # Convert LLM output to our schema format
        columns = refined.get("columns", [])
        types = refined.get("types", {})
        
        # Intelligent fallback based on description
        if not columns:
            logger.warning("LLM returned no columns, using intelligent fallback")
            columns, types = _generate_fallback_schema(data.description)
        
        # Build and validate schema fields
        schema_fields = _build_schema_fields(columns, types)
        
        # Create the schema
        schema_definition = DatasetSchema(
            fields=schema_fields,
            primary_key=None,
            version=1,
            description=refined.get("description", data.description),
        )
        
        # Create dataset with the generated schema
        create_data = DatasetCreate(
            name=data.name or refined.get("description", "AI Generated Dataset")[:100],
            description=data.description,
            schema_definition=schema_definition,
            tags=data.tags,
            organization_id=data.organization_id,
        )
        # Pass data first, then user_id (service signature: create(data, user_id))
        dataset = dataset_service.create(create_data, user.id)
        
        logger.info(f"Created AI-generated dataset {dataset.id} with {len(schema_fields)} fields")
        
        # Auto-start generation job if row_count was provided
        job = None
        job_response = None
        if data.row_count and data.row_count > 0:
            try:
                gen_request = GenerationRequest(
                    dataset_id=dataset.id,
                    row_count=data.row_count,
                    output_format=data.output_format or "csv",
                    priority="normal",
                )
                job = generation_service.create_job(
                    data=gen_request,
                    user_id=user.id,
                )
                job_response = GenerationJobResponse(
                    id=job.id,
                    dataset_id=job.dataset_id,
                    status=job.status,
                    row_count=job.row_count,
                    output_format=job.output_format,
                    progress=job.progress or 0,
                    created_at=job.created_at,
                )
                logger.info(f"Auto-started generation job {job.id} for dataset {dataset.id} with {data.row_count} rows")
            except Exception as e:
                logger.error(f"Failed to auto-start generation job: {e}")
                # Don't fail the whole request, just skip auto-generation
        
        return DatasetWithJobResponse(
            dataset=_make_dataset_detail_response(dataset),
            job=job_response,
            message=f"Dataset created with {len(schema_fields)} fields" + (f", generation started for {data.row_count} rows" if job else ""),
        )
        
    except Exception as e:
        logger.error(f"Failed to create dataset from description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dataset schema: {str(e)}"
        )


@router.get(
    "/templates",
    response_model=List[DatasetTemplateResponse],
    summary="List dataset templates",
)
def list_templates(
    db: DBSession,
    user: CurrentUser,
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """List available dataset templates."""
    dataset_service = DatasetService(db)
    templates, total = dataset_service.list_templates(category=category)
    
    # Templates feature not yet implemented, return empty array
    return []


@router.post(
    "/from-template/{template_id}",
    response_model=DatasetDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create dataset from template",
)
def create_from_template(
    template_id: UUID,
    db: DBSession,
    user: CurrentUser,
    name: str = Query(..., description="Name for the new dataset"),
    description: Optional[str] = Query(None, description="Optional description"),
):
    """Create a new dataset from an existing template."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.create_from_template(
        template_id=template_id,
        user_id=user.id,
        name=name,
        description=description,
    )
    
    return _make_dataset_detail_response(dataset)


@router.get(
    "/{dataset_id}",
    response_model=DatasetDetailResponse,
    summary="Get dataset details",
)
def get_dataset(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get dataset details with schema fields."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_by_id_or_raise(dataset_id)
    
    # Authorization check
    dataset_service.authorize_access(dataset, user.id)
    
    return _make_dataset_detail_response(dataset)


@router.put(
    "/{dataset_id}",
    response_model=DatasetDetailResponse,
    summary="Update dataset",
)
def update_dataset(
    dataset_id: UUID,
    data: DatasetUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update dataset properties."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.update(dataset_id, data, user.id)
    
    return _make_dataset_detail_response(dataset)


@router.delete(
    "/{dataset_id}",
    response_model=MessageResponse,
    summary="Delete dataset",
)
def delete_dataset(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Delete a dataset."""
    dataset_service = DatasetService(db)
    dataset_service.delete(dataset_id, user.id)
    return MessageResponse(message="Dataset deleted successfully")


@router.post(
    "/{dataset_id}/duplicate",
    response_model=DatasetDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate dataset",
)
def duplicate_dataset(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
    name: Optional[str] = Query(None, description="Name for the duplicate"),
):
    """Create a copy of an existing dataset."""
    dataset_service = DatasetService(db)
    dataset = dataset_service.clone_dataset(dataset_id, user.id, name)
    
    return _make_dataset_detail_response(dataset)


# =============================================================================
# SCHEMA FIELDS
# =============================================================================

@router.post(
    "/{dataset_id}/fields",
    response_model=SchemaFieldResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add schema field",
)
def add_schema_field(
    dataset_id: UUID,
    data: SchemaFieldCreate,
    db: DBSession,
    user: CurrentUser,
):
    """Add a new field to dataset schema."""
    dataset_service = DatasetService(db)
    field = dataset_service.add_field(dataset_id, user.id, data)
    
    return SchemaFieldResponse(
        id=field.id,
        name=field.name,
        display_name=field.display_name,
        data_type=field.data_type,
        constraints=field.constraints or {},
        llm_guidance=field.llm_guidance,
        order_index=field.order_index or 0,
    )


# IMPORTANT: This must be before /{dataset_id}/fields/{field_id} routes
@router.put(
    "/{dataset_id}/fields/reorder",
    response_model=List[SchemaFieldResponse],
    summary="Reorder schema fields",
)
def reorder_schema_fields(
    dataset_id: UUID,
    field_ids: List[UUID],
    db: DBSession,
    user: CurrentUser,
):
    """Reorder schema fields by providing ordered list of field IDs."""
    dataset_service = DatasetService(db)
    fields = dataset_service.reorder_fields(dataset_id, user.id, field_ids)
    
    return [
        SchemaFieldResponse(
            id=f.id,
            name=f.name,
            display_name=f.display_name,
            data_type=f.data_type,
            constraints=f.constraints or {},
            llm_guidance=f.llm_guidance,
            order_index=f.order_index or 0,
        )
        for f in fields
    ]


@router.put(
    "/{dataset_id}/fields/{field_id}",
    response_model=SchemaFieldResponse,
    summary="Update schema field",
)
def update_schema_field(
    dataset_id: UUID,
    field_id: UUID,
    data: SchemaFieldUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """Update a schema field."""
    dataset_service = DatasetService(db)
    field = dataset_service.update_field(dataset_id, field_id, user.id, data)
    
    return SchemaFieldResponse(
        id=field.id,
        name=field.name,
        display_name=field.display_name,
        data_type=field.data_type,
        constraints=field.constraints or {},
        llm_guidance=field.llm_guidance,
        order_index=field.order_index or 0,
    )


@router.delete(
    "/{dataset_id}/fields/{field_id}",
    response_model=MessageResponse,
    summary="Delete schema field",
)
def delete_schema_field(
    dataset_id: UUID,
    field_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Delete a schema field."""
    dataset_service = DatasetService(db)
    dataset_service.delete_field(dataset_id, field_id, user.id)
    return MessageResponse(message="Field deleted successfully")


# =============================================================================
# DATA GENERATION
# =============================================================================

@router.post(
    "/{dataset_id}/preview",
    response_model=GenerationPreviewResponse,
    summary="Preview generated data",
    dependencies=rate_limit(requests_per_minute=10),
)
def preview_generation(
    dataset_id: UUID,
    data: GenerationPreviewRequest,
    db: DBSession,
    user: CurrentUser,
):
    """Generate a preview of synthetic data (limited rows)."""
    generation_service = GenerationService(db)
    preview = generation_service.generate_preview(
        dataset_id=dataset_id,
        user_id=user.id,
        row_count=min(data.row_count, 10),  # Max 10 rows for preview
    )
    
    return GenerationPreviewResponse(
        data=preview["data"],
        row_count=preview["row_count"],
        format=preview["format"],
    )


@router.post(
    "/{dataset_id}/generate",
    response_model=GenerationJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start data generation job",
)
def start_generation(
    dataset_id: UUID,
    data: GenerationRequest,
    db: DBSession,
    user: CurrentUser,
    subscription: UserSubscription,
):
    """Start a background job to generate synthetic data."""
    generation_service = GenerationService(db)
    
    # Set dataset_id on the request data
    data.dataset_id = dataset_id
    
    job = generation_service.create_job(
        data=data,
        user_id=user.id,
    )
    
    return GenerationJobResponse(
        id=job.id,
        dataset_id=job.dataset_id,
        status=job.status,
        row_count=job.row_count,
        output_format=job.output_format,
        progress=job.progress or 0,
        created_at=job.created_at,
    )


@router.get(
    "/{dataset_id}/jobs",
    summary="List generation jobs for dataset",
)
def list_dataset_jobs(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
):
    """List all generation jobs for a dataset."""
    generation_service = GenerationService(db)
    jobs, total = generation_service.list_jobs(
        dataset_id=dataset_id,
        user_id=user.id,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    
    return {
        "items": [
            {
                "id": str(j.id),
                "status": j.status,
                "row_count": j.row_count,
                "output_format": j.output_format,
                "progress": j.progress or 0,
                "error_message": j.error_message,
                "file_size": j.file_size,
                "created_at": j.created_at.isoformat(),
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
    }


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

@router.get(
    "/{dataset_id}/export",
    summary="Export dataset to various formats",
    response_class=StreamingResponse,
)
def export_dataset(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
    format: str = Query("csv", description="Export format: csv, xlsx, parquet, sql, json, jsonl"),
    # CSV options
    delimiter: str = Query(",", description="CSV delimiter character"),
    include_header: bool = Query(True, description="Include header row in CSV"),
    # SQL options
    table_name: str = Query("data", description="Table name for SQL export"),
    sql_dialect: str = Query("postgresql", description="SQL dialect: postgresql, mysql, sqlite"),
    batch_size: int = Query(1000, ge=100, le=10000, description="Rows per INSERT statement"),
    include_create: bool = Query(True, description="Include CREATE TABLE statement"),
    # Parquet options
    compression: str = Query("snappy", description="Parquet compression: snappy, gzip, brotli, none"),
    # JSON options
    json_indent: int = Query(None, description="JSON indentation (null for compact)"),
):
    """
    Export dataset data to various formats.
    
    Supported formats:
    - **csv**: Comma-separated values (configurable delimiter)
    - **xlsx**: Microsoft Excel spreadsheet
    - **parquet**: Apache Parquet with compression
    - **sql**: SQL INSERT statements with batching
    - **json**: JSON array format
    - **jsonl**: Line-delimited JSON (NDJSON)
    
    For large datasets, consider using the async export endpoint which
    generates the file in the background and provides a download URL.
    """
    from app.services.export_service import ExportService, ExportOptions, ExportFormat
    
    # Validate format
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format '{format}'. Supported: csv, xlsx, parquet, sql, json, jsonl"
        )
    
    # Get dataset and verify ownership
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_by_id(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Check access permissions
    if dataset.user_id != user.id and not dataset.is_public:
        # Check organization membership
        if dataset.organization_id:
            from app.services.organization_service import OrganizationService
            org_service = OrganizationService(db)
            if not org_service.is_member(dataset.organization_id, user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this dataset"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this dataset"
            )
    
    # Get dataset data
    data = dataset_service.get_dataset_data(dataset_id)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data available for this dataset. Generate data first."
        )
    
    # Configure export options
    options = ExportOptions(
        format=export_format,
        csv_delimiter=delimiter,
        csv_include_header=include_header,
        sql_table_name=table_name,
        sql_dialect=sql_dialect,
        sql_batch_size=batch_size,
        sql_include_create=include_create,
        parquet_compression=compression,
        json_indent=json_indent,
    )
    
    # Export data
    export_service = ExportService(options)
    
    try:
        exported_data = export_service.export(data)
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )
    
    # Get content type and filename
    content_type = export_service.get_content_type()
    extension = export_service.get_file_extension()
    filename = f"{dataset.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{extension}"
    
    return StreamingResponse(
        iter([exported_data]),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(exported_data)),
        }
    )


@router.post(
    "/{dataset_id}/export/async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start async export job",
)
def start_export_job(
    dataset_id: UUID,
    db: DBSession,
    user: CurrentUser,
    format: str = Query("csv", description="Export format"),
    options: dict = None,
):
    """
    Start an asynchronous export job for large datasets.
    
    Returns a job ID that can be used to check status and download
    the exported file when complete.
    """
    from app.tasks.generation import export_dataset as export_task
    
    # Verify dataset access
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_by_id(dataset_id)
    
    if not dataset or (dataset.user_id != user.id and not dataset.is_public):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Start async export task
    task = export_task.delay(str(dataset_id), format)
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": f"Export job started for format '{format}'",
        "check_url": f"/api/v1/jobs/{task.id}/status"
    }


@router.post(
    "/convert",
    summary="Convert data between formats",
)
def convert_format(
    db: DBSession,
    user: CurrentUser,
    source_format: str = Query(..., description="Source format"),
    target_format: str = Query(..., description="Target format"),
    data: dict = None,
):
    """
    Convert data from one format to another without saving.
    
    Accepts JSON data and converts it to the target format.
    Useful for testing export configurations.
    """
    from app.services.export_service import ExportService, ExportOptions, ExportFormat
    
    if not data or "rows" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must contain 'rows' array"
        )
    
    try:
        export_format = ExportFormat(target_format.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target format '{target_format}'"
        )
    
    options = ExportOptions(format=export_format)
    export_service = ExportService(options)
    
    try:
        exported = export_service.export(data["rows"])
        content_type = export_service.get_content_type()
        
        return StreamingResponse(
            iter([exported]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="converted.{export_service.get_file_extension()}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
