# CORTEX Alignment & Fix Plan - Production Readiness 100%
**Date:** 2026-02-10  
**Authority:** Phase 70 Implementation Alignment Remediation  
**Orchestrator:** cortex-architect.md ✅  
**Status:** COMPREHENSIVE FIX PLAN

---

## 🎯 MISSION OBJECTIVE

**Achieve 100% production readiness through systematic alignment of:**
1. Implementation ↔ Specification (wiring.yaml)
2. Tests ↔ Code (eliminate stubs, enforce TDD)
3. Intelligence Layer ↔ Orchestrators (LENS integration)
4. Orchestrators ↔ Usage (eliminate unused/duplicate)
5. Governance ↔ Enforcement (automated validation)

**Timeline:** 4-6 weeks  
**Success Criteria:** 100% alignment score, 0 blockers, production deployment approved

---

## 📋 PHASE 70 EXECUTION BREAKDOWN

### Stage 1: Gap Triage & Decision Framework (Week 1-2)

#### Task 1.1: Implementation Inventory (3 days)

```bash
# Generate complete implementation inventory
python scripts/audit/generate_implementation_inventory.py \
  --output docs/audit/implementation-inventory-2026-02-10.json \
  --format json

# Output structure:
{
  "orchestrators": [
    {
      "name": "DocumentationOrchestrator",
      "file": "cortex/orchestrators/documentation/orchestrator.py",
      "class": "DocumentationOrchestrator",
      "wired": true,
      "wiring_entry": "domain.DocumentationOrchestrator",
      "mcp_tools": ["cortex_generate_docs"],
      "health_check": "generate_documentation",
      "last_modified": "2026-02-08",
      "test_coverage": 85,
      "usage_count_30d": 145
    },
    ...
  ],
  "unwired": [
    {
      "name": "EnhancedDocumentationOrchestrator",
      "file": "cortex/orchestrators/domain/enhanced_documentation_orchestrator.py",
      "reason": "possible_duplicate",
      "recommendation": "consolidate_with_DocumentationOrchestrator"
    },
    ...
  ],
  "summary": {
    "total_implementations": 113,
    "wired": 73,
    "unwired": 40,
    "duplicates_detected": 2,
    "unused_candidates": 5
  }
}
```

**Script to Create:**

```python
# scripts/audit/generate_implementation_inventory.py
"""
Generate comprehensive implementation inventory for Phase 70.

Scans:
- cortex/orchestrators/**/*.py for Orchestrator classes
- cortex/wiring/specifications/wiring.yaml for wired entries
- MCP logs for usage statistics (last 30 days)
- Test files for coverage metrics
"""
import ast
import yaml
import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class OrchestratorImpl:
    name: str
    file: str
    class_name: str
    wired: bool
    wiring_entry: str = None
    mcp_tools: List[str] = None
    health_check: str = None
    last_modified: str = None
    test_coverage: int = 0
    usage_count_30d: int = 0
    recommendation: str = None

class ImplementationInventory:
    def __init__(self):
        self.implementations: List[OrchestratorImpl] = []
        self.wiring_config = self._load_wiring()
    
    def _load_wiring(self) -> Dict:
        """Load wiring.yaml configuration"""
        with open('cortex/wiring/specifications/wiring.yaml') as f:
            return yaml.safe_load(f)
    
    def scan_implementations(self):
        """Scan all orchestrator implementations"""
        orch_files = Path('cortex/orchestrators').rglob('*.py')
        
        for file in orch_files:
            with open(file) as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if 'Orchestrator' in node.name:
                                impl = self._analyze_implementation(
                                    node.name, str(file)
                                )
                                self.implementations.append(impl)
                except SyntaxError:
                    continue
    
    def _analyze_implementation(self, class_name: str, file_path: str) -> OrchestratorImpl:
        """Analyze single implementation"""
        # Check if wired
        wired = self._check_wired(class_name)
        
        # Get usage statistics
        usage = self._get_usage_stats(class_name)
        
        # Get test coverage
        coverage = self._get_test_coverage(file_path)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            class_name, wired, usage, coverage
        )
        
        return OrchestratorImpl(
            name=class_name,
            file=file_path,
            class_name=class_name,
            wired=wired,
            usage_count_30d=usage,
            test_coverage=coverage,
            recommendation=recommendation
        )
    
    def _check_wired(self, class_name: str) -> bool:
        """Check if orchestrator is wired"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring_config.get('orchestrators', {}).get(category, [])
            for orch in orchestrators:
                if orch['class'] == class_name:
                    return True
        return False
    
    def _get_usage_stats(self, class_name: str) -> int:
        """Get usage statistics from MCP logs"""
        # TODO: Parse MCP logs for last 30 days
        return 0
    
    def _get_test_coverage(self, file_path: str) -> int:
        """Get test coverage for implementation"""
        # TODO: Parse pytest-cov output
        return 0
    
    def _generate_recommendation(
        self, name: str, wired: bool, usage: int, coverage: int
    ) -> str:
        """Generate recommendation for implementation"""
        if not wired and usage == 0:
            return "DELETE: Unwired and unused"
        elif not wired and usage > 0:
            return "WIRE: Active usage detected"
        elif wired and usage == 0:
            return "INVESTIGATE: Wired but no recent usage"
        elif coverage < 80:
            return "IMPROVE_TESTS: Coverage below 80%"
        else:
            return "OK: Properly wired and tested"
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        wired = [impl for impl in self.implementations if impl.wired]
        unwired = [impl for impl in self.implementations if not impl.wired]
        
        return {
            'orchestrators': [asdict(impl) for impl in wired],
            'unwired': [asdict(impl) for impl in unwired],
            'summary': {
                'total_implementations': len(self.implementations),
                'wired': len(wired),
                'unwired': len(unwired),
                'duplicates_detected': self._detect_duplicates(),
                'unused_candidates': self._detect_unused()
            }
        }
    
    def _detect_duplicates(self) -> int:
        """Detect possible duplicate implementations"""
        # TODO: Similarity analysis
        return 0
    
    def _detect_unused(self) -> int:
        """Detect unused orchestrators"""
        return len([impl for impl in self.implementations 
                   if impl.usage_count_30d == 0])

if __name__ == '__main__':
    inventory = ImplementationInventory()
    inventory.scan_implementations()
    report = inventory.generate_report()
    
    with open('docs/audit/implementation-inventory-2026-02-10.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Inventory complete: {report['summary']['total_implementations']} implementations")
    print(f"   Wired: {report['summary']['wired']}")
    print(f"   Unwired: {report['summary']['unwired']}")
```

**Deliverables:**
- [ ] implementation-inventory-2026-02-10.json
- [ ] unwired-implementations-analysis.md
- [ ] duplicate-detection-report.md

#### Task 1.2: Wiring Gap Analysis (2 days)

```bash
# Generate wiring gap report
python scripts/audit/analyze_wiring_gaps.py \
  --inventory docs/audit/implementation-inventory-2026-02-10.json \
  --wiring cortex/wiring/specifications/wiring.yaml \
  --output docs/audit/wiring-gap-analysis-2026-02-10.md

# Categories:
# 1. Unwired but active (HIGH priority - wire immediately)
# 2. Wired but missing implementation (CRITICAL - implement or remove)
# 3. Duplicate functionality (MEDIUM - consolidate)
# 4. Unused orchestrators (LOW - investigate, possibly retire)
```

**Output Format:**

