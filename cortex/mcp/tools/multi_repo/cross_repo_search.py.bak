"""Cross-Repo Search MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Find AC-ID references across repositories.

Author: CORTEX Framework
"""

from typing import Dict, Any, List
from pathlib import Path
import re


class CrossRepoSearch:
    """MCP tool for searching across repositories.
    
    Searches for AC-ID references across multiple projects.
    """
    
    AC_ID_PATTERN = re.compile(r"AC-[A-Z]+-\d+(?:-\d+)?")
    
    def __init__(self, base_path: str = "D:\\PROJECTS"):
        """Initialize cross-repo search.
        
        Args:
            base_path: Base path containing repositories.
        """
        self.base_path = base_path
    
    def search_ac_id(
        self,
        ac_id: str,
        repos: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for AC-ID across repositories.
        
        Args:
            ac_id: AC-ID to search for (supports * wildcard).
            repos: List of repository names to search.
            
        Returns:
            List of matches with file and line info.
        """
        results = []
        
        if repos is None:
            repos = self._list_repos()
        
        for repo in repos:
            matches = self._search_repo(repo, ac_id)
            results.extend(matches)
        
        return results
    
    def _list_repos(self) -> List[str]:
        """List available repositories.
        
        Returns:
            List of repository names.
        """
        try:
            path = Path(self.base_path)
            return [p.name for p in path.iterdir() if p.is_dir()]
        except Exception:
            return []
    
    def _search_repo(self, repo: str, ac_id: str) -> List[Dict[str, Any]]:
        """Search single repository.
        
        Args:
            repo: Repository name.
            ac_id: AC-ID pattern to search.
            
        Returns:
            List of matches in this repo.
        """
        results = []
        repo_path = Path(self.base_path) / repo
        
        if not repo_path.exists():
            return results
        
        # Convert wildcard to regex
        if "*" in ac_id:
            pattern = re.compile(ac_id.replace("*", ".*"))
        else:
            pattern = re.compile(re.escape(ac_id))
        
        # Search Python files
        try:
            for py_file in repo_path.rglob("*.py"):
                try:
                    content = py_file.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if pattern.search(line):
                            # Extract the actual AC-ID
                            match = self.AC_ID_PATTERN.search(line)
                            if match:
                                results.append({
                                    "file": str(py_file),
                                    "line": i,
                                    "match": match.group(),
                                    "context": line.strip()[:100],
                                })
                except Exception:
                    continue
        except Exception:
            pass
        
        return results
    
    def search_pattern(
        self,
        pattern: str,
        repos: List[str] = None,
        file_pattern: str = "*.py",
    ) -> List[Dict[str, Any]]:
        """Search for arbitrary pattern across repos.
        
        Args:
            pattern: Regex pattern to search.
            repos: Repositories to search.
            file_pattern: File glob pattern.
            
        Returns:
            List of matches.
        """
        results = []
        regex = re.compile(pattern)
        
        if repos is None:
            repos = self._list_repos()
        
        for repo in repos:
            repo_path = Path(self.base_path) / repo
            if not repo_path.exists():
                continue
            
            for file_path in repo_path.rglob(file_pattern):
                try:
                    content = file_path.read_text(errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        if regex.search(line):
                            results.append({
                                "file": str(file_path),
                                "line": i,
                                "repo": repo,
                                "context": line.strip()[:100],
                            })
                except Exception:
                    continue
        
        return results


__all__ = ["CrossRepoSearch"]
