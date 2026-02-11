"""
Upgrade Diff Analyzer for Phase 40.

Analyzes git diffs after CORTEX upgrade to detect:
- Prompt changes (new modes, commands, sections)
- Agent changes (new/modified agents, capabilities)
- Orchestrator changes (wiring.yaml additions)
- MCP tool additions
- Version changes

Author: Asif Hussain
Created: 2026-02-07
Phase: 40
"""

import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ChangeCategory(Enum):
    """Categories of changes that can be detected."""
    PROMPT = "prompt"
    AGENT = "agent"
    ORCHESTRATOR = "orchestrator"
    MCP_TOOL = "mcp_tool"
    BEST_PRACTICE = "best_practice"
    GOVERNANCE = "governance"


@dataclass
class PromptChange:
    """Represents a change in prompt files."""
    change_type: str  # "new_mode", "new_command", "new_section"
    name: str
    description: str
    impact: str = "medium"  # "critical", "high", "medium", "minor"


@dataclass
class AgentChange:
    """Represents a change in agent files."""
    change_type: str  # "new_agent", "modified_agent", "new_capability"
    name: str
    description: str
    version: Optional[str] = None


@dataclass
class OrchestratorChange:
    """Represents a change in orchestrator wiring."""
    change_type: str  # "new_orchestrator", "new_capability", "modified_config"
    name: str
    description: str
    priority: Optional[int] = None


@dataclass
class MCPToolChange:
    """Represents a new MCP tool."""
    name: str
    description: str
    change_type: str = "new_mcp_tool"
    function_signature: Optional[str] = None


@dataclass
class DiffResult:
    """Complete diff analysis result."""
    prompt_changes: List[PromptChange] = field(default_factory=list)
    agent_changes: List[AgentChange] = field(default_factory=list)
    orchestrator_changes: List[OrchestratorChange] = field(default_factory=list)
    mcp_tool_changes: List[MCPToolChange] = field(default_factory=list)
    old_version: Optional[str] = None
    new_version: Optional[str] = None

    @property
    def total_changes(self) -> int:
        """Total number of changes detected."""
        return (
            len(self.prompt_changes) +
            len(self.agent_changes) +
            len(self.orchestrator_changes) +
            len(self.mcp_tool_changes)
        )

    @property
    def has_user_facing_changes(self) -> bool:
        """Check if there are any user-facing changes."""
        return self.total_changes > 0


