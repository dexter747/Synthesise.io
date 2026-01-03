"""
Base Generator Abstract Class

Provides common functionality for all data generators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, TypeVar, Generic
import random
import logging

from faker import Faker

from app.services.data_factory.schema import ColumnSpec, ConstraintSpec

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseGenerator(ABC, Generic[T]):
    """
    Abstract base class for all data generators.
    
    Provides common functionality:
    - Faker instance management
    - Uniqueness tracking
    - Null value handling
    - Batch generation support
    - Seeding for reproducibility
    """
    
    def __init__(
        self,
        locale: str = "en_US",
        seed: Optional[int] = None
    ):
        """
        Initialize the generator.
        
        Args:
            locale: Locale for localized data generation
            seed: Random seed for reproducibility
        """
        self.locale = locale
        self.seed = seed
        
        # Initialize Faker with locale(s)
        self._faker = self._create_faker(locale)
        
        # Track unique values per column
        self._unique_values: Dict[str, Set[Any]] = {}
        
        # Track generation counts for sequential IDs
        self._sequence_counters: Dict[str, int] = {}
        
        # Set seed if provided
        if seed is not None:
            self.set_seed(seed)
    
    def _create_faker(self, locale: str) -> Faker:
        """Create Faker instance with proper locale handling."""
        # Support multiple locales for variety
        if "," in locale:
            locales = [loc.strip() for loc in locale.split(",")]
        else:
            locales = [locale]
        
        return Faker(locales)
    
    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self.seed = seed
        random.seed(seed)
        Faker.seed(seed)
        self._faker.seed_instance(seed)
    
    def reset(self) -> None:
        """Reset generator state (unique values, counters)."""
        self._unique_values.clear()
        self._sequence_counters.clear()
    
    def _get_unique_value(
        self,
        column: str,
        generator_func: callable,
        max_attempts: int = 1000,
        **kwargs
    ) -> Any:
        """
        Get a unique value for a column.
        
        Args:
            column: Column name for tracking
            generator_func: Function to generate values
            max_attempts: Maximum attempts before raising error
            **kwargs: Additional arguments for generator function
            
        Returns:
            Unique value
            
        Raises:
            ValueError: If unable to generate unique value after max_attempts
        """
        if column not in self._unique_values:
            self._unique_values[column] = set()
        
        for attempt in range(max_attempts):
            value = generator_func(**kwargs)
            
            if value not in self._unique_values[column]:
                self._unique_values[column].add(value)
                return value
        
        raise ValueError(
            f"Unable to generate unique value for '{column}' "
            f"after {max_attempts} attempts. "
            f"Consider increasing the value pool or reducing row count."
        )
    
    def _should_be_null(
        self,
        spec: ColumnSpec
    ) -> bool:
        """Check if value should be null based on spec."""
        if not spec.nullable:
            return False
        return random.random() < spec.null_probability
    
    def _get_next_sequence(
        self,
        key: str,
        start: int = 1
    ) -> int:
        """Get next sequential number for a key."""
        if key not in self._sequence_counters:
            self._sequence_counters[key] = start
        
        value = self._sequence_counters[key]
        self._sequence_counters[key] += 1
        return value
    
    @abstractmethod
    def generate(
        self,
        spec: ColumnSpec,
        count: int = 1
    ) -> List[T]:
        """
        Generate values for a column.
        
        Args:
            spec: Column specification
            count: Number of values to generate
            
        Returns:
            List of generated values
        """
        pass
    
    def generate_single(
        self,
        spec: ColumnSpec
    ) -> T:
        """Generate a single value."""
        values = self.generate(spec, count=1)
        return values[0] if values else None
    
    def generate_batch(
        self,
        spec: ColumnSpec,
        count: int,
        batch_size: int = 10000
    ) -> List[T]:
        """
        Generate values in batches for memory efficiency.
        
        Args:
            spec: Column specification
            count: Total number of values
            batch_size: Size of each batch
            
        Yields:
            Batches of generated values
        """
        values = []
        remaining = count
        
        while remaining > 0:
            current_batch = min(remaining, batch_size)
            batch = self.generate(spec, count=current_batch)
            values.extend(batch)
            remaining -= current_batch
        
        return values
    
    def _apply_constraints(
        self,
        value: Any,
        constraints: Optional[ConstraintSpec]
    ) -> Any:
        """
        Apply constraints to a generated value.
        
        Override in subclasses for type-specific constraint handling.
        """
        if constraints is None:
            return value
        
        # Apply prefix/suffix
        if isinstance(value, str):
            if constraints.prefix:
                value = constraints.prefix + value
            if constraints.suffix:
                value = value + constraints.suffix
        
        return value
    
    def supports_type(self, data_type: str) -> bool:
        """Check if this generator supports the given data type."""
        supported = self.get_supported_types()
        return data_type in supported
    
    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Get list of data types supported by this generator."""
        pass
