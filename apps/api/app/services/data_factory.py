"""
Data Factory - Core data generation algorithms
Separated from API/Celery layers for clean architecture
"""
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class DataFactory:
    """
    Main data generation engine
    This handles the actual data synthesis logic
    """
    
    def __init__(self):
        self.generators = {
            "name": self._generate_name,
            "email": self._generate_email,
            "phone": self._generate_phone,
            "address": self._generate_address,
            "number": self._generate_number,
            "date": self._generate_date,
            "text": self._generate_text,
            "boolean": self._generate_boolean,
        }
    
    def generate_dataset(
        self,
        sample_data: List[Dict[str, Any]],
        row_count: int,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate full dataset based on sample
        
        Args:
            sample_data: Sample rows (10-50) to use as template
            row_count: Number of rows to generate
            constraints: Optional constraints (uniqueness, ranges, etc.)
            
        Returns:
            List of generated data rows
        """
        logger.info(f"Generating {row_count} rows based on {len(sample_data)} sample rows")
        
        if not sample_data:
            raise ValueError("Sample data is required")
        
        # Analyze sample to understand schema and patterns
        schema = self._analyze_sample(sample_data)
        
        # Generate data
        generated_data = []
        for i in range(row_count):
            row = self._generate_row(schema, constraints)
            generated_data.append(row)
            
            # Log progress every 1000 rows
            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1}/{row_count} rows")
        
        return generated_data
    
    def _analyze_sample(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sample to understand data types, patterns, distributions
        """
        schema = {}
        first_row = sample_data[0]
        
        for column, value in first_row.items():
            schema[column] = {
                "type": self._infer_type(column, value),
                "sample_values": [row.get(column) for row in sample_data],
                "nullable": any(row.get(column) is None for row in sample_data)
            }
        
        return schema
    
    def _infer_type(self, column_name: str, value: Any) -> str:
        """
        Infer data type from column name and sample value
        """
        col_lower = column_name.lower()
        
        if "email" in col_lower:
            return "email"
        elif "name" in col_lower:
            return "name"
        elif "phone" in col_lower:
            return "phone"
        elif "address" in col_lower or "street" in col_lower:
            return "address"
        elif "date" in col_lower or isinstance(value, datetime):
            return "date"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        else:
            return "text"
    
    def _generate_row(self, schema: Dict[str, Dict[str, Any]], constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a single data row based on schema
        """
        row = {}
        
        for column, col_info in schema.items():
            data_type = col_info["type"]
            generator = self.generators.get(data_type, self._generate_text)
            row[column] = generator(col_info)
        
        return row
    
    # Generator methods
    def _generate_name(self, col_info: Dict[str, Any]) -> str:
        """Generate realistic names"""
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_email(self, col_info: Dict[str, Any]) -> str:
        """Generate email addresses"""
        domains = ["gmail.com", "yahoo.com", "outlook.com", "company.com"]
        username = f"user{random.randint(1000, 9999)}"
        return f"{username}@{random.choice(domains)}"
    
    def _generate_phone(self, col_info: Dict[str, Any]) -> str:
        """Generate phone numbers"""
        return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def _generate_address(self, col_info: Dict[str, Any]) -> str:
        """Generate addresses"""
        streets = ["Main St", "Oak Ave", "Elm St", "Maple Dr", "Pine Rd"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}"
    
    def _generate_number(self, col_info: Dict[str, Any]) -> float:
        """Generate numbers based on sample distribution"""
        sample_values = [v for v in col_info["sample_values"] if v is not None]
        if sample_values:
            min_val = min(sample_values)
            max_val = max(sample_values)
            return random.uniform(min_val, max_val)
        return random.uniform(0, 100)
    
    def _generate_date(self, col_info: Dict[str, Any]) -> str:
        """Generate dates"""
        year = random.randint(2020, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    def _generate_text(self, col_info: Dict[str, Any]) -> str:
        """Generate text from sample patterns"""
        sample_values = [v for v in col_info["sample_values"] if v is not None]
        if sample_values:
            return random.choice(sample_values)
        return f"Generated text {random.randint(1, 1000)}"
    
    def _generate_boolean(self, col_info: Dict[str, Any]) -> bool:
        """Generate boolean values"""
        return random.choice([True, False])
