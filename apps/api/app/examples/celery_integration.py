"""
Example integration of Celery tasks with FastAPI endpoints
This shows how FastAPI (brain) delegates to Celery workers (muscles)
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.tasks.generation import generate_dataset, export_dataset, validate_dataset
from app.tasks.notifications import send_email, trigger_webhook

router = APIRouter(prefix="/api/v1/generation", tags=["Data Generation"])


# Request/Response Models
class GenerationRequest(BaseModel):
    """User's data generation request"""
    description: str
    row_count: int = 1000
    format: str = "csv"
    sample_data: list[Dict[str, Any]]
    constraints: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    """Immediate response when job is queued"""
    job_id: str
    status: str = "queued"
    message: str = "Generation job queued successfully"


class JobStatusResponse(BaseModel):
    """Job status check response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: Optional[int] = None  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Endpoints
@router.post("/generate", response_model=GenerationResponse)
async def create_generation_job(request: GenerationRequest):
    """
    Create a data generation job
    
    FastAPI (Brain):
    - Validates the request
    - Creates job record
    - Queues task to Celery
    - Returns immediately (< 200ms)
    
    Celery Worker (Muscle):
    - Picks up task from queue
    - Generates full dataset (2-10 minutes)
    - Saves file
    - Sends notification
    """
    # TODO: Create job record in database
    job_id = "job_123456"  # Generate unique ID
    
    # Queue the heavy work to Celery worker
    task = generate_dataset.delay(
        job_id=job_id,
        request_data={
            "description": request.description,
            "row_count": request.row_count,
            "format": request.format,
            "sample_data": request.sample_data,
            "constraints": request.constraints
        }
    )
    
    # FastAPI returns immediately, doesn't wait for completion
    return GenerationResponse(
        job_id=job_id,
        status="queued",
        message=f"Generation job queued. Check status at /jobs/{job_id}"
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Check job status
    
    FastAPI (Brain):
    - Queries job status from database/Redis
    - Returns current progress
    - Fast operation (< 50ms)
    """
    # TODO: Query from database or Redis
    # For now, return mock status
    
    return JobStatusResponse(
        job_id=job_id,
        status="processing",
        progress=45,
        result=None
    )


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    
    FastAPI (Brain):
    - Sends cancellation signal
    - Updates database
    
    Celery Worker (Muscle):
    - Receives signal
    - Stops processing
    - Cleans up resources
    """
    # TODO: Send cancellation signal to Celery
    # from celery import current_app
    # current_app.control.revoke(task_id, terminate=True)
    
    return {"message": f"Job {job_id} cancellation requested"}


@router.post("/export/{dataset_id}")
async def export_dataset_endpoint(
    dataset_id: str,
    target_format: str = "json"
):
    """
    Export dataset to different format
    
    Delegated to Celery worker because:
    - File format conversion is CPU-intensive
    - Large files take time to process
    - Don't want to block API requests
    """
    task = export_dataset.delay(dataset_id, target_format)
    
    return {
        "task_id": task.id,
        "message": f"Export to {target_format} started",
        "status_url": f"/api/v1/generation/tasks/{task.id}"
    }


@router.post("/validate/{dataset_id}")
async def validate_dataset_endpoint(dataset_id: str):
    """
    Validate dataset quality
    
    Delegated to Celery because validation can be slow:
    - Check all rows for constraints
    - Verify referential integrity
    - Calculate statistics
    """
    task = validate_dataset.delay(dataset_id)
    
    return {
        "task_id": task.id,
        "message": "Validation started"
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Generic task status checker
    Works for any Celery task
    """
    from celery.result import AsyncResult
    from app.celery_app import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
        "info": result.info
    }


# Example: Synchronous notification (bad practice)
@router.post("/send-email-bad")
async def send_email_sync(to: str, subject: str, body: str):
    """
    ❌ BAD PRACTICE: Synchronous email sending
    
    Problems:
    - Blocks the API request
    - User waits 2-5 seconds for SMTP
    - If SMTP fails, request fails
    - Reduces API throughput
    """
    import smtplib
    # ... SMTP code here (takes 2-5 seconds)
    return {"message": "Email sent"}  # User waited too long!


# Example: Asynchronous notification (good practice)
@router.post("/send-email-good")
async def send_email_async(to: str, subject: str, body: str):
    """
    ✅ GOOD PRACTICE: Async email via Celery
    
    Benefits:
    - API returns immediately (< 50ms)
    - Email sent in background
    - Retries if SMTP fails
    - User doesn't wait
    """
    task = send_email.delay(to, subject, body)
    
    return {
        "message": "Email queued for sending",
        "task_id": task.id
    }  # Returns immediately!


# Example: Using FastAPI BackgroundTasks (for lightweight tasks)
@router.post("/trigger-webhook-light")
async def trigger_webhook_light(
    background_tasks: BackgroundTasks,
    webhook_url: str,
    event: str,
    payload: Dict[str, Any]
):
    """
    Alternative for LIGHTWEIGHT background tasks
    
    Use FastAPI BackgroundTasks when:
    - Task is very fast (< 1 second)
    - Doesn't need retries
    - Doesn't need monitoring
    
    Use Celery when:
    - Task is slow (> 1 second)
    - Needs retries
    - Needs progress tracking
    """
    # This runs after response is sent, but in same process
    def trigger_webhook_sync():
        import httpx
        httpx.post(webhook_url, json={"event": event, **payload})
    
    background_tasks.add_task(trigger_webhook_sync)
    
    return {"message": "Webhook will be triggered"}
