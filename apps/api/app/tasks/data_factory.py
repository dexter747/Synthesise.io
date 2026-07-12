"""
Data Factory Tasks - Celery Workers for Synthetic Data Generation
==================================================================
Heavy processing tasks for Faker, Synthcity, and LLM generators.

Task Pattern:
1. FastAPI creates GenerationJob with status='pending'
2. Task picks up job, updates to 'processing'
3. Task generates data in batches with progress updates
4. Task saves result, updates job to 'completed' or 'failed'
5. Optional webhook notification on completion
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

from app.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_db_session():
    """Create a database session for Celery workers."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    engine = create_engine(settings.DATABASE_URL)
    return Session(engine)


def update_job_status(
    db,
    job_id: str,
    status: str,
    progress: int = 0,
    rows_generated: int = 0,
    error_message: str = None,
    result_url: str = None,
):
    """Update GenerationJob status in database."""
    from app.models import GenerationJob, GenerationRequest, JobStatus
    
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if job:
        job.status = JobStatus(status)
        job.progress_percent = progress
        job.rows_generated = rows_generated
        if error_message:
            job.error_message = error_message
        if status == "processing" and not job.started_at:
            job.started_at = datetime.utcnow()
        if status == "completed":
            job.completed_at = datetime.utcnow()
        
        # Also update the parent GenerationRequest
        if job.request:
            job.request.status = JobStatus(status)
        
        db.commit()
        logger.info(f"Job {job_id} updated: status={status}, progress={progress}%")


def save_dataframe(df: pd.DataFrame, job_id: str, format: str = "csv") -> str:
    """Save DataFrame to file and return URL."""
    output_dir = getattr(settings, 'DATA_OUTPUT_DIR', os.path.join(settings.DATA_DIR, "generated"))
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == "csv":
        filename = f"{job_id}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
    elif format == "json":
        filename = f"{job_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        df.to_json(filepath, orient="records", indent=2)
    elif format == "parquet":
        filename = f"{job_id}_{timestamp}.parquet"
        filepath = os.path.join(output_dir, filename)
        df.to_parquet(filepath, index=False)
    elif format == "excel":
        filename = f"{job_id}_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
    else:
        # Default to CSV
        filename = f"{job_id}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
    
    file_url = f"/api/v1/files/generated/{filename}"
    logger.info(f"Saved {len(df)} rows to {filepath}")
    
    return file_url


# =============================================================================
# FAKER GENERATION TASK
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.data_factory.generate_faker_data",
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=600,  # 10 minutes
    time_limit=660,
)
def generate_faker_data(
    self,
    job_id: str,
    columns_config: List[Dict[str, Any]],
    num_rows: int,
    locale: str = "en_US",
    output_format: str = "csv",
) -> Dict[str, Any]:
    """
    Generate synthetic data using Faker library.
    
    Args:
        job_id: GenerationJob UUID
        columns_config: List of column configurations with provider paths
        num_rows: Number of rows to generate
        locale: Faker locale (e.g., "en_US", "en_GB", "fr_FR")
        output_format: Output file format
    
    Returns:
        Dict with status, file_url, and metadata
    """
    from app.services.faker_service import get_faker_service, FakerColumnConfig
    
    logger.info(f"[Faker Task] Starting job {job_id}: {num_rows} rows, {len(columns_config)} columns")
    
    db = get_db_session()
    
    try:
        # Update job status
        update_job_status(db, job_id, "processing", progress=5)
        self.update_state(state='PROCESSING', meta={'progress': 5, 'stage': 'initializing'})
        
        # Initialize service
        faker_service = get_faker_service()
        
        # Parse column configs
        columns = [FakerColumnConfig(**col) for col in columns_config]
        
        # Validate all providers
        for col in columns:
            if not faker_service.validate_provider(col.provider):
                raise ValueError(f"Invalid Faker provider: {col.provider}")
        
        update_job_status(db, job_id, "processing", progress=10)
        self.update_state(state='PROCESSING', meta={'progress': 10, 'stage': 'generating'})
        
        # Generate in batches with progress updates
        batch_size = min(10000, num_rows)
        all_dfs = []
        generated = 0
        
        for batch_df in faker_service.generate_batched(columns, num_rows, locale=locale, batch_size=batch_size):
            all_dfs.append(batch_df)
            generated += len(batch_df)
            
            # Calculate progress (10-90% for generation)
            progress = 10 + int((generated / num_rows) * 80)
            update_job_status(db, job_id, "processing", progress=progress, rows_generated=generated)
            self.update_state(state='PROCESSING', meta={'progress': progress, 'rows': generated})
            
            logger.info(f"[Faker Task] Job {job_id}: Generated {generated}/{num_rows} rows")
        
        # Combine all batches
        df = pd.concat(all_dfs, ignore_index=True)
        faker_service.reset_unique()  # Clear unique value tracking
        
        update_job_status(db, job_id, "processing", progress=90, rows_generated=len(df))
        self.update_state(state='PROCESSING', meta={'progress': 90, 'stage': 'saving'})
        
        # Save result
        file_url = save_dataframe(df, job_id, output_format)
        
        # Update job as completed
        update_job_status(
            db, job_id, "completed",
            progress=100,
            rows_generated=len(df),
            result_url=file_url,
        )
        
        result = {
            "status": "completed",
            "job_id": job_id,
            "file_url": file_url,
            "rows_generated": len(df),
            "columns": len(columns),
            "format": output_format,
            "locale": locale,
        }
        
        logger.info(f"[Faker Task] Job {job_id} completed: {len(df)} rows")
        return result
        
    except Exception as e:
        logger.error(f"[Faker Task] Job {job_id} failed: {str(e)}")
        update_job_status(db, job_id, "failed", error_message=str(e))
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    finally:
        db.close()


