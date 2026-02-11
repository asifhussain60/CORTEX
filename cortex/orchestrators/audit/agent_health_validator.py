"""
AgentHealthValidator - AUDIT Mode P1.5 Agent Health Check (Stage 2).

Validates agent health across 4 dimensions:
1. Version tracking (version numbers + updated dates + AGENT-INDEX.md sync)
2. Capability coverage (all 6 modes have assigned agents)
3. Cross-reference integrity (file references valid)
4. AGENT-INDEX.md synchronization (complete + accurate)

Checks:
1. P1.5-004: Agent version drift detection
2. P1.5-005: Agent capability gaps
3. P1.5-006: Agent cross-reference integrity
4. P1.5-007: AGENT-INDEX.md accuracy

Author: Asif Hussain
Date: 2026-02-07
Phase: 39 Stage 2
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Constants
AGENT_DIRECTORY = ".github/agents/core"
"""Directory containing core agent files."""

AGENT_INDEX_FILE = ".github/agents/AGENT-INDEX.md"
"""Agent index file for synchronization validation."""

CORTEX_MODES = [
    "AUDIT",
    "DESIGN",
    "PLAN",
    "DIGEST",
    "QUERY",
    "META-AUDIT"
]
"""Six operational modes that require agent coverage."""


@dataclass
class AgentMetadata:
    """Metadata extracted from agent file."""
    file_path: str
    version: Optional[str]
    updated: Optional[str]
    modes: List[str]
    file_references: List[str]
    description: Optional[str]
    in_index: bool = False
    index_version: Optional[str] = None


# AC_START: AC-PHASE39-004
# Description: AgentHealthValidator GREEN phase implementation
# Author: Asif Hussain
# Date: 2026-02-07


class AgentHealthValidator:
    """
    Validate agent health across CORTEX architecture.

    Ensures:
    - Version tracking consistency
    - Capability coverage completeness
    - Cross-reference integrity
    - AGENT-INDEX.md synchronization
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            repo_root: Repository root path (defaults to current directory)
        """
        self.repo_root = repo_root or Path.cwd()
        self.agent_dir = self.repo_root / AGENT_DIRECTORY
        self.index_file = self.repo_root / AGENT_INDEX_FILE

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all agent health validation checks.

        Returns:
            Dict with:
            - healthy: bool (all checks passed)
            - issues: List[str] (human-readable issues)
            - details: Dict (detailed check results)
        """
        # Extract metadata from all agent files
        agent_files = self._discover_agent_files()
        agents_metadata = {}

        for agent_file in agent_files:
            content = agent_file.read_text()
            metadata = self.extract_metadata(content, str(agent_file.relative_to(self.repo_root)))
            agents_metadata[agent_file.name] = metadata

        # Load index data
        index_data = self._load_agent_index()

        # Run checks
        version_tracking = self.check_version_tracking(agents_metadata, index_data)
        capability_coverage = self.check_capability_coverage(agents_metadata)
        cross_references = self.check_cross_references(agents_metadata)
        index_sync = self.check_index_sync(agents_metadata, index_data)

        # Aggregate issues
        issues = []

        if version_tracking["missing_versions"]:
            for agent in version_tracking["missing_versions"]:
                issues.append(f"P1.5-004: {agent} missing version number")

        if version_tracking["missing_dates"]:
            for agent in version_tracking["missing_dates"]:
                issues.append(f"P1.5-004: {agent} missing updated date")

        if version_tracking["version_mismatches"]:
            for agent, details in version_tracking["version_mismatches"].items():
                issues.append(
                    f"P1.5-004: {agent} version mismatch "
                    f"(file: {details['file_version']}, index: {details['index_version']})"
                )

        if capability_coverage["uncovered_modes"]:
            for mode in capability_coverage["uncovered_modes"]:
                issues.append(f"P1.5-005: No agents assigned to {mode} mode")

        if capability_coverage["unassigned_agents"]:
            for agent in capability_coverage["unassigned_agents"]:
                issues.append(f"P1.5-005: {agent} has no mode assignment")

        if cross_references["broken_references"]:
            for agent, refs in cross_references["broken_references"].items():
                for ref in refs:
                    issues.append(f"P1.5-006: {agent} has broken reference: {ref}")

        if index_sync["missing_from_index"]:
            for agent in index_sync["missing_from_index"]:
                issues.append(f"P1.5-007: {agent} not listed in AGENT-INDEX.md")

        if index_sync["orphaned_entries"]:
            for entry in index_sync["orphaned_entries"]:
                issues.append(f"P1.5-007: AGENT-INDEX.md has orphaned entry: {entry}")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "details": {
                "version_tracking": version_tracking,
                "capability_coverage": capability_coverage,
                "cross_references": cross_references,
                "index_sync": index_sync
            }
        }

    def _discover_agent_files(self) -> List[Path]:
        """Discover all agent .md files in agent directory."""
        if not self.agent_dir.exists():
            return []

        return sorted(self.agent_dir.glob("*.md"))

    def extract_metadata(self, content: str, file_path: str) -> AgentMetadata:
        """
        Extract metadata from agent file content.

        Args:
            content: Agent file content
            file_path: Relative file path

        Returns:
            AgentMetadata with extracted fields
        """
        version = self._extract_version(content)
        updated = self._extract_updated_date(content)
        modes = self._extract_modes(content)
        file_references = self._extract_file_references(content)
        description = self._extract_description(content)

        return AgentMetadata(
            file_path=file_path,
            version=version,
            updated=updated,
            modes=modes,
            file_references=file_references,
            description=description
        )

    def _extract_version(self, content: str) -> Optional[str]:
        """Extract version from agent header."""
        match = re.search(r'\*\*Version:\*\*\s+([\d.]+)', content)
        return match.group(1) if match else None

    def _extract_updated_date(self, content: str) -> Optional[str]:
        """Extract updated date from agent header."""
        match = re.search(r'\*\*Updated:\*\*\s+([\d-]+)', content)
        return match.group(1) if match else None

    def _extract_modes(self, content: str) -> List[str]:
        """Extract mode assignments from agent content."""
        modes = []
        for mode in CORTEX_MODES:
            # Look for patterns like "AUDIT Mode", "AUDIT mode", "**AUDIT**"
            if re.search(rf'\b{mode}\b', content, re.IGNORECASE):
                modes.append(mode)
        return modes

    def _extract_file_references(self, content: str) -> List[str]:
        """Extract file references from agent markdown content."""
        references = []

        # Pattern 1: Markdown links [text](path)
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for _, path in md_links:
            if not path.startswith(('http://', 'https://', '#')):
                references.append(path)

        # Pattern 2: Code backticks with file extensions
        code_refs = re.findall(r'`([^`]+\.(md|py|yaml|yml|json))`', content)
        for path, _ in code_refs:
            references.append(path)

        return references

    def _extract_description(self, content: str) -> Optional[str]:
        """Extract agent description (first paragraph after title)."""
        lines = content.split('\n')
        description_lines = []
        found_title = False

        for line in lines:
            line = line.strip()
            if line.startswith('#') and not found_title:
                found_title = True
                continue

            if found_title and line and not line.startswith('#'):
                description_lines.append(line)
            elif found_title and line.startswith('#'):
                break

        return ' '.join(description_lines[:2]) if description_lines else None

    def _load_agent_index(self) -> Dict[str, Dict[str, str]]:
        """
        Load agent index data from AGENT-INDEX.md.

        Returns:
            Dict of agent_name → {version, description}
        """
        if not self.index_file.exists():
            return {}

        content = self.index_file.read_text()
        index_data = {}

        # Parse markdown table format
        # Expected: | Agent Name | Version | Description |
        for line in content.split('\n'):
            line = line.strip()
            if '|' in line and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:  # | col1 | col2 | col3 |
                    agent_name = parts[1]
                    version = parts[2]
                    description = parts[3]

                    if agent_name and agent_name != "Agent Name":
                        # Normalize agent name to filename
                        if not agent_name.endswith('.md'):
                            agent_name = f"{agent_name}.md"

                        index_data[agent_name] = {
                            "version": version,
                            "description": description
                        }

        return index_data

    def check_version_tracking(
        self,
        agents_metadata: Dict[str, AgentMetadata],
        index_data: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Check P1.5-004: Agent version tracking.

        Args:
            agents_metadata: Dict of agent_name → AgentMetadata
            index_data: Dict from AGENT-INDEX.md

        Returns:
            Dict with:
            - missing_versions: List[str]
            - missing_dates: List[str]
            - version_mismatches: Dict[agent, {file_version, index_version}]
        """
        missing_versions = []
        missing_dates = []
        version_mismatches = {}

        for agent_name, metadata in agents_metadata.items():
            if metadata.version is None:
                missing_versions.append(agent_name)

            if metadata.updated is None:
                missing_dates.append(agent_name)

            # Check version sync with index
            if agent_name in index_data:
                index_version = index_data[agent_name]["version"]
                if metadata.version and metadata.version != index_version:
                    version_mismatches[agent_name] = {
                        "file_version": metadata.version,
                        "index_version": index_version
                    }

        return {
            "missing_versions": missing_versions,
            "missing_dates": missing_dates,
            "version_mismatches": version_mismatches
        }

    def check_capability_coverage(
        self,
        agents_metadata: Dict[str, AgentMetadata]
    ) -> Dict[str, Any]:
        """
        Check P1.5-005: Agent capability coverage matrix.

        Args:
            agents_metadata: Dict of agent_name → AgentMetadata

        Returns:
            Dict with:
            - coverage_matrix: Dict[mode, List[agent_name]]
            - uncovered_modes: List[str]
            - unassigned_agents: List[str]
        """
        coverage_matrix = {mode: [] for mode in CORTEX_MODES}
        unassigned_agents = []

        for agent_name, metadata in agents_metadata.items():
            if not metadata.modes:
                unassigned_agents.append(agent_name)
            else:
                for mode in metadata.modes:
                    if mode in coverage_matrix:
                        coverage_matrix[mode].append(agent_name)

        uncovered_modes = [mode for mode, agents in coverage_matrix.items() if not agents]

        return {
            "coverage_matrix": coverage_matrix,
            "uncovered_modes": uncovered_modes,
            "unassigned_agents": unassigned_agents
        }

    def check_cross_references(
        self,
        agents_metadata: Dict[str, AgentMetadata]
    ) -> Dict[str, Any]:
        """
        Check P1.5-006: Agent cross-reference integrity.

        Args:
            agents_metadata: Dict of agent_name → AgentMetadata

        Returns:
            Dict with:
            - broken_references: Dict[agent_name, List[broken_ref]]
            - total_references: int
            - valid_references: int
        """
        broken_references = {}
        total_refs = 0
        valid_refs = 0

        for agent_name, metadata in agents_metadata.items():
            broken_refs = []

            for ref in metadata.file_references:
                total_refs += 1

                # Try to resolve reference relative to repo root
                ref_path = self.repo_root / ref
                if not ref_path.exists():
                    # Try relative to agent directory
                    ref_path = self.agent_dir / ref
                    if not ref_path.exists():
                        broken_refs.append(ref)
                    else:
                        valid_refs += 1
                else:
                    valid_refs += 1

            if broken_refs:
                broken_references[agent_name] = broken_refs

        return {
            "broken_references": broken_references,
            "total_references": total_refs,
            "valid_references": valid_refs
        }

    def check_index_sync(
        self,
        agents_metadata: Dict[str, AgentMetadata],
        index_data: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Check P1.5-007: AGENT-INDEX.md synchronization.

        Args:
            agents_metadata: Dict of agent_name → AgentMetadata
            index_data: Dict from AGENT-INDEX.md

        Returns:
            Dict with:
            - missing_from_index: List[str]
            - orphaned_entries: List[str]
            - description_mismatches: Dict[agent, {file_desc, index_desc}]
        """
        agent_names = set(agents_metadata.keys())
        index_names = set(index_data.keys())

        missing_from_index = list(agent_names - index_names)
        orphaned_entries = list(index_names - agent_names)

        # Check description accuracy (simplified - just flag if very different)
        description_mismatches = {}
        for agent_name in agent_names & index_names:
            file_desc = agents_metadata[agent_name].description
            index_desc = index_data[agent_name]["description"]

            # Simple check: if both exist and are very different in length
            if file_desc and index_desc:
                if abs(len(file_desc) - len(index_desc)) > 50:
                    description_mismatches[agent_name] = {
                        "file_desc": file_desc[:100],
                        "index_desc": index_desc[:100]
                    }

        return {
            "missing_from_index": missing_from_index,
            "orphaned_entries": orphaned_entries,
            "description_mismatches": description_mismatches
        }


# AC_COMPLETE: AC-PHASE39-004 GREEN ✅ Agent version tracking implemented
# AC_COMPLETE: AC-PHASE39-005 GREEN ✅ Agent capability coverage implemented
# AC_COMPLETE: AC-PHASE39-006 GREEN ✅ Agent cross-reference validation implemented
# AC_COMPLETE: AC-PHASE39-007 GREEN ✅ AGENT-INDEX.md sync validation implemented
