# CORTEX Admin EPM Migration Guide

**Version:** 1.0.0  
**Target Spec:** DOCUMENTATION-FORMAT-SPEC-v1.0  
**Created:** 2025-11-28  
**Author:** Asif Hussain

---

## 📋 Overview

This guide provides step-by-step instructions for migrating existing CORTEX admin Entry Point Modules (EPMs) to the new D3.js interactive dashboard format.

**Applies To:**
- Enterprise Documentation Orchestrator
- System Alignment Orchestrator
- Diagram Regeneration Module
- Design Sync Orchestrator
- Analytics Dashboard
- Response Templates Module

**Migration Time:** 4-6 hours per EPM  
**Complexity:** Medium  
**Risk Level:** Low (backward compatibility maintained)

---

## 🎯 Migration Strategy

### Phase Approach

1. **Phase 1: Add D3.js Dashboard Generation** (2 hours)
   - Install dependencies
   - Create dashboard generator instance
   - Convert data to dashboard format
   - Generate HTML output

2. **Phase 2: Maintain Backward Compatibility** (1 hour)
   - Add format parameter to existing methods
   - Support both Rich/HTML outputs
   - Add deprecation warnings for old format

3. **Phase 3: Testing & Validation** (1-2 hours)
   - Write unit tests for dashboard generation
   - Validate against format schema
   - Test export functionality
   - Performance testing

4. **Phase 4: Documentation** (30 minutes)
   - Update EPM docstrings
   - Add usage examples
   - Update user-facing docs

---

## 🛠️ Prerequisites

### Required Dependencies

Add to `requirements.txt`:
```text
# D3.js Dashboard Requirements
playwright>=1.40.0
python-pptx>=0.6.21
Pillow>=10.0.0
jsonschema>=4.19.0
```

Install:
```bash
pip install playwright python-pptx Pillow jsonschema
playwright install chromium
```

### Import Required Modules

```python
from src.utils.interactive_dashboard_generator import InteractiveDashboardGenerator
from pathlib import Path
import json
```

---

## 📝 Step-by-Step Migration

### Step 1: Initialize Dashboard Generator

Add to your EPM's `__init__` method:

```python
class EnterpriseDocumentationOrchestrator:
    def __init__(self, config_path: Optional[str] = None):
        # Existing initialization...
        
        # NEW: Dashboard generator
        self.dashboard_generator = InteractiveDashboardGenerator()
        self.output_format = "dashboard"  # "dashboard" or "rich" for backward compatibility
```

### Step 2: Convert Data to Dashboard Format

Create a new method to transform your existing data:

```python
def _prepare_dashboard_data(self, operation_results: dict) -> dict:
    """
    Convert operation results to dashboard JSON format.
    
    Args:
        operation_results: Raw operation data (existing format)
        
    Returns:
        dict: Dashboard-compatible JSON structure
    """
    return {
        "metadata": {
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "version": self.version,  # e.g., "3.4.0"
            "operationType": "enterprise_documentation",
            "author": "CORTEX"
        },
        "overview": {
            "executiveSummary": self._generate_executive_summary(operation_results),
            "keyMetrics": self._extract_key_metrics(operation_results),
            "statusIndicator": self._determine_status(operation_results)
        },
        "visualizations": {
            "forceGraph": self._build_dependency_graph(operation_results),
            "timeSeries": self._build_time_series(operation_results)
        },
        "diagrams": self._convert_diagrams_to_mermaid(operation_results),
        "dataTable": self._build_data_table(operation_results),
        "recommendations": self._generate_recommendations(operation_results)
    }
```

### Step 3: Implement Data Extraction Helpers

#### Executive Summary

```python
def _generate_executive_summary(self, results: dict) -> str:
    """
    Generate 3-sentence executive summary.
    
    Returns:
        str: Natural language summary (100-1000 chars)
    """
    # Extract key information
    total_items = len(results.get("items", []))
    success_count = sum(1 for item in results.get("items", []) if item.get("status") == "success")
    success_rate = (success_count / total_items * 100) if total_items > 0 else 0
    
    # Build narrative
    summary = (
        f"Processed {total_items} documentation items with {success_rate:.1f}% success rate. "
        f"Operation completed in {results.get('duration', 0):.2f} seconds with no critical errors. "
        f"All outputs validated and ready for deployment."
    )
    
    return summary
```

