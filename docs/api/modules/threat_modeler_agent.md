# threat_modeler_agent

Threat Modeler Agent

Enhanced security threat analysis agent using STRIDE framework with:
- Feature-specific threat templates
- OWASP Top 10 mapping
- Auto-mitigation strategies with code examples
- Risk rating with context awareness

Author: CORTEX Development Team
Version: 3.0 (Phase 6.1 - cortex_agents integration)


## Table of Contents

### Classes
- [RiskRating](#riskrating)
- [OWASPCategory](#owaspcategory)
- [MitigationStrategy](#mitigationstrategy)
- [EnhancedThreat](#enhancedthreat)
- [ThreatReport](#threatreport)
- [ThreatModelerAgent](#threatmodeleragent)

### Functions
- [create_agent](#create_agent)


## Overview

- **Classes:** 6
- **Functions:** 1
- **Dependencies:** asyncio, dataclasses, datetime, enum, logging, src, typing


## Classes

### RiskRating

```python
class RiskRating(Enum)
```

Enhanced risk ratings



---

### OWASPCategory

```python
class OWASPCategory(Enum)
```

OWASP Top 10 2021 Categories



---

### MitigationStrategy

```python
class MitigationStrategy
```

**Decorators:** `dataclass`

Structured mitigation strategy with implementation details


**Attributes:**

- `name`: str
- `description`: str
- `implementation_steps`: List[str]
- `code_example`: str
- `language`: str
- `effort_hours`: float
- `effectiveness_percent`: int
- `tools`: List[str]
- `testing_guidance`: str
- `references`: List[str]



---

### EnhancedThreat

```python
class EnhancedThreat
```

**Decorators:** `dataclass`

Enhanced threat with OWASP mapping and detailed mitigations


**Attributes:**

- `category`: ThreatCategory
- `name`: str
- `description`: str
- `attack_scenario`: str
- `likelihood`: str
- `impact`: str
- `risk_rating`: RiskRating
- `owasp_categories`: List[OWASPCategory]
- `mitigation_strategies`: List[MitigationStrategy]
- `keywords_matched`: List[str]


**Methods:**

  #### `risk_score`

  *Decorators:* `property`

  ```python
  risk_score(self) -> int
  ```

  Calculate numeric risk score (1-10)

  **Parameters:**

  - `self`


  **Returns:** int



---

### ThreatReport

```python
class ThreatReport
```

**Decorators:** `dataclass`

Comprehensive threat analysis report


**Attributes:**

- `feature_name`: str
- `feature_type`: str
- `threats`: List[EnhancedThreat]
- `timestamp`: datetime
- `risk_level`: RiskRating
- `stride_summary`: Dict[str, int]
- `owasp_coverage`: Dict[str, int]
- `recommendations`: List[str]


**Methods:**

  #### `critical_threats`

  *Decorators:* `property`

  ```python
  critical_threats(self) -> List[EnhancedThreat]
  ```

  Get critical threats only

  **Parameters:**

  - `self`


  **Returns:** List[EnhancedThreat]


  #### `high_threats`

  *Decorators:* `property`

  ```python
  high_threats(self) -> List[EnhancedThreat]
  ```

  Get high risk threats

  **Parameters:**

  - `self`


  **Returns:** List[EnhancedThreat]



---

### ThreatModelerAgent

```python
class ThreatModelerAgent(BaseAgent)
```

Enhanced threat modeling agent using STRIDE framework.

Implements cortex_agents BaseAgent interface for standardized request/response flow.

Features:
- Feature-specific threat templates (auth, api, data, upload, payment)
- OWASP Top 10 2021 mapping
- Structured mitigation strategies with code examples
- Context-aware risk rating
- Semantic threat detection (100+ keywords)


**Methods:**

  #### `can_handle`

  ```python
  can_handle(self, request: AgentRequest) -> bool
  ```

  Check if this agent can handle threat modeling requests.

Args:
    request: AgentRequest with intent and context

Returns:
    True if intent relates to threat modeling

  **Parameters:**

  - `self`
  - `request` (AgentRequest): AgentRequest with intent and context


  **Returns:** bool
    True if intent relates to threat modeling


  #### `execute`

  ```python
  execute(self, request: AgentRequest) -> AgentResponse
  ```

  Execute threat analysis using STRIDE framework.

Args:
    request: AgentRequest containing:
        - user_message: Feature description
        - context: Optional dict with:
            - feature_description: Detailed requirements
            - feature_type: auth/api/data_storage/file_upload/payment/general
            - plan_data: Optional plan metadata

Returns:
    AgentResponse with:
        - success: True if analysis completed
        - result: Dict with threats, mitigations, OWASP mapping, risk summary
        - message: Summary message

  **Parameters:**

  - `self`
  - `request` (AgentRequest): AgentRequest containing:


  **Returns:** AgentResponse
    AgentResponse with: - success: True if analysis completed - result: Dict with threats, mitigations, OWASP mapping, risk summary - message: Summary message


  #### `process`

  ```python
  process(self, feature_requirements: str, feature_type: str, context: Optional[Dict[str, Any]]) -> ThreatReport
  ```

  Main processing method for threat analysis.

Args:
    feature_requirements: Description of feature to analyze
    feature_type: Type of feature (auth, api, data_storage, file_upload, payment, general)
    context: Optional context (project patterns, previous threats, etc.)

Returns:
    ThreatReport with identified threats and mitigations

  **Parameters:**

  - `self`
  - `feature_requirements` (str): Description of feature to analyze
  - `feature_type` (str) = `'general'`: Type of feature (auth, api, data_storage, file_upload, payment, general)
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context (project patterns, previous threats, etc.)


  **Returns:** ThreatReport
    ThreatReport with identified threats and mitigations



---

## Functions

### create_agent

```python
create_agent() -> ThreatModelerAgent
```

Create threat modeler agent instance


**Returns:** ThreatModelerAgent


---
