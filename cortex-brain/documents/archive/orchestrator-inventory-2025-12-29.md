# CORTEX Orchestrator Inventory
# Generated: 2025-12-29
# Purpose: Complete list of all orchestrators for intent router wiring

## Primary Orchestrators (MUST be in Intent Router)

1. **Planning System** (`planning-system-4.0-manifest.yaml`)
   - Triggers: `/CORTEX Plan [x]`, `create a plan`, `make a plan`, `plan: [x]`
   - Output: `planning/active/{NAME}/` + 4 subfolders
   - Status: ACTIVE

2. **TDD Mastery** (`tdd-orchestrator-v4-manifest.yaml`)
   - Triggers: `start tdd`, `run tests`, `tdd [x]`
   - Output: Tests in `tests/`
   - Status: ACTIVE

3. **ADO Planning** (`ado-planning-manifest.yaml`)
   - Triggers: `plan ado`, `ado story`, `ado feature`, `create ado work item`
   - Output: ADO work items
   - Status: ACTIVE

4. **Code Sanitization** (`code-sanitization-manifest.yaml`)
   - Triggers: `sanitize`, `make generic`, `anonymize`, `remove company data`
   - Output: Sanitized codebase
   - Status: ACTIVE

5. **Refinement** (`refinement-orchestrator-manifest.yaml`)
   - Triggers: `refine`, `improve cortex`, `enhance system`, `optimize code`
   - Output: 7-phase improvement reports
   - Status: ACTIVE

6. **System Maintenance** (`cortex-maintenance.prompt.md`)
   - Triggers: `system maintenance`, `health check`, `run diagnostics`
   - Output: Health reports in `cortex-brain/health-reports/`
   - Status: ACTIVE

7. **Debug Orchestrator** (`debug-orchestrator-manifest.yaml`)
   - Triggers: `debug`, `fix bug`, `troubleshoot`, `investigate error`
   - Output: Bug reports + fixes
   - Status: ACTIVE

8. **CORTEX Lens** (`cortex-lens-v3-manifest.yaml`)
   - Triggers: `open lens`, `show dashboard`, `analytics`
   - Output: Dashboard visualization
   - Status: ACTIVE

## Secondary Orchestrators (Optional in Intent Router)

9. **Onboarding**
   - Triggers: `onboard`, `getting started`, `learn cortex`, `tutorial`
   - Output: Interactive 6-phase guide
   - Status: ACTIVE (via `onboarding_interactive.py`)

10. **Technical Documentation** (`technical-documentation-orchestrator-manifest.yaml`)
    - Triggers: `generate docs`, `create documentation`, `api docs`
    - Output: Documentation artifacts
    - Status: ACTIVE

## System Operations (CLI-based, not orchestrators)

- `align` - Align system components
- `optimize` - Optimize performance
- `cleanup` - Clean up temporary files
- `healthcheck` - Quick health check

## Intent Router Wiring Requirements

### Minimum Required Entries (8):
1. Planning System
2. TDD Mastery  
3. ADO Planning
4. Code Sanitization
5. Refinement
6. System Maintenance
7. Debug Orchestrator
8. CORTEX Lens / Onboarding / Help

### Current CORTEX.prompt.md Status:
- Has: Planning, TDD, Onboarding, ADO, Sanitization, Refinement, Maintenance, System Ops, Help
- Missing: Debug Orchestrator, CORTEX Lens

### Recommended Intent Router Table:

| Command | Orchestrator | Manifest | Output |
|---------|--------------|----------|--------|
| `/CORTEX Plan [x]`, `create a plan`, `make a plan` | Planning System | `planning-system-4.0-manifest.yaml` | `planning/active/{NAME}/` + 4 subfolders **→ STOPS HERE** |
| `start tdd`, `run tests`, `tdd [x]` | TDD Mastery | `tdd-orchestrator-v4-manifest.yaml` | Tests in `tests/` |
| `debug [issue]`, `fix bug`, `troubleshoot` | Debug Orchestrator | `debug-orchestrator-manifest.yaml` | Bug report + fix |
| `open lens`, `show dashboard`, `analytics` | CORTEX Lens | `cortex-lens-v3-manifest.yaml` | Dashboard visualization |
| `onboard`, `getting started`, `learn cortex` | Onboarding | Via `onboarding_interactive.py` | Interactive 6-phase guide |
| `plan ado`, `ado story`, `ado feature` | ADO Operations | `ado-planning-manifest.yaml` | ADO work items |
| `sanitize`, `make generic`, `anonymize` | Sanitization | `code-sanitization-manifest.yaml` | Sanitized codebase |
| `refine`, `improve cortex`, `optimize code` | Refinement | `refinement-orchestrator-manifest.yaml` | 7-phase improvement |
| `system maintenance`, `health check` | Maintenance | Via `cortex-maintenance.prompt.md` | Health reports |
| `help`, `show commands` | Help | Template-based | Command list |

## copilot-instructions.md Requirements

Must include all primary operations in simplified format:

```markdown
| Intent Pattern | Route To |
|----------------|----------|
| `plan`, `create a plan` | Planning System → folder with 4 subfolders |
| `tdd`, `start tdd`, `run tests` | TDD Orchestrator → RED→GREEN→REFACTOR |
| `debug`, `fix bug` | Debug Orchestrator → investigation + fix |
| `lens`, `dashboard` | CORTEX Lens → visualization |
| `ado`, `ado story` | ADO Operations → work items |
| `sanitize`, `make generic` | Sanitization → 5-phase cleanup |
| `maintenance`, `health check` | Maintenance → 6-phase pipeline |
| `refine`, `improve` | Refinement → 7-phase improvement |
```

## Validation Checklist

- [ ] All 8 primary orchestrators in Intent Router table
- [ ] All command patterns include 3+ trigger variations
- [ ] All manifest paths resolve to existing files
- [ ] Output specifications are clear and actionable
- [ ] Planning commands include "→ STOPS HERE" indicator
- [ ] PLANNING_ISOLATION rule referenced in SKULL section
- [ ] copilot-instructions.md mirrors all primary operations
- [ ] Both files under line limits (200/150)
