"""
Data Factory Schema Definitions

Core data structures used throughout the Data Factory module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class GenerationTier(str, Enum):
    """
    Generation strategy tiers with different speed/quality tradeoffs.
    
    FAST: Faker-based generation, ~500K rows/min, good quality
    SMART: Pattern matching with constraints, ~100K rows/min, very good quality
    ML_BASED: SDV statistical synthesis, ~10K rows/min, excellent quality
    """
    FAST = "fast"
    SMART = "smart"
    ML_BASED = "ml_based"


class DataType(str, Enum):
    """Supported data types for generation."""
    # Personal
    NAME = "name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    USERNAME = "username"
    PASSWORD = "password"
    
    # Geographic
    ADDRESS = "address"
    STREET_ADDRESS = "street_address"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    COUNTRY_CODE = "country_code"
    ZIP_CODE = "zip_code"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    COORDINATES = "coordinates"
    IP_ADDRESS = "ip_address"
    
    # Financial
    CREDIT_CARD = "credit_card"
    CREDIT_CARD_NUMBER = "credit_card_number"
    CVV = "cvv"
    IBAN = "iban"
    SWIFT = "swift"
    CURRENCY = "currency"
    AMOUNT = "amount"
    PRICE = "price"
    
    # Temporal
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    TIME = "time"
    DURATION = "duration"
    AGE = "age"
    YEAR = "year"
    
    # Identifiers
    UUID = "uuid"
    ORDER_ID = "order_id"
    TRANSACTION_ID = "transaction_id"
    INVOICE_NUMBER = "invoice_number"
    SKU = "sku"
    SLUG = "slug"
    SEQUENTIAL_ID = "sequential_id"
    
    # Text
    TEXT = "text"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    WORD = "word"
    TITLE = "title"
    DESCRIPTION = "description"
    
    # Categorical
    BOOLEAN = "boolean"
    ENUM = "enum"
    STATUS = "status"
    CATEGORY = "category"
    
    # Numerical
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    
    # Business
    COMPANY = "company"
    JOB_TITLE = "job_title"
    DEPARTMENT = "department"
    DOMAIN = "domain"
    URL = "url"
    
    # Custom
    CUSTOM = "custom"
    PATTERN = "pattern"


class Distribution(str, Enum):
    """Statistical distributions for numerical data."""
    UNIFORM = "uniform"
    NORMAL = "normal"
    EXPONENTIAL = "exponential"
    LOG_NORMAL = "log_normal"
    POISSON = "poisson"
    BINOMIAL = "binomial"
    BETA = "beta"
    GAMMA = "gamma"


@dataclass
class ConstraintSpec:
    """Specification for column constraints."""
    min_value: Optional[Union[int, float, datetime]] = None
    max_value: Optional[Union[int, float, datetime]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # Regex pattern
    enum_values: Optional[List[Any]] = None
    weights: Optional[List[float]] = None  # For weighted enum selection
    format: Optional[str] = None  # e.g., "e164" for phone
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    decimal_places: Optional[int] = None
    distribution: Optional[Distribution] = None
    distribution_params: Optional[Dict[str, float]] = None


@dataclass
class ColumnSpec:
    """
    Specification for a single column in the dataset.
    
    Attributes:
        name: Column name
        data_type: Type of data to generate
        constraints: Optional constraints for generation
        nullable: Whether null values are allowed
        null_probability: Probability of generating null (0.0-1.0)
        unique: Whether values must be unique
        primary_key: Whether this is a primary key
        foreign_key: Reference to another table.column if FK
        generator_params: Additional parameters for the generator
    """
    name: str
    data_type: DataType
    constraints: Optional[ConstraintSpec] = None
    nullable: bool = False
    null_probability: float = 0.0
    unique: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # Format: "table.column"
    generator_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the column spec."""
        if self.nullable and self.null_probability == 0.0:
            self.null_probability = 0.05  # Default 5% null
        if self.primary_key:
            self.unique = True
            self.nullable = False


@dataclass
class RelationshipSpec:
    """Specification for table relationships."""
    parent_table: str
    parent_column: str
    child_table: str
    child_column: str
    relationship_type: str = "one_to_many"  # one_to_one, one_to_many, many_to_many


