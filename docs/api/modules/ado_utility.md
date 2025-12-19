# ado_utility

ADO Work Item Utility

Fast, lightweight Azure DevOps work item management.
Replaces heavy orchestrator (1,642 lines) with focused utility (~900 lines).

Core Operations:
- Create, load, update work items
- Generate completion summaries
- Validate DoR (Definition of Ready)
- Validate DoD (Definition of Done)
- List work items by status

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [WorkItemType](#workitemtype)
- [WorkItemStatus](#workitemstatus)
- [WorkItemMetadata](#workitemmetadata)
- [WorkItemSummary](#workitemsummary)
- [ValidationResult](#validationresult)
- [WorkItemResult](#workitemresult)

### Functions
- [create_work_item](#create_work_item)
- [load_work_item](#load_work_item)
- [update_work_item](#update_work_item)
- [generate_summary](#generate_summary)
- [validate_dor](#validate_dor)
- [validate_dod](#validate_dod)
- [list_work_items](#list_work_items)


## Overview

- **Classes:** 6
- **Functions:** 14
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, re, src, typing, yaml


## Classes

### WorkItemType

```python
class WorkItemType(Enum)
```

Azure DevOps work item types.



---

### WorkItemStatus

```python
class WorkItemStatus(Enum)
```

Work item status states.



---

### WorkItemMetadata

```python
class WorkItemMetadata
```

**Decorators:** `dataclass`

Core work item metadata (simplified).


**Attributes:**

- `work_item_type`: WorkItemType
- `title`: str
- `description`: str
- `work_item_id`: Optional[str]
- `status`: WorkItemStatus
- `assigned_to`: Optional[str]
- `iteration`: Optional[str]
- `area_path`: Optional[str]
- `priority`: int
- `tags`: List[str]
- `acceptance_criteria`: List[str]
- `related_work_items`: List[str]
- `created_date`: str
- `updated_date`: str



---

### WorkItemSummary

```python
class WorkItemSummary
```

**Decorators:** `dataclass`

Summary of completed work.


**Attributes:**

- `work_item_id`: str
- `work_item_type`: WorkItemType
- `title`: str
- `files_created`: List[str]
- `files_modified`: List[str]
- `tests_created`: List[str]
- `documentation_created`: List[str]
- `code_changes_count`: int
- `test_coverage`: float
- `duration_hours`: float
- `implementation_notes`: str
- `technical_decisions`: List[str]
- `dependencies`: List[str]
- `acceptance_criteria_met`: List[str]
- `test_results`: str
- `timestamp`: str



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

DoR/DoD validation result.


**Attributes:**

- `passed`: bool
- `score`: float
- `total_points`: int
- `earned_points`: int
- `category_scores`: Dict[str, float]
- `passed_checks`: List[str]
- `failed_checks`: List[str]
- `warnings`: List[str]
- `recommendations`: List[str]
- `validation_type`: str
- `timestamp`: str



---

### WorkItemResult

```python
class WorkItemResult
```

**Decorators:** `dataclass`

Result of work item operation.


**Attributes:**

- `success`: bool
- `message`: str
- `work_item_id`: Optional[str]
- `metadata`: Optional[WorkItemMetadata]
- `summary`: Optional[WorkItemSummary]
- `validation`: Optional[ValidationResult]
- `file_path`: Optional[Path]
- `errors`: List[str]



---

## Functions

### create_work_item

```python
create_work_item(work_item_type: WorkItemType, title: str, description: str, **kwargs) -> WorkItemResult
```

Create new ADO work item.

Args:
    work_item_type: Type of work item
    title: Work item title
    description: Work item description
    **kwargs: Additional metadata fields
    
Returns:
    WorkItemResult with creation outcome


**Parameters:**

- `work_item_type` (WorkItemType): Type of work item
- `title` (str): Work item title
- `description` (str): Work item description
- `**kwargs`


**Returns:** WorkItemResult
  WorkItemResult with creation outcome


---

### load_work_item

```python
load_work_item(work_item_id: str) -> WorkItemResult
```

Load existing work item.

Args:
    work_item_id: Work item identifier
    
Returns:
    WorkItemResult with loaded metadata


**Parameters:**

- `work_item_id` (str): Work item identifier


**Returns:** WorkItemResult
  WorkItemResult with loaded metadata


---

### update_work_item

```python
update_work_item(work_item_id: str, **updates) -> WorkItemResult
```

Update existing work item.

Args:
    work_item_id: Work item identifier
    **updates: Fields to update
    
Returns:
    WorkItemResult with update outcome


**Parameters:**

- `work_item_id` (str): Work item identifier
- `**updates`


**Returns:** WorkItemResult
  WorkItemResult with update outcome


---

### generate_summary

```python
generate_summary(work_item_id: str, **summary_data) -> WorkItemResult
```

Generate completion summary for work item.

Args:
    work_item_id: Work item identifier
    **summary_data: Summary fields
    
Returns:
    WorkItemResult with summary


**Parameters:**

- `work_item_id` (str): Work item identifier
- `**summary_data`


**Returns:** WorkItemResult
  WorkItemResult with summary


---

### validate_dor

```python
validate_dor(metadata: WorkItemMetadata, ambiguity_score: int) -> ValidationResult
```

Validate Definition of Ready.

Args:
    metadata: Work item metadata
    ambiguity_score: Number of ambiguities detected
    
Returns:
    ValidationResult with DoR assessment


**Parameters:**

- `metadata` (WorkItemMetadata): Work item metadata
- `ambiguity_score` (int) = `0`: Number of ambiguities detected


**Returns:** ValidationResult
  ValidationResult with DoR assessment


---

### validate_dod

```python
validate_dod(summary: WorkItemSummary) -> ValidationResult
```

Validate Definition of Done.

Args:
    summary: Work item summary
    
Returns:
    ValidationResult with DoD assessment


**Parameters:**

- `summary` (WorkItemSummary): Work item summary


**Returns:** ValidationResult
  ValidationResult with DoD assessment


---

### list_work_items

```python
list_work_items(status: Optional[WorkItemStatus]) -> WorkItemResult
```

List work items by status.

Args:
    status: Filter by status (None = all)
    
Returns:
    WorkItemResult with list of work items


**Parameters:**

- `status` (Optional[WorkItemStatus]) = `None`: Filter by status (None = all)


**Returns:** WorkItemResult
  WorkItemResult with list of work items


---
