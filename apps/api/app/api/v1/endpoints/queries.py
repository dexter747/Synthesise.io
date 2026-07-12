"""
Customer Query endpoints for Synthesize.io API.

Provides:
- Public endpoint for submitting contact queries (no auth required)
- Admin endpoints for managing queries
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Body, status, Request
from sqlalchemy import func, select, and_
from sqlalchemy.orm import joinedload

from app.api.deps import (
    DBSession,
    AdminUser,
    Pagination,
)
from app.models import CustomerQuery, QueryStatus, User
from app.schemas.query import (
    CustomerQueryCreate,
    CustomerQueryUpdate,
    CustomerQueryBulkAction,
    CustomerQueryResponse,
    CustomerQueryListResponse,
    CustomerQuerySubmitResponse,
    CustomerQueryStats,
    QueryStatus as SchemaQueryStatus,
)
from app.schemas.base import PaginatedResponse, MessageResponse


router = APIRouter()


# =============================================================================
# PUBLIC ENDPOINTS (No Auth Required)
# =============================================================================

@router.post(
    "/submit",
    response_model=CustomerQuerySubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact query",
)
async def submit_query(
    db: DBSession,
    request: Request,
    query_data: CustomerQueryCreate,
):
    """
    Submit a contact query from the public website.
    No authentication required.
    """
    # Create the query
    new_query = CustomerQuery(
        name=query_data.name,
        email=query_data.email,
        company=query_data.company,
        phone=query_data.phone,
        subject=query_data.subject,
        message=query_data.message,
        category=query_data.category.value,
        status=QueryStatus.NEW,
        source="website",
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    # TODO: Send notification email to admin team
    # TODO: Send confirmation email to user
    
    return CustomerQuerySubmitResponse(
        success=True,
        message="Your query has been submitted successfully. We'll get back to you soon!",
        reference_id=new_query.id,
    )


# =============================================================================
# ADMIN ENDPOINTS (Admin Auth Required)
# =============================================================================

@router.get(
    "/admin/list",
    response_model=PaginatedResponse[CustomerQueryListResponse],
    summary="List all customer queries (Admin)",
)
async def list_queries(
    db: DBSession,
    admin: AdminUser,
    pagination: Pagination,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name, email, subject"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
):
    """Get paginated list of customer queries for admin view."""
    
    # Build query
    query = select(CustomerQuery)
    
    # Apply filters
    if status_filter:
        try:
            status_enum = QueryStatus(status_filter)
            query = query.where(CustomerQuery.status == status_enum)
        except ValueError:
            pass
    
    if category:
        query = query.where(CustomerQuery.category == category)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            CustomerQuery.name.ilike(search_pattern) |
            CustomerQuery.email.ilike(search_pattern) |
            CustomerQuery.subject.ilike(search_pattern)
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0
    
    # Apply sorting
    sort_column = getattr(CustomerQuery, sort_by, CustomerQuery.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    query = query.offset(offset).limit(pagination.per_page)
    
    # Execute query
    result = db.execute(query).scalars().all()
    
    # Calculate pagination info
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    # Map to response
    items = [
        CustomerQueryListResponse(
            id=q.id,
            name=q.name,
            email=q.email,
            company=q.company,
            subject=q.subject,
            category=q.category,
            status=SchemaQueryStatus(q.status.value),
            responded_at=q.responded_at,
            created_at=q.created_at,
            updated_at=q.updated_at,
        )
        for q in result
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1,
    )


@router.get(
    "/admin/stats",
    response_model=CustomerQueryStats,
    summary="Get query statistics (Admin)",
)
async def get_query_stats(
    db: DBSession,
    admin: AdminUser,
):
    """Get statistics about customer queries."""
    
    # Get counts by status
    total = db.execute(select(func.count(CustomerQuery.id))).scalar() or 0
    new_count = db.execute(
        select(func.count(CustomerQuery.id)).where(CustomerQuery.status == QueryStatus.NEW)
    ).scalar() or 0
    read_count = db.execute(
        select(func.count(CustomerQuery.id)).where(CustomerQuery.status == QueryStatus.READ)
    ).scalar() or 0
    responded_count = db.execute(
        select(func.count(CustomerQuery.id)).where(CustomerQuery.status == QueryStatus.RESPONDED)
    ).scalar() or 0
    closed_count = db.execute(
        select(func.count(CustomerQuery.id)).where(CustomerQuery.status == QueryStatus.CLOSED)
    ).scalar() or 0
    
    # Calculate average response time (for responded queries)
    avg_response = db.execute(
        select(
            func.avg(
                func.extract('epoch', CustomerQuery.responded_at) - 
                func.extract('epoch', CustomerQuery.created_at)
            ) / 3600
        ).where(CustomerQuery.responded_at.isnot(None))
    ).scalar()
    
    return CustomerQueryStats(
        total=total,
        new=new_count,
        read=read_count,
        responded=responded_count,
        closed=closed_count,
        avg_response_time_hours=round(avg_response, 2) if avg_response else None,
    )


@router.get(
    "/admin/{query_id}",
    response_model=CustomerQueryResponse,
    summary="Get query details (Admin)",
)
async def get_query_detail(
    db: DBSession,
    admin: AdminUser,
    query_id: UUID,
):
    """Get full details of a specific customer query."""
    
    query = db.execute(
        select(CustomerQuery)
        .options(joinedload(CustomerQuery.responded_by))
        .where(CustomerQuery.id == query_id)
    ).scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Auto-mark as read if it's new
    if query.status == QueryStatus.NEW:
        query.status = QueryStatus.READ
        db.commit()
        db.refresh(query)
    
    return CustomerQueryResponse(
        id=query.id,
        name=query.name,
        email=query.email,
        company=query.company,
        phone=query.phone,
        subject=query.subject,
        message=query.message,
        category=query.category,
        status=SchemaQueryStatus(query.status.value),
        admin_notes=query.admin_notes,
        responded_at=query.responded_at,
        responded_by={
            "id": query.responded_by.id,
            "name": query.responded_by.name,
            "email": query.responded_by.email,
        } if query.responded_by else None,
        source=query.source,
        created_at=query.created_at,
        updated_at=query.updated_at,
    )


@router.patch(
    "/admin/{query_id}",
    response_model=CustomerQueryResponse,
    summary="Update query status (Admin)",
)
async def update_query(
    db: DBSession,
    admin: AdminUser,
    query_id: UUID,
    update_data: CustomerQueryUpdate,
):
    """Update a customer query's status or admin notes."""
    
    query = db.execute(
        select(CustomerQuery).where(CustomerQuery.id == query_id)
    ).scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Update fields
    if update_data.status is not None:
        query.status = QueryStatus(update_data.status.value)
        
        # Track response time
        if update_data.status == SchemaQueryStatus.RESPONDED and not query.responded_at:
            query.responded_at = datetime.utcnow()
            query.responded_by_id = admin.id
    
    if update_data.admin_notes is not None:
        query.admin_notes = update_data.admin_notes
    
    db.commit()
    db.refresh(query)
    
    # Reload with relationship
    db.refresh(query, ["responded_by"])
    
    return CustomerQueryResponse(
        id=query.id,
        name=query.name,
        email=query.email,
        company=query.company,
        phone=query.phone,
        subject=query.subject,
        message=query.message,
        category=query.category,
        status=SchemaQueryStatus(query.status.value),
        admin_notes=query.admin_notes,
        responded_at=query.responded_at,
        responded_by={
            "id": query.responded_by.id,
            "name": query.responded_by.name,
            "email": query.responded_by.email,
        } if query.responded_by else None,
        source=query.source,
        created_at=query.created_at,
        updated_at=query.updated_at,
    )


