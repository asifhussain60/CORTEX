# ux_enhancement_utility

UX Enhancement Utility

Fast, lightweight codebase analysis and dashboard generation utility.
Replaces orchestrator with focused utility for UX enhancement workflows.

Features:
- Codebase validation and metadata extraction
- Multi-dimensional analysis (quality, architecture, performance, security)
- Discovery Intelligence pattern application
- Interactive dashboard generation with Phase 2 template
- Browser auto-launch for immediate exploration

Operations:
1. analyze_and_generate_dashboard - Main workflow orchestration
2. validate_codebase - Validate path and extract metadata
3. analyze_quality - Code quality analysis
4. analyze_architecture - Architecture component mapping
5. analyze_performance - Performance profiling
6. analyze_security - Security vulnerability scanning
7. apply_discovery_patterns - Apply Discovery Intelligence
8. export_to_dashboard_format - Transform to dashboard JSON
9. generate_dashboard_html - Create interactive HTML

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [analyze_and_generate_dashboard](#analyze_and_generate_dashboard)
- [validate_codebase](#validate_codebase)
- [analyze_quality](#analyze_quality)
- [analyze_architecture](#analyze_architecture)
- [analyze_performance](#analyze_performance)
- [analyze_security](#analyze_security)
- [apply_discovery_patterns](#apply_discovery_patterns)
- [export_to_dashboard_format](#export_to_dashboard_format)
- [generate_dashboard_html](#generate_dashboard_html)


## Overview

- **Classes:** 0
- **Functions:** 10
- **Dependencies:** datetime, json, pathlib, shutil, typing, webbrowser


## Functions

### analyze_and_generate_dashboard

```python
analyze_and_generate_dashboard(cortex_root: Path, codebase_path: str, user_request: str, skip_explanation: bool) -> Dict[str, Any]
```

Main workflow: analyze codebase and generate interactive dashboard.

Steps:
1. Validate codebase path and extract metadata
2. Run multi-dimensional analysis (quality, arch, perf, security)
3. Apply Discovery Intelligence patterns
4. Export to dashboard JSON format
5. Generate HTML dashboard with visualizations
6. Open in browser

Args:
    cortex_root: Path to CORTEX repository root
    codebase_path: Path to codebase to analyze
    user_request: Original user request (for context)
    skip_explanation: Whether user opted into auto-approval
    
Returns:
    Dict with analysis results and dashboard path:
        - success: bool
        - dashboard_path: str
        - analysis_summary: dict with scores
        - error: str (if failed)


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository root
- `codebase_path` (str): Path to codebase to analyze
- `user_request` (str): Original user request (for context)
- `skip_explanation` (bool) = `False`: Whether user opted into auto-approval


**Returns:** Dict[str, Any]
  Dict with analysis results and dashboard path: - success: bool - dashboard_path: str - analysis_summary: dict with scores - error: str (if failed)


---

### validate_codebase

```python
validate_codebase(codebase_path: str) -> Dict[str, Any]
```

Validate codebase exists and gather basic metadata.

Args:
    codebase_path: Path to codebase
    
Returns:
    Dict with codebase metadata:
        - path: str
        - name: str
        - file_count: int
        - timestamp: str (ISO format)


**Parameters:**

- `codebase_path` (str): Path to codebase


**Returns:** Dict[str, Any]
  Dict with codebase metadata: - path: str - name: str - file_count: int - timestamp: str (ISO format)


---

### analyze_quality

```python
analyze_quality(codebase_path: str) -> Dict[str, Any]
```

Analyze code quality metrics.

TODO: Integrate with actual CodeCleanupValidator
Currently returns mock data matching dashboard format.

Args:
    codebase_path: Path to codebase
    
Returns:
    Dict with quality metrics:
        - overall_score: int (0-100)
        - maintainability: int
        - reliability: int
        - security: int
        - performance: int
        - test_coverage: int
        - code_smells: dict
        - technical_debt: str
        - trend: str


**Parameters:**

- `codebase_path` (str): Path to codebase


**Returns:** Dict[str, Any]
  Dict with quality metrics: - overall_score: int (0-100) - maintainability: int - reliability: int - security: int - performance: int - test_coverage: int - code_smells: dict - technical_debt: str - trend: str


---

### analyze_architecture

```python
analyze_architecture(codebase_path: str) -> Dict[str, Any]
```

Analyze architecture components and relationships.

TODO: Integrate with actual ArchitectureAnalyzer
Currently returns mock data matching dashboard format.

Args:
    codebase_path: Path to codebase
    
Returns:
    Dict with architecture data:
        - health_score: int (0-100)
        - components: list of dicts
        - relationships: list
        - issues: list of str


**Parameters:**

- `codebase_path` (str): Path to codebase


**Returns:** Dict[str, Any]
  Dict with architecture data: - health_score: int (0-100) - components: list of dicts - relationships: list - issues: list of str


---

### analyze_performance

```python
analyze_performance(codebase_path: str) -> Dict[str, Any]
```

Profile performance and identify bottlenecks.

TODO: Integrate with actual PerformanceProfiler
Currently returns mock data matching dashboard format.

Args:
    codebase_path: Path to codebase
    
Returns:
    Dict with performance data:
        - grade: str (A-F)
        - api_latencies: dict
        - bottlenecks: list of dicts


**Parameters:**

- `codebase_path` (str): Path to codebase


**Returns:** Dict[str, Any]
  Dict with performance data: - grade: str (A-F) - api_latencies: dict - bottlenecks: list of dicts


---

### analyze_security

```python
analyze_security(codebase_path: str) -> Dict[str, Any]
```

Scan for security vulnerabilities.

TODO: Integrate with actual SecurityScanner
Currently returns mock data matching dashboard format.

Args:
    codebase_path: Path to codebase
    
Returns:
    Dict with security data:
        - rating: str (A-F)
        - owasp_top_10: dict
        - vulnerabilities: dict
        - compliance: dict


**Parameters:**

- `codebase_path` (str): Path to codebase


**Returns:** Dict[str, Any]
  Dict with security data: - rating: str (A-F) - owasp_top_10: dict - vulnerabilities: dict - compliance: dict


---

### apply_discovery_patterns

```python
apply_discovery_patterns(quality: Dict, architecture: Dict, performance: Dict, security: Dict) -> Dict[str, Any]
```

Apply Discovery Intelligence patterns to analysis results.

Generates context-aware suggestions, progressive questioning flows,
"what if" scenarios, and guided discovery paths.

Args:
    quality: Quality analysis results
    architecture: Architecture analysis results
    performance: Performance analysis results
    security: Security analysis results
    
Returns:
    Dict with discovery intelligence:
        - suggestions: list of dicts
        - patterns: dict (loaded from patterns file)


**Parameters:**

- `quality` (Dict): Quality analysis results
- `architecture` (Dict): Architecture analysis results
- `performance` (Dict): Performance analysis results
- `security` (Dict): Security analysis results


**Returns:** Dict[str, Any]
  Dict with discovery intelligence: - suggestions: list of dicts - patterns: dict (loaded from patterns file)


---

### export_to_dashboard_format

```python
export_to_dashboard_format(codebase_info: Dict, quality: Dict, architecture: Dict, performance: Dict, security: Dict, discovery: Dict) -> Dict[str, Any]
```

Export analysis results to Phase 2 dashboard JSON format.

Transforms analysis data to match the structure expected by
interactive dashboard with full visualization support.

Args:
    codebase_info: Codebase metadata
    quality: Quality analysis results
    architecture: Architecture analysis results
    performance: Performance analysis results
    security: Security analysis results
    discovery: Discovery intelligence data
    
Returns:
    Complete dashboard data structure matching analysis-data.json format


**Parameters:**

- `codebase_info` (Dict): Codebase metadata
- `quality` (Dict): Quality analysis results
- `architecture` (Dict): Architecture analysis results
- `performance` (Dict): Performance analysis results
- `security` (Dict): Security analysis results
- `discovery` (Dict): Discovery intelligence data


**Returns:** Dict[str, Any]
  Complete dashboard data structure matching analysis-data.json format


---

### generate_dashboard_html

```python
generate_dashboard_html(brain_path: Path, dashboard_data: Dict, user_request: str) -> Path
```

Generate interactive HTML dashboard with Tailwind CSS and D3.js visualizations.

Uses Phase 2 dashboard template with full feature set:
- 6-tab navigation (Executive, Architecture, Quality, Roadmap, Journey, Security)
- D3.js visualizations (force graphs, heatmaps, treemaps, Gantt charts)
- Discovery system with behavioral tracking
- Theme toggle (dark/light mode)
- Responsive design

Args:
    brain_path: Path to CORTEX brain directory
    dashboard_data: Complete dashboard data
    user_request: Original user request (for context)
    
Returns:
    Path to generated HTML file


**Parameters:**

- `brain_path` (Path): Path to CORTEX brain directory
- `dashboard_data` (Dict): Complete dashboard data
- `user_request` (str): Original user request (for context)


**Returns:** Path
  Path to generated HTML file


---