@dataclass
class DataSchema:
    """
    Complete schema for dataset generation.
    
    Attributes:
        columns: List of column specifications
        row_count: Number of rows to generate
        tier: Generation strategy tier
        table_name: Optional table name for multi-table generation
        relationships: Optional relationships to other tables
        locale: Locale for localized data (e.g., "en_US", "de_DE")
        seed: Random seed for reproducibility
    """
    columns: List[ColumnSpec]
    row_count: int
    tier: GenerationTier = GenerationTier.SMART
    table_name: Optional[str] = None
    relationships: List[RelationshipSpec] = field(default_factory=list)
    locale: str = "en_US"
    seed: Optional[int] = None
    
    @property
    def column_names(self) -> List[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]
    
    @property
    def unique_columns(self) -> List[str]:
        """Get list of columns requiring uniqueness."""
        return [col.name for col in self.columns if col.unique]
    
    @property
    def primary_key_columns(self) -> List[str]:
        """Get primary key columns."""
        return [col.name for col in self.columns if col.primary_key]
    
    def get_column(self, name: str) -> Optional[ColumnSpec]:
        """Get column spec by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None


@dataclass
class GenerationConfig:
    """
    Configuration for the generation process.
    
    Attributes:
        batch_size: Number of rows per batch
        num_workers: Number of parallel workers
        quality_threshold: Minimum quality score required (0-100)
        max_retries: Maximum retry attempts for failed generations
        enable_validation: Whether to validate generated data
        enable_quality_check: Whether to run quality scoring
        cache_enabled: Whether to cache intermediate results
        streaming: Whether to stream output to file
        output_format: Output format (csv, json, parquet, etc.)
    """
    batch_size: int = 10000
    num_workers: int = 4
    quality_threshold: float = 95.0
    max_retries: int = 3
    enable_validation: bool = True
    enable_quality_check: bool = True
    cache_enabled: bool = True
    streaming: bool = False
    output_format: str = "csv"
    compression: Optional[str] = None  # gzip, snappy, etc.


@dataclass
class ValidationError:
    """A single validation error."""
    column: str
    row_index: Optional[int]
    value: Any
    error_type: str
    message: str


@dataclass
class QualityMetrics:
    """Individual quality metrics."""
    format_compliance: float = 100.0
    uniqueness_score: float = 100.0
    completeness_score: float = 100.0
    distribution_score: float = 100.0
    integrity_score: float = 100.0
    consistency_score: float = 100.0


@dataclass
class QualityReport:
    """
    Comprehensive quality report for generated data.
    
    Attributes:
        overall_score: Overall quality score (0-100)
        metrics: Individual quality metrics
        passed: Whether quality threshold was met
        issues: List of identified issues
        recommendations: Suggestions for improvement
        validation_errors: List of specific validation errors
        stats: Additional statistics about the generated data
    """
    overall_score: float
    metrics: QualityMetrics
    passed: bool
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_errors: List[ValidationError] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        metrics: QualityMetrics,
        threshold: float = 95.0,
        issues: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        validation_errors: Optional[List[ValidationError]] = None,
        stats: Optional[Dict[str, Any]] = None
    ) -> "QualityReport":
        """Create a quality report from metrics."""
        # Calculate weighted overall score
        weights = {
            "format_compliance": 0.25,
            "uniqueness_score": 0.20,
            "completeness_score": 0.20,
            "distribution_score": 0.15,
            "integrity_score": 0.10,
            "consistency_score": 0.10,
        }
        
        overall = sum(
            getattr(metrics, metric) * weight
            for metric, weight in weights.items()
        )
        
        return cls(
            overall_score=round(overall, 2),
            metrics=metrics,
            passed=overall >= threshold,
            issues=issues or [],
            recommendations=recommendations or [],
            validation_errors=validation_errors or [],
            stats=stats or {},
        )


@dataclass
class GenerationResult:
    """
    Result of a data generation operation.
    
    Attributes:
        success: Whether generation completed successfully
        row_count: Number of rows generated
        file_path: Path to output file (if streaming)
        quality_report: Quality assessment report
        duration_seconds: Time taken for generation
        error: Error message if failed
    """
    success: bool
    row_count: int
    file_path: Optional[str] = None
    quality_report: Optional[QualityReport] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
