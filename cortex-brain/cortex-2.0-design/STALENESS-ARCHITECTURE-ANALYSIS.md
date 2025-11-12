# CORTEX Staleness Architecture Analysis

**Date:** 2025-11-12  
**Issue:** Static template data vs dynamic runtime metrics - staleness problem  
**Severity:** 🔴 CRITICAL - Affects publish design, user trust, system reliability  
**Status:** Analysis Complete - Solution Required

---

## 🎯 The Core Problem

**User's Question:** "Won't these [response templates] become stale over time?"

**Answer:** **YES - This is a critical design flaw affecting multiple layers.**

### What Gets Stale?

1. **Response Templates** - Hardcoded metrics in YAML
2. **Documentation** - Static counts, status claims
3. **Entry Points** - Fixed module counts, implementation percentages
4. **Status Files** - Manual updates required
5. **Configuration Examples** - Outdated paths, settings
6. **Help Text** - Static feature lists

---

## 🔍 Staleness Analysis by Layer

### Layer 1: Response Templates (NEW - Just Added)

**File:** `cortex-brain/response-templates.yaml`

**Staleness Risk:** 🔴 **HIGH**

**What Gets Stale:**
```yaml
brain_performance_session:
  content: |
    **Tier 2: Knowledge Graph (Learned Patterns)**
    • Patterns learned: {{tier2_patterns_count}}  # ✅ Dynamic
    • Average confidence: {{tier2_avg_confidence}}%  # ✅ Dynamic
```

**Wait - this looks dynamic?**

**YES, BUT:** The template **structure** expects these placeholders to be populated by `BrainMetricsCollector`.

**Staleness occurs when:**
- ❌ Database schema changes (new columns)
- ❌ Metric calculation logic changes
- ❌ New tiers added (Tier 4?)
- ❌ Template placeholders don't match collector output

**Example Failure:**
```yaml
# Template expects:
{{tier2_patterns_count}}

# But BrainMetricsCollector returns:
{
  'tier2_total_patterns': 42,  # Different key!
  'tier2_active_patterns': 30,
  'tier2_archived_patterns': 12
}

# Result: {{tier2_patterns_count}} renders as empty string
```

**Publish Impact:**
- User downloads CORTEX
- Templates expect v2.0 database schema
- User has v1.9 database
- **All metrics show as 0 or "Unknown"**

---

### Layer 2: Documentation Modules

**Files:**
- `prompts/shared/story.md`
- `prompts/shared/technical-reference.md`
- `prompts/shared/operations-reference.md`

**Staleness Risk:** 🔴 **HIGH**

**What Gets Stale:**

```markdown
# From technical-reference.md

**Tier 1 API:**
- `add_conversation()` - Add new conversation
- `get_last_20_conversations()` - Retrieve working memory
- `get_token_metrics()` - Get optimization stats

# ❌ STALE if API changes to:
# - `add_conversation_v2()` (new signature)
# - `get_conversations(limit=20)` (parameterized)
# - `get_token_metrics_summary()` (renamed)
```

**Publish Impact:**
- Docs say "use `get_token_metrics()`"
- Actual API is `get_token_metrics_summary()`
- User's code breaks
- **GitHub issues flood in**

---

### Layer 3: Entry Point (CORTEX.prompt.md)

**File:** `.github/prompts/CORTEX.prompt.md`

**Staleness Risk:** 🟡 **MEDIUM-HIGH**

**What Gets Stale:**

```markdown
**Module Status Updates** - 37/86 modules implemented (43%)

# ❌ STALE after every module implementation
# Manual update required

**Test Coverage:** 82 tests passing

# ❌ STALE after every test added
# Manual update required

**Token Optimization:** 97.2% reduction achieved

# ❌ STALE if optimization improves to 98.1%
# Manual update required
```

**Publish Impact:**
- Entry point claims "37/86 modules (43%)"
- Reality: 50/86 modules (58%) implemented
- User thinks CORTEX is less complete than it actually is
- **Trust erosion**

---

### Layer 4: Status Files

**Files:**
- `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD`
- `cortex-brain/CORTEX-2.0-IMPLEMENTATION-STATUS.md`
- `CHANGELOG.md`

**Staleness Risk:** 🔴 **CRITICAL**

**What Gets Stale:**

```markdown
# CORTEX2-STATUS.MD

## Phase 1: Core Modularization
Status: ✅ COMPLETE (37/86 modules implemented)

# ❌ STALE immediately when module 38 is implemented
# No automated tracking

## Phase 5: Response Templates
Status: 🟡 PARTIAL (10/90 templates)

# ❌ STALE when template 11 is added
# Manual count required
```

**Publish Impact:**
- Status file is the "source of truth" for users
- Shows outdated completion percentages
- Users make decisions based on stale data
- **Wrong prioritization, wrong expectations**

