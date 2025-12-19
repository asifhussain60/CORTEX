# cortex_header

CORTEX Header Template Generator

Provides standardized branding header for all planning documents,
reports, and generated markdown files.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents


### Functions
- [generate_cortex_header](#generate_cortex_header)
- [generate_sub_plan_header](#generate_sub_plan_header)
- [generate_report_header](#generate_report_header)
- [generate_ado_header](#generate_ado_header)
- [extract_document_title](#extract_document_title)
- [has_cortex_header](#has_cortex_header)
- [inject_cortex_header](#inject_cortex_header)


## Overview

- **Classes:** 0
- **Functions:** 7
- **Dependencies:** datetime, typing


## Functions

### generate_cortex_header

```python
generate_cortex_header(document_title: str, document_type: str, status: str, version: Optional[str], additional_metadata: Optional[Dict[str, str]]) -> str
```

Generate standardized CORTEX header for markdown documents.

Args:
    document_title: Title of the document (H1 level)
    document_type: Type classification (Master Plan, Sub-Plan, Report, etc.)
    status: Document status with emoji
    version: Version number (optional)
    additional_metadata: Extra metadata fields (optional)

Returns:
    Formatted markdown header with CORTEX branding

Example:
    >>> header = generate_cortex_header(
    ...     document_title="CORTEX Evolution v3.9",
    ...     document_type="Tier 4 Complex Plan",
    ...     status="🟡 In Progress",
    ...     version="3.9.0"
    ... )


**Parameters:**

- `document_title` (str): Title of the document (H1 level)
- `document_type` (str): Type classification (Master Plan, Sub-Plan, Report, etc.)
- `status` (str) = `'🟡 In Progress'`: Document status with emoji
- `version` (Optional[str]) = `None`: Version number (optional)
- `additional_metadata` (Optional[Dict[str, str]]) = `None`: Extra metadata fields (optional)


**Returns:** str
  Formatted markdown header with CORTEX branding


---

### generate_sub_plan_header

```python
generate_sub_plan_header(phase_id: str, phase_name: str, master_plan_path: str, status: str, version: Optional[str]) -> str
```

Generate header specifically for sub-plan documents.

Args:
    phase_id: Phase identifier (e.g., "04")
    phase_name: Human-readable phase name
    master_plan_path: Relative path to master plan
    status: Phase status
    version: Version number (optional)

Returns:
    Formatted sub-plan header with breadcrumb navigation


**Parameters:**

- `phase_id` (str): Phase identifier (e.g., "04")
- `phase_name` (str): Human-readable phase name
- `master_plan_path` (str): Relative path to master plan
- `status` (str) = `'⏳ Pending'`: Phase status
- `version` (Optional[str]) = `None`: Version number (optional)


**Returns:** str
  Formatted sub-plan header with breadcrumb navigation


---

### generate_report_header

```python
generate_report_header(report_title: str, report_type: str, project_name: Optional[str]) -> str
```

Generate header for analysis reports and summaries.

Args:
    report_title: Title of the report
    report_type: Type of report (Analysis, Summary, Investigation, etc.)
    project_name: Name of project being analyzed (optional)

Returns:
    Formatted report header


**Parameters:**

- `report_title` (str): Title of the report
- `report_type` (str): Type of report (Analysis, Summary, Investigation, etc.)
- `project_name` (Optional[str]) = `None`: Name of project being analyzed (optional)


**Returns:** str
  Formatted report header


---

### generate_ado_header

```python
generate_ado_header(feature_title: str, feature_type: str, priority: str, area_path: Optional[str]) -> str
```

Generate header for Azure DevOps formatted documents.

Args:
    feature_title: Title of the feature/story
    feature_type: ADO work item type (Feature, User Story, Task, etc.)
    priority: Priority level
    area_path: Area path in ADO (optional)

Returns:
    Formatted ADO document header


**Parameters:**

- `feature_title` (str): Title of the feature/story
- `feature_type` (str) = `'Feature'`: ADO work item type (Feature, User Story, Task, etc.)
- `priority` (str) = `'Medium'`: Priority level
- `area_path` (Optional[str]) = `None`: Area path in ADO (optional)


**Returns:** str
  Formatted ADO document header


---

### extract_document_title

```python
extract_document_title(content: str) -> Optional[str]
```

Extract document title (H1) from markdown content.

Args:
    content: Markdown document content

Returns:
    Document title or None if not found


**Parameters:**

- `content` (str): Markdown document content


**Returns:** Optional[str]
  Document title or None if not found


---

### has_cortex_header

```python
has_cortex_header(content: str) -> bool
```

Check if content already has CORTEX header.

Args:
    content: Document content

Returns:
    True if CORTEX header present


**Parameters:**

- `content` (str): Document content


**Returns:** bool
  True if CORTEX header present


---

### inject_cortex_header

```python
inject_cortex_header(content: str, header_type: str, **kwargs) -> str
```

Inject CORTEX header into existing markdown document.

Args:
    content: Existing document content
    header_type: Type of header to generate (document, sub_plan, report, ado)
    **kwargs: Arguments passed to specific header generator

Returns:
    Document with CORTEX header prepended


**Parameters:**

- `content` (str): Existing document content
- `header_type` (str) = `'document'`: Type of header to generate (document, sub_plan, report, ado)
- `**kwargs`


**Returns:** str
  Document with CORTEX header prepended


---
