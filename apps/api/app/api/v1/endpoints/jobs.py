"""
Generation job endpoints for Synthesize.io API.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import (
    DBSession,
    CurrentUser,
    Pagination,
    Sorting,
)
from app.services.generation_service import GenerationService
from app.services.dataset_service import DatasetService
from app.utils.storage import FileStorage
from app.schemas.dataset import (
    GenerationJobResponse,
    GenerationJobDetailResponse,
    GenerationJobListResponse,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# JOB LISTING
# =============================================================================

@router.get(
    "/",
    response_model=GenerationJobListResponse,
    summary="List generation jobs",
)
def list_jobs(
    db: DBSession,
    user: CurrentUser,
    pagination: Pagination,
    sorting: Sorting,
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status: pending, running, completed, failed, cancelled",
    ),
    dataset_id: Optional[UUID] = Query(None, description="Filter by dataset ID"),
):
    """List current user's generation jobs."""
    generation_service = GenerationService(db)
    jobs, total = generation_service.list_jobs(
        user_id=user.id,
        dataset_id=dataset_id,
        status=status_filter,
        page=pagination.page,
        per_page=pagination.per_page,
        sort_by=sorting.sort_by or "created_at",
        sort_order=sorting.sort_order or "desc",
    )
    
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    return GenerationJobListResponse(
        items=[
            GenerationJobResponse(
                id=j.id,
                dataset_id=j.dataset_id,
                dataset_name=j.dataset.name if j.dataset else None,
                status=j.status,
                row_count=j.row_count,
                output_format=j.output_format,
                progress=j.progress or 0,
                error_message=j.error_message,
                file_size=j.file_size,
                created_at=j.created_at,
                started_at=j.started_at,
                completed_at=j.completed_at,
            )
            for j in jobs
        ],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1,
    )


@router.get(
    "/stats",
    summary="Get job statistics",
)
def get_job_stats(
    db: DBSession,
    user: CurrentUser,
):
    """Get aggregated statistics about user's generation jobs."""
    generation_service = GenerationService(db)
    stats = generation_service.get_user_stats(user.id)
    
    return {
        "total_jobs": stats.get("total_jobs", 0),
        "completed_jobs": stats.get("completed_jobs", 0),
        "failed_jobs": stats.get("failed_jobs", 0),
        "pending_jobs": stats.get("pending_jobs", 0),
        "running_jobs": stats.get("running_jobs", 0),
        "total_rows_generated": stats.get("total_rows_generated", 0),
        "total_api_credits_used": stats.get("total_credits_used", 0),
        "avg_completion_time_seconds": stats.get("avg_completion_time", 0),
    }


# =============================================================================
# JOB DETAILS
# =============================================================================

@router.get(
    "/{job_id}",
    response_model=GenerationJobDetailResponse,
    summary="Get job details",
)
def get_job(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get detailed information about a generation job."""
    generation_service = GenerationService(db)
    job = generation_service.get_job(job_id, user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return GenerationJobDetailResponse(
        id=job.id,
        dataset_id=job.dataset_id,
        dataset_name=job.dataset.name if job.dataset else None,
        status=job.status,
        row_count=job.row_count,
        output_format=job.output_format,
        progress=job.progress or 0,
        error_message=job.error_message,
        error_details=job.error_details,
        file_path=job.file_path,
        file_size=job.file_size,
        generation_options=job.generation_options,
        llm_model=job.llm_model,
        llm_tokens_used=job.llm_tokens_used,
        credits_used=job.credits_used,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        duration_seconds=(
            (job.completed_at - job.started_at).total_seconds()
            if job.completed_at and job.started_at
            else None
        ),
    )


@router.get(
    "/{job_id}/status",
    summary="Get job status",
)
def get_job_status(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Get lightweight status information about a job."""
    generation_service = GenerationService(db)
    job = generation_service.get_job(job_id, user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    return {
        "id": str(job.id),
        "status": job.status,
        "progress": job.progress or 0,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


# =============================================================================
# JOB ACTIONS
# =============================================================================

@router.post(
    "/{job_id}/cancel",
    response_model=MessageResponse,
    summary="Cancel job",
)
def cancel_job(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Cancel a pending or running generation job."""
    generation_service = GenerationService(db)
    success = generation_service.cancel_job(job_id, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel job - it may already be completed or cancelled",
        )
    
    return MessageResponse(message="Job cancelled successfully")


@router.post(
    "/{job_id}/retry",
    response_model=GenerationJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed job",
)
def retry_job(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Retry a failed generation job."""
    generation_service = GenerationService(db)
    new_job = generation_service.retry_job(job_id, user.id)
    
    if not new_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot retry job - only failed jobs can be retried",
        )
    
    return GenerationJobResponse(
        id=new_job.id,
        dataset_id=new_job.dataset_id,
        status=new_job.status,
        row_count=new_job.row_count,
        output_format=new_job.output_format,
        progress=new_job.progress or 0,
        created_at=new_job.created_at,
    )


@router.delete(
    "/{job_id}",
    response_model=MessageResponse,
    summary="Delete job",
)
def delete_job(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
):
    """Delete a completed or cancelled job and its files."""
    generation_service = GenerationService(db)
    success = generation_service.delete_job(job_id, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete job - only completed or cancelled jobs can be deleted",
        )
    
    return MessageResponse(message="Job deleted successfully")


# =============================================================================
# FILE DOWNLOAD
# =============================================================================

@router.get(
    "/{job_id}/download",
    summary="Download generated file",
)
def download_job_file(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser = None,
    token: Optional[str] = Query(None, description="Optional JWT token for browser downloads"),
):
    """Download the generated data file for a completed job.
    
    Supports both Authorization header and token query parameter for browser downloads.
    """
    from app.core.security import decode_token
    
    # If user not authenticated via header, try query token
    if user is None and token:
        try:
            payload = decode_token(token)
            user_id = UUID(payload.get("sub"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
    elif user:
        user_id = user.id
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    generation_service = GenerationService(db)
    job = generation_service.get_job(job_id, user_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed yet",
        )
    
    if not job.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file available for this job",
        )
    
    # Get file from storage
    storage = FileStorage()
    file_content = storage.get_file(job.file_path)
    
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    # Determine content type based on format
    content_type_map = {
        "json": "application/json",
        "csv": "text/csv",
        "xml": "application/xml",
        "parquet": "application/octet-stream",
        "sql": "text/plain",
    }
    content_type = content_type_map.get(job.output_format, "application/octet-stream")
    
    # Generate filename
    dataset_name = job.dataset.name if job.dataset else "dataset"
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in dataset_name)
    filename = f"{safe_name}_{job.id}.{job.output_format}"
    
    return StreamingResponse(
        iter([file_content]),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(file_content)),
        },
    )


@router.get(
    "/{job_id}/preview",
    summary="Preview generated data",
)
def preview_job_file(
    job_id: UUID,
    db: DBSession,
    user: CurrentUser,
    rows: int = Query(10, ge=1, le=100, description="Number of rows to preview"),
):
    """Preview the first N rows of generated data."""
    generation_service = GenerationService(db)
    job = generation_service.get_job(job_id, user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed yet",
        )
    
    # Get preview data
    preview_data = generation_service.get_job_preview(job_id, rows)
    
    return {
        "job_id": str(job_id),
        "format": job.output_format,
        "total_rows": job.row_count,
        "preview_rows": rows,
        "data": preview_data,
    }