```markdown
# Wiring Gap Analysis - 2026-02-10

## HIGH PRIORITY: Unwired but Active (Wire Immediately)

| Orchestrator | Usage (30d) | Test Coverage | Recommended Action |
|--------------|-------------|---------------|-------------------|
| SemanticSearchOrchestrator | 234 invocations | 92% | Wire to support category |
| VisualProgressReporter | 145 invocations | 88% | Wire to support category |

## CRITICAL: Wired but Missing Implementation

| Wiring Entry | Category | MCP Tool | Recommended Action |
|--------------|----------|----------|-------------------|
| domain.CompanyDomainOrchestrator | domain | cortex_company_domain | Verify implementation path |

## MEDIUM: Duplicate Functionality

| Orchestrator 1 | Orchestrator 2 | Similarity | Recommendation |
|----------------|----------------|------------|----------------|
| DocumentationOrchestrator | EnhancedDocumentationOrchestrator | 85% | Consolidate into DocumentationOrchestrator |

## LOW: Unused Orchestrators (0 usage in 30d)

| Orchestrator | Wired | Last Modified | Recommendation |
|--------------|-------|---------------|----------------|
| SeleniumPlaywrightOrchestrator | Yes | 2025-12-15 | Move to deprecated/, mark for retirement |
```

**Deliverables:**
- [ ] wiring-gap-analysis-2026-02-10.md
- [ ] priority-matrix.csv
- [ ] remediation-recommendations.md

#### Task 1.3: Decision Framework (2 days)

**Decision Matrix:**

```yaml
Implementation State Decision Tree:

1. Unwired + No Usage:
   Decision: DELETE
   Justification: Dead code, no value
   Process: Remove file, commit with AC marker

2. Unwired + High Usage (>50 invocations/30d):
   Decision: WIRE
   Justification: Active usage detected
   Process: Add to wiring.yaml, assign tier/priority, create MCP adapter

3. Unwired + Low Usage (<50 invocations/30d):
   Decision: INVESTIGATE
   Justification: Usage pattern unclear
   Process: Review usage context, decide wire or delete

4. Wired + No Implementation:
   Decision: IMPLEMENT or REMOVE_WIRING
   Justification: Broken wiring entry
   Process: Verify intent, implement or clean wiring.yaml

5. Wired + No Usage:
   Decision: RETIRE
   Justification: Wired but unused
   Process: Move to deprecated/, update docs, remove from wiring in 1 release

6. Duplicate Detected (>80% similarity):
   Decision: CONSOLIDATE
   Justification: CORE-035 violation
   Process: Merge implementations, update references, remove duplicate

7. Low Test Coverage (<80%):
   Decision: IMPROVE_TESTS
   Justification: Quality gate failure
   Process: Add tests to reach 85% minimum, enforce CORE-008
```

**Approval Process:**

```yaml
P0 Decisions (CRITICAL - Block Production):
  - Unwired + High Usage
  - Wired + No Implementation
  - Duplicate + High Usage
  Approval: Team lead + Architect
  Timeline: 24 hours

P1 Decisions (HIGH - Fix in Phase 70):
  - Unwired + Low Usage
  - Wired + No Usage
  - Duplicate + Low Usage
  Approval: Architect
  Timeline: 1 week

P2 Decisions (MEDIUM - Fix in Phase 70 or 71):
  - Low Test Coverage
  - Minor duplicates (<80% similarity)
  Approval: Auto-approved via CI/CD
  Timeline: 2 weeks
```

**Deliverables:**
- [ ] decision-framework.md
- [ ] approval-workflow.md
- [ ] priority-assignments.csv

---

### Stage 2: P0/P1 Remediation (Week 2-4)

#### Task 2.1: Wire Essential Implementations (5 days)

```yaml
For each UNWIRED + HIGH USAGE orchestrator:

1. Create wiring entry:
   File: cortex/wiring/specifications/wiring.yaml
   Category: Determine (core/domain/support)
   Tier: Assign based on dependencies
   Priority: Assign based on usage + complexity

2. Create MCP adapter:
   File: cortex/mcp/adapters/{orchestrator_name}_adapter.py
   Export MCP tool: cortex_{orchestrator_snake_case}

3. Register MCP tool:
   File: cortex/mcp/server.py
   Add to TOOL_REGISTRY

4. Add tests:
   File: tests/orchestrators/test_{orchestrator_name}_wiring.py
   Verify: health_check, MCP adapter, dependency injection

5. Update documentation:
   File: docs/orchestrators/{orchestrator_name}.md
   Include: Purpose, capabilities, MCP tools, examples

6. Commit with AC marker:
   Message: "feat: Wire {OrchestratorName} (AC-PHASE70-WIRE-001)"
```

**Example: Wire SemanticSearchOrchestrator**

```yaml
# Add to wiring.yaml
orchestrators:
  support:
    - name: SemanticSearchOrchestrator
      module: cortex.orchestrators.support.semantic_search
      class: SemanticSearchOrchestrator
      tier: 2
      priority: 145
      dependencies: []
      capabilities:
        - semantic_search
        - embedding_generation
        - similarity_ranking
      health_check: search_semantic
      mcp_adapter: cortex.mcp.adapters.semantic_search_adapter
      mcp_tools:
        - cortex_semantic_search
```

```python
# cortex/mcp/adapters/semantic_search_adapter.py
from cortex.mcp.base import BaseMCPAdapter
from cortex.orchestrators.support.semantic_search import SemanticSearchOrchestrator

class SemanticSearchMCPAdapter(BaseMCPAdapter):
    """MCP adapter for SemanticSearchOrchestrator"""
    
    def __init__(self):
        self.orchestrator = SemanticSearchOrchestrator()
    
    async def cortex_semantic_search(self, query: str, top_k: int = 10) -> dict:
        """
        Perform semantic search across codebase.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            Search results with relevance scores
        """
        return await self.orchestrator.search_semantic(query, top_k)
```

```python
# tests/orchestrators/test_semantic_search_wiring.py
import pytest
from cortex.wiring.registry import OrchestratorRegistry
from cortex.orchestrators.support.semantic_search import SemanticSearchOrchestrator

def test_semantic_search_orchestrator_wired():
    """Verify SemanticSearchOrchestrator is properly wired"""
    registry = OrchestratorRegistry()
    orchestrator = registry.get('SemanticSearchOrchestrator')
    
    assert orchestrator is not None
    assert isinstance(orchestrator, SemanticSearchOrchestrator)

def test_semantic_search_health_check():
    """Verify health check method exists"""
    orchestrator = SemanticSearchOrchestrator()
    
    assert hasattr(orchestrator, 'search_semantic')
    assert callable(orchestrator.search_semantic)

@pytest.mark.asyncio
async def test_semantic_search_mcp_adapter():
    """Verify MCP adapter is functional"""
    from cortex.mcp.adapters.semantic_search_adapter import SemanticSearchMCPAdapter
    
    adapter = SemanticSearchMCPAdapter()
    result = await adapter.cortex_semantic_search("test query", top_k=5)
    
    assert isinstance(result, dict)
    assert 'results' in result
    assert len(result['results']) <= 5
```

**Deliverables:**
- [ ] 10-15 orchestrators wired
- [ ] wiring.yaml updated
- [ ] MCP adapters created
- [ ] Tests passing (100 new tests)
- [ ] Documentation updated

#### Task 2.2: Delete Stub Tests (2 days)

```bash
# Delete tests/_legacy_broken/ (11 files, all stubs)
rm -rf tests/_legacy_broken/
git commit -m "cleanup: Delete legacy broken tests (Phase 70 S2.2)"

# Audit tier2/ for stub tests
python scripts/audit/detect_stub_tests.py \
  --path tests/tier2/ \
  --output docs/audit/stub-tests-tier2.csv

# Delete identified stubs
for file in $(cat docs/audit/stub-tests-to-delete.txt); do
  rm $file
  echo "Deleted stub test: $file"
done

# Verify test suite still passes
python -m pytest tests/ -v --tb=short
```

