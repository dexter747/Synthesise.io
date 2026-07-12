"""
Dataset service for Synthesize.io API.

Handles dataset CRUD, schema management, and data generation orchestration.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DuplicateError,
    NotFoundError,
    ValidationError,
    AuthorizationError,
    QuotaExceededError,
)
from app.models import (
    Dataset,
    DatasetStatus,
    DataFormat,
    GenerationJob,
    User,
    Subscription,
    SubscriptionPlan,
)
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetSchemaUpdate,
    DatasetSchema,
    GenerationRequest,
    GenerationOptions,
)


class DatasetService:
    """Service for dataset operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # =========================================================================
    # DATASET CRUD
    # =========================================================================
    
    def create(
        self, data: DatasetCreate, user_id: UUID
    ) -> Dataset:
        """Create a new dataset."""
        # Validate schema
        self._validate_schema(data.schema_definition)
        
        # Check user's dataset limit
        self._check_dataset_limit(user_id, data.organization_id)
        
        # Convert schema to dict for JSONB storage
        schema_dict = data.schema_definition.model_dump() if hasattr(data.schema_definition, 'model_dump') else data.schema_definition
        
        # Create dataset
        dataset = Dataset(
            name=data.name,
            description=data.description,
            user_id=user_id,
            organization_id=data.organization_id,
            schema_definition=schema_dict,
            tags=data.tags or [],
            status=DatasetStatus.READY,
            row_count=0,
            format=DataFormat.CSV,
            size_bytes=0,
            is_public=False,
        )
        
        self.db.add(dataset)
        self.db.flush()
        
        # TODO: Create initial version when DatasetVersion model is implemented
        # version = DatasetVersion(
        #     dataset_id=dataset.id,
        #     version=1,
        #     schema_definition=data.schema_definition.model_dump(),
        #     created_by=user_id,
        # )
        # self.db.add(version)
        
        self.db.commit()
        self.db.refresh(dataset)
        
        return dataset
    
    def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        """Get dataset by ID."""
        result = self.db.execute(
            select(Dataset)
            .where(Dataset.id == dataset_id)
            .where(Dataset.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    
    def get_by_id_or_raise(self, dataset_id: UUID) -> Dataset:
        """Get dataset by ID or raise NotFoundError."""
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundError("Dataset", str(dataset_id))
        return dataset
    
    def get_with_auth(
        self, dataset_id: UUID, user_id: UUID
    ) -> Dataset:
        """Get dataset with authorization check."""
        dataset = self.get_by_id_or_raise(dataset_id)
        
        # Check access
        if not self._can_access(dataset, user_id):
            raise AuthorizationError("You don't have access to this dataset")
        
        return dataset
    
    def update(
        self, dataset_id: UUID, data: DatasetUpdate, user_id: UUID
    ) -> Dataset:
        """Update dataset metadata."""
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dataset, field, value)
        
        self.db.commit()
        self.db.refresh(dataset)
        
        return dataset
    
    def update_schema(
        self, dataset_id: UUID, data: DatasetSchemaUpdate, user_id: UUID
    ) -> Dataset:
        """Update dataset schema (creates new version)."""
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        # Validate new schema
        self._validate_schema(data.schema_definition)
        
        # TODO: Create new version when DatasetVersion model is implemented
        # new_version = dataset.schema_version + 1
        # version = DatasetVersion(
        #     dataset_id=dataset.id,
        #     version=new_version,
        #     schema_definition=data.schema_definition.model_dump(),
        #     migration_notes=data.migration_notes,
        #     created_by=user_id,
        # )
        # self.db.add(version)
        
        # Update dataset
        dataset.schema_definition = data.schema_definition.model_dump()
        # dataset.schema_version = new_version  # Commented until versioning is implemented
        
        self.db.commit()
        self.db.refresh(dataset)
        
        return dataset
    
    def delete(self, dataset_id: UUID, user_id: UUID) -> None:
        """Delete dataset (soft delete)."""
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check delete access
        if not self._can_delete(dataset, user_id):
            raise AuthorizationError("You don't have permission to delete this dataset")
        
        dataset.deleted_at = datetime.utcnow()
        dataset.status = "deleted"
        self.db.commit()
    
    # =========================================================================
    # LISTING & SEARCH
    # =========================================================================
    
    def list_datasets(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        tags: Optional[list[str]] = None,
        is_template: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Dataset], int]:
        """List datasets accessible to user."""
        # Base query
        query = select(Dataset).where(Dataset.deleted_at.is_(None))
        count_query = select(func.count(Dataset.id)).where(Dataset.deleted_at.is_(None))
        
        # Filter by ownership/access
        if organization_id:
            query = query.where(Dataset.organization_id == organization_id)
            count_query = count_query.where(Dataset.organization_id == organization_id)
        else:
            # User's own datasets or public datasets
            query = query.where(
                (Dataset.user_id == user_id) | (Dataset.is_public == True)
            )
            count_query = count_query.where(
                (Dataset.user_id == user_id) | (Dataset.is_public == True)
            )
        
        # Search filter
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Dataset.name.ilike(search_filter)) |
                (Dataset.description.ilike(search_filter))
            )
            count_query = count_query.where(
                (Dataset.name.ilike(search_filter)) |
                (Dataset.description.ilike(search_filter))
            )
        
        # Tags filter
        if tags:
            for tag in tags:
                query = query.where(Dataset.tags.contains([tag]))
                count_query = count_query.where(Dataset.tags.contains([tag]))
        
        # Get total count
        total_result = self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(Dataset, sort_by, Dataset.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.limit(per_page).offset((page - 1) * per_page)
        
        result = self.db.execute(query)
        datasets = list(result.scalars().all())
        
        return datasets, total
    
    def list_templates(
        self,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Dataset], int]:
        """List public dataset templates."""
        # Templates feature not yet implemented in database schema
        # Return empty list for now
        return [], 0
    
    def get_template_categories(self) -> list[dict]:
        """Get list of template categories with counts."""
        # Templates feature not yet implemented in database schema
        # Return empty list for now
        return []
    
    # =========================================================================
    # SCHEMA OPERATIONS
    # =========================================================================
    
    # TODO: Implement DatasetVersion model and enable versioning
    # def get_versions(self, dataset_id: UUID) -> list[DatasetVersion]:
    #     """Get all versions of a dataset schema."""
    #     result = self.db.execute(
    #         select(DatasetVersion)
    #         .where(DatasetVersion.dataset_id == dataset_id)
    #         .order_by(DatasetVersion.version.desc())
    #     )
    #     return list(result.scalars().all())
    # 
    # def get_version(
    #     self, dataset_id: UUID, version: int
    # ) -> Optional[DatasetVersion]:
    #     """Get specific version of dataset schema."""
    #     result = self.db.execute(
    #         select(DatasetVersion)
    #         .where(
    #             and_(
    #                 DatasetVersion.dataset_id == dataset_id,
    #                 DatasetVersion.version == version,
    #             )
    #         )
    #     )
    #     return result.scalar_one_or_none()
    
    def clone_dataset(
        self,
        dataset_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        organization_id: Optional[UUID] = None,
    ) -> Dataset:
        """Clone a dataset (from template or existing dataset)."""
        source = self.get_by_id_or_raise(dataset_id)
        
        # Check access (must be public or owned by user)
        if not source.is_public and not self._can_access(source, user_id):
            raise AuthorizationError("You don't have access to this dataset")
        
        # Create clone with only fields that exist on the model
        clone = Dataset(
            name=name or f"{source.name} (Copy)",
            description=source.description,
            user_id=user_id,
            organization_id=organization_id,
            schema_definition=source.schema_definition,
            tags=source.tags.copy() if source.tags else [],
            status=DatasetStatus.PENDING,
            row_count=0,
            format=source.format or DataFormat.JSON,
            size_bytes=0,
            is_public=False,
        )
        
        self.db.add(clone)
        self.db.flush()
        
        self.db.commit()
        self.db.refresh(clone)
        
        return clone
    
    # =========================================================================
    # SCHEMA INFERENCE
    # =========================================================================
    
    def infer_schema(self, sample_data: list[dict]) -> DatasetSchema:
        """Infer schema from sample data."""
        if not sample_data:
            raise ValidationError("Sample data cannot be empty")
        
        fields = []
        first_row = sample_data[0]
        
        for key, value in first_row.items():
            data_type = self._infer_data_type(value)
            fields.append({
                "name": key,
                "data_type": data_type,
                "constraints": {
                    "required": True,
                    "nullable": value is None,
                },
            })
        
        return DatasetSchema(fields=fields)
    
    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from value."""
        if value is None:
            return "string"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "json"
        
        # String analysis for special types
        str_value = str(value)
        
        # Email pattern
        if "@" in str_value and "." in str_value:
            return "email"
        
        # UUID pattern
        if len(str_value) == 36 and str_value.count("-") == 4:
            return "uuid"
        
        return "string"
    
    # =========================================================================
    # SCHEMA FIELD MANAGEMENT
    # =========================================================================
    
    def add_field(
        self, dataset_id: UUID, user_id: UUID, data
    ):
        """Add a new field to dataset schema."""
        from app.models import SchemaField
        
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        # Check for duplicate field name
        existing = self.db.execute(
            select(SchemaField)
            .where(SchemaField.dataset_id == dataset_id)
            .where(SchemaField.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("Field with this name already exists")
        
        # Get next order index
        max_order = self.db.execute(
            select(func.coalesce(func.max(SchemaField.order_index), 0))
            .where(SchemaField.dataset_id == dataset_id)
        )
        next_order = (max_order.scalar() or 0) + 1
        
        field = SchemaField(
            dataset_id=dataset_id,
            name=data.name,
            display_name=getattr(data, 'display_name', None),
            data_type=getattr(data, 'data_type', getattr(data, 'field_type', 'string')),
            constraints=getattr(data, 'constraints', None) or {},
            llm_guidance=getattr(data, 'llm_guidance', None),
            order_index=getattr(data, 'order_index', None) or next_order,
        )
        
        self.db.add(field)
        self.db.commit()
        self.db.refresh(field)
        
        return field
    
    def update_field(
        self, dataset_id: UUID, field_id: UUID, user_id: UUID, data
    ):
        """Update a schema field."""
        from app.models import SchemaField
        
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        # Get the field
        result = self.db.execute(
            select(SchemaField)
            .where(SchemaField.id == field_id)
            .where(SchemaField.dataset_id == dataset_id)
        )
        field = result.scalar_one_or_none()
        
        if not field:
            raise NotFoundError("SchemaField", str(field_id))
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else {}
        for key, value in update_data.items():
            if hasattr(field, key):
                setattr(field, key, value)
        
        self.db.commit()
        self.db.refresh(field)
        
        return field
    
    def delete_field(
        self, dataset_id: UUID, field_id: UUID, user_id: UUID
    ) -> None:
        """Delete a schema field."""
        from app.models import SchemaField
        
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        # Get the field
        result = self.db.execute(
            select(SchemaField)
            .where(SchemaField.id == field_id)
            .where(SchemaField.dataset_id == dataset_id)
        )
        field = result.scalar_one_or_none()
        
        if not field:
            raise NotFoundError("SchemaField", str(field_id))
        
        self.db.delete(field)
        self.db.commit()
    
    def reorder_fields(
        self, dataset_id: UUID, user_id: UUID, field_ids: list[UUID]
    ):
        """Reorder schema fields."""
        from app.models import SchemaField
        
        dataset = self.get_with_auth(dataset_id, user_id)
        
        # Check write access
        if not self._can_write(dataset, user_id):
            raise AuthorizationError("You don't have permission to edit this dataset")
        
        # Get all fields for this dataset
        result = self.db.execute(
            select(SchemaField)
            .where(SchemaField.dataset_id == dataset_id)
        )
        fields = {f.id: f for f in result.scalars().all()}
        
        # Validate all field_ids belong to this dataset
        for fid in field_ids:
            if fid not in fields:
                raise NotFoundError("SchemaField", str(fid))
        
        # Update order indices
        ordered_fields = []
        for idx, fid in enumerate(field_ids):
            fields[fid].order_index = idx
            ordered_fields.append(fields[fid])
        
        self.db.commit()
        
        # Refresh and return in order
        for f in ordered_fields:
            self.db.refresh(f)
        
        return ordered_fields
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def _validate_schema(self, schema: DatasetSchema) -> None:
        """Validate dataset schema."""
        if not schema.fields:
            raise ValidationError("Schema must have at least one field")
        
        field_names = set()
        for field in schema.fields:
            if field.name in field_names:
                raise ValidationError(f"Duplicate field name: {field.name}")
            field_names.add(field.name)
            
            # Validate field name
            if not field.name or len(field.name) > 100:
                raise ValidationError(
                    f"Invalid field name: {field.name}. Must be 1-100 characters."
                )
    
    # =========================================================================
    # AUTHORIZATION HELPERS
    # =========================================================================
    
    def _can_access(self, dataset: Dataset, user_id: UUID) -> bool:
        """Check if user can access dataset."""
        if dataset.is_public:
            return True
        if dataset.user_id == user_id:
            return True
        if dataset.organization_id:
            # Check org membership
            from app.services.organization_service import OrganizationService
            org_service = OrganizationService(self.db)
            return org_service.is_member(dataset.organization_id, user_id)
        return False
    
    def authorize_access(self, dataset: Dataset, user_id: UUID) -> None:
        """Authorize user access to dataset, raises AuthorizationError if denied."""
        if not self._can_access(dataset, user_id):
            raise AuthorizationError("You don't have access to this dataset")
    
    def _can_write(self, dataset: Dataset, user_id: UUID) -> bool:
        """Check if user can write to dataset."""
        if dataset.user_id == user_id:
            return True
        if dataset.organization_id:
            from app.services.organization_service import OrganizationService
            org_service = OrganizationService(self.db)
            role = org_service.get_member_role(dataset.organization_id, user_id)
            return role in ["admin", "member"]
        return False
    
    def _can_delete(self, dataset: Dataset, user_id: UUID) -> bool:
        """Check if user can delete dataset."""
        if dataset.user_id == user_id:
            return True
        if dataset.organization_id:
            from app.services.organization_service import OrganizationService
            org_service = OrganizationService(self.db)
            role = org_service.get_member_role(dataset.organization_id, user_id)
            return role == "admin"
        return False
    
    def _check_dataset_limit(
        self, user_id: UUID, organization_id: Optional[UUID]
    ) -> None:
        """Check if user has reached dataset limit."""
        # Get user's subscription
        result = self.db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan))
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            max_datasets = 5  # Free tier default
        else:
            features = subscription.plan.features or {}
            max_datasets = features.get("max_datasets", 5)
        
        # Count current datasets
        count_query = (
            select(func.count(Dataset.id))
            .where(Dataset.user_id == user_id)
            .where(Dataset.deleted_at.is_(None))
        )
        
        count_result = self.db.execute(count_query)
        current_count = count_result.scalar() or 0
        
        if current_count >= max_datasets:
            raise QuotaExceededError(
                f"Dataset limit reached ({max_datasets}). Please upgrade your plan."
            )
    
    def get_dataset_data(
        self,
        dataset_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> list[dict]:
        """
        Get the generated data for a dataset.
        
        Args:
            dataset_id: Dataset ID
            user_id: User ID for authorization (optional)
            
        Returns:
            List of data rows as dictionaries
        """
        dataset = self.get_by_id_or_raise(dataset_id)
        
        # Check if dataset has data_content field
        if hasattr(dataset, 'data_content') and dataset.data_content:
            return dataset.data_content
        
        # If no data stored, return empty list
        return []


# Dependency injection helper
def get_dataset_service(db: AsyncSession) -> DatasetService:
    """Get dataset service instance."""
    return DatasetService(db)