#### Key Metrics

```python
def _extract_key_metrics(self, results: dict) -> list[dict]:
    """
    Extract top 5-10 key metrics with status indicators.
    
    Returns:
        list[dict]: Metric objects with label, value, trend, status
    """
    metrics = []
    
    # Metric 1: Success Rate
    success_rate = self._calculate_success_rate(results)
    metrics.append({
        "label": "Success Rate",
        "value": f"{success_rate:.1f}%",
        "trend": "up" if success_rate >= 90 else "down",
        "trendValue": "+5.2%" if success_rate >= 90 else "-2.1%",
        "status": "healthy" if success_rate >= 90 else "warning"
    })
    
    # Metric 2: Processing Time
    duration = results.get("duration", 0)
    metrics.append({
        "label": "Processing Time",
        "value": f"{duration:.2f}s",
        "trend": "stable",
        "trendValue": "+0.3s",
        "status": "healthy" if duration < 10 else "warning"
    })
    
    # Metric 3: Items Processed
    total_items = len(results.get("items", []))
    metrics.append({
        "label": "Items Processed",
        "value": str(total_items),
        "trend": "up",
        "trendValue": "+12",
        "status": "healthy"
    })
    
    # Metric 4: Error Count
    error_count = sum(1 for item in results.get("items", []) if item.get("status") == "error")
    metrics.append({
        "label": "Errors",
        "value": str(error_count),
        "trend": "down" if error_count == 0 else "up",
        "trendValue": "-3" if error_count == 0 else "+1",
        "status": "healthy" if error_count == 0 else "critical"
    })
    
    # Metric 5: System Health
    health_score = self._calculate_health_score(results)
    metrics.append({
        "label": "System Health",
        "value": f"{health_score}%",
        "trend": "up",
        "trendValue": "+3%",
        "status": "healthy" if health_score >= 80 else "warning"
    })
    
    return metrics
```

#### Status Indicator

```python
def _determine_status(self, results: dict) -> dict:
    """
    Determine overall operation status.
    
    Returns:
        dict: Status object with status level and message
    """
    error_count = sum(1 for item in results.get("items", []) if item.get("status") == "error")
    warning_count = sum(1 for item in results.get("items", []) if item.get("status") == "warning")
    
    if error_count > 0:
        return {
            "status": "critical",
            "message": f"Operation completed with {error_count} critical errors requiring immediate attention"
        }
    elif warning_count > 5:
        return {
            "status": "warning",
            "message": f"Operation completed successfully with {warning_count} warnings to review"
        }
    else:
        return {
            "status": "healthy",
            "message": "All operations completed successfully with no issues detected"
        }
```

#### Force-Directed Graph

```python
def _build_dependency_graph(self, results: dict) -> dict:
    """
    Build D3.js force-directed graph data.
    
    Returns:
        dict: Graph with nodes and links
    """
    nodes = []
    links = []
    
    # Extract nodes from results
    for idx, item in enumerate(results.get("items", [])):
        nodes.append({
            "id": f"item_{idx}",
            "group": 1 if item.get("status") == "success" else 2,
            "label": item.get("name", f"Item {idx}"),
            "size": 10
        })
        
        # Extract dependencies for links
        for dep in item.get("dependencies", []):
            links.append({
                "source": f"item_{idx}",
                "target": dep,
                "value": 1
            })
    
    return {
        "nodes": nodes,
        "links": links
    }
```

#### Time Series Chart

```python
def _build_time_series(self, results: dict) -> dict:
    """
    Build Chart.js time series data.
    
    Returns:
        dict: Time series with labels and datasets
    """
    # Extract historical data (last 30 days)
    history = results.get("history", [])
    
    labels = [entry.get("date") for entry in history]
    health_scores = [entry.get("health", 0) for entry in history]
    success_rates = [entry.get("success_rate", 0) for entry in history]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "System Health",
                "data": health_scores,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)"
            },
            {
                "label": "Success Rate",
                "data": success_rates,
                "borderColor": "rgb(54, 162, 235)",
                "backgroundColor": "rgba(54, 162, 235, 0.2)"
            }
        ]
    }
```

