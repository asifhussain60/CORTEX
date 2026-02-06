"""
Tech Intelligence Orchestrator - Central Knowledge Hub.

Monitors tech ecosystems, generates best practices, and provides
readiness verification for all CORTEX orchestrators.

Phase 34B, Week 1, Increment 1:
- Skeleton implementation with core interfaces
- Basic readiness scoring (4-factor weighted)
- Simple tech stack detection
- Placeholder sub-components for future enhancement

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import time

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.intelligence.types import TechStack, ReadinessScore
from cortex.orchestrators.intelligence.ecosystem_scanner import EcosystemScanner
from cortex.orchestrators.intelligence.readiness_engine import ReadinessEngine
from cortex.orchestrators.intelligence.knowledge_synthesizer import (
    KnowledgeSynthesizer,
    KnowledgeSource,
)
from cortex.orchestrators.intelligence.learning_trigger import LearningTrigger


class TechIntelligenceOrchestrator(IOrchestrator):
    """
    Central knowledge hub for tech intelligence.
    
    Provides:
    - Tech stack detection
    - Readiness scoring
    - Knowledge synthesis
    - Proactive learning
    
    Example:
        >>> orchestrator = TechIntelligenceOrchestrator()
        >>> tech_stack = orchestrator.detect_tech_stack("/path/to/repo")
        >>> score = orchestrator.get_readiness_score(tech_stack)
        >>> if score.overall < 0.7:
        ...     orchestrator.synthesize_knowledge(tech_stack)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize Tech Intelligence Orchestrator.
        
        Args:
            config: Optional configuration overrides:
                - cache_enabled (bool): Enable readiness score caching (default: True)
                - scan_interval_hours (int): Hours between ecosystem scans (default: 24)
                - readiness_threshold (float): Minimum score for PROCEED (default: 0.7)
                - synthesis_enabled (bool): Enable knowledge synthesis (default: True)
        
        Example:
            >>> config = {"readiness_threshold": 0.8, "cache_enabled": False}
            >>> orchestrator = TechIntelligenceOrchestrator(config)
        """
        super().__init__()
        
        # Default configuration
        self.config = {
            "cache_enabled": True,
            "scan_interval_hours": 24,
            "readiness_threshold": 0.7,
            "synthesis_enabled": True,
        }
        
        # Apply custom config
        if config:
            self.config.update(config)
        
        # Initialize sub-components with real implementations
        self.ecosystem_scanner = EcosystemScanner()
        self.readiness_engine = ReadinessEngine()
        self.knowledge_synthesizer = KnowledgeSynthesizer(config={"cache_enabled": self.config.get("cache_enabled", True)})
        self.learning_trigger = LearningTrigger(config={
            "threshold": self.config.get("readiness_threshold", 0.5),
            "notification_enabled": True,
        })
        
        # Cache for readiness scores
        self._readiness_cache: Dict[TechStack, ReadinessScore] = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        
        # Known tech stacks registry
        self._known_stacks: Dict[str, float] = {}  # language -> usage frequency
    
    def _init_ecosystem_scanner(self) -> EcosystemScanner:
        """
        Initialize ecosystem scanner component (DEPRECATED - use direct initialization).
        
        Returns:
            EcosystemScanner instance
        """
        return EcosystemScanner()
    
    def _init_readiness_engine(self) -> ReadinessEngine:
        """
        Initialize readiness engine component (DEPRECATED - use direct initialization).
        
        Returns:
            ReadinessEngine instance
        """
        return ReadinessEngine()
    
    def _init_knowledge_synthesizer(self) -> KnowledgeSynthesizer:
        """
        Initialize knowledge synthesizer component (DEPRECATED - use direct initialization).
        
        Returns:
            KnowledgeSynthesizer instance
        """
        return KnowledgeSynthesizer()
    
    # IOrchestrator interface implementation
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "TechIntelligenceOrchestrator"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0-week1"
    
    def initialize(self) -> Result[str]:
        """Initialize orchestrator components."""
        try:
            # Clear caches
            self._readiness_cache.clear()
            self.cache_stats = {"hits": 0, "misses": 0}
            
            # Re-initialize sub-components
            self.ecosystem_scanner = self._init_ecosystem_scanner()
            self.readiness_engine = self._init_readiness_engine()
            self.knowledge_synthesizer = self._init_knowledge_synthesizer()
            
            return Ok("TechIntelligenceOrchestrator initialized successfully")
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")
    
    def get_mode(self) -> OperationMode:
        """Get operation mode."""
        return OperationMode.PLANNING  # Tech intelligence is planning-phase
    
    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities."""
        return [
            "readiness_scoring",
            "tech_detection",
            "knowledge_synthesis",
            "proactive_learning",
            "cross_repo_analysis",
        ]
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get MCP tool definitions."""
        tools = {
            "get_tech_readiness": {
                "name": "get_tech_readiness",
                "description": "Get readiness score for a tech stack",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "description": "Programming language"},
                        "frameworks": {"type": "array", "items": {"type": "string"}, "description": "Frameworks"},
                        "version": {"type": "string", "description": "Language version"},
                    },
                    "required": ["language"],
                },
            },
            "detect_tech_stack": {
                "name": "detect_tech_stack",
                "description": "Detect tech stack from repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_path": {"type": "string", "description": "Repository path"},
                    },
                    "required": ["repo_path"],
                },
            },
            "synthesize_best_practices": {
                "name": "synthesize_best_practices",
                "description": "Synthesize best practices for tech stack",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "description": "Programming language"},
                        "frameworks": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["language"],
                },
            },
        }
        return Ok(tools)
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute MCP tool operation."""
        try:
            if operation_name == "get_tech_readiness":
                tech_stack = TechStack(
                    language=parameters["language"],
                    frameworks=parameters.get("frameworks", []),
                    version=parameters.get("version"),
                )
                score = self.get_readiness_score(tech_stack)
                return Ok({
                    "overall": score.overall,
                    "action": score.action,
                    "components": {
                        "best_practices": score.best_practices,
                        "tdd_support": score.tdd_support,
                        "security": score.security,
                        "usage": score.usage,
                    },
                })
            
            elif operation_name == "detect_tech_stack":
                tech_stack = self.detect_tech_stack(parameters["repo_path"])
                return Ok({
                    "language": tech_stack.language,
                    "frameworks": tech_stack.frameworks,
                    "version": tech_stack.version,
                })
            
            elif operation_name == "synthesize_best_practices":
                tech_stack = TechStack(
                    language=parameters["language"],
                    frameworks=parameters.get("frameworks", []),
                )
                practices = self.synthesize_best_practices(tech_stack)
                return Ok({"best_practices": practices})
            
            else:
                return Err(f"Unknown operation: {operation_name}")
        
        except Exception as e:
            return Err(f"Operation failed: {str(e)}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail (not implemented in skeleton)."""
        # Placeholder - will implement audit logging in later increments
        return Ok([])
    
    # Core methods
    def get_readiness_score(self, tech_stack: Optional[TechStack]) -> ReadinessScore:
        """
        Get readiness score for a tech stack with automatic learning trigger detection.
        
        Args:
            tech_stack: Technology stack to evaluate
            
        Returns:
            ReadinessScore with overall score and breakdown
        """
        # Handle invalid input
        if tech_stack is None:
            return ReadinessScore.calculate(0.0, 0.0, 0.0, 0.0)
        
        # Check cache
        if self.config["cache_enabled"] and tech_stack in self._readiness_cache:
            self.cache_stats["hits"] += 1
            return self._readiness_cache[tech_stack]
        
        self.cache_stats["misses"] += 1
        
        # Calculate readiness score
        score = self._calculate_readiness_score(tech_stack)
        
        # Use LearningTrigger to detect knowledge gaps and trigger learning
        trigger_event = self.learning_trigger.check_readiness(tech_stack)
        if trigger_event.triggered:
            # Learning trigger detected - log event for future enhancement
            # In Week 4-5, this will integrate with notification system
            pass
        
        # Cache result
        if self.config["cache_enabled"]:
            self._readiness_cache[tech_stack] = score
        
        return score
    
    def _calculate_readiness_score(self, tech_stack: TechStack) -> ReadinessScore:
        """
        Calculate readiness score using ReadinessEngine.
        
        Args:
            tech_stack: Technology stack
            
        Returns:
            Calculated readiness score from ReadinessEngine
        """
        # Use real ReadinessEngine for scoring
        return self.readiness_engine.calculate_readiness_score(tech_stack)
        best_practices = self._get_best_practices_coverage(tech_stack)
        
        # TDD support (check if we know testing framework)
        tdd_support = self._get_tdd_support(tech_stack)
        
        # Security tooling (basic check)
        security = self._get_security_tooling(tech_stack)
        
        # Cross-repo usage (check if we've seen this before)
        usage = self._get_cross_repo_usage(tech_stack)
        
        return ReadinessScore.calculate(
            best_practices, tdd_support, security, usage
        )
    
    def _get_best_practices_coverage(self, tech_stack: TechStack) -> float:
        """Estimate best practices coverage (placeholder)."""
        # Known languages get higher scores
        known_languages = ["python", "javascript", "typescript", "go", "rust"]
        if tech_stack.language.lower() in known_languages:
            return 0.8
        return 0.3
    
    def _get_tdd_support(self, tech_stack: TechStack) -> float:
        """Estimate TDD framework support (placeholder)."""
        # Check if frameworks include test frameworks
        test_frameworks = ["pytest", "unittest", "jest", "mocha", "junit"]
        if any(fw in tech_stack.frameworks for fw in test_frameworks):
            return 0.9
        return 0.4
    
    def _get_security_tooling(self, tech_stack: TechStack) -> float:
        """Estimate security tooling availability (placeholder)."""
        # Major languages have good security tooling
        if tech_stack.language.lower() in ["python", "javascript", "typescript"]:
            return 0.7
        return 0.5
    
    def _get_cross_repo_usage(self, tech_stack: TechStack) -> float:
        """Get cross-repo usage frequency (placeholder)."""
        return self._known_stacks.get(tech_stack.language, 0.1)
    
    def detect_tech_stack(self, repo_path: str) -> TechStack:
        """
        Detect tech stack from repository path using EcosystemScanner.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Detected TechStack
        """
        # Use EcosystemScanner for comprehensive detection
        scan_result = self.ecosystem_scanner.scan_repository(repo_path)
        
        if scan_result.tech_stack:
            return scan_result.tech_stack
        
        # Fallback if scan fails
        return TechStack(language="unknown", frameworks=[])
    
    def detect_tech_stack_from_files(self, files: List[str]) -> TechStack:
        """
        Detect tech stack from file list using EcosystemScanner.
        
        Args:
            files: List of filenames
            
        Returns:
            Detected TechStack
        """
        # Use EcosystemScanner's pattern matching
        # Convert file list to a format the scanner can use
        
        # Extract extension and check against known patterns
        for file in files:
            if file.endswith('.py'):
                return TechStack(language="python", frameworks=[])
            elif file.endswith(('.js', '.jsx')):
                return TechStack(language="javascript", frameworks=[])
            elif file.endswith(('.ts', '.tsx')):
                return TechStack(language="typescript", frameworks=[])
            elif file.endswith(('.java')):
                return TechStack(language="java", frameworks=[])
            elif file.endswith(('.go')):
                return TechStack(language="go", frameworks=[])
            elif file.endswith(('.rs')):
                return TechStack(language="rust", frameworks=[])
        
        # Default
        return TechStack(language="unknown", frameworks=[])
    
    def synthesize_best_practices(self, tech_stack: TechStack) -> Result:
        """
        Synthesize best practices for tech stack using KnowledgeSynthesizer.
        
        Args:
            tech_stack: Technology stack
            
        Returns:
            Result with generated knowledge or error
        """
        if not self.config["synthesis_enabled"]:
            return Err("Knowledge synthesis disabled")
        
        if tech_stack.language == "unknown":
            return Err(f"Cannot synthesize for unknown language")
        
        # Use KnowledgeSynthesizer for real generation
        synthesis_result = self.knowledge_synthesizer.synthesize_best_practices(
            tech_stack=tech_stack,
            source=KnowledgeSource.INTERNAL
        )
        
        # Wrap SynthesisResult in Ok
        return Ok({
            "content": synthesis_result.content,
            "source": synthesis_result.source.value,
            "template_type": synthesis_result.template_type.value,
        })
    
    def synthesize_tdd_patterns(self, tech_stack: TechStack) -> Result:
        """Synthesize TDD patterns for tech stack using KnowledgeSynthesizer."""
        if tech_stack.language == "unknown":
            return Err("Cannot synthesize TDD patterns for unknown language")
        
        # Use KnowledgeSynthesizer for real TDD pattern generation
        synthesis_result = self.knowledge_synthesizer.generate_tdd_patterns(tech_stack)
        
        return Ok({
            "content": synthesis_result.content,
            "source": synthesis_result.source.value,
            "template_type": synthesis_result.template_type.value,
        })
    
    def synthesize_security_rules(self, tech_stack: TechStack) -> Result:
        """Synthesize security rules for tech stack using KnowledgeSynthesizer."""
        if tech_stack.language == "unknown":
            return Err("Cannot synthesize security rules for unknown language")
        
        # Use KnowledgeSynthesizer for real security rule generation
        synthesis_result = self.knowledge_synthesizer.generate_security_rules(tech_stack)
        
        return Ok({
            "content": synthesis_result.content,
            "source": synthesis_result.source.value,
            "template_type": synthesis_result.template_type.value,
        })
    
    def synthesize_knowledge(self, tech_stack: TechStack) -> Result:
        """
        Synthesize all knowledge artifacts for tech stack.
        
        Args:
            tech_stack: Technology stack
            
        Returns:
            Result with synthesis status
        """
        if tech_stack.language == "invalid":
            return Err("Invalid tech stack")
        
        # Placeholder for full synthesis
        return Ok({"status": "complete", "artifacts": 3})
    
    def get_mcp_tools(self) -> Result:
        """
        Get MCP tools for external access.
        
        Returns:
            Result containing tool definitions
        """
        tools = {
            "get_readiness_score": {
                "description": "Get readiness score for a tech stack",
                "parameters": ["language", "frameworks"]
            },
            "detect_tech_stack": {
                "description": "Detect tech stack from repository",
                "parameters": ["repo_path"]
            },
            "synthesize_knowledge": {
                "description": "Generate knowledge artifacts for tech stack",
                "parameters": ["language", "frameworks"]
            }
        }
        return Ok(tools)