**Stub Detection Script:**

```python
# scripts/audit/detect_stub_tests.py
"""
Detect stub tests: tests with only pass statements, no assertions.

Patterns detected:
- def test_foo(): pass
- def test_foo(): ... (ellipsis only)
- def test_foo(): NotImplementedError  # Stub
- def test_foo(): pytest.skip("TODO")
"""
import ast
import csv
from pathlib import Path
from typing import List, Tuple

class StubTestDetector(ast.NodeVisitor):
    def __init__(self):
        self.stub_tests: List[Tuple[str, int, str]] = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition"""
        if node.name.startswith('test_'):
            if self._is_stub(node):
                self.stub_tests.append((
                    node.name,
                    node.lineno,
                    self._get_stub_reason(node)
                ))
        self.generic_visit(node)
    
    def _is_stub(self, node: ast.FunctionDef) -> bool:
        """Check if test function is a stub"""
        # Empty function
        if not node.body:
            return True
        
        # Only pass statement
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True
        
        # Only ellipsis
        if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                if node.body[0].value.value is ...:
                    return True
        
        # No assertions
        has_assertion = any(
            isinstance(stmt, ast.Assert) or 
            (isinstance(stmt, ast.Expr) and 
             isinstance(stmt.value, ast.Call) and
             hasattr(stmt.value.func, 'id') and
             'assert' in stmt.value.func.id.lower())
            for stmt in node.body
        )
        
        if not has_assertion:
            return True
        
        return False
    
    def _get_stub_reason(self, node: ast.FunctionDef) -> str:
        """Get reason why test is classified as stub"""
        if not node.body:
            return "EMPTY"
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return "PASS_ONLY"
        if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
            return "ELLIPSIS_ONLY"
        return "NO_ASSERTIONS"

def scan_directory(path: Path) -> List[dict]:
    """Scan directory for stub tests"""
    results = []
    
    for file in path.rglob('test_*.py'):
        with open(file) as f:
            try:
                tree = ast.parse(f.read())
                detector = StubTestDetector()
                detector.visit(tree)
                
                for test_name, lineno, reason in detector.stub_tests:
                    results.append({
                        'file': str(file),
                        'test': test_name,
                        'line': lineno,
                        'reason': reason
                    })
            except SyntaxError:
                continue
    
    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    results = scan_directory(Path(args.path))
    
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'test', 'line', 'reason'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Detected {len(results)} stub tests")
    print(f"   Report: {args.output}")
```

**Deliverables:**
- [ ] tests/_legacy_broken/ deleted (11 files)
- [ ] Stub tests in tier2/ identified (CSV report)
- [ ] Stub tests deleted or fixed
- [ ] Test suite passes (300+ tests remaining)
- [ ] Coverage report updated

#### Task 2.3: Consolidate Duplicate Orchestrators (3 days)

**Example: DocumentationOrchestrator Consolidation**

```yaml
Analysis:
  Primary: DocumentationOrchestrator (cortex/orchestrators/documentation/orchestrator.py)
    - Glassmorphism design system
    - D3.js visualization
    - MCP tool: cortex_generate_docs
    - Wired: Yes (domain category)
    - Usage: 145 invocations/30d
    - Coverage: 85%
  
  Duplicate: EnhancedDocumentationOrchestrator (cortex/orchestrators/domain/enhanced_documentation_orchestrator.py)
    - Additional features: Code examples, API documentation
    - MCP tool: cortex_enhanced_docs (not wired)
    - Wired: Yes (domain category)
    - Usage: 12 invocations/30d
    - Coverage: 72%
  
  Similarity: 85%
  
  Recommendation: MERGE
    - Keep DocumentationOrchestrator as primary
    - Migrate unique features from EnhancedDocumentationOrchestrator
    - Remove EnhancedDocumentationOrchestrator
    - Update tests
    - Update wiring.yaml

Consolidation Plan:
  1. Feature Migration (1 day)
     - Add code examples to DocumentationOrchestrator
     - Add API documentation to DocumentationOrchestrator
     - Test migrated features
  
  2. Reference Updates (1 day)
     - Update MCP adapter to expose new features
     - Update tests to cover new features
     - Ensure backward compatibility
  
  3. Cleanup (1 day)
     - Remove EnhancedDocumentationOrchestrator
     - Remove from wiring.yaml
     - Update documentation
     - Commit with AC marker: "refactor: Consolidate DocumentationOrchestrator (AC-PHASE70-CONSOLIDATE-001)"
```

**Deliverables:**
- [ ] 2-3 duplicate pairs consolidated
- [ ] Features preserved
- [ ] Tests updated (20-30 new tests)
- [ ] Wiring.yaml cleaned
- [ ] Documentation updated

#### Task 2.4: Fix Domain Orchestrators (5 days)

**Target: 2 problematic domain orchestrators**

```yaml
1. DomainOrchestrator:
   Issue: Abstract class incorrectly wired as concrete implementation
   Fix:
     - Mark as abstract in wiring.yaml (is_abstract: true)
     - Remove MCP adapter (abstract classes don't have MCP tools)
     - Update subclasses to wire correctly
     - Add tests for subclass wiring
   
   Subclasses to wire:
     - CompanyDomainOrchestrator (company rules)
     - AnalyticsDomainOrchestrator (metrics)
     - SecuretyDomainOrchestrator (security rules)

2. InquiryOrchestrator:
   Issue: Wired but no active usage detected
   Investigation:
     - Review MCP logs for cortex_inquiry tool
     - Check if feature is documented
     - Verify integration with InteractionOrchestrator
     - Determine if feature should be retired
   
   Options:
     a) If used via InteractionOrchestrator: Document dependency
     b) If not used: Move to deprecated/, plan retirement
     c) If feature incomplete: Complete implementation or remove

3. ConversationOrchestrator:
   Issue: Possible overlap with InteractionOrchestrator
   Analysis:
     - Compare capabilities
     - Review conversation management logic
     - Check if ConversationProtocol is separate concern
   
   Decision:
     - If separate: Document distinct responsibilities
     - If overlap: Consolidate into InteractionOrchestrator
```

**Deliverables:**
- [ ] DomainOrchestrator properly classified as abstract
- [ ] InquiryOrchestrator status determined (keep/retire)
- [ ] ConversationOrchestrator evaluated (keep/consolidate)
- [ ] Tests updated
- [ ] Documentation clarified

---

### Stage 3: P2/P3 Cleanup & Documentation (Week 4)

#### Task 3.1: Orchestrator Catalog Regeneration (2 days)

```bash
# Generate comprehensive orchestrator catalog
python scripts/docs/generate_orchestrator_catalog.py \
  --wiring cortex/wiring/specifications/wiring.yaml \
  --output docs/orchestrators/CATALOG.md

# Output format:
# - Categorized by tier (core/domain/support)
# - Sorted by priority
# - Include capabilities, MCP tools, health checks
# - Link to individual documentation
# - Usage statistics (if available)
```

**Example Output:**

```markdown
# CORTEX Orchestrator Catalog
**Updated:** 2026-02-10  
**Total Orchestrators:** 73  
**Wiring Version:** 2.0

---

## Core Orchestrators (Tier 1) - 11 Total

### InteractionOrchestrator
**Module:** cortex.orchestrators.core.interaction_orchestrator  
**Priority:** 10  
**Capabilities:** comprehension, lens_protocol, challenge_generation, pattern_enforcement  
**MCP Tools:** cortex_interactive_mode  
**Health Check:** execute_turn  
**Dependencies:** None  
**Status:** ✅ Production Ready  
**Usage (30d):** 1,234 invocations  

**Description:**
Main orchestrator for user interaction, comprehension, and turn-based conversation management.

**Documentation:** [InteractionOrchestrator.md](./InteractionOrchestrator.md)

---

### ArchitectureGuard
**Module:** cortex.orchestrators.core.architecture_guard  
**Priority:** 15  
**Capabilities:** architecture_validation, regression_prevention, phase_alignment, brittleness_detection  
**MCP Tools:** cortex_validate_architecture  
**Health Check:** validate_request  
**Dependencies:** None  
**Status:** ✅ Production Ready  
**Usage (30d):** 456 invocations

**Description:**
Pre-implementation validation gate to prevent architectural regression and master plan drift.

**Documentation:** [ArchitectureGuard.md](./ArchitectureGuard.md)

---

[Continue for all 73 orchestrators...]
```