---

### Layer 5: Configuration Files

**Files:**
- `cortex.config.example.json`
- `cortex.config.template.json`

**Staleness Risk:** 🟡 **MEDIUM**

**What Gets Stale:**

```json
{
  "tier1_db_path": "cortex-brain/tier1_conversations.db",
  "tier2_db_path": "cortex-brain/knowledge_graph.db",
  
  // ❌ STALE if we add:
  // "tier3_db_path": "cortex-brain/tier3_metrics.db"
  // "tier2_archive_path": "cortex-brain/tier2_archive.db"
  
  "features": {
    "token_optimization": true,
    "pattern_decay": true
    
    // ❌ STALE if we add:
    // "vision_api": true,
    // "auto_cleanup": true
  }
}
```

**Publish Impact:**
- User copies example config
- Missing new required fields
- CORTEX fails to initialize
- **Poor first-run experience**

---

### Layer 6: Help Text & Command Lists

**Files:**
- `response-templates.yaml` (help_table, help_detailed)

**Staleness Risk:** 🔴 **HIGH**

**What Gets Stale:**

```yaml
help_table:
  content: |
    Status  Command        What It Does
    ✅      update story   Refresh CORTEX story documentation
    🔄      setup          Setup/configure environment
    ✅      design sync    Synchronize design with implementation
    
    # ❌ STALE when new command added:
    # ✅      brain metrics  Show performance metrics
    # ✅      pattern decay  Analyze pattern staleness
```

**Publish Impact:**
- User types "help" to discover commands
- New commands not listed
- User doesn't know they exist
- **Features go undiscovered**

---

## 📊 Staleness Impact Matrix

| Layer | Staleness Frequency | User Impact | Publish Risk | Fix Complexity |
|-------|---------------------|-------------|--------------|----------------|
| **Response Templates** | Every DB schema change | 🔴 High (broken metrics) | 🔴 Critical | 🟡 Medium |
| **Documentation** | Every API change | 🔴 High (wrong usage) | 🔴 Critical | 🟡 Medium |
| **Entry Point** | Every module/test | 🟡 Medium (wrong %s) | 🟡 Medium | 🟢 Low |
| **Status Files** | Every implementation | 🟡 Medium (outdated status) | 🟡 Medium | 🟢 Low |
| **Config Files** | Every new feature | 🔴 High (init failures) | 🔴 Critical | 🟡 Medium |
| **Help Text** | Every new command | 🟡 Medium (discovery) | 🟡 Medium | 🟢 Low |

---

## 🔧 Root Cause Analysis

### Why Does Staleness Happen?

**1. Static Data in Dynamic System**
- Templates contain snapshot data
- System evolves continuously
- No automated sync mechanism

**2. Manual Update Burden**
- Developer adds feature
- Forgets to update 6 different documentation files
- No validation to catch it

**3. Publish Amplifies Staleness**
- Dev branch has latest code
- Publish branch has stale docs
- Users get mismatched experience

**4. No Schema Versioning**
- Templates expect v2.0 data format
- User has v1.9 database
- No compatibility layer

---

## 💡 Solution Architecture

### Strategy 1: Hybrid Static/Dynamic Templates

**Concept:** Templates with runtime data injection

**Before (Static):**
```yaml
brain_performance_session:
  content: |
    **Implementation Status:** 37/86 modules (43%)
    # ❌ Stale immediately
```

**After (Dynamic):**
```yaml
brain_performance_session:
  content: |
    **Implementation Status:** {{modules_implemented}}/{{modules_total}} ({{completion_percent}}%)
    # ✅ Calculated at runtime
```

**Implementation:**
```python
# src/metrics/implementation_metrics_collector.py

class ImplementationMetricsCollector:
    def get_module_statistics(self) -> Dict[str, int]:
        """Count actual implemented modules from filesystem."""
        
        # Scan src/ directory
        total_modules = len(list(Path('src').rglob('*.py')))
        
        # Count modules with tests
        implemented = sum(1 for f in Path('tests').rglob('test_*.py'))
        
        return {
            'modules_total': total_modules,
            'modules_implemented': implemented,
            'completion_percent': round((implemented / total_modules) * 100, 1)
        }
```

**Benefits:**
- ✅ Always accurate
- ✅ No manual updates
- ✅ Publish-safe

**Drawbacks:**
- Requires code execution (slower)
- Database dependency

---

### Strategy 2: Versioned Templates

**Concept:** Templates declare required schema version

**Template with Version:**
```yaml
brain_performance_session:
  schema_version: "2.0"
  required_fields:
    - tier1_conversations_count
    - tier2_patterns_count
    - tier3_commits_count
  
  fallback_template: brain_performance_legacy
  
  content: |
    {{#if schema_compatible}}
      # Render v2.0 template
    {{else}}
      # Render fallback
    {{/if}}
```

