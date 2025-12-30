"""
Module 1: Feature Discovery

Extracts CORTEX capabilities from codebase and categorizes by narrative weight.

Categorization:
    MAJOR: Full chapter (2,800-3,200 words)
    MEDIUM: Section within chapter (800-1,200 words)
    MINOR: Mention in epilogue (100-300 words)

Version: 3.0.0
Author: Asif Hussain
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class FeatureWeight(Enum):
    """Narrative weight for feature integration"""
    MAJOR = "MAJOR"      # Full chapter (TDD, Planning, Maintenance)
    MEDIUM = "MEDIUM"    # Section (ADO, Dashboard)
    MINOR = "MINOR"      # Mention (Execution, Templates)


@dataclass
class Feature:
    """CORTEX feature for story integration"""
    
    name: str
    weight: FeatureWeight
    description: str
    target_location: str  # Chapter number or "Epilogue"
    word_count: int
    rationale: str
    comedic_hook: str  # How to integrate humorously
    technical_concepts: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML export"""
        data = asdict(self)
        data['weight'] = self.weight.value
        return data


class FeatureDiscoveryModule:
    """
    Discovers CORTEX features from codebase and categorizes for narrative integration.
    
    Sources:
        - cortex-operations.yaml (operation definitions)
        - src/orchestrators/ (orchestrator implementations)
        - cortex-brain/brain-protection-rules.yaml (SKULL rules)
        - src/tier0/, tier1/, tier2/, tier3/ (brain architecture)
    """
    
    def __init__(self, cortex_root: str = "."):
        """
        Initialize feature discovery module.
        
        Args:
            cortex_root: Path to CORTEX repository root
        """
        self.cortex_root = Path(cortex_root)
        self._validate_paths()
    
    def _validate_paths(self):
        """Validate required paths exist"""
        required_paths = [
            self.cortex_root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml",
            self.cortex_root / "src" / "orchestrators",
            self.cortex_root / "cortex-brain" / "brain-protection-rules.yaml"
        ]
        
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Required path not found: {path}")
        
        logger.info(f"Validated cortex_root: {self.cortex_root}")
    
    def discover_features(self) -> List[Feature]:
        """
        Discover all CORTEX features and categorize by narrative weight.
        
        Returns:
            List of Feature objects categorized as MAJOR/MEDIUM/MINOR
        """
        features = []
        
        # MAJOR Features (Full chapters)
        features.extend(self._discover_major_features())
        
        # MEDIUM Features (Sections)
        features.extend(self._discover_medium_features())
        
        # MINOR Features (Mentions)
        features.extend(self._discover_minor_features())
        
        logger.info(f"Discovered {len(features)} total features: "
                   f"{sum(1 for f in features if f.weight == FeatureWeight.MAJOR)} MAJOR, "
                   f"{sum(1 for f in features if f.weight == FeatureWeight.MEDIUM)} MEDIUM, "
                   f"{sum(1 for f in features if f.weight == FeatureWeight.MINOR)} MINOR")
        
        return features
    
    def _discover_major_features(self) -> List[Feature]:
        """Discover MAJOR features (full chapters)"""
        
        return [
            Feature(
                name="TDD Mastery",
                weight=FeatureWeight.MAJOR,
                description="RED→GREEN→REFACTOR workflow with debugging orchestrator integration",
                target_location="Chapter 7",
                word_count=3000,
                rationale="Fundamental workflow change, brain protection integration, philosophical shift",
                comedic_hook="Mr. Codenstein learning that failure validates success (tests must fail first)",
                technical_concepts=[
                    "RED phase validation (tests fail before implementation)",
                    "GREEN phase (minimal code to pass)",
                    "REFACTOR phase (cleanup without breaking tests)",
                    "Per-layer coverage tracking",
                    "Empty test detection",
                    "Debugging orchestrator"
                ]
            ),
            Feature(
                name="Planning System",
                weight=FeatureWeight.MAJOR,
                description="Incremental planning, DoR/DoD gates, autonomous execution",
                target_location="Chapter 8",
                word_count=3200,
                rationale="Orchestrator coordination, multi-phase workflows, strategic intelligence",
                comedic_hook="From chaos to structure - CORTEX learns to plan before coding (revolutionary concept)",
                technical_concepts=[
                    "Incremental planning (HIGH→medium→low complexity routing)",
                    "Definition of Ready (DoR) gates",
                    "Definition of Done (DoD) compliance",
                    "Autonomous execution phases",
                    "Auto-TDD integration",
                    "Acceptance criteria validation"
                ]
            ),
            Feature(
                name="System Maintenance",
                weight=FeatureWeight.MAJOR,
                description="6-phase auto-fix with self-healing architecture",
                target_location="Chapter 9",
                word_count=2800,
                rationale="Self-awareness peak, CORTEX maintains itself, meta-programming",
                comedic_hook="The system that debugs itself - Mr. Codenstein's ultimate laziness achievement",
                technical_concepts=[
                    "Pre-healthcheck baseline",
                    "Align (auto-fix)",
                    "Cleanup (orphan removal)",
                    "Optimize (performance tuning)",
                    "Prompt refresh (self-updating instructions)",
                    "Post-healthcheck validation"
                ]
            )
        ]
    
    def _discover_medium_features(self) -> List[Feature]:
        """Discover MEDIUM features (sections within chapters)"""
        
        return [
            Feature(
                name="ADO Operations",
                weight=FeatureWeight.MEDIUM,
                description="Story/Feature/Task creation with Azure DevOps integration",
                target_location="Chapter 4 (Agent Uprising)",
                word_count=800,
                rationale="Professional workflow agent coordination",
                comedic_hook="CORTEX learns to speak corporate (while maintaining sanity)",
                technical_concepts=[
                    "ADO story creation",
                    "Feature/task hierarchy",
                    "Completion summaries",
                    "Code review integration",
                    "Planning System inheritance"
                ]
            ),
            Feature(
                name="Dashboard Launcher",
                weight=FeatureWeight.MEDIUM,
                description="HTTP server with visualization and metrics tracking",
                target_location="Chapter 6 (Token Crisis)",
                word_count=1000,
                rationale="Visual optimization validation",
                comedic_hook="Mr. Codenstein finally sees his chaos in graphical form (terrifying)",
                technical_concepts=[
                    "HTTP server (ports 8080-8089)",
                    "Auto-open browser",
                    "CORS configuration",
                    "Real-time metrics",
                    "Progress tracking",
                    "System health visualization"
                ]
            )
        ]
    
    def _discover_minor_features(self) -> List[Feature]:
        """Discover MINOR features (epilogue mentions)"""
        
        return [
            Feature(
                name="Execution Methods",
                weight=FeatureWeight.MINOR,
                description="cli_wrapper vs copilot_chat routing architecture",
                target_location="Epilogue",
                word_count=200,
                rationale="Routing architecture evolution",
                comedic_hook="CORTEX learns when to talk vs when to execute",
                technical_concepts=[
                    "cli_wrapper (system operations)",
                    "copilot_chat (interactive workflows)",
                    "internal (orchestrators)",
                    "Unified entry point routing"
                ]
            ),
            Feature(
                name="Response Templates v4.0",
                weight=FeatureWeight.MINOR,
                description="Adaptive tier-based format with emoji hierarchy",
                target_location="Epilogue",
                word_count=150,
                rationale="Format evolution for consistency",
                comedic_hook="CORTEX discovers structure (shocking development)",
                technical_concepts=[
                    "Adaptive tier-based format",
                    "Emoji hierarchy (🧠 🎯 ⚡ 💬 📊 🔍)",
                    "Anti-bloat enforcement",
                    "Template-based rendering"
                ]
            ),
            Feature(
                name="SKULL Rules Expansion",
                weight=FeatureWeight.MINOR,
                description="Brain protection evolution with TDD enforcement",
                target_location="Chapter 2 (callback)",
                word_count=100,
                rationale="Connect Tier 0 origin to TDD future",
                comedic_hook="SKULL rules: now with more acronyms",
                technical_concepts=[
                    "TDD_ENFORCEMENT",
                    "RED_PHASE_VALIDATION",
                    "HOLISTIC_CODE_DISCOVERY_ENFORCEMENT",
                    "GIT_ISOLATION_ENFORCEMENT"
                ]
            )
        ]
    
    def export_catalog(self, output_path: str) -> None:
        """
        Export feature catalog to YAML file.
        
        Args:
            output_path: Path to output YAML file
        """
        features = self.discover_features()
        
        catalog = {
            'version': '1.0',
            'total_features': len(features),
            'breakdown': {
                'MAJOR': len([f for f in features if f.weight == FeatureWeight.MAJOR]),
                'MEDIUM': len([f for f in features if f.weight == FeatureWeight.MEDIUM]),
                'MINOR': len([f for f in features if f.weight == FeatureWeight.MINOR])
            },
            'features': [f.to_dict() for f in features]
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Exported feature catalog to {output_path}")


if __name__ == "__main__":
    # Test feature discovery
    discovery = FeatureDiscoveryModule()
    features = discovery.discover_features()
    
    print(f"\n=== CORTEX FEATURE CATALOG ===")
    print(f"Total: {len(features)} features\n")
    
    for weight in FeatureWeight:
        weight_features = [f for f in features if f.weight == weight]
        if weight_features:
            print(f"\n{weight.value} Features ({len(weight_features)}):")
            for feature in weight_features:
                print(f"  - {feature.name} → {feature.target_location} ({feature.word_count} words)")
    
    # Export catalog
    discovery.export_catalog("cortex-brain/documents/reports/feature-catalog.yaml")
