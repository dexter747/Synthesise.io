"""
User service for Synthesize.io API.

Handles user CRUD operations, profile management, and user-related business logic.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DuplicateError,
    InvalidCredentialsError,
    NotFoundError,
    ValidationError,
)
from app.core.security import hash_password, verify_password
from app.models import User, Session, AuditLog, Dataset, GenerationJob, GenerationRequest
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPreferencesUpdate,
    AdminUserUpdate,
)


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    def get_by_id_or_raise(self, user_id: UUID) -> User:
        """Get user by ID or raise NotFoundError."""
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()
    
    def get_by_email_or_raise(self, email: str) -> User:
        """Get user by email or raise NotFoundError."""
        user = self.get_by_email(email)
        if not user:
            raise NotFoundError("User", email)
        return user
    
    def create(self, data: UserCreate) -> User:
        """Create a new user."""
        # Check for existing user
        existing = self.get_by_email(data.email)
        if existing:
            raise DuplicateError("User", "email", data.email)
        
        # Create user
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            status=data.status,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update(self, user_id: UUID, data: UserUpdate) -> User:
        """Update user profile."""
        user = self.get_by_id_or_raise(user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_preferences(
        self, user_id: UUID, data: UserPreferencesUpdate
    ) -> User:
        """Update user preferences."""
        user = self.get_by_id_or_raise(user_id)
        
        # Get current preferences or create empty dict
        preferences = user.preferences or {}
        
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        preferences.update(update_data)
        
        user.preferences = preferences
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def admin_update(self, user_id: UUID, data: AdminUserUpdate) -> User:
        """Admin update user (can change role, status, etc.)."""
        user = self.get_by_id_or_raise(user_id)
        
        # Check email uniqueness if changing email
        if data.email and data.email.lower() != user.email:
            existing = self.get_by_email(data.email)
            if existing:
                raise DuplicateError("User", "email", data.email)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "email" and value:
                value = value.lower()
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete(self, user_id: UUID) -> None:
        """Delete user (soft delete by setting status to deleted)."""
        user = self.get_by_id_or_raise(user_id)
        user.status = "deleted"
        user.deleted_at = datetime.utcnow()
        self.db.commit()
    
    def hard_delete(self, user_id: UUID) -> None:
        """Permanently delete user and all associated data."""
        user = self.get_by_id_or_raise(user_id)
        self.db.delete(user)
        self.db.commit()
    
    # =========================================================================
    # ADMIN USER MANAGEMENT
    # =========================================================================
    
    def suspend(self, user_id: UUID, reason: Optional[str] = None) -> None:
        """Suspend a user account."""
        from app.models import UserStatus
        user = self.get_by_id_or_raise(user_id)
        user.status = UserStatus.SUSPENDED
        self.db.commit()
    
    def reactivate(self, user_id: UUID) -> None:
        """Reactivate a suspended user account."""
        from app.models import UserStatus
        user = self.get_by_id_or_raise(user_id)
        user.status = UserStatus.ACTIVE
        self.db.commit()
    
    def change_role(self, user_id: UUID, new_role: str) -> None:
        """Change user's role (admin only)."""
        from app.models import UserRole
        valid_roles = ["user", "admin", "super_admin", "support", "analyst"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role: {new_role}. Must be one of {valid_roles}")
        
        user = self.get_by_id_or_raise(user_id)
        user.role = UserRole(new_role)
        self.db.commit()
    
    def change_subscription_tier(self, user_id: UUID, new_tier: str) -> None:
        """Manually change user's subscription tier (for technical overrides)."""
        valid_tiers = ["free", "starter", "professional", "business", "enterprise"]
        if new_tier not in valid_tiers:
            raise ValueError(f"Invalid tier: {new_tier}. Must be one of {valid_tiers}")
        
        user = self.get_by_id_or_raise(user_id)
        user.subscription_tier = new_tier
        self.db.commit()
    
    def admin_reset_password(self, user_id: UUID) -> str:
        """Admin reset password - generates a temporary password."""
        import secrets
        user = self.get_by_id_or_raise(user_id)
        temp_password = secrets.token_urlsafe(12)
        user.password_hash = hash_password(temp_password)
        user.password_changed_at = datetime.utcnow()
        self.db.commit()
        # In production, this would send an email with the temp password
        return temp_password
    
    # =========================================================================
    # PASSWORD OPERATIONS
    # =========================================================================
    
    def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        """Change user's password."""
        from app.core.exceptions import ValidationError
        
        user = self.get_by_id_or_raise(user_id)
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValidationError("Current password is incorrect", field="current_password")
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        self.db.commit()
    
    def reset_password(self, user_id: UUID, new_password: str) -> None:
        """Reset user's password (admin or password reset flow)."""
        user = self.get_by_id_or_raise(user_id)
        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        self.db.commit()
    
    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================
    
    def verify_email(self, user_id: UUID) -> None:
        """Mark user's email as verified."""
        user = self.get_by_id_or_raise(user_id)
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()
        self.db.commit()
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def record_login(
        self, user_id: UUID, ip_address: Optional[str] = None
    ) -> None:
        """Record successful login."""
        self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_login_at=datetime.utcnow(),
            )
        )
        self.db.commit()
    
    def get_sessions(self, user_id: UUID) -> list[Session]:
        """Get all active sessions for user."""
        result = self.db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.expires_at > datetime.utcnow())
            .order_by(Session.created_at.desc())
        )
        return list(result.scalars().all())
    
    def revoke_session(self, user_id: UUID, session_id: UUID) -> None:
        """Revoke a specific session."""
        result = self.db.execute(
            select(Session)
            .where(Session.id == session_id)
            .where(Session.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if session:
            self.db.delete(session)
            self.db.commit()
    
    def revoke_all_sessions(self, user_id: UUID, except_current: Optional[UUID] = None) -> int:
        """Revoke all sessions for user, optionally keeping current session."""
        query = select(Session).where(Session.user_id == user_id)
        if except_current:
            query = query.where(Session.id != except_current)
        
        result = self.db.execute(query)
        sessions = result.scalars().all()
        count = len(sessions)
        
        for session in sessions:
            self.db.delete(session)
        
        self.db.commit()
        return count
    
    # =========================================================================
    # STATISTICS & ACTIVITY
    # =========================================================================
    
    def get_platform_stats(self) -> dict:
        """Get platform-wide user statistics for admin dashboard."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Total users
        total_users_result = self.db.execute(
            select(func.count(User.id))
            .where(User.status != "deleted")
        )
        total_users = total_users_result.scalar() or 0
        
        # Active users (logged in within last 30 days)
        active_users_result = self.db.execute(
            select(func.count(User.id))
            .where(User.status == "active")
            .where(User.last_login_at >= month_start)
        )
        active_users = active_users_result.scalar() or 0
        
        # New users today
        new_today_result = self.db.execute(
            select(func.count(User.id))
            .where(User.created_at >= today_start)
        )
        new_users_today = new_today_result.scalar() or 0
        
        # New users this week
        new_week_result = self.db.execute(
            select(func.count(User.id))
            .where(User.created_at >= week_start)
        )
        new_users_this_week = new_week_result.scalar() or 0
        
        # New users this month
        new_month_result = self.db.execute(
            select(func.count(User.id))
            .where(User.created_at >= month_start)
        )
        new_users_this_month = new_month_result.scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_today": new_users_today,
            "new_users_this_week": new_users_this_week,
            "new_users_this_month": new_users_this_month,
        }
    
    def get_stats(self, user_id: UUID) -> dict:
        """Get user statistics."""
        # Datasets count
        datasets_result = self.db.execute(
            select(func.count(Dataset.id))
            .where(Dataset.user_id == user_id)
            .where(Dataset.deleted_at.is_(None))
        )
        datasets_count = datasets_result.scalar() or 0
        
        # Jobs stats (join with GenerationRequest to get user_id)
        jobs_result = self.db.execute(
            select(
                func.count(GenerationJob.id),
                func.sum(GenerationJob.rows_generated),
            )
            .join(GenerationRequest, GenerationJob.request_id == GenerationRequest.id)
            .where(GenerationRequest.user_id == user_id)
        )
        row = jobs_result.one()
        jobs_count = row[0] or 0
        total_rows = row[1] or 0
        
        # Completed/failed jobs
        completed_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .join(GenerationRequest, GenerationJob.request_id == GenerationRequest.id)
            .where(GenerationRequest.user_id == user_id)
            .where(GenerationJob.status == "completed")
        )
        completed_jobs = completed_result.scalar() or 0
        
        failed_result = self.db.execute(
            select(func.count(GenerationJob.id))
            .join(GenerationRequest, GenerationJob.request_id == GenerationRequest.id)
            .where(GenerationRequest.user_id == user_id)
            .where(GenerationJob.status == "failed")
        )
        failed_jobs = failed_result.scalar() or 0
        
        return {
            "total_datasets": datasets_count,
            "total_rows_generated": total_rows,
            "total_jobs": jobs_count,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "api_calls_this_month": 0,  # TODO: Implement API call tracking
            "storage_used_bytes": 0,  # TODO: Implement storage tracking
        }
    
    def get_activity(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[AuditLog]:
        """Get user activity log."""
        result = self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    # =========================================================================
    # LISTING & SEARCH
    # =========================================================================
    
    def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[User], int]:
        """List users with filtering and pagination."""
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.email.ilike(search_filter)) |
                (User.first_name.ilike(search_filter)) |
                (User.last_name.ilike(search_filter)) |
                (User.display_name.ilike(search_filter))
            )
            count_query = count_query.where(
                (User.email.ilike(search_filter)) |
                (User.first_name.ilike(search_filter)) |
                (User.last_name.ilike(search_filter)) |
                (User.display_name.ilike(search_filter))
            )
        
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        if status:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)
        else:
            # By default, exclude deleted users
            query = query.where(User.status != "deleted")
            count_query = count_query.where(User.status != "deleted")
        
        # Get total count
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    def get_signups_over_time(self, start_date: datetime = None) -> dict:
        """
        Get user signup statistics over time.
        
        Args:
            start_date: Start date for the statistics. Defaults to 30 days ago.
            
        Returns:
            Dictionary with signup data including daily counts.
        """
        from datetime import timedelta
        
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get total signups
        total_result = self.db.execute(
            select(func.count(User.id))
            .where(User.created_at >= start_date)
        )
        total_signups = total_result.scalar() or 0
        
        # Get daily signups - simplified version
        daily_signups = []
        current_date = start_date
        now = datetime.utcnow()
        
        while current_date < now:
            day_end = current_date + timedelta(days=1)
            day_count_result = self.db.execute(
                select(func.count(User.id))
                .where(User.created_at >= current_date)
                .where(User.created_at < day_end)
            )
            day_count = day_count_result.scalar() or 0
            daily_signups.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": day_count
            })
            current_date = day_end
        
        return {
            "total": total_signups,
            "period_start": start_date.isoformat(),
            "period_end": now.isoformat(),
            "daily": daily_signups
        }


# Dependency injection helper
def get_user_service(db: Session) -> UserService:
    """Get user service instance."""
    return UserService(db)
