# Implementation Guide: Three High-Value Enhancements
**Date:** January 18, 2026  
**Duration:** 4 weeks, 25-40 hours  
**Governance:** Follow cortex-builder.prompt.md standards throughout

---

## ENHANCEMENT 1: MCP Compliance Validation Framework

### Overview
- **Problem:** New MCP tools may violate protocol without detection
- **Solution:** Automated compliance validator + checklist
- **Effort:** 3-5 hours
- **Blocking:** None
- **Dependency:** PHASE-22-MCP-PROTOCOL-COMPLIANCE (already locked)

### Acceptance Criteria

#### AC-MCP-VALID-001: Tool Compliance Validator
```yaml
description: "Automated tool compliance checking against MCP spec"
acceptance_criteria:
  - Tool metadata complete (name, version, capabilities, schema)
  - Tool schema validates against OpenAPI 3.0.0 spec
  - Tool error handling follows protocol (success/error fields)
  - Tool documentation auto-generated from schema
  - Validator rejects non-compliant tools with clear error messages

test_count: 18
estimated_hours: 2
files_to_create:
  - src/mcp/tools/validator.py
  - tests/mcp/test_tool_validator.py
```

#### AC-MCP-VALID-002: Compliance Checklist & Documentation
```yaml
description: "Tool developer guide for MCP compliance"
acceptance_criteria:
  - Checklist document with 12-15 required elements
  - Example: "Tool exposes required metadata fields"
  - Example: "Tool schema uses standard types"
  - Example: "Tool errors include error codes and descriptions"
  - Example: "Tool documentation includes all parameters"
  - Developer can use checklist standalone without running code

test_count: 8
estimated_hours: 2
files_to_create:
  - docs/mcp-tool-compliance-checklist.md
  - docs/mcp-tool-development-guide.md
  - examples/mcp-compliant-tool-template.py
```

### Implementation Details

**File 1: src/mcp/tools/validator.py (~250 lines)**
```python
from typing import Protocol, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

class ComplianceLevel(Enum):
    STRICT = "strict"      # All required + optional fields
    REQUIRED = "required"  # All required fields only
    MINIMAL = "minimal"    # Core functionality only

@dataclass
class ComplianceResult:
    is_compliant: bool
    level: ComplianceLevel
    errors: List[str]
    warnings: List[str]
    metadata_missing: List[str]
    schema_issues: List[str]

class ToolComplianceValidator:
    """Validates MCP tools against compliance standards."""
    
    def validate_metadata(self, tool: Any) -> ComplianceResult:
        """Check tool has required metadata."""
        # Check: name, version, description, capabilities, schema
        # Return ComplianceResult with findings
    
    def validate_schema(self, schema: Dict) -> Tuple[bool, List[str]]:
        """Validate tool schema against OpenAPI spec."""
        # Check: schema structure, type definitions, required fields
        # Return (is_valid, error_messages)
    
    def validate_error_handling(self, tool: Any) -> Tuple[bool, List[str]]:
        """Verify error handling follows MCP protocol."""
        # Check: errors include code, message, context
        # Return (is_compliant, issues)
    
    def generate_documentation(self, tool: Any) -> str:
        """Auto-generate documentation from tool definition."""
        # Extract metadata and schema
        # Generate markdown documentation
        # Return formatted doc string
    
    def validate_tool(self, tool: Any, 
                     level: ComplianceLevel = ComplianceLevel.REQUIRED
                     ) -> ComplianceResult:
        """Run all validations and return aggregated result."""
```

