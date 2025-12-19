# rca_utility

RCA (Root Cause Analysis) Utility

Fast, lightweight root cause analysis management.
Replaces heavy orchestrator (1,174 lines) with focused utility (~650 lines).

Core Operations:
- Create RCA analysis
- Load existing RCA
- Update RCA fields
- Add Why question/answer (5 Whys methodology)
- Generate report
- List RCAs by status

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [RCAStatus](#rcastatus)
- [WhyDepth](#whydepth)
- [IncidentDetails](#incidentdetails)
- [WhyQuestion](#whyquestion)
- [RootCause](#rootcause)
- [CorrectiveAction](#correctiveaction)
- [RCAAnalysis](#rcaanalysis)
- [RCAResult](#rcaresult)

### Functions
- [create_rca](#create_rca)
- [load_rca](#load_rca)
- [update_rca](#update_rca)
- [add_why_question](#add_why_question)
- [generate_report](#generate_report)
- [list_rcas](#list_rcas)


## Overview

- **Classes:** 8
- **Functions:** 11
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, re, src, typing, yaml


## Classes

### RCAStatus

```python
class RCAStatus(Enum)
```

RCA analysis status states.



---

### WhyDepth

```python
class WhyDepth(Enum)
```

Depth levels for 5 Whys analysis.



---

### IncidentDetails

```python
class IncidentDetails
```

**Decorators:** `dataclass`

Structured incident information.


**Attributes:**

- `incident_id`: str
- `title`: str
- `description`: str
- `occurred_at`: str
- `detected_at`: str
- `severity`: str
- `impact`: str
- `affected_systems`: List[str]
- `resolved_at`: Optional[str]



---

### WhyQuestion

```python
class WhyQuestion
```

**Decorators:** `dataclass`

A single Why question in the 5 Whys chain.


**Attributes:**

- `depth`: int
- `question`: str
- `answer`: str
- `confidence`: float
- `evidence`: List[str]



---

### RootCause

```python
class RootCause
```

**Decorators:** `dataclass`

Identified root cause with supporting evidence.


**Attributes:**

- `description`: str
- `confidence`: float
- `evidence`: List[str]
- `category`: str
- `why_chain`: List[WhyQuestion]



---

### CorrectiveAction

```python
class CorrectiveAction
```

**Decorators:** `dataclass`

Action to address the root cause.


**Attributes:**

- `action_id`: str
- `description`: str
- `action_type`: str
- `owner`: str
- `status`: str
- `priority`: str



---

### RCAAnalysis

```python
class RCAAnalysis
```

**Decorators:** `dataclass`

Complete RCA analysis structure.


**Attributes:**

- `analysis_id`: str
- `incident`: IncidentDetails
- `status`: RCAStatus
- `why_questions`: List[WhyQuestion]
- `current_depth`: int
- `root_causes`: List[RootCause]
- `corrective_actions`: List[CorrectiveAction]
- `analyst`: str
- `created_at`: str
- `updated_at`: str
- `completed_at`: Optional[str]



---

### RCAResult

```python
class RCAResult
```

**Decorators:** `dataclass`

Result of RCA operation.


**Attributes:**

- `success`: bool
- `message`: str
- `analysis_id`: Optional[str]
- `analysis`: Optional[RCAAnalysis]
- `report_path`: Optional[Path]
- `errors`: List[str]



---

## Functions

### create_rca

```python
create_rca(incident_id: str, title: str, description: str, occurred_at: str, detected_at: str, **kwargs) -> RCAResult
```

Create new RCA analysis.

Args:
    incident_id: Unique incident identifier
    title: Incident title
    description: Incident description
    occurred_at: When incident occurred (ISO format)
    detected_at: When incident was detected (ISO format)
    **kwargs: Additional incident fields
    
Returns:
    RCAResult with creation outcome


**Parameters:**

- `incident_id` (str): Unique incident identifier
- `title` (str): Incident title
- `description` (str): Incident description
- `occurred_at` (str): When incident occurred (ISO format)
- `detected_at` (str): When incident was detected (ISO format)
- `**kwargs`


**Returns:** RCAResult
  RCAResult with creation outcome


---

### load_rca

```python
load_rca(analysis_id: str) -> RCAResult
```

Load existing RCA analysis.

Args:
    analysis_id: Analysis identifier
    
Returns:
    RCAResult with loaded analysis


**Parameters:**

- `analysis_id` (str): Analysis identifier


**Returns:** RCAResult
  RCAResult with loaded analysis


---

### update_rca

```python
update_rca(analysis_id: str, **updates) -> RCAResult
```

Update RCA analysis fields.

Args:
    analysis_id: Analysis identifier
    **updates: Fields to update
    
Returns:
    RCAResult with update outcome


**Parameters:**

- `analysis_id` (str): Analysis identifier
- `**updates`


**Returns:** RCAResult
  RCAResult with update outcome


---

### add_why_question

```python
add_why_question(analysis_id: str, question: str, answer: Optional[str], evidence: Optional[List[str]]) -> RCAResult
```

Add Why question to 5 Whys chain.

Args:
    analysis_id: Analysis identifier
    question: Why question
    answer: Answer (optional)
    evidence: Supporting evidence (optional)
    
Returns:
    RCAResult with update outcome


**Parameters:**

- `analysis_id` (str): Analysis identifier
- `question` (str): Why question
- `answer` (Optional[str]) = `None`: Answer (optional)
- `evidence` (Optional[List[str]]) = `None`: Supporting evidence (optional)


**Returns:** RCAResult
  RCAResult with update outcome


---

### generate_report

```python
generate_report(analysis_id: str) -> RCAResult
```

Generate RCA report.

Args:
    analysis_id: Analysis identifier
    
Returns:
    RCAResult with report path


**Parameters:**

- `analysis_id` (str): Analysis identifier


**Returns:** RCAResult
  RCAResult with report path


---

### list_rcas

```python
list_rcas(status: Optional[RCAStatus]) -> RCAResult
```

List RCA analyses by status.

Args:
    status: Filter by status (None = all)
    
Returns:
    RCAResult with list of analyses


**Parameters:**

- `status` (Optional[RCAStatus]) = `None`: Filter by status (None = all)


**Returns:** RCAResult
  RCAResult with list of analyses


---
