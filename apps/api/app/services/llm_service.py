"""
LLM Service - Multi-Provider Support (Anthropic Claude & Groq)
=================================================================
Handles AI-powered sample generation, request refinement, and creative data generation.

Features:
- Refining user data generation requests
- Generating sample data (10-50 rows)
- Analyzing patterns for data factory
- Creative/narrative data generation
- Sync methods for Celery workers
"""
import logging
import json
import re
import httpx
from typing import Dict, List, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import GenerationError

logger = logging.getLogger(__name__)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class LLMColumnConfig(BaseModel):
    """Column configuration for LLM generation."""
    name: str
    description: str = Field(default="", description="Natural language description of what this column should contain")
    data_type: str = Field(default="string", description="Expected data type")
    examples: Optional[List[str]] = Field(default=None, description="Example values to guide generation")
    constraints: Optional[str] = Field(default=None, description="Any constraints like format, range, etc.")


class LLMGenerateRequest(BaseModel):
    """Request model for LLM data generation."""
    num_rows: int = Field(..., gt=0, le=1000, description="Number of rows (limited for LLM)")
    columns: List[LLMColumnConfig]
    context: Optional[str] = Field(default=None, description="Overall context for the dataset")
    style: str = Field(default="realistic", description="Data style: realistic, creative, formal, casual")
    domain: Optional[str] = Field(default=None, description="Domain: healthcare, finance, ecommerce, etc.")


# =============================================================================
# LLM SERVICE CLASS  
# =============================================================================