**File 2: tests/mcp/test_tool_validator.py (~200 lines)**
```python
import pytest
from src.mcp.tools.validator import ToolComplianceValidator, ComplianceLevel

class TestToolComplianceValidator:
    
    def test_validate_metadata_complete(self):
        """Tool with all metadata fields passes validation."""
        tool = {
            "name": "my-tool",
            "version": "1.0.0",
            "description": "Does something",
            "capabilities": ["read", "write"],
            "schema": {...}
        }
        validator = ToolComplianceValidator()
        result = validator.validate_tool(tool)
        assert result.is_compliant == True
    
    def test_validate_metadata_missing_name(self):
        """Tool without name field fails validation."""
        tool = {
            "version": "1.0.0",
            "description": "Does something"
        }
        validator = ToolComplianceValidator()
        result = validator.validate_tool(tool)
        assert result.is_compliant == False
        assert "name" in result.metadata_missing
    
    def test_validate_schema_valid(self):
        """Valid OpenAPI schema passes validation."""
        # Test with proper OpenAPI 3.0.0 schema
    
    def test_validate_schema_invalid(self):
        """Invalid schema fails with clear error."""
        # Test with malformed schema
    
    def test_validate_error_handling(self):
        """Tool error responses follow protocol."""
        # Test error format: { "error": { "code": "...", "message": "..." } }
    
    def test_generate_documentation(self):
        """Documentation auto-generated from tool definition."""
        # Verify markdown contains all relevant info
    
    # ... 12+ total tests covering all paths
```

### Success Criteria
- ✅ All existing MCP tools pass validator
- ✅ Validator catches schema violations
- ✅ Checklist used by next new tool developer
- ✅ Documentation auto-generation produces readable output

---

## ENHANCEMENT 2: Knowledge Quality Assurance Framework

### Overview
- **Problem:** Ingested knowledge lacks quality metrics, causing hallucination
- **Solution:** Confidence scoring, staleness detection, verification workflow
- **Effort:** 6-8 hours
- **Blocking:** PHASE-21-INTELLIGENT-KNOWLEDGE completion (planned for next week)
- **Dependency:** PHASE-17-DOMAIN-BRAIN (already locked)

### Acceptance Criteria

#### AC-KN-QUALITY-001: Confidence Scoring System
```yaml
description: "Automatic confidence scoring for all knowledge entries"
acceptance_criteria:
  - Every knowledge entry has confidence_score (0.0-1.0)
  - Score computed from: source quality, verification status, age
  - Score accessible via knowledge.get_entry() API
  - Confidence factors documented (source quality 40%, verified 40%, age 20%)
  - Low confidence (<0.5) entries flagged in LENS routing

test_count: 12
estimated_hours: 2.5
files_to_create:
  - src/knowledge/confidence_scorer.py
  - tests/knowledge/test_confidence_scoring.py
```

#### AC-KN-QUALITY-002: Staleness Detection & Verification Workflow
```yaml
description: "Automatic staleness detection and human verification workflow"
acceptance_criteria:
  - Each entry tracked: source, last_verified_at, verified_by
  - Staleness threshold configurable per source (AST:1d, Git:7d, Manual:30d)
  - Stale entries flagged in LENS (confidence reduced to 0.3)
  - Human verification workflow: Approve/Reject/Clarify with audit trail
  - Conflict resolution: Multiple sources disagree → require human resolution

test_count: 13
estimated_hours: 3.5
files_to_create:
  - src/knowledge/staleness_detector.py
  - src/knowledge/verification_workflow.py
  - tests/knowledge/test_staleness_and_verification.py
```

#### AC-KN-QUALITY-003: Integration with Knowledge Router
```yaml
description: "Quality scores integrated into intelligent routing"
acceptance_criteria:
  - IntelligentKnowledgeRouter considers confidence scores in routing decision
  - Low confidence knowledge used only if high confidence unavailable
  - LENS comprehension phase receives confidence metadata
  - Documentation updated with quality considerations

test_count: 8
estimated_hours: 2
files_to_create:
  - docs/knowledge-quality-standards.md
  - examples/knowledge-quality-assessment.md
```

### Implementation Details

**File 1: src/knowledge/confidence_scorer.py (~280 lines)**
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
from enum import Enum

class SourceQuality(Enum):
    AUTOMATIC = 0.7      # AST parsing, git history
    DOCUMENTED = 0.8     # Manual documentation
    VERIFIED = 0.95      # Human verified
    TRUSTED = 1.0        # Trusted expert

