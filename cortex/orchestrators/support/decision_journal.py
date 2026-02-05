"""
Phase 24.4 - Layer 4: Architecture Evolution Tracking (DecisionJournal)
Decision recording and retrieval system for architecture decisions

This orchestrator captures:
- Architecture decisions with rationale
- Challenge verdicts (PROCEED/PIVOT/BLOCK)
- DoR approval tracking
- Execution outcomes (SUCCESS/FAILURE/PENDING)
- Alternative approaches considered
- Impact assessments

Decision files stored in cortex-registry/_cortex-master/decisions/
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging


logger = logging.getLogger(__name__)


class DecisionJournal:
    """
    Journal for recording and retrieving architecture decisions.
    
    Captures decision rationale, alternatives, impact, and execution outcomes
    for Phase 24 Architecture Integrity System Layer 4.
    
    Example:
        journal = DecisionJournal(Path("cortex-registry/_cortex-master/decisions"))
        decision_id = journal.record_decision(
            decision="Use PhaseCompletionOrchestrator",
            rationale="Automate phase sync",
            alternatives=["Manual updates"],
            impact="60s sync latency",
            challenge_verdict="PROCEED",
            dor_approved=True
        )
    """
    
    def __init__(self, journal_dir: Path):
        """
        Initialize DecisionJournal.
        
        Args:
            journal_dir: Directory to store decision journal entries
        """
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)
    
    def record_decision(
        self,
        decision: str,
        rationale: str,
        alternatives: List[str],
        impact: str,
        challenge_verdict: Optional[str] = None,
        dor_approved: Optional[bool] = None,
        execution_outcome: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Record an architecture decision.
        
        Args:
            decision: The decision made
            rationale: Why this decision was made
            alternatives: Alternative approaches considered
            impact: Impact assessment
            challenge_verdict: PROCEED/PIVOT/BLOCK from Challenge phase
            dor_approved: Whether DoR gate approved (True/False)
            execution_outcome: SUCCESS/FAILURE/PENDING
            **metadata: Additional metadata
        
        Returns:
            decision_id: Unique ID for this decision
        
        Raises:
            ValueError: If required field missing
        """
        if not decision:
            raise ValueError("Required field 'decision' missing")
        
        # Generate unique decision ID
        timestamp = datetime.now()
        decision_id = timestamp.strftime("decision-%Y%m%d-%H%M%S")
        
        # Build decision record
        record = {
            "id": decision_id,
            "timestamp": timestamp.isoformat(),
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives,
            "impact": impact
        }
        
        # Add optional fields
        if challenge_verdict:
            record["challenge_verdict"] = challenge_verdict
        if dor_approved is not None:
            record["dor_approved"] = dor_approved
        if execution_outcome:
            record["execution_outcome"] = execution_outcome
        
        # Add any additional metadata
        record.update(metadata)
        
        # Write to file
        decision_file = self.journal_dir / f"{decision_id}.yaml"
        decision_file.write_text(yaml.dump(record, sort_keys=False))
        
        logger.info(f"Recorded decision: {decision_id}")
        return decision_id
    
    def load_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific decision by ID.
        
        Args:
            decision_id: Unique decision ID
        
        Returns:
            Decision record dict or None if not found
        """
        decision_file = self.journal_dir / f"{decision_id}.yaml"
        
        if not decision_file.exists():
            return None
        
        return yaml.safe_load(decision_file.read_text())
    
    def load_all_decisions(self) -> List[Dict[str, Any]]:
        """
        Load all decisions from journal.
        
        Returns:
            List of decision records
        """
        decisions = []
        
        for decision_file in self.journal_dir.glob("decision-*.yaml"):
            try:
                decision = yaml.safe_load(decision_file.read_text())
                decisions.append(decision)
            except Exception as e:
                logger.warning(f"Failed to load {decision_file}: {e}")
        
        return decisions
    
    def update_decision(self, decision_id: str, **updates) -> bool:
        """
        Update an existing decision.
        
        Args:
            decision_id: Unique decision ID
            **updates: Fields to update
        
        Returns:
            True if updated successfully, False if decision not found
        """
        decision = self.load_decision(decision_id)
        
        if decision is None:
            return False
        
        # Update fields
        decision.update(updates)
        
        # Write back to file
        decision_file = self.journal_dir / f"{decision_id}.yaml"
        decision_file.write_text(yaml.dump(decision, sort_keys=False))
        
        logger.info(f"Updated decision: {decision_id}")
        return True
    
    def search_decisions(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search decisions by criteria.
        
        Args:
            **criteria: Search criteria (e.g., challenge_verdict="PROCEED")
        
        Returns:
            List of matching decision records
        """
        all_decisions = self.load_all_decisions()
        matches = []
        
        for decision in all_decisions:
            if self._matches_criteria(decision, criteria):
                matches.append(decision)
        
        return matches
    
    def _matches_criteria(self, decision: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """
        Check if decision matches search criteria.
        
        Args:
            decision: Decision record
            criteria: Search criteria
        
        Returns:
            True if all criteria match
        """
        for key, value in criteria.items():
            if key not in decision or decision[key] != value:
                return False
        return True
