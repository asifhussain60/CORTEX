# Cortex-Review Orchestrator Conversion Analysis

**Analysis Date:** 2026-01-07T07:45:00Z  
**Source:** `.github/prompts/cortex-review.prompt.md`  
**Target:** Registered toolkit orchestrator  
**Epic:** cortex5-epic-v3  
**Analyzer:** CORTEX Planner v1.0.0

---

## 🎯 Conversion Objectives

Transform the cortex-review prompt into a **registered toolkit orchestrator** that:

1. ✅ **Validates epic plans** against implementation and CORTEX design goals
2. ✅ **Autonomous execution** via Python (no LLM inline execution)
3. ✅ **Registered in orchestrator registry** with unique pattern matching
4. ✅ **Integrates with cortex5-epic** validation workflow
5. ✅ **Phase progression blocking** for governance compliance

---

## 📋 Current Prompt Analysis

### Functionality Breakdown

**Core Capabilities:**
1. **Strategic Alignment** - Goal achievement verification
2. **Architecture Integrity** - Conflict and brittleness detection
3. **Autonomous Execution** - RAG/DAG execution validation
4. **Best Practices** - Knowledge library and domain boundary enforcement
5. **Implementation Fidelity** - Plan vs. code alignment
6. **Governance Validation** - SKULL rules enforcement
7. **Phase Progression Blocking** - Critical violation prevention

**Review Process (7 Phases):**
- Phase 1: Epic Structure Analysis
- Phase 2: Architecture Coherence Review
- Phase 3: Knowledge Integration Analysis
- Phase 4: Orchestrator Registry Audit
- Phase 5: Edge Case & Failure Mode Analysis
- Phase 6: Implementation Fidelity Check
- Phase 7: Best Practices & Governance Validation

**Output:** YAML report with scores, issues, recommendations

---

## 🏗️ Orchestrator Design

### Component Structure

```
src/orchestrators/review/
├── __init__.py
├── review_orchestrator_v2.py          # Main orchestrator
├── analyzers/
│   ├── __init__.py
│   ├── epic_structure_analyzer.py     # Phase 1
│   ├── architecture_analyzer.py       # Phase 2
│   ├── knowledge_analyzer.py          # Phase 3
│   ├── registry_analyzer.py           # Phase 4
│   ├── edge_case_analyzer.py          # Phase 5
│   ├── fidelity_analyzer.py           # Phase 6
│   └── governance_analyzer.py         # Phase 7
├── validators/
│   ├── __init__.py
│   ├── python_validator.py            # mypy, pylint, pydocstyle
│   ├── audit_log_validator.py         # Audit log cross-check
│   └── phase_progression_validator.py # Blocking rules
└── reporters/
    ├── __init__.py
    ├── yaml_reporter.py               # YAML output
    └── markdown_reporter.py           # Human-readable
```

### Orchestrator Registration

**File:** `cortex-brain/manifests/orchestrators/review-orchestrator-v2.yaml`

```yaml
orchestrator_id: "review_v2"
version: "2.0.0"
type: "validation"
priority: 3

patterns:
  primary:
    - "review epic"
    - "verify plan"
    - "cortex review"
    - "check alignment"
    - "validate implementation"
    - "review (.*) plan"
    - "verify (.*) epic"
  
  parameters:
    - name: "epic_path"
      type: "path"
      required: true
      description: "Path to epic folder (active/archived)"
      examples:
        - "cortex5-epic"
        - "active/cortex5-epic"
        - "archived/cortex5-enhancement-epic-20260107"
    
    - name: "review_type"
      type: "enum"
      required: false
      default: "comprehensive"
      values: ["baseline", "progress", "phase", "final", "retrospective", "comprehensive"]
      description: "Type of review to perform"

capabilities:
  - epic_validation
  - architecture_analysis
  - governance_enforcement
  - phase_progression_blocking
  - implementation_fidelity_check

dependencies:
  - state_db
  - governance_rules
  - knowledge_library

execution:
  mode: "autonomous"
  timeout: 300  # 5 minutes max
  parallelizable: false
  requires_llm: false  # Pure Python execution

output:
  format: "yaml"
  location: "{epic_path}/reports/cortex-review/"
  filename: "{timestamp}_{review_type}_review.yaml"
```

---

## 🔧 Implementation Plan