@dataclass
class KnowledgeEntry:
    content: str
    source: str
    source_quality: SourceQuality
    created_at: datetime
    last_verified_at: datetime
    verified_by: str = None
    verification_status: str = "unverified"  # unverified, verified, rejected, under_review
    conflict_notes: str = None

class ConfidenceScorer:
    """Computes confidence scores for knowledge entries."""
    
    # Scoring weights
    SOURCE_QUALITY_WEIGHT = 0.40      # 40% from source quality
    VERIFICATION_WEIGHT = 0.40        # 40% from human verification
    RECENCY_WEIGHT = 0.20             # 20% from age/recency
    
    # Staleness thresholds per source
    STALENESS_THRESHOLDS = {
        "ast_intelligence": timedelta(days=1),
        "git_history": timedelta(days=7),
        "manual_knowledge": timedelta(days=30),
        "business_knowledge": timedelta(days=14),
    }
    
    def compute_confidence(self, entry: KnowledgeEntry) -> float:
        """
        Compute confidence score (0.0-1.0) based on:
        - Source quality (0.40 weight)
        - Verification status (0.40 weight)
        - Recency/age (0.20 weight)
        """
        source_score = entry.source_quality.value
        verification_score = self._verification_score(entry)
        recency_score = self._recency_score(entry)
        
        confidence = (
            source_score * self.SOURCE_QUALITY_WEIGHT +
            verification_score * self.VERIFICATION_WEIGHT +
            recency_score * self.RECENCY_WEIGHT
        )
        return min(1.0, max(0.0, confidence))
    
    def _verification_score(self, entry: KnowledgeEntry) -> float:
        """Score based on verification status."""
        scores = {
            "verified": 1.0,
            "unverified": 0.5,
            "rejected": 0.0,
            "under_review": 0.3,
        }
        return scores.get(entry.verification_status, 0.5)
    
    def _recency_score(self, entry: KnowledgeEntry) -> float:
        """Score based on age (newer = higher)."""
        age = datetime.now() - entry.last_verified_at
        max_age = self.STALENESS_THRESHOLDS.get(entry.source, timedelta(days=30))
        
        if age < max_age:
            return 1.0  # Fresh
        elif age < max_age * 2:
            return 0.7  # Aging
        elif age < max_age * 3:
            return 0.4  # Stale
        else:
            return 0.1  # Very stale
    
    def get_staleness_status(self, entry: KnowledgeEntry) -> Dict:
        """Check if entry is stale."""
        threshold = self.STALENESS_THRESHOLDS.get(
            entry.source, 
            timedelta(days=30)
        )
        age = datetime.now() - entry.last_verified_at
        
        return {
            "is_stale": age > threshold,
            "age_days": age.days,
            "threshold_days": threshold.days,
            "last_verified": entry.last_verified_at.isoformat(),
        }
```

**File 2: src/knowledge/verification_workflow.py (~320 lines)**
```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from datetime import datetime

class VerificationAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    CLARIFY = "clarify"
    ESCALATE = "escalate"

@dataclass
class VerificationRequest:
    entry_id: str
    entry: Dict
    reason: str
    conflicting_entries: List[Dict]
    confidence_score: float
    requester: str

@dataclass
class VerificationDecision:
    action: VerificationAction
    decided_by: str
    decided_at: datetime
    notes: str
    updated_confidence: float

