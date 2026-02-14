# CORTEX Directive Protocol (CDP)

**Version:** 1.0.0 | **Status:** Foundation Complete | **Date:** 2026-02-06

---

## 🎯 Problem Statement

**Before CDP:**
- `cortex-architect.prompt.md`: 2,948 lines
- Token waste: ~12,000 tokens loaded every request
- Maintenance overhead: Freeform Markdown, no validation
- Duplication: Copy-paste between prompts/agents
- No versioning: Breaking changes without migration paths

**After CDP:**
- `architect.directive.yaml`: 400 lines (86% reduction)
- Token efficiency: 150-500 tokens (context-aware pruning)
- Machine-first: YAML + JSON Schema validation
- DRY: Composition via `inherits_from`
- Semantic versioning: Deprecation paths, backward compatibility

---

## 📐 Architecture

```
cortex-registry/_cortex-master/
├── directives/
│   ├── schema.json                     # JSON Schema validator
│   ├── core/
│   │   ├── architect.directive.yaml    # ✅ POC complete
│   │   ├── cortex.directive.yaml       # ⏭️ Planned
│   │   └── response-format.directive.yaml
│   ├── agents/
│   │   ├── core/
│   │   │   └── {agent}.directive.yaml  # 11 agents
│   │   └── domain/
│   │       └── {agent}.directive.yaml
│   └── knowledge/
│       └── {topic}.directive.yaml
├── meta/
│   ├── directive-index.yaml            # O(1) lookup registry
│   ├── directive-protocol.yaml         # This architecture
│   └── schema-versions.yaml
└── docs/
    └── directives/
        └── {name}.md                   # Auto-generated, never edit
```

---

## 🚀 Usage

### Load Directive (Python)

```python
from cortex.brain.core.directive_loader import DirectiveLoader

loader = DirectiveLoader()

# Load full directive
directive = loader.load_directive('architect')

# Context-aware pruning (60-80% token reduction)
directive = loader.load_directive(
    'architect',
    context_hints=['AUDIT', 'DESIGN']
)

# Specific version
directive = loader.load_directive('architect', version='2.0.0')
```

### MCP Tool (Production)

```bash
# Via MCP gateway
curl http://localhost:8000/directives/architect

# With context hints
curl http://localhost:8000/directives/architect?context=AUDIT,DESIGN

# Specific version
curl http://localhost:8000/directives/architect/v2.0.0
```

### Validate Directive

```python
from cortex.brain.core.directive_loader import DirectiveLoader

loader = DirectiveLoader()
result = loader.validate_directive(
    Path('directives/core/architect.directive.yaml')
)

print(result)
# {'valid': True, 'errors': [], 'warnings': []}
```

### Compile with Inheritance

```python
# Resolve 'inherits_from' chains
compiled = loader.compile_directive('architect', format='yaml')

# Generate human docs
markdown = loader.compile_directive('architect', format='markdown')
```

---

## 📊 Directive Schema

**Required Fields:**

```yaml
metadata:
  id: cortex://directives/{name}/v{version}
  version: semver (major.minor.patch)
  replaces: [list of deprecated files]

context:
  intent_patterns: [IMPLEMENT, FIX, AUDIT, ...]
  token_budget: integer (100-50000)

capabilities:
  - id: unique_identifier
    description: "What this capability does"
    constraints: [operational rules]
    examples: [input/output pairs]
    mcp_tools: [tools used]

constraints:
  tier0_rules: [CORE-xxx rules]
  governance: [enforcement rules]

execution:
  phases: [ordered steps]
  success_criteria: [metrics]
```

**See `directives/schema.json` for complete JSON Schema.**

---

## 🛡️ Governance Rules

### ARCH-050: Directive-First Prompts
- ❌ **BLOCK:** New `.prompt.md` files
- ✅ **REQUIRE:** `.directive.yaml` with schema validation

### ARCH-051: Agent Specification Format
- ❌ **BLOCK:** Agent docs >500 lines
- ✅ **REQUIRE:** Structured YAML (capabilities/constraints/examples)

### ARCH-052: Directive Composition
- ❌ **BLOCK:** >70% similarity (copy-paste)
- ✅ **REQUIRE:** Use `inherits_from` or `extends`

### ARCH-053: Token Budget Enforcement
- ⚠️ **WARN:** Actual usage > declared budget * 1.2
- 📊 **MONITOR:** Token usage metrics

### ARCH-054: Breaking Change Gating
- ❌ **BLOCK:** Version bump without `replaces` metadata
- ✅ **REQUIRE:** 30-day deprecation window

---

## 📈 Token Optimization

| Strategy | Reduction | Example |
|----------|-----------|---------|
| **Context-Aware Pruning** | 60-80% | Load only AUDIT capability (150 tokens vs 500) |
| **Lazy Agent Loading** | 70-85% | AUDIT mode = 2 agents (300 tokens vs 1800) |
| **Inheritance Flattening** | 30-50% | Compile-time resolution, cache result |
| **LRU Caching** | 70% hit rate | 5min TTL, invalidate on git pull |

**Total Impact:** 75-86% token reduction on typical requests

---

## 🔄 Migration Plan

