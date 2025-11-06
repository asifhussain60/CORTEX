# Config Template Engine - Quick Reference

**Script:** `scripts/lib/config-template-engine.ps1`  
**Created:** 2025-11-06  
**Part of:** Phase 3 - Configuration Templating System

---

## Quick Start

### 1. Expand String Template
```powershell
. ./scripts/lib/config-template-engine.ps1

Expand-ConfigTemplate -TemplateContent 'Hello {{NAME}}' -Variables @{NAME='World'}
# Output: Hello World
```

### 2. Expand File Template
```powershell
. ./scripts/lib/config-template-engine.ps1

Expand-ConfigTemplate `
    -TemplatePath "config.template.json" `
    -OutputPath "config.json" `
    -Force
```

### 3. Use Built-in Variables
```powershell
. ./scripts/lib/config-template-engine.ps1

Expand-ConfigTemplate -TemplateContent '{{PROJECT_NAME}} on {{GIT_BRANCH}}'
# Output: CORTEX on cortex-migration
```

---

## Variable Syntax

| Syntax | Behavior | Example |
|--------|----------|---------|
| `{{VARIABLE}}` | **Required** - Error if missing | `{{API_URL}}` |
| `{{VARIABLE:default}}` | **Optional** - Use default if missing | `{{ENV:dev}}` |
| `{{lowercase}}` | **Ignored** - Not a valid variable | Preserved as-is |

---

## Built-in Variables

| Variable | Source | Example Value |
|----------|--------|---------------|
| `PROJECT_ROOT` | Git workspace root | `/Users/.../CORTEX` |
| `PROJECT_NAME` | Folder name | `CORTEX` |
| `KDS_ROOT` | CORTEX install dir | `/Users/.../CORTEX` |
| `GIT_BRANCH` | Current branch | `cortex-migration` |
| `TIMESTAMP` | ISO 8601 now | `2025-11-06T13:41:08Z` |

**Note:** Built-in variables are auto-detected. Custom variables override built-ins.

---

## Functions

### `Expand-ConfigTemplate`
Expand template with variable substitution.

**Parameters:**
- `-TemplatePath` - Path to template file
- `-TemplateContent` - String template (alternative to file)
- `-Variables` - Hashtable of custom variables
- `-OutputPath` - File to write (optional, returns string if omitted)
- `-Force` - Overwrite without confirmation

**Returns:** String or file path

### `Get-BuiltInVariables`
Get all auto-detected variables.

**Returns:** Hashtable

### `Test-TemplateVariables`
Validate template has all required variables.

**Parameters:**
- `-TemplatePath` - Path to template file
- `-Variables` - Custom variables

**Returns:** Boolean

---

## Common Patterns

### Pattern 1: JSON Config with Defaults
```json
{
  "name": "{{PROJECT_NAME}}",
  "version": "{{VERSION:1.0.0}}",
  "environment": "{{ENV:development}}"
}
```

### Pattern 2: YAML with Paths
```yaml
project: '{{PROJECT_NAME}}'
paths:
  root: '{{PROJECT_ROOT}}'
  config: '{{PROJECT_ROOT}}/config'
```

### Pattern 3: Markdown Documentation
```markdown
# {{PROJECT_NAME}}

**Generated:** {{TIMESTAMP}}  
**Branch:** {{GIT_BRANCH}}
```

---

## Error Handling

### Missing Required Variable
```powershell
Expand-ConfigTemplate -TemplateContent '{{REQUIRED}}'
# Error: Required variable not found: REQUIRED
#        (use {{REQUIRED:default}} for optional)
```

### File Not Found
```powershell
Expand-ConfigTemplate -TemplatePath "missing.json"
# Error: Template file not found: missing.json
```

### File Exists (No -Force)
```powershell
Expand-ConfigTemplate -TemplatePath "in.json" -OutputPath "exists.json"
# Prompt: File exists: exists.json. Overwrite? (y/N)
```

---

## Testing

### Run Unit Tests (Pester)
```powershell
Invoke-Pester -Path tests/Unit/ConfigTemplateEngine.tests.ps1
```

### Manual Test
```powershell
. ./scripts/lib/config-template-engine.ps1

# Test 1: Basic substitution
$result = Expand-ConfigTemplate -TemplateContent 'Hello {{NAME}}' -Variables @{NAME='Test'}
Write-Host "Result: $result"

# Test 2: Built-in variables
$vars = Get-BuiltInVariables
$vars | Format-Table

# Test 3: Validation
Test-TemplateVariables -TemplatePath "template.json" -Variables @{VAR='value'}
```

---

## Examples

### Example 1: Generate cortex.config.json
```powershell
$vars = @{
    LOG_LEVEL = "Debug"
    MAX_WORKERS = "4"
}

Expand-ConfigTemplate `
    -TemplatePath "cortex.config.template.json" `
    -Variables $vars `
    -OutputPath "cortex.config.json" `
    -Force
```

### Example 2: Validate Before Expand
```powershell
if (Test-TemplateVariables -TemplatePath "config.template.json") {
    Expand-ConfigTemplate -TemplatePath "config.template.json" -OutputPath "config.json"
} else {
    Write-Warning "Missing variables - cannot expand"
}
```

### Example 3: Programmatic Generation
```powershell
$projects = @('Project1', 'Project2', 'Project3')

foreach ($proj in $projects) {
    $vars = @{ PROJECT_NAME = $proj }
    
    Expand-ConfigTemplate `
        -TemplatePath "template.json" `
        -Variables $vars `
        -OutputPath "$proj/config.json" `
        -Force
}
```

---

## Tips & Best Practices

### ✅ DO
- Use UPPERCASE variable names (`{{PROJECT_NAME}}`)
- Provide defaults for optional values (`{{ENV:dev}}`)
- Validate templates before deployment
- Use descriptive variable names
- Document custom variables

### ❌ DON'T
- Use lowercase variables (`{{project}}` won't work)
- Hard-code sensitive data (use variables)
- Mix variable formats (`${VAR}` not supported)
- Forget to test expanded output
- Leave required variables undocumented

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Variable not found" error | Add to `-Variables` or use default syntax |
| Variables not expanding | Check UPPERCASE naming |
| Built-in vars not working | Ensure workspace-resolver.ps1 exists |
| Git branch not detected | Verify git repository initialized |
| Template file not found | Use absolute or relative path |

---

## Next Steps

After Task 3.1, proceed to:
1. **Task 3.2** - Convert existing configs to templates
2. **Task 3.3** - Update .gitignore
3. **Task 4.1** - Integrate with setup wizard

---

**Documentation:** `docs/TASK-3.1-TEMPLATE-ENGINE-COMPLETE.md`  
**Tests:** `tests/Unit/ConfigTemplateEngine.tests.ps1`  
**Examples:** `tests/fixtures/test.template.json`