**Deliverables:**
- [ ] CATALOG.md with all 73 orchestrators
- [ ] Individual orchestrator documentation (73 files)
- [ ] Cross-reference links
- [ ] Usage statistics (if available)

#### Task 3.2: Wiring Documentation Update (1 day)

```markdown
# Wiring.yaml Structure Documentation

## Purpose
The wiring.yaml file is the single source of truth (SSOT) for orchestrator registration and configuration in CORTEX.

## Structure

### Analyzers
Lightweight analysis components used by LENS for code intelligence.

### Orchestrators
Categorized into three tiers:
- **core:** Tier 1 orchestrators (11 total) - Essential system orchestration
- **domain:** Domain-specific orchestrators (8 total) - Feature orchestrators
- **support:** Support orchestrators (54 total) - Utility and specialized tasks

### Orchestrator Entry Schema

```yaml
- name: OrchestatorName           # Human-readable name
  module: cortex.path.to.module   # Python module path
  class: OrchestratorClass        # Python class name
  tier: 1                         # 1=core, 2=domain, 3=support
  priority: 10                    # Lower = higher priority
  dependencies:                   # List of orchestrator names
    - DependencyOrchestrator
  capabilities:                   # List of capabilities
    - capability_name
  health_check: method_name       # Health check method
  mcp_adapter: cortex.mcp.adapters.adapter  # MCP adapter module
  mcp_tools:                      # List of MCP tool names
    - cortex_tool_name
  metadata:                       # Optional metadata
    icon: "🔧"
    stages: 4
    intelligence:
      - lens
      - knowledge
```

## Adding a New Orchestrator

1. **Implement the orchestrator:**
   ```python
   # cortex/orchestrators/category/my_orchestrator.py
   from cortex.orchestrators.base import IOrchestrator
   
   class MyOrchestrator(IOrchestrator):
       def health_check_method(self):
           """Health check implementation"""
           pass
   ```

2. **Add wiring entry:**
   ```yaml
   - name: MyOrchestrator
     module: cortex.orchestrators.category.my_orchestrator
     class: MyOrchestrator
     tier: 2
     priority: 150
     dependencies: []
     capabilities:
       - my_capability
     health_check: health_check_method
     mcp_adapter: cortex.mcp.adapters.my_adapter
     mcp_tools:
       - cortex_my_tool
   ```

3. **Create MCP adapter:**
   ```python
   # cortex/mcp/adapters/my_adapter.py
   from cortex.mcp.base import BaseMCPAdapter
   
   class MyMCPAdapter(BaseMCPAdapter):
       async def cortex_my_tool(self):
           orchestrator = self.get_orchestrator('MyOrchestrator')
           return await orchestrator.execute()
   ```

4. **Add tests:**
   ```python
   # tests/orchestrators/test_my_orchestrator_wiring.py
   def test_my_orchestrator_wired():
       registry = OrchestratorRegistry()
       orch = registry.get('MyOrchestrator')
       assert orch is not None
   ```

## Validation Rules

- **No duplicate names:** Each orchestrator must have a unique name
- **Valid module paths:** Module must exist and be importable
- **Valid class names:** Class must exist in module
- **Priority uniqueness:** No two orchestrators should have same priority (within category)
- **Dependency validity:** All dependencies must reference existing orchestrators
- **Health check presence:** Health check method must exist in class
- **MCP adapter validity:** MCP adapter module must exist

## CI/CD Enforcement

The wiring.yaml file is validated on every commit:
- **Pre-commit hook:** Runs wiring validation locally
- **CI pipeline:** Runs comprehensive wiring validation
- **Alignment check:** Verifies all wired orchestrators have implementations
- **Orphan detection:** Detects implementations not in wiring.yaml

See: scripts/ci/validate_wiring.py
```

**Deliverables:**
- [ ] WIRING-DOCUMENTATION.md
- [ ] ADDING-ORCHESTRATORS.md (tutorial)
- [ ] wiring.yaml schema documentation
- [ ] Validation rules documented

#### Task 3.3: Retirement FAQ (1 day)

```markdown
# Orchestrator Retirement FAQ

## Why was [OrchestratorName] removed?

### SeleniumPlaywrightOrchestrator
**Retirement Date:** 2026-02-10  
**Reason:** One-time migration utility, no longer needed  
**Alternative:** Use PlaywrightTestOrchestrator for new test automation  
**Migration Guide:** N/A (migration complete in Phase 52)

### EnhancedDocumentationOrchestrator
**Retirement Date:** 2026-02-10  
**Reason:** Consolidated into DocumentationOrchestrator  
**Alternative:** Use DocumentationOrchestrator (all features migrated)  
**Migration Guide:**
- Old: `cortex_enhanced_docs()`
- New: `cortex_generate_docs(enhanced=True)`

## Can I still use retired orchestrators?

**Short answer:** No. Retired orchestrators are removed from wiring.yaml and may be deleted in future releases.

**Long answer:** Retired orchestrators move through this lifecycle:
1. **Deprecated** (1 release) - Still functional, warnings displayed
2. **Removed from wiring** (next release) - No longer accessible via MCP
3. **Deleted** (2 releases later) - Code removed from repository

If you need a retired orchestrator:
1. Check migration guide for alternative
2. Review git history to restore old implementation
3. Consider if functionality should be added to active orchestrator

## How can I prevent my orchestrator from being retired?

1. **Use it regularly:** Orchestrators with active usage are not retired
2. **Document it well:** Clear documentation prevents misunderstanding
3. **Keep it tested:** Maintain test coverage above 85%
4. **Wire it properly:** Ensure it's in wiring.yaml with correct metadata

## Retirement Criteria

An orchestrator may be retired if:
- **Zero usage:** No MCP invocations in last 60 days
- **Duplicate functionality:** Overlaps significantly with another orchestrator
- **Incomplete:** Implementation is <50% complete and abandoned
- **Obsolete:** Feature no longer needed (e.g., migration utilities)

## Appeal Process

If you believe an orchestrator was retired incorrectly:
1. Open issue on GitHub with justification
2. Include usage statistics (if available)
3. Describe unique value provided
4. Propose alternative if retirement stands

Appeals reviewed within 2 weeks by architecture team.
```

**Deliverables:**
- [ ] RETIREMENT-FAQ.md
- [ ] Individual retirement notices (per orchestrator)
- [ ] Migration guides (where applicable)
- [ ] Appeal process documentation

---

### Stage 4: CI/CD Automation & Continuous Monitoring (Week 5)

#### Task 4.1: Wiring Alignment Check (2 days)

```bash
# Create CI/CD validation script
python scripts/ci/validate_wiring_alignment.py \
  --fail-on-mismatch \
  --report docs/ci/wiring-alignment-report.html

# Exit code 0: 100% alignment
# Exit code 1: Alignment < 100% (CI fails)
```

**Script Implementation:**