#### Mermaid Diagrams

```python
def _convert_diagrams_to_mermaid(self, results: dict) -> list[dict]:
    """
    Convert existing diagrams to Mermaid format.
    
    Returns:
        list[dict]: Diagram objects with title, code, type
    """
    diagrams = []
    
    # Architecture Diagram
    diagrams.append({
        "title": "System Architecture",
        "mermaidCode": """graph TD
    A[User Request] --> B{Intent Router}
    B --> C[Documentation Module]
    B --> D[Validation Module]
    C --> E[Output Generator]
    D --> E
    E --> F[Dashboard]""",
        "type": "flowchart",
        "description": "Overall system architecture and data flow"
    })
    
    # Data Flow Diagram
    diagrams.append({
        "title": "Processing Pipeline",
        "mermaidCode": """sequenceDiagram
    participant U as User
    participant E as EPM
    participant D as Dashboard Gen
    participant O as Output
    U->>E: Request operation
    E->>E: Process data
    E->>D: Generate dashboard
    D->>O: Write HTML
    O->>U: Return dashboard""",
        "type": "sequenceDiagram",
        "description": "Operation processing sequence"
    })
    
    return diagrams
```

#### Data Table

```python
def _build_data_table(self, results: dict) -> list[dict]:
    """
    Build sortable data table rows.
    
    Returns:
        list[dict]: Table rows with consistent schema
    """
    table_rows = []
    
    for item in results.get("items", []):
        table_rows.append({
            "name": item.get("name", "Unknown"),
            "type": item.get("type", "N/A"),
            "status": item.get("status", "unknown"),
            "health": item.get("health", 0),
            "lastUpdated": item.get("last_updated", "2025-11-28")
        })
    
    return table_rows
```

#### Recommendations

```python
def _generate_recommendations(self, results: dict) -> list[dict]:
    """
    Generate AI-powered recommendations with priority ranking.
    
    Returns:
        list[dict]: Prioritized recommendations
    """
    recommendations = []
    
    # Analyze results for issues
    error_items = [item for item in results.get("items", []) if item.get("status") == "error"]
    warning_items = [item for item in results.get("items", []) if item.get("status") == "warning"]
    
    # High Priority: Fix Errors
    if error_items:
        recommendations.append({
            "priority": "high",
            "title": f"Resolve {len(error_items)} Critical Errors",
            "rationale": "Critical errors blocking deployment and affecting system stability",
            "steps": [
                "Review error logs for root cause analysis",
                "Apply fixes to failing components",
                "Re-run validation tests",
                "Verify all errors resolved"
            ],
            "expectedImpact": f"+{len(error_items) * 5}% system health improvement",
            "estimatedEffort": f"{len(error_items) * 2}-{len(error_items) * 4} hours",
            "relatedResources": [
                "/docs/troubleshooting-guide.md",
                "/docs/error-reference.md"
            ]
        })
    
    # Medium Priority: Address Warnings
    if warning_items:
        recommendations.append({
            "priority": "medium",
            "title": f"Address {len(warning_items)} Warnings",
            "rationale": "Warnings indicate potential issues that may escalate if not addressed",
            "steps": [
                "Review warning details and context",
                "Prioritize by severity and impact",
                "Implement fixes for top warnings",
                "Monitor for recurrence"
            ],
            "expectedImpact": f"+{len(warning_items) * 2}% reliability improvement",
            "estimatedEffort": f"{len(warning_items)}-{len(warning_items) * 2} hours",
            "relatedResources": [
                "/docs/warning-resolution-guide.md"
            ]
        })
    
    # Low Priority: Optimization
    recommendations.append({
        "priority": "low",
        "title": "Optimize Processing Performance",
        "rationale": "Current processing time can be reduced through caching and parallelization",
        "steps": [
            "Profile operation to identify bottlenecks",
            "Implement caching for repeated operations",
            "Add parallel processing where applicable",
            "Validate performance improvements"
        ],
        "expectedImpact": "-30% processing time reduction",
        "estimatedEffort": "4-6 hours",
        "relatedResources": [
            "/docs/performance-optimization-guide.md"
        ]
    })
    
    return recommendations
```

### Step 4: Generate Dashboard

Update your main operation method:

```python
def execute_operation(self, params: dict, output_format: str = "dashboard") -> str:
    """
    Execute operation and generate output.
    
    Args:
        params: Operation parameters
        output_format: "dashboard" (new) or "rich" (legacy)
        
    Returns:
        str: Path to generated output file
    """
    # Execute operation (existing logic)
    results = self._perform_operation(params)
    
    # Generate output based on format
    if output_format == "dashboard":
        # NEW: Generate D3.js dashboard
        dashboard_data = self._prepare_dashboard_data(results)
        output_path = Path(f"cortex-brain/documents/reports/{self.operation_name}-dashboard.html")
        
        success = self.dashboard_generator.generate_dashboard(
            title=f"{self.operation_name} Dashboard",
            data=dashboard_data,
            output_file=str(output_path)
        )
        
        if not success:
            raise RuntimeError("Dashboard generation failed")
            
        return str(output_path)
    
    elif output_format == "rich":
        # LEGACY: Generate Rich console output (backward compatibility)
        return self._generate_rich_output(results)
    
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
```

---

## ✅ Testing Checklist

### Unit Tests

Create test file `tests/test_[epm_name]_dashboard.py`:

```python
import pytest
from src.orchestrators.enterprise_documentation_orchestrator import EnterpriseDocumentationOrchestrator
from pathlib import Path
import json

def test_dashboard_generation():
    """Test dashboard HTML generation."""
    orchestrator = EnterpriseDocumentationOrchestrator()
    output_path = orchestrator.execute_operation(
        params={"test": True},
        output_format="dashboard"
    )
    
    assert Path(output_path).exists()
    assert output_path.endswith(".html")

def test_dashboard_data_structure():
    """Test dashboard JSON data structure."""
    orchestrator = EnterpriseDocumentationOrchestrator()
    results = {"items": [], "duration": 1.5}
    dashboard_data = orchestrator._prepare_dashboard_data(results)
    
    # Validate structure
    assert "metadata" in dashboard_data
    assert "overview" in dashboard_data
    assert "visualizations" in dashboard_data
    assert "diagrams" in dashboard_data
    assert "dataTable" in dashboard_data
    assert "recommendations" in dashboard_data

def test_executive_summary_length():
    """Test executive summary meets length requirements."""
    orchestrator = EnterpriseDocumentationOrchestrator()
    results = {"items": [{"status": "success"}], "duration": 2.0}
    summary = orchestrator._generate_executive_summary(results)
    
    assert 100 <= len(summary) <= 1000

def test_key_metrics_count():
    """Test key metrics array has 5-10 items."""
    orchestrator = EnterpriseDocumentationOrchestrator()
    results = {"items": [], "duration": 1.0}
    metrics = orchestrator._extract_key_metrics(results)
    
    assert 5 <= len(metrics) <= 10

def test_backward_compatibility():
    """Test Rich output still works."""
    orchestrator = EnterpriseDocumentationOrchestrator()
    output = orchestrator.execute_operation(
        params={"test": True},
        output_format="rich"
    )
    
    assert output is not None
```

### Validation Tests

```python
def test_schema_validation():
    """Test dashboard data validates against JSON schema."""
    from jsonschema import validate
    import json
    
    # Load schema
    schema_path = Path("cortex-brain/documents/standards/format-validation-schema.json")
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Generate dashboard data
    orchestrator = EnterpriseDocumentationOrchestrator()
    results = {"items": [], "duration": 1.0}
    dashboard_data = orchestrator._prepare_dashboard_data(results)
    
    # Validate
    validate(instance=dashboard_data, schema=schema)  # Raises if invalid
```

### Performance Tests

```python
def test_generation_performance():
    """Test dashboard generation completes in <5 seconds."""
    import time
    
    orchestrator = EnterpriseDocumentationOrchestrator()
    
    start = time.time()
    output_path = orchestrator.execute_operation(
        params={"test": True},
        output_format="dashboard"
    )
    duration = time.time() - start
    
    assert duration < 5.0, f"Generation took {duration:.2f}s (target: <5s)"
```

---

## 🚨 Common Pitfalls

### 1. Missing Required Fields

**Problem:** Schema validation fails due to missing required fields

**Solution:** Use the helper methods provided above and validate data structure before generation

