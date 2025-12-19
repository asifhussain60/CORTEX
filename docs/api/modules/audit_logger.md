# audit_logger

CORTEX Planning System 3.0 - Audit Trail Logger

Provides comprehensive audit logging for all planning orchestrator operations.
Stores events in JSONL format for easy querying and analysis.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX


## Table of Contents

### Classes
- [AuditEvent](#auditevent)
- [AuditLogger](#auditlogger)

### Functions
- [get_audit_logger](#get_audit_logger)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** csv, dataclasses, datetime, gzip, json, pathlib, threading, typing


## Classes

### AuditEvent

```python
class AuditEvent
```

**Decorators:** `dataclass`

Structured audit event.


**Attributes:**

- `timestamp`: str
- `event_type`: str
- `session_id`: str
- `plan_id`: str
- `user_request`: Optional[str]
- `orchestrator`: str
- `phase`: str
- `metadata`: Dict[str, Any]
- `outcome`: str
- `duration_ms`: Optional[int]
- `error_message`: Optional[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> dict
  ```

  Convert to dictionary for JSON serialization.

  **Parameters:**

  - `self`


  **Returns:** dict



---

### AuditLogger

```python
class AuditLogger
```

Singleton audit logger for Planning System 3.0.

Captures all significant planning operations and stores them in JSONL format
for complete visibility, troubleshooting, and compliance.

Storage:
    - Active log: cortex-brain/audit-trail.jsonl
    - Archives: cortex-brain/audit-archive/{YYYY-MM}-audit.jsonl.gz

Features:
    - Append-only writes (no locking issues)
    - Structured event schema
    - Query and filtering
    - Monthly archival
    - CSV export
    - Statistics generation


**Methods:**

  #### `log_event`

  ```python
  log_event(self, event_type: str, session_id: str, plan_id: str, orchestrator: str, user_request: Optional[str], phase: str, metadata: Optional[Dict[str, Any]], outcome: str, duration_ms: Optional[int], error_message: Optional[str]) -> None
  ```

  Log an audit event.

Args:
    event_type: Type of event (e.g., "temp_plan_created", "plan_refined")
    session_id: Planning session identifier
    plan_id: Plan identifier
    orchestrator: Name of orchestrator generating the event
    user_request: User's original request (optional)
    phase: Current phase (e.g., "refinement", "approval", "execution")
    metadata: Additional structured data
    outcome: "success", "failure", "warning"
    duration_ms: Operation duration in milliseconds (optional)
    error_message: Error details if outcome is "failure" (optional)

  **Parameters:**

  - `self`
  - `event_type` (str): Type of event (e.g., "temp_plan_created", "plan_refined")
  - `session_id` (str): Planning session identifier
  - `plan_id` (str): Plan identifier
  - `orchestrator` (str): Name of orchestrator generating the event
  - `user_request` (Optional[str]) = `None`: User's original request (optional)
  - `phase` (str) = `'unknown'`: Current phase (e.g., "refinement", "approval", "execution")
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional structured data
  - `outcome` (str) = `'success'`: "success", "failure", "warning"
  - `duration_ms` (Optional[int]) = `None`: Operation duration in milliseconds (optional)
  - `error_message` (Optional[str]) = `None`: Error details if outcome is "failure" (optional)


  **Returns:** None


  #### `query_events`

  ```python
  query_events(self, plan_id: Optional[str], session_id: Optional[str], event_type: Optional[str], orchestrator: Optional[str], since: Optional[datetime], until: Optional[datetime], outcome: Optional[str], limit: Optional[int]) -> List[Dict[str, Any]]
  ```

  Query audit events with filters.

Args:
    plan_id: Filter by plan ID
    session_id: Filter by session ID
    event_type: Filter by event type
    orchestrator: Filter by orchestrator name
    since: Events after this timestamp
    until: Events before this timestamp
    outcome: Filter by outcome ("success", "failure", "warning")
    limit: Maximum number of events to return

Returns:
    List of matching events (most recent first)

  **Parameters:**

  - `self`
  - `plan_id` (Optional[str]) = `None`: Filter by plan ID
  - `session_id` (Optional[str]) = `None`: Filter by session ID
  - `event_type` (Optional[str]) = `None`: Filter by event type
  - `orchestrator` (Optional[str]) = `None`: Filter by orchestrator name
  - `since` (Optional[datetime]) = `None`: Events after this timestamp
  - `until` (Optional[datetime]) = `None`: Events before this timestamp
  - `outcome` (Optional[str]) = `None`: Filter by outcome ("success", "failure", "warning")
  - `limit` (Optional[int]) = `None`: Maximum number of events to return


  **Returns:** List[Dict[str, Any]]
    List of matching events (most recent first)


  #### `get_plan_history`

  ```python
  get_plan_history(self, plan_id: str) -> List[Dict[str, Any]]
  ```

  Get complete audit trail for a specific plan.

Args:
    plan_id: Plan identifier

Returns:
    Chronological list of events for this plan

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier


  **Returns:** List[Dict[str, Any]]
    Chronological list of events for this plan


  #### `get_session_timeline`

  ```python
  get_session_timeline(self, session_id: str) -> List[Dict[str, Any]]
  ```

  Get chronological session events.

Args:
    session_id: Session identifier

Returns:
    Chronological list of events for this session

  **Parameters:**

  - `self`
  - `session_id` (str): Session identifier


  **Returns:** List[Dict[str, Any]]
    Chronological list of events for this session


  #### `export_to_csv`

  ```python
  export_to_csv(self, events: List[Dict[str, Any]], output_path: str) -> None
  ```

  Export events to CSV format.

Args:
    events: List of audit events
    output_path: Path to output CSV file

  **Parameters:**

  - `self`
  - `events` (List[Dict[str, Any]]): List of audit events
  - `output_path` (str): Path to output CSV file


  **Returns:** None


  #### `generate_stats`

  ```python
  generate_stats(self, since: Optional[datetime]) -> Dict[str, Any]
  ```

  Generate audit statistics.

Args:
    since: Calculate stats from this timestamp (default: last 30 days)

Returns:
    Dictionary with statistics

  **Parameters:**

  - `self`
  - `since` (Optional[datetime]) = `None`: Calculate stats from this timestamp (default: last 30 days)


  **Returns:** Dict[str, Any]
    Dictionary with statistics


  #### `archive_old_logs`

  ```python
  archive_old_logs(self, days_threshold: int) -> Dict[str, Any]
  ```

  Archive logs older than threshold to compressed files.

Args:
    days_threshold: Archive events older than this many days

Returns:
    Dictionary with archival statistics

  **Parameters:**

  - `self`
  - `days_threshold` (int) = `30`: Archive events older than this many days


  **Returns:** Dict[str, Any]
    Dictionary with archival statistics



---

## Functions

### get_audit_logger

```python
get_audit_logger(base_path: Optional[Path]) -> AuditLogger
```

Get the global audit logger instance.

Args:
    base_path: Base path for audit files (default: cortex-brain/)

Returns:
    AuditLogger singleton instance


**Parameters:**

- `base_path` (Optional[Path]) = `None`: Base path for audit files (default: cortex-brain/)


**Returns:** AuditLogger
  AuditLogger singleton instance


---