```python
# scripts/ci/validate_wiring_alignment.py
"""
CI/CD validation for wiring.yaml ↔ implementation alignment.

Checks:
1. All wired orchestrators have implementations
2. All implementations are wired (or explicitly excluded)
3. Module paths are correct
4. Class names are correct
5. Health check methods exist
6. MCP adapters exist

Exit codes:
0 - 100% alignment
1 - Alignment < 100%
"""
import sys
import yaml
import importlib
from pathlib import Path
from typing import List, Dict, Tuple

class WiringAlignmentValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.wiring = self._load_wiring()
    
    def _load_wiring(self) -> Dict:
        with open('cortex/wiring/specifications/wiring.yaml') as f:
            return yaml.safe_load(f)
    
    def validate(self) -> bool:
        """Run all validation checks"""
        self._validate_implementations_exist()
        self._validate_all_implementations_wired()
        self._validate_module_paths()
        self._validate_class_names()
        self._validate_health_checks()
        self._validate_mcp_adapters()
        
        return len(self.errors) == 0
    
    def _validate_implementations_exist(self):
        """Check all wired orchestrators have implementations"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            
            for orch in orchestrators:
                module_path = orch['module']
                class_name = orch['class']
                
                try:
                    module = importlib.import_module(module_path)
                    if not hasattr(module, class_name):
                        self.errors.append(
                            f"Wired orchestrator {class_name} not found in {module_path}"
                        )
                except ImportError:
                    self.errors.append(
                        f"Module {module_path} not found (wired orchestrator: {class_name})"
                    )
    
    def _validate_all_implementations_wired(self):
        """Check all implementations are wired"""
        # Get all wired orchestrator names
        wired = set()
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            wired.update(orch['class'] for orch in orchestrators)
        
        # Scan implementations
        implementations = self._scan_implementations()
        
        # Check for unwired implementations
        for impl in implementations:
            if impl not in wired:
                # Check if explicitly excluded
                if not self._is_excluded(impl):
                    self.warnings.append(
                        f"Implementation {impl} exists but is not wired"
                    )
    
    def _scan_implementations(self) -> List[str]:
        """Scan all orchestrator implementations"""
        implementations = []
        
        for file in Path('cortex/orchestrators').rglob('*.py'):
            with open(file) as f:
                content = f.read()
                # Simple regex to find Orchestrator classes
                import re
                classes = re.findall(r'class\s+(\w*Orchestrator)\(', content)
                implementations.extend(classes)
        
        return implementations
    
    def _is_excluded(self, class_name: str) -> bool:
        """Check if implementation is explicitly excluded from wiring"""
        excluded = [
            'BaseOrchestrator',
            'IOrchestrator',
            'AbstractOrchestrator',
            # Add more exclusions as needed
        ]
        return class_name in excluded
    
    def _validate_module_paths(self):
        """Validate module paths are correct"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            
            for orch in orchestrators:
                module_path = orch['module']
                
                try:
                    importlib.import_module(module_path)
                except ImportError:
                    self.errors.append(
                        f"Invalid module path: {module_path} (orchestrator: {orch['name']})"
                    )
    
    def _validate_class_names(self):
        """Validate class names exist in modules"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            
            for orch in orchestrators:
                module_path = orch['module']
                class_name = orch['class']
                
                try:
                    module = importlib.import_module(module_path)
                    if not hasattr(module, class_name):
                        self.errors.append(
                            f"Class {class_name} not found in {module_path}"
                        )
                except ImportError:
                    pass  # Already reported in module path validation
    
    def _validate_health_checks(self):
        """Validate health check methods exist"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            
            for orch in orchestrators:
                module_path = orch['module']
                class_name = orch['class']
                health_check = orch.get('health_check')
                
                if not health_check:
                    self.warnings.append(
                        f"No health check defined for {class_name}"
                    )
                    continue
                
                try:
                    module = importlib.import_module(module_path)
                    cls = getattr(module, class_name)
                    
                    if not hasattr(cls, health_check):
                        self.errors.append(
                            f"Health check method {health_check} not found in {class_name}"
                        )
                except (ImportError, AttributeError):
                    pass  # Already reported in other validations
    
    def _validate_mcp_adapters(self):
        """Validate MCP adapters exist"""
        for category in ['core', 'domain', 'support']:
            orchestrators = self.wiring.get('orchestrators', {}).get(category, [])
            
            for orch in orchestrators:
                mcp_adapter = orch.get('mcp_adapter')
                
                if not mcp_adapter:
                    self.warnings.append(
                        f"No MCP adapter defined for {orch['name']}"
                    )
                    continue
                
                try:
                    importlib.import_module(mcp_adapter)
                except ImportError:
                    self.errors.append(
                        f"MCP adapter {mcp_adapter} not found (orchestrator: {orch['name']})"
                    )
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("=" * 70)
        report.append("WIRING ALIGNMENT VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✅ 100% ALIGNMENT - ALL CHECKS PASSED")
        else:
            if self.errors:
                report.append(f"🔴 ERRORS: {len(self.errors)}")
                for error in self.errors:
                    report.append(f"   - {error}")
                report.append("")
            
            if self.warnings:
                report.append(f"⚠️  WARNINGS: {len(self.warnings)}")
                for warning in self.warnings:
                    report.append(f"   - {warning}")
                report.append("")
            
            alignment_score = 100 * (1 - len(self.errors) / (len(self.errors) + len(self.warnings) + 1))
            report.append(f"ALIGNMENT SCORE: {alignment_score:.1f}%")
        
        report.append("=" * 70)
        return "\n".join(report)

if __name__ == '__main__':
    validator = WiringAlignmentValidator()
    is_valid = validator.validate()
    
    print(validator.generate_report())
    
    if not is_valid:
        sys.exit(1)
    else:
        sys.exit(0)
```

**CI/CD Integration:**

```yaml
# .github/workflows/wiring-validation.yml
name: Wiring Alignment Validation

on:
  push:
    branches: [main, CORTEX]
  pull_request:
    branches: [main, CORTEX]

jobs:
  validate-wiring:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install pyyaml
    
    - name: Validate wiring alignment
      run: |
        python scripts/ci/validate_wiring_alignment.py --fail-on-mismatch
    
    - name: Upload report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: wiring-alignment-report
        path: docs/ci/wiring-alignment-report.html
```

**Deliverables:**
- [ ] validate_wiring_alignment.py script
- [ ] CI/CD workflow integration
- [ ] Pre-commit hook for local validation
- [ ] HTML report template

#### Task 4.2: Dashboard Alignment Widget (2 days)

```typescript
// company/dashboards/widgets/alignment-score-widget.ts
/**
 * Real-time wiring alignment score widget for CORTEX dashboard.
 * 
 * Displays:
 * - Current alignment score (0-100%)
 * - Trend (7-day moving average)
 * - Error count
 * - Warning count
 * - Last validation timestamp
 */
import { Widget } from '@cortex/dashboard';
import { WiringAlignmentAPI } from '@cortex/api';

export class AlignmentScoreWidget extends Widget {
  private api: WiringAlignmentAPI;
  
  constructor() {
    super({
      title: 'Implementation Alignment',
      icon: '🔗',
      updateInterval: 300000, // 5 minutes
    });
    
    this.api = new WiringAlignmentAPI();
  }
  
  async fetchData() {
    const data = await this.api.getAlignmentScore();
    return {
      score: data.alignment_score,
      trend: data.trend_7d,
      errors: data.error_count,
      warnings: data.warning_count,
      last_validation: data.last_validation_timestamp,
    };
  }
  
  render(data) {
    const color = this.getColor(data.score);
    const trendIcon = data.trend >= 0 ? '📈' : '📉';
    
    return `
      <div class="alignment-widget">
        <div class="gauge" style="--score: ${data.score}; --color: ${color}">
          <div class="gauge-value">${data.score.toFixed(1)}%</div>
          <div class="gauge-label">Alignment Score</div>
        </div>
        
        <div class="metrics">
          <div class="metric">
            <span class="metric-icon">🔴</span>
            <span class="metric-value">${data.errors}</span>
            <span class="metric-label">Errors</span>
          </div>
          
          <div class="metric">
            <span class="metric-icon">⚠️</span>
            <span class="metric-value">${data.warnings}</span>
            <span class="metric-label">Warnings</span>
          </div>
          
          <div class="metric">
            <span class="metric-icon">${trendIcon}</span>
            <span class="metric-value">${Math.abs(data.trend).toFixed(1)}%</span>
            <span class="metric-label">7-Day Trend</span>
          </div>
        </div>
        
        <div class="last-validation">
          Last validated: ${this.formatTimestamp(data.last_validation)}
        </div>
      </div>
    `;
  }
  
  getColor(score: number): string {
    if (score >= 95) return '#4caf50'; // Green
    if (score >= 85) return '#ff9800'; // Orange
    return '#f44336'; // Red
  }
  
  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  }
}
```

