"""
Phase-Based Coverage Tracking for Planning System 3.0

Tracks test coverage for each planning phase independently, enabling:
- Coverage trend analysis across phases
- Per-phase validation against thresholds
- Historical coverage metrics for planning optimization

Phase 05 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PhaseCoverageData:
    """Coverage data for a single phase."""
    phase_name: str
    timestamp: str
    total_coverage: float
    lines_covered: int
    lines_total: int
    files: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CoverageTracker:
    """
    Tracks coverage metrics per planning phase.
    
    Features:
    - Per-phase coverage recording
    - Coverage trend analysis
    - Threshold validation
    - Persistent storage
    - Phase comparison
    """
    
    def __init__(self, session_id: str, coverage_dir: Optional[Path] = None):
        """
        Initialize coverage tracker.
        
        Args:
            session_id: Planning session identifier
            coverage_dir: Directory for coverage storage (defaults to .cortex/coverage/)
        """
        self.session_id = session_id
        self.coverage_data: Dict[str, PhaseCoverageData] = {}
        
        # Coverage storage
        if coverage_dir is None:
            coverage_dir = Path.cwd() / ".cortex" / "coverage"
        
        self.coverage_dir = coverage_dir
        self.coverage_file = self.coverage_dir / f"{session_id}.json"
        
        # Load existing coverage if available
        self._load_coverage()
        
        logger.info(f"📊 CoverageTracker initialized for session: {session_id}")
    
    def record_phase_coverage(
        self,
        phase_name: str,
        coverage_report: Dict[str, Any]
    ) -> None:
        """
        Record coverage for completed phase.
        
        Args:
            phase_name: Name of completed phase
            coverage_report: Coverage report from pytest-cov or similar tool
        
        Expected coverage_report format:
        {
            'timestamp': '2025-12-15T10:30:00',
            'totals': {
                'percent_covered': 85.5,
                'covered_lines': 342,
                'num_statements': 400
            },
            'files': {
                'src/module.py': {'coverage': 90.0, 'lines': [1,2,3,...]},
                ...
            }
        }
        """
        logger.info(f"📊 Recording coverage for phase: {phase_name}")
        
        # Extract coverage metrics
        totals = coverage_report.get('totals', {})
        
        phase_coverage = PhaseCoverageData(
            phase_name=phase_name,
            timestamp=coverage_report.get('timestamp', datetime.now().isoformat()),
            total_coverage=totals.get('percent_covered', 0.0),
            lines_covered=totals.get('covered_lines', 0),
            lines_total=totals.get('num_statements', 0),
            files=coverage_report.get('files', {})
        )
        
        self.coverage_data[phase_name] = phase_coverage
        
        # Persist to disk
        self._save_coverage()
        
        logger.info(
            f"✅ Phase coverage recorded: {phase_name} = {phase_coverage.total_coverage:.1f}% "
            f"({phase_coverage.lines_covered}/{phase_coverage.lines_total} lines)"
        )
    
    def get_coverage_trend(self) -> List[Dict[str, Any]]:
        """
        Get coverage trend across phases.
        
        Returns:
            List of phase coverage data sorted by timestamp
        """
        if not self.coverage_data:
            return []
        
        # Sort by timestamp
        sorted_phases = sorted(
            self.coverage_data.values(),
            key=lambda x: x.timestamp
        )
        
        trend = [
            {
                'phase': phase.phase_name,
                'coverage': phase.total_coverage,
                'lines_covered': phase.lines_covered,
                'lines_total': phase.lines_total,
                'timestamp': phase.timestamp
            }
            for phase in sorted_phases
        ]
        
        logger.debug(f"Coverage trend: {len(trend)} phases")
        return trend
    
    def validate_coverage_threshold(
        self,
        threshold: float = 80.0,
        phase_name: Optional[str] = None
    ) -> bool:
        """
        Check if coverage meets threshold.
        
        Args:
            threshold: Minimum coverage percentage required
            phase_name: Specific phase to validate (defaults to latest)
        
        Returns:
            True if coverage >= threshold
        """
        if not self.coverage_data:
            logger.warning("No coverage data available for validation")
            return False
        
        if phase_name:
            phase_coverage = self.coverage_data.get(phase_name)
            if not phase_coverage:
                logger.warning(f"Phase not found: {phase_name}")
                return False
        else:
            # Get latest phase
            sorted_phases = sorted(
                self.coverage_data.values(),
                key=lambda x: x.timestamp
            )
            phase_coverage = sorted_phases[-1]
        
        current_coverage = phase_coverage.total_coverage
        passes_threshold = current_coverage >= threshold
        
        status = "✅" if passes_threshold else "❌"
        logger.info(
            f"{status} Coverage validation: {current_coverage:.1f}% "
            f"({'PASS' if passes_threshold else 'FAIL'} >= {threshold}%)"
        )
        
        return passes_threshold
    
    def get_phase_coverage(self, phase_name: str) -> Optional[PhaseCoverageData]:
        """
        Get coverage data for specific phase.
        
        Args:
            phase_name: Name of phase
        
        Returns:
            PhaseCoverageData or None if not found
        """
        return self.coverage_data.get(phase_name)
    
    def get_coverage_delta(
        self,
        phase1: str,
        phase2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate coverage change between two phases.
        
        Args:
            phase1: Earlier phase name
            phase2: Later phase name
        
        Returns:
            Dict with delta metrics or None if phases not found
        """
        cov1 = self.coverage_data.get(phase1)
        cov2 = self.coverage_data.get(phase2)
        
        if not cov1 or not cov2:
            logger.warning(f"Cannot calculate delta: missing phase data")
            return None
        
        delta = {
            'phase1': phase1,
            'phase2': phase2,
            'coverage_change': cov2.total_coverage - cov1.total_coverage,
            'lines_added': cov2.lines_covered - cov1.lines_covered,
            'lines_total_change': cov2.lines_total - cov1.lines_total
        }
        
        logger.debug(f"Coverage delta {phase1}→{phase2}: {delta['coverage_change']:+.1f}%")
        return delta
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all coverage data.
        
        Returns:
            Summary dict with aggregate metrics
        """
        if not self.coverage_data:
            return {
                'session_id': self.session_id,
                'phases': 0,
                'current_coverage': 0.0,
                'trend': []
            }
        
        sorted_phases = sorted(
            self.coverage_data.values(),
            key=lambda x: x.timestamp
        )
        
        latest = sorted_phases[-1]
        first = sorted_phases[0]
        
        return {
            'session_id': self.session_id,
            'phases': len(self.coverage_data),
            'current_coverage': latest.total_coverage,
            'initial_coverage': first.total_coverage,
            'coverage_change': latest.total_coverage - first.total_coverage,
            'lines_covered': latest.lines_covered,
            'lines_total': latest.lines_total,
            'trend': self.get_coverage_trend()
        }
    
    def _load_coverage(self) -> None:
        """Load coverage data from disk."""
        if not self.coverage_file.exists():
            logger.debug(f"No existing coverage data: {self.coverage_file}")
            return
        
        try:
            with open(self.coverage_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct PhaseCoverageData objects
            for phase_name, phase_dict in data.items():
                self.coverage_data[phase_name] = PhaseCoverageData(**phase_dict)
            
            logger.info(f"📊 Loaded coverage data: {len(self.coverage_data)} phases")
        
        except Exception as e:
            logger.error(f"Failed to load coverage data: {e}")
    
    def _save_coverage(self) -> None:
        """Persist coverage data to disk."""
        try:
            # Ensure directory exists
            self.coverage_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            data = {
                phase_name: phase_coverage.to_dict()
                for phase_name, phase_coverage in self.coverage_data.items()
            }
            
            with open(self.coverage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"💾 Coverage data saved: {self.coverage_file}")
        
        except Exception as e:
            logger.error(f"Failed to save coverage data: {e}")
