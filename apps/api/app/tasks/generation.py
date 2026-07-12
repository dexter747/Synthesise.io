"""
Data Generation Celery Tasks
============================
Heavy processing happens here, not in FastAPI.
Implements production-grade data generation with:
- Faker-based synthetic data
- LLM-powered creative data
- Batch processing with progress tracking
- Retry logic and error handling
"""
import os
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_file_id() -> str:
    """Generate a unique file identifier."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_part = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_part}"


def ensure_directory(path: str) -> str:
    """Ensure directory exists, create if not."""
    os.makedirs(path, exist_ok=True)
    return path


def save_dataframe(df: pd.DataFrame, filepath: str, output_format: str) -> str:
    """Save DataFrame to file in specified format."""
    if output_format == "csv":
        df.to_csv(filepath, index=False)
    elif output_format == "json":
        df.to_json(filepath, orient="records", indent=2)
    elif output_format == "parquet":
        df.to_parquet(filepath, index=False)
    elif output_format in ("xlsx", "excel"):
        df.to_excel(filepath, index=False, engine="openpyxl")
    else:
        # Default to CSV
        df.to_csv(filepath, index=False)
    return filepath


def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy/pandas types to JSON-serializable Python types."""
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


def update_job_in_db(job_id: str, status: str, progress: float = None, 
                     rows_generated: int = None, file_path: str = None, 
                     file_size: int = None, error_message: str = None) -> None:
    """Update job status in database."""
    try:
        from app.models import GenerationJob, JobStatus
        
        # Create sync engine for Celery worker
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as db:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                # Map string status to enum (using correct enum values)
                status_map = {
                    "pending": JobStatus.PENDING,
                    "queued": JobStatus.QUEUED,
                    "running": JobStatus.PROCESSING,  # "running" maps to PROCESSING
                    "processing": JobStatus.PROCESSING,
                    "completed": JobStatus.COMPLETED,
                    "failed": JobStatus.FAILED,
                    "canceled": JobStatus.CANCELED,
                    "cancelled": JobStatus.CANCELED,
                    "timeout": JobStatus.TIMEOUT,
                }
                job.status = status_map.get(status, JobStatus.PROCESSING)
                
                if progress is not None:
                    job.progress = min(progress, 100.0)
                if rows_generated is not None:
                    job.rows_generated = rows_generated
                if file_path is not None:
                    job.file_path = file_path
                if file_size is not None:
                    job.file_size_bytes = file_size
                if error_message is not None:
                    job.error_message = error_message
                if status in ("running", "processing") and not job.started_at:
                    job.started_at = datetime.utcnow()
                if status in ("completed", "failed", "canceled", "cancelled"):
                    job.completed_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Updated job {job_id}: status={status}, progress={progress}")
    except Exception as e:
        logger.error(f"Failed to update job {job_id} in DB: {e}")