**API Endpoint:**

```python
# cortex/api/endpoints/wiring_alignment.py
from fastapi import APIRouter
from cortex.ci.wiring_validator import WiringAlignmentValidator

router = APIRouter(prefix="/api/wiring")

@router.get("/alignment")
async def get_alignment_score():
    """Get current wiring alignment score"""
    validator = WiringAlignmentValidator()
    validator.validate()
    
    return {
        "alignment_score": validator.get_alignment_score(),
        "trend_7d": validator.get_trend_7d(),
        "error_count": len(validator.errors),
        "warning_count": len(validator.warnings),
        "last_validation_timestamp": validator.get_last_validation_timestamp(),
        "errors": validator.errors,
        "warnings": validator.warnings
    }
```

**Deliverables:**
- [ ] AlignmentScoreWidget implemented
- [ ] API endpoint created
- [ ] Dashboard integration complete
- [ ] Real-time updates working

#### Task 4.3: Monthly Audit Automation (1 day)

```yaml
# .github/workflows/monthly-audit.yml
name: Monthly Wiring Alignment Audit

on:
  schedule:
    - cron: '0 0 1 * *'  # First day of each month at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  monthly-audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyyaml
    
    - name: Run comprehensive audit
      run: |
        python scripts/audit/monthly_wiring_audit.py \
          --output docs/audit/monthly-audit-$(date +%Y-%m).md \
          --send-email
    
    - name: Create issue if alignment < 95%
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: 'Monthly Audit: Wiring Alignment Below 95%',
            body: 'Automated monthly audit detected wiring alignment below 95%. Review required.\n\nSee: docs/audit/monthly-audit-' + new Date().toISOString().slice(0,7) + '.md',
            labels: ['audit', 'P1', 'architecture']
          })
    
    - name: Commit audit report
      run: |
        git config user.name "CORTEX Bot"
        git config user.email "cortex@example.com"
        git add docs/audit/
        git commit -m "audit: Monthly wiring alignment audit $(date +%Y-%m)"
        git push
```

**Monthly Audit Script:**

```python
# scripts/audit/monthly_wiring_audit.py
"""
Comprehensive monthly wiring alignment audit.

Generates:
- Alignment score report
- Trend analysis (vs. previous months)
- Recommendations for improvement
- Identifies new risks
- Email notification to team
"""
import argparse
from pathlib import Path
from datetime import datetime
from cortex.ci.wiring_validator import WiringAlignmentValidator

class MonthlyWiringAudit:
    def __init__(self):
        self.validator = WiringAlignmentValidator()
        self.timestamp = datetime.now()
    
    def run_audit(self):
        """Run comprehensive monthly audit"""
        self.validator.validate()
        
        report = self._generate_report()
        return report
    
    def _generate_report(self) -> str:
        """Generate comprehensive audit report"""
        lines = []
        lines.append(f"# Monthly Wiring Alignment Audit")
        lines.append(f"**Date:** {self.timestamp.strftime('%Y-%m-%d')}")
        lines.append(f"**Alignment Score:** {self.validator.get_alignment_score():.1f}%")
        lines.append("")
        
        lines.append("## Summary")
        lines.append(f"- Errors: {len(self.validator.errors)}")
        lines.append(f"- Warnings: {len(self.validator.warnings)}")
        lines.append(f"- Wired Orchestrators: {self.validator.get_wired_count()}")
        lines.append(f"- Unwired Implementations: {self.validator.get_unwired_count()}")
        lines.append("")
        
        if self.validator.errors:
            lines.append("## Errors")
            for error in self.validator.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        if self.validator.warnings:
            lines.append("## Warnings")
            for warning in self.validator.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        lines.append("## Trend Analysis")
        trend = self.validator.get_trend_90d()
        lines.append(f"- 90-day trend: {trend:+.1f}%")
        lines.append("")
        
        lines.append("## Recommendations")
        if self.validator.get_alignment_score() < 95:
            lines.append("- ⚠️ Alignment below 95% - Phase 70 remediation recommended")
        if len(self.validator.errors) > 0:
            lines.append("- 🔴 Critical errors detected - immediate attention required")
        if self.validator.get_unwired_count() > 5:
            lines.append("- 🟡 High number of unwired implementations - review and wire or delete")
        
        return "\n".join(lines)
    
    def send_email_notification(self, report: str):
        """Send email notification to team"""
        # TODO: Implement email sending
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--send-email', action='store_true')
    args = parser.parse_args()
    
    audit = MonthlyWiringAudit()
    report = audit.run_audit()
    
    # Write report
    Path(args.output).write_text(report)
    
    # Send email if requested
    if args.send_email:
        audit.send_email_notification(report)
    
    # Exit with error if alignment < 95%
    if audit.validator.get_alignment_score() < 95:
        print("❌ Monthly audit failed: Alignment < 95%")
        exit(1)
    else:
        print("✅ Monthly audit passed")
        exit(0)
```

**Deliverables:**
- [ ] monthly-audit.yml workflow
- [ ] monthly_wiring_audit.py script
- [ ] Email notification template
- [ ] GitHub issue automation

---

## 🎓 AGENT ENHANCEMENTS

### 1. Create architecture-integrity-agent.md

**File:** `.github/agents/core/architecture-integrity-agent.md`

```markdown
# Architecture Integrity Agent
**Version:** 1.0  
**Authority:** Phase 70 Implementation Alignment Remediation  
**Purpose:** Automated implementation ↔ specification alignment validation

---

## 🎯 MISSION

Enforce 100% alignment between wiring.yaml and actual orchestrator implementations through:
1. Pre-commit validation
2. CI/CD enforcement
3. Real-time dashboard monitoring
4. Monthly audit automation

---

## 🔍 CAPABILITIES

### 1. Wiring Validation

**Checks:**
- All wired orchestrators have implementations
- All implementations are wired (or explicitly excluded)
- Module paths are correct
- Class names match
- Health check methods exist
- MCP adapters are functional

**Triggers:**
- Pre-commit hook (local)
- CI/CD pipeline (on push/PR)
- Dashboard widget (real-time)
- Monthly audit (scheduled)

### 2. Stub Test Detection

**Patterns Detected:**
- `def test_foo(): pass`
- `def test_foo(): ...`
- `def test_foo(): pytest.skip("TODO")`
- Tests with no assertions

**Actions:**
- Flag in CI/CD
- Block commit if stub tests added
- Generate cleanup report

### 3. Duplicate Detection

**Analysis:**
- Compare orchestrator implementations
- Calculate similarity score
- Identify consolidation candidates

**Threshold:** >80% similarity = duplicate

### 4. Usage Tracking

**Metrics:**
- MCP tool invocations (30-day window)
- Last usage timestamp
- Usage frequency

**Actions:**
- Flag unused orchestrators
- Recommend retirement

---

## 📋 VALIDATION RULES

### Rule 1: 100% Wiring Alignment

```python
IF orchestrator in wiring.yaml:
    THEN implementation must exist
    AND module_path must be correct
    AND class_name must match
    AND health_check method must exist