**Version Check:**
```python
class TemplateRenderer:
    def render(self, template: Template, context: Dict) -> str:
        # Check schema compatibility
        if template.schema_version > context.get('schema_version'):
            # Use fallback template
            fallback = self.load_template(template.fallback_template)
            return self.render(fallback, context)
        
        # Render normally
        return self._substitute_placeholders(template.content, context)
```

**Benefits:**
- ✅ Backward compatible
- ✅ Graceful degradation
- ✅ Clear versioning

**Drawbacks:**
- More complex
- Requires version tracking

---

### Strategy 3: Generated Documentation

**Concept:** Docs generated from code/DB at publish time

**Implementation:**
```python
# scripts/cortex/generate-publish-docs.py

def generate_implementation_status():
    """Generate status.md from actual codebase scan."""
    
    # Scan actual implementation
    stats = {
        'modules': count_modules(),
        'tests': count_tests(),
        'templates': count_templates(),
        'operations': count_operations(),
    }
    
    # Render template
    template = env.get_template('status.md.j2')
    content = template.render(**stats)
    
    # Write to publish branch
    Path('publish/CORTEX/STATUS.md').write_text(content)

# Run automatically during publish
```

**Benefits:**
- ✅ Always accurate at publish time
- ✅ No manual updates
- ✅ Can't forget to update

**Drawbacks:**
- Publish-time only (dev branch still manual)
- Requires build step

---

### Strategy 4: Runtime Metrics Only

**Concept:** No static metrics - all calculated on demand

**Template (No Static Data):**
```yaml
brain_performance_session:
  content: |
    **Brain Performance - Current Session**
    
    {{#tier1_available}}
    **Tier 1:** {{tier1_conversations_count}} conversations
    {{/tier1_available}}
    {{^tier1_available}}
    **Tier 1:** Not initialized
    {{/tier1_available}}
```

**Collector Always Queries:**
```python
def get_brain_performance_metrics(self) -> Dict[str, Any]:
    """Always query live data - never cache."""
    
    return {
        'tier1_available': self.tier1_db.exists(),
        'tier1_conversations_count': self._query_tier1() if self.tier1_db.exists() else 0,
        # ... all metrics calculated fresh
    }
```

**Benefits:**
- ✅ Never stale
- ✅ Always reflects reality
- ✅ Simple mental model

**Drawbacks:**
- ❌ Slower (database queries every time)
- ❌ Requires working brain (fails if DB corrupted)

---

## 🎯 Recommended Solution: Hybrid Approach

### Phase 1: Immediate (This Week)

**1. Add Schema Version to Templates**
```yaml
# Every template gets:
schema_version: "2.0.0"
last_updated: "2025-11-12"
```

**2. Add Version Check to BrainMetricsCollector**
```python
class BrainMetricsCollector:
    SCHEMA_VERSION = "2.0.0"
    
    def get_brain_performance_metrics(self) -> Dict[str, Any]:
        metrics = {
            'schema_version': self.SCHEMA_VERSION,
            # ... rest of metrics
        }
        return metrics
```

**3. Add Fallback Templates**
```yaml
brain_performance_legacy:
  # Minimal template for older schemas
  content: |
    **Brain Performance**
    Schema version mismatch. Please update CORTEX.
```

---

### Phase 2: Short-Term (Next Sprint)

**4. Automated Doc Generation**
```bash
# scripts/cortex/sync-docs.py

# Run before every publish:
python scripts/cortex/sync-docs.py \
  --scan-implementation \
  --update-templates \
  --verify-no-staleness
```

**5. Staleness Detection**
```python
# tests/staleness/test_documentation_sync.py

def test_entry_point_module_count():
    """Verify entry point shows correct module count."""
    
    # Count actual modules
    actual = count_modules()
    
    # Read claimed count from CORTEX.prompt.md
    claimed = parse_module_count_from_entry_point()
    
    assert actual == claimed, f"Entry point claims {claimed}, actual is {actual}"
```

---

### Phase 3: Long-Term (CORTEX 2.2)

**6. Runtime Metrics Cache**
```python
# src/metrics/metrics_cache.py

class MetricsCache:
    """Cache metrics with TTL."""
    
    def get_brain_metrics(self, ttl_seconds=300):
        # Cache for 5 minutes
        if self.is_cached('brain_metrics', ttl_seconds):
            return self.cached_metrics['brain_metrics']
        
        # Refresh from DB
        fresh = BrainMetricsCollector().get_brain_performance_metrics()
        self.cache('brain_metrics', fresh)
        return fresh
```

