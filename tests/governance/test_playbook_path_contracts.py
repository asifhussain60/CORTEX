"""
GAP-128-A-03: Playbook folder paths mismatch actual locations.

Asserts that every playbook registered in cortex-master.yaml under the
`playbooks:` key resolves to a file that actually exists on disk.
Also asserts the canonical playbook directories are stable.

Drift lock: check-42-master-yaml-path-contract-lock.yaml
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
MASTER_YAML = REPO_ROOT / "cortex-registry" / "cortex-master.yaml"
PLAYBOOKS_ROOT = REPO_ROOT / "cortex-registry" / "playbooks"


def _registered_playbooks():
    """Return list of (id, file_path) tuples from cortex-master.yaml playbooks section."""
    data = yaml.safe_load(MASTER_YAML.read_text(encoding="utf-8"))
    playbooks = data.get("playbooks", [])
    if not isinstance(playbooks, list):
        return []
    results = []
    for entry in playbooks:
        if isinstance(entry, dict):
            pb_id = entry.get("id", "<no-id>")
            file_val = entry.get("file", "")
            results.append((pb_id, file_val))
    return results


class TestPlaybookPathContracts:
    """Every playbook registered in cortex-master.yaml must exist on disk."""

    def test_all_registered_playbooks_exist(self):
        """Each playbook file: pointer must resolve to an existing file."""
        playbooks = _registered_playbooks()
        missing = []
        for pb_id, file_path in playbooks:
            if not file_path:
                missing.append(f"{pb_id}: no file: field")
                continue
            resolved = REPO_ROOT / file_path
            if not resolved.exists():
                missing.append(f"{pb_id}: {file_path} → NOT FOUND")

        assert missing == [], (
            f"Found {len(missing)} playbook(s) with broken file: pointers:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_playbooks_root_directory_exists(self):
        """cortex-registry/playbooks/ directory must exist."""
        assert PLAYBOOKS_ROOT.is_dir(), (
            f"Playbooks directory not found: {PLAYBOOKS_ROOT}"
        )

    def test_playbooks_directory_has_content(self):
        """The playbooks directory must contain at least one YAML file."""
        yaml_files = list(PLAYBOOKS_ROOT.rglob("*.yaml"))
        assert len(yaml_files) >= 1, (
            f"No YAML files found in {PLAYBOOKS_ROOT}"
        )

    def test_registered_count_matches_actual_playbook_count(self):
        """Registered playbook count should be ≤ actual files on disk (extras are OK)."""
        registered = _registered_playbooks()
        on_disk = list(PLAYBOOKS_ROOT.rglob("*.yaml"))
        # It's fine to have unregistered playbooks, but registered > on-disk is a violation
        assert len(registered) <= len(on_disk), (
            f"More playbooks registered ({len(registered)}) than exist on disk ({len(on_disk)}). "
            "Check cortex-master.yaml playbooks section."
        )

    def test_playbook_file_pointers_use_forward_slash(self):
        """All playbook file: values must use forward-slash notation."""
        playbooks = _registered_playbooks()
        violations = [
            f"{pb_id}: {file_path}"
            for pb_id, file_path in playbooks
            if "\\" in file_path
        ]
        assert violations == [], (
            f"Playbook file: pointers use Windows backslash:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
