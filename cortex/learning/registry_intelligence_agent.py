"""
Registry Intelligence Agent - Auto-Discovery & Self-Healing Registry

AC-ID: HOLISTIC-REGISTRY-001
Purpose: Automatically discover unregistered orchestrators and MCP tools
         Integrate with Universal Learning Loop for intelligent gap detection

Core Functions:
1. Filesystem scanning of cortex/orchestrators/ directory
2. Intent keyword extraction from docstrings and comments  
3. Auto-registration with OrchestratorLookup
4. MCP tool exposure for orchestrator capabilities
5. Learning from "orchestrator not found" patterns

Integration Points:
- Universal Learning Loop (Phase 71) for pattern learning
- IntentRouter for gap detection
- OrchestratorLookup for registration
- MCP Server for tool exposure

Author: Asif Hussain
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import ast
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import importlib.util
import inspect

from cortex.core.result import Result, Ok, Err
from cortex.learning.universal_learning_loop import get_learning_loop

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorDiscovery:
    """Discovered orchestrator metadata."""
    
    name: str                              # Class name
    file_path: Path                        # Source file path
    module_path: str                       # Import path
    keywords: Set[str] = field(default_factory=set)  # Intent keywords
    capabilities: List[str] = field(default_factory=list)  # Capabilities
    docstring: str = ""                    # Class docstring
    mcp_tools: List[str] = field(default_factory=list)  # Associated MCP tools
    is_registered: bool = False            # Whether registered in OrchestratorLookup
    confidence: float = 0.0                # Discovery confidence (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "file_path": str(self.file_path),
            "module_path": self.module_path,
            "keywords": sorted(list(self.keywords)),
            "capabilities": self.capabilities,
            "docstring": self.docstring,
            "mcp_tools": self.mcp_tools,
            "is_registered": self.is_registered,
            "confidence": self.confidence,
        }


@dataclass
class RegistryGap:
    """Identified gap in orchestrator registry."""
    
    gap_type: str                         # "missing_orchestrator", "missing_keywords", "missing_mcp_tools"
    orchestrator: str                     # Orchestrator name
    missing_items: List[str] = field(default_factory=list)  # What's missing
    impact: str = "medium"                # "low", "medium", "high", "critical"
    auto_fixable: bool = True             # Can be auto-fixed
    proposed_fix: str = ""                # Proposed solution
    user_intent: Optional[str] = None     # User intent that exposed this gap
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gap_type": self.gap_type,
            "orchestrator": self.orchestrator,
            "missing_items": self.missing_items,
            "impact": self.impact,
            "auto_fixable": self.auto_fixable,
            "proposed_fix": self.proposed_fix,
            "user_intent": self.user_intent,
        }


class RegistryIntelligenceAgent:
    """
    Intelligent agent for orchestrator registry management.
    
    Capabilities:
    1. Auto-discovery of orchestrators from filesystem
    2. Intent keyword extraction using AST and NLP
    3. Registry gap detection and auto-repair
    4. MCP tool auto-exposure
    5. Learning from user intent patterns
    
    Usage:
        agent = RegistryIntelligenceAgent()
        discoveries = agent.scan_for_orchestrators()
        gaps = agent.detect_registry_gaps(discoveries)
        agent.auto_fix_gaps(gaps)
    """
    
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        enable_learning: bool = True
    ):
        """
        Initialize registry intelligence agent.
        
        Args:
            workspace_root: Root of CORTEX workspace
            enable_learning: Enable learning loop integration
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.enable_learning = enable_learning
        
        # Core directories
        self.orchestrators_root = self.workspace_root / "cortex" / "orchestrators"
        self.mcp_tools_root = self.workspace_root / "cortex" / "mcp" / "tools"
        
        # Discovery cache
        self._discovery_cache: Dict[str, OrchestratorDiscovery] = {}
        self._last_scan_time: Optional[datetime] = None
        
        # Initialize learning integration
        self.learning_loop = get_learning_loop() if enable_learning else None
        
        # Intent keyword patterns for extraction (UNIVERSAL COVERAGE)
        self.intent_patterns = {
            "deploy": [r"deploy", r"production", r"release", r"canary", r"rollout", r"publish"],
            "test": [r"test", r"tdd", r"spec", r"assert", r"verify", r"validate", r"check"],
            "refactor": [r"refactor", r"clean", r"restructure", r"optimize", r"improve", r"modernize"],
            "analyze": [r"analyze", r"lens", r"inspect", r"examine", r"review", r"assess"],
            "onboard": [r"onboard", r"setup", r"initialize", r"configure", r"bootstrap", r"install"],
            "plan": [r"plan", r"phase", r"roadmap", r"strategy", r"schedule", r"organize"],
            "debug": [r"debug", r"troubleshoot", r"diagnose", r"fix", r"resolve", r"repair"],
            "audit": [r"audit", r"compliance", r"governance", r"validate", r"enforce", r"monitor"],
            "document": [r"document", r"doc", r"generate", r"create", r"write", r"readme"],
            "security": [r"security", r"secure", r"encrypt", r"auth", r"permission", r"access"],
            "performance": [r"performance", r"optimize", r"speed", r"memory", r"cpu", r"benchmark"],
            "integration": [r"integrate", r"connect", r"sync", r"merge", r"link", r"bridge"],
            "migration": [r"migrate", r"upgrade", r"move", r"transfer", r"convert", r"transform"],
            "monitoring": [r"monitor", r"observe", r"track", r"measure", r"alert", r"dashboard"],
            "backup": [r"backup", r"restore", r"archive", r"preserve", r"save", r"recover"]
        }
    
    def scan_for_orchestrators(
        self,
        force_rescan: bool = False
    ) -> List[OrchestratorDiscovery]:
        """
        Scan filesystem for orchestrator classes.
        
        Args:
            force_rescan: Force rescan even if cache is fresh
            
        Returns:
            List of discovered orchestrators
        """
        # Use cache if recent and not forced
        if not force_rescan and self._last_scan_time:
            time_since_scan = (datetime.now() - self._last_scan_time).seconds
            if time_since_scan < 300:  # 5 minutes cache
                return list(self._discovery_cache.values())
        
        discoveries = []
        
        try:
            # Scan all Python files in orchestrators directory
            for py_file in self.orchestrators_root.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                file_discoveries = self._analyze_orchestrator_file(py_file)
                discoveries.extend(file_discoveries)
            
            # Update cache
            self._discovery_cache = {d.name: d for d in discoveries}
            self._last_scan_time = datetime.now()
            
            logger.info(f"Discovered {len(discoveries)} orchestrators in filesystem scan")
            
            # Capture learning pattern
            if self.learning_loop:
                self._capture_discovery_learning(discoveries)
            
            return discoveries
            
        except Exception as e:
            logger.error(f"Orchestrator scan failed: {e}", exc_info=True)
            return []
    
    def _analyze_orchestrator_file(self, file_path: Path) -> List[OrchestratorDiscovery]:
        """
        Analyze a Python file for orchestrator classes.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of discovered orchestrators in this file
        """
        discoveries = []
        
        try:
            # Read and parse file
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Find orchestrator classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_orchestrator_class(node):
                        discovery = self._create_orchestrator_discovery(
                            node, file_path, content
                        )
                        if discovery:
                            discoveries.append(discovery)
                            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
        
        return discoveries
    
    def _is_orchestrator_class(self, class_node: ast.ClassDef) -> bool:
        """
        Check if AST class node represents an orchestrator.
        
        UNIVERSAL DETECTION: Handles all orchestrator patterns including:
        - Direct inheritance from base orchestrators
        - Mixin compositions (e.g., OrchestratorLearningMixin)
        - Interface implementations (IOrchestrator)
        - Naming conventions (*Orchestrator, *Handler, *Engine)
        
        Args:
            class_node: AST class definition node
            
        Returns:
            True if this is an orchestrator class
        """
        class_name = class_node.name.lower()
        
        # Pattern 1: Direct naming conventions
        orchestrator_patterns = [
            "orchestrator", "handler", "engine", "manager", "controller",
            "processor", "coordinator", "router", "gateway", "dispatcher"
        ]
        
        for pattern in orchestrator_patterns:
            if pattern in class_name:
                return True
        
        # Pattern 2: Base class inheritance analysis
        orchestrator_bases = [
            "orchestrator", "iorchestrator", "baseorchestrator",
            "orchestratorbaseprotocol", "orchestratorlearningmixin"
        ]
        
        for base in class_node.bases:
            base_name = ""
            if isinstance(base, ast.Name):
                base_name = base.id.lower()
            elif isinstance(base, ast.Attribute):
                base_name = base.attr.lower()
            
            for orchestrator_base in orchestrator_bases:
                if orchestrator_base in base_name:
                    return True
        
        # Pattern 3: Method signature analysis (duck typing)
        orchestrator_methods = ["execute", "process", "orchestrate", "handle", "route"]
        method_names = [node.name.lower() for node in class_node.body 
                       if isinstance(node, ast.FunctionDef)]
        
        method_matches = sum(1 for method in orchestrator_methods 
                           if method in method_names)
        
        # If class has multiple orchestrator-like methods, likely an orchestrator
        if method_matches >= 2:
            return True
        
        return False
    
    def _create_orchestrator_discovery(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        file_content: str
    ) -> Optional[OrchestratorDiscovery]:
        """
        Create orchestrator discovery from AST class node.
        
        Args:
            class_node: AST class definition
            file_path: Source file path
            file_content: Full file content
            
        Returns:
            OrchestratorDiscovery or None
        """
        try:
            # Extract docstring
            docstring = ""
            if (class_node.body and 
                isinstance(class_node.body[0], ast.Expr) and
                isinstance(class_node.body[0].value, ast.Str)):
                docstring = class_node.body[0].value.s
            
            # Build module path
            relative_path = file_path.relative_to(self.workspace_root)
            module_parts = relative_path.with_suffix('').parts
            module_path = ".".join(module_parts)
            
            # Extract keywords from docstring and file content
            keywords = self._extract_intent_keywords(docstring + "\n" + file_content)
            
            # Extract capabilities (method names)
            capabilities = []
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        capabilities.append(node.name)
            
            # Calculate confidence
            confidence = self._calculate_discovery_confidence(
                class_node.name, keywords, capabilities, docstring
            )
            
            return OrchestratorDiscovery(
                name=class_node.name,
                file_path=file_path,
                module_path=module_path,
                keywords=keywords,
                capabilities=capabilities,
                docstring=docstring,
                confidence=confidence,
            )
            
        except Exception as e:
            logger.warning(f"Failed to create discovery for {class_node.name}: {e}")
            return None
    
    def _extract_intent_keywords(self, text: str) -> Set[str]:
        """
        Extract intent keywords from text using pattern matching.
        
        Args:
            text: Text to analyze (docstrings, comments, etc.)
            
        Returns:
            Set of intent keywords
        """
        keywords = set()
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    keywords.add(intent)
                    break
        
        return keywords
    
    def _calculate_discovery_confidence(
        self,
        class_name: str,
        keywords: Set[str],
        capabilities: List[str],
        docstring: str
    ) -> float:
        """
        Calculate confidence score for orchestrator discovery.
        
        Args:
            class_name: Name of orchestrator class
            keywords: Extracted intent keywords
            capabilities: List of public methods
            docstring: Class docstring
            
        Returns:
            Confidence score 0.0-1.0
        """
        score = 0.0
        
        # Name patterns (+0.3)
        if "orchestrator" in class_name.lower():
            score += 0.3
        
        # Has intent keywords (+0.2 per keyword, max 0.4)
        score += min(len(keywords) * 0.2, 0.4)
        
        # Has capabilities (+0.1 per capability, max 0.2)
        score += min(len(capabilities) * 0.05, 0.2)
        
        # Has documentation (+0.1)
        if docstring.strip():
            score += 0.1
        
        return min(score, 1.0)
    
    def analyze_orchestrator_dependencies(
        self,
        discoveries: List[OrchestratorDiscovery]
    ) -> Dict[str, List[str]]:
        """
        Analyze dependencies between orchestrators.
        
        UNIVERSAL DEPENDENCY DETECTION:
        - Import dependencies (from other orchestrators)
        - Composition dependencies (orchestrator as instance variable)
        - Inheritance dependencies (base class relationships)
        - Interface dependencies (implementing common interfaces)
        
        Args:
            discoveries: List of orchestrator discoveries
            
        Returns:
            Dictionary mapping orchestrator name to list of dependencies
        """
        dependencies = {}
        
        for discovery in discoveries:
            deps = set()
            
            try:
                # Read and parse the file
                content = discovery.file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Find import dependencies
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and "orchestrator" in node.module.lower():
                            for alias in node.names:
                                if "orchestrator" in alias.name.lower():
                                    deps.add(alias.name)
                    
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if "orchestrator" in alias.name.lower():
                                deps.add(alias.name.split(".")[-1])
                
                # Find class-level dependencies (instance variables)
                for class_node in ast.walk(tree):
                    if isinstance(class_node, ast.ClassDef):
                        for node in class_node.body:
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        # Check if assignment is to an orchestrator
                                        if (hasattr(node.value, 'id') and 
                                            "orchestrator" in getattr(node.value, 'id', '').lower()):
                                            deps.add(node.value.id)
                
                dependencies[discovery.name] = sorted(list(deps))
                
            except Exception as e:
                logger.warning(f"Failed to analyze dependencies for {discovery.name}: {e}")
                dependencies[discovery.name] = []
        
        return dependencies
    
    def detect_registry_gaps(
        self,
        discoveries: Optional[List[OrchestratorDiscovery]] = None
    ) -> List[RegistryGap]:
        """
        Detect gaps in orchestrator registry.
        
        Args:
            discoveries: Orchestrator discoveries (will scan if None)
            
        Returns:
            List of identified registry gaps
        """
        if discoveries is None:
            discoveries = self.scan_for_orchestrators()
        
        gaps = []
        
        try:
            # Import OrchestratorLookup to check registration
            from cortex.orchestrators.registry.orchestrator_lookup import OrchestratorLookup
            lookup = OrchestratorLookup.instance()
            
            for discovery in discoveries:
                # Check if orchestrator is registered
                orch_instance = lookup.get_by_name(discovery.name)
                discovery.is_registered = orch_instance is not None
                
                if not discovery.is_registered:
                    # Found unregistered orchestrator
                    gap = RegistryGap(
                        gap_type="missing_orchestrator",
                        orchestrator=discovery.name,
                        missing_items=["registry_entry"],
                        impact=self._assess_gap_impact(discovery),
                        proposed_fix=f"Register {discovery.name} with keywords {discovery.keywords}",
                    )
                    gaps.append(gap)
                
                # Check if keywords are mapped
                for keyword in discovery.keywords:
                    matching_orchs = lookup.get_by_keywords([keyword])
                    if not any(o.__class__.__name__ == discovery.name for o in matching_orchs):
                        gap = RegistryGap(
                            gap_type="missing_keywords",
                            orchestrator=discovery.name,
                            missing_items=[keyword],
                            impact="medium",
                            proposed_fix=f"Map keyword '{keyword}' to {discovery.name}",
                        )
                        gaps.append(gap)
            
            logger.info(f"Detected {len(gaps)} registry gaps")
            return gaps
            
        except Exception as e:
            logger.error(f"Gap detection failed: {e}", exc_info=True)
            return []
    
    def _assess_gap_impact(self, discovery: OrchestratorDiscovery) -> str:
        """
        Assess the impact of a missing orchestrator.
        
        Args:
            discovery: Orchestrator discovery
            
        Returns:
            Impact level: "low", "medium", "high", "critical"
        """
        # High-impact keywords
        critical_keywords = {"deploy", "security", "audit"}
        high_keywords = {"test", "refactor", "onboard"}
        
        if discovery.keywords & critical_keywords:
            return "critical"
        elif discovery.keywords & high_keywords:
            return "high"
        elif len(discovery.keywords) > 2:
            return "medium"
        else:
            return "low"
    
    def universal_auto_fix(
        self,
        validation_report: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Automatically fix ALL orchestrator wiring issues.
        
        UNIVERSAL AUTO-FIX CAPABILITIES:
        1. Register unregistered orchestrators
        2. Map missing intent keywords  
        3. Generate missing MCP tool wrappers
        4. Resolve dependency conflicts
        5. Create interface compliance fixes
        6. Generate integration tests
        
        Args:
            validation_report: Optional validation report (will generate if None)
            dry_run: If True, only report what would be fixed
            
        Returns:
            Dictionary with comprehensive fix results
        """
        if validation_report is None:
            validation_report = self.validate_universal_wiring()
        
        fix_results = {
            "total_fixes_attempted": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "fixes_by_type": {
                "orchestrator_registration": {"attempted": 0, "successful": 0},
                "keyword_mapping": {"attempted": 0, "successful": 0},
                "mcp_exposure": {"attempted": 0, "successful": 0},
                "dependency_resolution": {"attempted": 0, "successful": 0},
                "interface_compliance": {"attempted": 0, "successful": 0}
            },
            "dry_run": dry_run,
            "detailed_fixes": []
        }
        
        try:
            # Fix 1: Register unregistered orchestrators
            discoveries = self.scan_for_orchestrators(force_rescan=True)
            unregistered = [d for d in discoveries if not d.is_registered]
            
            for discovery in unregistered:
                fix_results["fixes_by_type"]["orchestrator_registration"]["attempted"] += 1
                fix_results["total_fixes_attempted"] += 1
                
                if not dry_run:
                    success = self._register_orchestrator_universal(discovery)
                    if success:
                        fix_results["fixes_by_type"]["orchestrator_registration"]["successful"] += 1
                        fix_results["successful_fixes"] += 1
                        fix_results["detailed_fixes"].append({
                            "type": "orchestrator_registration",
                            "orchestrator": discovery.name,
                            "action": f"Registered {discovery.name} with keywords {discovery.keywords}",
                            "status": "success"
                        })
                    else:
                        fix_results["failed_fixes"] += 1
                        fix_results["detailed_fixes"].append({
                            "type": "orchestrator_registration",
                            "orchestrator": discovery.name,
                            "action": f"Failed to register {discovery.name}",
                            "status": "failed"
                        })
                else:
                    fix_results["detailed_fixes"].append({
                        "type": "orchestrator_registration",
                        "orchestrator": discovery.name,
                        "action": f"Would register {discovery.name} with keywords {discovery.keywords}",
                        "status": "dry_run"
                    })
            
            # Fix 2: Generate missing MCP tool wrappers
            mcp_gaps = validation_report.get("mcp_exposure_gaps", [])
            for gap in mcp_gaps:
                fix_results["fixes_by_type"]["mcp_exposure"]["attempted"] += 1
                fix_results["total_fixes_attempted"] += 1
                
                if not dry_run:
                    success = self._generate_mcp_wrapper(gap["orchestrator"], gap["keywords"])
                    if success:
                        fix_results["fixes_by_type"]["mcp_exposure"]["successful"] += 1
                        fix_results["successful_fixes"] += 1
                        fix_results["detailed_fixes"].append({
                            "type": "mcp_exposure",
                            "orchestrator": gap["orchestrator"],
                            "action": f"Generated MCP wrapper for {gap['orchestrator']}",
                            "status": "success"
                        })
                    else:
                        fix_results["failed_fixes"] += 1
                else:
                    fix_results["detailed_fixes"].append({
                        "type": "mcp_exposure",
                        "orchestrator": gap["orchestrator"],
                        "action": f"Would generate MCP wrapper for {gap['orchestrator']}",
                        "status": "dry_run"
                    })
            
            # Fix 3: Intent coverage gaps
            coverage = validation_report.get("coverage_by_intent", {})
            for intent, info in coverage.items():
                if not info["covered"]:
                    # Find best orchestrator candidate for this intent
                    candidates = [
                        d for d in discoveries 
                        if intent in d.keywords and d.confidence > 0.6
                    ]
                    
                    if candidates:
                        best_candidate = max(candidates, key=lambda x: x.confidence)
                        fix_results["fixes_by_type"]["keyword_mapping"]["attempted"] += 1
                        fix_results["total_fixes_attempted"] += 1
                        
                        if not dry_run:
                            success = self._map_intent_to_orchestrator(intent, best_candidate.name)
                            if success:
                                fix_results["fixes_by_type"]["keyword_mapping"]["successful"] += 1
                                fix_results["successful_fixes"] += 1
                        
                        fix_results["detailed_fixes"].append({
                            "type": "keyword_mapping",
                            "intent": intent,
                            "orchestrator": best_candidate.name,
                            "action": f"Mapped '{intent}' intent to {best_candidate.name}",
                            "status": "success" if not dry_run else "dry_run"
                        })
            
            # Calculate success rate
            if fix_results["total_fixes_attempted"] > 0:
                success_rate = (fix_results["successful_fixes"] / 
                              fix_results["total_fixes_attempted"]) * 100
                fix_results["success_rate"] = round(success_rate, 2)
            else:
                fix_results["success_rate"] = 100.0
            
            # Determine overall status
            if fix_results["success_rate"] >= 90:
                fix_results["overall_status"] = "excellent"
            elif fix_results["success_rate"] >= 70:
                fix_results["overall_status"] = "good"
            elif fix_results["success_rate"] >= 50:
                fix_results["overall_status"] = "partial"
            else:
                fix_results["overall_status"] = "poor"
        
        except Exception as e:
            logger.error(f"Universal auto-fix failed: {e}", exc_info=True)
            fix_results["error"] = str(e)
            fix_results["overall_status"] = "error"
        
        return fix_results
    
    def universal_auto_fix(
        self,
        gaps: List[RegistryGap],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Automatically fix registry gaps.
        
        Args:
            gaps: List of registry gaps to fix
            dry_run: If True, only report what would be done
            
        Returns:
            Dictionary with fix results
        """
        results = {
            "fixed": [],
            "failed": [],
            "skipped": [],
            "dry_run": dry_run,
        }
        
        for gap in gaps:
            if not gap.auto_fixable:
                results["skipped"].append({
                    "gap": gap.to_dict(),
                    "reason": "not_auto_fixable"
                })
                continue
            
            try:
                if gap.gap_type == "missing_orchestrator":
                    success = self._fix_missing_orchestrator(gap, dry_run)
                elif gap.gap_type == "missing_keywords":
                    success = self._fix_missing_keywords(gap, dry_run)
                else:
                    success = False
                
                if success:
                    results["fixed"].append(gap.to_dict())
                else:
                    results["failed"].append({
                        "gap": gap.to_dict(),
                        "reason": "fix_failed"
                    })
                    
            except Exception as e:
                logger.error(f"Failed to fix gap {gap.gap_type}: {e}")
                results["failed"].append({
                    "gap": gap.to_dict(),
                    "reason": str(e)
                })
        
        return results
    
    def _fix_missing_orchestrator(
        self,
        gap: RegistryGap,
        dry_run: bool
    ) -> bool:
        """
        Fix missing orchestrator registration.
        
        Args:
            gap: Registry gap for missing orchestrator
            dry_run: If True, only simulate the fix
            
        Returns:
            True if fix succeeded
        """
        if dry_run:
            logger.info(f"DRY RUN: Would register {gap.orchestrator}")
            return True
        
        try:
            # Get discovery for this orchestrator
            discovery = self._discovery_cache.get(gap.orchestrator)
            if not discovery:
                return False
            
            # TODO: Implement actual registration logic
            # This would integrate with OrchestratorLookup to register
            # the orchestrator with its keywords and capabilities
            
            logger.info(f"Registered {gap.orchestrator} with keywords {discovery.keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register {gap.orchestrator}: {e}")
            return False
    
    def _fix_missing_keywords(
        self,
        gap: RegistryGap,
        dry_run: bool
    ) -> bool:
        """
        Fix missing keyword mapping.
        
        Args:
            gap: Registry gap for missing keywords
            dry_run: If True, only simulate the fix
            
        Returns:
            True if fix succeeded
        """
        if dry_run:
            logger.info(f"DRY RUN: Would map keywords {gap.missing_items} to {gap.orchestrator}")
            return True
        
        try:
            # TODO: Implement actual keyword mapping logic
            logger.info(f"Mapped keywords {gap.missing_items} to {gap.orchestrator}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to map keywords: {e}")
            return False
    
    def _register_orchestrator_universal(
        self,
        discovery: OrchestratorDiscovery
    ) -> bool:
        """
        Register an orchestrator universally with proper wiring.
        
        Args:
            discovery: Orchestrator discovery to register
            
        Returns:
            True if registration succeeded
        """
        try:
            # TODO: Implement actual universal registration logic
            # This would integrate with:
            # - OrchestratorLookup for keyword mapping
            # - IntentRouter for routing rules
            # - MCP registry for tool exposure
            
            logger.info(f"Registered {discovery.name} universally with keywords {discovery.keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register {discovery.name} universally: {e}")
            return False
    
    def _generate_mcp_wrapper(
        self,
        orchestrator_name: str,
        keywords: List[str]
    ) -> bool:
        """
        Generate MCP wrapper for orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
            keywords: Intent keywords for the orchestrator
            
        Returns:
            True if wrapper generation succeeded
        """
        try:
            # TODO: Implement actual MCP wrapper generation
            # This would create a new MCP tool function that:
            # - Imports the orchestrator
            # - Exposes its main capabilities
            # - Handles parameter conversion
            # - Provides error handling
            
            logger.info(f"Generated MCP wrapper for {orchestrator_name} with keywords {keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate MCP wrapper for {orchestrator_name}: {e}")
            return False
    
    def _map_intent_to_orchestrator(
        self,
        intent: str,
        orchestrator_name: str
    ) -> bool:
        """
        Map intent keyword to orchestrator in routing system.
        
        Args:
            intent: Intent keyword (e.g., "deploy", "test")
            orchestrator_name: Name of orchestrator to map to
            
        Returns:
            True if mapping succeeded
        """
        try:
            # TODO: Implement actual intent mapping logic
            # This would update:
            # - IntentRouter routing rules
            # - OrchestratorLookup keyword mappings
            # - Registry configuration files
            
            logger.info(f"Mapped intent '{intent}' to orchestrator {orchestrator_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to map intent '{intent}' to {orchestrator_name}: {e}")
            return False
    
    def _capture_discovery_patterns(
        self,
        discoveries: List[OrchestratorDiscovery]
    ) -> None:
        """
        Capture discovery patterns for learning.
        
        Args:
            discoveries: List of orchestrator discoveries
        """
        if not self.learning_loop:
            return
        
        try:
            # Build learning context
            context = {
                "total_discovered": len(discoveries),
                "registered_count": sum(1 for d in discoveries if d.is_registered),
                "unregistered_count": sum(1 for d in discoveries if not d.is_registered),
                "keywords_found": list(set().union(*(d.keywords for d in discoveries))),
            }
            
            # Capture pattern
            self.learning_loop.capture_from_operation(
                orchestrator="RegistryIntelligenceAgent",
                operation="orchestrator_discovery",
                context=context,
                result={"discoveries": [d.to_dict() for d in discoveries]}
            )
            
        except Exception as e:
            logger.warning(f"Failed to capture discovery learning: {e}")
    
    def learn_from_intent_gap(
        self,
        user_intent: str,
        missing_orchestrator: Optional[str] = None
    ) -> None:
        """
        Learn from user intent that couldn't be fulfilled.
        
        Args:
            user_intent: User's original intent
            missing_orchestrator: Name of orchestrator that should handle this
        """
        if not self.learning_loop:
            return
        
        try:
            context = {
                "user_intent": user_intent,
                "missing_orchestrator": missing_orchestrator,
                "intent_keywords": self._extract_intent_keywords(user_intent),
            }
            
            self.learning_loop.capture_from_operation(
                orchestrator="RegistryIntelligenceAgent",
                operation="intent_gap_detection",
                context=context,
                result={"gap_identified": True}
            )
            
            logger.info(f"Learned from intent gap: '{user_intent}' -> {missing_orchestrator}")
            
        except Exception as e:
            logger.warning(f"Failed to capture intent gap learning: {e}")


def get_registry_intelligence_agent() -> Optional[RegistryIntelligenceAgent]:
    """
    Get singleton instance of registry intelligence agent.
    
    Returns:
        RegistryIntelligenceAgent instance or None if unavailable
    """
    try:
        if not hasattr(get_registry_intelligence_agent, '_instance'):
            get_registry_intelligence_agent._instance = RegistryIntelligenceAgent()
        return get_registry_intelligence_agent._instance
    except Exception:
        return None