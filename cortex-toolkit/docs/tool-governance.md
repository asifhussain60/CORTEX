# Tool Governance Guide

**Version:** 1.0.0  
**Last Updated:** December 31, 2025  
**Author:** Asif Hussain

This document establishes governance rules and best practices for the CORTEX Toolkit lifecycle management.

---

## Overview

The Tool Governance framework ensures:

- **Quality** - All tools meet standards before release
- **Consistency** - Uniform interfaces and behaviors
- **Maintainability** - Clear ownership and lifecycle
- **Security** - Safe execution and input validation

---

## Tool Lifecycle States

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Draft     │────▶│    Beta     │────▶│   Active    │────▶│ Deprecated  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │   Removed   │
                                                            └─────────────┘
```

### State Definitions

| State | Description | Requirements |
|-------|-------------|--------------|
| **Draft** | Initial development | None |
| **Beta** | Testing phase | Basic tests, documentation draft |
| **Active** | Production ready | Full tests, docs, manifest entry |
| **Deprecated** | Scheduled for removal | Deprecation notice, replacement identified |
| **Removed** | No longer available | Archived, removed from manifest |

---

## Tool Creation

### Prerequisites

Before creating a new tool, you MUST:

1. **Check for duplicates** using RequestAnalyzer
2. **Define capabilities** clearly
3. **Choose appropriate category**
4. **Plan test coverage**

### RequestAnalyzer Check

```python
from core.request_analyzer import RequestAnalyzer, ToolRequest

analyzer = RequestAnalyzer()

request = ToolRequest(
    name="my-new-tool",
    description="Description of what it does",
    capabilities=["capability1", "capability2"]
)

result = analyzer.analyze_request(request)

if result.recommendation_type == RecommendationType.BLOCK:
    # DO NOT CREATE - use existing tool instead
    print(f"Use existing: {result.overlapping_tools}")
elif result.recommendation_type == RecommendationType.WARN:
    # Proceed with caution - document why this is different
    print(f"Similar tools exist: {result.overlapping_tools}")
```

### Required Files

| File | Purpose | Required |
|------|---------|----------|
| `script.py` | Tool implementation | ✅ Yes |
| `test_script.py` | Unit tests | ✅ Yes |
| `wrapper.py` | CLI wrapper (if using cli_wrapper) | Optional |
| `docs/tool-name.md` | Documentation | ✅ Yes |

### Manifest Entry

Every tool must have an entry in `toolkit-manifest.yaml`:

```yaml
- name: my-tool
  command: cortex-my-tool
  script: category/my_tool.py
  description: Clear, concise description
  platforms: [windows, linux, macos]
  requires_admin: false
  execution_method: cli  # or cli_wrapper, copilot_chat
  
  # v2 fields (required for new tools)
  capabilities: [capability1, capability2]
  destructive: false
  idempotent: true
```

### Checklist for New Tools

- [ ] RequestAnalyzer check passed (no BLOCK recommendation)
- [ ] Script implemented with proper error handling
- [ ] Unit tests with >80% coverage
- [ ] Documentation written
- [ ] Manifest entry added with v2 fields
- [ ] Wrapper created (if using cli_wrapper)
- [ ] Security review completed (for destructive tools)

---

## Tool Modification

### Backward Compatibility Rules

1. **No breaking changes** to existing command-line arguments
2. **New arguments** must have defaults
3. **Deprecated arguments** must show warnings for 90 days
4. **Output format changes** require major version bump

### Version Numbering

Follow semantic versioning:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Modification Checklist

- [ ] All existing tests still pass
- [ ] New functionality has tests
- [ ] Documentation updated
- [ ] Version number updated appropriately
- [ ] Changelog updated

---

## Tool Deprecation

### When to Deprecate

- Tool has been superseded by better alternative
- Functionality consolidated into another tool
- One-time utility no longer needed
- Security issues that cannot be fixed

### Deprecation Process

1. **Announce** (Day 0)
   - Add `lifecycle: deprecated` to manifest
   - Add entry to `DEPRECATED-TOOLS.md`
   - Log warning on tool execution

2. **Warning Period** (90 days minimum)
   - Tool remains functional
   - Warning displayed on every use
   - Migration guide available

3. **Removal** (Day 90+)
   - Remove from manifest
   - Archive script to `archives/deprecated/`
   - Update documentation

### Deprecation Notice Format

```python
import warnings
from datetime import datetime

DEPRECATION_DATE = "2025-12-31"
REMOVAL_DATE = "2026-03-31"
REPLACEMENT = "new-tool-name"