class UpgradeDiffAnalyzer:
    """
    Analyzes git diffs to detect CORTEX upgrade changes.

    Usage:
        analyzer = UpgradeDiffAnalyzer(repo_path="/path/to/cortex")
        result = analyzer.analyze_upgrade()

        print(f"Found {result.total_changes} changes")
        for change in result.prompt_changes:
            print(f"  - {change.name}: {change.description}")
    """

    # Patterns for detection
    MODE_PATTERN = re.compile(r'^\+###\s+(\w+)\s+Mode\s*(?:\(NEW\))?', re.MULTILINE | re.IGNORECASE)
    COMMAND_PATTERN = re.compile(r'^\+\|\s*`(/\w+[^`]*)`\s*\|\s*([^|]+)\s*\|', re.MULTILINE)
    SECTION_PATTERN = re.compile(r'^\+##\s+([^#\n]+?)(?:\s*\(NEW\))?$', re.MULTILINE)
    VERSION_PATTERN = re.compile(r'\*\*Version:\*\*\s+([\d.]+)')
    AGENT_FILE_PATTERN = re.compile(r'b/\.github/agents/core/([^/\s]+\.md)', re.MULTILINE)
    ORCHESTRATOR_PATTERN = re.compile(r'^\+\s+-\s+name:\s+"([^"]+)"', re.MULTILINE)
    MCP_TOOL_PATTERN = re.compile(r'^\+@mcp_tool\(name="([^"]+)"\)', re.MULTILINE)
    DOCSTRING_PATTERN = re.compile(r"(?:'''([^']+)'''|\"\"\"([^\"]+)\"\"\")", re.MULTILINE)
    CAPABILITY_PATTERN = re.compile(r'^\+\s+-\s+([a-z_]+(?:_[a-z]+)*)\s*$', re.MULTILINE)

    def __init__(self, repo_path: str = "."):
        """
        Initialize the analyzer.

        Args:
            repo_path: Path to the CORTEX repository
        """
        self.repo_path = Path(repo_path)

    def get_git_diff(self, base: str = "HEAD~1", target: str = "HEAD") -> str:
        """
        Get git diff between two commits.

        Args:
            base: Base commit (default: HEAD~1)
            target: Target commit (default: HEAD)

        Returns:
            Git diff output as string
        """
        try:
            result = subprocess.run(
                ["git", "diff", base, target],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting git diff: {e}")
            return ""

    def analyze_prompt_diff(self, diff: str) -> List[PromptChange]:
        """
        Analyze prompt file changes.

        Args:
            diff: Git diff output

        Returns:
            List of detected prompt changes
        """
        changes = []

        # Detect new modes
        for match in self.MODE_PATTERN.finditer(diff):
            mode_name = match.group(1)
            # Extract description from lines after the mode header
            lines_after = diff[match.end():match.end() + 200].split('\n')
            description = next((line.strip('+').strip() for line in lines_after if line.startswith('+')), "")

            changes.append(PromptChange(
                change_type="new_mode",
                name=f"{mode_name} Mode",
                description=description[:100] if description else f"New {mode_name} mode added",
                impact="high"
            ))

        # Detect new commands
        for match in self.COMMAND_PATTERN.finditer(diff):
            command = match.group(1).strip()
            action = match.group(2).strip()

            changes.append(PromptChange(
                change_type="new_command",
                name=command,
                description=action,
                impact="medium"
            ))

        # Detect new sections (filter out minor ones)
        for match in self.SECTION_PATTERN.finditer(diff):
            section_name = match.group(1).strip()
            # Filter out minor sections
            if len(section_name) > 10 and any(keyword in section_name.upper() for keyword in
                                              ["PROTOCOL", "MODE", "ENFORCEMENT", "SYSTEM"]):
                changes.append(PromptChange(
                    change_type="new_section",
                    name=section_name,
                    description=f"New section: {section_name}",
                    impact="medium"
                ))

        return changes

    def analyze_agent_diff(self, diff: str) -> List[AgentChange]:
        """
        Analyze agent file changes.

        Args:
            diff: Git diff output

        Returns:
            List of detected agent changes
        """
        changes = []

        # Detect new agent files - match both +++ and regular file additions
        for match in self.AGENT_FILE_PATTERN.finditer(diff):
            agent_file = match.group(1)
            agent_name = agent_file.replace('.md', '').replace('-', ' ').title()

            # Extract version if present
            version_match = self.VERSION_PATTERN.search(diff[match.end():match.end() + 300])
            version = version_match.group(1) if version_match else None

            changes.append(AgentChange(
                change_type="new_agent",
                name=agent_name,
                description=f"New agent: {agent_name}",
                version=version
            ))

        # Also check for explicit "new file mode" pattern
        if 'new file mode' in diff and 'agents/core/' in diff:
            # Extract filename from the diff
            file_match = re.search(r'agents/core/([^/\s]+\.md)', diff)
            if file_match:
                agent_file = file_match.group(1)
                agent_name = agent_file.replace('.md', '').replace('-', ' ').title()

                # Avoid duplicates
                if not any(c.name == agent_name for c in changes):
                    version_match = self.VERSION_PATTERN.search(diff)
                    version = version_match.group(1) if version_match else None

                    changes.append(AgentChange(
                        change_type="new_agent",
                        name=agent_name,
                        description=f"New agent: {agent_name}",
                        version=version
                    ))

        # Detect new capabilities (in agent context)
        if "agents/core" in diff:
            capability_section = False
            for line in diff.split('\n'):
                if '## Capabilities' in line or '### Capabilities' in line:
                    capability_section = True
                    continue
                if capability_section and line.startswith('+') and '-' in line:
                    capability = line.strip('+ -').strip()
                    if len(capability) > 5:  # Filter out noise
                        changes.append(AgentChange(
                            change_type="new_capability",
                            name=capability[:50],
                            description=capability
                        ))
                elif capability_section and (line.startswith('##') or line.startswith('###')):
                    capability_section = False

        return changes

    def analyze_wiring_diff(self, diff: str) -> List[OrchestratorChange]:
        """
        Analyze wiring.yaml changes.

        Args:
            diff: Git diff output

        Returns:
            List of detected orchestrator changes
        """
        changes = []

        # Detect new orchestrators
        for match in self.ORCHESTRATOR_PATTERN.finditer(diff):
            orchestrator_name = match.group(1)

            # Extract description from nearby lines
            context = diff[max(0, match.start() - 200):match.end() + 300]
            desc_match = re.search(r'\+\s+description:\s+"([^"]+)"', context)
            description = desc_match.group(1) if desc_match else f"New orchestrator: {orchestrator_name}"

            # Extract priority
            priority_match = re.search(r'\+\s+priority:\s+(\d+)', context)
            priority = int(priority_match.group(1)) if priority_match else None

            changes.append(OrchestratorChange(
                change_type="new_orchestrator",
                name=orchestrator_name,
                description=description,
                priority=priority
            ))

        # Detect new capabilities
        if "capabilities:" in diff:
            capability_section = False
            for line in diff.split('\n'):
                if '+      capabilities:' in line:
                    capability_section = True
                    continue
                if capability_section and line.startswith('+') and '-' in line:
                    capability = line.strip('+ -').strip()
                    if '_' in capability or capability.islower():  # Looks like a capability
                        changes.append(OrchestratorChange(
                            change_type="new_capability",
                            name=capability,
                            description=f"New capability: {capability.replace('_', ' ').title()}"
                        ))
                elif capability_section and not line.strip().startswith('+'):
                    capability_section = False

        return changes

    def analyze_mcp_tool_diff(self, diff: str) -> List[MCPToolChange]:
        """
        Analyze MCP tool additions.

        Args:
            diff: Git diff output

        Returns:
            List of detected MCP tool changes
        """
        changes = []

        # Detect new @mcp_tool decorators
        for match in self.MCP_TOOL_PATTERN.finditer(diff):
            tool_name = match.group(1)

            # Extract function signature and docstring
            context = diff[match.end():match.end() + 500]
            func_match = re.search(r'\+def\s+\w+\([^)]*\)[^:]*:', context)
            signature = func_match.group(0).strip('+').strip() if func_match else None

            # Extract docstring - try both single and triple quotes
            description = f"New MCP tool: {tool_name}"
            doc_match = self.DOCSTRING_PATTERN.search(context)
            if doc_match:
                # Get whichever group matched (triple single or triple double quotes)
                description = doc_match.group(1) or doc_match.group(2)
                description = description.strip()

            changes.append(MCPToolChange(
                name=tool_name,
                description=description,
                function_signature=signature
            ))

        return changes

    def extract_version_change(self, diff: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract version number changes from diff.

        Args:
            diff: Git diff output

        Returns:
            Tuple of (old_version, new_version)
        """
        old_version = None
        new_version = None

        # Look for version changes in format: -**Version:** X.Y -> +**Version:** X.Z
        for line in diff.split('\n'):
            if line.startswith('-') and '**Version:**' in line:
                match = self.VERSION_PATTERN.search(line)
                if match:
                    old_version = match.group(1)
            elif line.startswith('+') and '**Version:**' in line:
                match = self.VERSION_PATTERN.search(line)
                if match:
                    new_version = match.group(1)

        return old_version, new_version

    def extract_agent_version(self, diff: str) -> Optional[str]:
        """Extract agent version from diff."""
        match = self.VERSION_PATTERN.search(diff)
        return match.group(1) if match else None

    def extract_orchestrator_version(self, diff: str) -> Optional[str]:
        """Extract orchestrator version from diff."""
        match = re.search(r'\+\s+version:\s+"([^"]+)"', diff)
        return match.group(1) if match else None

    def analyze_upgrade(self, base: str = "HEAD~1", target: str = "HEAD") -> DiffResult:
        """
        Analyze complete upgrade diff.

        Args:
            base: Base commit (default: HEAD~1)
            target: Target commit (default: HEAD)

        Returns:
            DiffResult with all detected changes
        """
        diff = self.get_git_diff(base, target)

        # Extract version change
        old_version, new_version = self.extract_version_change(diff)

        # Analyze all categories
        result = DiffResult(
            prompt_changes=self.analyze_prompt_diff(diff),
            agent_changes=self.analyze_agent_diff(diff),
            orchestrator_changes=self.analyze_wiring_diff(diff),
            mcp_tool_changes=self.analyze_mcp_tool_diff(diff),
            old_version=old_version,
            new_version=new_version
        )

        return result

    def analyze_prompt_upgrade(self, old_content: str, new_content: str) -> DiffResult:
        """
        Analyze prompt upgrade without git diff.

        Args:
            old_content: Old prompt content
            new_content: New prompt content

        Returns:
            DiffResult with detected changes
        """
        # Create a pseudo-diff
        diff_lines = []
        for line in old_content.split('\n'):
            diff_lines.append(f'-{line}')
        for line in new_content.split('\n'):
            diff_lines.append(f'+{line}')

        diff = '\n'.join(diff_lines)

        # Extract version change
        old_version, new_version = self.extract_version_change(diff)

        result = DiffResult(
            prompt_changes=self.analyze_prompt_diff(diff),
            old_version=old_version,
            new_version=new_version
        )

        return result