```

### Rule 2: No Orphan Implementations

```python
IF orchestrator implementation exists:
    THEN (wired in wiring.yaml) OR (explicitly excluded)
    
Excluded patterns:
  - BaseOrchestrator
  - IOrchestrator
  - AbstractOrchestrator
  - *Test*Orchestrator
```

### Rule 3: No Stub Tests

```python
IF test function starts with "test_":
    THEN must have assertions
    OR must have explicit skip reason
    
Forbidden:
  - def test_foo(): pass
  - def test_foo(): ...
```

### Rule 4: Dependency Validity

```python
IF orchestrator declares dependency:
    THEN dependency must be wired
    AND dependency must exist
```

---

## 🚨 ENFORCEMENT ACTIONS

### Pre-Commit (Local)

```bash
# Run validation
python scripts/ci/validate_wiring_alignment.py

# If alignment < 100%:
#   Block commit
#   Display errors
#   Provide fix guidance
```

### CI/CD (Remote)

```yaml
# On push/PR:
#   Run validation
#   If alignment < 100%:
#     Fail pipeline
#     Post comment on PR
#     Block merge
```

### Dashboard (Real-Time)

```typescript
// Update every 5 minutes
//   Display alignment score (gauge)
//   Show error count
//   Show warning count
//   Display trend (7-day)
```

### Monthly Audit (Scheduled)

```yaml
# First day of month:
#   Run comprehensive audit
#   Generate report
#   Send email to team
#   If alignment < 95%:
#     Create GitHub issue
```

---

## 📊 METRICS TRACKED

### Alignment Score

```python
alignment_score = 100 * (
    1 - (errors / (errors + warnings + valid_entries))
)

Thresholds:
  95-100%: Green (Production Ready)
  85-94%: Yellow (Warning)
  <85%: Red (Blocked)
```

### Error Categories

1. **Critical Errors** (block production):
   - Wired but no implementation
   - Invalid module path
   - Invalid class name
   - Missing health check

2. **Warnings** (fix soon):
   - Unwired implementation
   - Low test coverage (<85%)
   - Unused orchestrator (0 invocations/30d)

3. **Info** (monitor):
   - Possible duplicate
   - Deprecated usage

---

## 🔧 INTEGRATION POINTS

### 1. Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/ci/validate_wiring_alignment.py
exit $?
```

### 2. CI/CD Pipeline

```yaml
# .github/workflows/wiring-validation.yml
- name: Validate wiring alignment
  run: python scripts/ci/validate_wiring_alignment.py --fail-on-mismatch
```

### 3. Dashboard API

```python
# cortex/api/endpoints/wiring_alignment.py
@router.get("/alignment")
async def get_alignment_score():
    validator = WiringAlignmentValidator()
    validator.validate()
    return validator.get_score()
```

### 4. MCP Tool

```python
# cortex/mcp/tools/architecture_integrity.py
@mcp_tool
async def cortex_validate_wiring():
    """Validate wiring alignment on-demand"""
    validator = WiringAlignmentValidator()
    return validator.validate_and_report()
```

---

## 📋 USAGE

### Manual Validation

```bash
# Validate wiring alignment
python scripts/ci/validate_wiring_alignment.py

# Generate report
python scripts/audit/generate_wiring_report.py --output report.html

# Detect stub tests
python scripts/audit/detect_stub_tests.py --path tests/
```

### MCP Tool

```python
# Via Copilot Chat
/cortex_validate_wiring

# Via Python
from cortex.mcp.tools import cortex_validate_wiring
result = await cortex_validate_wiring()
```

### Dashboard Widget

```
Navigate to: http://localhost:5000/dashboard
Widget: "Implementation Alignment"
Updates: Every 5 minutes
```

---

## 🎯 SUCCESS CRITERIA

- ✅ Alignment score: 100%
- ✅ Zero critical errors
- ✅ Warnings < 5
- ✅ CI/CD passing
- ✅ Dashboard displaying correct metrics

---

## 📚 REFERENCES

- Phase 70: Implementation Alignment Remediation
- wiring.yaml: Orchestrator wiring specification
- CORE-035: Single Canonical Implementation
- scripts/ci/validate_wiring_alignment.py: Validation script
```

### 2. Enhance cortex-auditor.md

**Add new section:**

```markdown
## 🔗 IMPLEMENTATION ALIGNMENT AUDIT

### Purpose
Verify 100% alignment between wiring.yaml and actual implementations.

### Checks Performed

1. **Wired → Implementation:**
   - All wired orchestrators have implementations
   - Module paths are correct
   - Class names match
   - Health checks exist

2. **Implementation → Wired:**
   - All implementations are wired (or excluded)
   - No orphan implementations
   - No duplicate functionality

3. **Test Quality:**
   - No stub tests
   - AC marker coverage ≥ 80%
   - Test-to-code ratio ≥ 1:1
   - Coverage ≥ 85% per module

4. **Usage Analysis:**
   - MCP invocation frequency
   - Last usage timestamp
   - Retirement candidates identified

### Output Format

```yaml
Alignment Audit Results:
  Overall Score: 98.5%
  Status: ⚠️ YELLOW (Warning)
  
  Critical Errors: 0
  Warnings: 2
    - SemanticSearchOrchestrator not wired (234 invocations/30d)
    - EnhancedDocumentationOrchestrator duplicate detected
  
  Test Quality: 92%
    - Stub tests detected: 0
    - AC coverage: 87%
    - Overall coverage: 89%
  
  Usage Analysis:
    - Active orchestrators: 68/73
    - Unused orchestrators: 5
    - Retirement candidates: 2
  
  Recommendations:
    1. Wire SemanticSearchOrchestrator (HIGH)
    2. Consolidate DocumentationOrchestrator duplicates (MEDIUM)
    3. Investigate unused orchestrators (LOW)
```

### Integration

**Frequency:** Weekly  
**Trigger:** CI/CD + Manual  
**Output:** Markdown report + Dashboard widget

**Command:**
```bash
python scripts/audit/comprehensive_alignment_audit.py \
  --output docs/audit/weekly-alignment-audit.md
```
```

### 3. Enhance cortex-architect.md

**Add Production Readiness section:**

```markdown
## 🚀 PRODUCTION READINESS CHECKLIST

### Phase 70: Implementation Alignment (P0-BLOCKING)

Before production deployment, verify:

#### 1. Wiring Alignment (100% required)

```bash
# Run alignment validation
python scripts/ci/validate_wiring_alignment.py

# Expected output:
✅ 100% ALIGNMENT - ALL CHECKS PASSED
```

**If alignment < 100%:**
- Identify unwired implementations
- Classify: wire, delete, or consolidate
- Execute remediation plan
- Re-validate

#### 2. Test Quality (≥85% coverage, 0 stubs)

```bash
# Run test quality audit
python scripts/audit/test_quality_audit.py

# Expected output:
✅ Test Quality Score: 92%
✅ Stub tests: 0
✅ AC coverage: 89%
✅ Overall coverage: 91%
```

**If quality < 85%:**
- Delete stub tests
- Add missing tests
- Improve AC marker coverage
- Re-validate

#### 3. LENS Integration (E2E verification)

```bash
# Run E2E LENS integration tests
python -m pytest tests/e2e/test_lens_integration.py -v

# Expected output:
✅ 15/15 tests passed
✅ UnifiedIntelligenceProvider active
✅ LENSWarmer invoked on every turn
✅ Company domain rules loaded
```

