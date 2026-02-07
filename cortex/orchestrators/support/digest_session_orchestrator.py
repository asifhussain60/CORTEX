"""
AC-PHASE41-001: DigestSessionOrchestrator detects chat files (score ≥5)

DigestSessionOrchestrator - Main orchestrator for DIGEST mode automation.

Coordinates chat file detection, enhancement extraction, and storage.
Auto-triggers on files with confidence score ≥5.

Workflow:
1. Detect chat file using ChatFileDetector
2. Extract enhancements using EnhancementProposalGenerator
3. Apply confidence scoring
4. Store proposals in enhancement-history.yaml
5. Optional auto-apply for high-confidence (score ≥9)
"""

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from cortex.sensory.chat_file_detector import ChatFileDetector, ChatFileScore
from cortex.learning.enhancement_proposal_generator import (
    EnhancementProposalGenerator,
    EnhancementProposal
)


@dataclass
class DigestResult:
    """
    Result of digest session operation.
    
    Attributes:
        success: Whether operation succeeded
        is_chat_file: Whether file was detected as chat
        confidence_score: Detection confidence (0-10)
        enhancements_found: Number of enhancements extracted
        enhancements: List of enhancement proposals
        auto_applied_count: Number of enhancements auto-applied
        review_queue_count: Number in review queue
        error_message: Error message if failed
        file_score: Detailed chat file score
    """
    success: bool
    is_chat_file: bool = False
    confidence_score: float = 0.0
    enhancements_found: int = 0
    enhancements: List[EnhancementProposal] = None  # type: ignore
    auto_applied_count: int = 0
    review_queue_count: int = 0
    error_message: str = ""
    file_score: Optional[ChatFileScore] = None
    
    def __post_init__(self):
        """Initialize lists if None."""
        if self.enhancements is None:
            self.enhancements = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "success": self.success,
            "is_chat_file": self.is_chat_file,
            "confidence_score": self.confidence_score,
            "enhancements_found": self.enhancements_found,
            "enhancement_proposals": [e.to_dict() for e in self.enhancements],
            "auto_applied_count": self.auto_applied_count,
            "review_queue_count": self.review_queue_count,
            "error_message": self.error_message,
        }


