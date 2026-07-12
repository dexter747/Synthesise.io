"""
Example usage of LLM Service with FastAPI
Shows how FastAPI uses LLM for quick sample generation (< 5s)
Then delegates heavy work to Celery workers
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.llm_service import get_llm_service
from app.tasks.generation import generate_dataset

router = APIRouter(prefix="/api/v1/ai", tags=["AI Generation"])


class GenerationRequest(BaseModel):
    """User's natural language request"""
    description: str
    row_count: Optional[int] = 1000


class SampleResponse(BaseModel):
    """Quick response with LLM-generated sample"""
    request_id: str
    refined_schema: Dict[str, Any]
    sample_data: List[Dict[str, Any]]
    message: str


@router.post("/refine", response_model=Dict[str, Any])
async def refine_user_request(description: str):
    """
    Step 1: Refine user's natural language into structured schema
    
    FastAPI calls LLM directly (fast operation, 1-3 seconds)
    No need for Celery since it's quick
    
    Example:
    POST /api/v1/ai/refine
    {
        "description": "I need customer data with names, emails, and purchase history"
    }
    
    Returns:
    {
        "columns": ["customer_id", "name", "email", "total_purchases", "last_purchase_date"],
        "types": {...},
        "constraints": {...}
    }
    """
    llm = get_llm_service()
    
    try:
        refined = llm.refine_request(description)
        return refined
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@router.post("/generate-sample", response_model=SampleResponse)
async def generate_sample(request: GenerationRequest):
    """
    Step 2: Generate small sample using LLM (10-50 rows)
    
    FastAPI + LLM (takes 2-5 seconds, acceptable for API)
    User reviews this sample before approving full generation
    
    Workflow:
    1. Refine description → schema
    2. Generate 10-50 sample rows with LLM
    3. Return to user for approval
    4. User approves → Queue full generation to Celery
    """
    llm = get_llm_service()
    
    try:
        # Step 1: Refine request
        schema = llm.refine_request(request.description)
        
        # Step 2: Generate small sample (10 rows)
        sample_data = llm.generate_sample_data(schema, row_count=10)
        
        # TODO: Store in database with request_id
        request_id = "req_12345"
        
        return SampleResponse(
            request_id=request_id,
            refined_schema=schema,
            sample_data=sample_data,
            message="Sample generated. Review and approve to generate full dataset."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample generation failed: {str(e)}")


@router.post("/approve-and-generate")
async def approve_and_generate_full(
    request_id: str,
    row_count: int = 1000,
    modifications: Optional[Dict[str, Any]] = None
):
    """
    Step 3: User approves sample, queue full generation to Celery
    
    FastAPI (Brain):
    - Validates approval
    - Queues job to Celery
    - Returns immediately (< 100ms)
    
    Celery Worker (Muscle):
    - Uses approved sample as template
    - Generates 1K-1M rows (takes 2-10 minutes)
    - Uses Data Factory, not LLM (LLM too slow for large datasets)
    """
    # TODO: Retrieve sample from database using request_id
    sample_data = [{"name": "John", "email": "john@example.com"}]  # Placeholder
    
    # Apply user modifications if any
    if modifications:
        # Update schema based on user tweaks
        pass
    
    # Queue to Celery (Heavy work happens here)
    task = generate_dataset.delay(
        job_id=f"job_{request_id}",
        request_data={
            "sample_data": sample_data,
            "row_count": row_count,
            "format": "csv"
        }
    )
    
    return {
        "job_id": f"job_{request_id}",
        "task_id": task.id,
        "status": "queued",
        "message": f"Generating {row_count} rows in background. Check status at /jobs/job_{request_id}"
    }


@router.post("/analyze-sample")
async def analyze_sample(sample_data: List[Dict[str, Any]]):
    """
    Optional: Analyze sample data patterns
    
    Helps data factory understand:
    - Value distributions
    - Column relationships
    - Constraints to maintain
    """
    llm = get_llm_service()
    
    try:
        analysis = llm.analyze_data_patterns(sample_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/suggest-improvements")
async def suggest_schema_improvements(schema: Dict[str, Any]):
    """
    Optional: Get AI suggestions for schema improvements
    
    Example suggestions:
    - Add created_at/updated_at timestamps
    - Add status field for state tracking
    - Better data types for certain columns
    - Recommended indexes
    """
    llm = get_llm_service()
    
    try:
        suggestions = llm.suggest_improvements(schema)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")


# Complete workflow example
"""
COMPLETE USER FLOW:

1. User enters: "I need customer data for testing"
   ↓
2. POST /api/v1/ai/refine
   FastAPI + LLM (2s) → Returns structured schema
   ↓
3. POST /api/v1/ai/generate-sample
   FastAPI + LLM (3s) → Returns 10 sample rows
   ↓
4. User reviews sample in UI:
   ✓ "Looks good!" or "Modify name format"
   ↓
5. POST /api/v1/ai/approve-and-generate
   FastAPI (100ms) → Queues to Celery → Returns job_id
   ↓
6. Celery Worker picks up task
   Data Factory (5 min) → Generates 100K rows
   ↓
7. Webhook/Email notification
   User downloads dataset

KEY POINTS:
- LLM used for SMALL tasks (refinement, samples) - runs in FastAPI
- Data Factory used for LARGE generation - runs in Celery
- FastAPI never blocks on heavy work
- User gets quick feedback with sample, then waits for full dataset
"""