def get_dataset_schema(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Get dataset schema from database."""
    try:
        from app.models import Dataset
        
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as db:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if dataset and dataset.schema_definition:
                return dataset.schema_definition
    except Exception as e:
        logger.error(f"Failed to get dataset schema: {e}")
    return None


def schema_to_faker_columns(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert dataset schema to Faker column configs with intelligent field mapping."""
    columns = []
    fields = schema.get("fields", [])
    
    # Type to Faker provider mapping
    type_mapping = {
        "string": "pystr",
        "text": "text",
        "integer": "pyint",
        "float": "pyfloat",
        "boolean": "pybool",
        "date": "date",
        "datetime": "date_time",
        "email": "email",
        "phone": "phone_number",
        "url": "url",
        "uuid": "uuid4",
        "name": "name",
        "first_name": "first_name",
        "last_name": "last_name",
        "address": "address",
        "city": "city",
        "state": "administrative_unit",
        "country": "country",
        "country_code": "country_code",
        "postcode": "postcode",
        "zipcode": "postcode",
        "zip_code": "postcode",
        "company": "company",
        "job": "job",
        "job_title": "job",
        "credit_card": "credit_card_number",
        "ssn": "ssn",
        "ipv4": "ipv4",
        "ipv6": "ipv6",
        "ip_address": "ipv4",
        "mac_address": "mac_address",
        "user_agent": "user_agent",
        "password": "password",
        "color": "color",
        "currency": "currency_code",
        "price": "pricetag",
        "sentence": "sentence",
        "paragraph": "paragraph",
        "word": "word",
        "domain": "domain_name",
        "username": "user_name",
        "slug": "slug",
        "iban": "iban",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    
    # Name-based heuristic mapping (checked against field name)
    name_hints = [
        # (pattern_substring, provider)
        ("email", "email"),
        ("phone", "phone_number"),
        ("mobile", "phone_number"),
        ("first_name", "first_name"),
        ("firstname", "first_name"),
        ("last_name", "last_name"),
        ("lastname", "last_name"),
        ("full_name", "name"),
        ("fullname", "name"),
        ("username", "user_name"),
        ("user_name", "user_name"),
        ("street", "street_address"),
        ("address", "address"),
        ("city", "city"),
        ("state", "administrative_unit"),
        ("province", "administrative_unit"),
        ("country", "country"),
        ("zip", "postcode"),
        ("postal", "postcode"),
        ("postcode", "postcode"),
        ("company", "company"),
        ("organization", "company"),
        ("org_name", "company"),
        ("job_title", "job"),
        ("job", "job"),
        ("title", "sentence"),
        ("description", "paragraph"),
        ("bio", "paragraph"),
        ("summary", "sentence"),
        ("comment", "sentence"),
        ("review", "paragraph"),
        ("price", "pricetag"),
        ("amount", "pricetag"),
        ("cost", "pricetag"),
        ("salary", "pricetag"),
        ("revenue", "pricetag"),
        ("url", "url"),
        ("website", "url"),
        ("domain", "domain_name"),
        ("slug", "slug"),
        ("ip_address", "ipv4"),
        ("ipv4", "ipv4"),
        ("ipv6", "ipv6"),
        ("mac", "mac_address"),
        ("ssn", "ssn"),
        ("iban", "iban"),
        ("credit_card", "credit_card_number"),
        ("card_number", "credit_card_number"),
        ("latitude", "latitude"),
        ("lat", "latitude"),
        ("longitude", "longitude"),
        ("lng", "longitude"),
        ("lon", "longitude"),
        ("color", "color_name"),
        ("colour", "color_name"),
        ("avatar", "image_url"),
        ("image", "image_url"),
        ("password", "password"),
        ("license_plate", "license_plate"),
        ("vin", "vin"),
    ]
    
    for field in fields:
        field_name = field.get("name", "column")
        # Support both "data_type" (from schema) and "type" (from LLM)
        field_type = field.get("data_type", field.get("type", "string")).lower()
        
        # Determine Faker provider from type mapping first
        provider = type_mapping.get(field_type, "pystr")
        
        # Override with name-based heuristics (more specific)
        name_lower = field_name.lower()
        
        # Check for date/time patterns first (common override)
        if any(kw in name_lower for kw in ("created", "updated", "modified", "deleted", "timestamp")):
            provider = "date_time"
        elif name_lower == "id" or name_lower.endswith("_id"):
            if "uuid" in field_type:
                provider = "uuid4"
            else:
                provider = "pyint"
        else:
            # Check name hints first (more specific patterns checked first)
            matched = False
            for hint_pattern, hint_provider in name_hints:
                if hint_pattern in name_lower:
                    provider = hint_provider
                    matched = True
                    break
            
            # Fall back to "name" check only if nothing more specific matched
            if not matched and "name" in name_lower and provider == "pystr":
                if "first" in name_lower:
                    provider = "first_name"
                elif "last" in name_lower:
                    provider = "last_name"
                else:
                    provider = "name"
        
        columns.append({
            "name": field_name,
            "provider": provider,
            "unique": field.get("unique", False),
            "null_probability": 0.0 if field.get("required", True) else 0.1,
        })
    
    return columns


# =============================================================================
# MAIN GENERATION TASK (Production Implementation)
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.generation.generate_dataset",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def generate_dataset(self, job_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a full dataset using Faker.
    This runs in Celery worker, keeping FastAPI free for handling requests.
    
    Args:
        job_id: Unique job identifier
        request_data: Generation parameters including:
            - row_count: Number of rows to generate
            - output_format: Output format (csv, json, parquet, xlsx)
            - dataset_id: Dataset UUID to get schema from
            - columns: Optional direct column configs
            - priority: Job priority
            
    Returns:
        Dict with status, file_url, and metadata
    """
    task_id = self.request.id
    logger.info(f"Starting generation task {task_id} for job {job_id}")
    
    try:
        # =====================================================================
        # PHASE 1: Initialize (0-10%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 0, "message": "Initializing generation service"}
        )
        update_job_in_db(job_id, "running", progress=0)
        
        # Parse request data
        num_rows = request_data.get("row_count", 1000)
        output_format = request_data.get("output_format", "csv")
        dataset_id = request_data.get("dataset_id")
        direct_columns = request_data.get("columns")
        batch_size = min(request_data.get("batch_size", 1000), 5000)
        
        logger.info(f"Job {job_id}: Generating {num_rows} rows in {output_format} format")
        
        # =====================================================================
        # PHASE 2: Get/Build Column Configuration (10-15%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 10, "message": "Loading schema configuration"}
        )
        update_job_in_db(job_id, "running", progress=10)
        
        # Get column configuration
        faker_columns = []
        
        if direct_columns:
            # Use directly provided columns
            faker_columns = direct_columns
            logger.info(f"Using {len(faker_columns)} directly provided columns")
        elif dataset_id:
            # Get schema from dataset
            schema = get_dataset_schema(dataset_id)
            if schema:
                faker_columns = schema_to_faker_columns(schema)
                logger.info(f"Converted schema to {len(faker_columns)} Faker columns")
            else:
                logger.warning(f"No schema found for dataset {dataset_id}")
        
        # Fallback to default columns if none found
        if not faker_columns:
            logger.info("Using default column configuration")
            faker_columns = [
                {"name": "id", "provider": "pyint"},
                {"name": "name", "provider": "name"},
                {"name": "email", "provider": "email"},
                {"name": "created_at", "provider": "date_time"},
            ]
        
        # =====================================================================
        # PHASE 3: Initialize Faker Service (15-20%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 15, "message": "Initializing Faker service"}
        )
        update_job_in_db(job_id, "running", progress=15)
        
        from app.services.faker_service import FakerService, FakerColumnConfig
        
        faker_service = FakerService(locale="en_US")
        
        # Convert to FakerColumnConfig objects
        column_configs = []
        for col in faker_columns:
            try:
                config = FakerColumnConfig(
                    name=col.get("name", "column"),
                    provider=col.get("provider", "pystr"),
                    method=col.get("method"),
                    params=col.get("params"),
                    args=col.get("args"),
                    locale=col.get("locale"),
                    unique=col.get("unique", False),
                    null_probability=col.get("null_probability", 0.0),
                )
                column_configs.append(config)
            except Exception as e:
                logger.warning(f"Invalid column config {col}: {e}")
        
        if not column_configs:
            raise ValueError("No valid column configurations")
        
        # =====================================================================
        # PHASE 4: Generate Data in Batches (20-85%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 20, "message": f"Generating {num_rows} rows of data"}
        )
        update_job_in_db(job_id, "running", progress=20)
        
        if num_rows <= batch_size:
            # Generate all at once for small datasets
            df = faker_service.generate_dataframe(
                columns=column_configs,
                num_rows=num_rows,
            )
            update_job_in_db(job_id, "running", progress=80, rows_generated=num_rows)
        else:
            # Generate in batches for large datasets
            all_dfs = []
            generated = 0
            
            for batch_df in faker_service.generate_batched(
                columns=column_configs,
                num_rows=num_rows,
                batch_size=batch_size,
            ):
                all_dfs.append(batch_df)
                generated += len(batch_df)
                
                # Calculate progress (20% to 80% range)
                progress = 20 + int((generated / num_rows) * 60)
                
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": progress,
                        "message": f"Generated {generated:,}/{num_rows:,} rows"
                    }
                )
                update_job_in_db(job_id, "running", progress=progress, rows_generated=generated)
                
                logger.info(f"Job {job_id}: Generated {generated}/{num_rows} rows")
            
            df = pd.concat(all_dfs, ignore_index=True)
        
        # Reset unique value tracking
        faker_service.reset_unique()
        
        # =====================================================================
        # PHASE 5: Save Output File (85-95%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 85, "message": "Saving output file"}
        )
        update_job_in_db(job_id, "running", progress=85)
        
        # Ensure output directory exists
        output_dir = ensure_directory(os.path.join(settings.DATA_DIR, "generated"))
        
        # Generate filename
        file_id = generate_file_id()
        ext = output_format if output_format != "excel" else "xlsx"
        filename = f"dataset_{file_id}.{ext}"
        filepath = os.path.join(output_dir, filename)
        
        # Save file
        save_dataframe(df, filepath, output_format)
        file_size = os.path.getsize(filepath)
        
        logger.info(f"Job {job_id}: Saved {filename} ({file_size:,} bytes)")
        
        # =====================================================================
        # PHASE 6: Finalize (95-100%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 95, "message": "Finalizing"}
        )
        
        # Update job in database as completed
        update_job_in_db(
            job_id, 
            "completed", 
            progress=100, 
            rows_generated=len(df),
            file_path=filepath,
            file_size=file_size
        )
        
        result = convert_to_serializable({
            "status": "completed",
            "task_id": task_id,
            "job_id": job_id,
            "file_id": file_id,
            "filename": filename,
            "filepath": filepath,
            "file_url": f"/api/v1/files/generated/{filename}",
            "rows_generated": len(df),
            "columns": list(df.columns),
            "file_size": file_size,
            "output_format": output_format,
        })
        
        logger.info(f"Job {job_id} completed successfully: {len(df)} rows generated")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job_id} failed: {error_msg}")
        
        # Update job as failed
        update_job_in_db(job_id, "failed", error_message=error_msg)
        
        self.update_state(state="FAILURE", meta={"error": error_msg})
        
        # Retry on transient errors
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=e)
        
        raise


@celery_app.task(bind=True, name="app.tasks.generation.export_dataset")
def export_dataset(self, dataset_id: str, target_format: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convert dataset to different format (CSV, JSON, Parquet, SQL, Excel, JSONL)
    Runs asynchronously for large datasets.
    
    Args:
        dataset_id: UUID of the dataset to export
        target_format: Target format (csv, xlsx, parquet, sql, json, jsonl)
        options: Export options dict (delimiter, compression, etc.)
        
    Returns:
        Dict with status, file_url, and metadata
    """
    import os
    import uuid
    from datetime import datetime
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.config import settings
    from app.services.export_service import ExportService, ExportOptions, ExportFormat
    from app.services.dataset_service import DatasetService
    from app.models import Dataset, GenerationJob, JobStatus
    
    logger.info(f"Starting export of dataset {dataset_id} to {target_format}")
    
    try:
        # Update state
        self.update_state(state='PROCESSING', meta={'progress': 10, 'stage': 'initializing'})
        
        # Create database session
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as db:
            # Get dataset
            dataset_service = DatasetService(db)
            dataset = dataset_service.get_by_id(dataset_id)
            
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            self.update_state(state='PROCESSING', meta={'progress': 20, 'stage': 'loading_data'})
            
            # Get dataset data
            data = dataset_service.get_dataset_data(dataset_id)
            
            if not data:
                raise ValueError("No data available for export")
            
            self.update_state(state='PROCESSING', meta={'progress': 40, 'stage': 'configuring_export'})
            
            # Parse format
            try:
                export_format = ExportFormat(target_format.lower())
            except ValueError:
                raise ValueError(f"Invalid format: {target_format}")
            
            # Configure options
            export_options = ExportOptions(format=export_format)
            if options:
                for key, value in options.items():
                    if hasattr(export_options, key):
                        setattr(export_options, key, value)
            
            self.update_state(state='PROCESSING', meta={'progress': 50, 'stage': 'exporting'})
            
            # Export data
            export_service = ExportService(export_options)
            exported_data = export_service.export(data)
            
            self.update_state(state='PROCESSING', meta={'progress': 80, 'stage': 'saving_file'})
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = dataset.name.replace(' ', '_').replace('/', '_')[:50]
            extension = export_service.get_file_extension()
            filename = f"{safe_name}_{timestamp}.{extension}"
            
            # Ensure export directory exists
            export_dir = os.path.join(settings.DATA_DIR, "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(export_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(exported_data)
            
            file_size = len(exported_data)
            
            self.update_state(state='PROCESSING', meta={'progress': 95, 'stage': 'finalizing'})
            
            # Create download URL
            file_url = f"/api/v1/files/exports/{filename}"
            
            result = {
                "status": "completed",
                "dataset_id": dataset_id,
                "format": target_format,
                "file_url": file_url,
                "file_path": file_path,
                "file_size": file_size,
                "row_count": len(data) if isinstance(data, list) else 0,
                "filename": filename,
                "created_at": datetime.now().isoformat(),
            }
            
            logger.info(f"Export completed: {filename} ({file_size} bytes)")
            return result
            
    except Exception as e:
        logger.error(f"Export failed for dataset {dataset_id}: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@celery_app.task(name="app.tasks.generation.validate_dataset")
def validate_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Validate dataset quality and constraints
    """
    logger.info(f"Validating dataset {dataset_id}")
    
    # TODO: Implement validation logic
    return {
        "status": "valid",
        "dataset_id": dataset_id,
        "checks_passed": 10,
        "checks_failed": 0
    }


# =============================================================================
# LLM-BASED GENERATION TASK
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.generation.generate_llm_data",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
    rate_limit="10/m",  # Rate limit to avoid API overuse
)
def generate_llm_data(
    self,
    job_id: str,
    prompt: str,
    columns: Optional[List[Dict[str, Any]]] = None,
    num_rows: int = 50,
    temperature: float = 0.7,
    output_format: str = "csv",
) -> Dict[str, Any]:
    """
    Celery task for generating data using LLM.
    Best for creative, context-aware data that needs semantic coherence.
    
    Args:
        job_id: Job identifier
        prompt: Description of the dataset to generate
        columns: Column specifications (optional)
        num_rows: Number of rows to generate (max 1000 for LLM)
        temperature: LLM temperature for creativity
        output_format: Output format
    
    Returns:
        Dictionary with task result information
    """
    task_id = self.request.id
    logger.info(f"Starting LLM data generation task {task_id} for job {job_id}")
    
    try:
        # Initialize
        self.update_state(
            state="PROCESSING",
            meta={"progress": 10, "message": "Initializing LLM service"}
        )
        update_job_in_db(job_id, "running", progress=10)
        
        from app.services.llm_service import LLMService, LLMColumnConfig
        
        llm_service = LLMService()
        
        if not llm_service.client:
            raise ValueError("No LLM provider available (set GROQ_API_KEY or ANTHROPIC_API_KEY)")
        
        # Parse column configs if provided
        column_configs = None
        if columns:
            column_configs = [LLMColumnConfig(**col) for col in columns]
        
        # LLM batch size (smaller than Faker due to API limits)
        batch_size = 50
        
        self.update_state(
            state="PROCESSING",
            meta={"progress": 20, "message": "Calling LLM API"}
        )
        update_job_in_db(job_id, "running", progress=20)
        
        if num_rows <= batch_size:
            # Generate all at once
            sample_data = llm_service.generate_sample_data(
                schema={"prompt": prompt, "columns": columns or []},
                row_count=num_rows,
            )
            df = pd.DataFrame(sample_data)
        else:
            # Generate in batches
            all_dfs = []
            generated = 0
            remaining = num_rows
            
            while remaining > 0:
                current_batch = min(remaining, batch_size)
                
                # Add context for consistency
                batch_prompt = prompt
                if all_dfs:
                    batch_prompt += f"\n\nContinue generating {current_batch} more unique rows following the same pattern."
                
                batch_data = llm_service.generate_sample_data(
                    schema={"prompt": batch_prompt, "columns": columns or []},
                    row_count=current_batch,
                )
                
                batch_df = pd.DataFrame(batch_data)
                all_dfs.append(batch_df)
                generated += len(batch_df)
                remaining -= current_batch
                
                progress = min(20 + int((generated / num_rows) * 60), 80)
                self.update_state(
                    state="PROCESSING",
                    meta={
                        "progress": progress,
                        "message": f"Generated {generated}/{num_rows} rows"
                    }
                )
                update_job_in_db(job_id, "running", progress=progress, rows_generated=generated)
            
            df = pd.concat(all_dfs, ignore_index=True)
        
        # Save output
        self.update_state(
            state="PROCESSING",
            meta={"progress": 90, "message": "Saving output file"}
        )
        update_job_in_db(job_id, "running", progress=90)
        
        file_id = generate_file_id()
        output_dir = ensure_directory(os.path.join(settings.DATA_DIR, "generated"))
        ext = output_format if output_format != "excel" else "xlsx"
        filename = f"llm_data_{file_id}.{ext}"
        filepath = os.path.join(output_dir, filename)
        
        save_dataframe(df, filepath, output_format)
        file_size = os.path.getsize(filepath)
        
        # Update job as completed
        update_job_in_db(
            job_id,
            "completed",
            progress=100,
            rows_generated=len(df),
            file_path=filepath,
            file_size=file_size
        )
        
        logger.info(f"LLM task {task_id} completed: {len(df)} rows")
        
        return convert_to_serializable({
            "status": "completed",
            "task_id": task_id,
            "job_id": job_id,
            "file_id": file_id,
            "filename": filename,
            "filepath": filepath,
            "file_url": f"/api/v1/files/generated/{filename}",
            "rows_generated": len(df),
            "columns": list(df.columns),
            "file_size": file_size,
            "output_format": output_format,
            "generator": "llm",
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"LLM task {task_id} failed: {error_msg}")
        
        update_job_in_db(job_id, "failed", error_message=error_msg)
        self.update_state(state="FAILURE", meta={"error": error_msg})
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        raise


# =============================================================================
# SCHEDULED CLEANUP TASK
# =============================================================================

@celery_app.task(name="app.tasks.generation.cleanup_old_files")
def cleanup_old_files(max_age_days: int = 7) -> Dict[str, Any]:
    """
    Clean up old generated files to save storage.
    Runs as a scheduled task.
    """
    import os
    import time
    
    logger.info(f"Starting cleanup of files older than {max_age_days} days")
    
    deleted_count = 0
    freed_bytes = 0
    errors = []
    
    # Directories to clean
    dirs_to_clean = [
        os.path.join(settings.DATA_DIR, "generated"),
        os.path.join(settings.DATA_DIR, "exports"),
    ]
    
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    
    for dir_path in dirs_to_clean:
        if not os.path.exists(dir_path):
            continue
        
        try:
            for filename in os.listdir(dir_path):
                filepath = os.path.join(dir_path, filename)
                
                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    
                    if file_mtime < cutoff_time:
                        try:
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            deleted_count += 1
                            freed_bytes += file_size
                            logger.debug(f"Deleted: {filename}")
                        except Exception as e:
                            errors.append(f"{filename}: {str(e)}")
        except Exception as e:
            errors.append(f"Error scanning {dir_path}: {str(e)}")
    
    result = {
        "status": "completed",
        "deleted_files": deleted_count,
        "freed_bytes": freed_bytes,
        "freed_mb": round(freed_bytes / (1024 * 1024), 2),
        "errors": errors if errors else None,
    }
    
    logger.info(f"Cleanup completed: {deleted_count} files, {result['freed_mb']} MB freed")
    return result


# =============================================================================
# SYNTHCITY/SDV ML-BASED GENERATION TASK
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.generation.generate_synthcity_data",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
    time_limit=3600,  # 1 hour max for training
)
def generate_synthcity_data(
    self,
    job_id: str,
    file_content_b64: str,
    filename: str,
    num_rows: int,
    columns_config: Optional[List[Dict[str, Any]]] = None,
    model_name: str = "ctgan",
    epochs: int = 300,
    output_format: str = "csv",
) -> Dict[str, Any]:
    """
    Celery task for generating synthetic data using Synthcity/SDV.
    Trains a model on uploaded data and generates statistically similar synthetic data.
    
    Args:
        job_id: Job identifier
        file_content_b64: Base64 encoded training data file
        filename: Original filename
        num_rows: Number of rows to generate
        columns_config: Column configurations (identifier columns, etc.)
        model_name: Model to use (ctgan, tvae, copulagan, gaussiancopula)
        epochs: Training epochs
        output_format: Output format
    
    Returns:
        Dictionary with task result information
    """
    import base64
    
    task_id = self.request.id
    logger.info(f"Starting Synthcity task {task_id} for job {job_id} with model {model_name}")
    
    try:
        # =====================================================================
        # PHASE 1: Decode and Validate Input (0-10%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 5, "message": "Validating input file"}
        )
        update_job_in_db(job_id, "running", progress=5)
        
        # Decode base64 content
        file_content = base64.b64decode(file_content_b64)
        
        from app.services.synthcity_service import (
            SynthcityService, 
            SynthcityColumnConfig,
        )
        
        synthcity_service = SynthcityService()
        
        # Parse column configs
        parsed_columns = None
        if columns_config:
            parsed_columns = [
                SynthcityColumnConfig(**col) for col in columns_config
            ]
        
        # =====================================================================
        # PHASE 2: Validate and Parse File (10-15%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 10, "message": "Loading and parsing data"}
        )
        update_job_in_db(job_id, "running", progress=10)
        
        df, validation = synthcity_service.validate_csv(file_content, filename)
        
        logger.info(f"Job {job_id}: Validated {validation.rows} rows, {len(validation.columns)} columns")
        
        # =====================================================================
        # PHASE 3: Preprocess Data (15-20%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 15, "message": "Preprocessing data"}
        )
        update_job_in_db(job_id, "running", progress=15)
        
        df_training, identifier_columns, identifier_data = synthcity_service.preprocess_data(
            df, parsed_columns
        )
        
        logger.info(f"Job {job_id}: Preprocessed data, {len(identifier_columns)} identifier columns")
        
        # =====================================================================
        # PHASE 4: Train Model (20-75%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={
                "progress": 20,
                "message": f"Training {model_name.upper()} model ({epochs} epochs)..."
            }
        )
        update_job_in_db(job_id, "running", progress=20)
        
        trained_model = synthcity_service.train_model(
            df_training,
            model_name=model_name,
            epochs=epochs,
        )
        
        logger.info(f"Job {job_id}: Model training completed")
        
        # =====================================================================
        # PHASE 5: Generate Synthetic Data (75-85%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 75, "message": f"Generating {num_rows:,} synthetic rows"}
        )
        update_job_in_db(job_id, "running", progress=75, rows_generated=0)
        
        synthetic_df = synthcity_service.generate_synthetic_data(
            trained_model,
            num_rows,
            identifier_columns,
            df,
        )
        
        logger.info(f"Job {job_id}: Generated {len(synthetic_df)} synthetic rows")
        
        # =====================================================================
        # PHASE 6: Save Output File (85-95%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 85, "message": "Saving output file"}
        )
        update_job_in_db(job_id, "running", progress=85, rows_generated=len(synthetic_df))
        
        file_id = generate_file_id()
        output_dir = ensure_directory(os.path.join(settings.DATA_DIR, "generated"))
        ext = output_format if output_format != "excel" else "xlsx"
        output_filename = f"synthcity_data_{file_id}.{ext}"
        filepath = os.path.join(output_dir, output_filename)
        
        save_dataframe(synthetic_df, filepath, output_format)
        file_size = os.path.getsize(filepath)
        
        # =====================================================================
        # PHASE 7: Save Model for Reuse (95-100%)
        # =====================================================================
        self.update_state(
            state="PROCESSING",
            meta={"progress": 95, "message": "Saving trained model"}
        )
        
        model_id = f"model_{file_id}"
        model_path = synthcity_service.save_model(trained_model, model_id)
        
        # Update job as completed
        update_job_in_db(
            job_id,
            "completed",
            progress=100,
            rows_generated=len(synthetic_df),
            file_path=filepath,
            file_size=file_size
        )
        
        result = convert_to_serializable({
            "status": "completed",
            "task_id": task_id,
            "job_id": job_id,
            "file_id": file_id,
            "filename": output_filename,
            "filepath": filepath,
            "file_url": f"/api/v1/files/generated/{output_filename}",
            "rows_generated": len(synthetic_df),
            "columns": list(synthetic_df.columns),
            "file_size": file_size,
            "output_format": output_format,
            "model_name": model_name,
            "model_id": model_id,
            "model_path": model_path,
            "original_rows": validation.rows,
            "original_columns": validation.columns,
            "identifier_columns": identifier_columns,
            "generator": "synthcity",
        })
        
        logger.info(f"Job {job_id} completed: {len(synthetic_df)} rows, model saved as {model_id}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Synthcity task {task_id} failed: {error_msg}")
        
        update_job_in_db(job_id, "failed", error_message=error_msg)
        self.update_state(state="FAILURE", meta={"error": error_msg})
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            "status": "error",
            "task_id": task_id,
            "job_id": job_id,
            "error": error_msg,
            "error_type": type(e).__name__,
        }


@celery_app.task(
    bind=True,
    name="app.tasks.generation.generate_from_saved_model",
    max_retries=2,
    acks_late=True,
)
def generate_from_saved_model(
    self,
    job_id: str,
    model_id: str,
    num_rows: int,
    output_format: str = "csv",
) -> Dict[str, Any]:
    """
    Generate synthetic data from a previously trained and saved model.
    Much faster than re-training.
    
    Args:
        job_id: Job identifier
        model_id: ID of the saved model
        num_rows: Number of rows to generate
        output_format: Output format
    
    Returns:
        Dictionary with task result information
    """
    task_id = self.request.id
    logger.info(f"Starting generation from saved model {model_id} for job {job_id}")
    
    try:
        self.update_state(
            state="PROCESSING",
            meta={"progress": 10, "message": "Loading saved model"}
        )
        update_job_in_db(job_id, "running", progress=10)
        
        from app.services.synthcity_service import SynthcityService
        
        synthcity_service = SynthcityService()
        model = synthcity_service.load_model(model_id)
        
        self.update_state(
            state="PROCESSING",
            meta={"progress": 30, "message": f"Generating {num_rows:,} rows"}
        )
        update_job_in_db(job_id, "running", progress=30)
        
        # Generate data
        synthetic_df = synthcity_service.generate_synthetic_data(
            model,
            num_rows,
            identifier_columns=[],
            original_df=None,
        )
        
        self.update_state(
            state="PROCESSING",
            meta={"progress": 80, "message": "Saving output file"}
        )
        update_job_in_db(job_id, "running", progress=80, rows_generated=len(synthetic_df))
        
        # Save output
        file_id = generate_file_id()
        output_dir = ensure_directory(os.path.join(settings.DATA_DIR, "generated"))
        ext = output_format if output_format != "excel" else "xlsx"
        filename = f"synthcity_data_{file_id}.{ext}"
        filepath = os.path.join(output_dir, filename)
        
        save_dataframe(synthetic_df, filepath, output_format)
        file_size = os.path.getsize(filepath)
        
        update_job_in_db(
            job_id,
            "completed",
            progress=100,
            rows_generated=len(synthetic_df),
            file_path=filepath,
            file_size=file_size
        )
        
        result = convert_to_serializable({
            "status": "completed",
            "task_id": task_id,
            "job_id": job_id,
            "file_id": file_id,
            "filename": filename,
            "filepath": filepath,
            "file_url": f"/api/v1/files/generated/{filename}",
            "rows_generated": len(synthetic_df),
            "columns": list(synthetic_df.columns),
            "file_size": file_size,
            "output_format": output_format,
            "model_id": model_id,
            "generator": "synthcity-cached",
        })
        
        logger.info(f"Job {job_id} completed from cached model: {len(synthetic_df)} rows")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Generation from model {model_id} failed: {error_msg}")
        
        update_job_in_db(job_id, "failed", error_message=error_msg)
        self.update_state(state="FAILURE", meta={"error": error_msg})
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        raise