class DigestSessionOrchestrator:
    """
    Orchestrate DIGEST mode operations.
    
    Main entry point for automated enhancement detection and application.
    Integrates ChatFileDetector and EnhancementProposalGenerator.
    
    Attributes:
        detector: ChatFileDetector instance
        generator: EnhancementProposalGenerator instance
        history_path: Path to enhancement-history.yaml
    """
    
    def __init__(self, history_path: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            history_path: Custom path to enhancement-history.yaml
        """
        self.detector = ChatFileDetector()
        self.generator = EnhancementProposalGenerator()
        
        if history_path:
            self.history_path = Path(history_path)
        else:
            # Default to docs/meta/enhancement-history.yaml
            self.history_path = Path("docs/meta/enhancement-history.yaml")
    
    def detect_chat_file(self, content: str) -> DigestResult:
        """
        Detect if content is a chat file.
        
        Args:
            content: Text content to analyze
            
        Returns:
            DigestResult with detection information
        """
        score = self.detector.calculate_score(content)
        
        return DigestResult(
            success=True,
            is_chat_file=score.total_score >= 5.0,
            confidence_score=score.total_score,
            file_score=score
        )
    
    def extract_enhancements(
        self,
        content: str,
        source_file: str = "unknown"
    ) -> List[EnhancementProposal]:
        """
        Extract enhancement proposals from content.
        
        Args:
            content: Chat content to analyze
            source_file: Source file path
            
        Returns:
            List of enhancement proposals
        """
        return self.generator.generate_proposals(
            content=content,
            source_file=source_file,
            deduplicate=True
        )
    
    def digest_session(
        self,
        file_path: str,
        auto_apply: bool = False,
        min_confidence: float = 5.0
    ) -> DigestResult:
        """
        Execute full digest session on file.
        
        Workflow:
        1. Read file content
        2. Detect if chat file (score ≥ min_confidence)
        3. Extract enhancements
        4. Store proposals in enhancement-history.yaml
        5. Optionally auto-apply high-confidence enhancements
        
        Args:
            file_path: Path to file to digest
            auto_apply: Auto-apply high-confidence enhancements (score ≥9)
            min_confidence: Minimum confidence threshold
            
        Returns:
            DigestResult with operation outcome
        """
        try:
            # Read file
            path = Path(file_path)
            if not path.exists():
                return DigestResult(
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
            
            content = path.read_text(encoding='utf-8')
            
            # Detect chat file
            is_chat, score = self.detector.is_chat_file_from_path(file_path, min_confidence)
            
            if not is_chat:
                return DigestResult(
                    success=False,
                    is_chat_file=False,
                    confidence_score=score.total_score,
                    file_score=score,
                    error_message=f"Not a chat file (score {score.total_score:.1f} < {min_confidence})"
                )
            
            # Extract enhancements
            enhancements = self.extract_enhancements(content, file_path)
            
            if not enhancements:
                return DigestResult(
                    success=True,
                    is_chat_file=True,
                    confidence_score=score.total_score,
                    enhancements_found=0,
                    file_score=score,
                    error_message="No enhancements detected"
                )
            
            # Store proposals
            for proposal in enhancements:
                self.write_enhancement_proposal(proposal)
            
            # Auto-apply if enabled
            auto_applied = 0
            review_queue = 0
            
            if auto_apply:
                for proposal in enhancements:
                    if proposal.confidence_score >= 9.0:
                        # Auto-apply high-confidence
                        if self._auto_apply_enhancement(proposal):
                            auto_applied += 1
                    elif proposal.confidence_score >= 7.0:
                        # Add to review queue
                        review_queue += 1
            else:
                # All go to review queue
                review_queue = len(enhancements)
            
            return DigestResult(
                success=True,
                is_chat_file=True,
                confidence_score=score.total_score,
                enhancements_found=len(enhancements),
                enhancements=enhancements,
                auto_applied_count=auto_applied,
                review_queue_count=review_queue,
                file_score=score
            )
            
        except Exception as e:
            return DigestResult(
                success=False,
                error_message=f"Digest session failed: {str(e)}"
            )
    
    def read_enhancement_history(self) -> Dict[str, Any]:
        """
        Read enhancement-history.yaml.
        
        Returns:
            Dictionary with enhancement history
        """
        if not self.history_path.exists():
            # Create default structure
            return {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "enhancements": [],
                "rejected_recommendations": []
            }
        
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {"enhancements": []}
    
    def write_enhancement_proposal(self, proposal: EnhancementProposal) -> DigestResult:
        """
        Write enhancement proposal to enhancement-history.yaml.
        
        Args:
            proposal: Enhancement proposal to store
            
        Returns:
            DigestResult indicating success/failure
        """
        try:
            # Read current history
            history = self.read_enhancement_history()
            
            # Ensure enhancements list exists
            if "enhancements" not in history:
                history["enhancements"] = []
            
            # Add new proposal
            history["enhancements"].append(proposal.to_dict())
            
            # Update timestamp
            history["last_updated"] = datetime.now().isoformat()
            
            # Write back
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                yaml.dump(history, f, default_flow_style=False, sort_keys=False)
            
            return DigestResult(success=True)
            
        except Exception as e:
            return DigestResult(
                success=False,
                error_message=f"Failed to write proposal: {str(e)}"
            )
    
    def _auto_apply_enhancement(self, proposal: EnhancementProposal) -> bool:
        """
        Auto-apply high-confidence enhancement.
        
        Note: Stage 5 will implement full auto-apply pipeline.
        For now, just validate and log.
        
        Args:
            proposal: Enhancement to apply
            
        Returns:
            True if successfully applied
        """
        # TODO: Stage 5 - Full auto-apply pipeline
        # For now, just validate proposal structure
        return (
            proposal.confidence_score >= 9.0 and
            len(proposal.description) > 10 and
            proposal.category is not None
        )