# =============================================================================
# SYNTHCITY GENERATION TASK (ML-Based)
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.data_factory.generate_synthcity_data",
    max_retries=2,
    default_retry_delay=120,
    soft_time_limit=3600,  # 1 hour for training
    time_limit=3660,
)
def generate_synthcity_data(
    self,
    job_id: str,
    training_file_path: str,
    num_rows: int,
    model_name: str = "ctgan",
    epochs: int = 300,
    columns_config: List[Dict[str, Any]] = None,
    output_format: str = "csv",
    save_model: bool = True,
) -> Dict[str, Any]:
    """
    Train model on real data and generate synthetic data.
    
    Args:
        job_id: GenerationJob UUID
        training_file_path: Path to training CSV file
        num_rows: Number of synthetic rows to generate
        model_name: Model type (ctgan, tvae, copulagan, gaussiancopula)
        epochs: Training epochs
        columns_config: Column configurations (identifier handling)
        output_format: Output file format
        save_model: Whether to persist trained model
    
    Returns:
        Dict with status, file_url, model_id, and metadata
    """
    from app.services.synthcity_service import get_synthcity_service, SynthcityColumnConfig
    
    logger.info(f"[Synthcity Task] Starting job {job_id}: {num_rows} rows, model={model_name}")
    
    db = get_db_session()
    
    try:
        update_job_status(db, job_id, "processing", progress=5)
        self.update_state(state='PROCESSING', meta={'progress': 5, 'stage': 'loading_data'})
        
        synthcity_service = get_synthcity_service()
        
        # Load training data
        with open(training_file_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(training_file_path)
        training_df, validation = synthcity_service.validate_csv(file_content, filename)
        
        logger.info(f"[Synthcity Task] Loaded training data: {len(training_df)} rows, {len(training_df.columns)} columns")
        
        update_job_status(db, job_id, "processing", progress=15)
        self.update_state(state='PROCESSING', meta={'progress': 15, 'stage': 'preprocessing'})
        
        # Preprocess data
        columns_cfg = None
        if columns_config:
            columns_cfg = [SynthcityColumnConfig(**col) for col in columns_config]
        
        processed_df, identifier_cols, identifier_data = synthcity_service.preprocess_data(
            training_df, columns_cfg
        )
        
        update_job_status(db, job_id, "processing", progress=20)
        self.update_state(state='PROCESSING', meta={'progress': 20, 'stage': 'training'})
        
        # Train model (this is the slow part)
        logger.info(f"[Synthcity Task] Training {model_name} model...")
        model = synthcity_service.train_model(processed_df, model_name, epochs)
        
        update_job_status(db, job_id, "processing", progress=70)
        self.update_state(state='PROCESSING', meta={'progress': 70, 'stage': 'generating'})
        
        # Generate synthetic data
        synthetic_df = synthcity_service.generate_synthetic_data(
            model, num_rows, identifier_cols, training_df
        )
        
        update_job_status(db, job_id, "processing", progress=85, rows_generated=len(synthetic_df))
        self.update_state(state='PROCESSING', meta={'progress': 85, 'stage': 'saving'})
        
        # Save result
        file_url = save_dataframe(synthetic_df, job_id, output_format)
        
        # Optionally save model
        model_id = None
        if save_model:
            model_id = f"{job_id}_model"
            synthcity_service.save_model(model, model_id)
            logger.info(f"[Synthcity Task] Model saved: {model_id}")
        
        update_job_status(
            db, job_id, "completed",
            progress=100,
            rows_generated=len(synthetic_df),
            result_url=file_url,
        )
        
        result = {
            "status": "completed",
            "job_id": job_id,
            "file_url": file_url,
            "rows_generated": len(synthetic_df),
            "model_name": model_name,
            "model_id": model_id,
            "epochs": epochs,
            "training_rows": len(training_df),
            "format": output_format,
        }
        
        logger.info(f"[Synthcity Task] Job {job_id} completed: {len(synthetic_df)} rows")
        return result
        
    except Exception as e:
        logger.error(f"[Synthcity Task] Job {job_id} failed: {str(e)}")
        update_job_status(db, job_id, "failed", error_message=str(e))
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    finally:
        db.close()


# =============================================================================
# LLM GENERATION TASK
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.data_factory.generate_llm_data",
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=300,  # 5 minutes
    time_limit=360,
)
def generate_llm_data(
    self,
    job_id: str,
    columns_config: List[Dict[str, Any]],
    num_rows: int,
    context: str = None,
    style: str = "realistic",
    domain: str = None,
    output_format: str = "csv",
) -> Dict[str, Any]:
    """
    Generate creative data using LLM (Groq/Anthropic).
    Best for: product descriptions, reviews, bios, narrative content.
    
    Args:
        job_id: GenerationJob UUID
        columns_config: List of column configurations with descriptions
        num_rows: Number of rows (limited to 1000 for LLM)
        context: Overall context for the dataset
        style: Data style (realistic, creative, formal, casual)
        domain: Domain (healthcare, finance, ecommerce, etc.)
        output_format: Output file format
    
    Returns:
        Dict with status, file_url, and metadata
    """
    from app.services.llm_service import get_llm_service, LLMColumnConfig, LLMGenerateRequest
    
    # Limit rows for LLM (expensive)
    num_rows = min(num_rows, 1000)
    
    logger.info(f"[LLM Task] Starting job {job_id}: {num_rows} rows, style={style}")
    
    db = get_db_session()
    
    try:
        update_job_status(db, job_id, "processing", progress=5)
        self.update_state(state='PROCESSING', meta={'progress': 5, 'stage': 'initializing'})
        
        llm_service = get_llm_service()
        
        # Build request
        columns = [LLMColumnConfig(**col) for col in columns_config]
        request = LLMGenerateRequest(
            num_rows=num_rows,
            columns=columns,
            context=context,
            style=style,
            domain=domain,
        )
        
        update_job_status(db, job_id, "processing", progress=10)
        self.update_state(state='PROCESSING', meta={'progress': 10, 'stage': 'generating'})
        
        # Progress callback
        def progress_callback(current, total):
            progress = 10 + int((current / total) * 80)
            update_job_status(db, job_id, "processing", progress=progress, rows_generated=current)
            self.update_state(state='PROCESSING', meta={'progress': progress, 'rows': current})
        
        # Generate using sync method for Celery
        df = llm_service.generate_creative_data_sync(
            request,
            batch_size=25,
            progress_callback=progress_callback,
        )
        
        update_job_status(db, job_id, "processing", progress=90, rows_generated=len(df))
        self.update_state(state='PROCESSING', meta={'progress': 90, 'stage': 'saving'})
        
        # Save result
        file_url = save_dataframe(df, job_id, output_format)
        
        update_job_status(
            db, job_id, "completed",
            progress=100,
            rows_generated=len(df),
            result_url=file_url,
        )
        
        result = {
            "status": "completed",
            "job_id": job_id,
            "file_url": file_url,
            "rows_generated": len(df),
            "columns": len(columns),
            "style": style,
            "domain": domain,
            "format": output_format,
            "provider": llm_service.provider,
        }
        
        logger.info(f"[LLM Task] Job {job_id} completed: {len(df)} rows")
        return result
        
    except Exception as e:
        logger.error(f"[LLM Task] Job {job_id} failed: {str(e)}")
        update_job_status(db, job_id, "failed", error_message=str(e))
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    finally:
        db.close()


