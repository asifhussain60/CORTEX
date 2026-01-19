# CORTEX Gap Detection - Design-Build Gap Analysis Prompt

**Role:** Identify and track "Design-Build Gaps" where functionality designed but NOT properly exposed, integrated, or implemented.

---

## Gap Detection Commands

- `/gaps` → Show all design-build gaps
- `/gap <gap-id>` → Details for specific gap
- `/gap-status <component>` → Current exposure/integration status
- `/gap-remediation` → Recommended fixes (new ACs)
- `/gap-audit` → Audit trail of discovered gaps

---

## Gap Categories Table

| Category | Example | Status | Remediation |
|---|---|---|---|
| **Not Exposed** | MCP server tools not exposed | CRITICAL | Wrap with @mcp_tool |
| **Partially Integrated** | Governance rules loaded but not enforced | HIGH | Add enforcement layer |
| **Missing Config** | Claude Desktop config missing | HIGH | Create claude_desktop_config.json |
| **Incomplete Tests** | 85% coverage only | MEDIUM | Add edge case tests |
| **Orphaned Code** | Tools created but not registered | MEDIUM | Register in orchestrator |

---

## Finding Format

```yaml
gap_id: "GAP-XXX-001"
severity: "CRITICAL|HIGH|MEDIUM|LOW"
component: "Component Name"
status: "DESIGNED_NOT_EXPOSED|DESIGNED_NOT_INTEGRATED|INCOMPLETE"

findings:
  - What is NOT working
  - How users are impacted
  - Current state vs. expected

evidence:
  designed_in: "phase-XX.yaml or PHASE-N"
  implementation_loc: "src/path/to/code.py"
  test_coverage: "N%"
  mcp_exposed: true|false

remediation:
  effort: "Xh"
  new_acs: ["AC-REM-001", "AC-REM-002"]
  blocker: true|false
```

---

## Common Gaps Checklist

- [ ] MCP tools not in `@mcp_tool` decorator
- [ ] Required `mcp` package NOT in `requirements.txt`
- [ ] Transport protocol NOT spec-compliant (stdio vs HTTP)
- [ ] Config files missing (claude_desktop_config.json)
- [ ] Tool help/docstrings missing or incomplete
- [ ] Governance rules loaded but NOT enforced
- [ ] Audit trail NOT auto-populated in tests
- [ ] Hash chain NOT verified on startup
- [ ] LENS protocol designed but NOT operationalized
- [ ] Knowledge graph indexed but NOT queryable

---

## Investigation Commands

```bash
# Find MCP tools without decorator
grep -r "@mcp_tool" src/ | cut -d: -f1 | sort -u
# vs
find src/ -name "*.py" -exec grep -l "def.*tool" {} \; | sort -u
# Gap = files in second list not in first

# Find tools not imported in __init__
grep "from.*import" src/__init__.py | wc -l
ls src/tools/*.py | wc -l
# If counts don't match → gap exists

# Verify requirements.txt has MCP
grep "^mcp" requirements.txt
# If not found → CRITICAL gap

# Check config file existence
ls -la ~/.config/Claude/claude_desktop_config.json
# If not found → HIGH gap (for users)
```

---

## Response Format

**✅ Preferred:**
- Gap table (above format)
- 3-5 bullet findings
- Clear remediation path

**❌ Avoid:**
- Lengthy investigation logs
- Code examples
- Narrative explanations
