"""
Pytest configuration and fixtures for Synthesize.io API tests.
"""
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import app and dependencies
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models import (
    User, Organization, OrganizationMember, SubscriptionPlan,
    Subscription, Dataset, GenerationJob,
    APIKey, Webhook, UserStatus, UserRole, DataFormat
)


# ============================================================================
# Database Fixtures
# ============================================================================

# Use SQLite for testing (in-memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db: Session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def test_user_data() -> dict:
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest.fixture
def test_user(db: Session, test_user_data: dict) -> User:
    """Create a test user in the database."""
    user = User(
        id=uuid.uuid4(),
        email=test_user_data["email"],
        password_hash=hash_password(test_user_data["password"]),
        first_name="Test",
        last_name="User",
        display_name=test_user_data["full_name"],
        status=UserStatus.ACTIVE,
        email_verified=True,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db: Session) -> User:
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123!"),
        first_name="Admin",
        last_name="User",
        display_name="Admin User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        email_verified=True,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_superadmin_user(db: Session) -> User:
    """Create a test superadmin user."""
    user = User(
        id=uuid.uuid4(),
        email="superadmin@example.com",
        password_hash=hash_password("SuperAdminPassword123!"),
        first_name="Super",
        last_name="Admin",
        display_name="Super Admin User",
        role=UserRole.SUPER_ADMIN,
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for the test user."""
    token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(hours=1),
        additional_claims={"email": test_user.email, "role": test_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin_user: User) -> dict:
    """Create authentication headers for the admin user."""
    token = create_access_token(
        subject=str(test_admin_user.id),
        expires_delta=timedelta(hours=1),
        additional_claims={"email": test_admin_user.email, "role": test_admin_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superadmin_auth_headers(test_superadmin_user: User) -> dict:
    """Create authentication headers for the superadmin user."""
    token = create_access_token(
        subject=str(test_superadmin_user.id),
        expires_delta=timedelta(hours=1),
        additional_claims={"email": test_superadmin_user.email, "role": test_superadmin_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Organization Fixtures
# ============================================================================

@pytest.fixture
def test_organization(db: Session, test_user: User) -> Organization:
    """Create a test organization."""
    from app.models import OrganizationRole
    
    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug="test-organization",
        owner_id=test_user.id,
    )
    db.add(org)
    
    # Add owner as admin member
    member = OrganizationMember(
        id=uuid.uuid4(),
        organization_id=org.id,
        user_id=test_user.id,
        role=OrganizationRole.ADMIN,
    )
    db.add(member)
    
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_organization_member(db: Session, test_organization: Organization, test_user: User) -> OrganizationMember:
    """Get the organization member for the test user in the test organization."""
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == test_organization.id,
        OrganizationMember.user_id == test_user.id
    ).first()
    return member


# ============================================================================
# Subscription Fixtures
# ============================================================================

@pytest.fixture
def test_subscription_plan(db: Session) -> SubscriptionPlan:
    """Create a test subscription plan."""
    from app.models import SubscriptionTier
    
    plan = SubscriptionPlan(
        id=uuid.uuid4(),
        name="Pro",
        tier=SubscriptionTier.PRO,
        description="Pro plan for testing",
        monthly_price_cents=2900,
        annual_price_cents=29000,
        currency="USD",
        monthly_data_limit_gb=100.0,
        max_datasets=50,
        max_api_keys=10,
        max_team_members=5,
        api_rate_limit_per_minute=1000,
        retention_days=90,
        features={"advanced_types": True, "priority_support": True},
        is_active=True,
        is_public=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@pytest.fixture
def test_user_subscription(db: Session, test_user: User, test_subscription_plan: SubscriptionPlan) -> Subscription:
    """Create a test user subscription."""
    from app.models import SubscriptionStatus, BillingCycle
    
    subscription = Subscription(
        id=uuid.uuid4(),
        user_id=test_user.id,
        plan_id=test_subscription_plan.id,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle=BillingCycle.MONTHLY,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


# ============================================================================
# Dataset Fixtures
# ============================================================================

@pytest.fixture
def test_dataset(db: Session, test_user: User) -> Dataset:
    """Create a test dataset."""
    dataset = Dataset(
        id=uuid.uuid4(),
        name="Test Dataset",
        description="A test dataset",
        user_id=test_user.id,
        row_count=1000,
        column_count=10,
        format=DataFormat.CSV,
        size_bytes=1024,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@pytest.fixture
def test_schema_field(db: Session, test_dataset: Dataset):
    """Create a test schema field."""
    from app.models import SchemaField
    
    field = SchemaField(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        name="email",
        display_name="Email Address",
        data_type="email",
        constraints={"nullable": False},
        order_index=0,
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field
#     """SchemaField model doesn't exist - schema stored as JSONB in Dataset"""
#     pass


# ============================================================================
# Job Fixtures
# ============================================================================

@pytest.fixture
def test_generation_request(db: Session, test_user: User) -> "GenerationRequest":
    """Create a test generation request."""
    from app.models import GenerationRequest, DataFormat
    
    request = GenerationRequest(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Test Generation",
        description="Generate test data",
        row_count=1000,
        output_format=DataFormat.CSV,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@pytest.fixture
def test_job(db: Session, test_user: "User", test_generation_request: "GenerationRequest") -> GenerationJob:
    """Create a test generation job."""
    from app.models import JobStatus, JobPriority
    
    job = GenerationJob(
        id=uuid.uuid4(),
        request_id=test_generation_request.id,
        user_id=test_user.id,
        status=JobStatus.PENDING,
        priority=JobPriority.NORMAL,
        row_count=1000,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def completed_job(db: Session, test_user: "User", test_generation_request: "GenerationRequest") -> GenerationJob:
    """Create a completed generation job."""
    from app.models import JobStatus, JobPriority
    
    job = GenerationJob(
        id=uuid.uuid4(),
        request_id=test_generation_request.id,
        user_id=test_user.id,
        status=JobStatus.COMPLETED,
        priority=JobPriority.NORMAL,
        progress_percent=100.0,
        rows_generated=1000,
        row_count=1000,
        started_at=datetime.utcnow() - timedelta(minutes=5),
        completed_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ============================================================================
# API Key Fixtures
# ============================================================================

@pytest.fixture
def test_api_key(db: Session, test_user: User) -> tuple[APIKey, str]:
    """Create a test API key. Returns (APIKey, raw_key)."""
    from app.core.security import generate_api_key
    
    key_prefix, raw_key, key_hash = generate_api_key()
    
    api_key = APIKey(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Test API Key",
        key_prefix=key_prefix,
        key_hash=key_hash,
        scopes=["datasets:read", "datasets:write", "jobs:read"],
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, raw_key


@pytest.fixture
def api_key_headers(test_api_key: tuple[APIKey, str]) -> dict:
    """Create API key authentication headers."""
    _, raw_key = test_api_key
    return {"X-API-Key": raw_key}


# ============================================================================
# Webhook Fixtures
# ============================================================================

@pytest.fixture
def test_webhook(db: Session, test_user: User) -> Webhook:
    """Create a test webhook."""
    from app.core.security import generate_token
    
    webhook = Webhook(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Test Webhook",
        url="https://example.com/webhook",
        secret=generate_token(32),
        events=["job.completed", "job.failed"],
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_email_service() -> MagicMock:
    """Mock email service."""
    mock = MagicMock()
    mock.send_email = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_stripe() -> MagicMock:
    """Mock Stripe client."""
    mock = MagicMock()
    mock.Customer.create = MagicMock(return_value={"id": "cus_test123"})
    mock.Subscription.create = MagicMock(return_value={"id": "sub_test123"})
    mock.checkout.Session.create = MagicMock(return_value={"url": "https://checkout.stripe.com/test"})
    return mock


@pytest.fixture
def mock_redis() -> MagicMock:
    """Mock Redis client."""
    mock = MagicMock()
    mock.get = MagicMock(return_value=None)
    mock.set = MagicMock(return_value=True)
    mock.delete = MagicMock(return_value=True)
    mock.incr = MagicMock(return_value=1)
    mock.expire = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_celery() -> MagicMock:
    """Mock Celery app."""
    mock = MagicMock()
    mock.send_task = MagicMock(return_value=MagicMock(id="task_test123"))
    return mock


# ============================================================================
# Utility Functions
# ============================================================================

def create_test_user(
    db: Session,
    email: str = "user@example.com",
    password: str = "Password123!",
    full_name: str = "Test User",
    role: str = "user",
    is_active: bool = True,
    is_verified: bool = True,
) -> User:
    """Helper to create a test user with custom parameters."""
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        first_name=full_name.split()[0] if full_name else "Test",
        last_name=full_name.split()[-1] if full_name and len(full_name.split()) > 1 else "User",
        display_name=full_name,
        role=UserRole[role.upper()] if isinstance(role, str) else role,
        status=UserStatus.ACTIVE if is_active else UserStatus.INACTIVE,
        email_verified=is_verified,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_dataset(
    db: Session,
    user: User,
    name: str = "Test Dataset",
    row_count: int = 1000,
    format: str = "csv",
) -> Dataset:
    """Helper to create a test dataset with custom parameters."""
    dataset = Dataset(
        id=uuid.uuid4(),
        name=name,
        user_id=user.id,
        row_count=row_count,
        column_count=10,
        format=DataFormat(format.lower()),
        size_bytes=row_count * 100,
        created_at=datetime.utcnow(),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


# ============================================================================
# Celery Mock Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def mock_celery_tasks(monkeypatch):
    """Mock all Celery task delays to prevent Redis connection errors in tests."""
    
    class MockAsyncResult:
        def __init__(self, task_id=None):
            self.id = task_id or str(uuid.uuid4())
            self.status = "PENDING"
            self.result = None
    
    def mock_delay(*args, **kwargs):
        return MockAsyncResult()
    
    def mock_apply_async(*args, **kwargs):
        return MockAsyncResult()
    
    # Mock all Celery tasks in generation module
    try:
        from app.tasks import generation
        if hasattr(generation, 'generate_faker_data'):
            monkeypatch.setattr(generation.generate_faker_data, 'delay', mock_delay)
            monkeypatch.setattr(generation.generate_faker_data, 'apply_async', mock_apply_async)
        if hasattr(generation, 'generate_dataset'):
            monkeypatch.setattr(generation.generate_dataset, 'delay', mock_delay)
            monkeypatch.setattr(generation.generate_dataset, 'apply_async', mock_apply_async)
        if hasattr(generation, 'generate_llm_data'):
            monkeypatch.setattr(generation.generate_llm_data, 'delay', mock_delay)
            monkeypatch.setattr(generation.generate_llm_data, 'apply_async', mock_apply_async)
        if hasattr(generation, 'generate_synthcity_data'):
            monkeypatch.setattr(generation.generate_synthcity_data, 'delay', mock_delay)
            monkeypatch.setattr(generation.generate_synthcity_data, 'apply_async', mock_apply_async)
    except (ImportError, AttributeError):
        pass
    
    # Mock the Celery app's send_task method
    try:
        from app.celery_app import celery_app
        monkeypatch.setattr(celery_app, 'send_task', lambda *a, **kw: MockAsyncResult())
    except (ImportError, AttributeError):
        pass
