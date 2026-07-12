"""
Base schema classes and common types for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional, Generic, TypeVar, List, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for created_at/updated_at fields."""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str
    success: bool = True


class ErrorDetail(BaseModel):
    """Error detail structure."""
    
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response wrapper."""
    
    error: ErrorDetail


class IDResponse(BaseModel):
    """Response with just an ID."""
    
    id: UUID


class SuccessResponse(BaseModel):
    """Generic success response."""
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