**7. Template Validation CI**
```yaml
# .github/workflows/template-validation.yml

name: Validate Templates

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check Template Placeholders
        run: |
          python scripts/validate-templates.py \
            --check-placeholders \
            --verify-collectors \
            --fail-on-mismatch
```

---

## 📋 Affected Files Audit

### Files Requiring Immediate Attention:

**Response Templates:**
- ✅ `cortex-brain/response-templates.yaml` - Add schema version
- ✅ `src/metrics/brain_metrics_collector.py` - Add version tracking

**Documentation:**
- 🟡 `prompts/shared/technical-reference.md` - API signatures (manual review)
- 🟡 `prompts/shared/operations-reference.md` - Command list (auto-generate)
- 🟡 `.github/prompts/CORTEX.prompt.md` - Module counts (auto-calculate)

**Status Files:**
- 🔴 `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` - Progress bars (auto-generate)
- 🔴 `cortex-brain/CORTEX-2.0-IMPLEMENTATION-STATUS.md` - Completion % (auto-calculate)

**Configuration:**
- 🟡 `cortex.config.example.json` - Schema validation needed
- 🟡 `cortex.config.template.json` - Version tracking needed

**Help Text:**
- 🔴 Response templates (help_table, help_detailed) - Auto-generate from plugins

---

## 🚨 Critical Publish Implications

### Scenario: User Downloads Published CORTEX

**Without Staleness Fix:**
1. User installs CORTEX v2.0 from publish branch
2. Entry point claims "43% complete"
3. User queries "how did the brain do?"
4. Template expects v2.0 schema
5. User has fresh DB (v2.0 schema ✅)
6. Metrics show correctly **THIS TIME**
7. **Next week:** User updates CORTEX to v2.1
8. Templates still expect v2.0 schema
9. Database now has v2.1 schema (new columns)
10. **ALL METRICS BREAK** 💥

**With Staleness Fix:**
1. Template declares schema: v2.0
2. Collector returns: schema v2.1
3. Version mismatch detected
4. Fallback template used
5. User sees: "Update templates for v2.1 metrics"
6. **Graceful degradation** ✅

---

## 🎯 Action Items (Priority Order)

### CRITICAL (Do This Week):
1. ✅ **Add schema versioning** to templates and collectors
2. ✅ **Create fallback templates** for version mismatches
3. ✅ **Add staleness tests** to catch documentation drift
4. ✅ **Document staleness strategy** in architecture

### HIGH (Next Sprint):
5. 🔄 **Automated doc generation** for publish
6. 🔄 **CI validation** for template placeholders
7. 🔄 **Metrics cache** with TTL

### MEDIUM (CORTEX 2.2):
8. ⏸️ **Runtime-only metrics** (no static data)
9. ⏸️ **Auto-updating help text** from plugin registry
10. ⏸️ **Schema migration tools** for database evolution

---

## 💡 Key Insights

### What We Learned:

1. **Static data is a liability** in evolving systems
2. **Publish amplifies staleness** - stale docs get frozen
3. **Templates need versioning** just like APIs
4. **Documentation is code** - should be tested, validated, generated
5. **Manual updates don't scale** - automation is mandatory

### Design Principles Going Forward:

- **Prefer runtime over static** - Calculate, don't hardcode
- **Version everything** - Templates, schemas, configs
- **Validate in CI** - Catch staleness before publish
- **Graceful degradation** - Never break, fall back safely
- **Generate documentation** - Truth from code, not markdown

---

## 📊 Staleness Prevention Checklist

When adding any new feature:

- [ ] Update `BrainMetricsCollector` to include new metrics
- [ ] Increment schema version if data format changes
- [ ] Add fallback template for old schema versions
- [ ] Update automated doc generation script
- [ ] Add staleness test for new documentation
- [ ] Verify template placeholders match collector output
- [ ] Test against both old and new database schemas
- [ ] Update CI validation rules

**Make this checklist mandatory in PR template!**

---

## 🔮 Future Vision: Self-Documenting CORTEX

**Long-term goal:** CORTEX that documents itself

```python
# Every module declares its own metadata
class BrainMetricsCollector:
    __cortex_metadata__ = {
        'category': 'metrics',
        'status': 'implemented',
        'schema_version': '2.0.0',
        'metrics_provided': [
            'tier1_conversations_count',
            'tier2_patterns_count',
            # ...
        ]
    }

# Documentation auto-generated from metadata
>>> generate_docs()
✅ Scanned 86 modules
✅ Found 50 implemented (58%)
✅ Generated technical-reference.md
✅ Updated CORTEX.prompt.md
✅ No staleness detected
```

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Priority:** 🔴 CRITICAL - Fix before next publish  
**Decision:** Implement Phase 1 (schema versioning) immediately
