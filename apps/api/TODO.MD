# 🏭 Data Factory - Implementation TODO

**Last Updated:** January 3, 2026  
**Status:** In Development  
**Branch:** SetuBranch  

---

## 🎯 Overview

The Data Factory is the **heart of Synthesize.io** - responsible for generating high-quality synthetic data at scale. We're building a **god-level, production-grade** system that can generate **ANY kind of data in the world**.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FACTORY ORCHESTRATOR                        │
│                    (Coordinates all generation tiers)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  TIER 1: FAST     │   │  TIER 2: SMART    │   │  TIER 3: ML/AI    │
│  (Faker-based)    │   │  (Pattern Match)  │   │  (SDV/Synthcity)  │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ FREE TIER         │   │ PRO TIER          │   │ ENTERPRISE TIER   │
│ 500K rows/min     │   │ 100K rows/min     │   │ 10K rows/min      │
│ Basic types       │   │ Distributions     │   │ Privacy-preserving│
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

### Pricing Model

| Feature | Free | Pro ($29/mo) | Enterprise ($199/mo) |
|---------|------|--------------|----------------------|
| Faker Generators | ✅ | ✅ | ✅ |
| SDV Synthesis | ❌ | ✅ | ✅ |
| Synthcity (Privacy) | ❌ | ❌ | ✅ |
| HIPAA Compliance | ❌ | ❌ | ✅ |
| Rows/month | 100K | 1M | Unlimited |

---

## ✅ Completed

### Core Infrastructure
- [x] `schema.py` - DataType enum (50+ types), ColumnSpec, DataSchema, QualityReport
- [x] `generators/base.py` - BaseGenerator abstract class with Faker integration
- [x] `generators/__init__.py` - Package exports
- [x] `requirements.txt` - All dependencies including SDV + Synthcity

### Generators (Tier 1: Fast)
- [x] `generators/personal.py` - Names, emails, phones, SSN, usernames, passwords
- [x] `generators/financial.py` - Credit cards (Luhn-valid), amounts, IBAN, SWIFT, transactions

### Synthesizers (Tier 3: ML)
- [x] `synthesizers/sdv_synthesizer.py` - **PRO TIER**
  - GaussianCopula, CTGAN, TVAE, CopulaGAN
  - Multi-table support
  - Quality evaluation
  - Model caching
- [x] `synthesizers/synthcity_synthesizer.py` - **ENTERPRISE TIER**
  - 15+ models (CTGAN, DPGAN, PATEGAN, PrivBayes, etc.)
  - Differential privacy (ε-DP)
  - k-anonymity, l-diversity
  - HIPAA compliance helpers

---

## 🔄 In Progress

### Generators (Tier 1: Fast)
- [ ] `generators/temporal.py` - Dates, timestamps, durations, business hours
- [ ] `generators/geographic.py` - Addresses, coordinates, cities, countries
- [ ] `generators/identifier.py` - UUIDs, order IDs, SKUs, slugs
- [ ] `generators/categorical.py` - Enums, statuses, weighted distributions
- [ ] `generators/numerical.py` - Integers, floats with distributions
- [ ] `generators/text.py` - Lorem ipsum, sentences, paragraphs, structured text
- [ ] `generators/business.py` - Companies, job titles, departments, industries

---

## 📋 TODO

### Phase 1: Complete Base Generators (Priority: P0)

#### 1.1 Temporal Data Generator
```python
# generators/temporal.py
- generate_date(start, end, distribution)
- generate_datetime(business_hours_only)
- generate_timestamp(format)
- generate_duration(min, max, unit)
- generate_time_series(pattern, seasonality)
- generate_age(min, max, distribution)
```

#### 1.2 Geographic Data Generator
```python
# generators/geographic.py
- generate_address(locale, include_country)
- generate_street_address()
- generate_city()
- generate_state()
- generate_country()
- generate_country_code(format)  # alpha-2, alpha-3
- generate_coordinates(bounds)
- generate_timezone()
- generate_ip_address(version, private)
- generate_mac_address()
```

#### 1.3 Identifier Generator
```python
# generators/identifier.py
- generate_uuid(version)
- generate_order_id(prefix, length)
- generate_sku(category_code)
- generate_sequential_id(prefix, start)
- generate_slug(text)
- generate_barcode(format)  # EAN-13, UPC-A
- generate_isbn()
- generate_serial_number()
```