@router.delete(
    "/admin/{query_id}",
    response_model=MessageResponse,
    summary="Delete query (Admin)",
)
async def delete_query(
    db: DBSession,
    admin: AdminUser,
    query_id: UUID,
):
    """Delete a customer query."""
    
    query = db.execute(
        select(CustomerQuery).where(CustomerQuery.id == query_id)
    ).scalar_one_or_none()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    db.delete(query)
    db.commit()
    
    return MessageResponse(
        message="Query deleted successfully",
        success=True,
    )


@router.post(
    "/admin/bulk-action",
    response_model=MessageResponse,
    summary="Bulk action on queries (Admin)",
)
async def bulk_action(
    db: DBSession,
    admin: AdminUser,
    action_data: CustomerQueryBulkAction,
):
    """Perform bulk actions on multiple queries."""
    
    # Get queries
    queries = db.execute(
        select(CustomerQuery).where(CustomerQuery.id.in_(action_data.query_ids))
    ).scalars().all()
    
    if not queries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No queries found"
        )
    
    action = action_data.action.lower()
    updated_count = 0
    
    for query in queries:
        if action == "mark_read":
            if query.status == QueryStatus.NEW:
                query.status = QueryStatus.READ
                updated_count += 1
        elif action == "mark_responded":
            if query.status not in [QueryStatus.RESPONDED, QueryStatus.CLOSED]:
                query.status = QueryStatus.RESPONDED
                query.responded_at = datetime.utcnow()
                query.responded_by_id = admin.id
                updated_count += 1
        elif action == "close":
            if query.status != QueryStatus.CLOSED:
                query.status = QueryStatus.CLOSED
                updated_count += 1
        elif action == "delete":
            db.delete(query)
            updated_count += 1
    
    db.commit()
    
    return MessageResponse(
        message=f"Successfully performed '{action}' on {updated_count} queries",
        success=True,
    )