### Phase 1: Core Orchestrator Creation (3 hours)

**File:** `src/orchestrators/review/review_orchestrator_v2.py`

```python
"""
CORTEX Review Orchestrator v2.0.0
Validates epic plans against implementation and design goals.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from src.orchestrators.base_orchestrator import BaseOrchestrator
from src.state.planning_state_db import PlanningStateDB

class ReviewOrchestratorV2(BaseOrchestrator):
    """
    Comprehensive epic plan and implementation review orchestrator.
    
    Attributes:
        state_db: Planning state database
        epic_path: Path to epic folder
        review_type: Type of review (baseline, progress, phase, etc.)
    """
    
    def __init__(
        self,
        config_path: str,
        state_db: PlanningStateDB,
        epic_path: str,
        review_type: str = "comprehensive"
    ):
        super().__init__(config_path)
        self.state_db = state_db
        self.epic_path = Path(epic_path)
        self.review_type = review_type
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self._init_analyzers()
    
    def _init_analyzers(self) -> None:
        """Initialize all analyzer modules."""
        from .analyzers import (
            EpicStructureAnalyzer,
            ArchitectureAnalyzer,
            KnowledgeAnalyzer,
            RegistryAnalyzer,
            EdgeCaseAnalyzer,
            FidelityAnalyzer,
            GovernanceAnalyzer
        )
        
        self.analyzers = {
            "structure": EpicStructureAnalyzer(self.epic_path),
            "architecture": ArchitectureAnalyzer(self.epic_path),
            "knowledge": KnowledgeAnalyzer(self.epic_path),
            "registry": RegistryAnalyzer(self.epic_path),
            "edge_cases": EdgeCaseAnalyzer(self.epic_path),
            "fidelity": FidelityAnalyzer(self.epic_path),
            "governance": GovernanceAnalyzer(self.epic_path, self.state_db)
        }
    
    def execute(self, request: str, **kwargs) -> Dict[str, Any]:
        """
        Execute review based on review type.
        
        Args:
            request: User request string
            **kwargs: Additional parameters
        
        Returns:
            Review results with scores and recommendations
        
        Raises:
            FileNotFoundError: If epic path doesn't exist
            ValidationError: If critical violations found
        """
        self.logger.info(f"Starting {self.review_type} review for {self.epic_path}")
        
        # Execute all analyzers
        results = {}
        for analyzer_name, analyzer in self.analyzers.items():
            self.logger.info(f"Running {analyzer_name} analyzer...")
            results[analyzer_name] = analyzer.analyze()
        
        # Calculate overall scores
        overall_score = self._calculate_overall_score(results)
        
        # Check blocking conditions
        blocking_issues = self._check_blocking_conditions(results)
        
        # Generate report
        report = self._generate_report(results, overall_score, blocking_issues)
        
        # Save report
        output_path = self._save_report(report)
        
        return {
            "status": "complete" if not blocking_issues else "blocked",
            "overall_score": overall_score,
            "blocking_issues": blocking_issues,
            "report_path": str(output_path),
            "results": results
        }
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate weighted overall score."""
        weights = {
            "structure": 0.15,
            "architecture": 0.20,
            "knowledge": 0.10,
            "registry": 0.10,
            "edge_cases": 0.15,
            "fidelity": 0.15,
            "governance": 0.15
        }
        
        score = sum(
            results[name]["score"] * weights[name]
            for name in weights
        )
        return round(score, 2)
    
    def _check_blocking_conditions(self, results: Dict[str, Any]) -> List[str]:
        """Check if any blocking conditions exist."""
        blocking = []
        
        # Check governance violations
        gov_violations = results["governance"].get("blocked_violations", [])
        if gov_violations:
            blocking.extend(gov_violations)
        
        # Check critical scores
        if results["architecture"]["score"] < 65:
            blocking.append("Architecture coherence score below threshold (65)")
        
        if results["fidelity"]["score"] < 60:
            blocking.append("Implementation fidelity score below threshold (60)")
        
        if results["governance"]["score"] < 70:
            blocking.append("Governance compliance score below threshold (70)")
        
        return blocking
    
    def _generate_report(
        self,
        results: Dict[str, Any],
        overall_score: float,
        blocking_issues: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive review report."""
        return {
            "review_metadata": {
                "timestamp": self._get_timestamp(),
                "epic_path": str(self.epic_path),
                "review_type": self.review_type,
                "orchestrator_version": "2.0.0"
            },
            "overall_assessment": {
                "score": overall_score,
                "status": "PASS" if overall_score >= 70 else "FAIL",
                "severity": self._calculate_severity(overall_score, blocking_issues)
            },
            "blocking_issues": blocking_issues,
            "phase_results": results,
            "recommendations": self._generate_recommendations(results, blocking_issues)
        }
    
    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save report to YAML file."""
        import yaml
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.epic_path / "reports" / "cortex-review"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{timestamp}_{self.review_type}_review.yaml"
        
        with open(output_file, "w") as f:
            yaml.dump(report, f, sort_keys=False, default_flow_style=False)
        
        self.logger.info(f"Report saved to {output_file}")
        return output_file
```

