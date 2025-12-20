"""
Smart Plan Loader - Token-Optimized Plan Loading Utility

Purpose: Intelligently load planning documents based on query intent to minimize token consumption.
Version: 1.0
Author: CORTEX Development Team
Created: 2025-12-20

Token Optimization Strategy:
- Tier 1 (Status Only): ~400 tokens (95% reduction)
- Tier 2 (Status + Master): ~1,200 tokens (94% reduction)
- Tier 3 (Status + Specific Phase): ~2,500 tokens (87% reduction)
- Tier 4 (Status + Worker): ~1,000 tokens (95% reduction)

Usage:
    loader = SmartPlanLoader("d:/PROJECTS/CORTEX")
    context = loader.load_plan_context("What's the current status?")  # Tier 1: ~400 tokens
    context = loader.load_plan_context("Tell me about Phase 6")       # Tier 3: ~2,500 tokens
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

logger = logging.getLogger(__name__)


class SmartPlanLoader:
    """
    Token-optimized plan loader with intelligent query routing.
    
    Loads minimal required content based on query intent:
    - Status queries: Load status file only (~400 tokens)
    - Architecture queries: Load status + master hub (~1,200 tokens)
    - Phase queries: Load status + specific phase file (~2,500 tokens)
    - Week queries: Load status + specific worker file (~1,000 tokens)
    """
    
    def __init__(self, cortex_root: Path | str):
        """
        Initialize smart plan loader.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.plan_base = self.cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0"
        self.metadata_path = self.plan_base / "metadata" / "plan-metadata.yaml"
        
        # Load metadata for intelligent routing
        self.metadata = self._load_metadata()
        
        logger.info(f"SmartPlanLoader initialized for plan: {self.plan_base.name}")
    
    def _load_metadata(self) -> Dict:
        """Load plan metadata YAML."""
        if not self.metadata_path.exists():
            logger.warning(f"Metadata file not found: {self.metadata_path}")
            return {}
        
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {}
    
    def load_plan_context(self, query: str) -> str:
        """
        Load plan context optimized for query intent.
        
        Args:
            query: User query string
            
        Returns:
            str: Loaded plan content (token-optimized)
        """
        # Determine query intent
        intent = self._classify_query_intent(query)
        
        logger.info(f"Query intent classified as: {intent['type']} (estimated {intent['estimated_tokens']} tokens)")
        
        # Route to appropriate loader
        if intent['type'] == 'status_only':
            return self._load_status_only()
        
        elif intent['type'] == 'architecture':
            return self._load_status_and_master()
        
        elif intent['type'] == 'phase_specific':
            return self._load_status_and_phase(intent['phase_id'])
        
        elif intent['type'] == 'week_specific':
            return self._load_status_and_week(intent['phase_id'], intent['week_number'])
        
        else:  # default
            return self._load_status_and_master()
    
    def _classify_query_intent(self, query: str) -> Dict:
        """
        Classify query intent for optimal loading strategy.
        
        Returns:
            Dict with keys: type, estimated_tokens, phase_id (optional), week_number (optional)
        """
        query_lower = query.lower()
        
        # Status-only queries
        status_keywords = ['status', 'summary', 'progress', 'overall', 'current state', 'where are we']
        if any(keyword in query_lower for keyword in status_keywords):
            return {
                'type': 'status_only',
                'estimated_tokens': 400
            }
        
        # Architecture/design queries
        arch_keywords = ['architecture', 'dependencies', 'structure', 'design', 'decisions', 'strategy']
        if any(keyword in query_lower for keyword in arch_keywords):
            return {
                'type': 'architecture',
                'estimated_tokens': 1200
            }
        
        # Phase-specific queries
        phase_match = re.search(r'phase\s+(\d+(?:\.\d+)?)', query_lower)
        if phase_match:
            phase_id = phase_match.group(1)
            return {
                'type': 'phase_specific',
                'phase_id': phase_id,
                'estimated_tokens': 2500
            }
        
        # Week-specific queries
        week_match = re.search(r'week\s+(\d+)', query_lower)
        if week_match:
            week_number = week_match.group(1)
            # Try to infer phase from current status
            phase_id = self._infer_phase_from_week(week_number)
            return {
                'type': 'week_specific',
                'phase_id': phase_id,
                'week_number': week_number,
                'estimated_tokens': 1000
            }
        
        # Default: Load status + master hub
        return {
            'type': 'default',
            'estimated_tokens': 1200
        }
    
    def _load_status_only(self) -> str:
        """Load status file only (~400 tokens)."""
        status_path = self.plan_base / "CORTEX4-STATUS.md"
        
        if not status_path.exists():
            logger.warning(f"Status file not found: {status_path}")
            return "Status file not available."
        
        try:
            content = status_path.read_text(encoding='utf-8')
            logger.info(f"Loaded status file: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"Failed to load status file: {e}")
            return f"Error loading status: {e}"
    
    def _load_status_and_master(self) -> str:
        """Load status + master hub (~1,200 tokens)."""
        status_content = self._load_status_only()
        
        master_path = self.plan_base / "00-MASTER-PLAN.md"
        
        if not master_path.exists():
            logger.warning(f"Master plan file not found: {master_path}")
            return status_content
        
        try:
            master_content = master_path.read_text(encoding='utf-8')
            logger.info(f"Loaded master plan: {len(master_content)} characters")
            
            # Combine with separator
            combined = f"{status_content}\n\n{'='*80}\n\n{master_content}"
            return combined
        except Exception as e:
            logger.error(f"Failed to load master plan: {e}")
            return status_content
    
    def _load_status_and_phase(self, phase_id: str) -> str:
        """
        Load status + specific phase file (~2,500 tokens).
        
        Args:
            phase_id: Phase identifier (e.g., "01", "06", "10")
        """
        status_content = self._load_status_only()
        
        # Find phase file from metadata
        phase_file = self._find_phase_file(phase_id)
        
        if not phase_file:
            logger.warning(f"Phase file not found for phase {phase_id}")
            return status_content
        
        phase_path = self.plan_base / phase_file
        
        if not phase_path.exists():
            logger.warning(f"Phase file does not exist: {phase_path}")
            return status_content
        
        try:
            phase_content = phase_path.read_text(encoding='utf-8')
            logger.info(f"Loaded phase file: {len(phase_content)} characters")
            
            # Combine with separator
            combined = f"{status_content}\n\n{'='*80}\n\n{phase_content}"
            return combined
        except Exception as e:
            logger.error(f"Failed to load phase file: {e}")
            return status_content
    
    def _load_status_and_week(self, phase_id: str, week_number: str) -> str:
        """
        Load status + specific worker file (~1,000 tokens).
        
        Args:
            phase_id: Phase identifier (e.g., "06")
            week_number: Week number (e.g., "9")
        """
        status_content = self._load_status_only()
        
        # Try to find worker file
        worker_pattern = f"workers/phase-{phase_id}*/week-{week_number}*.md"
        worker_files = list(self.plan_base.glob(worker_pattern))
        
        if not worker_files:
            logger.warning(f"No worker file found for week {week_number}")
            # Fallback to phase file
            return self._load_status_and_phase(phase_id)
        
        worker_path = worker_files[0]  # Take first match
        
        try:
            worker_content = worker_path.read_text(encoding='utf-8')
            logger.info(f"Loaded worker file: {len(worker_content)} characters")
            
            # Combine with separator
            combined = f"{status_content}\n\n{'='*80}\n\n{worker_content}"
            return combined
        except Exception as e:
            logger.error(f"Failed to load worker file: {e}")
            return status_content
    
    def _find_phase_file(self, phase_id: str) -> Optional[str]:
        """Find phase file path from metadata."""
        if not self.metadata or 'structure' not in self.metadata:
            return None
        
        phases = self.metadata['structure'].get('phases', [])
        
        for phase in phases:
            if phase.get('id') == phase_id:
                return phase.get('file')
        
        return None
    
    def _infer_phase_from_week(self, week_number: str) -> str:
        """Infer phase ID from week number using metadata."""
        if not self.metadata or 'structure' not in self.metadata:
            return "06"  # Default to current phase
        
        week_num = int(week_number)
        
        # Simple inference logic (can be enhanced)
        if week_num == 0:
            return "01"
        elif 1 <= week_num <= 3:
            return "03"
        elif 4 <= week_num <= 14:
            return "06"  # Most likely current phase
        elif 15 <= week_num <= 17:
            return "07"
        elif 18 <= week_num <= 20:
            return "08"
        elif week_num == 21:
            return "09"
        elif 22 <= week_num <= 37:
            return "10"
        else:
            return "06"  # Default
    
    def get_token_estimate(self, query: str) -> int:
        """
        Get estimated token count for query without loading content.
        
        Args:
            query: User query string
            
        Returns:
            int: Estimated token count
        """
        intent = self._classify_query_intent(query)
        return intent['estimated_tokens']
    
    def list_available_phases(self) -> List[Dict[str, str]]:
        """
        List all available phases with metadata.
        
        Returns:
            List of dicts with keys: id, name, status, file, estimated_tokens
        """
        if not self.metadata or 'structure' not in self.metadata:
            return []
        
        return self.metadata['structure'].get('phases', [])


# ============================================================================
# Convenience Functions
# ============================================================================

def load_plan_for_query(query: str, cortex_root: Optional[Path] = None) -> str:
    """
    Convenience function to load plan context for a query.
    
    Args:
        query: User query string
        cortex_root: CORTEX root directory (default: current directory's CORTEX root)
        
    Returns:
        str: Loaded plan content
    """
    if cortex_root is None:
        # Try to find CORTEX root
        cortex_root = Path.cwd()
        while cortex_root != cortex_root.parent:
            if (cortex_root / "cortex-brain").exists():
                break
            cortex_root = cortex_root.parent
    
    loader = SmartPlanLoader(cortex_root)
    return loader.load_plan_context(query)


def estimate_tokens_for_query(query: str, cortex_root: Optional[Path] = None) -> int:
    """
    Estimate token count for query without loading content.
    
    Args:
        query: User query string
        cortex_root: CORTEX root directory
        
    Returns:
        int: Estimated token count
    """
    if cortex_root is None:
        cortex_root = Path.cwd()
        while cortex_root != cortex_root.parent:
            if (cortex_root / "cortex-brain").exists():
                break
            cortex_root = cortex_root.parent
    
    loader = SmartPlanLoader(cortex_root)
    return loader.get_token_estimate(query)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example 1: Status-only query
    query1 = "What's the current status of CORTEX 4.0?"
    print(f"\nQuery 1: {query1}")
    print(f"Estimated tokens: {estimate_tokens_for_query(query1)}")
    
    # Example 2: Phase-specific query
    query2 = "Tell me about Phase 6 orchestrator consolidation"
    print(f"\nQuery 2: {query2}")
    print(f"Estimated tokens: {estimate_tokens_for_query(query2)}")
    
    # Example 3: Architecture query
    query3 = "What's the architecture strategy for agents?"
    print(f"\nQuery 3: {query3}")
    print(f"Estimated tokens: {estimate_tokens_for_query(query3)}")
    
    # Example 4: Load actual content
    loader = SmartPlanLoader(Path.cwd())
    content = loader.load_plan_context(query1)
    print(f"\nLoaded content length: {len(content)} characters")
