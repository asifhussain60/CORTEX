"""
Master Orchestrator Stage 1 Stub (Docker-First Architecture)

Stage 1 (Comprehension) is now handled by InteractionOrchestrator.
This stub provides backward compatibility.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


@dataclass
class Stage1ComprehensionContext:
    """Context for Stage 1 comprehension."""
    user_input: str
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stage1Output:
    """Output from Stage 1 comprehension."""
    understood_intent: str
    confidence: float = 0.85
    entities: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


class MasterOrchestrationStage1:
    """
    Stub for Stage 1 comprehension.
    
    In production, use InteractionOrchestrator instead.
    """
    
    def __init__(self):
        """Initialize stage 1."""
        logger.debug("MasterOrchestrationStage1 stub initialized")
    
    def execute(self, context: Stage1ComprehensionContext) -> Result[Stage1Output, str]:
        """Execute stage 1 comprehension (stub)."""
        logger.info(f"Stage 1 stub processing: {context.user_input[:50]}...")
        
        return Ok(Stage1Output(
            understood_intent=context.user_input,
            confidence=0.85,
            entities=[],
            context={"source": "stage1_stub"}
        ))
    
    def comprehend(self, user_input: str) -> Result[Stage1Output, str]:
        """Comprehend user input."""
        context = Stage1ComprehensionContext(user_input=user_input)
        return self.execute(context)