warnings.warn(
    f"{__name__} is deprecated as of {DEPRECATION_DATE}. "
    f"It will be removed on {REMOVAL_DATE}. "
    f"Use '{REPLACEMENT}' instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Minimum Deprecation Periods

| Tool Type | Minimum Notice |
|-----------|----------------|
| Core tools | 90 days |
| Utility tools | 60 days |
| One-time migration tools | 30 days |
| Security-critical removals | Immediate |

---

## Tool Removal

### Pre-Removal Checklist

- [ ] Deprecation period completed
- [ ] No active users (check audit logs)
- [ ] Replacement fully functional
- [ ] Migration guide verified
- [ ] Archives created

### Removal Steps

1. **Archive** the tool script:
   ```bash
   cp script.py archives/deprecated/script_YYYYMMDD.py
   ```

2. **Remove** from manifest:
   - Delete entry from `toolkit-manifest.yaml`
   - Update `tool-inventory.yaml` lifecycle to `removed`

3. **Update** documentation:
   - Move from active docs to historical reference
   - Update `DEPRECATED-TOOLS.md`

4. **Clean up** tests:
   - Archive or remove tool-specific tests
   - Update integration tests

---

## Security Requirements

### For All Tools

- Input validation on all arguments
- No arbitrary code execution
- Proper error handling (no stack traces to users)
- Logging of operations

### For Destructive Tools

Destructive tools (`destructive: true`) require:

- [ ] Explicit confirmation prompt (unless `--force`)
- [ ] Dry-run mode (`--dry-run`)
- [ ] Checkpoint creation before execution
- [ ] Audit logging of all operations
- [ ] Admin review before Active status

### For Admin Tools

Tools requiring admin (`requires_admin: true`):

- [ ] Elevated privilege check at startup
- [ ] Clear documentation of what requires admin
- [ ] Minimal admin scope (don't request unnecessary permissions)

---

## Testing Requirements

### Minimum Coverage

| Tool Type | Coverage | Integration Tests |
|-----------|----------|-------------------|
| Core tools | 90% | Required |
| Utility tools | 80% | Recommended |
| Wrappers | 70% | Required |

### Test Types Required

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test with real data
3. **Security Tests** - For tools handling sensitive data
4. **Performance Tests** - For tools with SLA requirements

### No Mocks Policy

Production test suites should use real implementations:

```python
# ❌ Avoid in production tests
@patch('core.toolkit_manager.ToolkitRegistry')
def test_with_mock(self, mock_registry):
    ...

# ✅ Preferred
@pytest.fixture
def real_registry(tmp_path):
    return ToolkitRegistry(tmp_path)

def test_with_real(self, real_registry):
    ...
```

---

## Documentation Requirements

### Required Sections

Every tool documentation must include:

1. **Overview** - What the tool does
2. **Usage** - Command-line syntax
3. **Options** - All arguments documented
4. **Examples** - Real-world usage examples
5. **Exit Codes** - What each code means
6. **See Also** - Related tools

### Documentation Template

```markdown
# Tool Name

Brief description of what the tool does.

## Usage

\`\`\`bash
cortex-tool-name [options] <required-arg>
\`\`\`

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--option` | What it does | value |

## Examples

\`\`\`bash
# Example 1: Basic usage
cortex-tool-name file.txt

# Example 2: With options
cortex-tool-name --verbose --dry-run file.txt
\`\`\`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |

## See Also

- `related-tool` - Description
```

---

## Audit and Compliance

### Audit Trail

All tool executions are logged via `AuditLogger`:

```python
from core.audit_logger import AuditLogger, ExecutionEvent

logger = AuditLogger()

event = ExecutionEvent(
    tool="my-tool",
    args=["--option", "value"],
    status="success",
    exit_code=0,
    duration_ms=150
)

logger.log_execution(event)
```

### Compliance Checks

Run quarterly:

1. **Orphan check** - Tools without scripts
2. **Coverage check** - Tools without tests
3. **Documentation check** - Tools without docs
4. **Deprecation check** - Overdue deprecations

Use `ToolAuditor` for automated checks:

```python
from migration.tool_auditor import ToolAuditor

auditor = ToolAuditor()
report = auditor.audit_all_tools()

print(f"Orphaned tools: {report.orphaned_tools}")
print(f"Untested tools: {report.missing_tests}")
```

---

## Review Process

### New Tool Review

All new tools require review before Active status:

1. **Code Review** - At least one approver
2. **Security Review** - For destructive/admin tools
3. **Documentation Review** - Technical writer or peer
4. **Test Review** - Verify coverage meets requirements

### Change Review

Significant changes require:

1. **Backward Compatibility Check**
2. **Test Verification**
3. **Documentation Update**

---

## Contacts

| Role | Responsibility |
|------|---------------|
| **Toolkit Owner** | Overall toolkit governance |
| **Security Lead** | Security reviews |
| **Documentation Lead** | Doc standards |

---

*Generated by CORTEX Toolkit Manager*  
*Last Updated: December 31, 2025*
