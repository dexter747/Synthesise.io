"""
Synthesize.io Data Factory Package

The core synthetic data generation engine powering Synthesize.io.
Combines Faker-based fake data generation with SDV statistical synthesis
for high-quality, scalable synthetic data generation.

Author: Synthesize.io Engineering Team
Version: 1.0.0
"""

from app.services.data_factory.orchestrator import DataFactory
from app.services.data_factory.schema import (
    DataSchema,
    ColumnSpec,
    GenerationTier,
    GenerationConfig,
    QualityReport,
)

__all__ = [
    "DataFactory",
    "DataSchema",
    "ColumnSpec",
    "GenerationTier",
    "GenerationConfig",
    "QualityReport",
]

__version__ = "1.0.0"
