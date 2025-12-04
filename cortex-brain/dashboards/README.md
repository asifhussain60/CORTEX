# CORTEX Repository Dashboard

**Version:** 1.0  
**Location:** `cortex-brain/dashboards/ui/`  
**Type:** Pure client-side JavaScript dashboard (no backend required)

---

## Quick Start

### 1. Start HTTP Server

```bash
# Navigate to dashboards directory
cd cortex-brain/dashboards/
python -m http.server 8080
```

### 2. Open Dashboard

```
http://localhost:8080/ui/index.html?source=mock
```

### 3. Data Sources

The `?source=` parameter controls which data directory to load:
- `mock` - Example data
- `cortex` - CORTEX repository data
- `noor-canvas` - Noor Canvas application data
- `alist` - Alist application data
- `ksessions` - K-Sessions application data

---

## For Repository Scanners & Data Generators

**📖 IMPORTANT:** To generate compatible JSON data for your repository:

**See:** `cortex-brain/documents/user-guides/dashboard-data-format-guidelines.md`

This guide provides:
- **Exact JSON schemas** for all 7 required files
- **Field specifications** with data types and validation rules
- **Common mistakes to avoid**
- **Python code examples**

### Required Data Files (7 files)

Your scanner must generate these in `cortex-brain/dashboards/{source}/`:

1. **health-data.json** - Repository health metrics
2. **tech-stack.json** - Technologies (languages, frameworks)
3. **security.json** - Vulnerabilities, OWASP compliance
4. **architecture.json** - Code structure, components
5. **code-organization.json** - Complexity, hotspots
6. **team-metrics.json** - Git activity, contributors
7. **vendors.json** - Third-party services

---

## File Structure

```
dashboards/
├── ui/                 # Dashboard application (49 files)
│   ├── index.html
│   ├── app.js
│   ├── data-loader.js
│   ├── components/     # 7 tab components
│   └── tests/          # 170 tests
├── mock/               # Example data (7 JSON files)
├── cortex/             # CORTEX data
├── noor-canvas/        # Noor Canvas data
├── alist/              # Alist data
└── ksessions/          # K-Sessions data
```

## JSON Schema

Each dashboard file follows this schema:

```json
{
  "app_id": "string (required)",
  "tabs": {
    "tab_name": {
      "key": "value",
      ...
    }
  },
  "metadata": {
    "app_name": "string (optional)",
    "app_type": "internal|external|user (optional)",
    "version": "string (optional)",
    "last_updated": "ISO 8601 datetime (optional)",
    "last_scan": "ISO 8601 datetime (optional)"
  }
}
```

## Example Dashboard File

```json
{
  "app_id": "cortex",
  "tabs": {
    "overview": {
      "total_files": 250,
      "total_lines": 12500,
      "test_coverage": 85
    },
    "metrics": {
      "complexity": 3.2,
      "maintainability": 82
    },
    "health": {
      "status": "healthy",
      "last_check": "2025-12-04T10:30:00Z"
    }
  },
  "metadata": {
    "app_name": "CORTEX",
    "app_type": "internal",
    "version": "3.3.0",
    "last_updated": "2025-12-04T10:30:00Z"
  }
}
```

## Clean Architecture Notes

- **Domain Layer**: Defines `DashboardData` entity (pure Python, no I/O)
- **Infrastructure Layer**: `JsonDashboardRepository` implements persistence (this directory)
- **Application Layer**: Use cases orchestrate loading/saving via repository interface
- **Presentation Layer**: Flask routes display dashboard data

Dashboard files are managed exclusively through the repository pattern - never edit directly in production.