**If integration fails:**
- Review Phase 65 implementation
- Verify UnifiedIntelligenceProvider usage
- Check LENS analyzer wiring
- Re-run E2E tests

#### 4. Orchestrator Usage (No unused components)

```bash
# Run usage analysis
python scripts/audit/orchestrator_usage_analysis.py --days 30

# Expected output:
✅ 68/73 orchestrators active (93%)
⚠️ 5 orchestrators unused (candidates for retirement)
```

**If unused orchestrators detected:**
- Review usage context
- Decide: keep, retire, or consolidate
- Update documentation
- Re-validate

#### 5. Dashboard Monitoring (Real-time metrics)

```
Navigate to: http://localhost:5000/dashboard

Verify widgets:
  ✅ Implementation Alignment: 100%
  ✅ Test Quality Score: 92%
  ✅ LENS Usage Heatmap: All green
  ✅ Orchestrator Health: All operational
```

**If any widget shows warning:**
- Investigate root cause
- Execute remediation
- Monitor trend
- Re-validate

### Production Deployment Gate

**All checks must pass:**
- [ ] Wiring alignment: 100%
- [ ] Test quality: ≥85%
- [ ] LENS integration: Working
- [ ] Orchestrator usage: Reviewed
- [ ] Dashboard: All green
- [ ] Security scan: Passing
- [ ] Performance benchmarks: Met
- [ ] Documentation: Complete

**Only then:** **PRODUCTION READY** ✅
```

### 4. Enhance cortex-holistic-validator.md

**Add Pre-Implementation Alignment Check:**

```markdown
## 🔗 IMPLEMENTATION ALIGNMENT VALIDATION

### Pre-Implementation Gate

Before creating new orchestrator:

```python
# Step 1: Check if already exists
orchestrator_name = extract_orchestrator_name(request)
existing = check_existing_implementation(orchestrator_name)

if existing:
    CHALLENGE:
    """
    ⚠️ Orchestrator may already exist
    
    Found: {existing.name}
    Wired: {existing.wired}
    Usage: {existing.usage_count_30d} invocations
    Similarity: {similarity_score}%
    
    Options:
    1. Use existing orchestrator (if similarity > 80%)
    2. Enhance existing orchestrator (if similarity 50-80%)
    3. Create new orchestrator (if similarity < 50%)
    
    Recommendation: {recommendation}
    ```
    
    WAIT for user confirmation before proceeding
```

### Wiring Validation

Before implementation:

```python
# Step 2: Validate wiring plan
wiring_plan = {
    'name': orchestrator_name,
    'category': determine_category(),  # core/domain/support
    'tier': determine_tier(),
    'priority': calculate_priority(),
    'dependencies': extract_dependencies(request),
}

validate_wiring_plan(wiring_plan)

# Checks:
#   - No duplicate names
#   - Priority not already taken
#   - Dependencies exist
#   - Module path valid
```

### Test Plan Validation

```python
# Step 3: Verify test coverage plan
test_plan = extract_test_plan(request)

if test_plan.target_coverage < 85:
    CHALLENGE:
    """
    ⚠️ Test coverage below minimum
    
    Target: {test_plan.target_coverage}%
    Minimum: 85%
    
    Increase test coverage plan before implementation.
    """
    BLOCK implementation
```

### LENS Integration Validation

```python
# Step 4: Verify LENS integration plan
lens_plan = extract_lens_integration_plan(request)

if not lens_plan.uses_unified_intelligence_provider:
    CHALLENGE:
    """
    ⚠️ Missing LENS integration
    
    All orchestrators must use UnifiedIntelligenceProvider for:
    - Company domain rules
    - CORTEX best practices
    - LENS code intelligence
    
    Add LENS integration plan before implementation.
    """
    BLOCK implementation
```
```

---

## 🎯 SUCCESS METRICS

### Phase 70 Completion Criteria

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Wiring Alignment | 100% | TBD | ⚪ Pending |
| Test Quality Score | ≥92% | TBD | ⚪ Pending |
| Stub Tests | 0 | ~50 | 🔴 Action Required |
| LENS Integration | E2E passing | Unknown | 🔴 Verification Needed |
| Orchestrator Usage | 95% active | 93% estimated | 🟡 Investigate |
| CI/CD Enforcement | Active | Not yet | ⚪ Pending |
| Dashboard Widgets | Live | Not yet | ⚪ Pending |

### Week-by-Week Targets

**Week 1:**
- [ ] Implementation inventory complete
- [ ] Gap analysis report generated
- [ ] Decision framework established
- [ ] Triage complete

**Week 2:**
- [ ] 10-15 orchestrators wired
- [ ] Stub tests deleted (tests/_legacy_broken/)
- [ ] Duplicate orchestrators identified

**Week 3:**
- [ ] Duplicate orchestrators consolidated (2-3 pairs)
- [ ] Domain orchestrators fixed (2 orchestrators)
- [ ] Test quality improving (stub count decreasing)

**Week 4:**
- [ ] Orchestrator catalog regenerated
- [ ] Wiring documentation updated
- [ ] Retirement FAQ published

**Week 5:**
- [ ] CI/CD validation active
- [ ] Dashboard widgets live
- [ ] Monthly audit automation deployed
- [ ] **PHASE 70 COMPLETE** ✅

---

## 🏁 PRODUCTION DEPLOYMENT TIMELINE

```
Week 0 (Now): AUDIT COMPLETE
  ✅ Comprehensive audit report
  ✅ Gap analysis
  ✅ Fix plan documented

Week 1-2: PHASE 70 S1 (Gap Triage)
  - Implementation inventory
  - Decision framework
  - Priority assignments

Week 2-4: PHASE 70 S2 (Remediation)
  - Wire essential implementations
  - Delete stub tests
  - Consolidate duplicates
  - Fix domain orchestrators

Week 4: PHASE 70 S3 (Documentation)
  - Regenerate catalog
  - Update wiring docs
  - Publish retirement FAQ

Week 5: PHASE 70 S4 (Automation)
  - CI/CD validation
  - Dashboard widgets
  - Monthly audits

Week 6: PHASE 70 VERIFICATION
  - Run all validations
  - Confirm 100% alignment
  - Generate certification report

Week 7-10: PHASE 71 (LENS Framework)
  - LDv1 schema definition
  - Analyzer standardization
  - Incremental extraction
  - Manifest publishing

Week 11-12: PRODUCTION DEPLOYMENT
  - Final verification
  - Security scan
  - Performance benchmarks
  - GO LIVE ✅
```

**Estimated Production Ready Date:** 10-12 weeks from now

---

## 📝 NEXT STEPS

### Immediate Actions (This Week)

1. **Review Audit Report**
   - Team discussion
   - Validate findings
   - Approve Phase 70

2. **Environment Setup**
   - Configure Python environment
   - Install dependencies
   - Verify test collection

3. **Baseline Metrics**
   - Run pytest --collect-only
   - Generate coverage report
   - Document current state

### Phase 70 Kickoff (Next Week)

1. **Task 1.1: Implementation Inventory**
   - Run inventory script
   - Generate JSON report
   - Analyze unwired implementations

2. **Task 1.2: Gap Analysis**
   - Categorize gaps
   - Calculate priority
   - Generate remediation matrix

3. **Task 1.3: Decision Framework**
   - Establish approval process
   - Create decision tree
   - Assign responsibilities

---

**END OF PLAN**

**Generated by:** cortex-architect.md  
**Authority:** Phase 70 Implementation Alignment Remediation  
**Status:** READY FOR EXECUTION  
**Confidence:** HIGH (95%)

**Recommendation:** **PROCEED WITH PHASE 70 IMMEDIATELY**
