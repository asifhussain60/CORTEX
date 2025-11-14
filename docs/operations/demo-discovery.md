# Demo Discovery Operation

**Auto-generated:** 2025-11-14 07:18:41

---

## Overview

Discovery Report Generator

Orchestrates crawlers and generates comprehensive project intelligence reports.

## Usage

```python
from src.operations.demo_discovery import DiscoveryReportGenerator

operation = DiscoveryReportGenerator()
result = operation.execute()
```

## Methods

### `generate(self)`

Generate discovery report.

Returns:
    Dict with:
        - success: bool
        - report_path: str (path to generated report)
        - execution_time_ms: float
        - summary: str
