"""
Dashboard Output Manager - Smart Location Routing.

Determines dashboard output location based on repository type and context:
- External repository (local): repo_root/.cortex/lens-dashboard/
- CORTEX repository (local): repo_root/reports/lens-dashboard/
- Remote repository: ~/.cortex/cache/{repo_hash}/lens-dashboard/

Automatically handles:
- .gitignore creation (external repos only)
- Directory creation
- index.html generation

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cortex.visualization.repository_detector import is_cortex_repository


@dataclass
class OutputConfiguration:
    """
    Configuration for dashboard output location.

    Attributes:
        repo_path: Path to repository root
        is_cortex: Whether repository is CORTEX
        is_remote: Whether repository is remote (not local)
        output_path: Determined output path for dashboard
        gitignore_entry: Entry to add to .gitignore (None if not needed)
    """
    repo_path: Path
    is_cortex: bool
    is_remote: bool
    output_path: Path
    gitignore_entry: Optional[str]


class DashboardOutputManager:
    """
    Manages dashboard output location routing.

    Determines output path based on repository type and execution context:

    **Local External Repository:**
    - Output: `{repo_root}/.cortex/lens-dashboard/`
    - Gitignore: `.cortex/` (auto-created)

    **Local CORTEX Repository:**
    - Output: `{repo_root}/reports/lens-dashboard/`
    - Gitignore: None (reports/ is tracked)

    **Remote Repository:**
    - Output: `~/.cortex/cache/{repo_hash}/lens-dashboard/`
    - Gitignore: None (outside repo)

    Example:
        ```python
        manager = DashboardOutputManager()

        # Get configuration for repository
        config = manager.get_output_configuration(Path("/path/to/repo"))

        # Ensure output directory exists
        manager.ensure_output_directory(config.output_path)

        # Create .gitignore if needed
        manager.create_gitignore_entry(config.repo_path, config.gitignore_entry)

        # Generate index.html
        manager.generate_index_html(config.output_path, "my-repo")
        ```
    """

    def get_output_configuration(
        self,
        repo_path: Path,
        is_remote: bool = False,
        output_override: Optional[Path] = None,
    ) -> OutputConfiguration:
        """
        Get output configuration for repository.

        Args:
            repo_path: Path to repository root
            is_remote: Whether repository is remote (not local clone)
            output_override: Optional explicit output path override

        Returns:
            OutputConfiguration with determined paths and settings
        """
        is_cortex = is_cortex_repository(repo_path)

        # Determine output path
        if output_override:
            output_path = output_override
        elif is_remote:
            # Remote: ~/.cortex/cache/{repo_hash}/lens-dashboard/
            repo_hash = self._get_repo_hash(repo_path)
            output_path = Path.home() / ".cortex/cache" / repo_hash / "lens-dashboard"
        elif is_cortex:
            # CORTEX local: reports/lens-dashboard/
            output_path = repo_path / "reports/lens-dashboard"
        else:
            # External local: .cortex/lens-dashboard/
            output_path = repo_path / ".cortex/lens-dashboard"

        # Determine gitignore entry
        if is_remote or is_cortex:
            gitignore_entry = None  # No gitignore needed
        else:
            gitignore_entry = ".cortex/"  # External repos need gitignore

        return OutputConfiguration(
            repo_path=repo_path,
            is_cortex=is_cortex,
            is_remote=is_remote,
            output_path=output_path,
            gitignore_entry=gitignore_entry,
        )

    def ensure_output_directory(self, output_path: Path) -> None:
        """
        Ensure output directory exists (create if missing).

        Args:
            output_path: Path to dashboard output directory
        """
        output_path.mkdir(parents=True, exist_ok=True)

    def create_gitignore_entry(self, repo_path: Path, gitignore_entry: Optional[str]) -> None:
        """
        Create or update .gitignore with dashboard entry.

        Idempotent - safe to call multiple times (won't duplicate entries).

        Args:
            repo_path: Path to repository root
            gitignore_entry: Entry to add (e.g., ".cortex/"), or None to skip
        """
        if gitignore_entry is None:
            return  # No gitignore needed

        gitignore_path = repo_path / ".gitignore"

        # Read existing content
        if gitignore_path.exists():
            content = gitignore_path.read_text()

            # Check if entry already exists
            if gitignore_entry in content:
                return  # Already present, skip
        else:
            content = ""

        # Append new entry with comment
        if content and not content.endswith("\n"):
            content += "\n"

        content += f"\n# CORTEX LENS Dashboard (auto-generated)\n{gitignore_entry}\n"

        gitignore_path.write_text(content)

    def generate_index_html(self, output_path: Path, repo_name: str) -> None:
        """
        Generate index.html for dashboard.

        Args:
            output_path: Path to dashboard output directory
            repo_name: Name of repository (for page title)
        """
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX LENS Dashboard - {repo_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .repo-name {{
            color: #764ba2;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        .message {{
            background: #f0f4ff;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 CORTEX LENS Dashboard</h1>
        <div class="repo-name">{repo_name}</div>
        <div class="message">
            <p>Dashboard is being generated. Refresh this page in a moment to see visualizations.</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Repository Overview (Business Language)</li>
                <li>Dependency Graphs (Call Graph + Import Graph)</li>
                <li>Class Diagrams (UML, ERD, Interfaces)</li>
                <li>Temporal Analysis (Git Timeline + Change Heatmap)</li>
                <li>Impact Analysis (Change Propagation)</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

        index_path = output_path / "index.html"
        index_path.write_text(html_content, encoding="utf-8")

    def _get_repo_hash(self, repo_path: Path) -> str:
        """
        Get stable hash for repository path (for cache directory naming).

        Args:
            repo_path: Path to repository

        Returns:
            8-character hex hash of absolute path
        """
        abs_path = str(repo_path.resolve())
        hash_obj = hashlib.sha256(abs_path.encode())
        return hash_obj.hexdigest()[:8]


def get_output_path(repo_path: Path, is_remote: bool = False) -> Path:
    """
    Convenience function to get dashboard output path.

    Args:
        repo_path: Path to repository root
        is_remote: Whether repository is remote

    Returns:
        Path to dashboard output directory
    """
    manager = DashboardOutputManager()
    config = manager.get_output_configuration(repo_path, is_remote=is_remote)
    return config.output_path
