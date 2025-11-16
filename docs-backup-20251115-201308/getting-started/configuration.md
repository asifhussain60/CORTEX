# Configuration Guide

**Generated**:   
**Version**: 

This guide covers all configuration options for CORTEX 3.0.

## Configuration Files

CORTEX uses multiple configuration files for different aspects of the system:

| File | Purpose | Format |
|------|---------|--------|
| `cortex.config.json` | Main system configuration | JSON |
| `mkdocs.yml` | Documentation site configuration | YAML |
| `cortex-brain/**/*.yaml` | Brain configuration and data | YAML |
| `package.json` | VS Code extension configuration | JSON |

## Main Configuration

### cortex.config.json

```json
{
  "brain_path": "cortex-brain",
  "tier0_protection": true,
  "auto_learning": true,
  "agent_config": {
    "right_brain": {
      "enabled": true,
      "agents": ["intent_router", "work_planner", "change_governor"]
    },
    "left_brain": {
      "enabled": true,
      "agents": ["code_executor", "test_generator", "health_validator"]
    }
  },
  "logging": {
    "level": "INFO",
    "directory": "logs",
    "rotation": "daily",
    "retention_days": 30
  }
}
```


### Configuration Options

#### Brain Path

**Property**: `brain_path`  
**Type**: `string`  
**Default**: `"cortex-brain"`

Path to the cortex-brain directory containing all knowledge and configuration.

```json
"brain_path": "cortex-brain"
```

#### Tier 0 Protection

**Property**: `tier0_protection`  
**Type**: `boolean`  
**Default**: `true`

Enable/disable Tier 0 brain protection. When enabled, all brain modifications require validation against protection rules.

```json
"tier0_protection": true
```

⚠️ **WARNING**: Disabling this removes brain protection safeguards.

#### Auto Learning

**Property**: `auto_learning`  
**Type**: `boolean`  
**Default**: `true`

Enable/disable automatic knowledge graph updates from conversations.

```json
"auto_learning": true
```

#### Agent Configuration

**Property**: `agent_config`  
**Type**: `object`

Configure which agents are enabled and their settings.

```json
"agent_config": {
  "right_brain": {
    "enabled": true,
    "agents": ["intent_router", "work_planner", "change_governor"],
    "max_concurrent": 3,
    "timeout_seconds": 30
  },
  "left_brain": {
    "enabled": true,
    "agents": ["code_executor", "test_generator", "health_validator"],
    "max_concurrent": 5,
    "timeout_seconds": 60
  }
}
```

#### Logging Configuration

**Property**: `logging`  
**Type**: `object`

Configure logging behavior.

```json
"logging": {
  "level": "INFO",
  "directory": "logs",
  "rotation": "daily",
  "retention_days": 30,
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
```

**Log Levels**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

#### Performance Settings

**Property**: `performance`  
**Type**: `object`

Tune performance settings.

```json
"performance": {
  "tier1_cache_size": 1000,
  "tier2_index_enabled": true,
  "tier3_lazy_load": true,
  "conversation_buffer_size": 50
}
```

## MkDocs Configuration

### mkdocs.yml


```yaml
site_name: CORTEX - AI Enhancement Framework
site_description: Long-term memory and strategic planning for GitHub Copilot
theme:
  name: material
  features: ["navigation.instant", "navigation.tracking", "navigation.tabs", "navigation.sections", "navigation.expand", "navigation.top", "search.suggest", "search.highlight", "toc.integrate", "content.code.copy", "content.tabs.link"]
```


## Brain Configuration

### Operations Config

**Location**: `cortex-brain/operations-config.yaml`

Configure operation routing and workflows.

```yaml
operations:
  documentation_generation:
    enabled: true
    trigger: manual
    validation_required: true
  
  health_check:
    enabled: true
    trigger: scheduled
    schedule: "0 6 * * *"  # Daily at 6 AM
  
  knowledge_cleanup:
    enabled: true
    trigger: scheduled
    schedule: "0 2 * * 0"  # Weekly on Sunday at 2 AM
```

### Brain Protection Rules

**Location**: `cortex-brain/brain-protection-rules.yaml`

Define protection rules for the cortex-brain.

```yaml
protection_rules:
  - path: "cortex-brain/tier0/**"
    action: deny
    reason: "Tier 0 files are protected from modification"
  
  - path: "cortex-brain/capabilities.yaml"
    action: require_approval
    approvers: ["admin"]
  
  - path: "cortex-brain/conversation-*.jsonl"
    action: allow
    reason: "Conversation logs can be written"
```

### Response Templates

**Location**: `cortex-brain/response-templates.yaml`

Define response templates for consistent communication.

```yaml
templates:
  task_complete:
    template: "✓ Task completed: {task_name}"
    usage: "When a task is successfully completed"
  
  validation_failed:
    template: "✗ Validation failed: {reason}"
    usage: "When validation fails"
  
  brain_protected:
    template: "⚠️ Brain protection: {rule_name} blocked this operation"
    usage: "When brain protection blocks an operation"
```

## Environment Variables

CORTEX respects these environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `CORTEX_BRAIN_PATH` | Override brain path | `cortex-brain` |
| `CORTEX_LOG_LEVEL` | Override log level | `INFO` |
| `CORTEX_DRY_RUN` | Enable dry-run mode globally | `false` |
| `CORTEX_NO_PROTECTION` | Disable brain protection (dangerous!) | `false` |

Example:

```bash
export CORTEX_LOG_LEVEL=DEBUG
export CORTEX_DRY_RUN=true
python -m src.epm.doc_generator
```

## Advanced Configuration

### Custom Source Mappings

**Location**: `cortex-brain/doc-generation-config/source-mapping.yaml`

Define custom data sources for documentation generation.

```yaml
custom_sources:
  my_data:
    type: yaml
    path: path/to/my/data.yaml
    description: "My custom data source"
```

### Custom Validation Rules

**Location**: `cortex-brain/doc-generation-config/validation-rules.yaml`

Add custom validation rules.

```yaml
custom_validations:
  - name: "Custom file check"
    check_type: file_exists
    path: path/to/required/file.txt
    severity: warning
```

### Custom Diagram Types

**Location**: `cortex-brain/doc-generation-config/diagram-definitions.yaml`

Define custom diagram types.

```yaml
custom_diagrams:
  - name: "My Custom Diagram"
    type: custom_type
    output_path: images/diagrams/custom/my-diagram.md
    generator: my_custom_generator
```

## Configuration Best Practices

1. **Keep secrets out of config**: Use environment variables for sensitive data
2. **Version control**: Commit configuration files to git
3. **Document changes**: Add comments explaining non-obvious settings
4. **Test changes**: Use dry-run mode to test configuration changes
5. **Backup before changing**: Keep backup of working configuration
6. **Use validation**: Validate YAML syntax before committing

## Troubleshooting

### Configuration Validation

Validate configuration files:

```bash
python -m src.epm.validate_config
```

### Common Issues

#### Invalid JSON

**Error**: `JSONDecodeError: Expecting property name`

**Solution**: Check for trailing commas, missing quotes, or syntax errors.

#### Invalid YAML

**Error**: `YAMLError: mapping values are not allowed here`

**Solution**: Check indentation, ensure proper YAML syntax.

#### Missing Configuration

**Error**: `ConfigurationError: Required key 'brain_path' not found`

**Solution**: Ensure all required configuration keys are present.

## Related Documentation

- [Quick Start Guide](quick-start.md)
- [Installation Guide](installation.md)
- [Admin Guide](../guides/admin-guide.md)

---

*This page was automatically generated by the CORTEX Documentation Generator.*