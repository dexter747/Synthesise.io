"""
Customer Query schemas for Synthesize.io API.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse


class QueryStatus(str, Enum):
    """Status for customer contact queries"""
    NEW = "new"
    READ = "read"
    RESPONDED = "responded"
    CLOSED = "closed"


class QueryCategory(str, Enum):
    """Category for customer queries"""
    GENERAL = "general"
    SALES = "sales"
    SUPPORT = "support"
    PARTNERSHIP = "partnership"
    OTHER = "other"


# =============================================================================
# Request Schemas
# =============================================================================

class CustomerQueryCreate(BaseModel):
    """Schema for creating a new customer query (public contact form)"""
    
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the person")
    email: EmailStr = Field(..., description="Contact email address")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    subject: str = Field(..., min_length=5, max_length=255, description="Query subject")
    message: str = Field(..., min_length=10, max_length=5000, description="Query message")
    category: QueryCategory = Field(default=QueryCategory.GENERAL, description="Query category")


class CustomerQueryUpdate(BaseModel):
    """Schema for admin to update a customer query"""
    
    status: Optional[QueryStatus] = None
    admin_notes: Optional[str] = Field(None, max_length=5000)


class CustomerQueryBulkAction(BaseModel):
    """Schema for bulk actions on queries"""
    
    query_ids: List[UUID]
    action: str = Field(..., description="Action: mark_read, mark_responded, close")


# =============================================================================
# Response Schemas
# =============================================================================

class ResponderInfo(BaseSchema):
    """Brief info about who responded to a query"""
    
    id: UUID
    name: str
    email: str


class CustomerQueryResponse(BaseSchema, TimestampMixin):
    """Full customer query response for admin view"""
    
    id: UUID
    name: str
    email: str
    company: Optional[str]
    phone: Optional[str]
    subject: str
    message: str
    category: str
    status: QueryStatus
    admin_notes: Optional[str]
    responded_at: Optional[datetime]
    responded_by: Optional[ResponderInfo]
    source: str


class CustomerQueryListResponse(BaseSchema, TimestampMixin):
    """Slim query response for list view"""
    
    id: UUID
    name: str
    email: str
    company: Optional[str]
    subject: str
    category: str
    status: QueryStatus
    responded_at: Optional[datetime]


class CustomerQuerySubmitResponse(BaseModel):
    """Response after submitting a query"""
    
    success: bool = True
    message: str = "Your query has been submitted successfully. We'll get back to you soon!"
    reference_id: UUID


class CustomerQueryStats(BaseModel):
    """Statistics about customer queries"""
    
    total: int
    new: int
    read: int
    responded: int
    closed: int
    avg_response_time_hours: Optional[float]


# Type alias for paginated queries
PaginatedQueriesResponse = PaginatedResponse[CustomerQueryListResponse]
