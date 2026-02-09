"""
Base Intelligence Engine.

Abstract base class enforcing contract for all intelligence engines.

Authority: Phase 56 - LENS/Intelligence Hybrid Architecture
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """
    Context for intelligence analysis.
    
    Attributes:
        file_path: Primary file being analyzed
        workspace_root: Root of workspace
        additional_files: Related files for cross-file analysis
        config: Engine-specific configuration
        cache_key: Optional cache key for results
    """
    file_path: Path
    workspace_root: Path
    additional_files: List[Path] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    cache_key: Optional[str] = None


@dataclass
class AnalysisResult:
    """
    Result from intelligence analysis.
    
    Attributes:
        engine_name: Name of engine that produced result
        data: Analysis data (engine-specific)
        metadata: Timing, errors, warnings
        cache_hit: Whether result came from cache
    """
    engine_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_hit: bool = False


class BaseIntelligenceEngine(ABC):
    """
    Abstract base class for intelligence engines.
    
    All intelligence engines must:
    1. Inherit from BaseIntelligenceEngine
    2. Implement analyze() method
    3. Implement validate_context() method
    4. Support both sync and async modes
    5. Never import from cortex.lens (prevents circular deps)
    6. Return AnalysisResult with standardized format
    """
    
    def __init__(self, engine_name: str):
        """
        Initialize intelligence engine.
        
        Args:
            engine_name: Human-readable name for this engine
        """
        self.engine_name = engine_name
        self.logger = logging.getLogger(f"{__name__}.{engine_name}")
    
    @abstractmethod
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """
        Analyze code and return intelligence.
        
        Args:
            context: Analysis context with file path, workspace, config
            
        Returns:
            AnalysisResult with standardized data format
            
        Raises:
            ValueError: If context validation fails
        """
        pass
    
    @abstractmethod
    def validate_context(self, context: AnalysisContext) -> bool:
        """
        Validate that context is suitable for analysis.
        
        Args:
            context: Analysis context to validate
            
        Returns:
            True if context is valid
            
        Raises:
            ValueError: If context is invalid
        """
        pass
    
    def analyze_async(self, context: AnalysisContext) -> AnalysisResult:
        """
        Async version of analyze() (optional).
        
        Default implementation delegates to sync analyze().
        Override for true async implementations.
        
        Args:
            context: Analysis context
            
        Returns:
            AnalysisResult
        """
        return self.analyze(context)
    
    def _create_result(self, data: Dict[str, Any], cache_hit: bool = False) -> AnalysisResult:
        """
        Helper to create standardized result.
        
        Args:
            data: Engine-specific analysis data
            cache_hit: Whether this came from cache
            
        Returns:
            AnalysisResult with metadata
        """
        return AnalysisResult(
            engine_name=self.engine_name,
            data=data,
            metadata={
                "engine": self.engine_name,
                "timestamp": __import__("time").time(),
            },
            cache_hit=cache_hit,
        )
    
    def _error_result(self, error: Exception) -> AnalysisResult:
        """
        Helper to create error result.
        
        Args:
            error: Exception that occurred
            
        Returns:
            AnalysisResult with error metadata
        """
        self.logger.error(f"Analysis error: {error}", exc_info=True)
        return AnalysisResult(
            engine_name=self.engine_name,
            data={"error": str(error)},
            metadata={
                "engine": self.engine_name,
                "error": str(error),
                "timestamp": __import__("time").time(),
            },
        )