class VerificationWorkflow:
    """Human verification workflow for knowledge conflicts."""
    
    def create_verification_request(self, 
                                   entry_id: str,
                                   entry: Dict,
                                   reason: str,
                                   conflicting_entries: List[Dict] = None
                                   ) -> VerificationRequest:
        """Create request for human review."""
        request = VerificationRequest(
            entry_id=entry_id,
            entry=entry,
            reason=reason,
            conflicting_entries=conflicting_entries or [],
            confidence_score=self._compute_score(entry),
            requester="system"
        )
        # Log to audit trail
        self._log_audit_event("VERIFICATION_REQUESTED", entry_id, reason)
        return request
    
    def apply_verification_decision(self,
                                   request: VerificationRequest,
                                   action: VerificationAction,
                                   decided_by: str,
                                   notes: str = ""
                                   ) -> VerificationDecision:
        """Apply human verification decision."""
        if action == VerificationAction.APPROVE:
            new_confidence = min(0.95, request.confidence_score + 0.2)
            status = "verified"
        elif action == VerificationAction.REJECT:
            new_confidence = 0.1
            status = "rejected"
        elif action == VerificationAction.CLARIFY:
            new_confidence = request.confidence_score
            status = "under_review"
        else:  # ESCALATE
            new_confidence = request.confidence_score
            status = "escalated"
        
        decision = VerificationDecision(
            action=action,
            decided_by=decided_by,
            decided_at=datetime.now(),
            notes=notes,
            updated_confidence=new_confidence
        )
        
        # Update knowledge entry
        self._update_entry_status(request.entry_id, status, decided_by)
        
        # Log to audit trail
        self._log_audit_event(
            f"VERIFICATION_{action.name}",
            request.entry_id,
            notes
        )
        
        return decision
    
    def resolve_conflicting_entries(self,
                                   entries: List[Dict],
                                   resolution_strategy: str = "trust_verified"
                                   ) -> Dict:
        """Resolve when multiple sources have conflicting knowledge."""
        if resolution_strategy == "trust_verified":
            # Prefer verified entries
            verified = [e for e in entries if e.get("verified_by")]
            if verified:
                return verified[0]
        
        # Otherwise use highest confidence
        return max(entries, key=lambda e: e.get("confidence_score", 0.5))
```

### Success Criteria
- ✅ All knowledge entries have confidence scores
- ✅ Staleness detected and flagged
- ✅ Human verification workflow operational
- ✅ LENS routing considers quality scores

---

## ENHANCEMENT 3: Orchestrator Testing & Debugging Framework

### Overview
- **Problem:** Multi-stage orchestrators lack debugging tools for edge cases
- **Solution:** Snapshot/replay debugging + chaos scenario library
- **Effort:** 8-12 hours
- **Blocking:** None
- **Dependency:** PHASE-16-ORCHESTRATOR-CONTINUATION (already locked)

### Acceptance Criteria

#### AC-ODX-DEBUG-001: State Snapshot & Replay System
```yaml
description: "Capture workflow state at any turn for debugging"
acceptance_criteria:
  - Snapshot captures ConversationSession state (turn N)
  - Snapshot serializable to JSON for persistence
  - Replay reconstructs workflow from snapshot
  - Replay supports breakpoints at stage transitions
  - Breakpoint inspection shows: context, variables, history
  - Performance: Snapshot <100ms, Replay <1s

test_count: 18
estimated_hours: 4
files_to_create:
  - src/devx/snapshot_manager.py
  - src/devx/replay_engine.py
  - tests/devx/test_snapshot_replay.py
```

#### AC-ODX-DEBUG-002: Chaos Scenario Library
```yaml
description: "Pre-built edge case scenarios for orchestrator testing"
acceptance_criteria:
  - Token budget exhaustion scenario
  - User rejection at each stage (1, 2, 3, 4)
  - Network error in LENS execution
  - Database connection timeout
  - Governance rule violation scenario
  - Unknown operation type scenario
  - Each scenario includes expected behavior and validation

test_count: 15
estimated_hours: 3
files_to_create:
  - src/devx/chaos_scenarios.py
  - tests/devx/test_chaos_scenarios.py
  - docs/chaos-testing-guide.md
```

#### AC-ODX-DEBUG-003: Debugging Tools Integration
```yaml
description: "Unified orchestrator debugging interface"
acceptance_criteria:
  - OrchestratorDebugger class provides unified interface
  - CLI: cortex-debug orchestrator-name --snapshot-at turn-3
  - API: debugger.snapshot(), debugger.replay(), debugger.breakpoint()
  - Integration with PHASE-09 CLI tools
  - Documentation with 5+ example workflows

test_count: 12
estimated_hours: 2
files_to_create:
  - src/devx/orchestrator_debugger.py
  - tests/devx/test_debugger_integration.py
  - docs/orchestrator-debugging-guide.md
  - examples/debug-master-orchestrator.md