#### 1.4 Categorical Generator
```python
# generators/categorical.py
- generate_from_list(values, weights)
- generate_status(statuses, weights)
- generate_enum(enum_values, distribution)
- generate_boolean(true_probability)
- generate_gender()
- generate_blood_type()
- generate_rating(min, max, distribution)
```

#### 1.5 Numerical Generator
```python
# generators/numerical.py
- generate_integer(min, max, distribution)
- generate_float(min, max, distribution, precision)
- generate_percentage()
- generate_normal(mean, std)
- generate_exponential(scale)
- generate_poisson(lambda)
- generate_binomial(n, p)
- generate_from_histogram(bins, counts)
```

#### 1.6 Text Generator
```python
# generators/text.py
- generate_word()
- generate_sentence(word_count)
- generate_paragraph(sentence_count)
- generate_text(length)
- generate_lorem_ipsum(paragraphs)
- generate_json_object(schema)
- generate_xml(schema)
- generate_markdown()
- generate_code_snippet(language)
```

#### 1.7 Business Generator
```python
# generators/business.py
- generate_company_name()
- generate_company_suffix()  # Inc, LLC, Ltd
- generate_industry()
- generate_job_title()
- generate_department()
- generate_catch_phrase()
- generate_bs()  # Business buzzwords
- generate_ein()  # Employer ID Number
- generate_duns()  # D-U-N-S Number
```

### Phase 2: Pattern Analyzers (Priority: P0)

#### 2.1 Type Detector
```python
# analyzers/type_detector.py
- detect_column_type(values)  # Infer DataType from sample
- detect_format(values)  # Detect email, phone, SSN patterns
- detect_locale(values)  # Detect language/locale
- confidence_score()
```

#### 2.2 Pattern Analyzer
```python
# analyzers/pattern_analyzer.py
- analyze_sample(sample_df)  # Full analysis
- extract_regex_pattern(values)
- detect_prefix_suffix(values)
- detect_format_mask(values)  # e.g., "XXX-XX-XXXX"
```

#### 2.3 Distribution Analyzer
```python
# analyzers/distribution_analyzer.py
- fit_distribution(values)  # Find best-fit distribution
- detect_outliers(values)
- calculate_statistics(values)
- compare_distributions(real, synthetic)
```

### Phase 3: Validators (Priority: P1)

#### 3.1 Format Validator
```python
# validators/format_validator.py
- validate_email(value)
- validate_phone(value, locale)
- validate_ssn(value)
- validate_credit_card(value)  # Luhn
- validate_iban(value)
- validate_uuid(value)
- validate_url(value)
- validate_ip(value)
```

#### 3.2 Uniqueness Validator
```python
# validators/uniqueness_validator.py
- check_unique(column, value)
- get_duplicate_count(column)
- enforce_uniqueness(df, columns)
```

#### 3.3 Integrity Validator
```python
# validators/integrity_validator.py
- register_primary_key(table, column, values)
- validate_foreign_key(value, references)
- validate_referential_integrity(tables)
```

#### 3.4 Quality Scorer
```python
# validators/quality_scorer.py
- score_dataset(df, schema)
- score_format_compliance()
- score_uniqueness()
- score_completeness()
- score_distribution_match()
- score_referential_integrity()
- generate_quality_report()
```

### Phase 4: Orchestrator (Priority: P0)

#### 4.1 Data Factory Main Class
```python
# orchestrator.py
class DataFactory:
    - __init__(locale, tier, config)
    - analyze_sample(sample_data)  # From LLM
    - generate(sample_data, row_count, constraints)
    - generate_fast(schema)  # Tier 1
    - generate_smart(sample_data, schema)  # Tier 2
    - generate_ml_based(sample_data, schema)  # Tier 3
    - validate_quality(df)
    - export(df, format)
```

### Phase 5: Batch Processing (Priority: P1)

#### 5.1 Batch Generator
```python
# batch_generator.py
- generate_in_batches(generator_func, total_rows)
- generate_parallel(generator_func, total_rows)
- memory_efficient_generation()
```

#### 5.2 Streaming Exporter
```python
# exporters/streaming_exporter.py
- write_batch(df, first_batch)
- export_csv(df, path)
- export_json(df, path)
- export_parquet(df, path)
- export_excel(df, path)
```

