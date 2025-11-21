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

Updated: November 8, 2025 - YAML-based configuration
Now loads rules from cortex-brain/brain-protection-rules.yaml
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import yaml


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
    
    Implements 6 protection layers from brain-protection-rules.yaml:
    1. Instinct Immutability - Cannot disable TDD, skip DoD/DoR
    2. Tier Boundary Protection - Application paths not in Tier 0
    3. SOLID Compliance - No God Objects, no mode switches
    4. Hemisphere Specialization - RIGHT plans, LEFT executes
    5. Knowledge Quality - Min 3 occurrences, max 0.50 single-event confidence
    6. Commit Integrity - Brain state files excluded from commits
    """
    
    def __init__(self, log_path: Optional[Path] = None, rules_path: Optional[Path] = None):
        """
        Initialize Brain Protector.
        
        Args:
            log_path: Path to protection events log (default: corpus-callosum/protection-events.jsonl)
            rules_path: Path to protection rules YAML (default: cortex-brain/brain-protection-rules.yaml)
        """
        project_root = Path(__file__).parent.parent.parent
        
        # Set up logging path
        if log_path is None:
            log_dir = project_root / "cortex-brain" / "corpus-callosum"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "protection-events.jsonl"
        self.log_path = Path(log_path)
        
        # Load rules from YAML
        if rules_path is None:
            rules_path = project_root / "cortex-brain" / "brain-protection-rules.yaml"
        
        self.rules_path = Path(rules_path)
        self.rules_config = self._load_rules()
        
        # Extract configuration for easy access
        self.CRITICAL_PATHS = self.rules_config.get('critical_paths', [])
        self.TIER0_INSTINCTS = self.rules_config.get('tier0_instincts', [])
        self.APPLICATION_PATHS = self.rules_config.get('application_paths', [])
        self.BRAIN_STATE_FILES = self.rules_config.get('brain_state_files', [])
        self.protection_layers = self.rules_config.get('protection_layers', [])
    
    def _load_rules(self) -> Dict[str, Any]:
        """
        Load protection rules from YAML configuration file.
        
        Uses universal YAML cache for performance (99.9% faster on subsequent loads).
        First load: ~550ms, subsequent loads: ~0.1-0.5ms.
        """
        try:
            # Use universal YAML cache
            from src.utils.yaml_cache import load_yaml_cached
            return load_yaml_cached(self.rules_path)
        except ImportError:
            # Fallback to direct loading if cache not available
            try:
                import yaml
                with open(self.rules_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except ImportError:
                print("WARNING: PyYAML not installed. Using minimal fallback rules.")
                return self._get_fallback_rules()
        except FileNotFoundError:
            print(f"WARNING: Rules file not found at {self.rules_path}. Using fallback rules.")
            return self._get_fallback_rules()
    
    def _get_fallback_rules(self) -> Dict[str, Any]:
        """Provide minimal fallback rules if YAML can't be loaded."""
        return {
            'critical_paths': ["CORTEX/src/tier0/", "prompts/internal/", "cortex-brain/tier0/"],
            'tier0_instincts': ["TDD_ENFORCEMENT", "DEFINITION_OF_DONE"],
            'application_paths': ["SPA/", "KSESSIONS/", "NOOR/"],
            'brain_state_files': ["conversation-history.jsonl", "protection-events.jsonl"],
            'protection_layers': []
        }
    
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
        
        # Layer 7: SKULL Protection (Test Validation)
        violations.extend(self._check_skull_protection(request))
        
        # Layer 8: Git Checkpoint Enforcement
        violations.extend(self._check_git_checkpoint(request))
        
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
        """Check Layer 1: Instinct Immutability violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("instinct_immutability")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.INSTINCT_IMMUTABILITY):
                violations.append(self._create_violation(request, rule, ProtectionLayer.INSTINCT_IMMUTABILITY))
        
        return violations
    
    def _get_layer_by_id(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Get protection layer configuration by ID."""
        for layer in self.protection_layers:
            if layer.get('layer_id') == layer_id:
                return layer
        return None
    
    def _check_rule(self, request: ModificationRequest, rule: Dict[str, Any], layer: ProtectionLayer) -> bool:
        """Check if a rule is violated based on YAML detection config."""
        detection = rule.get('detection', {})
        
        # Check keyword-based detection
        if 'keywords' in detection:
            keywords = detection['keywords']
            scope = detection.get('scope', ['intent', 'description'])
            
            text_to_check = ""
            if 'intent' in scope:
                text_to_check += request.intent.lower() + " "
            if 'description' in scope:
                text_to_check += request.description.lower()
            
            if any(kw.lower() in text_to_check for kw in keywords):
                return True
        
        # Check combined keywords (AND logic)
        if 'combined_keywords' in detection:
            all_groups_match = True
            for group_name, group_keywords in detection['combined_keywords'].items():
                if group_name in ['logic', 'scope']:
                    continue
                
                scope = detection.get('scope', ['description'])
                text_to_check = ""
                if 'intent' in scope:
                    text_to_check += request.intent.lower() + " "
                if 'description' in scope:
                    text_to_check += request.description.lower()
                
                group_match = any(kw.lower() in text_to_check for kw in group_keywords)
                if not group_match:
                    all_groups_match = False
                    break
            
            if all_groups_match:
                return True
        
        # Check file-based detection
        if 'files' in detection:
            target_files = detection['files']
            keywords = detection.get('keywords', [])
            scope = detection.get('scope', ['intent'])
            
            # Check if any request file matches target files
            file_match = any(
                any(tf in req_file for tf in target_files)
                for req_file in request.files
            )
            
            if file_match:
                # Check keywords in scope
                text_to_check = ""
                if 'intent' in scope:
                    text_to_check += request.intent.lower() + " "
                if 'description' in scope:
                    text_to_check += request.description.lower()
                
                if any(kw.lower() in text_to_check for kw in keywords):
                    return True
        
        # Check path pattern detection
        if 'path_patterns' in detection:
            patterns = detection['path_patterns']
            contains_value = detection.get('contains', '')
            contains_any = detection.get('contains_any', '')
            
            # Expand template variables
            if contains_any == "{{application_paths}}":
                contains_any = self.APPLICATION_PATHS
            
            for file_path in request.files:
                # Normalize path separators for cross-platform compatibility
                file_lower = file_path.lower().replace('\\', '/')
                
                # Check if path matches pattern
                pattern_match = False
                for pattern in patterns:
                    pattern_lower = pattern.lower().replace('**', '')
                    if pattern_lower in file_lower:
                        pattern_match = True
                        break
                
                if pattern_match:
                    # Check contains condition
                    if contains_value and contains_value in file_lower:
                        return True
                    
                    # Check contains_any condition
                    if contains_any:
                        if isinstance(contains_any, list):
                            # Case-insensitive check
                            if any(val.lower().strip('/') in file_lower for val in contains_any):
                                return True
        
        # Check file match with keywords
        if 'files' in detection and isinstance(detection['files'], str):
            # Template variable like {{brain_state_files}}
            if detection['files'] == "{{brain_state_files}}":
                target_files = self.BRAIN_STATE_FILES
            else:
                target_files = [detection['files']]
            
            keywords = detection.get('keywords', [])
            scope = detection.get('scope', ['intent'])
            
            file_match = any(
                any(tf in req_file for tf in target_files)
                for req_file in request.files
            )
            
            if file_match:
                text_to_check = ""
                if 'intent' in scope:
                    text_to_check += request.intent.lower() + " "
                if 'description' in scope:
                    text_to_check += request.description.lower()
                
                if any(kw.lower() in text_to_check for kw in keywords):
                    return True
        
        return False
    
    def _create_violation(self, request: ModificationRequest, rule: Dict[str, Any], layer: ProtectionLayer) -> Violation:
        """Create a Violation object from YAML rule configuration."""
        severity_str = rule.get('severity', 'warning')
        severity = Severity.BLOCKED if severity_str == 'blocked' else Severity.WARNING if severity_str == 'warning' else Severity.SAFE
        
        evidence = rule.get('evidence', '')
        evidence_template = rule.get('evidence_template', '')
        
        # Format evidence template
        if evidence_template:
            evidence = evidence_template.format(
                intent=request.intent,
                description=request.description
            )
        
        # Find affected file
        file_path = None
        detection = rule.get('detection', {})
        if 'files' in detection or 'path_patterns' in detection:
            if request.files:
                file_path = request.files[0]
        
        return Violation(
            layer=layer,
            rule=rule.get('rule_id', 'UNKNOWN'),
            severity=severity,
            description=rule.get('description', 'No description'),
            evidence=evidence,
            file_path=file_path
        )
    
    def _check_tier_boundaries(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 2: Tier Boundary violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("tier_boundary")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.TIER_BOUNDARY):
                violations.append(self._create_violation(request, rule, ProtectionLayer.TIER_BOUNDARY))
        
        return violations
    
    def _check_solid_compliance(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 3: SOLID Compliance violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("solid_compliance")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.SOLID_COMPLIANCE):
                violations.append(self._create_violation(request, rule, ProtectionLayer.SOLID_COMPLIANCE))
        
        return violations
    
    def _check_hemisphere_specialization(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 4: Hemisphere Specialization violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("hemisphere_specialization")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.HEMISPHERE_SPECIALIZATION):
                violations.append(self._create_violation(request, rule, ProtectionLayer.HEMISPHERE_SPECIALIZATION))
        
        return violations
    
    def _check_knowledge_quality(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 5: Knowledge Quality violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("knowledge_quality")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.KNOWLEDGE_QUALITY):
                violations.append(self._create_violation(request, rule, ProtectionLayer.KNOWLEDGE_QUALITY))
        
        return violations
    
    def _check_skull_protection(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 7: SKULL Protection (Test Validation) using integrated SkullProtector."""
        violations = []
        
        # Detect fix claims in request
        fix_claim_keywords = ["fixed ✅", "complete ✅", "done ✅", "implemented ✅"]
        has_fix_claim = any(keyword.lower() in request.description.lower() for keyword in fix_claim_keywords)
        
        if has_fix_claim:
            # Check if tests are mentioned
            test_keywords = ["test passed", "test verified", "validated by test", "pytest"]
            has_test_validation = any(keyword.lower() in request.description.lower() for keyword in test_keywords)
            
            if not has_test_validation:
                violations.append(Violation(
                    layer=ProtectionLayer.INSTINCT_IMMUTABILITY,  # SKULL is part of Tier 0 instincts
                    rule="SKULL-001",
                    severity=Severity.BLOCKED,
                    description="Fix claimed complete without test validation (SKULL-001 violation)",
                    evidence=f"Description contains fix claim but no test validation: {request.description[:100]}"
                ))
        
        # Detect integration claims
        integration_keywords = ["integration complete", "auto-engages", "components connected"]
        has_integration_claim = any(keyword.lower() in request.description.lower() for keyword in integration_keywords)
        
        if has_integration_claim:
            e2e_keywords = ["end-to-end test", "integration test", "e2e test"]
            has_e2e_test = any(keyword.lower() in request.description.lower() for keyword in e2e_keywords)
            
            if not has_e2e_test:
                violations.append(Violation(
                    layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                    rule="SKULL-002",
                    severity=Severity.BLOCKED,
                    description="Integration claimed without end-to-end test (SKULL-002 violation)",
                    evidence=f"Description contains integration claim but no E2E test: {request.description[:100]}"
                ))
        
        # Detect CSS/UI changes
        css_keywords = ["css fixed", "style updated", "color changed", "ui improved"]
        has_css_change = any(keyword.lower() in request.description.lower() for keyword in css_keywords)
        
        if has_css_change:
            visual_keywords = ["visual test", "computed style", "playwright", "browser test"]
            has_visual_test = any(keyword.lower() in request.description.lower() for keyword in visual_keywords)
            
            if not has_visual_test:
                violations.append(Violation(
                    layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                    rule="SKULL-003",
                    severity=Severity.WARNING,
                    description="CSS/UI change without visual validation (SKULL-003 violation)",
                    evidence=f"Description contains CSS change but no visual test: {request.description[:100]}"
                ))
        
        # Detect retry attempts
        retry_keywords = ["try again", "retry", "attempt 2", "attempt 3"]
        has_retry = any(keyword.lower() in request.description.lower() for keyword in retry_keywords)
        
        if has_retry:
            diagnosis_keywords = ["diagnosed", "root cause", "cache cleared", "verified"]
            has_diagnosis = any(keyword.lower() in request.description.lower() for keyword in diagnosis_keywords)
            
            if not has_diagnosis:
                violations.append(Violation(
                    layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                    rule="SKULL-004",
                    severity=Severity.WARNING,
                    description="Retry without diagnosis (SKULL-004 violation)",
                    evidence=f"Description contains retry but no root cause analysis: {request.description[:100]}"
                ))
        
        return violations
    
    def _check_git_checkpoint(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 8: Git Checkpoint Enforcement using YAML rules."""
        violations = []
        
        # Import git checkpoint module for validation
        try:
            from src.operations.modules.git_checkpoint_module import GitCheckpointModule
            checkpoint_module = GitCheckpointModule()
        except ImportError:
            # If module not available, skip validation
            return violations
        
        # Detect development-starting keywords
        development_keywords = [
            "implement", "start development", "begin implementation",
            "fix bug", "refactor code", "add functionality",
            "create new", "modify existing", "develop feature"
        ]
        
        # Check if request is starting development work
        text_to_check = (request.intent + " " + request.description).lower()
        is_development_start = any(kw.lower() in text_to_check for kw in development_keywords)
        
        if is_development_start:
            # Validate checkpoint exists
            try:
                result = checkpoint_module.execute({
                    'operation': 'validate',
                    'required_for': request.intent
                })
                
                if not result.success:
                    # Get rule configuration from YAML
                    layer = self._get_layer_by_id("instinct_immutability")
                    rule_config = None
                    if layer:
                        for rule in layer.get('rules', []):
                            if rule.get('rule_id') == 'GIT_CHECKPOINT_ENFORCEMENT':
                                rule_config = rule
                                break
                    
                    # Create violation
                    violations.append(Violation(
                        layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                        rule="GIT_CHECKPOINT_ENFORCEMENT",
                        severity=Severity.BLOCKED,
                        description="Git checkpoint required before starting development work",
                        evidence=f"Starting development: '{request.intent}' but {result.message}",
                        file_path=None
                    ))
            
            except Exception as e:
                # Log but don't block if checkpoint validation fails
                print(f"Warning: Checkpoint validation failed: {e}")
        
        return violations
    
    def _check_commit_integrity(self, request: ModificationRequest) -> List[Violation]:
        """Check Layer 6: Commit Integrity violations using YAML rules."""
        violations = []
        layer = self._get_layer_by_id("commit_integrity")
        if not layer:
            return violations
        
        for rule in layer.get('rules', []):
            if self._check_rule(request, rule, ProtectionLayer.COMMIT_INTEGRITY):
                violations.append(self._create_violation(request, rule, ProtectionLayer.COMMIT_INTEGRITY))
        
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
        """Generate safe alternatives for violations from YAML rules."""
        alternatives = []
        
        for v in violations:
            # Find the rule in YAML config
            layer = self._get_layer_by_id(v.layer.value)
            if layer:
                for rule in layer.get('rules', []):
                    if rule.get('rule_id') == v.rule:
                        rule_alternatives = rule.get('alternatives', [])
                        alternatives.extend(rule_alternatives)
                        break
        
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