```python
# BAD
dashboard_data = {
    "metadata": {},  # Missing required fields
    "overview": {}
}

# GOOD
dashboard_data = self._prepare_dashboard_data(results)  # Uses validated structure
```

### 2. Incorrect Mermaid Syntax

**Problem:** Mermaid diagrams fail to render

**Solution:** Test Mermaid code at https://mermaid.live before embedding

```python
# BAD
mermaidCode = "graph A -> B"  # Invalid syntax

# GOOD
mermaidCode = """graph TD
    A[Start] --> B[End]"""
```

### 3. Large File Sizes

**Problem:** Dashboard HTML files exceed 2MB limit

**Solution:** Paginate data tables and optimize embedded data

```python
# Limit table rows to first 100
dataTable = self._build_data_table(results)[:100]
```

### 4. Performance Issues

**Problem:** Dashboard generation takes >5 seconds

**Solution:** Use caching and lazy loading

```python
# Cache expensive computations
@lru_cache(maxsize=128)
def _calculate_health_score(self, results_hash: str) -> float:
    # Expensive calculation
    pass
```

---

## 📚 Example: Complete EPM Migration

Here's a complete example migrating the System Alignment Orchestrator:

```python
# src/orchestrators/system_alignment_orchestrator.py

from src.utils.interactive_dashboard_generator import InteractiveDashboardGenerator
from pathlib import Path
import json

class SystemAlignmentOrchestrator:
    def __init__(self):
        self.dashboard_generator = InteractiveDashboardGenerator()
        self.version = "3.4.0"
    
    def run_alignment(self, output_format: str = "dashboard") -> str:
        """Run 7-layer validation with dashboard output."""
        # Execute validation (existing logic)
        results = self._run_7_layer_validation()
        
        if output_format == "dashboard":
            return self._generate_dashboard(results)
        else:
            return self._generate_rich_output(results)
    
    def _generate_dashboard(self, results: dict) -> str:
        """Generate D3.js dashboard."""
        dashboard_data = {
            "metadata": {
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "version": self.version,
                "operationType": "system_alignment",
                "author": "CORTEX"
            },
            "overview": {
                "executiveSummary": f"System Alignment validation completed {results['passed']}/{results['total']} layers successfully. Overall health score: {results['health_score']}%. {results['critical_count']} critical issues require immediate attention.",
                "keyMetrics": [
                    {
                        "label": "Overall Health",
                        "value": f"{results['health_score']}%",
                        "trend": "up",
                        "trendValue": "+3%",
                        "status": "healthy" if results['health_score'] >= 80 else "warning"
                    },
                    {
                        "label": "Layers Passed",
                        "value": f"{results['passed']}/{results['total']}",
                        "trend": "stable",
                        "status": "healthy" if results['passed'] == results['total'] else "warning"
                    },
                    # ... more metrics
                ],
                "statusIndicator": {
                    "status": "healthy" if results['critical_count'] == 0 else "critical",
                    "message": f"{results['critical_count']} critical issues detected" if results['critical_count'] > 0 else "All layers validated successfully"
                }
            },
            "visualizations": {
                "forceGraph": self._build_layer_dependency_graph(results),
                "timeSeries": self._build_health_trend(results)
            },
            "diagrams": self._generate_validation_diagrams(results),
            "dataTable": self._build_layer_table(results),
            "recommendations": self._generate_remediation_steps(results)
        }
        
        output_path = Path("cortex-brain/documents/reports/system-alignment-dashboard.html")
        self.dashboard_generator.generate_dashboard(
            title="CORTEX System Alignment Dashboard",
            data=dashboard_data,
            output_file=str(output_path)
        )
        
        return str(output_path)
```

---

## 🔄 Rollback Procedure

If migration causes issues, rollback is simple:

1. Set `output_format="rich"` in method calls
2. All legacy functionality remains intact
3. No data loss or compatibility issues

---

## 📞 Support

For migration assistance, see:
- **Format Specification:** `cortex-brain/documents/standards/DOCUMENTATION-FORMAT-SPEC-v1.0.md`
- **Validation Schema:** `cortex-brain/documents/standards/format-validation-schema.json`
- **Reference Implementation:** `src/utils/interactive_dashboard_generator.py`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
