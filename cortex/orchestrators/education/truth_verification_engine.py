"""
Truth Verification Engine for ASK Mode.

Phase 22 - P0 Week 1: Verify claims against implementation reality.

This engine extracts evidence from:
1. File system (implementation files exist)
2. AST analysis (class/function definitions)
3. wiring.yaml entries
4. MCP tool catalog
5. Test coverage

Authority: cortex-registry/_cortex-master/phases/active/phase-22-ask-mode-system.yaml
"""
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class VerificationStatus(Enum):
    """Claim verification status."""
    VERIFIED = "verified"  # Claim is true (confidence >= 0.7)
    REFUTED = "refuted"    # Claim is false (confidence >= 0.7)
    UNCERTAIN = "uncertain"  # Not enough evidence (confidence < 0.7)


@dataclass
class ImplementationEvidence:
    """Evidence from implementation files."""
    file_path: str
    line_number: int
    evidence_type: str  # file_exists, class_definition, test_exists, wiring_entry, etc
    excerpt: str
    confidence: float  # 0.0-1.0


@dataclass
class TruthVerificationResult:
    """Result of truth verification."""
    status: VerificationStatus
    confidence: float  # 0.0-1.0
    evidence: List[ImplementationEvidence]
    refutation_reason: Optional[str] = None


