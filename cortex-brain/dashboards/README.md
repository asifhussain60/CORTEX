# Dashboard Data Storage

This directory stores dashboard JSON files for the universal dashboard system.

## File Structure

Each application has its own JSON file:
```
dashboards/
├── cortex.json         # CORTEX dashboard data
├── user-app-1.json     # External application 1
└── user-app-2.json     # External application 2
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