```

### Implementation Details

**File 1: src/devx/snapshot_manager.py (~320 lines)**
```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import json

@dataclass
class StageSnapshot:
    """Snapshot of a single orchestrator stage."""
    stage_name: str
    stage_number: int
    start_time: datetime
    end_time: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: str  # "running", "completed", "failed", "rejected"
    error: Optional[str] = None

@dataclass
class ConversationSnapshot:
    """Complete snapshot of ConversationSession state."""
    session_id: str
    turn_number: int
    timestamp: datetime
    user_input: str
    orchestrator_name: str
    stages: List[StageSnapshot]
    current_stage: int
    context_variables: Dict[str, Any]
    governance_state: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]
    continuation_decision: Optional[Dict[str, Any]] = None

class SnapshotManager:
    """Captures and manages workflow snapshots."""
    
    def snapshot_current_state(self,
                              session: Any,
                              turn_number: int,
                              orchestrator_name: str
                              ) -> ConversationSnapshot:
        """
        Capture current state of orchestrator execution.
        Called at key points: before stage, after stage, on error.
        """
        stages = self._extract_stage_snapshots(session)
        
        snapshot = ConversationSnapshot(
            session_id=session.session_id,
            turn_number=turn_number,
            timestamp=datetime.now(),
            user_input=session.current_input,
            orchestrator_name=orchestrator_name,
            stages=stages,
            current_stage=session.current_stage_index,
            context_variables=dict(session.context),
            governance_state=self._extract_governance_state(session),
            audit_trail=list(session.audit_log),
        )
        
        return snapshot
    
    def save_snapshot(self, snapshot: ConversationSnapshot, 
                     filepath: str) -> None:
        """Serialize snapshot to JSON file."""
        data = asdict(snapshot)
        # Convert datetime objects to ISO format
        data['timestamp'] = data['timestamp'].isoformat()
        data['stages'] = [
            {
                **asdict(stage),
                'start_time': stage.start_time.isoformat(),
                'end_time': stage.end_time.isoformat() if stage.end_time else None,
            }
            for stage in snapshot.stages
        ]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_snapshot(self, filepath: str) -> ConversationSnapshot:
        """Deserialize snapshot from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct objects from JSON
        stages = [
            StageSnapshot(
                stage_name=s['stage_name'],
                stage_number=s['stage_number'],
                start_time=datetime.fromisoformat(s['start_time']),
                end_time=datetime.fromisoformat(s['end_time']) if s['end_time'] else None,
                input_data=s['input_data'],
                output_data=s['output_data'],
                status=s['status'],
                error=s.get('error'),
            )
            for s in data['stages']
        ]
        
        return ConversationSnapshot(
            session_id=data['session_id'],
            turn_number=data['turn_number'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_input=data['user_input'],
            orchestrator_name=data['orchestrator_name'],
            stages=stages,
            current_stage=data['current_stage'],
            context_variables=data['context_variables'],
            governance_state=data['governance_state'],
            audit_trail=data['audit_trail'],
        )
    
    def _extract_stage_snapshots(self, session: Any) -> List[StageSnapshot]:
        """Extract snapshots from completed stages."""
        # Implementation accesses session's stage history
        pass
    
    def _extract_governance_state(self, session: Any) -> Dict[str, Any]:
        """Extract governance evaluation state."""
        # Implementation accesses governance context
        pass
```

**File 2: src/devx/replay_engine.py (~280 lines)**
```python
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

@dataclass
class Breakpoint:
    stage_name: str
    turn_number: Optional[int] = None

class ReplayEngine:
    """Replays orchestrator workflow from snapshot."""
    
    def __init__(self, snapshot_manager: SnapshotManager):
        self.snapshot_manager = snapshot_manager
        self.breakpoints: List[Breakpoint] = []
        self.paused_at: Optional[Breakpoint] = None
        self.inspection_context: Optional[Dict[str, Any]] = None
    
    def replay_from_snapshot(self, snapshot_path: str) -> None:
        """Load snapshot and prepare for replay."""
        self.snapshot = self.snapshot_manager.load_snapshot(snapshot_path)
        self.current_position = 0
    
    def set_breakpoint(self, stage_name: str, 
                      turn_number: Optional[int] = None) -> None:
        """Set breakpoint at specific stage."""
        bp = Breakpoint(stage_name=stage_name, turn_number=turn_number)
        self.breakpoints.append(bp)
    
    def step_to_breakpoint(self) -> bool:
        """Execute until next breakpoint, return True if hit."""
        while self.current_position < len(self.snapshot.stages):
            stage = self.snapshot.stages[self.current_position]
            
            # Check if any breakpoint matches
            for bp in self.breakpoints:
                if self._matches_breakpoint(stage, bp):
                    self.paused_at = bp
                    self._capture_inspection_context(stage)
                    return True
            
            self.current_position += 1
        
        return False  # End of replay reached
    
    def inspect_at_breakpoint(self) -> Dict[str, Any]:
        """Inspect context at current breakpoint."""
        if not self.inspection_context:
            raise RuntimeError("Not paused at breakpoint")
        
        return {
            "breakpoint": self.paused_at,
            "stage": self.snapshot.stages[self.current_position],
            "context": self.inspection_context,
            "previous_stages": self.snapshot.stages[:self.current_position],
            "governance_state": self.snapshot.governance_state,
            "audit_trail": self.snapshot.audit_trail,
        }
    
    def _matches_breakpoint(self, stage: Any, bp: Breakpoint) -> bool:
        """Check if stage matches breakpoint criteria."""
        if stage.stage_name != bp.stage_name:
            return False
        if bp.turn_number and stage.stage_number != bp.turn_number:
            return False
        return True
    
    def _capture_inspection_context(self, stage: Any) -> None:
        """Capture detailed context for inspection."""
        self.inspection_context = {
            "stage_input": stage.input_data,
            "stage_output": stage.output_data,
            "stage_status": stage.status,
            "execution_time": (stage.end_time - stage.start_time).total_seconds(),
            "error": stage.error,
        }
```

**File 3: src/devx/chaos_scenarios.py (~240 lines)**
```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any

@dataclass
class ChaosScenario:
    name: str
    description: str
    trigger_condition: Callable
    failure_action: Callable
    expected_behavior: str
    validation_steps: list

class ChaosScenarios:
    """Pre-built edge case scenarios for orchestrator testing."""
    
    @staticmethod
    def token_budget_exhaustion() -> ChaosScenario:
        """Simulate token budget running out mid-workflow."""
        return ChaosScenario(
            name="token_budget_exhaustion",
            description="Token budget exhausted during Stage 3",
            trigger_condition=lambda ctx: ctx.tokens_used > ctx.token_budget * 0.9,
            failure_action=lambda ctx: ctx.halt_with_error("TOKEN_LIMIT"),
            expected_behavior="Workflow halts with TOKEN_LIMIT error, saves state",
            validation_steps=[
                "Verify continuation_decision reason == TOKEN_LIMIT",
                "Verify audit trail captures TOKEN_LIMIT event",
                "Verify snapshot can be loaded for later retry",
            ]
        )
    
    @staticmethod
    def user_rejection_at_stage() -> ChaosScenario:
        """User rejects approval at each stage."""
        return ChaosScenario(
            name="user_rejection",
            description="User rejects at approval stage",
            trigger_condition=lambda ctx: hasattr(ctx, 'approval_required'),
            failure_action=lambda ctx: ctx.user_action("REJECT"),
            expected_behavior="Workflow halts with USER_REJECTION decision",
            validation_steps=[
                "Verify continuation_decision reason == USER_REJECTION",
                "Verify rejection reason captured",
                "Verify workflow can be retried with modified input",
            ]
        )
    
    @staticmethod
    def network_error_in_lens() -> ChaosScenario:
        """Network error during LENS execution (Stage 1)."""
        return ChaosScenario(
            name="network_error_lens",
            description="Network timeout in LENS comprehension",
            trigger_condition=lambda ctx: ctx.current_stage == 1,
            failure_action=lambda ctx: ctx.raise_error("NetworkTimeout"),
            expected_behavior="Fallback to cached knowledge, continue workflow",
            validation_steps=[
                "Verify fallback mechanism engaged",
                "Verify audit logs LENS_TIMEOUT event",
                "Verify workflow continues to Stage 2",
            ]
        )
    
    @staticmethod
    def database_timeout() -> ChaosScenario:
        """Database connection times out."""
        return ChaosScenario(
            name="database_timeout",
            description="DB timeout when querying audit log",
            trigger_condition=lambda ctx: "audit_log" in ctx.operations,
            failure_action=lambda ctx: ctx.raise_error("DBConnectionTimeout"),
            expected_behavior="Retry with exponential backoff",
            validation_steps=[
                "Verify retry attempts logged",
                "Verify backoff timing correct",
                "Verify eventual success or graceful failure",
            ]
        )
    
    # ... 4 more scenarios: governance_violation, unknown_operation, etc.
```

### Success Criteria
- ✅ Snapshots capture complete workflow state
- ✅ Replay reconstructs workflow correctly
- ✅ Breakpoints work at stage boundaries
- ✅ All 6 chaos scenarios execute and validate
- ✅ Debugging guide used by next developer troubleshooting issue

---

## EXECUTION CHECKLIST

### Week 1: Planning & Foundation
- [ ] Create PHASE-22 extension for MCP validator (AC-MCP-VALID-001-002)
- [ ] Create AC entries for Knowledge QA (AC-KN-QUALITY-001-003)
- [ ] Create AC entries for Orchestrator Testing (AC-ODX-DEBUG-001-003)
- [ ] Update cortex-master.yaml with 3 new phases
- [ ] Create branches: enhancement-mcp-validator, enhancement-knowledge-qa, enhancement-devx-testing

### Week 2: MCP Compliance Implementation
- [ ] Implement ToolComplianceValidator (src/mcp/tools/validator.py)
- [ ] Write validator tests (18 tests passing)
- [ ] Create compliance checklist document
- [ ] Create developer guide
- [ ] Git checkpoint: mcp-validator-complete

### Week 3: Knowledge QA Implementation  
- [ ] Implement ConfidenceScorer (2.5 hours, 12 tests)
- [ ] Implement VerificationWorkflow (3.5 hours, 13 tests)
- [ ] Integration with IntelligentKnowledgeRouter (2 hours, 8 tests)
- [ ] Create quality standards documentation
- [ ] Git checkpoint: knowledge-qa-complete

### Week 4: Orchestrator Testing Implementation
- [ ] Implement SnapshotManager (4 hours, 18 tests)
- [ ] Implement ReplayEngine (3 hours, 15 tests)
- [ ] Implement ChaosScenarios (2 hours, integration tests)
- [ ] Create debugging guide with examples
- [ ] Git checkpoint: devx-testing-complete

### Final: Integration & Documentation
- [ ] Update cortex-vision artifacts (2 hours)
- [ ] Update cortex-builder.prompt.md with new phases
- [ ] Create completion report for all 3 enhancements
- [ ] Governance audit trail verification
- [ ] Phase lock when all tests passing

---

## GOVERNANCE REMINDERS

**Before implementing each AC:**
1. ✅ Read cortex-builder.prompt.md CORE rules section
2. ✅ Create git checkpoint with `checkpoint: before AC-XXX`
3. ✅ Write tests FIRST (RED → GREEN pattern)
4. ✅ Ensure all functions have type hints (CORE-011)
5. ✅ Ensure all classes have docstrings (CORE-012)
6. ✅ Add audit logging (AC_START → AC_EXECUTE → AC_COMPLETE)
7. ✅ Run full test suite (no regressions)
8. ✅ Update phase_tracker when AC complete

---

**Implementation Guide Version:** 1.0  
**Last Updated:** 2026-01-18  
**Status:** Ready for Development  
**Total Effort:** 25-40 hours over 4 weeks  
**Success Criteria:** All 3 enhancements complete, 100% test pass rate, governance compliance verified