---

### Phase 2: Analyzer Modules (6 hours)

Create 7 analyzer modules, each focused on one review phase:

1. **EpicStructureAnalyzer** - Validates epic structure, phases, dependencies
2. **ArchitectureAnalyzer** - Checks orchestrator routing, state management
3. **KnowledgeAnalyzer** - Validates knowledge integration and merge logic
4. **RegistryAnalyzer** - Audits orchestrator registry for conflicts
5. **EdgeCaseAnalyzer** - Tests race conditions, failure modes, security
6. **FidelityAnalyzer** - Compares plan vs. implementation
7. **GovernanceAnalyzer** - Enforces SKULL rules and static analysis

---

### Phase 3: Validator Modules (2 hours)

1. **PythonValidator** - Runs mypy, pylint, pydocstyle, black, isort
2. **AuditLogValidator** - Cross-checks audit logs with current code
3. **PhaseProgressionValidator** - Enforces blocking rules

---

### Phase 4: Integration & Testing (3 hours)

1. Register orchestrator in `cortex-brain/manifests/orchestrators/`
2. Update `src/orchestrators/master_orchestrator.py` routing
3. Create integration tests
4. Create sample review outputs

---

### Phase 5: Documentation & Cleanup (1 hour)

1. Update README.md with review orchestrator usage
2. Delete `.github/prompts/cortex-review.prompt.md`
3. Add to CHANGELOG.md

---

## 📊 Estimated Effort

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | 3 hours | Core orchestrator |
| Phase 2 | 6 hours | 7 analyzer modules |
| Phase 3 | 2 hours | 3 validator modules |
| Phase 4 | 3 hours | Integration & tests |
| Phase 5 | 1 hour | Docs & cleanup |
| **Total** | **15 hours** | **Registered orchestrator** |

---

## 🎯 Integration with cortex5-epic

**Location in Epic:** Phase 4 (Orchestrator Registry System)

**Integration Points:**
1. Add to orchestrator registry
2. Update master orchestrator routing
3. Create phase-specific review trigger
4. Integrate with phase progression validation

**Post-Integration:**
- ✅ Run review after each phase completion
- ✅ Block phase progression if blocking issues found
- ✅ Generate remediation plans automatically

---

## ✅ Success Criteria

1. ✅ **Orchestrator registered** in `cortex-brain/manifests/orchestrators/review-orchestrator-v2.yaml`
2. ✅ **Pattern matching** works for all trigger phrases
3. ✅ **Autonomous execution** via Python (no LLM required)
4. ✅ **YAML reports generated** in `{epic_path}/reports/cortex-review/`
5. ✅ **Phase progression blocking** enforced for critical violations
6. ✅ **Integration tests pass** 100%
7. ✅ **Original prompt deleted** after verification

---

## 🔄 Execution Plan

**Step 1:** Create orchestrator skeleton (this analysis document)  
**Step 2:** Implement core orchestrator (Phase 1)  
**Step 3:** Implement analyzers (Phase 2)  
**Step 4:** Implement validators (Phase 3)  
**Step 5:** Integration and testing (Phase 4)  
**Step 6:** Documentation and cleanup (Phase 5)  
**Step 7:** Delete `.github/prompts/cortex-review.prompt.md`  
**Step 8:** Commit and push to CORTEX-5.5

---

**Analysis Complete:** Ready for orchestrator creation  
**Next Step:** Begin Phase 1 implementation
