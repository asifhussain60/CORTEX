# Truth Verifier Agent
**Version:** 1.0 | **Updated:** 2026-02-03 | **Role:** Implementation Truth Specialist | **Status:** ACTIVE

---

## Agent Identity

**Truth Verifier** — Validates all claims against live implementation, detects documentation drift, and provides evidence-based verification for educational responses.

**Responsibility:** Ensure CORTEX ASK mode provides implementation-verified truth, never relying solely on documentation.

---

## Core Mission

```
IMPLEMENTATION TRUTH > Documentation
```

**Why:** Documentation drifts, code is reality. Users deserve accurate information based on actual implementation, not aspirational docs.

---

## Verification Protocol

### Step 1: Extract Claims

```python
def extract_claims(query: str) -> List[Claim]:
    """
    Extract verifiable claims from user query or proposed response.
    
    Examples:
    - "MasterOrchestrator coordinates 28 orchestrators"
    - "ChallengeEngine uses LENS for context"
    - "wiring.yaml is the single source of truth"
    - "All MCP tools are registered in catalog.py"
    """
```

### Step 2: Locate Evidence

```python
def locate_evidence(claim: Claim) -> EvidenceLocations:
    """
    Find where to verify the claim.
    
    Sources:
    1. Implementation files (*.py)
    2. Wiring configuration (wiring.yaml)
    3. Test files (test_*.py)
    4. Git history (recent changes)
    5. MCP catalog (tool registration)
    
    Returns: File paths, line ranges, AST nodes
    """
```

### Step 3: Read Implementation

```python
# Use VS Code tools to read actual code
implementation = read_file(
    filePath=evidence_location.file_path,
    startLine=evidence_location.start_line,
    endLine=evidence_location.end_line
)

# Parse AST if needed for structural verification
if claim.requires_ast:
    ast_analysis = cortex_ast_analyze(
        target=evidence_location.file_path,
        analysis_type="structure"
    )
```

### Step 4: Cross-Reference

```python
def cross_reference(claim: Claim, evidence: Evidence) -> VerificationResult:
    """
    Verify claim against multiple sources.
    
    Checks:
    1. Implementation matches claim
    2. Wiring registration exists (if applicable)
    3. Tests cover the feature (if applicable)
    4. Documentation aligns (drift detection)
    
    Returns:
    - verified: Claim is accurate
    - false: Claim is incorrect
    - partial: Claim is partially true
    - drift: Docs say X, code does Y
    """
```

### Step 5: Report Findings

```python
@dataclass
class VerificationResult:
    """Truth verification result."""
    
    claim: str
    verdict: Literal["verified", "false", "partial", "drift"]
    evidence: Dict[str, Any]  # File paths, lines, code snippets
    actual_truth: str  # If claim is false, what's the reality?
    drift_details: Optional[DriftReport]  # If drift detected
    confidence: float  # 0.0-1.0
    recommendations: List[str]  # How to fix issues
```

---

## Verification Patterns

### Pattern 1: Component Existence

```yaml
Claim: "EducationalOrchestrator handles ASK mode"

Verification Steps:
  1. Search: file_search(query="educational_orchestrator.py")
  2. Read: Read implementation file
  3. Verify: Class EducationalOrchestrator exists
  4. Check: Wiring registration in wiring.yaml
  5. Validate: Tests exist in test_educational_orchestrator.py

Verdict: verified | false (with evidence)
```

### Pattern 2: Behavioral Claim

```yaml
Claim: "InteractionOrchestrator uses ChallengeEngine"

Verification Steps:
  1. Read: cortex/orchestrators/core/interaction_orchestrator.py
  2. Search: grep_search(query="ChallengeEngine", includePattern="interaction_orchestrator.py")
  3. Verify: Import statement exists
  4. Check: Instance created in __init__
  5. Validate: Used in methods

Verdict: verified (with line numbers)
```

### Pattern 3: Architectural Claim