| Phase | Status | Target | Tasks |
|-------|--------|--------|-------|
| **Phase 1: Foundation** | ✅ Complete | 2026-02-06 | Schema, index, POC, loader |
| **Phase 2: Core Prompts** | ⏭️ Planned | 2026-02-13 | CORTEX.prompt.md, response-format |
| **Phase 3: Agents** | ⏭️ Planned | 2026-02-20 | 11 core agents, AGENT-INDEX |
| **Phase 4: Knowledge** | ⏭️ Planned | 2026-02-27 | Best practices, company domains |
| **Phase 5: Enforcement** | ⏭️ Planned | 2026-03-06 | CI/CD, metrics, pre-commit hooks |

**Success Criteria:**
- ✅ 70%+ token reduction
- ✅ <50ms loading (p95)
- ✅ 100% schema compliance
- ✅ 90% migration coverage by Q2 2026

---

## 🔧 Integration

### MCP Gateway
```yaml
Endpoints:
  GET /directives/{name}           # Load latest
  GET /directives/{name}/{version} # Load specific version
  POST /directives/validate        # Schema validation
  GET /directives/index            # Full registry
```

### EnforcementOrchestrator
- **DirectiveComplianceAgent** (8th agent)
- Pre-execution: Validate directive exists, not deprecated
- Runtime: Monitor token usage vs budget
- Post-execution: Validate success criteria

### Documentation
- **Auto-generation:** Pre-commit hook
- **Input:** `directives/**/*.directive.yaml`
- **Output:** `docs/directives/{name}.md`
- **Never edit:** Markdown is generated, YAML is source of truth

---

## 📚 Examples

### POC Migration: cortex-architect

**Before:** `.github/prompts/cortex-architect.prompt.md` (2,948 lines)  
**After:** `directives/core/architect.directive.yaml` (400 lines)  
**Reduction:** 86%

**Capabilities Extracted:**
1. `hexa_mode_operation` — 6 modes (PRE-FLIGHT, AUDIT, DESIGN, PLAN, DIGEST, INTERACTIVE, META-AUDIT)
2. `dual_mode_audit_design` — Read-only vs implementation
3. `p0_p1_p2_classification` — Issue severity scoring
4. `token_optimization` — EXIT GATE integration
5. `plan_registry_integration` — ROI-based phase prioritization
6. `digest_mode` — Chat session learning extraction
7. `interactive_mode` — Exploratory Q&A
8. `meta_audit_mode` — Self-improvement analysis
9. `pre_flight_check` — Auto-upgrade detection

**Token Cost:** 500 tokens (declared) vs ~12,000 (original prompt)

---

## 🎬 Quick Start

### 1. Validate Existing Directive
```bash
python -c "
from cortex.brain.core.directive_loader import DirectiveLoader
loader = DirectiveLoader()
result = loader.validate_directive(
    Path('cortex-registry/_cortex-master/directives/core/architect.directive.yaml')
)
print('Valid!' if result['valid'] else f\"Errors: {result['errors']}\")
"
```

### 2. Load and Inspect
```bash
python -c "
from cortex.brain.core.directive_loader import DirectiveLoader
import yaml
loader = DirectiveLoader()
directive = loader.load_directive('architect', context_hints=['AUDIT'])
print(yaml.dump(directive, default_flow_style=False))
"
```

### 3. Measure Token Reduction
```bash
# Before: Count lines in original prompt
wc -l .github/prompts/cortex-architect.prompt.md

# After: Load directive and estimate tokens
python -c "
from cortex.brain.core.directive_loader import DirectiveLoader
loader = DirectiveLoader()
directive = loader.load_directive('architect', context_hints=['AUDIT'])
print(f'Tokens: {loader._estimate_tokens(directive)}')
"
```

---

## 🔗 References

- **Schema:** `cortex-registry/_cortex-master/directives/schema.json`
- **Index:** `cortex-registry/_cortex-master/meta/directive-index.yaml`
- **Protocol:** `cortex-registry/_cortex-master/meta/directive-protocol.yaml`
- **POC:** `cortex-registry/_cortex-master/directives/core/architect.directive.yaml`
- **Loader:** `cortex/brain/core/directive_loader.py`

---

## 🤝 Contributing

### Create New Directive

1. **Define in YAML:**
   ```yaml
   metadata:
     id: cortex://directives/myfeature/v1.0.0
     version: 1.0.0
     replaces: []
   # ... rest of schema
   ```

2. **Validate:**
   ```bash
   python -c "
   from cortex.brain.core.directive_loader import DirectiveLoader
   loader = DirectiveLoader()
   result = loader.validate_directive(Path('directives/core/myfeature.directive.yaml'))
   print(result)
   "
   ```

3. **Register in Index:**
   ```yaml
   # meta/directive-index.yaml
   directives:
     myfeature:
       id: cortex://directives/myfeature/v1.0.0
       version: 1.0.0
       path: directives/core/myfeature.directive.yaml
   ```

4. **Auto-Generate Docs:**
   ```bash
   python -c "
   from cortex.brain.core.directive_loader import DirectiveLoader
   loader = DirectiveLoader()
   md = loader.compile_directive('myfeature', format='markdown')
   with open('docs/directives/myfeature.md', 'w') as f:
       f.write(md)
   "
   ```

---

**Status:** Foundation complete, Phase 2 ready to begin.
