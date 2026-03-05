"""Phase 128-a: Master YAML Path Contract Tests.

Authority: GAP-128-A-01 (cortex-master.yaml file: pointers to non-existent paths)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/planned/phase-128-conflict-drift-eradication.yaml

These tests verify that all file: pointers in cortex-master.yaml point to actual files.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestMasterYamlPathContracts:
    """Verify cortex-master.yaml file: pointers resolve to actual files."""

    @pytest.fixture
    def master_yaml(self) -> dict:
        """Load cortex-master.yaml."""
        master_path = PROJECT_ROOT / "cortex-registry" / "cortex-master.yaml"
        with open(master_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_phase_detail_files_exist(self, master_yaml: dict) -> None:
        """All phase_detail_files[].file pointers must resolve to actual files.
        
        GAP-128-A-01: cortex-master.yaml file: pointers to non-existent paths
        """
        phase_detail_files = master_yaml.get("phase_detail_files", [])
        assert phase_detail_files, "phase_detail_files section must exist"

        missing_files: list[str] = []
        for entry in phase_detail_files:
            file_path = entry.get("file")
            if not file_path:
                continue  # Some entries may have only 'note' without 'file'
            
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                missing_files.append(f"{entry.get('id')}: {file_path}")

        assert not missing_files, (
            f"Found {len(missing_files)} phase_detail_files with missing file pointers:\n"
            + "\n".join(f"  - {f}" for f in missing_files)
        )

    def test_playbook_files_exist(self, master_yaml: dict) -> None:
        """All playbooks[].file pointers must resolve to actual files."""
        playbooks = master_yaml.get("playbooks", [])
        
        missing_files: list[str] = []
        for entry in playbooks:
            file_path = entry.get("file")
            if not file_path:
                continue
            
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                missing_files.append(f"{entry.get('id')}: {file_path}")

        assert not missing_files, (
            f"Found {len(missing_files)} playbooks with missing file pointers:\n"
            + "\n".join(f"  - {f}" for f in missing_files)
        )

    def test_phases_section_file_refs_exist(self, master_yaml: dict) -> None:
        """All phases[].file pointers must resolve to actual files."""
        phases = master_yaml.get("phases", [])
        
        missing_files: list[str] = []
        for entry in phases:
            file_path = entry.get("file")
            if not file_path:
                continue
            
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                missing_files.append(f"{entry.get('id')}: {file_path}")

        assert not missing_files, (
            f"Found {len(missing_files)} phases with missing file pointers:\n"
            + "\n".join(f"  - {f}" for f in missing_files)
        )

    def test_no_duplicate_phase_ids_in_detail_files(self, master_yaml: dict) -> None:
        """Phase IDs in phase_detail_files must be unique."""
        phase_detail_files = master_yaml.get("phase_detail_files", [])
        
        ids = [entry.get("id") for entry in phase_detail_files if entry.get("id")]
        duplicates = [id_ for id_ in ids if ids.count(id_) > 1]
        unique_duplicates = list(set(duplicates))

        assert not unique_duplicates, (
            f"Found {len(unique_duplicates)} duplicate phase IDs in phase_detail_files:\n"
            + "\n".join(f"  - {d}" for d in unique_duplicates)
        )

    def test_completed_phases_point_to_completed_dir(self, master_yaml: dict) -> None:
        """COMPLETE phases should have file pointers to completed/ directory."""
        phase_detail_files = master_yaml.get("phase_detail_files", [])
        
        misplaced: list[str] = []
        for entry in phase_detail_files:
            status = entry.get("status", "")
            file_path = entry.get("file", "")
            
            if status == "COMPLETE" and file_path:
                if "/planned/" in file_path and "/completed/" not in file_path:
                    misplaced.append(f"{entry.get('id')}: {file_path}")

        assert not misplaced, (
            f"Found {len(misplaced)} COMPLETE phases pointing to planned/ instead of completed/:\n"
            + "\n".join(f"  - {m}" for m in misplaced)
        )

    def test_planned_phases_point_to_planned_dir(self, master_yaml: dict) -> None:
        """PLANNED phases should have file pointers to planned/ directory."""
        phase_detail_files = master_yaml.get("phase_detail_files", [])
        
        misplaced: list[str] = []
        for entry in phase_detail_files:
            status = entry.get("status", "")
            file_path = entry.get("file", "")
            
            if status == "PLANNED" and file_path:
                if "/completed/" in file_path and "/planned/" not in file_path:
                    misplaced.append(f"{entry.get('id')}: {file_path}")

        assert not misplaced, (
            f"Found {len(misplaced)} PLANNED phases pointing to completed/ instead of planned/:\n"
            + "\n".join(f"  - {m}" for m in misplaced)
        )
