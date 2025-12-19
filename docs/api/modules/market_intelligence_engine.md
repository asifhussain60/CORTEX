# market_intelligence_engine

Market Intelligence Engine
Fetches domain knowledge from authoritative sources during planning analysis

Provides informed recommendations based on:
- Industry standards and best practices
- Market trends and upcoming changes
- Regulatory compliance requirements
- Technology alternatives and comparisons

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ResearchValue](#researchvalue)
- [MarketInsight](#marketinsight)
- [ResearchReport](#researchreport)
- [MarketIntelligenceEngine](#marketintelligenceengine)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, enum, hashlib, json, pathlib, re, sys, typing


## Classes

### ResearchValue

```python
class ResearchValue(Enum)
```

Research value classification based on ROI



---

### MarketInsight

```python
class MarketInsight
```

**Decorators:** `dataclass`

Single market intelligence finding


**Attributes:**

- `category`: str
- `title`: str
- `description`: str
- `source_url`: str
- `source_authority`: str
- `relevance_score`: int
- `recommendation`: str
- `implementation_impact`: str



---

### ResearchReport

```python
class ResearchReport
```

**Decorators:** `dataclass`

Comprehensive market intelligence report


**Attributes:**

- `total_score`: int
- `value_tier`: ResearchValue
- `insights`: List[MarketInsight]
- `recommendations`: List[str]
- `guardrails`: List[str]
- `authoritative_sources`: List[str]



---

### MarketIntelligenceEngine

```python
class MarketIntelligenceEngine
```

Intelligent domain research system

Research Value Scoring (0-100):
1. Domain Criticality (0-30): Financial, healthcare, security, compliance
2. Industry Maturity (0-25): Established standards vs emerging tech
3. User Expertise Gap (0-20): Novice vs expert developer
4. Compliance Requirements (0-15): Regulatory mandates
5. Technology Complexity (0-10): Novel vs well-understood

Guardrails:
- Only surface insights with relevance ≥ 70 (HIGH/CRITICAL value)
- Maximum 5 insights per response (avoid overwhelming)
- Collapse into expandable section if > 3 insights
- Skip research for internal tools, basic CRUD, trivial features

Authoritative Source Whitelist:
- Standards: ISO, W3C, IETF, IEEE, NIST, PCI DSS, HIPAA
- Security: OWASP, CVE, NVD, CIS Benchmarks
- Industry: Microsoft Docs, Google Cloud, AWS, MDN Web Docs
- Academic: ACM Digital Library, IEEE Xplore, arXiv


**Methods:**

  #### `should_research`

  ```python
  should_research(self, user_request: str, codebase_context: str) -> ResearchReport
  ```

  Determine if market research adds value for this request

Args:
    user_request: User's feature request
    codebase_context: Existing codebase summary (from AST analysis)
    
Returns:
    ResearchReport with value assessment

  **Parameters:**

  - `self`
  - `user_request` (str): User's feature request
  - `codebase_context` (str): Existing codebase summary (from AST analysis)


  **Returns:** ResearchReport
    ResearchReport with value assessment



---
