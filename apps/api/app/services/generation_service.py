"""
Generation service for Synthesize.io API.

Handles data generation job orchestration, preview generation, and job management.
"""
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    AuthorizationError,
    QuotaExceededError,
    GenerationError,
)
from app.models import (
    Dataset,
    GenerationJob,
    GenerationRequest,
    Subscription,
    SubscriptionPlan,
    UsageRecord,
    JobStatus,
    JobPriority,
)
from app.schemas.dataset import (
    GenerationOptions,
    DataPreviewResponse,
)
from app.services.data_factory import DataFactory


class GenerationService:
    """Service for data generation operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.data_factory = DataFactory()
    
    # =========================================================================
    # JOB MANAGEMENT
    # =========================================================================
    
    def create_job(
        self,
        data: GenerationRequest,
        user_id: UUID,
    ) -> GenerationJob:
        """Create a new generation job."""
        # Get dataset
        dataset = self._get_dataset(data.dataset_id, user_id)
        
        # Check quota
        self._check_row_quota(user_id, data.row_count)
        
        # Create job
        job = GenerationJob(
            dataset_id=data.dataset_id,
            user_id=user_id,
            organization_id=dataset.organization_id,
            status=JobStatus.PENDING,
            row_count=data.row_count,
            rows_generated=0,
            output_format=data.output_format,
            generation_options=data.options.model_dump() if data.options else None,
            priority=data.priority if data.priority else JobPriority.NORMAL,
            progress=0.0,
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Queue the job for processing
        self._queue_job(job)
        
        return job
    
    def get_job(self, job_id: UUID, user_id: UUID = None) -> Optional[GenerationJob]:
        """Get job by ID, optionally checking authorization."""
        result = self.db.execute(
            select(GenerationJob)
            .options(
                selectinload(GenerationJob.request),
                selectinload(GenerationJob.dataset),
            )
            .where(GenerationJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job and user_id:
            # Check authorization if user_id provided
            if job.user_id != user_id:
                return None
        
        return job
    
    def get_job_or_raise(self, job_id: UUID) -> GenerationJob:
        """Get job by ID or raise NotFoundError."""
        job = self.get_job(job_id)
        if not job:
            raise NotFoundError("Job", str(job_id))
        return job
    
    def get_job_with_auth(
        self, job_id: UUID, user_id: UUID
    ) -> GenerationJob:
        """Get job with authorization check."""
        job = self.get_job_or_raise(job_id)
        
        if job.user_id != user_id:
            # Check if user has access via organization
            if job.organization_id:
                from app.services.organization_service import OrganizationService
                org_service = OrganizationService(self.db)
                if not org_service.is_member(job.organization_id, user_id):
                    raise AuthorizationError("You don't have access to this job")
            else:
                raise AuthorizationError("You don't have access to this job")
        
        return job
    
    def cancel_job(self, job_id: UUID, user_id: UUID) -> GenerationJob:
        """Cancel a pending or running job."""
        job = self.get_job_with_auth(job_id, user_id)
        
        if job.status not in ["pending", "running"]:
            raise ValidationError(f"Cannot cancel job in {job.status} status")
        
        job.status = "canceled"
        job.completed_at = datetime.utcnow()
        job.error_message = "Canceled by user"
        
        self.db.commit()
        self.db.refresh(job)
        
        # TODO: Send cancellation to Celery worker
        
        return job
    
    def retry_job(self, job_id: UUID, user_id: UUID) -> GenerationJob:
        """Retry a failed job."""
        old_job = self.get_job_with_auth(job_id, user_id)
        
        if old_job.status != "failed":
            raise ValidationError("Can only retry failed jobs")
        
        # Check quota for retry
        self._check_row_quota(user_id, old_job.row_count)
        
        # Create new job
        new_job = GenerationJob(
            dataset_id=old_job.dataset_id,
            user_id=user_id,
            organization_id=old_job.organization_id,
            status="pending",
            row_count=old_job.row_count,
            rows_generated=0,
            output_format=old_job.output_format,
            options=old_job.options,
            webhook_url=old_job.webhook_url,
            priority=old_job.priority,
            progress=0.0,
            schema_snapshot=old_job.schema_snapshot,
        )
        
        self.db.add(new_job)
        self.db.commit()
        self.db.refresh(new_job)
        
        # Queue for processing
        self._queue_job(new_job)
        
        return new_job
    
    def delete_job(self, job_id: UUID, user_id: UUID) -> bool:
        """Delete a job."""
        try:
            job = self.get_job_with_auth(job_id, user_id)
            
            # Only allow deleting completed, failed, or canceled jobs
            if job.status in ["pending", "running"]:
                return False
            
            self.db.delete(job)
            self.db.commit()
            return True
        except (NotFoundError, AuthorizationError):
            return False
    
    def get_job_preview(
        self, job_id: UUID, user_id: UUID, limit: int = 10
    ) -> list[dict]:
        """Get preview data from a completed job."""
        job = self.get_job_with_auth(job_id, user_id)
        
        if job.status != "completed":
            raise ValidationError("Job must be completed to preview data")
        
        # Get the dataset and read preview data
        if job.dataset:
            from app.services.dataset_service import DatasetService
            dataset_service = DatasetService(self.db)
            return dataset_service.get_preview(job.dataset.id, user_id, limit)
        
        return []
    
    # =========================================================================
    # JOB LISTING
    # =========================================================================
    
    def list_all_jobs(
        self,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[UUID] = None,
        status_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[GenerationJob], int]:
        """List all generation jobs for admin. No user filtering by default."""
        query = (
            select(GenerationJob)
            .options(
                selectinload(GenerationJob.user),
                selectinload(GenerationJob.dataset)
            )
        )
        count_query = select(func.count(GenerationJob.id))
        
        # Optional user filter
        if user_id:
            query = query.where(GenerationJob.user_id == user_id)
            count_query = count_query.where(GenerationJob.user_id == user_id)
        
        # Status filter
        if status_filter:
            query = query.where(GenerationJob.status == status_filter)
            count_query = count_query.where(GenerationJob.status == status_filter)
        
        # Get total
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sort
        sort_column = getattr(GenerationJob, sort_by, GenerationJob.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Paginate
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        jobs = list(result.scalars().all())
        
        return jobs, total
    
    def list_jobs(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        dataset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[GenerationJob], int]:
        """List generation jobs."""
        query = (
            select(GenerationJob)
            .join(GenerationRequest)
            .options(selectinload(GenerationJob.request))
        )
        count_query = select(func.count(GenerationJob.id)).join(GenerationRequest)
        
        # Filter by ownership through request
        if organization_id:
            query = query.where(GenerationRequest.organization_id == organization_id)
            count_query = count_query.where(GenerationRequest.organization_id == organization_id)
        else:
            query = query.where(GenerationRequest.user_id == user_id)
            count_query = count_query.where(GenerationRequest.user_id == user_id)
        
        # Note: dataset_id filter not applicable as GenerationJob links to GenerationRequest
        # Filter by status
        if status:
            query = query.where(GenerationJob.status == status)
            count_query = count_query.where(GenerationJob.status == status)
        
        # Get total
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sort
        sort_column = getattr(GenerationJob, sort_by, GenerationJob.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Paginate
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        jobs = list(result.scalars().all())
        
        return jobs, total
    
    def get_active_jobs(self, user_id: UUID) -> list[GenerationJob]:
        """Get user's active (pending/running) jobs."""
        result = self.db.execute(
            select(GenerationJob)
            .join(GenerationRequest)
            .options(selectinload(GenerationJob.request))
            .where(GenerationRequest.user_id == user_id)
            .where(GenerationJob.status.in_(["pending", "running"]))
            .order_by(GenerationJob.created_at.desc())
        )
        return list(result.scalars().all())
    
    # =========================================================================
    # DATA PREVIEW
    # =========================================================================
    
    def generate_preview(
        self,
        dataset_id: UUID,
        user_id: UUID,
        row_count: int = 10,
        options: Optional[GenerationOptions] = None,
    ) -> DataPreviewResponse:
        """Generate preview data (synchronous, limited rows)."""
        dataset = self._get_dataset(dataset_id, user_id)
        
        if row_count > 100:
            raise ValidationError("Preview is limited to 100 rows")
        
        # Generate preview data
        schema = dataset.schema_definition
        opts = options.model_dump() if options else {}
        
        try:
            data = self.data_factory.generate(
                schema=schema,
                row_count=row_count,
                options=opts,
            )
        except Exception as e:
            raise GenerationError(f"Failed to generate preview: {str(e)}")
        
        return DataPreviewResponse(
            dataset_id=dataset_id,
            row_count=len(data),
            data=data,
            schema_definition=schema,
        )
    
    # =========================================================================
    # JOB PROCESSING (Called by Celery worker)
    # =========================================================================
    
    def start_job(self, job_id: UUID) -> GenerationJob:
        """Mark job as started (called by worker)."""
        job = self.get_job_or_raise(job_id)
        
        job.status = "running"
        job.started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def update_job_progress(
        self,
        job_id: UUID,
        rows_generated: int,
        progress: float,
    ) -> GenerationJob:
        """Update job progress (called by worker)."""
        job = self.get_job_or_raise(job_id)
        
        job.rows_generated = rows_generated
        job.progress = min(progress, 100.0)
        
        # Estimate completion time
        if progress > 0 and job.started_at:
            elapsed = (datetime.utcnow() - job.started_at).total_seconds()
            remaining = (elapsed / progress) * (100 - progress)
            job.estimated_completion = datetime.utcnow() + timedelta(seconds=remaining)
        
        self.db.commit()
        
        return job
    
    def complete_job(
        self,
        job_id: UUID,
        file_path: str,
        file_size: int,
    ) -> GenerationJob:
        """Mark job as completed (called by worker)."""
        job = self.get_job_or_raise(job_id)
        
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        job.rows_generated = job.row_count
        job.file_path = file_path
        job.file_size_bytes = file_size
        job.download_expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Update dataset stats
        dataset_result = self.db.execute(
            select(Dataset).where(Dataset.id == job.dataset_id)
        )
        dataset = dataset_result.scalar_one_or_none()
        if dataset:
            dataset.row_count = (dataset.row_count or 0) + job.row_count
            dataset.last_generated_at = datetime.utcnow()
        
        # Record usage
        usage = UsageRecord(
            user_id=job.user_id,
            organization_id=job.organization_id,
            usage_type="rows_generated",
            quantity=job.row_count,
            unit="rows",
            recorded_at=datetime.utcnow(),
        )
        self.db.add(usage)
        
        self.db.commit()
        self.db.refresh(job)
        
        # TODO: Trigger webhook if configured
        if job.webhook_url:
            self._trigger_webhook(job)
        
        return job
    
    def fail_job(
        self,
        job_id: UUID,
        error_message: str,
    ) -> GenerationJob:
        """Mark job as failed (called by worker)."""
        job = self.get_job_or_raise(job_id)
        
        job.status = "failed"
        job.completed_at = datetime.utcnow()
        job.error_message = error_message
        
        self.db.commit()
        self.db.refresh(job)
        
        # TODO: Trigger failure webhook if configured
        if job.webhook_url:
            self._trigger_webhook(job)
        
        return job
    
    # =========================================================================
    # DOWNLOAD
    # =========================================================================
    
    def get_download_url(
        self, job_id: UUID, user_id: UUID
    ) -> Optional[str]:
        """Get download URL for completed job."""
        job = self.get_job_with_auth(job_id, user_id)
        
        if job.status != "completed":
            raise ValidationError("Job is not completed")
        
        if not job.file_path:
            raise ValidationError("No file available for download")
        
        if job.download_expires_at and job.download_expires_at < datetime.utcnow():
            raise ValidationError("Download link has expired")
        
        # Generate signed URL or return file path
        # For local storage, return the file path
        # For S3/cloud storage, generate signed URL
        return job.file_path
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_dataset(self, dataset_id: UUID, user_id: UUID) -> Dataset:
        """Get dataset with authorization check."""
        from app.services.dataset_service import DatasetService
        dataset_service = DatasetService(self.db)
        return dataset_service.get_with_auth(dataset_id, user_id)
    
    def _check_row_quota(self, user_id: UUID, row_count: int) -> None:
        """Check if user has enough row quota."""
        # Get subscription
        result = self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            features = subscription.plan.features or {}
            max_rows = features.get("max_rows_per_month", 10000)
            max_per_request = features.get("max_rows_per_request", 10000)
        else:
            # Free tier
            max_rows = 1000
            max_per_request = 100
        
        # Check per-request limit
        if row_count > max_per_request:
            raise QuotaExceededError(
                "rows_per_request",
                limit=max_per_request,
                used=row_count,
            )
        
        # Check monthly quota
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
        usage_result = self.db.execute(
            select(func.sum(UsageRecord.datasets_created))
            .where(UsageRecord.user_id == user_id)
            .where(UsageRecord.date >= month_start)
        )
        used_rows = usage_result.scalar() or 0
        
        if used_rows + row_count > max_rows:
            raise QuotaExceededError(
                "monthly_rows",
                limit=max_rows,
                used=int(used_rows),
            )
    
    def _queue_job(self, job: GenerationJob) -> None:
        """Queue job for processing by Celery worker."""
        from app.tasks.generation import generate_dataset
        
        # Build request data for Celery task
        request_data = {
            "row_count": job.row_count,
            "output_format": job.output_format,
            "dataset_id": str(job.dataset_id),
            "priority": job.priority,
        }
        
        # Queue with Celery - use apply_async with explicit queue for reliability
        # The 'generation' queue is for production, 'celery' for simple local dev
        generate_dataset.apply_async(
            args=[str(job.id), request_data],
            queue='generation',  # Match the configured task_routes
        )
    
    def _trigger_webhook(self, job: GenerationJob) -> None:
        """Trigger webhook for job completion/failure."""
        # TODO: Implement webhook delivery
        pass
    
    def get_platform_stats(self) -> dict:
        """Get platform-wide generation statistics for admin dashboard."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now - timedelta(days=30)
        
        # Total jobs
        total_result = self.db.execute(
            select(func.count(GenerationJob.id))
        )
        total_jobs = total_result.scalar() or 0
        
        # Jobs today
        today_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.created_at >= today_start)
        )
        jobs_today = today_result.scalar() or 0
        
        # Jobs this month
        month_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.created_at >= month_start)
        )
        jobs_this_month = month_result.scalar() or 0
        
        # Total rows generated
        rows_result = self.db.execute(
            select(func.sum(GenerationJob.rows_generated))
            .where(GenerationJob.status == "completed")
        )
        total_rows = rows_result.scalar() or 0
        
        # Success/failure rates
        success_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.status == "completed")
        )
        successful_jobs = success_result.scalar() or 0
        
        failed_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.status == "failed")
        )
        failed_jobs = failed_result.scalar() or 0
        
        return {
            "total_jobs": total_jobs,
            "jobs_today": jobs_today,
            "jobs_this_month": jobs_this_month,
            "total_rows_generated": int(total_rows or 0),
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        }

    def get_user_stats(self, user_id: UUID) -> dict:
        """Get job statistics for a specific user."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now - timedelta(days=30)
        
        # Total jobs for user
        total_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.user_id == user_id)
        )
        total_jobs = total_result.scalar() or 0
        
        # Jobs today
        today_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.user_id == user_id)
            .where(GenerationJob.created_at >= today_start)
        )
        jobs_today = today_result.scalar() or 0
        
        # Pending jobs
        pending_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.user_id == user_id)
            .where(GenerationJob.status == JobStatus.PENDING)
        )
        pending_jobs = pending_result.scalar() or 0
        
        # Completed jobs
        completed_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.user_id == user_id)
            .where(GenerationJob.status == JobStatus.COMPLETED)
        )
        completed_jobs = completed_result.scalar() or 0
        
        # Failed jobs
        failed_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.user_id == user_id)
            .where(GenerationJob.status == JobStatus.FAILED)
        )
        failed_jobs = failed_result.scalar() or 0
        
        # Total rows generated
        rows_result = self.db.execute(
            select(func.sum(GenerationJob.rows_generated))
            .where(GenerationJob.user_id == user_id)
            .where(GenerationJob.status == JobStatus.COMPLETED)
        )
        total_rows = rows_result.scalar() or 0
        
        return {
            "total_jobs": total_jobs,
            "jobs_today": jobs_today,
            "pending_jobs": pending_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_rows_generated": int(total_rows or 0),
        }
    
    def get_jobs_over_time(self, start_date: datetime) -> dict:
        """
        Get job statistics over time.
        
        Args:
            start_date: Start date for the statistics.
            
        Returns:
            Dictionary with job count data.
        """
        from datetime import timedelta
        
        # Get total jobs
        total_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .where(GenerationJob.created_at >= start_date)
        )
        total_jobs = total_result.scalar() or 0
        
        # Get daily job counts
        daily_jobs = []
        current_date = start_date
        now = datetime.utcnow()
        
        while current_date < now:
            day_end = current_date + timedelta(days=1)
            day_count_result = self.db.execute(
                select(func.count(GenerationJob.id))
                .where(GenerationJob.created_at >= current_date)
                .where(GenerationJob.created_at < day_end)
            )
            day_count = day_count_result.scalar() or 0
            daily_jobs.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": day_count
            })
            current_date = day_end
        
        return {
            "total": total_jobs,
            "period_start": start_date.isoformat(),
            "period_end": now.isoformat(),
            "daily": daily_jobs
        }


# Dependency injection helper
def get_generation_service(db: AsyncSession) -> GenerationService:
    """Get generation service instance."""
    return GenerationService(db)
