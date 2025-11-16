# Configuration

Customize CORTEX to match your project needs and workflow preferences.

## Configuration File

CORTEX uses `cortex.config.json` in your project root:

```json
{
  "brain": {
    "conversation_limit": 20,
    "auto_update_threshold": 50,
    "tier3_refresh_interval": 3600,
    "enable_conversation_memory": true,
    "enable_knowledge_learning": true,
    "enable_context_collection": true
  },
  "agents": {
    "enable_brain_protector": true,
    "enforce_tdd": true,
    "require_element_ids": true,
    "semantic_commits": true,
    "challenge_risky_changes": true
  },
  "project": {
    "name": "MyProject",
    "type": "web-application",
    "primary_language": "javascript",
    "test_framework": "playwright",
    "namespaces": ["MyProject", "core"]
  },
  "thresholds": {
    "file_churn_warning": 0.20,
    "min_test_coverage": 0.80,
    "max_feature_time_minutes": 30,
    "min_pattern_confidence": 0.70
  },
  "paths": {
    "brain_directory": "cortex-brain",
    "governance_rules": "governance/rules.md",
    "prompts_directory": "prompts/user"
  }
}
```

---

## Brain Configuration

### Conversation Memory (Tier 1)

```json
"brain": {
  "conversation_limit": 20,
  "enable_conversation_memory": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `conversation_limit` | int | 20 | Max conversations to store (FIFO queue) |
| `enable_conversation_memory` | bool | true | Enable Tier 1 memory system |

**When to adjust:**

- **Increase limit (30-50):** Long-running projects, extensive context needed
- **Decrease limit (10-15):** Short sprints, limited disk space
- **Disable:** Testing only (not recommended for production)

### Auto-Learning (Tier 2)

```json
"brain": {
  "auto_update_threshold": 50,
  "enable_knowledge_learning": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `auto_update_threshold` | int | 50 | Trigger brain update after N events |
| `enable_knowledge_learning` | bool | true | Enable pattern learning |

**When to adjust:**

- **Lower threshold (20-30):** Rapid learning, frequent updates
- **Higher threshold (100+):** Batch learning, less overhead
- **Disable:** Static projects (no pattern learning needed)

### Context Collection (Tier 3)

```json
"brain": {
  "tier3_refresh_interval": 3600,
  "enable_context_collection": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `tier3_refresh_interval` | int | 3600 | Seconds between Tier 3 refreshes |
| `enable_context_collection` | bool | true | Enable development metrics |

**When to adjust:**

- **Shorter interval (1800):** Active development, real-time metrics
- **Longer interval (7200+):** Mature projects, reduce overhead
- **Disable:** Minimal projects (no need for holistic metrics)

---

## Agent Configuration

### Brain Protector (Rule #22)

```json
"agents": {
  "enable_brain_protector": true,
  "challenge_risky_changes": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enable_brain_protector` | bool | true | Enable Rule #22 protection |
| `challenge_risky_changes` | bool | true | Challenge Tier 0 violations |

**When to disable:**

⚠️ **Not recommended!** Brain Protector guards quality.

Only disable for:
- Prototyping (spike branches)
- Learning experiments (throwaway code)
- Migration scripts (temporary work)

### Test-Driven Development

```json
"agents": {
  "enforce_tdd": true,
  "require_element_ids": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enforce_tdd` | bool | true | Require RED → GREEN → REFACTOR |
| `require_element_ids` | bool | true | Enforce ID-based test selectors |

**When to adjust:**

- **`enforce_tdd: false`:** Legacy code (add tests gradually)
- **`require_element_ids: false`:** Non-UI projects

⚠️ **Warning:** Disabling TDD reduces success rate from 96% to 67%

### Commit Handling

```json
"agents": {
  "semantic_commits": true
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `semantic_commits` | bool | true | Use semantic commit messages |

**Semantic format:**
```
feat(scope): Brief description

- Detailed changes
- Test coverage
- Any warnings

Additional context here.
```

**When to disable:**

- Project uses different commit convention
- Manual commit messages preferred

---

## Project Configuration

### Project Metadata

```json
"project": {
  "name": "MyProject",
  "type": "web-application",
  "primary_language": "javascript",
  "test_framework": "playwright",
  "namespaces": ["MyProject", "core"]
}
```

**Options:**

| Setting | Type | Example | Description |
|---------|------|---------|-------------|
| `name` | string | "MyProject" | Project identifier |
| `type` | string | "web-application" | Project category |
| `primary_language` | string | "javascript" | Main programming language |
| `test_framework` | string | "playwright" | Testing framework |
| `namespaces` | array | ["MyProject"] | Knowledge boundaries |

**Project types:**
- `web-application` (React, Vue, Angular)
- `mobile-application` (React Native, Flutter)
- `api-service` (REST, GraphQL)
- `cli-tool` (command-line utilities)
- `library` (npm packages, gems)
- `desktop-application` (Electron, WPF)

**Namespaces:**

Used for **knowledge boundaries** (Tier 2 protection):

```json
"namespaces": ["KSESSIONS", "NOOR", "core"]
```

- Prevents application-specific patterns from contaminating CORTEX core
- Enables multi-project pattern isolation
- See [Knowledge Boundaries](../architecture/protection-system.md#knowledge-boundaries)

---

## Threshold Configuration

### Quality Thresholds

```json
"thresholds": {
  "file_churn_warning": 0.20,
  "min_test_coverage": 0.80,
  "max_feature_time_minutes": 30,
  "min_pattern_confidence": 0.70
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `file_churn_warning` | float | 0.20 | Churn % to flag file as unstable |
| `min_test_coverage` | float | 0.80 | Minimum acceptable coverage (80%) |
| `max_feature_time_minutes` | int | 30 | Warn if feature takes longer |
| `min_pattern_confidence` | float | 0.70 | Minimum confidence for pattern suggestions |

**When to adjust:**

- **Stricter quality (increase):** Production systems, critical applications
- **Relaxed quality (decrease):** Prototypes, learning projects

Example (strict):
```json
"thresholds": {
  "file_churn_warning": 0.15,
  "min_test_coverage": 0.90,
  "max_feature_time_minutes": 20,
  "min_pattern_confidence": 0.80
}
```

---

## Path Configuration

### Directory Structure

```json
"paths": {
  "brain_directory": "cortex-brain",
  "governance_rules": "governance/rules.md",
  "prompts_directory": "prompts/user"
}
```

**Options:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `brain_directory` | string | "cortex-brain" | Brain storage location |
| `governance_rules` | string | "governance/rules.md" | Tier 0 rules file |
| `prompts_directory` | string | "prompts/user" | Entry point location |

**When to change:**

- Monorepo with multiple projects
- Corporate naming conventions
- Custom directory structures

Example (monorepo):
```json
"paths": {
  "brain_directory": "tools/cortex/brain",
  "governance_rules": "tools/cortex/governance/rules.md",
  "prompts_directory": "tools/cortex/prompts"
}
```

---

## Environment-Specific Configuration

### Development vs Production

**dev.cortex.config.json:**
```json
{
  "brain": {
    "conversation_limit": 50,
    "auto_update_threshold": 20
  },
  "agents": {
    "challenge_risky_changes": true
  },
  "thresholds": {
    "min_test_coverage": 0.70
  }
}
```

**prod.cortex.config.json:**
```json
{
  "brain": {
    "conversation_limit": 20,
    "auto_update_threshold": 100
  },
  "agents": {
    "challenge_risky_changes": false
  },
  "thresholds": {
    "min_test_coverage": 0.90
  }
}
```

Load with:
```bash
export CORTEX_CONFIG=prod.cortex.config.json
```

---

## Validation

Test your configuration:

```bash
python test_cortex.py --validate-config
```

Expected output:
```
✅ Configuration valid
   - Brain settings: OK
   - Agent settings: OK
   - Project metadata: OK
   - Thresholds: OK
   - Paths exist: OK

Warnings:
  ⚠️ min_test_coverage below recommended (0.70 < 0.80)
  ⚠️ file_churn_warning high (0.30 > 0.20)

Configuration loaded successfully.
```

---

## Best Practices

### Start Conservative

Use defaults for first project:
- ✅ All protections enabled
- ✅ TDD enforced
- ✅ Semantic commits
- ✅ 20 conversation limit

Adjust after observing patterns.

### Monitor Brain Health

Check Tier 3 metrics weekly:
```markdown
#file:prompts/user/cortex.md

Show brain health status
```

### Version Control

Commit `cortex.config.json`:
```bash
git add cortex.config.json
git commit -m "chore: Update CORTEX configuration"
```

Share team settings, but exclude brain data:
```
# .gitignore
cortex-brain/
```

### Document Customizations

Add comments explaining why:
```json
{
  "brain": {
    // Increased for long-term project context
    "conversation_limit": 50
  },
  "thresholds": {
    // Relaxed during MVP phase
    "min_test_coverage": 0.70
  }
}
```

---

## Advanced Configuration

### Custom Agent Routing

```json
"agents": {
  "custom_intents": {
    "ANALYZE_IMAGE": "screenshot-analyzer.md",
    "COMMIT_CODE": "commit-handler.md"
  }
}
```

### Pattern Weighting

```json
"brain": {
  "pattern_weights": {
    "current_project": 2.0,
    "generic": 1.5,
    "other_projects": 0.5
  }
}
```

### Event Filtering

```json
"brain": {
  "event_filters": {
    "exclude_types": ["debug", "trace"],
    "min_importance": "info"
  }
}
```

See [Advanced Configuration](../guides/advanced-configuration.md) for details.

---

## Troubleshooting

### Configuration Not Loading

```bash
# Check file exists
ls -la cortex.config.json

# Validate JSON syntax
python -m json.tool cortex.config.json

# Check permissions
chmod 644 cortex.config.json
```

### Settings Not Applying

1. Restart Copilot session
2. Clear brain cache:
   ```bash
   python setup_cortex.py --reset-cache
   ```
3. Verify active config:
   ```markdown
   #file:prompts/user/cortex.md
   
   Show active configuration
   ```

### Performance Issues

If CORTEX feels slow:

1. Increase `tier3_refresh_interval` to 7200 (2 hours)
2. Increase `auto_update_threshold` to 100
3. Decrease `conversation_limit` to 10

---

## Next Steps

- **[Understanding the Brain](../guides/brain-system.md)** - Learn how memory works
- **[Agent Workflows](../guides/agent-workflows.md)** - Customize agent behavior
- **[Protection System](../architecture/protection-system.md)** - Configure safeguards

Your configuration shapes CORTEX's behavior. Start with defaults, then optimize for your team! 🎯
