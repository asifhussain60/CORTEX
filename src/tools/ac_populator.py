"""
AC Index Populator - Populate Database from Master Plan

Parses cortex-master.yaml and populates governance.db with AC-IDs.
Creates the single source of truth for AC tracking.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.core.result import Result, Ok, Err
from src.core.path_resolver import resolve_path
from src.infrastructure.database import DatabaseManager


class ACPopulator:
    """
    Populates AC index from cortex-master.yaml.
    
    Extracts AC-IDs from:
    - phases.phase_XX.ac_ids lists
    - architecture_decisions.AR-XXX.acceptance_criteria
    - functional_requirements.FR-XXX.acceptance_criteria
    - non_functional_requirements.NFR-XXX.acceptance_criteria
    - hallucination_prevention.phase_X_enhancements.components
    - brittleness_fixes.critical_blockers/high_priority.ac_ids
    """
    
    def __init__(
        self,
        db: DatabaseManager,
        master_yaml_path: Optional[Path] = None
    ):
        """
        Initialize populator.
        
        Args:
            db: Initialized DatabaseManager
            master_yaml_path: Path to cortex-master.yaml (uses default if None)
        """
        self._db = db
        self._master_path = master_yaml_path or resolve_path(
            ".github", "roadmap", "cortex-master.yaml"
        )
    
    def parse_ac_ids(self) -> List[Dict[str, Any]]:
        """
        Parse all AC-IDs from master YAML.
        
        Returns:
            List of AC-ID dicts with ac_id, phase, description, test_file
        """
        with open(self._master_path, "r", encoding="utf-8") as f:
            master = yaml.safe_load(f)
        
        ac_ids = []
        ac_details = {}  # ac_id -> details
        
        # Build phase mapping from phases section
        phase_mapping = {}  # ac_id -> phase_id
        phases = master.get("phases", {})
        for phase_key, phase_data in phases.items():
            phase_id = phase_data.get("id", phase_key.upper().replace("_", "-"))
            for ac_id in phase_data.get("ac_ids", []):
                phase_mapping[ac_id] = phase_id
        
        # Extract from architecture_decisions
        for ar_id, ar_data in master.get("architecture_decisions", {}).items():
            for ac in ar_data.get("acceptance_criteria", []):
                ac_id = ac.get("ac_id")
                if ac_id:
                    ac_details[ac_id] = {
                        "description": ac.get("description", ""),
                        "test_file": ac.get("test", ""),
                        "source": f"AR: {ar_id}"
                    }
        
        # Extract from functional_requirements
        for fr_id, fr_data in master.get("functional_requirements", {}).items():
            for ac in fr_data.get("acceptance_criteria", []):
                ac_id = ac.get("ac_id")
                if ac_id:
                    ac_details[ac_id] = {
                        "description": ac.get("description", ""),
                        "test_file": ac.get("test", ""),
                        "source": f"FR: {fr_id}"
                    }
        
        # Extract from non_functional_requirements
        for nfr_id, nfr_data in master.get("non_functional_requirements", {}).items():
            for ac in nfr_data.get("acceptance_criteria", []):
                ac_id = ac.get("ac_id")
                if ac_id:
                    ac_details[ac_id] = {
                        "description": ac.get("description", ""),
                        "test_file": ac.get("test", ""),
                        "source": f"NFR: {nfr_id}"
                    }
        
        # Extract from hallucination_prevention
        hp = master.get("hallucination_prevention", {})
        for phase_key in ["phase_2_enhancements", "phase_4_enhancements"]:
            phase_data = hp.get(phase_key, {})
            for comp_name, comp_data in phase_data.get("components", {}).items():
                for ac_id in comp_data.get("ac_ids", []):
                    if ac_id not in ac_details:
                        ac_details[ac_id] = {
                            "description": comp_data.get("description", ""),
                            "test_file": "",
                            "source": f"HP: {comp_name}"
                        }
        
        # Extract from brittleness_fixes
        bf = master.get("brittleness_fixes", {})
        for section in ["critical_blockers", "high_priority"]:
            section_data = bf.get(section, {})
            for ac in section_data.get("ac_ids", []):
                ac_id = ac.get("id") if isinstance(ac, dict) else ac
                if ac_id and ac_id not in ac_details:
                    ac_details[ac_id] = {
                        "description": ac.get("problem", "") if isinstance(ac, dict) else "",
                        "test_file": "",
                        "source": f"BF: {section}"
                    }
        
        # Combine phase mapping with details
        for ac_id, phase_id in phase_mapping.items():
            details = ac_details.get(ac_id, {})
            ac_ids.append({
                "ac_id": ac_id,
                "phase": phase_id,
                "description": details.get("description", ""),
                "test_file": details.get("test_file", ""),
            })
        
        # Add any AC-IDs from details not in phase mapping
        for ac_id, details in ac_details.items():
            if ac_id not in phase_mapping:
                # Infer phase from AC-ID pattern
                phase = self._infer_phase(ac_id)
                ac_ids.append({
                    "ac_id": ac_id,
                    "phase": phase,
                    "description": details.get("description", ""),
                    "test_file": details.get("test_file", ""),
                })
        
        return ac_ids
    
    def _infer_phase(self, ac_id: str) -> str:
        """Infer phase from AC-ID pattern."""
        if "AR-001" in ac_id or "AR-002" in ac_id or "AR-003" in ac_id or "AR-004" in ac_id or "AR-005" in ac_id:
            return "PHASE-01"
        if "AR-008" in ac_id:
            return "PHASE-01"
        if "FR-001" in ac_id or "FR-003" in ac_id or "FR-004" in ac_id or "FR-005" in ac_id or "FR-006" in ac_id:
            return "PHASE-01"
        if "AR-006" in ac_id or "AR-007" in ac_id or "AR-009" in ac_id:
            return "PHASE-02"
        if "FR-002" in ac_id:
            return "PHASE-02"
        if "VALIDATE" in ac_id or "METRICS" in ac_id:
            return "PHASE-02"
        if "NFR-002" in ac_id or "NFR-004" in ac_id:
            return "PHASE-03"
        if "NFR-003" in ac_id or "COHERENCE" in ac_id or "EXPLAIN" in ac_id:
            return "PHASE-04"
        if "NFR-001" in ac_id or "BRITTLE" in ac_id:
            return "PHASE-05"
        if "AR-010" in ac_id:
            return "PHASE-PARALLEL"
        return "PHASE-01"  # Default
    
    def populate(self) -> Result[Dict[str, int]]:
        """
        Populate database with AC-IDs from master plan.
        
        Returns:
            Result containing stats dict with inserted/skipped/total counts
        """
        try:
            ac_ids = self.parse_ac_ids()
            
            inserted = 0
            skipped = 0
            errors = []
            
            for ac in ac_ids:
                # Check if already exists
                exists = self._db.ac_exists(ac["ac_id"])
                if exists.is_ok() and exists.unwrap():
                    skipped += 1
                    continue
                
                # Insert
                result = self._db.insert_ac(
                    ac_id=ac["ac_id"],
                    phase=ac["phase"],
                    title=ac["description"] or f"AC: {ac['ac_id']}",
                    description=ac["description"],
                    test_file=ac.get("test_file")
                )
                
                if result.is_ok():
                    inserted += 1
                else:
                    errors.append(f"{ac['ac_id']}: {result.error}")
            
            # Log population to audit
            self._db.insert_audit(
                operation="AC_INDEX_POPULATED",
                component="ac_populator",
                level="INFO",
                message=f"Populated AC index: {inserted} inserted, {skipped} skipped",
                metadata={
                    "inserted": inserted,
                    "skipped": skipped,
                    "total": len(ac_ids),
                    "errors": errors
                }
            )
            
            return Ok({
                "inserted": inserted,
                "skipped": skipped,
                "total": len(ac_ids),
                "errors": errors
            })
            
        except Exception as e:
            return Err(f"Population failed: {e}")