class TruthVerificationEngine:
    """
    Verify claims about CORTEX against implementation reality.

    Phase 22: Truth Verification

    Example:
        >>> engine = TruthVerificationEngine()
        >>> result = engine.verify_claim(
        ...     claim="CORTEX has a MasterOrchestrator",
        ...     context={"repo_root": "/path/to/cortex"}
        ... )
        >>> result.status
        VerificationStatus.VERIFIED
    """

    def __init__(self):
        """Initialize TruthVerificationEngine."""
        self.logger = logging.getLogger(__name__)

    def verify_claim(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> TruthVerificationResult:
        """
        Verify claim against implementation reality.

        Args:
            claim: User's claim to verify
            context: Context including repo_root

        Returns:
            TruthVerificationResult with status, confidence, evidence

        Example:
            >>> engine.verify_claim(
            ...     "CORTEX has MasterOrchestrator",
            ...     {"repo_root": "/path/to/cortex"}
            ... )
            TruthVerificationResult(status=VERIFIED, confidence=0.9, ...)
        """
        # Validate input
        if not claim or not claim.strip():
            return TruthVerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0.0,
                evidence=[],
                refutation_reason="Empty claim provided"
            )

        repo_root_str = context.get("repo_root")
        if not repo_root_str:
            return TruthVerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0.0,
                evidence=[],
                refutation_reason="No repository root provided"
            )

        repo_root = Path(repo_root_str)
        if not repo_root.exists():
            return TruthVerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0.0,
                evidence=[],
                refutation_reason=f"Repository root does not exist: {repo_root}"
            )

        # Extract component name from claim
        component = self._extract_component(claim)

        # Gather evidence
        evidence = self.find_implementation_evidence(component, repo_root)

        # Calculate confidence
        confidence = self.calculate_confidence(evidence)

        # Determine status
        if len(evidence) > 0 and confidence >= 0.65:
            status = VerificationStatus.VERIFIED
            refutation = None
        elif len(evidence) == 0 and confidence < 0.3:
            status = VerificationStatus.REFUTED
            refutation = f"No implementation found for '{component}'"
        else:
            status = VerificationStatus.UNCERTAIN
            refutation = None

        return TruthVerificationResult(
            status=status,
            confidence=confidence,
            evidence=evidence,
            refutation_reason=refutation
        )

    def find_implementation_evidence(
        self,
        component: str,
        repo_root: Path
    ) -> List[ImplementationEvidence]:
        """
        Find implementation evidence for component.

        Args:
            component: Component name to search for
            repo_root: CORTEX repository root

        Returns:
            List of ImplementationEvidence
        """
        evidence = []

        # Search for Python files
        component_lower = component.lower().replace("orchestrator", "")
        search_patterns = [
            f"**/{component.lower()}.py",
            f"**/{component_lower}*orchestrator.py",
            f"**/orchestrators/**/*{component_lower}*.py"
        ]

        for pattern in search_patterns:
            for file_path in repo_root.glob(pattern):
                if file_path.is_file():
                    # File exists evidence
                    evidence.append(ImplementationEvidence(
                        file_path=str(file_path.relative_to(repo_root)),
                        line_number=1,
                        evidence_type="file_exists",
                        excerpt=file_path.name,
                        confidence=0.7
                    ))

                    # Check for class definition
                    try:
                        content = file_path.read_text()
                        class_pattern = rf"class\s+{re.escape(component)}"
                        for i, line in enumerate(content.split('\n'), 1):
                            if re.search(class_pattern, line, re.IGNORECASE):
                                evidence.append(ImplementationEvidence(
                                    file_path=str(file_path.relative_to(repo_root)),
                                    line_number=i,
                                    evidence_type="class_definition",
                                    excerpt=line.strip(),
                                    confidence=0.9
                                ))
                    except Exception as e:
                        self.logger.debug(f"Error reading {file_path}: {e}")

        # Search for test files
        test_patterns = [
            f"**/test_{component.lower()}.py",
            f"**/test_*{component_lower}*.py"
        ]

        for pattern in test_patterns:
            for file_path in repo_root.glob(pattern):
                if file_path.is_file():
                    evidence.append(ImplementationEvidence(
                        file_path=str(file_path.relative_to(repo_root)),
                        line_number=1,
                        evidence_type="test_exists",
                        excerpt=file_path.name,
                        confidence=0.8
                    ))

        return evidence

    def verify_wiring(
        self,
        component: str,
        repo_root: Path
    ) -> TruthVerificationResult:
        """
        Verify component exists in wiring.yaml.

        Args:
            component: Component name to verify
            repo_root: CORTEX repository root

        Returns:
            TruthVerificationResult
        """
        wiring_path = repo_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"

        if not wiring_path.exists():
            return TruthVerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0.0,
                evidence=[],
                refutation_reason="wiring.yaml not found"
            )

        try:
            with open(wiring_path) as f:
                wiring_data = yaml.safe_load(f)

            # Search for component in orchestrators
            found = False
            for section in ['core', 'domain', 'support']:
                orchestrators = wiring_data.get('orchestrators', {}).get(section, [])
                for orch in orchestrators:
                    if orch.get('name') == component:
                        found = True
                        evidence = [ImplementationEvidence(
                            file_path=str(wiring_path.relative_to(repo_root)),
                            line_number=1,
                            evidence_type="wiring_entry",
                            excerpt=f"- name: {component}",
                            confidence=0.85
                        )]
                        return TruthVerificationResult(
                            status=VerificationStatus.VERIFIED,
                            confidence=0.85,
                            evidence=evidence
                        )

            if not found:
                return TruthVerificationResult(
                    status=VerificationStatus.REFUTED,
                    confidence=0.8,
                    evidence=[],
                    refutation_reason=f"{component} not found in wiring.yaml"
                )

        except Exception as e:
            return TruthVerificationResult(
                status=VerificationStatus.UNCERTAIN,
                confidence=0.0,
                evidence=[],
                refutation_reason=f"Error reading wiring.yaml: {e}"
            )

    def verify_mcp_tool(
        self,
        tool_name: str,
        repo_root: Path
    ) -> TruthVerificationResult:
        """
        Verify MCP tool exists in catalog.

        Args:
            tool_name: MCP tool name
            repo_root: CORTEX repository root

        Returns:
            TruthVerificationResult
        """
        # Search for MCP tool in multiple locations
        search_paths = [
            repo_root / "cortex" / "mcp" / "tools",
            repo_root / "cortex" / "mcp",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Search for tool definition in Python files
            for tool_file in search_path.rglob("*.py"):
                try:
                    content = tool_file.read_text()
                    # Look for function name or @mcp_tool decorator
                    if f"def {tool_name}" in content or f'"{tool_name}"' in content or f"'{tool_name}'" in content:
                        evidence = [ImplementationEvidence(
                            file_path=str(tool_file.relative_to(repo_root)),
                            line_number=1,
                            evidence_type="mcp_tool_definition",
                            excerpt=f"Tool: {tool_name}",
                            confidence=0.8
                        )]
                        return TruthVerificationResult(
                            status=VerificationStatus.VERIFIED,
                            confidence=0.8,
                            evidence=evidence
                        )
                except Exception as e:
                    self.logger.debug(f"Error reading {tool_file}: {e}")

        return TruthVerificationResult(
            status=VerificationStatus.REFUTED,
            confidence=0.8,
            evidence=[],
            refutation_reason=f"MCP tool '{tool_name}' not found in catalog"
        )

    def calculate_confidence(
        self,
        evidence: List[ImplementationEvidence]
    ) -> float:
        """
        Calculate overall confidence from evidence.

        Args:
            evidence: List of evidence items

        Returns:
            Confidence score (0.0-1.0)

        Algorithm:
        - No evidence: 0.0
        - Weak evidence (docs only): < 0.5
        - Moderate evidence (file exists): 0.5-0.7
        - Strong evidence (implementation + tests): >= 0.8
        """
        if not evidence:
            return 0.0

        # Weight by evidence type
        type_weights = {
            "class_definition": 1.0,
            "test_exists": 0.9,
            "wiring_entry": 0.85,
            "file_exists": 0.7,
            "mcp_tool_definition": 0.8,
            "documentation_mention": 0.3
        }

        weighted_sum = sum(
            e.confidence * type_weights.get(e.evidence_type, 0.5)
            for e in evidence
        )

        # Average with cap at 1.0
        confidence = min(weighted_sum / len(evidence), 1.0)

        # Boost if multiple evidence types
        unique_types = len(set(e.evidence_type for e in evidence))
        if unique_types >= 3:
            confidence = min(confidence * 1.1, 1.0)

        return confidence

    def _extract_component(self, claim: str) -> str:
        """
        Extract component name from claim.

        Args:
            claim: User's claim

        Returns:
            Component name

        Example:
            >>> engine._extract_component("CORTEX has MasterOrchestrator")
            "MasterOrchestrator"
        """
        # Look for capitalized words (likely component names)
        words = claim.split()
        for word in words:
            # Check if word looks like an orchestrator name
            if "Orchestrator" in word:
                return word.strip(",.;:!?")
            # Check if word is capitalized and not a common word
            if word[0].isupper() and word not in ["CORTEX", "The", "A", "An", "Has", "Is"]:
                return word.strip(",.;:!?")

        # Default: return cleaned claim
        return claim.strip()
