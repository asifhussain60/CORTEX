# CORTEX Documentation Generation Report

**Generated:** 2025-11-18 17:43:09  
**Profile:** standard  
**Duration:** 1.34 seconds

## Summary

- **Diagrams Generated:** 0
- **Pages Generated:** 20
- **Errors:** 0
- **Warnings:** 1

## Pipeline Stages

### Pre Flight Validation

- **Duration:** 0.00s
- **Result:** {
  "brain_structure": "VALID",
  "yaml_schemas": "VALID",
  "code_structure": "VALID",
  "write_permissions": "VALID"
}

### Destructive Cleanup

- **Duration:** 0.02s
- **Result:** {
  "backup_path": "D:\\PROJECTS\\CORTEX\\docs-backup-20251118-174308",
  "files_removed": 53,
  "space_freed_mb": 0.2644691467285156
}

### Diagram Generation

- **Duration:** 0.03s
- **Result:** {
  "mermaid_diagrams": {
    "total": 14,
    "files": [
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\01-tier-architecture.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\02-agent-coordination-system.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\03-information-flow.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\04-vision-api-integration.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\05-cortex-one-pager.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\06-epm-doc-generator-pipeline.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\07-module-structure.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\08-brain-protection.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\09-tdd-cycle.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\10-doc-component-registry.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\11-plugin-architecture.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\12-conversation-flow.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\13-knowledge-graph-update.mmd",
      "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\mermaid\\14-health-check.mmd"
    ]
  },
  "image_prompts": {
    "enabled": false,
    "reason": "Profile 'standard' does not include image prompts"
  }
}

### Page Generation

- **Duration:** 1.15s
- **Result:** {
  "story": {
    "success": true,
    "output_file": "D:\\PROJECTS\\CORTEX\\docs\\diagrams\\story\\The CORTEX Story.md",
    "content_length": 13728,
    "word_count": 1974
  },
  "template_pages": {
    "total": 20,
    "files": [
      "D:\\PROJECTS\\CORTEX\\docs\\getting-started\\quick-start.md",
      "D:\\PROJECTS\\CORTEX\\docs\\getting-started\\installation.md",
      "D:\\PROJECTS\\CORTEX\\docs\\getting-started\\configuration.md",
      "D:\\PROJECTS\\CORTEX\\docs\\architecture\\overview.md",
      "D:\\PROJECTS\\CORTEX\\docs\\architecture\\tier-system.md",
      "D:\\PROJECTS\\CORTEX\\docs\\architecture\\agents.md",
      "D:\\PROJECTS\\CORTEX\\docs\\architecture\\brain-protection.md",
      "D:\\PROJECTS\\CORTEX\\docs\\operations\\overview.md",
      "D:\\PROJECTS\\CORTEX\\docs\\operations\\entry-point-modules.md",
      "D:\\PROJECTS\\CORTEX\\docs\\operations\\workflows.md",
      "D:\\PROJECTS\\CORTEX\\docs\\operations\\health-monitoring.md",
      "D:\\PROJECTS\\CORTEX\\docs\\plugins\\vscode-extension.md",
      "D:\\PROJECTS\\CORTEX\\docs\\plugins\\development.md",
      "D:\\PROJECTS\\CORTEX\\docs\\reference\\api.md",
      "D:\\PROJECTS\\CORTEX\\docs\\reference\\configuration.md",
      "D:\\PROJECTS\\CORTEX\\docs\\reference\\response-templates.md",
      "D:\\PROJECTS\\CORTEX\\docs\\guides\\admin-guide.md",
      "D:\\PROJECTS\\CORTEX\\docs\\guides\\developer-guide.md",
      "D:\\PROJECTS\\CORTEX\\docs\\guides\\troubleshooting.md",
      "D:\\PROJECTS\\CORTEX\\docs\\guides\\best-practices.md"
    ]
  },
  "total_pages": 21
}

### Cross Reference

- **Duration:** 0.10s
- **Result:** {
  "total_pages": 42,
  "total_links": 42,
  "broken_links": 17,
  "total_headings": 1292,
  "navigation_entries": 26
}

### Post Validation

- **Duration:** 0.04s
- **Result:** {
  "capability_coverage": {
    "validation_approach": "capability_driven",
    "threshold": 0.8,
    "total_capabilities": 8,
    "documented_capabilities": 0,
    "undocumented_capabilities": 8,
    "coverage_rate": 0.0,
    "is_valid": false,
    "status": "FAIL",
    "documented_list": [],
    "undocumented_list": [
      {
        "id": "code_writing",
        "name": "Code Writing",
        "status": "implemented",
        "priority": "high",
        "expected_docs": [
          "guides/code-writing.md",
          "api/code-writing-api.md"
        ]
      },
      {
        "id": "code_review",
        "name": "Code Review",
        "status": "partial",
        "priority": "high",
        "expected_docs": [
          "guides/code-review.md"
        ]
      },
      {
        "id": "code_rewrite",
        "name": "Code Rewrite",
        "status": "implemented",
        "priority": "high",
        "expected_docs": [
          "guides/code-rewrite.md",
          "api/code-rewrite-api.md"
        ]
      },
      {
        "id": "backend_testing",
        "name": "Backend Testing",
        "status": "implemented",
        "priority": "high",
        "expected_docs": [
          "guides/backend-testing.md",
          "api/backend-testing-api.md"
        ]
      },
      {
        "id": "web_testing",
        "name": "Web Testing",
        "status": "implemented",
        "priority": "high",
        "expected_docs": [
          "guides/web-testing.md"
        ]
      },
      {
        "id": "code_documentation",
        "name": "Code Documentation",
        "status": "implemented",
        "priority": "high",
        "expected_docs": [
          "guides/code-documentation.md"
        ]
      },
      {
        "id": "reverse_engineering",
        "name": "Reverse Engineering",
        "status": "partial",
        "priority": "medium",
        "expected_docs": [
          "guides/reverse-engineering.md"
        ]
      },
      {
        "id": "ui_from_server_spec",
        "name": "UI from Server Spec",
        "status": "partial",
        "priority": "medium",
        "expected_docs": [
          "guides/ui-from-server-spec.md"
        ]
      }
    ],
    "total_docs_found": 42,
    "expected_doc_patterns": 11
  },
  "internal_links": "VALID",
  "broken_links": [],
  "diagram_references": "VALID",
  "markdown_syntax": "VALID",
  "mkdocs_build": "VALID"
}

## Warnings

- Post-validation found issues


---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Generated by:** CORTEX EPM Documentation Generator v1.0.0
