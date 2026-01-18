# Response Templates - Deprecated Location

**⚠️ NOTICE: This directory is deprecated.**

Response templates have been reorganized into a more structured hierarchy:

## New Template Locations

```
cortex-brain/tier2/
├── base/                        # Base templates (success, error, warning)
│   ├── success-response.yaml
│   ├── error-response.yaml
│   └── warning-response.yaml
├── domains/                     # Domain-specific templates
│   ├── governance/
│   │   ├── evaluation-result.yaml
│   │   └── rule-violation.yaml
│   ├── planning/
│   │   ├── recommendations.yaml
│   │   └── impact-assessment.yaml
│   └── tdd/
│       ├── test-result.yaml
│       └── coverage-report.yaml
└── response-templates-index.yaml  # Central index
```

## Usage

See `response-templates-index.yaml` for:
- Complete template listing
- Usage guidelines
- Selection guide by operation type

## Migration

If you have custom templates in this directory:
1. Move them to appropriate `domains/` subdirectory
2. Update template metadata to new format
3. Add entry to `response-templates-index.yaml`

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
