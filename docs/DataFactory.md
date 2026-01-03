# Synthesize.io - Data Factory Architecture

**Version:** 1.0  
**Date:** January 3, 2026  
**Status:** Technical Specification  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Library Evaluation](#3-library-evaluation)
4. [Recommended Architecture](#4-recommended-architecture)
5. [Implementation Plan](#5-implementation-plan)
6. [Data Type Generators](#6-data-type-generators)
7. [Quality & Validation](#7-quality--validation)
8. [Performance Optimization](#8-performance-optimization)

---

## 1. Executive Summary

### 1.1 Purpose

The Data Factory is the core engine of Synthesize.io responsible for generating high-quality synthetic datasets at scale. This document outlines the technical architecture, library choices, and implementation strategy for building a production-grade data generation system.

### 1.2 Design Philosophy

**Three-Stage Pipeline** (as defined in Whitepaper):
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 1: LLM Sample Generation (Anthropic Claude)                      │
│  - User submits natural language request                                │
│  - LLM interprets and generates small sample (10-50 rows)               │
│  - Cost: ~$0.01-0.05 per request                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 2: Pattern Analysis Engine                                       │
│  - Extract statistical distributions from sample                        │
│  - Identify data types, constraints, relationships                      │
│  - Create generation templates                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 3: Bulk Generation (Data Factory)                                │
│  - Deterministic algorithms replicate patterns at scale                 │
│  - Target: 100K+ rows/minute                                            │
│  - Cost: ~$0 (algorithmic, no API calls)                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Key Requirements

| Requirement | Target | Priority |
|-------------|--------|----------|
| Generation Speed | 100,000+ rows/minute | P0 |
| Data Quality Score | >95% | P0 |
| Uniqueness Enforcement | 100% for specified fields | P0 |
| Referential Integrity | 100% for related tables | P0 |
| Format Compliance | 100% (email, phone, SSN, etc.) | P0 |
| Statistical Accuracy | Distribution matching >90% | P1 |
| Localization Support | 50+ locales | P1 |

---

## 2. Current State Analysis

### 2.1 Existing Implementation

**Location:** `apps/api/app/services/data_factory.py`

**Current Capabilities:**
- Basic type inference from column names
- Simple random generators for 8 data types
- No statistical distribution matching
- No uniqueness enforcement
- No referential integrity
- Limited name/address pools (~8 items each)

**Current Limitations:**
```python
# Current naive implementation
def _generate_name(self, col_info):
    first_names = ["John", "Jane", "Alice", "Bob", ...]  # Only 8 names!
    last_names = ["Smith", "Johnson", ...]  # Only 7 names!
    return f"{random.choice(first_names)} {random.choice(last_names)}"
```

**Problems:**
1. **Low Diversity**: ~56 unique name combinations (8×7)
2. **No Localization**: Only English names
3. **No Realism**: Random combinations like "John Smith" repeated often
4. **No Validation**: Emails don't follow realistic patterns
5. **Performance**: ~1,000 rows/minute (target: 100,000+)

---

## 3. Library Evaluation

### 3.1 Library Comparison Matrix

| Library | Use Case | Speed | Quality | Complexity | License |
|---------|----------|-------|---------|------------|---------|
| **Faker** | Fake data (names, emails, etc.) | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Low | MIT |
| **Mimesis** | Fake data (faster than Faker) | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Low | MIT |
| **SDV** | Statistical ML synthesis | ⚡⚡ | ⭐⭐⭐⭐⭐ | Medium | BSL |
| **Synthcity** | GAN/VAE-based synthesis | ⚡ | ⭐⭐⭐⭐⭐ | High | Apache 2.0 |
| **Gretel** | ACTGAN, TimeSeries DGAN | ⚡⚡ | ⭐⭐⭐⭐ | Medium | Gretel SAL |
| **YData** | CTGAN, TimeGAN | ⚡⚡ | ⭐⭐⭐⭐ | Medium | MIT |

### 3.2 Faker - Primary Fake Data Library

**Best For:** Fast generation of realistic-looking fake data

**Strengths:**
- 100+ locales (en_US, de_DE, ja_JP, hi_IN, etc.)
- 20+ built-in providers (person, address, company, credit_card, etc.)
- Uniqueness support via `fake.unique.field()`
- Seeding for reproducibility
- Custom provider support
- Very fast (~500K+ records/minute for simple fields)

**Usage Example:**
```python
from faker import Faker

fake = Faker(['en_US', 'en_IN', 'de_DE'])
fake.seed_instance(42)  # Reproducibility

# Generate diverse data
name = fake.name()           # "Dr. Sarah Johnson"
email = fake.email()         # "sjohnson@example.com"
phone = fake.phone_number()  # "+1-555-123-4567"
address = fake.address()     # "123 Main St\nNew York, NY 10001"
ssn = fake.ssn()             # "123-45-6789"
credit_card = fake.credit_card_number()  # Luhn-valid!
```

**Providers We'll Use:**
- `faker.providers.person` - Names, prefixes, suffixes
- `faker.providers.address` - Addresses, cities, countries
- `faker.providers.company` - Company names, catch phrases
- `faker.providers.credit_card` - Luhn-valid card numbers
- `faker.providers.bank` - IBAN, SWIFT, account numbers
- `faker.providers.date_time` - Dates, times, timestamps
- `faker.providers.internet` - Emails, URLs, IPs, domains
- `faker.providers.phone_number` - Country-specific formats
- `faker.providers.ssn` - SSN, tax IDs
- `faker.providers.job` - Job titles, departments

### 3.3 SDV (Synthetic Data Vault) - Statistical Synthesis

**Best For:** Learning and replicating statistical distributions from sample data

**Strengths:**
- Learns correlations between columns
- Preserves statistical properties (mean, std, distributions)
- Multi-table support with foreign key relationships
- Multiple synthesizer options

**Synthesizers:**
| Synthesizer | Method | Speed | Quality |
|-------------|--------|-------|---------|
| GaussianCopulaSynthesizer | Copula-based | Fast | Good |
| CTGANSynthesizer | GAN-based | Slow | Excellent |
| TVAESynthesizer | VAE-based | Medium | Very Good |
| CopulaGANSynthesizer | Hybrid | Medium | Very Good |

**Usage Example:**
```python
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import Metadata

# Learn from LLM sample
metadata = Metadata.detect_from_dataframe(sample_df)
synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(sample_df)

# Generate at scale
synthetic_data = synthesizer.sample(num_rows=100000)
```

**When to Use SDV:**
- User wants statistical accuracy (ML training data)
- Sample has complex correlations (age↔income, location↔price)
- Multi-table relational datasets
- NOT for simple fake data (overkill, slower)

### 3.4 Synthcity - Advanced ML Synthesis

**Best For:** Privacy-preserving synthesis, research-grade quality

**Strengths:**
- 15+ generator models (CTGAN, TVAE, AdsGAN, PrivBayes, etc.)
- Built-in privacy metrics (k-anonymity, l-diversity)
- Comprehensive evaluation metrics
- Time-series support (TimeGAN, FourierFlows)
- Survival analysis support

**Available Models:**
```python
from synthcity.plugins import Plugins

# List available models
Plugins(categories=["generic", "privacy"]).list()
# ['adsgan', 'ctgan', 'tvae', 'nflow', 'bayesian_network', 
#  'privbayes', 'dpgan', 'pategan', ...]
```

**When to Use Synthcity:**
- Enterprise tier with privacy requirements
- Healthcare/financial data with strict compliance
- When user explicitly requests "privacy-preserving" synthesis
- NOT for standard generation (too slow, complex)

### 3.5 Custom Generators - Domain-Specific Data

**Best For:** Specialized data types not covered by libraries

**Examples:**
- Luhn-valid credit card numbers
- Valid ISBN/ISSN numbers
- Realistic transaction patterns
- Time-series with seasonality
- Correlated financial data

---

## 4. Recommended Architecture

### 4.1 Hybrid Multi-Engine Approach

We will use a **tiered generation strategy** that selects the optimal engine based on data type and user requirements:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Factory Orchestrator                        │
│                    (apps/api/app/services/data_factory.py)              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Tier 1: Fast    │   │  Tier 2: Smart    │   │  Tier 3: ML-Based │
│   (Faker/Custom)  │   │  (Pattern Match)  │   │  (SDV/Synthcity)  │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ • Names, Emails   │   │ • Distributions   │   │ • Complex corr.   │
│ • Phones, SSN     │   │ • Constraints     │   │ • Privacy-pres.   │
│ • Addresses       │   │ • Relationships   │   │ • Multi-table     │
│ • Dates, IDs      │   │ • Business rules  │   │ • Time-series     │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ Speed: 500K/min   │   │ Speed: 100K/min   │   │ Speed: 10K/min    │
│ Quality: Good     │   │ Quality: V.Good   │   │ Quality: Excellent│
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

### 4.2 Component Architecture

```python
# apps/api/app/services/data_factory/
├── __init__.py
├── orchestrator.py          # Main DataFactory class
├── analyzers/
│   ├── __init__.py
│   ├── pattern_analyzer.py  # Analyze LLM sample patterns
│   ├── type_detector.py     # Detect column data types
│   └── distribution_analyzer.py  # Statistical distribution fitting
├── generators/
│   ├── __init__.py
│   ├── base.py              # BaseGenerator abstract class
│   ├── personal.py          # Names, emails, phones, SSN
│   ├── financial.py         # Credit cards, transactions, amounts
│   ├── temporal.py          # Dates, timestamps, durations
│   ├── geographic.py        # Addresses, coordinates, countries
│   ├── identifier.py        # UUIDs, order IDs, invoice numbers
│   ├── categorical.py       # Enums, statuses, categories
│   ├── numerical.py         # Numbers with distributions
│   ├── text.py              # Lorem ipsum, sentences, paragraphs
│   └── custom.py            # User-defined patterns
├── synthesizers/
│   ├── __init__.py
│   ├── sdv_synthesizer.py   # SDV wrapper for statistical synthesis
│   └── privacy_synthesizer.py  # Synthcity wrapper for privacy
├── validators/
│   ├── __init__.py
│   ├── format_validator.py  # Regex, Luhn, checksum validation
│   ├── uniqueness_validator.py  # Ensure unique values
│   └── integrity_validator.py   # Foreign key validation
└── exporters/
    ├── __init__.py
    └── batch_exporter.py    # Efficient batch writing
```

### 4.3 Core Classes

#### DataFactory Orchestrator
```python
# apps/api/app/services/data_factory/orchestrator.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class GenerationTier(Enum):
    FAST = "fast"           # Faker-based, simple types
    SMART = "smart"         # Pattern matching, constraints
    ML_BASED = "ml_based"   # SDV/Synthcity

@dataclass
class ColumnSpec:
    name: str
    data_type: str
    generator: str
    constraints: Dict[str, Any]
    nullable: bool = False
    unique: bool = False
    
@dataclass
class DataSchema:
    columns: List[ColumnSpec]
    row_count: int
    tier: GenerationTier
    relationships: Optional[Dict[str, str]] = None

class DataFactory:
    """
    Main orchestrator for synthetic data generation.
    Selects optimal generation strategy based on data requirements.
    """
    
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self.faker = self._init_faker()
        self.generators = self._init_generators()
        self.validators = self._init_validators()
        
    def generate(
        self,
        sample_data: List[Dict[str, Any]],
        row_count: int,
        constraints: Optional[Dict[str, Any]] = None,
        tier: GenerationTier = GenerationTier.SMART
    ) -> pd.DataFrame:
        """
        Main generation entry point.
        
        Args:
            sample_data: LLM-generated sample (10-50 rows)
            row_count: Target number of rows
            constraints: Column constraints (unique, ranges, etc.)
            tier: Generation strategy tier
            
        Returns:
            Generated DataFrame
        """
        # Step 1: Analyze sample
        schema = self.analyze_sample(sample_data, constraints)
        
        # Step 2: Select generation strategy
        if tier == GenerationTier.ML_BASED:
            return self._generate_ml_based(sample_data, schema)
        elif tier == GenerationTier.SMART:
            return self._generate_smart(sample_data, schema)
        else:
            return self._generate_fast(schema)
            
    def analyze_sample(
        self,
        sample_data: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None
    ) -> DataSchema:
        """Analyze LLM sample to extract patterns and schema."""
        pass
        
    def _generate_fast(self, schema: DataSchema) -> pd.DataFrame:
        """Fast generation using Faker."""
        pass
        
    def _generate_smart(
        self,
        sample_data: List[Dict[str, Any]],
        schema: DataSchema
    ) -> pd.DataFrame:
        """Smart generation with pattern matching."""
        pass
        
    def _generate_ml_based(
        self,
        sample_data: List[Dict[str, Any]],
        schema: DataSchema
    ) -> pd.DataFrame:
        """ML-based generation using SDV."""
        pass
```

---

## 5. Implementation Plan

### 5.1 Phase 1: Core Generators (Week 1)

**Goal:** Replace basic generators with Faker-based ones

**Deliverables:**
1. Personal data generator (names, emails, phones)
2. Geographic data generator (addresses, cities, countries)
3. Financial data generator (credit cards, amounts)
4. Temporal data generator (dates, timestamps)
5. Identifier generator (UUIDs, order IDs)

**Dependencies to Add:**
```txt
# apps/api/requirements.txt
faker>=24.0.0
mimesis>=12.0.0  # Faster alternative for some types
```

### 5.2 Phase 2: Pattern Analysis (Week 2)

**Goal:** Implement intelligent pattern detection from LLM samples

**Deliverables:**
1. Type detector (auto-detect column types)
2. Distribution analyzer (fit statistical distributions)
3. Constraint extractor (unique, ranges, formats)
4. Relationship mapper (foreign keys)

### 5.3 Phase 3: Statistical Synthesis (Week 3)

**Goal:** Add SDV integration for advanced use cases

**Deliverables:**
1. SDV synthesizer wrapper
2. Multi-table relationship support
3. Distribution preservation
4. Quality metrics

**Dependencies to Add:**
```txt
# apps/api/requirements.txt
sdv>=1.10.0
```

### 5.4 Phase 4: Validation & Quality (Week 4)

**Goal:** Ensure generated data meets quality standards

**Deliverables:**
1. Format validators (email, phone, SSN regex)
2. Semantic validators (Luhn for credit cards)
3. Uniqueness enforcer
4. Quality scorer (target: >95%)

---

## 6. Data Type Generators

### 6.1 Personal Data Generator

```python
# apps/api/app/services/data_factory/generators/personal.py

from faker import Faker
from typing import Dict, Any, Optional, Set
import re

class PersonalDataGenerator:
    """Generate personal information (names, emails, phones, SSN)."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        self._used_emails: Set[str] = set()
        self._used_ssns: Set[str] = set()
        
    def generate_name(
        self,
        style: str = "full",  # full, first, last, prefix
        gender: Optional[str] = None
    ) -> str:
        """Generate realistic names."""
        if style == "first":
            return self.fake.first_name_male() if gender == "male" \
                else self.fake.first_name_female() if gender == "female" \
                else self.fake.first_name()
        elif style == "last":
            return self.fake.last_name()
        elif style == "prefix":
            return self.fake.prefix()
        else:
            return self.fake.name()
    
    def generate_email(
        self,
        domain: Optional[str] = None,
        unique: bool = True
    ) -> str:
        """Generate realistic email addresses."""
        while True:
            if domain:
                username = self.fake.user_name()
                email = f"{username}@{domain}"
            else:
                email = self.fake.email()
            
            if not unique or email not in self._used_emails:
                self._used_emails.add(email)
                return email
    
    def generate_phone(
        self,
        format: str = "e164"  # e164, national, international
    ) -> str:
        """Generate phone numbers in various formats."""
        if format == "e164":
            return self.fake.phone_number()
        elif format == "national":
            return self.fake.phone_number()
        else:
            return self.fake.phone_number()
    
    def generate_ssn(self, unique: bool = True) -> str:
        """Generate valid-format SSN."""
        while True:
            ssn = self.fake.ssn()
            if not unique or ssn not in self._used_ssns:
                self._used_ssns.add(ssn)
                return ssn
    
    def generate_username(self) -> str:
        """Generate usernames."""
        return self.fake.user_name()
    
    def generate_password(
        self,
        length: int = 12,
        special_chars: bool = True
    ) -> str:
        """Generate secure passwords."""
        return self.fake.password(
            length=length,
            special_chars=special_chars
        )
```

### 6.2 Financial Data Generator

```python
# apps/api/app/services/data_factory/generators/financial.py

from faker import Faker
from typing import Dict, Any, Optional, Tuple
import random
from decimal import Decimal, ROUND_HALF_UP

class FinancialDataGenerator:
    """Generate financial data (credit cards, transactions, amounts)."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        
    def generate_credit_card(
        self,
        card_type: Optional[str] = None  # visa, mastercard, amex
    ) -> Dict[str, str]:
        """Generate Luhn-valid credit card details."""
        if card_type:
            number = self.fake.credit_card_number(card_type=card_type)
        else:
            number = self.fake.credit_card_number()
            
        return {
            "number": number,
            "expiry": self.fake.credit_card_expire(),
            "cvv": self.fake.credit_card_security_code(),
            "provider": self.fake.credit_card_provider()
        }
    
    def generate_amount(
        self,
        min_val: float = 0.01,
        max_val: float = 10000.00,
        distribution: str = "uniform",  # uniform, normal, exponential
        decimal_places: int = 2
    ) -> Decimal:
        """Generate monetary amounts with realistic distributions."""
        if distribution == "normal":
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6
            value = random.gauss(mean, std)
            value = max(min_val, min(max_val, value))
        elif distribution == "exponential":
            # Exponential for transaction amounts (many small, few large)
            scale = (max_val - min_val) / 5
            value = min_val + random.expovariate(1/scale)
            value = min(max_val, value)
        else:
            value = random.uniform(min_val, max_val)
            
        return Decimal(str(value)).quantize(
            Decimal(10) ** -decimal_places,
            rounding=ROUND_HALF_UP
        )
    
    def generate_iban(self, country_code: str = "DE") -> str:
        """Generate valid IBAN."""
        return self.fake.iban()
    
    def generate_swift(self) -> str:
        """Generate SWIFT/BIC code."""
        return self.fake.swift()
    
    def generate_transaction_id(
        self,
        prefix: str = "TXN",
        length: int = 12
    ) -> str:
        """Generate transaction IDs."""
        suffix = ''.join(random.choices('0123456789ABCDEF', k=length))
        return f"{prefix}-{suffix}"
    
    def generate_invoice_number(
        self,
        prefix: str = "INV",
        year: Optional[int] = None
    ) -> str:
        """Generate invoice numbers."""
        import datetime
        year = year or datetime.datetime.now().year
        seq = random.randint(1, 999999)
        return f"{prefix}-{year}-{seq:06d}"
```

### 6.3 Temporal Data Generator

```python
# apps/api/app/services/data_factory/generators/temporal.py

from faker import Faker
from typing import Optional, Tuple
from datetime import datetime, date, timedelta
import random

class TemporalDataGenerator:
    """Generate dates, times, and timestamps."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        
    def generate_date(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        distribution: str = "uniform"  # uniform, recent_bias
    ) -> date:
        """Generate dates within range."""
        start = start_date or date(2020, 1, 1)
        end = end_date or date.today()
        
        if distribution == "recent_bias":
            # Bias towards more recent dates
            days_range = (end - start).days
            # Use beta distribution to bias towards end
            beta_val = random.betavariate(2, 5)
            offset = int(days_range * (1 - beta_val))
            return start + timedelta(days=offset)
        else:
            return self.fake.date_between(
                start_date=start,
                end_date=end
            )
    
    def generate_datetime(
        self,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        business_hours: bool = False
    ) -> datetime:
        """Generate datetime values."""
        start = start_datetime or datetime(2020, 1, 1)
        end = end_datetime or datetime.now()
        
        dt = self.fake.date_time_between(
            start_date=start,
            end_date=end
        )
        
        if business_hours:
            # Adjust to business hours (9 AM - 6 PM)
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            dt = dt.replace(hour=hour, minute=minute)
            
            # Skip weekends
            while dt.weekday() >= 5:
                dt += timedelta(days=1)
                
        return dt
    
    def generate_timestamp(self) -> str:
        """Generate ISO format timestamp."""
        return self.generate_datetime().isoformat()
    
    def generate_duration(
        self,
        min_minutes: int = 1,
        max_minutes: int = 480,
        unit: str = "minutes"
    ) -> int:
        """Generate duration values."""
        minutes = random.randint(min_minutes, max_minutes)
        if unit == "seconds":
            return minutes * 60
        elif unit == "hours":
            return minutes // 60
        return minutes
```

### 6.4 Identifier Generator

```python
# apps/api/app/services/data_factory/generators/identifier.py

import uuid
import random
import string
from typing import Optional, Set
from datetime import datetime

class IdentifierGenerator:
    """Generate unique identifiers (UUIDs, order IDs, SKUs)."""
    
    def __init__(self):
        self._used_ids: Set[str] = set()
        self._sequence_counters: dict = {}
        
    def generate_uuid(self, version: int = 4) -> str:
        """Generate UUID."""
        if version == 4:
            return str(uuid.uuid4())
        elif version == 1:
            return str(uuid.uuid1())
        else:
            return str(uuid.uuid4())
    
    def generate_order_id(
        self,
        prefix: str = "ORD",
        length: int = 8,
        unique: bool = True
    ) -> str:
        """Generate order IDs like ORD-12345678."""
        while True:
            suffix = ''.join(random.choices(string.digits, k=length))
            order_id = f"{prefix}-{suffix}"
            
            if not unique or order_id not in self._used_ids:
                self._used_ids.add(order_id)
                return order_id
    
    def generate_sku(
        self,
        category_code: Optional[str] = None,
        length: int = 6
    ) -> str:
        """Generate SKU codes like CAT-ABC123."""
        category = category_code or ''.join(
            random.choices(string.ascii_uppercase, k=3)
        )
        suffix = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=length)
        )
        return f"{category}-{suffix}"
    
    def generate_sequential_id(
        self,
        prefix: str = "ID",
        start: int = 1
    ) -> str:
        """Generate sequential IDs."""
        if prefix not in self._sequence_counters:
            self._sequence_counters[prefix] = start
        
        current = self._sequence_counters[prefix]
        self._sequence_counters[prefix] += 1
        return f"{prefix}-{current:08d}"
    
    def generate_slug(self, text: str) -> str:
        """Generate URL-friendly slugs."""
        import re
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]
```

### 6.5 Geographic Data Generator

```python
# apps/api/app/services/data_factory/generators/geographic.py

from faker import Faker
from typing import Dict, Any, Optional, Tuple
import random

class GeographicDataGenerator:
    """Generate geographic data (addresses, coordinates, countries)."""
    
    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        
    def generate_address(
        self,
        include_country: bool = False
    ) -> Dict[str, str]:
        """Generate full address."""
        return {
            "street": self.fake.street_address(),
            "city": self.fake.city(),
            "state": self.fake.state(),
            "zip_code": self.fake.zipcode(),
            "country": self.fake.country() if include_country else None
        }
    
    def generate_street_address(self) -> str:
        """Generate street address."""
        return self.fake.street_address()
    
    def generate_city(self) -> str:
        """Generate city name."""
        return self.fake.city()
    
    def generate_state(self) -> str:
        """Generate state/province."""
        return self.fake.state()
    
    def generate_country(self) -> str:
        """Generate country name."""
        return self.fake.country()
    
    def generate_country_code(self, format: str = "alpha-2") -> str:
        """Generate country code (ISO 3166-1)."""
        if format == "alpha-3":
            return self.fake.country_code(representation="alpha-3")
        return self.fake.country_code()
    
    def generate_coordinates(
        self,
        bounds: Optional[Dict[str, float]] = None
    ) -> Tuple[float, float]:
        """Generate latitude/longitude coordinates."""
        if bounds:
            lat = random.uniform(bounds["min_lat"], bounds["max_lat"])
            lon = random.uniform(bounds["min_lon"], bounds["max_lon"])
        else:
            lat = float(self.fake.latitude())
            lon = float(self.fake.longitude())
        return (lat, lon)
    
    def generate_timezone(self) -> str:
        """Generate timezone."""
        return self.fake.timezone()
    
    def generate_ip_address(
        self,
        version: int = 4,
        private: bool = False
    ) -> str:
        """Generate IP address."""
        if private and version == 4:
            return self.fake.ipv4_private()
        elif version == 6:
            return self.fake.ipv6()
        return self.fake.ipv4()
```

### 6.6 Categorical & Numerical Generators

```python
# apps/api/app/services/data_factory/generators/categorical.py

from typing import List, Dict, Any, Optional
import random
import numpy as np

class CategoricalDataGenerator:
    """Generate categorical data with weighted distributions."""
    
    def generate_from_list(
        self,
        values: List[Any],
        weights: Optional[List[float]] = None
    ) -> Any:
        """Generate value from predefined list."""
        if weights:
            return random.choices(values, weights=weights, k=1)[0]
        return random.choice(values)
    
    def generate_status(
        self,
        statuses: Optional[List[str]] = None,
        weights: Optional[List[float]] = None
    ) -> str:
        """Generate status values."""
        default_statuses = ["active", "inactive", "pending", "completed"]
        default_weights = [0.6, 0.1, 0.15, 0.15]
        
        statuses = statuses or default_statuses
        weights = weights or default_weights[:len(statuses)]
        
        return self.generate_from_list(statuses, weights)
    
    def generate_enum(
        self,
        enum_values: List[str],
        distribution: Dict[str, float] = None
    ) -> str:
        """Generate enum values with distribution."""
        if distribution:
            weights = [distribution.get(v, 1.0) for v in enum_values]
            return self.generate_from_list(enum_values, weights)
        return random.choice(enum_values)


class NumericalDataGenerator:
    """Generate numerical data with statistical distributions."""
    
    def generate_integer(
        self,
        min_val: int = 0,
        max_val: int = 100,
        distribution: str = "uniform"
    ) -> int:
        """Generate integer with distribution."""
        if distribution == "normal":
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6
            value = int(np.random.normal(mean, std))
            return max(min_val, min(max_val, value))
        elif distribution == "poisson":
            lam = (min_val + max_val) / 2
            return max(min_val, min(max_val, np.random.poisson(lam)))
        return random.randint(min_val, max_val)
    
    def generate_float(
        self,
        min_val: float = 0.0,
        max_val: float = 100.0,
        distribution: str = "uniform",
        decimal_places: int = 2
    ) -> float:
        """Generate float with distribution."""
        if distribution == "normal":
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6
            value = np.random.normal(mean, std)
            value = max(min_val, min(max_val, value))
        elif distribution == "exponential":
            scale = (max_val - min_val) / 3
            value = min_val + np.random.exponential(scale)
            value = min(max_val, value)
        elif distribution == "log_normal":
            mean = np.log((min_val + max_val) / 2)
            value = np.random.lognormal(mean, 0.5)
            value = max(min_val, min(max_val, value))
        else:
            value = random.uniform(min_val, max_val)
            
        return round(value, decimal_places)
    
    def generate_percentage(
        self,
        min_val: float = 0.0,
        max_val: float = 100.0
    ) -> float:
        """Generate percentage value."""
        return round(random.uniform(min_val, max_val), 2)
```

---

## 7. Quality & Validation

### 7.1 Validation Framework

```python
# apps/api/app/services/data_factory/validators/format_validator.py

import re
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0.0 to 1.0

class FormatValidator:
    """Validate data format compliance."""
    
    PATTERNS = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone_us": r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
        "phone_intl": r'^\+[1-9]\d{1,14}$',
        "ssn": r'^\d{3}-\d{2}-\d{4}$',
        "zip_us": r'^\d{5}(-\d{4})?$',
        "credit_card": r'^\d{13,19}$',
        "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        "date_iso": r'^\d{4}-\d{2}-\d{2}$',
        "datetime_iso": r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        "ip_v4": r'^(\d{1,3}\.){3}\d{1,3}$',
        "url": r'^https?://[^\s/$.?#].[^\s]*$',
    }
    
    def validate_format(
        self,
        value: Any,
        format_type: str
    ) -> Tuple[bool, str]:
        """Validate value against format pattern."""
        pattern = self.PATTERNS.get(format_type)
        if not pattern:
            return True, ""
            
        if re.match(pattern, str(value), re.IGNORECASE):
            return True, ""
        return False, f"Value '{value}' does not match {format_type} format"
    
    def validate_luhn(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        digits = [int(d) for d in str(card_number) if d.isdigit()]
        if len(digits) < 13:
            return False
            
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
            
        return checksum % 10 == 0


class UniquenessValidator:
    """Ensure uniqueness constraints are met."""
    
    def __init__(self):
        self._seen_values: Dict[str, set] = {}
        
    def check_unique(
        self,
        column: str,
        value: Any
    ) -> Tuple[bool, str]:
        """Check if value is unique for column."""
        if column not in self._seen_values:
            self._seen_values[column] = set()
            
        if value in self._seen_values[column]:
            return False, f"Duplicate value '{value}' in column '{column}'"
            
        self._seen_values[column].add(value)
        return True, ""
    
    def get_duplicate_count(self, column: str) -> int:
        """Get count of duplicates found."""
        return len(self._seen_values.get(column, set()))


class IntegrityValidator:
    """Validate referential integrity."""
    
    def __init__(self):
        self._foreign_keys: Dict[str, set] = {}
        
    def register_primary_key(
        self,
        table: str,
        column: str,
        values: set
    ):
        """Register primary key values for FK validation."""
        key = f"{table}.{column}"
        self._foreign_keys[key] = values
        
    def validate_foreign_key(
        self,
        value: Any,
        references: str  # "table.column"
    ) -> Tuple[bool, str]:
        """Validate FK references existing PK."""
        if references not in self._foreign_keys:
            return True, ""  # No PK registered, skip validation
            
        if value in self._foreign_keys[references]:
            return True, ""
        return False, f"FK violation: '{value}' not found in {references}"
```

### 7.2 Quality Scoring

```python
# apps/api/app/services/data_factory/validators/quality_scorer.py

from typing import Dict, List, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass
class QualityReport:
    overall_score: float  # 0-100
    format_compliance: float
    uniqueness_score: float
    completeness_score: float
    distribution_score: float
    integrity_score: float
    issues: List[str]
    recommendations: List[str]

class QualityScorer:
    """Calculate data quality scores."""
    
    def __init__(self, target_score: float = 95.0):
        self.target_score = target_score
        
    def score_dataset(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> QualityReport:
        """Calculate comprehensive quality score."""
        scores = {
            "format": self._score_format_compliance(df, schema),
            "unique": self._score_uniqueness(df, constraints),
            "complete": self._score_completeness(df, schema),
            "distribution": self._score_distribution(df, schema),
            "integrity": self._score_integrity(df, constraints),
        }
        
        # Weighted average
        weights = {
            "format": 0.25,
            "unique": 0.20,
            "complete": 0.20,
            "distribution": 0.20,
            "integrity": 0.15,
        }
        
        overall = sum(
            scores[k] * weights[k] 
            for k in scores
        )
        
        issues = self._identify_issues(df, schema, scores)
        recommendations = self._generate_recommendations(scores)
        
        return QualityReport(
            overall_score=overall,
            format_compliance=scores["format"],
            uniqueness_score=scores["unique"],
            completeness_score=scores["complete"],
            distribution_score=scores["distribution"],
            integrity_score=scores["integrity"],
            issues=issues,
            recommendations=recommendations
        )
    
    def _score_format_compliance(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any]
    ) -> float:
        """Score format compliance (email, phone, etc.)."""
        validator = FormatValidator()
        total_checks = 0
        passed_checks = 0
        
        for col, spec in schema.items():
            if col not in df.columns:
                continue
                
            format_type = spec.get("format")
            if not format_type:
                continue
                
            for value in df[col].dropna():
                total_checks += 1
                is_valid, _ = validator.validate_format(value, format_type)
                if is_valid:
                    passed_checks += 1
                    
        if total_checks == 0:
            return 100.0
        return (passed_checks / total_checks) * 100
    
    def _score_uniqueness(
        self,
        df: pd.DataFrame,
        constraints: Dict[str, Any]
    ) -> float:
        """Score uniqueness constraints."""
        unique_cols = constraints.get("unique_columns", [])
        if not unique_cols:
            return 100.0
            
        scores = []
        for col in unique_cols:
            if col not in df.columns:
                continue
            total = len(df[col])
            unique = df[col].nunique()
            scores.append((unique / total) * 100)
            
        return np.mean(scores) if scores else 100.0
    
    def _score_completeness(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any]
    ) -> float:
        """Score data completeness (non-null values)."""
        required_cols = [
            col for col, spec in schema.items()
            if not spec.get("nullable", False)
        ]
        
        if not required_cols:
            return 100.0
            
        scores = []
        for col in required_cols:
            if col not in df.columns:
                scores.append(0.0)
                continue
            non_null = df[col].notna().sum()
            total = len(df)
            scores.append((non_null / total) * 100)
            
        return np.mean(scores)
    
    def _score_distribution(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any]
    ) -> float:
        """Score statistical distribution matching."""
        # Compare generated distribution to expected
        # Use KS-test or similar
        return 95.0  # Placeholder
    
    def _score_integrity(
        self,
        df: pd.DataFrame,
        constraints: Dict[str, Any]
    ) -> float:
        """Score referential integrity."""
        # Check FK relationships
        return 100.0  # Placeholder
    
    def _identify_issues(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        scores: Dict[str, float]
    ) -> List[str]:
        """Identify specific quality issues."""
        issues = []
        for metric, score in scores.items():
            if score < 90:
                issues.append(f"{metric} score below threshold: {score:.1f}%")
        return issues
    
    def _generate_recommendations(
        self,
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recs = []
        if scores["format"] < 95:
            recs.append("Review format validation patterns")
        if scores["unique"] < 95:
            recs.append("Increase uniqueness pool size")
        if scores["distribution"] < 90:
            recs.append("Consider using SDV for better distributions")
        return recs
```

---

## 8. Performance Optimization

### 8.1 Batch Generation Strategy

```python
# apps/api/app/services/data_factory/batch_generator.py

import pandas as pd
import numpy as np
from typing import Generator, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

class BatchGenerator:
    """
    High-performance batch data generation.
    Target: 100,000+ rows/minute
    """
    
    def __init__(
        self,
        batch_size: int = 10000,
        num_workers: int = None
    ):
        self.batch_size = batch_size
        self.num_workers = num_workers or multiprocessing.cpu_count()
        
    def generate_in_batches(
        self,
        generator_func,
        total_rows: int,
        **kwargs
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Generate data in memory-efficient batches.
        
        Yields DataFrames of batch_size rows each.
        """
        rows_generated = 0
        
        while rows_generated < total_rows:
            current_batch_size = min(
                self.batch_size,
                total_rows - rows_generated
            )
            
            batch_df = generator_func(
                row_count=current_batch_size,
                **kwargs
            )
            
            rows_generated += len(batch_df)
            yield batch_df
            
    def generate_parallel(
        self,
        generator_func,
        total_rows: int,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate data using parallel workers.
        
        Splits work across CPU cores for faster generation.
        """
        rows_per_worker = total_rows // self.num_workers
        remainder = total_rows % self.num_workers
        
        tasks = []
        for i in range(self.num_workers):
            worker_rows = rows_per_worker + (1 if i < remainder else 0)
            tasks.append((generator_func, worker_rows, kwargs))
        
        results = []
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(func, rows, **kw)
                for func, rows, kw in tasks
            ]
            for future in futures:
                results.append(future.result())
                
        return pd.concat(results, ignore_index=True)


class StreamingExporter:
    """
    Stream generated data directly to file.
    Avoids holding entire dataset in memory.
    """
    
    def __init__(self, output_path: str, format: str = "csv"):
        self.output_path = output_path
        self.format = format
        self.rows_written = 0
        
    def write_batch(
        self,
        df: pd.DataFrame,
        first_batch: bool = False
    ):
        """Write batch to file."""
        if self.format == "csv":
            df.to_csv(
                self.output_path,
                mode='w' if first_batch else 'a',
                header=first_batch,
                index=False
            )
        elif self.format == "jsonl":
            df.to_json(
                self.output_path,
                orient='records',
                lines=True,
                mode='w' if first_batch else 'a'
            )
        elif self.format == "parquet":
            # Parquet requires different handling for appends
            import pyarrow as pa
            import pyarrow.parquet as pq
            
            table = pa.Table.from_pandas(df)
            if first_batch:
                pq.write_table(table, self.output_path)
            else:
                existing = pq.read_table(self.output_path)
                combined = pa.concat_tables([existing, table])
                pq.write_table(combined, self.output_path)
                
        self.rows_written += len(df)
```

### 8.2 Memory Optimization

```python
# Memory-efficient generation patterns

class MemoryOptimizedGenerator:
    """
    Techniques for reducing memory footprint during generation.
    """
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Downcast numeric types to reduce memory.
        Can reduce memory by 50-75%.
        """
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
            
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
            
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
                
        return df
    
    @staticmethod
    def use_numpy_arrays(
        row_count: int,
        generators: Dict[str, callable]
    ) -> pd.DataFrame:
        """
        Generate using numpy arrays instead of row-by-row.
        10-100x faster than iterative generation.
        """
        data = {}
        
        for col_name, gen_func in generators.items():
            # Generate entire column at once
            data[col_name] = gen_func(row_count)
            
        return pd.DataFrame(data)
```

### 8.3 Caching Strategy

```python
# apps/api/app/services/data_factory/cache.py

import redis
import pickle
from typing import Any, Optional
import hashlib

class GeneratorCache:
    """
    Cache expensive computations:
    - SDV trained models
    - Distribution parameters
    - Analyzed schemas
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "datafactory:"
        self.ttl = 3600 * 24  # 24 hours
        
    def _hash_key(self, key: str) -> str:
        """Create consistent hash for cache key."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def get_cached_model(
        self,
        sample_hash: str
    ) -> Optional[Any]:
        """Retrieve cached SDV model."""
        key = f"{self.prefix}model:{sample_hash}"
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    def cache_model(
        self,
        sample_hash: str,
        model: Any
    ):
        """Cache trained SDV model."""
        key = f"{self.prefix}model:{sample_hash}"
        self.redis.setex(
            key,
            self.ttl,
            pickle.dumps(model)
        )
    
    def get_cached_schema(
        self,
        request_hash: str
    ) -> Optional[Dict]:
        """Retrieve cached analyzed schema."""
        key = f"{self.prefix}schema:{request_hash}"
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    def cache_schema(
        self,
        request_hash: str,
        schema: Dict
    ):
        """Cache analyzed schema."""
        key = f"{self.prefix}schema:{request_hash}"
        self.redis.setex(
            key,
            self.ttl,
            pickle.dumps(schema)
        )
```

---

## 9. Integration with Celery Tasks

### 9.1 Task Implementation

```python
# apps/api/app/tasks/generation.py

from celery import shared_task
from app.services.data_factory import DataFactory, GenerationTier
from app.services.export_service import ExportService
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    name="app.tasks.generation.generate_dataset",
    max_retries=3,
    soft_time_limit=600,  # 10 minutes
    hard_time_limit=900   # 15 minutes
)
def generate_dataset(
    self,
    job_id: str,
    sample_data: list,
    row_count: int,
    format: str = "csv",
    constraints: dict = None,
    tier: str = "smart"
):
    """
    Celery task for async dataset generation.
    
    Progress updates:
    - 0%: Starting
    - 10%: Analyzing sample
    - 20%: Generating data
    - 80%: Validating quality
    - 90%: Exporting to file
    - 100%: Complete
    """
    try:
        # Update progress: Starting
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0, 'status': 'Starting generation...'}
        )
        
        # Initialize factory
        factory = DataFactory()
        generation_tier = GenerationTier(tier)
        
        # Analyze sample
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'status': 'Analyzing sample patterns...'}
        )
        
        # Generate data in batches
        self.update_state(
            state='PROGRESS',
            meta={'progress': 20, 'status': f'Generating {row_count} rows...'}
        )
        
        df = factory.generate(
            sample_data=sample_data,
            row_count=row_count,
            constraints=constraints,
            tier=generation_tier
        )
        
        # Validate quality
        self.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'status': 'Validating data quality...'}
        )
        
        quality_report = factory.validate_quality(df)
        
        if quality_report.overall_score < 90:
            logger.warning(
                f"Quality score below threshold: {quality_report.overall_score}"
            )
        
        # Export to file
        self.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'status': f'Exporting to {format}...'}
        )
        
        export_service = ExportService()
        file_path = export_service.export(
            df=df,
            format=format,
            job_id=job_id
        )
        
        # Complete
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 100,
                'status': 'Complete',
                'file_path': file_path,
                'row_count': len(df),
                'quality_score': quality_report.overall_score
            }
        )
        
        return {
            'job_id': job_id,
            'file_path': file_path,
            'row_count': len(df),
            'quality_score': quality_report.overall_score
        }
        
    except Exception as e:
        logger.exception(f"Generation failed for job {job_id}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
```

---

## 10. Dependencies & Requirements

### 10.1 Required Packages

Add to `apps/api/requirements.txt`:

```txt
# Data Generation
faker>=24.0.0              # Fake data generation
mimesis>=12.0.0            # Fast fake data (alternative)
sdv>=1.10.0                # Statistical synthesis
numpy>=1.24.0              # Numerical operations
pandas>=2.0.0              # DataFrame handling
scipy>=1.11.0              # Statistical distributions

# Optional: Advanced ML synthesis (Enterprise tier)
#  >=0.2.0         # GAN/VAE synthesis
# torch>=2.0.0             # PyTorch for ML models

# Validation
python-stdnum>=1.19        # Standard number validation (IBAN, SSN, etc.)

# Export formats
pyarrow>=14.0.0            # Parquet export
openpyxl>=3.1.0            # Excel export
```

### 10.2 Environment Variables

```env
# Data Factory Configuration
DATA_FACTORY_DEFAULT_LOCALE=en_US
DATA_FACTORY_BATCH_SIZE=10000
DATA_FACTORY_MAX_WORKERS=4
DATA_FACTORY_QUALITY_THRESHOLD=95.0
DATA_FACTORY_CACHE_TTL=86400

# SDV Configuration (optional)
SDV_ENABLE_GPU=false
SDV_DEFAULT_SYNTHESIZER=GaussianCopula
```

---

## 11. Summary & Next Steps

### 11.1 Recommended Approach

1. **Phase 1 (Week 1)**: Replace current generators with Faker-based ones
   - Immediate 10x improvement in data quality
   - Add localization support
   - Implement uniqueness enforcement

2. **Phase 2 (Week 2)**: Add pattern analysis
   - Type detection from LLM samples
   - Distribution fitting
   - Constraint extraction

3. **Phase 3 (Week 3)**: Integrate SDV for advanced use cases
   - Multi-table relationships
   - Statistical preservation
   - Enterprise tier feature

4. **Phase 4 (Week 4)**: Quality validation & optimization
   - Format validators
   - Quality scoring
   - Performance tuning to hit 100K rows/min

### 11.2 Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| **Faker as primary** | Fast, reliable, 100+ locales, MIT license |
| **SDV for ML synthesis** | Best statistical quality, good docs |
| **Synthcity optional** | Too complex for MVP, Enterprise-only |
| **Hybrid tiered approach** | Balance speed vs quality per use case |
| **Batch streaming** | Handle large datasets without memory issues |

### 11.3 Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Generation Speed | ~1K/min | 100K/min | Rows per minute |
| Quality Score | N/A | >95% | Quality scorer |
| Unique Name Combinations | 56 | 1M+ | Faker locales |
| Format Compliance | ~70% | 100% | Validator pass rate |
| Supported Data Types | 8 | 25+ | Generator count |

---

**Document Maintained By:** Synthesize.io Engineering Team  
**Last Updated:** January 3, 2026
