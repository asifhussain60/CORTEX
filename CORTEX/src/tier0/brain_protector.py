"""
CORTEX Brain Protector - Architectural Integrity Guardian

Implements 6 protection layers to prevent degradation of CORTEX intelligence:
1. Instinct Immutability - Tier 0 governance rules cannot be bypassed
2. Tier Boundary Protection - Data stored in correct tier
3. SOLID Compliance - No God Objects, proper separation
4. Hemisphere Specialization - Strategic vs tactical separation
5. Knowledge Quality - Pattern validation and confidence thresholds
6. Commit Integrity - Brain state files excluded from commits

Phase 3 Task 3.2: Brain Protector Automation
Duration: 2-3 hours
Date: November 6, 2025
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class Severity(Enum):
    """Protection violation severity levels."""
    SAFE = "safe"           # No issues detected
    WARNING = "warning"     # Risky but allowable with caution
    BLOCKED = "blocked"     # Critical violation, require override


class ProtectionLayer(Enum):
    """6 protection layers."""
    INSTINCT_IMMUTABILITY = "instinct_immutability"
    TIER_BOUNDARY = "tier_boundary"
    SOLID_COMPLIANCE = "solid_compliance"
    HEMISPHERE_SPECIALIZATION = "hemisphere_specialization"
    KNOWLEDGE_QUALITY = "knowledge_quality"
    COMMIT_INTEGRITY = "commit_integrity"


@dataclass
class Violation:
    """A single protection violation."""
    layer: ProtectionLayer
    rule: str
    severity: Severity
    description: str
    evidence: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class ModificationRequest:
    """Request to modify CORTEX system."""
    intent: str
    description: str
    files: List[str]
    justification: Optional[str] = None
    user: str = "user"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProtectionResult:
    """Result of protection analysis."""
    severity: Severity
    violations: List[Violation]
    decision: str  # "ALLOW", "WARN", "BLOCK"
    message: str
    alternatives: List[str]
    override_required: bool


@dataclass
class Challenge:
    """Protection challenge presented to user."""
    timestamp: str
    request: ModificationRequest
    result: ProtectionResult
    challenge_text: str
    options: List[str]


class BrainProtector:
    """
    Automates architectural protection challenges.
    
    Implements 6 protection layers from brain-protector.md:
    1. Instinct Immutability - Cannot disable TDD, skip DoD/DoR
    2. Tier Boundary Protection - Application paths not in Tier 0
    3. SOLID Compliance - No God Objects, no mode switches
    4. Hemisphere Specialization - RIGHT plans, LEFT executes
    5. Knowledge Quality - Min 3 occurrences, max 0.50 single-event confidence
    6. Commit Integrity - Brain state files excluded from commits
    """
    
    # Critical system files that trigger high-level protection
    CRITICAL_PATHS = [
        "CORTEX/src/tier0/",
        "prompts/internal/",
        "governance/rules.md",
        "cortex-brain/tier0/",
    ]
    
    # Tier 0 instincts (immutable rules)
    TIER0_INSTINCTS = [
        "TDD_ENFORCEMENT",
        "DEFINITION_OF_READY",
        "DEFINITION_OF_DONE",
        "SOLID_PRINCIPLES",
        "LOCAL_FIRST",
    ]
    
    # Application-specific paths that don't belong in CORTEX core
    APPLICATION_PATHS = [
        "SPA/", "KSESSIONS/", "NOOR/",
        "blazor", "signalr", "canvas"
    ]
    
    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize Brain Protector.
        
        Args:
            log_path: Path to protection events log (default: corpus-callosum/protection-events.jsonl)
        """
        if log_path is None:
            # Default location
            project_root = Path(__file__).parent.parent.parent.parent
            log_dir = project_root / "cortex-brain" / "corpus-callosum"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "protection-events.jsonl"
        
        self.log_path = Path(log_path)
    
    def analyze_request(self, request: ModificationRequest) -> ProtectionResult:
        """
        Analyze modification request against all protection layers.
        
        Args:
            request: Modification request to analyze
        
        Returns:
            ProtectionResult with severity and violations
        """
        violations = []
        
        # Layer 1: Instinct Immutability
        violations.extend(self._check_instinct_immutability(request))
        
        # Layer 2: Tier Boundary Protection
        violations.extend(self._check_tier_boundaries(request))
        
        # Layer 3: SOLID Compliance
        violations.extend(self._check_solid_compliance(request))
        
        # Layer 4: Hemisphere Specialization
        violations.extend(self._check_hemisphere_specialization(request))
        
        # Layer 5: Knowledge Quality
        violations.extend(self._check_knowledge_quality(request))
        
        # Layer 6: Commit Integrity
        violations.extend(self._check_commit_integrity(request))
        
        # Determine overall severity
        if any(v.severity == Severity.BLOCKED for v in violations):
            severity = Severity.BLOCKED
            decision = "BLOCK"
            override_required = True
        elif any(v.severity == Severity.WARNING for v in violations):
            severity = Severity.WARNING
            decision = "WARN"
            override_required = False
        else:
            severity = Severity.SAFE
            decision = "ALLOW"
            override_required = False
        
        # Generate message and alternatives
        message = self._generate_message(violations, decision)
        alternatives = self._generate_alternatives(violations)
        
        return ProtectionResult(
            severity=severity,
            violations=violations,
            decision=decision,
            message=message,
            alternatives=alternatives,
            override_required=override_required
        )
    
    def _check_instinct_immutability(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 1: Instinct Immutability violations."""
        violations = []
        
        # Check for TDD bypass attempts
        bypass_keywords = ["skip test", "bypass tdd", "no tests", "disable tdd", "skip validation"]
        intent_lower = request.intent.lower()
        desc_lower = request.description.lower()
        
        if any(kw in intent_lower or kw in desc_lower for kw in bypass_keywords):
            violations.append(Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="TDD_ENFORCEMENT",
                severity=Severity.BLOCKED,
                description="Attempt to bypass Test-Driven Development requirement",
                evidence=f"Intent: '{request.intent}'"
            ))
        
        # Check for DoD/DoR modifications
        dod_keywords = ["skip validation", "bypass done", "disable error check", "allow warnings"]
        if any(kw in intent_lower or kw in desc_lower for kw in dod_keywords):
            violations.append(Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="DEFINITION_OF_DONE",
                severity=Severity.BLOCKED,
                description="Attempt to bypass Definition of Done (zero errors, zero warnings)",
                evidence=f"Description: '{request.description}'"
            ))
        
        return violations
    
    def _check_tier_boundaries(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 2: Tier Boundary violations."""
        violations = []
        
        for file_path in request.files:
            file_lower = file_path.lower()
            
            # Check for application data in Tier 0
            if "tier0" in file_lower or "governance" in file_lower:
                # Check both APPLICATION_PATHS and common app names
                app_indicators = self.APPLICATION_PATHS + ["ksessions", "noor"]
                if any(app_path.lower() in file_lower for app_path in app_indicators):
                    violations.append(Violation(
                        layer=ProtectionLayer.TIER_BOUNDARY,
                        rule="TIER0_APPLICATION_DATA",
                        severity=Severity.BLOCKED,
                        description=f"Application-specific path in Tier 0 (immutable governance)",
                        file_path=file_path,
                        evidence="Tier 0 is for generic CORTEX principles only"
                    ))
            
            # Check for conversation data in Tier 2
            if "tier2" in file_lower and "conversation" in file_lower:
                violations.append(Violation(
                    layer=ProtectionLayer.TIER_BOUNDARY,
                    rule="TIER2_CONVERSATION_DATA",
                    severity=Severity.WARNING,
                    description=f"Conversation data should be in Tier 1, not Tier 2",
                    file_path=file_path,
                    evidence="Tier 2 is for aggregated patterns, not raw conversations"
                ))
        
        return violations
    
    def _check_solid_compliance(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 3: SOLID Compliance violations."""
        violations = []
        
        # Check for God Object patterns
        god_object_keywords = ["add mode", "add switch", "handle all", "do everything"]
        intent_lower = request.intent.lower()
        
        if any(kw in intent_lower for kw in god_object_keywords):
            violations.append(Violation(
                layer=ProtectionLayer.SOLID_COMPLIANCE,
                rule="SINGLE_RESPONSIBILITY",
                severity=Severity.WARNING,
                description="Potential God Object pattern detected (adding multiple responsibilities)",
                evidence=f"Intent: '{request.intent}'"
            ))
        
        # Check for hardcoded dependencies
        hardcoded_keywords = ["hardcode path", "fixed path", "absolute path", "inline config"]
        desc_lower = request.description.lower()
        
        if any(kw in desc_lower for kw in hardcoded_keywords):
            violations.append(Violation(
                layer=ProtectionLayer.SOLID_COMPLIANCE,
                rule="DEPENDENCY_INVERSION",
                severity=Severity.WARNING,
                description="Hardcoded dependency detected (violates DIP)",
                evidence=f"Description: '{request.description}'"
            ))
        
        return violations
    
    def _check_hemisphere_specialization(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 4: Hemisphere Specialization violations."""
        violations = []
        
        # Check for strategic logic in LEFT brain (tactical hemisphere)
        left_brain_files = ["code-executor.md", "test-generator.md", "error-corrector.md"]
        strategic_keywords = ["create plan", "estimate time", "assess risk", "strategy"]
        
        for file_path in request.files:
            if any(lf in file_path for lf in left_brain_files):
                if any(kw in request.intent.lower() for kw in strategic_keywords):
                    violations.append(Violation(
                        layer=ProtectionLayer.HEMISPHERE_SPECIALIZATION,
                        rule="LEFT_BRAIN_TACTICAL",
                        severity=Severity.WARNING,
                        description=f"Strategic planning logic in tactical executor",
                        file_path=file_path,
                        evidence="LEFT brain should execute, not plan"
                    ))
        
        # Check for tactical execution in RIGHT brain (strategic hemisphere)
        right_brain_files = ["work-planner.md", "intent-router.md"]
        tactical_keywords = ["write code", "run test", "execute", "implement"]
        
        for file_path in request.files:
            if any(rf in file_path for rf in right_brain_files):
                if any(kw in request.intent.lower() for kw in tactical_keywords):
                    violations.append(Violation(
                        layer=ProtectionLayer.HEMISPHERE_SPECIALIZATION,
                        rule="RIGHT_BRAIN_STRATEGIC",
                        severity=Severity.WARNING,
                        description=f"Tactical execution logic in strategic planner",
                        file_path=file_path,
                        evidence="RIGHT brain should plan, not execute"
                    ))
        
        return violations
    
    def _check_knowledge_quality(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 5: Knowledge Quality violations."""
        violations = []
        
        # Check for single-event high confidence
        high_conf_keywords = ["confidence: 1.0", "confidence=1.0", "confidence: 0.95"]
        single_event_keywords = ["first occurrence", "single event", "occurrences: 1"]
        
        desc_lower = request.description.lower()
        
        has_high_conf = any(kw in desc_lower for kw in high_conf_keywords)
        has_single_event = any(kw in desc_lower for kw in single_event_keywords)
        
        if has_high_conf and has_single_event:
            violations.append(Violation(
                layer=ProtectionLayer.KNOWLEDGE_QUALITY,
                rule="MIN_OCCURRENCES",
                severity=Severity.WARNING,
                description="High confidence (>0.50) with single occurrence",
                evidence="Require 3+ occurrences for confidence >0.50"
            ))
        
        return violations
    
    def _check_commit_integrity(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 6: Commit Integrity violations."""
        violations = []
        
        # Brain state files that shouldn't be committed
        brain_state_files = [
            "conversation-history.jsonl",
            "conversation-context.jsonl",
            "events.jsonl",
            "development-context.yaml",
            "protection-events.jsonl"
        ]
        
        for file_path in request.files:
            if any(bsf in file_path for bsf in brain_state_files):
                if "commit" in request.intent.lower():
                    violations.append(Violation(
                        layer=ProtectionLayer.COMMIT_INTEGRITY,
                        rule="BRAIN_STATE_GITIGNORE",
                        severity=Severity.WARNING,
                        description=f"Brain state file should not be committed",
                        file_path=file_path,
                        evidence="Add to .gitignore to prevent pollution"
                    ))
        
        return violations
    
    def _generate_message(self, violations: List[Violation], decision: str) -> str:
        """Generate human-readable message for protection result."""
        if not violations:
            return "✅ Modification appears safe. No violations detected."
        
        if decision == "BLOCK":
            msg = "🛡️ BLOCKED: Critical architectural violations detected.\n\n"
        elif decision == "WARN":
            msg = "⚠️ WARNING: Risky patterns detected. Proceed with caution.\n\n"
        else:
            msg = "ℹ️ NOTICE: Minor issues detected.\n\n"
        
        msg += "Violations:\n"
        for v in violations:
            msg += f"  • [{v.layer.value}] {v.rule}: {v.description}\n"
            if v.evidence:
                msg += f"    Evidence: {v.evidence}\n"
        
        return msg
    
    def _generate_alternatives(self, violations: List[Violation]) -> List[str]:
        """Generate safe alternatives for violations."""
        alternatives = []
        
        for v in violations:
            if v.rule == "TDD_ENFORCEMENT":
                alternatives.append("1. Write failing test first (RED phase)")
                alternatives.append("2. Create spike branch for exploration (throwaway)")
            
            elif v.rule == "TIER0_APPLICATION_DATA":
                alternatives.append("1. Store in Tier 2 with scope='application'")
                alternatives.append("2. Keep generic principles in Tier 0")
            
            elif v.rule == "SINGLE_RESPONSIBILITY":
                alternatives.append("1. Create dedicated agent for new responsibility")
                alternatives.append("2. Use composition instead of adding modes")
            
            elif v.rule == "LEFT_BRAIN_TACTICAL":
                alternatives.append("1. Move planning logic to work-planner.md")
                alternatives.append("2. Keep execution logic in code-executor.md")
        
        # Deduplicate
        return list(set(alternatives))
    
    def generate_challenge(self, violations: List[Violation]) -> Challenge:
        """
        Generate challenge with threat description, risks, and alternatives.
        
        Args:
            violations: List of violations detected
        
        Returns:
            Challenge object with formatted text and options
        """
        timestamp = datetime.now().isoformat()
        
        # Create dummy request for now (would come from actual request)
        request = ModificationRequest(
            intent="User modification request",
            description="Details not available",
            files=[]
        )
        
        result = ProtectionResult(
            severity=Severity.BLOCKED if any(v.severity == Severity.BLOCKED for v in violations) else Severity.WARNING,
            violations=violations,
            decision="BLOCK" if any(v.severity == Severity.BLOCKED for v in violations) else "WARN",
            message=self._generate_message(violations, "BLOCK" if any(v.severity == Severity.BLOCKED for v in violations) else "WARN"),
            alternatives=self._generate_alternatives(violations),
            override_required=any(v.severity == Severity.BLOCKED for v in violations)
        )
        
        challenge_text = f"""
═══════════════════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

Timestamp: {timestamp}
Severity: {result.severity.value.upper()}
Decision: {result.decision}

{result.message}

SAFE ALTERNATIVES:
{chr(10).join(result.alternatives) if result.alternatives else "  No alternatives available"}

═══════════════════════════════════════════════

Options:
  1. Accept recommended alternative (SAFE)
  2. Provide different approach (REVIEW)
  3. Type 'OVERRIDE' with justification (RISKY)

Your choice:
"""
        
        options = ["Accept alternative", "Different approach", "Override with justification"]
        
        return Challenge(
            timestamp=timestamp,
            request=request,
            result=result,
            challenge_text=challenge_text,
            options=options
        )
    
    def log_event(self, challenge: Challenge, user_decision: str, override_justification: Optional[str] = None):
        """
        Log protection event to corpus callosum.
        
        Args:
            challenge: Protection challenge
            user_decision: User's decision (accept/different/override)
            override_justification: Justification if user overrode
        """
        event = {
            "timestamp": challenge.timestamp,
            "event": "brain_protector_challenge",
            "request": {
                "intent": challenge.request.intent,
                "description": challenge.request.description,
                "files": challenge.request.files,
                "justification": challenge.request.justification
            },
            "violations": [
                {
                    "layer": v.layer.value,
                    "rule": v.rule,
                    "severity": v.severity.value,
                    "description": v.description,
                    "evidence": v.evidence,
                    "file_path": v.file_path
                }
                for v in challenge.result.violations
            ],
            "decision": challenge.result.decision,
            "severity": challenge.result.severity.value,
            "alternatives_suggested": challenge.result.alternatives,
            "user_decision": user_decision,
            "override_justification": override_justification,
            "override_required": challenge.result.override_required
        }
        
        # Append to log
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
