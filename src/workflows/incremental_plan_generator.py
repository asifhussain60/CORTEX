"""
Incremental Plan Generator

Purpose: Generate planning documents in token-budgeted chunks with skeleton-first approach
Strategy: 200-token skeleton → 500-token sections → User checkpoints
Benefits: Prevents context overflow, enables user review, memory-efficient

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlanSection:
    """Represents a section of a planning document"""
    name: str
    content: str
    token_count: int
    status: str  # 'pending', 'in-progress', 'complete', 'approved'
    subsections: List['PlanSection'] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class PlanCheckpoint:
    """Represents a user checkpoint in planning workflow"""
    checkpoint_id: str
    section_name: str
    content_preview: str
    token_count: int
    status: str  # 'pending_approval', 'approved', 'rejected'
    feedback: Optional[str] = None


class IncrementalPlanGenerator:
    """
    Generates planning documents incrementally with token budget enforcement.
    
    Features:
    - Token budget: 500 tokens/chunk (configurable)
    - Skeleton-first: 200-token structure before content
    - User checkpoints: Approve/reject between major sections
    - Context preservation: Stores state in Tier 1 memory
    
    Workflow:
    1. Generate skeleton (200 tokens) → User approval
    2. Fill Phase 1 sections (500 tokens each) → User approval
    3. Fill Phase 2 sections → User approval
    4. Fill Phase 3 sections → User approval
    5. Generate final markdown → Complete
    """
    
    # Token budgets
    SKELETON_TOKEN_LIMIT = 200
    SECTION_TOKEN_LIMIT = 500
    CHUNK_TOKEN_LIMIT = 500
    
    def __init__(
        self, 
        brain_path: Path,
        session_id: Optional[str] = None,
        skeleton_token_limit: int = 200,
        section_token_limit: int = 500
    ):
        """
        Initialize incremental plan generator.
        
        Args:
            brain_path: Path to CORTEX brain directory
            session_id: Optional session ID for checkpoint tracking
            skeleton_token_limit: Token limit for skeleton generation
            section_token_limit: Token limit per section
        """
        self.brain_path = brain_path
        self.session_id = session_id or self._generate_session_id()
        self.skeleton_token_limit = skeleton_token_limit
        self.section_token_limit = section_token_limit
        
        # Planning state
        self.skeleton: Optional[Dict[str, Any]] = None
        self.sections: Dict[str, PlanSection] = {}
        self.checkpoints: List[PlanCheckpoint] = []
        self.current_phase: str = 'not_started'
        
        logger.info(f"🚀 IncrementalPlanGenerator initialized (session: {self.session_id})")
        logger.info(f"📊 Token limits: Skeleton={skeleton_token_limit}, Section={section_token_limit}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for checkpoint tracking"""
        from datetime import datetime
        import random
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"plan-{timestamp}-{random_suffix}"
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximation: 1 token ≈ 4 characters).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Simple approximation: 1 token ≈ 4 characters
        # In production, use actual tokenizer (tiktoken)
        return len(text) // 4
    
    def generate_skeleton(self, feature_requirements: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Generate 200-token skeleton structure for planning document.
        
        Args:
            feature_requirements: Feature requirements from user input
            
        Returns:
            Tuple of (skeleton structure, token count)
        """
        logger.info("🏗️ Generating skeleton structure (200-token limit)...")
        
        skeleton = {
            'feature_name': feature_requirements.get('feature_name', 'Unnamed Feature'),
            'phases': [
                {
                    'name': 'Phase 1: Foundation',
                    'sections': ['Requirements', 'Dependencies', 'Architecture'],
                    'estimated_tokens': 150
                },
                {
                    'name': 'Phase 2: Core Implementation',
                    'sections': ['Implementation Plan', 'Test Strategy', 'Integration Points'],
                    'estimated_tokens': 200
                },
                {
                    'name': 'Phase 3: Validation',
                    'sections': ['Acceptance Criteria', 'Security Review', 'Deployment Plan'],
                    'estimated_tokens': 150
                }
            ],
            'total_estimated_tokens': 500,
            'checkpoint_count': 4  # Skeleton + 3 phases
        }
        
        # Calculate actual token count for skeleton
        skeleton_text = self._serialize_skeleton(skeleton)
        token_count = self.count_tokens(skeleton_text)
        
        if token_count > self.skeleton_token_limit:
            logger.warning(f"⚠️ Skeleton exceeds limit ({token_count}/{self.skeleton_token_limit} tokens)")
        else:
            logger.info(f"✅ Skeleton generated ({token_count}/{self.skeleton_token_limit} tokens)")
        
        self.skeleton = skeleton
        self.current_phase = 'skeleton_complete'
        
        return skeleton, token_count
    
    def _serialize_skeleton(self, skeleton: Dict[str, Any]) -> str:
        """Serialize skeleton to text for token counting"""
        text = f"# {skeleton['feature_name']}\n\n"
        for phase in skeleton['phases']:
            text += f"## {phase['name']}\n"
            for section in phase['sections']:
                text += f"- {section}\n"
        return text
    
    def fill_section(
        self, 
        section_name: str, 
        context: Dict[str, Any],
        max_tokens: Optional[int] = None
    ) -> Tuple[PlanSection, bool]:
        """
        Fill a single section with content, respecting token limits.
        
        Args:
            section_name: Name of section to fill
            context: Context data for section generation
            max_tokens: Override default section token limit
            
        Returns:
            Tuple of (PlanSection object, needs_checkpoint flag)
        """
        token_limit = max_tokens or self.section_token_limit
        logger.info(f"📝 Filling section: {section_name} (limit: {token_limit} tokens)")
        
        # Generate section content (placeholder - will integrate with LLM in production)
        content = self._generate_section_content(section_name, context)
        token_count = self.count_tokens(content)
        
        # Check if section needs chunking
        needs_chunking = token_count > token_limit
        
        if needs_chunking:
            logger.warning(f"⚠️ Section exceeds limit ({token_count}/{token_limit} tokens) - chunking needed")
            # Split into chunks (will implement in next iteration)
            content = content[:token_limit * 4]  # Rough truncation for now
            token_count = token_limit
        
        section = PlanSection(
            name=section_name,
            content=content,
            token_count=token_count,
            status='complete'
        )
        
        self.sections[section_name] = section
        
        # Checkpoint needed if this completes a phase
        needs_checkpoint = self._is_phase_complete(section_name)
        
        logger.info(f"✅ Section complete ({token_count} tokens, checkpoint: {needs_checkpoint})")
        
        return section, needs_checkpoint
    
    def _generate_section_content(self, section_name: str, context: Dict[str, Any]) -> str:
        """
        Generate content for a section (placeholder).
        
        In production, this will call LLM with section-specific prompts.
        For now, returns placeholder content for testing.
        """
        return f"""
## {section_name}

{context.get('description', 'Section content will be generated here.')}

**Key Points:**
- Point 1 related to {section_name}
- Point 2 with implementation details
- Point 3 covering edge cases

**Implementation Notes:**
This section will be filled with detailed content based on feature requirements
and DoR/DoD validation results.
"""
    
    def _is_phase_complete(self, section_name: str) -> bool:
        """Check if completing this section finishes a phase"""
        # Simplified check - in production, track phase progress
        phase_endings = ['Architecture', 'Integration Points', 'Deployment Plan']
        return section_name in phase_endings
    
    def create_checkpoint(
        self, 
        section_name: str, 
        content_preview: str
    ) -> PlanCheckpoint:
        """
        Create a checkpoint for user approval.
        
        Args:
            section_name: Name of section at checkpoint
            content_preview: Preview of content (first 200 chars)
            
        Returns:
            PlanCheckpoint object
        """
        checkpoint_id = f"cp-{len(self.checkpoints) + 1}"
        token_count = sum(s.token_count for s in self.sections.values())
        
        checkpoint = PlanCheckpoint(
            checkpoint_id=checkpoint_id,
            section_name=section_name,
            content_preview=content_preview[:200],
            token_count=token_count,
            status='pending_approval'
        )
        
        self.checkpoints.append(checkpoint)
        
        logger.info(f"🚦 Checkpoint created: {checkpoint_id} at {section_name}")
        logger.info(f"📊 Total tokens so far: {token_count}")
        
        return checkpoint
    
    def approve_checkpoint(self, checkpoint_id: str, feedback: Optional[str] = None) -> bool:
        """
        Approve a checkpoint and continue generation.
        
        Args:
            checkpoint_id: ID of checkpoint to approve
            feedback: Optional user feedback
            
        Returns:
            True if approved successfully, False if checkpoint not found
        """
        for checkpoint in self.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                checkpoint.status = 'approved'
                checkpoint.feedback = feedback
                logger.info(f"✅ Checkpoint approved: {checkpoint_id}")
                return True
        
        logger.warning(f"⚠️ Checkpoint not found: {checkpoint_id}")
        return False
    
    def reject_checkpoint(self, checkpoint_id: str, reason: str) -> bool:
        """
        Reject a checkpoint and request regeneration.
        
        Args:
            checkpoint_id: ID of checkpoint to reject
            reason: Reason for rejection
            
        Returns:
            True if rejected successfully, False if checkpoint not found
        """
        for checkpoint in self.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                checkpoint.status = 'rejected'
                checkpoint.feedback = reason
                logger.info(f"❌ Checkpoint rejected: {checkpoint_id}")
                logger.info(f"📝 Reason: {reason}")
                return True
        
        logger.warning(f"⚠️ Checkpoint not found: {checkpoint_id}")
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current generation status.
        
        Returns:
            Status dictionary with progress info
        """
        total_tokens = sum(s.token_count for s in self.sections.values())
        completed_sections = len([s for s in self.sections.values() if s.status == 'complete'])
        
        return {
            'session_id': self.session_id,
            'current_phase': self.current_phase,
            'total_tokens': total_tokens,
            'completed_sections': completed_sections,
            'total_sections': len(self.skeleton['phases']) * 3 if self.skeleton else 0,
            'checkpoints': len(self.checkpoints),
            'pending_approvals': len([cp for cp in self.checkpoints if cp.status == 'pending_approval'])
        }
