"""
Token Reduction Tracker for CORTEX Planning

Tracks token baselines and reductions across all planning operations.
Provides consistent metrics across all orchestrators.

Author: Asif Hussain
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class TokenBaseline:
    """Token baseline for a plan."""
    plan_id: str
    tokens: int
    files: int
    measurement_date: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "tokens": self.tokens,
            "files": self.files,
            "measurement_date": self.measurement_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenBaseline':
        return cls(
            plan_id=data["plan_id"],
            tokens=data["tokens"],
            files=data["files"],
            measurement_date=datetime.fromisoformat(data["measurement_date"])
        )


@dataclass
class PhaseReduction:
    """Token reduction for a single phase."""
    phase_number: int
    tokens_saved: int
    files_modified: List[str]
    recorded_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase_number": self.phase_number,
            "tokens_saved": self.tokens_saved,
            "files_modified": self.files_modified,
            "recorded_at": self.recorded_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhaseReduction':
        return cls(
            phase_number=data["phase_number"],
            tokens_saved=data["tokens_saved"],
            files_modified=data["files_modified"],
            recorded_at=datetime.fromisoformat(data["recorded_at"])
        )


class TokenReductionTracker:
    """
    Unified token tracking across all plans.
    
    Stores baselines, tracks reductions, calculates percentages.
    """
    
    def __init__(self, metrics_dir: Path = None):
        """
        Initialize token reduction tracker.
        
        Args:
            metrics_dir: Directory for metrics storage (default: cortex-brain/metrics)
        """
        self.metrics_dir = metrics_dir or Path("cortex-brain/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.baselines_file = self.metrics_dir / "token-baselines.json"
        self.reductions_file = self.metrics_dir / "token-reductions.json"
        
        self.baselines = self._load_baselines()
        self.reductions = self._load_reductions()
        
        logger.info(f"✅ TokenReductionTracker initialized (metrics: {self.metrics_dir})")
    
    def establish_baseline(
        self,
        plan_id: str,
        token_count: int,
        file_count: int,
        measurement_date: datetime
    ):
        """
        Record baseline for a plan.
        
        Args:
            plan_id: Plan identifier
            token_count: Total tokens at baseline
            file_count: Total files at baseline
            measurement_date: When measurement was taken
        """
        baseline = TokenBaseline(
            plan_id=plan_id,
            tokens=token_count,
            files=file_count,
            measurement_date=measurement_date
        )
        
        self.baselines[plan_id] = baseline
        self._save_baselines()
        
        logger.info(f"📊 Baseline established: {plan_id} = {self.format_tokens(token_count)} tokens, {file_count} files")
    
    def record_reduction(
        self,
        plan_id: str,
        phase_number: int,
        tokens_saved: int,
        files_modified: List[str]
    ):
        """
        Record token reduction for a phase.
        
        Args:
            plan_id: Plan identifier
            phase_number: Phase number
            tokens_saved: Tokens saved in this phase
            files_modified: Files modified in this phase
        """
        if plan_id not in self.reductions:
            self.reductions[plan_id] = []
        
        reduction = PhaseReduction(
            phase_number=phase_number,
            tokens_saved=tokens_saved,
            files_modified=files_modified,
            recorded_at=datetime.now()
        )
        
        self.reductions[plan_id].append(reduction)
        self._save_reductions()
        
        logger.info(f"📉 Token reduction recorded: {plan_id} Phase {phase_number} = {self.format_tokens(tokens_saved)} saved")
    
    def get_plan_metrics(self, plan_id: str) -> Dict:
        """
        Get all metrics for a plan.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Dictionary with baseline, reductions, totals
        """
        if plan_id not in self.baselines:
            return {
                "error": f"No baseline for plan {plan_id}",
                "baseline": None,
                "reductions": [],
                "total_saved": 0,
                "current_tokens": 0,
                "percentage_reduction": 0.0
            }
        
        baseline = self.baselines[plan_id]
        reductions = self.reductions.get(plan_id, [])
        
        total_saved = sum(r.tokens_saved for r in reductions)
        current_tokens = baseline.tokens - total_saved
        percentage = self.calculate_percentage(baseline.tokens, current_tokens)
        
        return {
            "baseline": {
                "tokens": baseline.tokens,
                "files": baseline.files,
                "measurement_date": baseline.measurement_date.isoformat()
            },
            "reductions": [r.to_dict() for r in reductions],
            "total_saved": total_saved,
            "current_tokens": current_tokens,
            "percentage_reduction": percentage
        }
    
    def calculate_percentage(self, baseline: int, current: int) -> float:
        """
        Calculate reduction percentage.
        
        Args:
            baseline: Baseline token count
            current: Current token count
        
        Returns:
            Percentage reduction (0-100)
        """
        if baseline == 0:
            return 0.0
        
        reduction = baseline - current
        percentage = (reduction / baseline) * 100
        return round(percentage, 2)
    
    def format_tokens(self, tokens: int, include_label: bool = False) -> str:
        """
        Format tokens with K/M suffix and optional label.
        
        Args:
            tokens: Token count
            include_label: If True, append " saved" to clarify meaning
        
        Returns:
            Formatted string (e.g., "6.7M saved", "150K saved", "500")
        """
        if tokens >= 1000000:
            formatted = f"{tokens / 1000000:.1f}M"
        elif tokens >= 1000:
            formatted = f"{tokens / 1000:.1f}K"
        else:
            formatted = str(tokens)
        
        if include_label:
            return f"{formatted} saved"
        return formatted
    
    # ===== Private Methods =====
    
    def _load_baselines(self) -> Dict[str, TokenBaseline]:
        """Load baselines from disk."""
        if not self.baselines_file.exists():
            return {}
        
        try:
            with open(self.baselines_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    plan_id: TokenBaseline.from_dict(baseline_data)
                    for plan_id, baseline_data in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load baselines: {e}")
            return {}
    
    def _save_baselines(self):
        """Save baselines to disk."""
        try:
            data = {
                plan_id: baseline.to_dict()
                for plan_id, baseline in self.baselines.items()
            }
            with open(self.baselines_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    def _load_reductions(self) -> Dict[str, List[PhaseReduction]]:
        """Load reductions from disk."""
        if not self.reductions_file.exists():
            return {}
        
        try:
            with open(self.reductions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    plan_id: [PhaseReduction.from_dict(r) for r in reductions_data]
                    for plan_id, reductions_data in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load reductions: {e}")
            return {}
    
    def _save_reductions(self):
        """Save reductions to disk."""
        try:
            data = {
                plan_id: [r.to_dict() for r in reductions]
                for plan_id, reductions in self.reductions.items()
            }
            with open(self.reductions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save reductions: {e}")
