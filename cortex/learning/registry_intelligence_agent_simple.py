# Universal Orchestrator Wiring System
# Simplified implementation for immediate testing

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

@dataclass
class OrchestratorDiscovery:
    """Represents a discovered orchestrator."""
    name: str
    file_path: Path
    class_name: str
    keywords: Set[str]
    orchestrator_type: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "file_path": str(self.file_path),
            "class_name": self.class_name,
            "keywords": list(self.keywords),
            "type": self.orchestrator_type,
            "confidence": self.confidence
        }

@dataclass
class RegistryGap:
    """Represents a gap in orchestrator registry."""
    orchestrator: OrchestratorDiscovery
    gap_type: str
    impact: str
    suggested_fix: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "orchestrator": self.orchestrator.to_dict(),
            "gap_type": self.gap_type,
            "impact": self.impact,
            "suggested_fix": self.suggested_fix
        }

class RegistryIntelligenceAgent:
    """Universal orchestrator discovery and wiring system."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize registry intelligence agent."""
        self.workspace_root = workspace_root or Path.cwd()
        self._discovery_cache: Dict[str, OrchestratorDiscovery] = {}

        # Intent keyword patterns for universal detection
        self.intent_patterns = {
            "deploy": ["deploy", "deployment", "production", "release", "publish"],
            "test": ["test", "testing", "tdd", "unit", "integration"],
            "refactor": ["refactor", "cleanup", "improve", "optimize"],
            "analyze": ["analyze", "analysis", "examine", "inspect"],
            "onboard": ["onboard", "setup", "initialize", "bootstrap"],
            "plan": ["plan", "planning", "phase", "stage", "roadmap"],
            "debug": ["debug", "troubleshoot", "diagnose", "fix"],
            "audit": ["audit", "compliance", "governance", "security"],
        }

    def scan_for_orchestrators(self) -> List[OrchestratorDiscovery]:
        """Scan for all orchestrators in the workspace."""
        if self._discovery_cache:
            return list(self._discovery_cache.values())

        discoveries = []
        orchestrator_dirs = [
            self.workspace_root / "cortex" / "orchestrators",
            self.workspace_root / "cortex" / "domain_orchestrators",
            self.workspace_root / "cortex_brain" / "governance"
        ]

        for directory in orchestrator_dirs:
            if directory.exists():
                discoveries.extend(self._scan_directory(directory))

        # Cache results
        for discovery in discoveries:
            self._discovery_cache[discovery.name] = discovery

        return discoveries

    def _scan_directory(self, directory: Path) -> List[OrchestratorDiscovery]:
        """Scan a directory for orchestrator files."""
        discoveries = []

        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                discoveries.extend(self._analyze_file(py_file))
            except Exception as e:
                logger.debug(f"Failed to analyze {py_file}: {e}")

        return discoveries

    def _analyze_file(self, file_path: Path) -> List[OrchestratorDiscovery]:
        """Analyze a Python file for orchestrator classes."""
        discoveries = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_orchestrator_class(node, content):
                        discovery = self._create_discovery(node, file_path, content)
                        if discovery:
                            discoveries.append(discovery)

        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")

        return discoveries

    def _is_orchestrator_class(self, class_node: ast.ClassDef, content: str) -> bool:
        """Check if class is an orchestrator."""
        name = class_node.name.lower()

        # Direct name patterns
        if any(pattern in name for pattern in ["orchestrator", "handler", "engine", "manager"]):
            return True

        # Check for inheritance patterns
        for base in class_node.bases:
            if hasattr(base, 'id') and base.id:
                base_name = base.id.lower()
                if any(pattern in base_name for pattern in ["orchestrator", "protocol", "interface"]):
                    return True

        return False

    def _create_discovery(self, class_node: ast.ClassDef, file_path: Path, content: str) -> Optional[OrchestratorDiscovery]:
        """Create orchestrator discovery from AST node."""
        try:
            # Extract keywords from docstring and comments
            keywords = self._extract_keywords(class_node, content)

            # Determine orchestrator type
            orchestrator_type = self._determine_type(class_node.name, keywords)

            # Calculate confidence
            confidence = self._calculate_confidence(class_node, keywords)

            return OrchestratorDiscovery(
                name=class_node.name,
                file_path=file_path,
                class_name=class_node.name,
                keywords=keywords,
                orchestrator_type=orchestrator_type,
                confidence=confidence
            )

        except Exception as e:
            logger.debug(f"Failed to create discovery for {class_node.name}: {e}")
            return None

    def _extract_keywords(self, class_node: ast.ClassDef, content: str) -> Set[str]:
        """Extract intent keywords from class."""
        keywords = set()

        # From class name
        name_parts = class_node.name.lower().split("_") + class_node.name.lower().split()
        keywords.update(name_parts)

        # From docstring
        if class_node.body and isinstance(class_node.body[0], ast.Expr):
            if hasattr(class_node.body[0].value, 's'):
                docstring = class_node.body[0].value.s.lower()
                for intent, patterns in self.intent_patterns.items():
                    if any(pattern in docstring for pattern in patterns):
                        keywords.add(intent)

        return keywords

    def _determine_type(self, class_name: str, keywords: Set[str]) -> str:
        """Determine orchestrator type from name and keywords."""
        name_lower = class_name.lower()

        # Direct mapping from name
        if "deploy" in name_lower or "deploy" in keywords:
            return "deployment"
        elif "test" in name_lower or "tdd" in name_lower or "test" in keywords:
            return "testing"
        elif "refactor" in name_lower or "refactor" in keywords:
            return "refactoring"
        elif "analyze" in name_lower or "lens" in name_lower or "analyze" in keywords:
            return "analysis"
        elif "onboard" in name_lower or "onboard" in keywords:
            return "onboarding"
        elif "plan" in name_lower or "plan" in keywords:
            return "planning"
        elif "debug" in name_lower or "debug" in keywords:
            return "debugging"
        elif "audit" in name_lower or "audit" in keywords:
            return "auditing"
        else:
            return "general"

    def _calculate_confidence(self, class_node: ast.ClassDef, keywords: Set[str]) -> float:
        """Calculate confidence score for orchestrator detection."""
        score = 0.0

        # Name patterns
        name_lower = class_node.name.lower()
        if "orchestrator" in name_lower:
            score += 0.4
        elif any(pattern in name_lower for pattern in ["handler", "engine", "manager"]):
            score += 0.2

        # Keyword matches
        if keywords:
            score += min(0.3, len(keywords) * 0.1)

        # Method patterns
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_name = node.name.lower()
                if method_name in ["execute", "orchestrate", "process", "handle"]:
                    score += 0.2
                    break

        return min(1.0, score)

    def detect_registry_gaps(self, discoveries: Optional[List[OrchestratorDiscovery]] = None) -> List[RegistryGap]:
        """Detect gaps in orchestrator registry."""
        if discoveries is None:
            discoveries = self.scan_for_orchestrators()

        gaps = []

        for discovery in discoveries:
            # For now, just mark as unregistered if we found it
            # In full implementation, would check against OrchestratorLookup
            gap = RegistryGap(
                orchestrator=discovery,
                gap_type="unregistered",
                impact="high" if discovery.confidence > 0.7 else "medium",
                suggested_fix=f"Register {discovery.name} with keyword mapping for {discovery.orchestrator_type}"
            )
            gaps.append(gap)

        return gaps

    def validate_universal_wiring(self) -> Dict[str, Any]:
        """Validate universal orchestrator wiring."""
        discoveries = self.scan_for_orchestrators()
        gaps = self.detect_registry_gaps(discoveries)

        # Analyze coverage
        intent_coverage = {}
        for intent in self.intent_patterns:
            matching_orchestrators = [
                d for d in discoveries
                if intent in d.keywords or d.orchestrator_type == intent
            ]
            intent_coverage[intent] = {
                "count": len(matching_orchestrators),
                "orchestrators": [d.name for d in matching_orchestrators],
                "covered": len(matching_orchestrators) > 0
            }

        return {
            "discovered_orchestrators": len(discoveries),
            "registry_gaps": len(gaps),
            "intent_coverage": intent_coverage,
            "coverage_percentage": sum(1 for c in intent_coverage.values() if c["covered"]) / len(intent_coverage) * 100,
            "discoveries": [d.to_dict() for d in discoveries],
            "gaps": [g.to_dict() for g in gaps]
        }

def get_registry_intelligence_agent() -> Optional[RegistryIntelligenceAgent]:
    """Get registry intelligence agent instance."""
    try:
        return RegistryIntelligenceAgent()
    except Exception as e:
        logger.error(f"Failed to create registry intelligence agent: {e}")
        return None