# =============================================================================
# UNIFIED GENERATION TASK (Auto-selects generator)
# =============================================================================

@celery_app.task(
    bind=True,
    name="app.tasks.data_factory.generate_unified",
    max_retries=3,
    default_retry_delay=60,
)
def generate_unified(
    self,
    job_id: str,
    generator_type: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Unified generation task that routes to the appropriate generator.
    
    Args:
        job_id: GenerationJob UUID
        generator_type: "faker", "synthcity", or "llm"
        config: Generator-specific configuration
    
    Returns:
        Result from the selected generator
    """
    logger.info(f"[Unified Task] Job {job_id}: routing to {generator_type}")
    
    if generator_type == "faker":
        return generate_faker_data(
            job_id=job_id,
            columns_config=config.get("columns", []),
            num_rows=config.get("num_rows", 1000),
            locale=config.get("locale", "en_US"),
            output_format=config.get("format", "csv"),
        )
    
    elif generator_type == "synthcity":
        return generate_synthcity_data(
            job_id=job_id,
            training_file_path=config.get("training_file_path"),
            num_rows=config.get("num_rows", 1000),
            model_name=config.get("model", "ctgan"),
            epochs=config.get("epochs", 300),
            columns_config=config.get("columns"),
            output_format=config.get("format", "csv"),
            save_model=config.get("save_model", True),
        )
    
    elif generator_type == "llm":
        return generate_llm_data(
            job_id=job_id,
            columns_config=config.get("columns", []),
            num_rows=config.get("num_rows", 100),
            context=config.get("context"),
            style=config.get("style", "realistic"),
            domain=config.get("domain"),
            output_format=config.get("format", "csv"),
        )
    
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")
