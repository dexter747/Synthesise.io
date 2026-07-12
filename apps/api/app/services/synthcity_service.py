"""
Synthcity Service - ML-Based Synthetic Data Generation
=======================================================
Generate statistically similar synthetic data from real datasets using ML models.

Features:
- Multiple models: CTGAN, TVAE, CopulaGAN, GaussianCopula
- CSV/Excel/Parquet file validation
- Training progress tracking
- Model persistence for reuse
- Identifier column handling
"""

import logging
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple
from io import BytesIO
import pandas as pd
import numpy as np
import pickle

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import ValidationError, GenerationError

# Suppress warnings during import
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


# =============================================================================
# AVAILABLE MODELS
# =============================================================================

SYNTHCITY_MODELS = {
    "ctgan": {
        "name": "CTGAN",
        "description": "Conditional Tabular GAN - Good for mixed data types with complex relationships",
        "supports_constraints": True,
        "training_time": "medium",
        "best_for": ["mixed types", "complex relationships", "moderate size datasets"],
    },
    "tvae": {
        "name": "TVAE",
        "description": "Tabular Variational Autoencoder - Fast and efficient for most use cases",
        "supports_constraints": True,
        "training_time": "fast",
        "best_for": ["large datasets", "quick results", "numerical data"],
    },
    "copulagan": {
        "name": "CopulaGAN",
        "description": "GAN with Gaussian copula for better correlation preservation",
        "supports_constraints": True,
        "training_time": "medium",
        "best_for": ["correlated features", "financial data", "statistical accuracy"],
    },
    "gaussiancopula": {
        "name": "Gaussian Copula",
        "description": "Statistical model using Gaussian copula - Very fast, good baseline",
        "supports_constraints": False,
        "training_time": "fast",
        "best_for": ["quick baseline", "simple distributions", "small datasets"],
    },
}


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class SynthcityColumnConfig(BaseModel):
    """Column configuration for Synthcity."""
    name: str
    is_identifier: bool = Field(default=False, description="Whether this is an identifier column")
    data_type: Optional[str] = Field(default=None, description="Override detected data type")
    sdtype: Optional[str] = Field(default=None, description="SDV semantic data type")


class SynthcityGenerateRequest(BaseModel):
    """Request model for Synthcity data generation."""
    num_rows: int = Field(..., gt=0, le=100000, description="Number of rows to generate")
    columns_config: Optional[List[SynthcityColumnConfig]] = Field(
        default=None, 
        description="Column configurations"
    )
    model: str = Field(default="ctgan", description="Model to use")
    epochs: int = Field(default=300, ge=10, le=1000, description="Training epochs")
    output_format: str = Field(default="csv", description="Output format")
    preserve_constraints: bool = Field(default=True, description="Preserve data constraints")


class SynthcityValidationResponse(BaseModel):
    """Response from CSV validation."""
    valid: bool
    filename: str
    rows: int
    columns: List[str]
    column_types: Dict[str, str]
    null_counts: Dict[str, int]
    memory_usage: int
    warnings: List[str] = []


# =============================================================================
# SYNTHCITY SERVICE CLASS
# =============================================================================