### Phase 6: Integration (Priority: P1)

#### 6.1 Celery Tasks
```python
# tasks/generation_tasks.py
@celery_task
def generate_dataset_task(job_id, sample_data, row_count, ...)
    - Progress tracking (0-100%)
    - Error handling with retries
    - Quality validation
    - Export to file
```

#### 6.2 API Endpoints
```python
# api/routes/data_factory.py
POST /api/v1/generate
    - Accepts sample data
    - Returns job_id
    
GET /api/v1/jobs/{job_id}/status
    - Returns progress, status

GET /api/v1/jobs/{job_id}/download
    - Returns generated file
```

### Phase 7: Testing (Priority: P1)

- [ ] `tests/test_generators.py` - Unit tests for all generators
- [ ] `tests/test_synthesizers.py` - Unit tests for SDV/Synthcity
- [ ] `tests/test_validators.py` - Validation tests
- [ ] `tests/test_orchestrator.py` - Integration tests
- [ ] `tests/test_performance.py` - Performance benchmarks

### Phase 8: Advanced Features (Priority: P2)

- [ ] Multi-table relational generation
- [ ] Time-series generation (SDV TimeSeriesSynthesizer)
- [ ] Custom provider support
- [ ] LLM-assisted schema inference
- [ ] Real-time streaming generation
- [ ] Data augmentation pipelines

---

## 📊 Performance Targets

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Generation Speed (Tier 1) | - | 500K rows/min | 🟡 Pending |
| Generation Speed (Tier 2) | - | 100K rows/min | 🟡 Pending |
| Generation Speed (Tier 3) | - | 10K rows/min | 🟡 Pending |
| Quality Score | - | >95% | 🟡 Pending |
| Format Compliance | - | 100% | 🟡 Pending |
| Uniqueness Enforcement | - | 100% | 🟡 Pending |
| Memory Usage (1M rows) | - | <2GB | 🟡 Pending |

---

## 📁 File Structure

```
apps/api/app/services/data_factory/
├── __init__.py                 ✅
├── schema.py                   ✅
├── orchestrator.py             ⏳
├── generators/
│   ├── __init__.py             ✅
│   ├── base.py                 ✅
│   ├── personal.py             ✅
│   ├── financial.py            ✅
│   ├── temporal.py             ⏳
│   ├── geographic.py           ⏳
│   ├── identifier.py           ⏳
│   ├── categorical.py          ⏳
│   ├── numerical.py            ⏳
│   ├── text.py                 ⏳
│   └── business.py             ⏳
├── synthesizers/
│   ├── __init__.py             ✅
│   ├── sdv_synthesizer.py      ✅
│   └── synthcity_synthesizer.py ✅
├── analyzers/
│   ├── __init__.py             ⏳
│   ├── type_detector.py        ⏳
│   ├── pattern_analyzer.py     ⏳
│   └── distribution_analyzer.py ⏳
├── validators/
│   ├── __init__.py             ⏳
│   ├── format_validator.py     ⏳
│   ├── uniqueness_validator.py ⏳
│   ├── integrity_validator.py  ⏳
│   └── quality_scorer.py       ⏳
├── exporters/
│   ├── __init__.py             ⏳
│   ├── batch_exporter.py       ⏳
│   └── streaming_exporter.py   ⏳
└── cache/
    └── generator_cache.py      ⏳
```

Legend: ✅ Complete | ⏳ Pending | 🚧 In Progress

---

## 🧠 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Faker as Tier 1** | Fast (500K/min), 100+ locales, MIT license, battle-tested |
| **SDV as Tier 2 (Pro)** | Best statistical fidelity, multi-table support, good docs |
| **Synthcity as Tier 3 (Enterprise)** | Privacy-preserving, HIPAA-compliant, 15+ models |
| **Separate synthesizers** | Different pricing tiers, different use cases |
| **Batch streaming** | Handle large datasets without memory issues |
| **Redis caching** | Cache trained ML models, avoid retraining |

---

## 📚 Reference Documentation

- [DataFactory.md](/docs/DataFactory.md) - Full architecture specification
- [SDV Documentation](https://docs.sdv.dev/)
- [Synthcity Documentation](https://synthcity.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)

---

**Maintained by:** Setu & Team  
**Questions?** Check DataFactory.md or ask in #dev-backend