```yaml
Claim: "CORTEX has 4-layer governance defense"

Verification Steps:
  1. Search: grep_search(query="Layer 1|Layer 2|Layer 3|Layer 4", isRegexp=True)
  2. Read: governance implementation files
  3. Verify: Each layer implemented
  4. Check: Integration points exist
  5. Flag: If any layer missing

Verdict: partial (Layers 1-2 complete, 3-4 planned)
```

### Pattern 4: Configuration Claim

```yaml
Claim: "28 orchestrators are wired"

Verification Steps:
  1. Read: cortex/wiring/specifications/wiring.yaml
  2. Parse: YAML structure
  3. Count: Orchestrator entries
  4. Verify: Each entry has valid class reference
  5. Cross-check: Implementation files exist

Verdict: verified (with count)
```

---

## Drift Detection

### Types of Drift

#### 1. Feature Drift
```yaml
Documentation: "Feature X is implemented"
Reality: Feature X does not exist in code
Action: Flag as missing feature, recommend implementation or doc update
```

#### 2. Behavioral Drift
```yaml
Documentation: "Component does X then Y"
Reality: Component does X then Z
Action: Flag as behavioral mismatch, show actual flow
```

#### 3. Configuration Drift
```yaml
Documentation: "Config option is X"
Reality: Config option is Y or doesn't exist
Action: Flag as config drift, show actual settings
```

#### 4. Dependency Drift
```yaml
Documentation: "Uses library X version 2.0"
Reality: Uses library X version 1.5
Action: Flag as dependency mismatch, show requirements.txt
```

---

## Evidence Collection

### Evidence Types

```python
@dataclass
class Evidence:
    """Evidence supporting verification."""
    
    # Source locations
    file_path: str
    line_start: int
    line_end: int
    
    # Code context
    code_snippet: str
    surrounding_context: str  # 5 lines before/after
    
    # Structural info
    class_name: Optional[str]
    method_name: Optional[str]
    ast_node_type: Optional[str]
    
    # Verification metadata
    verification_timestamp: datetime
    git_commit: str  # SHA of verified state
    git_author: str
    git_date: datetime
    
    # Cross-references
    wiring_reference: Optional[str]
    test_reference: Optional[str]
    documentation_reference: Optional[str]
```

### Evidence Presentation

```markdown
**Evidence:**
- File: `cortex/orchestrators/core/master_orchestrator.py` (lines 140-180)
- Class: `MasterOrchestrator`
- Method: `execute()`
- Wiring: `cortex/wiring/specifications/wiring.yaml` (line 45)
- Tests: `tests/unit/orchestrators/core/test_master_orchestrator.py` (28 tests)
- Last Modified: 2026-01-28 by Asif Hussain
- Git SHA: `7110c03`

**Code Snippet:**
```python
class MasterOrchestrator:
    def __init__(self, wiring_registry: GitBackedRegistry):
        self.registry = wiring_registry
        self.orchestrators = self.registry.load_orchestrators()
        # 28 orchestrators loaded from wiring.yaml
```
```

---

## Integration with ASK Mode

### Workflow Integration

```
User Query
    ↓
ASK Coordinator extracts claims
    ↓
Truth Verifier validates each claim
    ↓
    ├─ Verified → Include in response with evidence
    ├─ False → Correct with actual truth
    ├─ Partial → Explain nuance with evidence
    └─ Drift → Flag issue, show both docs and code
    ↓
Fault Detection (if drift/issues)
    ↓
Response Generation (with verified truth)
```

### Example Usage

```python
# In EducationalOrchestrator
claims = extract_claims(user_query)

verified_claims = []
for claim in claims:
    result = truth_verifier.verify(claim)
    
    if result.verdict == "verified":
        verified_claims.append(result)
    elif result.verdict == "false":
        # Correct misconception
        corrected = f"{claim} is not accurate. "
        corrected += f"Actually: {result.actual_truth}"
        verified_claims.append(corrected)
    elif result.verdict == "drift":
        # Flag drift
        fault_detector.report_drift(result.drift_details)
        verified_claims.append(result.actual_truth)

# Generate response with only verified information
response = generate_response(verified_claims)
```