class SynthcityService:
    """
    Production-grade service for synthetic data generation using SDV.
    Handles CSV upload, model training, and synthetic data generation.
    """
    
    def __init__(self):
        """Initialize the Synthcity service."""
        self._models_cache: Dict[str, Any] = {}
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        upload_dir = getattr(settings, 'DATA_UPLOAD_DIR', '/tmp/synthesize/uploads')
        output_dir = getattr(settings, 'DATA_OUTPUT_DIR', '/tmp/synthesize/outputs')
        models_dir = getattr(settings, 'DATA_MODELS_DIR', '/tmp/synthesize/models')
        
        for dir_path in [upload_dir, output_dir, models_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available Synthcity models."""
        return SYNTHCITY_MODELS
    
    def validate_csv(
        self, 
        file_content: bytes, 
        filename: str
    ) -> Tuple[pd.DataFrame, SynthcityValidationResponse]:
        """
        Validate and parse uploaded CSV/Excel/Parquet file.
        
        Args:
            file_content: Raw file content
            filename: Original filename
        
        Returns:
            Tuple of (DataFrame, validation response)
        """
        warnings_list = []
        
        try:
            # Detect file type and parse
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.csv':
                df = pd.read_csv(BytesIO(file_content))
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(BytesIO(file_content))
            elif ext == '.json':
                df = pd.read_json(BytesIO(file_content))
            elif ext == '.parquet':
                df = pd.read_parquet(BytesIO(file_content))
            else:
                # Default to CSV
                df = pd.read_csv(BytesIO(file_content))
                warnings_list.append(f"Unknown file extension '{ext}', treating as CSV")
                
        except Exception as e:
            raise ValidationError(
                f"Failed to parse file: {str(e)}",
                details={"filename": filename, "error": str(e)}
            )
        
        if df.empty:
            raise ValidationError("Uploaded file is empty")
        
        max_columns = getattr(settings, 'FAKER_MAX_COLUMNS', 100)
        if len(df.columns) > max_columns:
            raise ValidationError(
                f"Too many columns. Maximum is {max_columns}",
                details={"columns": len(df.columns), "max": max_columns}
            )
        
        max_rows = getattr(settings, 'SYNTHCITY_MAX_TRAINING_ROWS', 100000)
        if len(df) > max_rows:
            warnings_list.append(
                f"Dataset has {len(df)} rows, will use first {max_rows} for training"
            )
            df = df.head(max_rows)
        
        # Infer column types
        column_types = self._infer_column_types(df)
        
        # Check for null values
        null_counts = df.isnull().sum().to_dict()
        
        response = SynthcityValidationResponse(
            valid=True,
            filename=filename,
            rows=len(df),
            columns=list(df.columns),
            column_types=column_types,
            null_counts=null_counts,
            memory_usage=df.memory_usage(deep=True).sum(),
            warnings=warnings_list,
        )
        
        return df, response
    
    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column types from DataFrame."""
        type_mapping = {
            "int64": "integer",
            "int32": "integer",
            "float64": "float",
            "float32": "float",
            "object": "string",
            "bool": "boolean",
            "datetime64[ns]": "datetime",
            "category": "category",
        }
        
        result = {}
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            result[col] = type_mapping.get(dtype_str, dtype_str)
        
        return result
    
    def preprocess_data(
        self,
        df: pd.DataFrame,
        columns_config: Optional[List[SynthcityColumnConfig]] = None,
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, pd.Series]]:
        """
        Preprocess data for Synthcity training.
        Handles identifier columns separately.
        
        Args:
            df: Input DataFrame
            columns_config: Column configurations
        
        Returns:
            Tuple of (processed DataFrame, identifier columns, identifier data)
        """
        identifier_columns: List[str] = []
        identifier_data: Dict[str, pd.Series] = {}
        
        if columns_config:
            for config in columns_config:
                if config.is_identifier and config.name in df.columns:
                    identifier_columns.append(config.name)
                    identifier_data[config.name] = df[config.name].copy()
        
        # Create training DataFrame without identifiers
        training_df = df.drop(columns=identifier_columns, errors='ignore')
        
        # Handle missing values
        for col in training_df.columns:
            if training_df[col].isnull().any():
                if training_df[col].dtype in ['float64', 'int64']:
                    training_df[col] = training_df[col].fillna(training_df[col].median())
                else:
                    training_df[col] = training_df[col].fillna(training_df[col].mode().iloc[0] if not training_df[col].mode().empty else "MISSING")
        
        return training_df, identifier_columns, identifier_data
    
    def train_model(
        self,
        df: pd.DataFrame,
        model_name: str = "ctgan",
        epochs: int = 300,
    ) -> Any:
        """
        Train a synthetic data model on the provided data.
        
        Args:
            df: Training DataFrame
            model_name: Model type to use
            epochs: Number of training epochs
        
        Returns:
            Trained model instance
        """
        if model_name not in SYNTHCITY_MODELS:
            raise ValidationError(
                f"Unknown model: {model_name}",
                details={"available_models": list(SYNTHCITY_MODELS.keys())}
            )
        
        try:
            # Try to import SDV
            from sdv.single_table import CTGANSynthesizer, TVAESynthesizer, CopulaGANSynthesizer, GaussianCopulaSynthesizer
            from sdv.metadata import SingleTableMetadata
            
            logger.info(f"Training {model_name} model on {len(df)} rows, {len(df.columns)} columns")
            
            # Create metadata
            metadata = SingleTableMetadata()
            metadata.detect_from_dataframe(df)
            
            # Select model
            model_classes = {
                "ctgan": CTGANSynthesizer,
                "tvae": TVAESynthesizer,
                "copulagan": CopulaGANSynthesizer,
                "gaussiancopula": GaussianCopulaSynthesizer,
            }
            
            ModelClass = model_classes[model_name]
            
            # Create and train model
            if model_name in ["ctgan", "tvae", "copulagan"]:
                model = ModelClass(metadata, epochs=epochs)
            else:
                model = ModelClass(metadata)
            
            model.fit(df)
            
            logger.info(f"Model training completed successfully")
            return model
            
        except ImportError:
            logger.warning("SDV not installed, using fallback statistical generation")
            return self._create_fallback_model(df)
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise GenerationError(
                f"Model training failed: {str(e)}",
                details={"model": model_name, "error": str(e)}
            )
    
    def _create_fallback_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a simple statistical fallback model when SDV is not available."""
        model = {
            "type": "fallback",
            "columns": {},
            "original_df": df,
        }
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if df[col].dtype in ['int64', 'float64']:
                model["columns"][col] = {
                    "type": "numerical",
                    "mean": col_data.mean(),
                    "std": col_data.std(),
                    "min": col_data.min(),
                    "max": col_data.max(),
                }
            else:
                value_counts = col_data.value_counts(normalize=True)
                model["columns"][col] = {
                    "type": "categorical",
                    "values": value_counts.index.tolist(),
                    "probabilities": value_counts.values.tolist(),
                }
        
        return model
    
    def generate_synthetic_data(
        self,
        model: Any,
        num_rows: int,
        identifier_columns: List[str] = None,
        original_df: pd.DataFrame = None,
    ) -> pd.DataFrame:
        """
        Generate synthetic data from a trained model.
        
        Args:
            model: Trained model instance
            num_rows: Number of rows to generate
            identifier_columns: Columns to regenerate as identifiers
            original_df: Original DataFrame (for schema reference)
        
        Returns:
            DataFrame with synthetic data
        """
        try:
            # Check if it's a fallback model
            if isinstance(model, dict) and model.get("type") == "fallback":
                return self._generate_from_fallback(model, num_rows)
            
            # Generate using SDV model
            synthetic_df = model.sample(num_rows)
            
            # Add identifier columns back if needed
            if identifier_columns and original_df is not None:
                from faker import Faker
                fake = Faker()
                
                for col in identifier_columns:
                    if col in original_df.columns:
                        dtype = original_df[col].dtype
                        if 'int' in str(dtype):
                            synthetic_df[col] = range(1, num_rows + 1)
                        else:
                            synthetic_df[col] = [fake.uuid4() for _ in range(num_rows)]
            
            return synthetic_df
            
        except Exception as e:
            logger.error(f"Data generation failed: {e}")
            raise GenerationError(
                f"Data generation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _generate_from_fallback(self, model: Dict[str, Any], num_rows: int) -> pd.DataFrame:
        """Generate data using fallback statistical model."""
        data = {}
        
        for col, config in model["columns"].items():
            if config["type"] == "numerical":
                # Generate from normal distribution clipped to range
                values = np.random.normal(config["mean"], config["std"], num_rows)
                values = np.clip(values, config["min"], config["max"])
                
                # Round if original was integer
                if model["original_df"][col].dtype == 'int64':
                    values = np.round(values).astype(int)
                
                data[col] = values
            else:
                # Generate from categorical distribution
                data[col] = np.random.choice(
                    config["values"],
                    size=num_rows,
                    p=config["probabilities"]
                )
        
        return pd.DataFrame(data)
    
    def save_model(self, model: Any, model_id: str) -> str:
        """
        Save a trained model to disk.
        
        Args:
            model: Trained model instance
            model_id: Unique identifier for the model
        
        Returns:
            Path to saved model file
        """
        models_dir = getattr(settings, 'DATA_MODELS_DIR', '/tmp/synthesize/models')
        os.makedirs(models_dir, exist_ok=True)
        
        model_path = os.path.join(models_dir, f"{model_id}.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, model_id: str) -> Any:
        """
        Load a saved model from disk.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Loaded model instance
        """
        models_dir = getattr(settings, 'DATA_MODELS_DIR', '/tmp/synthesize/models')
        model_path = os.path.join(models_dir, f"{model_id}.pkl")
        
        if not os.path.exists(model_path):
            raise ValidationError(f"Model not found: {model_id}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Model loaded from {model_path}")
        return model
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a saved model."""
        models_dir = getattr(settings, 'DATA_MODELS_DIR', '/tmp/synthesize/models')
        model_path = os.path.join(models_dir, f"{model_id}.pkl")
        
        if os.path.exists(model_path):
            os.remove(model_path)
            logger.info(f"Model deleted: {model_id}")
            return True
        
        return False


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_synthcity_service_instance: Optional[SynthcityService] = None


def get_synthcity_service() -> SynthcityService:
    """Get or create the Synthcity service singleton."""
    global _synthcity_service_instance
    
    if _synthcity_service_instance is None:
        _synthcity_service_instance = SynthcityService()
    
    return _synthcity_service_instance
