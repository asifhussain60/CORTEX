# ⚙️ Customization Guide

## Adding New Phases

To add a custom maintenance phase:

### Step 1: Create Phase File

```bash
# Create phase file
cat > .github/prompts/maintenance/phases/phase-12-custom.prompt.md << 'EOF'
# Phase 12: Custom Validation

## Purpose
[Your custom phase purpose]

## Execution
```bash
# Your custom commands
echo "Running custom phase..."
```

## Success Criteria
- [Criterion 1]
- [Criterion 2]
EOF
```

### Step 2: Register in Pipeline

Edit `pipeline/execution-flow.prompt.md`:

```python
phases = [
    # ... existing phases ...
    (11, "VERIFICATION", verify_health),
    (12, "CUSTOM", custom_validation),  # ADD THIS
]
```

### Step 3: Add Checkpoint

Edit `pipeline/checkpoints.prompt.md`:

```markdown
| Phase 11→12 | Custom checks pass | Re-run custom |
| Phase 12→END | All criteria met | Escalate |
```

---

## Customizing Cleanup Rules

Edit `cortex-brain/cleanup-rules.yaml`:

```yaml
# Add custom cleanup rule
custom_temp_files:
  enabled: true
  paths:
    - "custom-temp/**"
    - "*.custom-tmp"
  preserve:
    - "custom-temp/important.txt"
  actions:
    - delete
```

---

## Customizing Data Preservation

Edit `core/data-preservation.prompt.md`:

```markdown
## Custom Protected Paths

- [ ] `custom-brain/my-data.yaml` preserved
- [ ] `custom-config/*.json` preserved
```

---

## Customizing Enforcement Rules

Add custom rule to `core/enforcement-rules.prompt.md`:

```markdown
## Rule 11: Custom Validation (NEW)

**✅ REQUIRED:**
- Custom validation passes before Phase 5
- Custom metrics tracked in report
```

---

## Disabling Specific Phases

**Option 1: Skip via command line**
```bash
# Run all phases except Phase 6 (Testing)
system maintenance --skip-phases 6
```

**Option 2: Disable in configuration**

Create `.cortex-maintenance-config.yaml`:

```yaml
phases:
  enabled:
    - 0  # Cleanup
    - 1  # Discovery
    - 2  # Template Validation
    # ... etc
  disabled:
    - 6  # Skip testing phase
```

---

## Customizing Report Template

Edit `pipeline/final-report-template.prompt.md`:

```markdown
## Custom Metrics Section

### Custom Metric 1
- **Value:** {custom_value_1}
- **Threshold:** {threshold}

### Custom Metric 2
- **Value:** {custom_value_2}
- **Status:** {status}
```

---

## Adjusting Thresholds

### Wiring Coverage Threshold

```python
# Default: 100% required
# To allow <100%:
MIN_WIRING_COVERAGE = 95  # 95% minimum
```

### Test Pass Rate Threshold

```python
# Default: 100% required
# To allow failures:
MIN_TEST_PASS_RATE = 95  # 95% minimum
```

### Health Score Threshold

```python
# Default: 95% required
# To adjust:
MIN_HEALTH_SCORE = 90  # 90% minimum
```

---

## Custom Auto-Repair Handlers

Add custom repair logic:

```python
# In custom phase file
def custom_auto_repair(issue):
    """Custom auto-repair logic."""
    if issue.type == "CUSTOM_ERROR":
        # Your repair logic
        fix_custom_error(issue)
        return True
    return False
```

---

## Extending Validation Checks

Add custom validation:

```bash
# In phase-11-verification.prompt.md
echo "Running custom validation..."

# Custom check 1
if ! custom_check_1; then
    echo "❌ Custom check 1 failed"
    HEALTH_ISSUES=$((HEALTH_ISSUES + 1))
fi

# Custom check 2
if ! custom_check_2; then
    echo "❌ Custom check 2 failed"
    HEALTH_ISSUES=$((HEALTH_ISSUES + 1))
fi
```

---

## Environment-Specific Configurations

```yaml
# .cortex-maintenance-config.yaml
environments:
  development:
    phases:
      enabled: [0,1,2,3,4,5,6,7,8,9,10,11]
    thresholds:
      min_health_score: 90
  
  production:
    phases:
      enabled: [0,1,2,3,5,7,9,11]  # Skip some phases
    thresholds:
      min_health_score: 98  # Higher standard
```

---

## Best Practices

1. **Always test custom phases in dry-run mode first**
2. **Document custom rules in metadata/customization-log.md**
3. **Version control custom configurations**
4. **Keep custom phases lightweight (<100 lines)**
5. **Follow existing phase structure for consistency**

---

## Examples

See `../metadata/FULL-IMPLEMENTATION-REFERENCE.md` for complete examples of phase implementations.