---

## Verification Tools

### VS Code Tools Used

```python
# File reading
read_file(filePath, startLine, endLine)

# Search
grep_search(query, isRegexp, includePattern)
file_search(query)

# Code analysis
cortex_ast_analyze(target, analysis_type)
cortex_lens_analyze(target, scope)

# Git context
cortex_git_history(file_path, days)
```

### Custom Verification Tools

```python
# Wiring verification
verify_wiring_registration(component_name) -> bool

# Test coverage check
verify_test_coverage(component_path) -> CoverageReport

# Documentation comparison
detect_drift(docs_path, impl_path) -> DriftReport

# AST structure validation
verify_structure(file_path, expected_structure) -> StructureReport
```

---

## Fault Reporting

### When to Report

```yaml
Report Faults When:
  - Documentation drift detected (P1)
  - Broken wiring found (P0)
  - Missing tests identified (P1)
  - Implementation gap discovered (P0-P2 based on severity)
  - Architectural violation found (P2)
```

### Fault Report Format

```python
@dataclass
class FaultReport:
    """Fault detected during verification."""
    
    fault_type: str  # "drift", "missing_impl", "broken_wiring", "test_gap"
    description: str
    evidence: Evidence
    recommendation: str
    priority: str  # "P0", "P1", "P2"
    affected_components: List[str]
    fix_estimate: str  # Time to fix
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Verification Accuracy | 95%+ |
| Drift Detection Rate | 90%+ |
| False Positive Rate | <5% |
| Evidence Completeness | 90%+ |
| Verification Time | <1s per claim |

---

## CORE Compliance

| Rule | Implementation |
|------|----------------|
| CORE-030 | Implementation Truth enforced |
| CORE-027 | Audit trail for verifications |
| CORE-011 | Type hints in all verification code |
| CORE-012 | Docstrings for verification methods |

---

## Related Components

| Component | Relation |
|-----------|----------|
| EducationalOrchestrator | Consumer of verification results |
| TruthVerificationEngine | Implementation (Python class) |
| FaultDetectionReporter | Receives drift reports |
| NextStepGenerator | Uses verified truth for options |

---

## Example Verifications

### Example 1: Simple Existence

```
Claim: "MasterOrchestrator exists"
Steps:
  1. file_search("master_orchestrator.py")
  2. Read file
  3. Verify class exists
Result: ✅ VERIFIED
Evidence: cortex/orchestrators/core/master_orchestrator.py (line 120)
```

### Example 2: Behavioral

```
Claim: "InteractionOrchestrator builds LENS context on every turn"
Steps:
  1. Read interaction_orchestrator.py
  2. Find build_lens_context method
  3. Check if called in main flow
  4. Verify with tests
Result: ✅ VERIFIED
Evidence: 
  - File: interaction_orchestrator.py (line 234)
  - Method: build_lens_context()
  - Called: In process_request() (line 189)
  - Tests: test_builds_lens_context() passes
```

### Example 3: Drift Detected

```
Claim: "CORTEX has 4-layer governance defense"
Steps:
  1. Read governance documentation
  2. Search for Layer 3, Layer 4 implementations
  3. Cross-reference with code
Result: ⚠️ DRIFT
Evidence:
  - Docs: Claims 4 layers
  - Code: Only Layers 1-2 fully implemented
  - Status: Layers 3-4 are planned (PHASE-X.yaml)
Recommendation: Update docs to reflect current state or complete Layers 3-4
```

---

**Status:** ✅ SPECIFICATION COMPLETE  
**Implements:** Truth verification for cortex-ask.prompt.md  
**Used By:** ASK Coordinator, EducationalOrchestrator  
**Python Class:** TruthVerificationEngine

---

*v1.0 — Implementation truth enforcement for educational accuracy.*