class LLMService:
    """
    Multi-provider LLM integration supporting:
    - Groq (Free, Fast, Llama models)
    - Anthropic Claude (Premium, High Quality)
    
    Features:
    1. Refining user data generation requests
    2. Generating sample data (10-50 rows)
    3. Analyzing patterns for data factory
    """
    
    def __init__(self):
        """Initialize LLM client (Groq preferred, fallback to Anthropic)"""
        self.provider = None
        self.client = None
        
        # Try Groq first (free alternative)
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                # Don't pass unsupported parameters to Groq client
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                self.provider = "groq"
                self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
                self.max_tokens = 4096
                logger.info(f"Using Groq LLM provider with model {self.model}")
            except ImportError:
                logger.warning("Groq library not installed. Install with: pip install groq")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                logger.debug(f"Groq initialization error details: {type(e).__name__}: {str(e)}")
        
        # Fallback to Anthropic Claude
        if not self.client and settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.provider = "anthropic"
                self.model = "claude-3-5-sonnet-20241022"
                self.max_tokens = 4096
                logger.info("Using Anthropic Claude LLM provider")
            except ImportError:
                logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
        
        if not self.client:
            logger.warning("No LLM provider available, using fallback methods")
    
    def _call_llm(self, prompt: str) -> str:
        """Unified LLM call method for both providers"""
        if not self.client:
            raise ValueError("No LLM client available")
        
        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        raise ValueError(f"Unknown provider: {self.provider}")
    
    def refine_request(self, user_description: str, sample_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Refine user's natural language description into structured requirements
        
        Args:
            user_description: Natural language description of desired data
            sample_data: Optional sample data (CSV, JSON, or text) to infer schema from
        
        Example:
        Input: "I need customer data for testing"
        Output: {
            "columns": ["id", "name", "email", "phone", "created_at"],
            "types": {"id": "integer", "name": "string", ...},
            "constraints": {...},
            "suggested_row_count": 1000
        }
        """
        if not self.client:
            return self._fallback_refinement(user_description)
        
        try:
            # Build the prompt with optional sample data context
            sample_context = ""
            if sample_data:
                # Truncate sample data if too long (keep first 2000 chars)
                truncated_sample = sample_data[:2000] if len(sample_data) > 2000 else sample_data
                sample_context = f"""

The user has also provided sample data to help you understand the structure they need:
```
{truncated_sample}
```
Analyze this sample data to understand the column structure, data types, and patterns.
Your schema should match or extend this sample format while following the description."""

            prompt = f"""You are a data generation expert. A user wants to generate synthetic data.
Analyze their description and provide a structured JSON schema.

User description: "{user_description}"{sample_context}

Return a JSON object with:
- columns: Array of column names
- types: Object mapping column to data type (string, integer, float, date, boolean, email, phone, etc.)
- constraints: Object with any constraints (unique, range, format, etc.)
- suggested_row_count: Recommended number of rows
- description: Refined clear description of the dataset

Be specific and practical. Include common fields like id, created_at, updated_at if relevant.
Return ONLY valid JSON, no markdown or explanation."""

            response_text = self._call_llm(prompt)
            
            # Parse response - handle markdown code blocks
            import json
            
            # Extract JSON from markdown code blocks if present
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```"):
                # Remove markdown code block markers
                lines = cleaned_response.split("\n")
                # Remove first line (```json or ```)
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_response = "\n".join(lines)
            
            # Try to find JSON object in response
            json_start = cleaned_response.find("{")
            json_end = cleaned_response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                cleaned_response = cleaned_response[json_start:json_end]
            
            result = json.loads(cleaned_response)
            
            logger.info(f"Refined request: {len(result.get('columns', []))} columns identified")
            return result
            
        except Exception as e:
            logger.error(f"LLM refinement failed: {e}")
            return self._fallback_refinement(user_description)
    
    def generate_sample_data(
        self,
        schema: Dict[str, Any],
        row_count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate sample data rows using LLM
        
        Args:
            schema: Data schema from refine_request()
            row_count: Number of sample rows (10-50 recommended)
            
        Returns:
            List of sample data dictionaries
        """
        if not self.client:
            return self._fallback_sample_data(schema, row_count)
        
        try:
            prompt = f"""Generate {row_count} realistic sample data rows based on this schema:

{schema}

Rules:
- Generate REALISTIC and DIVERSE data (not "John Doe 1", "John Doe 2")
- Follow all constraints and types exactly
- Make data look like real production data
- Return ONLY a JSON array of objects, no markdown

Example format: [{{"col1": "value1", "col2": "value2"}}, ...]"""

            response_text = self._call_llm(prompt)
            
            # Parse response
            import json
            sample_data = json.loads(response_text)
            
            if not isinstance(sample_data, list):
                raise ValueError("LLM did not return array")
            
            logger.info(f"Generated {len(sample_data)} sample rows")
            return sample_data[:row_count]  # Limit to requested count
            
        except Exception as e:
            logger.error(f"LLM sample generation failed: {e}")
            return self._fallback_sample_data(schema, row_count)
    
    def analyze_data_patterns(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sample data to extract patterns for data factory
        
        Returns:
            Pattern analysis including distributions, correlations, constraints
        """
        if not self.client or not sample_data:
            return {"patterns": "basic"}
        
        try:
            import json
            
            prompt = f"""Analyze these sample data rows and extract patterns for synthetic data generation:

{json.dumps(sample_data[:5], indent=2)}

Identify:
- Data type for each column
- Value ranges and distributions
- Relationships between columns
- Constraints (uniqueness, format patterns, etc.)
- Any correlations or dependencies

Return JSON with analysis for data generation algorithms."""

            response_text = self._call_llm(prompt)
            analysis = json.loads(response_text)
            logger.info("Data pattern analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {"error": str(e)}
    
    def suggest_improvements(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements to the data schema
        
        Returns:
            Suggestions for additional columns, better types, constraints
        """
        if not self.client:
            return {"suggestions": []}
        
        try:
            import json
            
            prompt = f"""Review this data schema and suggest improvements:

{json.dumps(schema, indent=2)}

Provide:
- Missing important columns (e.g., created_at, updated_at, status)
- Better data types if current ones are suboptimal
- Recommended constraints for data quality
- Indexing suggestions for better performance

Return JSON with concrete suggestions."""

            response_text = self._call_llm(prompt)
            suggestions = json.loads(response_text)
            logger.info("Schema improvement suggestions generated")
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return {"suggestions": [], "error": str(e)}
    
    # Fallback methods when LLM is not available
    
    def _fallback_refinement(self, description: str) -> Dict[str, Any]:
        """Basic refinement without LLM"""
        return {
            "columns": ["id", "name", "email", "created_at"],
            "types": {
                "id": "integer",
                "name": "string",
                "email": "email",
                "created_at": "datetime"
            },
            "constraints": {"id": {"unique": True}},
            "suggested_row_count": 1000,
            "description": description
        }
    
    def _fallback_sample_data(self, schema: Dict[str, Any], row_count: int) -> List[Dict[str, Any]]:
        """Generate basic sample data without LLM"""
        import random
        from datetime import datetime
        
        sample = []
        columns = schema.get("columns", ["id", "name", "value"])
        
        for i in range(row_count):
            row = {}
            for col in columns:
                if "id" in col.lower():
                    row[col] = i + 1
                elif "name" in col.lower():
                    row[col] = f"Sample {i + 1}"
                elif "email" in col.lower():
                    row[col] = f"user{i + 1}@example.com"
                elif "date" in col.lower() or "time" in col.lower():
                    row[col] = datetime.now().isoformat()
                else:
                    row[col] = f"Value {i + 1}"
            sample.append(row)
        
        return sample

    # =========================================================================
    # CREATIVE DATA GENERATION (for unique, narrative-style data)
    # =========================================================================
    
    def generate_creative_data(
        self,
        request: LLMGenerateRequest,
        batch_size: int = 25,
    ) -> pd.DataFrame:
        """
        Generate creative/narrative data using LLM.
        Best for: product descriptions, reviews, bios, story content.
        
        Args:
            request: LLMGenerateRequest with columns and context
            batch_size: Rows per LLM call (25-50 recommended)
        
        Returns:
            DataFrame with generated data
        """
        if not self.client:
            logger.warning("No LLM client, using fallback")
            return self._fallback_creative_data(request)
        
        all_rows = []
        remaining = request.num_rows
        
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            
            try:
                batch_data = self._generate_creative_batch(request, current_batch)
                all_rows.extend(batch_data)
                remaining -= len(batch_data)
                
                logger.info(f"Generated {len(all_rows)}/{request.num_rows} creative rows")
                
            except Exception as e:
                logger.error(f"Creative batch generation failed: {e}")
                if not all_rows:
                    raise GenerationError(f"LLM generation failed: {str(e)}")
                break
        
        return pd.DataFrame(all_rows)
    
    def _generate_creative_batch(
        self, 
        request: LLMGenerateRequest, 
        num_rows: int
    ) -> List[Dict[str, Any]]:
        """Generate a single batch of creative data."""
        
        # Build column descriptions
        column_specs = []
        for col in request.columns:
            spec = f"- {col.name}: {col.description or col.data_type}"
            if col.examples:
                spec += f" (examples: {', '.join(col.examples[:3])})"
            if col.constraints:
                spec += f" [{col.constraints}]"
            column_specs.append(spec)
        
        prompt = f"""Generate exactly {num_rows} unique and creative data rows.

Context: {request.context or "General synthetic data generation"}
Domain: {request.domain or "general"}
Style: {request.style}

Columns to generate:
{chr(10).join(column_specs)}

Requirements:
1. Each row must be UNIQUE and REALISTIC
2. Data should be diverse (no repetitive patterns)
3. Follow the data type and constraints for each column
4. Make content engaging and believable for {request.style} style
5. Return ONLY a valid JSON array of objects

Return exactly {num_rows} rows as a JSON array:
[{{"column1": "value1", "column2": "value2"}}, ...]"""

        response_text = self._call_llm(prompt)
        
        # Parse JSON from response
        data = self._parse_json_response(response_text)
        
        if not isinstance(data, list):
            raise GenerationError("LLM did not return a valid array")
        
        return data[:num_rows]
    
    def _parse_json_response(self, text: str) -> Any:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        text = text.strip()
        
        # Handle ```json ... ``` blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            text = json_match.group(1).strip()
        
        # Try to find JSON array
        if not text.startswith('['):
            array_match = re.search(r'\[[\s\S]*\]', text)
            if array_match:
                text = array_match.group(0)
        
        return json.loads(text)
    
    def _fallback_creative_data(self, request: LLMGenerateRequest) -> pd.DataFrame:
        """Fallback creative data generation without LLM."""
        from faker import Faker
        fake = Faker()
        
        rows = []
        for i in range(request.num_rows):
            row = {}
            for col in request.columns:
                if 'name' in col.name.lower():
                    row[col.name] = fake.name()
                elif 'email' in col.name.lower():
                    row[col.name] = fake.email()
                elif 'description' in col.name.lower() or 'bio' in col.name.lower():
                    row[col.name] = fake.paragraph(nb_sentences=3)
                elif 'title' in col.name.lower():
                    row[col.name] = fake.sentence(nb_words=5)
                elif 'date' in col.name.lower():
                    row[col.name] = fake.date()
                elif col.data_type == 'integer':
                    row[col.name] = fake.random_int(min=1, max=1000)
                elif col.data_type == 'float':
                    row[col.name] = round(fake.pyfloat(min_value=0, max_value=100), 2)
                elif col.data_type == 'boolean':
                    row[col.name] = fake.boolean()
                else:
                    row[col.name] = fake.sentence()
            rows.append(row)
        
        return pd.DataFrame(rows)

    # =========================================================================
    # SYNC METHODS FOR CELERY WORKERS
    # =========================================================================
    
    def _call_groq_api_sync(self, prompt: str) -> str:
        """
        Synchronous Groq API call for Celery workers.
        Uses httpx instead of async client.
        """
        if not settings.GROQ_API_KEY:
            raise GenerationError("Groq API key not configured")
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def generate_creative_data_sync(
        self,
        request: LLMGenerateRequest,
        batch_size: int = 25,
        progress_callback: Optional[callable] = None,
    ) -> pd.DataFrame:
        """
        Synchronous version for Celery workers.
        Uses httpx for HTTP calls instead of async clients.
        
        Args:
            request: LLMGenerateRequest with columns and context
            batch_size: Rows per API call
            progress_callback: Optional callback(current, total) for progress updates
        
        Returns:
            DataFrame with generated data
        """
        all_rows = []
        remaining = request.num_rows
        
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            
            try:
                # Build prompt
                column_specs = []
                for col in request.columns:
                    spec = f"- {col.name}: {col.description or col.data_type}"
                    if col.examples:
                        spec += f" (examples: {', '.join(col.examples[:3])})"
                    column_specs.append(spec)
                
                prompt = f"""Generate exactly {current_batch} unique data rows.

Context: {request.context or "Synthetic data"}
Style: {request.style}

Columns:
{chr(10).join(column_specs)}

Return ONLY a JSON array. No markdown, no explanation.
[{{"col1": "val1", ...}}, ...]"""

                # Call API synchronously
                response_text = self._call_groq_api_sync(prompt)
                batch_data = self._parse_json_response(response_text)
                
                if isinstance(batch_data, list):
                    all_rows.extend(batch_data[:current_batch])
                    remaining -= len(batch_data[:current_batch])
                    
                    if progress_callback:
                        progress_callback(len(all_rows), request.num_rows)
                    
                    logger.info(f"Generated {len(all_rows)}/{request.num_rows} rows")
                
            except Exception as e:
                logger.error(f"Sync generation failed: {e}")
                if not all_rows:
                    raise GenerationError(f"LLM generation failed: {str(e)}")
                break
        
        return pd.DataFrame(all_rows)


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get singleton LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
