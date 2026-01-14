"""
CORTEX Git History Intelligence Tool

Mines existing CORTEX branches for production-ready code, designs, and patterns.
Avoids reinventing the wheel by searching git history before creating new implementations.

Key Capabilities:
- Search across all CORTEX-* branches for existing implementations
- Extract patterns, designs, and approved configurations
- Output machine-readable formats (JSON, YAML) to organized folder structure
- Build searchable index for efficient future queries
- Integrate findings with CX6-requirements schema

Practical Scenarios:
- "Do we have an existing auth implementation?" → Search branches for auth-related code
- "What was the original SKULL rule design?" → Extract from CORTEX-4.0 branch
- "Did we solve file locking before?" → Find previous implementations
- "What patterns were approved for ADO integration?" → Recover from git history

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import subprocess
import json
import yaml
import hashlib
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class SearchCategory(str, Enum):
    """Categories for organizing search results."""
    GOVERNANCE = "governance"          # Rules, policies, constraints
    ORCHESTRATOR = "orchestrators"     # Orchestrator implementations
    INFRASTRUCTURE = "infrastructure"  # Core infrastructure code
    PATTERNS = "patterns"              # Design patterns, approved approaches
    CONFIGURATIONS = "configurations"  # YAML/JSON configs
    TESTS = "tests"                    # Test implementations
    PROMPTS = "prompts"                # Prompt files
    SCHEMAS = "schemas"                # Schema definitions
    TOOLS = "tools"                    # Utility tools and scripts


@dataclass
class GitSearchResult:
    """Individual search result from git history."""
    branch: str
    file_path: str
    content_hash: str
    line_count: int
    category: SearchCategory
    relevance_score: float
    matched_terms: List[str]
    extracted_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        return result


@dataclass
class ExtractedAsset:
    """Asset extracted from git history."""
    source_branch: str
    source_path: str
    target_path: str
    content: str
    content_type: str  # 'python', 'yaml', 'json', 'markdown'
    extraction_reason: str
    related_ac_ids: List[str] = field(default_factory=list)
    transformation_notes: List[str] = field(default_factory=list)


@dataclass
class BranchIndex:
    """Index of searchable content in a branch."""
    branch_name: str
    indexed_at: str
    file_count: int
    categories: Dict[str, int]
    key_files: Dict[str, str]  # path -> content_hash
    keywords: Dict[str, List[str]]  # keyword -> [file_paths]


class GitHistoryIntelligence:
    """
    Intelligent git history mining for CORTEX knowledge recovery.
    
    Searches across CORTEX branches to find existing implementations,
    patterns, and designs before creating new code.
    """
    
    # Branches to search (in priority order)
    TARGET_BRANCHES = [
        "CORTEX-5.5",
        "CORTEX-5.0", 
        "CORTEX-4.0",
        "CORTEX-3.0",
        "CORTEX-2.0",
        "CORTEX-1.0",
    ]
    
    # File patterns for each category
    CATEGORY_PATTERNS = {
        SearchCategory.GOVERNANCE: [
            "**/governance/**", "**/rules/**", "**/*-rules.yaml",
            "**/brain-protection*.yaml", "**/skull/**", "**/tier0/**"
        ],
        SearchCategory.ORCHESTRATOR: [
            "**/orchestrators/**", "**/*_orchestrator.py", 
            "**/orchestration/**", "**/master_orchestrator.py"
        ],
        SearchCategory.INFRASTRUCTURE: [
            "**/infrastructure/**", "**/core/**", "**/base/**",
            "**/audit*.py", "**/state*.py", "**/cache/**"
        ],
        SearchCategory.PATTERNS: [
            "**/patterns/**", "**/design/**", "**/*-pattern*.md",
            "**/architecture/**"
        ],
        SearchCategory.CONFIGURATIONS: [
            "**/config/**", "**/*.yaml", "**/*.json",
            "**/manifests/**", "**/settings/**"
        ],
        SearchCategory.TESTS: [
            "**/tests/**", "**/test_*.py", "**/*_test.py"
        ],
        SearchCategory.PROMPTS: [
            "**/*.prompt.md", "**/prompts/**"
        ],
        SearchCategory.SCHEMAS: [
            "**/*schema*.yaml", "**/*schema*.json", "**/schemas/**",
            "**/*-spec.yaml"
        ],
        SearchCategory.TOOLS: [
            "**/tools/**", "**/scripts/**", "**/crawlers/**",
            "**/cli/**", "**/utils/**"
        ],
    }
    
    # Keywords for intelligent search
    SEARCH_KEYWORDS = {
        "auth": ["authentication", "auth", "login", "oauth", "jwt", "session", "token"],
        "governance": ["skull", "rule", "governance", "protection", "enforcement", "tier0"],
        "file_locking": ["lock", "flock", "fcntl", "msvcrt", "mutex", "concurrent"],
        "ado": ["azure", "devops", "ado", "work_item", "backlog", "sprint"],
        "tdd": ["test", "tdd", "red", "green", "refactor", "pytest", "unittest"],
        "state": ["state", "session", "persistence", "checkpoint", "continuation"],
        "audit": ["audit", "log", "trace", "track", "record", "history"],
        "planning": ["plan", "phase", "epic", "todo", "backlog", "roadmap"],
        "vacuum": ["vacuum", "cleanup", "clean", "purge", "archive", "delete"],
        "crawlers": ["crawler", "scanner", "analyzer", "parser", "walker"],
    }
    
    def __init__(
        self,
        repo_path: Optional[Path] = None,
        output_root: Optional[Path] = None,
        index_path: Optional[Path] = None
    ):
        """
        Initialize Git History Intelligence.
        
        Args:
            repo_path: Path to git repository
            output_root: Root folder for extracted assets
            index_path: Path to store/load index
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.output_root = output_root or self.repo_path / "cortex-brain" / "git-history-assets"
        self.index_path = index_path or self.output_root / "index"
        
        # Ensure clean folder structure
        self._setup_output_structure()
        
        # Load or create index
        self.branch_indexes: Dict[str, BranchIndex] = {}
        self._load_indexes()
    
    def _setup_output_structure(self):
        """Create organized output folder structure."""
        folders = [
            self.output_root,
            self.index_path,
            self.output_root / "extracted",
            self.output_root / "extracted" / "governance",
            self.output_root / "extracted" / "orchestrators",
            self.output_root / "extracted" / "infrastructure",
            self.output_root / "extracted" / "patterns",
            self.output_root / "extracted" / "configurations",
            self.output_root / "extracted" / "tools",
            self.output_root / "extracted" / "schemas",
            self.output_root / "search-results",
            self.output_root / "transformations",
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
    
    def _run_git_command(self, args: List[str]) -> Tuple[bool, str]:
        """Run git command and return (success, output)."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            logger.warning(f"Git command timed out: {args}")
            return False, ""
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return False, ""
    
    def _get_available_branches(self) -> List[str]:
        """Get list of available CORTEX branches."""
        success, output = self._run_git_command(["branch", "-a"])
        if not success:
            return []
        
        branches = []
        for line in output.splitlines():
            branch = line.strip().lstrip("* ").replace("remotes/origin/", "").replace("remotes/cortex-upstream/", "")
            if branch.startswith("CORTEX") and branch not in branches:
                branches.append(branch)
        
        # Sort by version (higher first)
        def version_key(b):
            match = re.search(r'(\d+)\.?(\d*)', b)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2)) if match.group(2) else 0
                return (major, minor)
            return (0, 0)
        
        return sorted(branches, key=version_key, reverse=True)
    
    def _get_file_content(self, branch: str, file_path: str) -> Optional[str]:
        """Get file content from specific branch."""
        success, content = self._run_git_command(["show", f"{branch}:{file_path}"])
        return content if success else None
    
    def _list_files_in_branch(self, branch: str, pattern: Optional[str] = None) -> List[str]:
        """List all files in a branch, optionally filtered by pattern."""
        args = ["ls-tree", "-r", "--name-only", branch]
        success, output = self._run_git_command(args)
        if not success:
            return []
        
        files = output.strip().splitlines()
        
        if pattern:
            import fnmatch
            pattern = pattern.replace("**", "*")  # Simplify glob
            files = [f for f in files if fnmatch.fnmatch(f, pattern)]
        
        return files
    
    def _categorize_file(self, file_path: str) -> SearchCategory:
        """Determine category for a file path."""
        file_lower = file_path.lower()
        
        if any(p in file_lower for p in ["governance", "rules", "skull", "tier0", "protection"]):
            return SearchCategory.GOVERNANCE
        if any(p in file_lower for p in ["orchestrator", "orchestration"]):
            return SearchCategory.ORCHESTRATOR
        if any(p in file_lower for p in ["infrastructure", "audit", "state", "cache"]):
            return SearchCategory.INFRASTRUCTURE
        if any(p in file_lower for p in ["pattern", "design", "architecture"]):
            return SearchCategory.PATTERNS
        if file_path.endswith(".prompt.md") or "prompts/" in file_lower:
            return SearchCategory.PROMPTS
        if any(p in file_lower for p in ["schema", "spec.yaml", "spec.json"]):
            return SearchCategory.SCHEMAS
        if any(p in file_lower for p in ["test", "tests/"]):
            return SearchCategory.TESTS
        if any(p in file_lower for p in ["tools/", "scripts/", "crawlers/", "cli/", "utils/"]):
            return SearchCategory.TOOLS
        if file_path.endswith((".yaml", ".json")):
            return SearchCategory.CONFIGURATIONS
        
        return SearchCategory.PATTERNS  # Default
    
    def _compute_relevance(self, content: str, search_terms: List[str]) -> Tuple[float, List[str]]:
        """Compute relevance score and matched terms."""
        content_lower = content.lower()
        matched = []
        score = 0.0
        
        for term in search_terms:
            term_lower = term.lower()
            count = content_lower.count(term_lower)
            if count > 0:
                matched.append(term)
                # Diminishing returns for repeated matches
                score += min(count * 0.1, 1.0)
        
        # Bonus for exact phrase matches
        for term in search_terms:
            if len(term) > 5 and term.lower() in content_lower:
                score += 0.5
        
        return min(score, 10.0), matched
    
    # =========================================================================
    # Index Management
    # =========================================================================
    
    def build_index(self, branches: Optional[List[str]] = None, force: bool = False) -> Dict[str, BranchIndex]:
        """
        Build searchable index for specified branches.
        
        Args:
            branches: Branches to index (default: all CORTEX branches)
            force: Rebuild even if index exists
            
        Returns:
            Dictionary of branch indexes
        """
        branches = branches or self._get_available_branches()
        logger.info(f"Building index for {len(branches)} branches")
        
        for branch in branches:
            if branch in self.branch_indexes and not force:
                logger.info(f"Skipping {branch} (already indexed)")
                continue
            
            logger.info(f"Indexing branch: {branch}")
            index = self._index_branch(branch)
            if index:
                self.branch_indexes[branch] = index
                self._save_index(branch, index)
        
        return self.branch_indexes
    
    def _index_branch(self, branch: str) -> Optional[BranchIndex]:
        """Index a single branch."""
        files = self._list_files_in_branch(branch)
        if not files:
            return None
        
        categories: Dict[str, int] = {}
        key_files: Dict[str, str] = {}
        keywords: Dict[str, List[str]] = {k: [] for k in self.SEARCH_KEYWORDS}
        
        # Index important files
        important_patterns = [
            "*.py", "*.yaml", "*.json", "*.prompt.md", "*.md"
        ]
        
        for file_path in files:
            # Skip unimportant files
            if not any(file_path.endswith(p.replace("*", "")) for p in important_patterns):
                continue
            
            # Categorize
            category = self._categorize_file(file_path)
            categories[category.value] = categories.get(category.value, 0) + 1
            
            # Get content for important files
            content = self._get_file_content(branch, file_path)
            if content:
                # Compute hash
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                key_files[file_path] = content_hash
                
                # Extract keywords
                content_lower = content.lower()
                for keyword, terms in self.SEARCH_KEYWORDS.items():
                    if any(t in content_lower for t in terms):
                        keywords[keyword].append(file_path)
        
        return BranchIndex(
            branch_name=branch,
            indexed_at=datetime.now().isoformat(),
            file_count=len(files),
            categories=categories,
            key_files=key_files,
            keywords=keywords
        )
    
    def _save_index(self, branch: str, index: BranchIndex):
        """Save branch index to disk."""
        safe_name = branch.replace("/", "_").replace(".", "_")
        index_file = self.index_path / f"{safe_name}.json"
        
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(asdict(index), f, indent=2)
    
    def _load_indexes(self):
        """Load existing indexes from disk."""
        if not self.index_path.exists():
            return
        
        for index_file in self.index_path.glob("*.json"):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    index = BranchIndex(**data)
                    self.branch_indexes[index.branch_name] = index
            except Exception as e:
                logger.warning(f"Failed to load index {index_file}: {e}")
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    def search(
        self,
        query: str,
        categories: Optional[List[SearchCategory]] = None,
        branches: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[GitSearchResult]:
        """
        Search git history for matching content.
        
        Args:
            query: Search query (natural language or keywords)
            categories: Limit to specific categories
            branches: Limit to specific branches
            max_results: Maximum results to return
            
        Returns:
            List of search results sorted by relevance
        """
        # Expand query to search terms
        search_terms = self._expand_query(query)
        logger.info(f"Searching for: {search_terms}")
        
        branches = branches or list(self.branch_indexes.keys()) or self._get_available_branches()
        results: List[GitSearchResult] = []
        
        for branch in branches:
            # Use index if available
            if branch in self.branch_indexes:
                branch_results = self._search_indexed(branch, search_terms, categories)
            else:
                branch_results = self._search_unindexed(branch, search_terms, categories)
            
            results.extend(branch_results)
        
        # Sort by relevance and limit
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:max_results]
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query to include related terms."""
        terms = query.lower().split()
        expanded = set(terms)
        
        for term in terms:
            # Add keyword expansions
            for keyword, related in self.SEARCH_KEYWORDS.items():
                if term in related or term == keyword:
                    expanded.update(related)
        
        return list(expanded)
    
    def _search_indexed(
        self,
        branch: str,
        search_terms: List[str],
        categories: Optional[List[SearchCategory]]
    ) -> List[GitSearchResult]:
        """Search using pre-built index."""
        index = self.branch_indexes[branch]
        results = []
        
        # Find files matching keywords
        candidate_files: Set[str] = set()
        for term in search_terms:
            for keyword, files in index.keywords.items():
                if term in self.SEARCH_KEYWORDS.get(keyword, []):
                    candidate_files.update(files)
        
        # Also search by term in file path
        for file_path in index.key_files:
            if any(term in file_path.lower() for term in search_terms):
                candidate_files.add(file_path)
        
        # Filter by category
        if categories:
            category_values = [c.value for c in categories]
            candidate_files = {
                f for f in candidate_files 
                if self._categorize_file(f).value in category_values
            }
        
        # Score candidates
        for file_path in candidate_files:
            content = self._get_file_content(branch, file_path)
            if content:
                relevance, matched = self._compute_relevance(content, search_terms)
                if relevance > 0:
                    results.append(GitSearchResult(
                        branch=branch,
                        file_path=file_path,
                        content_hash=index.key_files.get(file_path, ""),
                        line_count=len(content.splitlines()),
                        category=self._categorize_file(file_path),
                        relevance_score=relevance,
                        matched_terms=matched,
                        extracted_at=datetime.now().isoformat()
                    ))
        
        return results
    
    def _search_unindexed(
        self,
        branch: str,
        search_terms: List[str],
        categories: Optional[List[SearchCategory]]
    ) -> List[GitSearchResult]:
        """Search without index (slower)."""
        results = []
        files = self._list_files_in_branch(branch)
        
        for file_path in files:
            # Filter by category
            category = self._categorize_file(file_path)
            if categories and category not in categories:
                continue
            
            # Only search text files
            if not any(file_path.endswith(ext) for ext in [".py", ".yaml", ".json", ".md"]):
                continue
            
            content = self._get_file_content(branch, file_path)
            if content:
                relevance, matched = self._compute_relevance(content, search_terms)
                if relevance > 0.5:  # Higher threshold for unindexed
                    results.append(GitSearchResult(
                        branch=branch,
                        file_path=file_path,
                        content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
                        line_count=len(content.splitlines()),
                        category=category,
                        relevance_score=relevance,
                        matched_terms=matched,
                        extracted_at=datetime.now().isoformat()
                    ))
        
        return results
    
    # =========================================================================
    # Extraction Operations
    # =========================================================================
    
    def extract_asset(
        self,
        branch: str,
        file_path: str,
        target_name: Optional[str] = None,
        transform: bool = True
    ) -> Optional[ExtractedAsset]:
        """
        Extract an asset from git history.
        
        Args:
            branch: Source branch
            file_path: Path to file in branch
            target_name: Optional new name for extracted file
            transform: Whether to apply transformations
            
        Returns:
            ExtractedAsset if successful
        """
        content = self._get_file_content(branch, file_path)
        if not content:
            logger.error(f"Failed to get content from {branch}:{file_path}")
            return None
        
        # Determine content type
        if file_path.endswith(".py"):
            content_type = "python"
        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            content_type = "yaml"
        elif file_path.endswith(".json"):
            content_type = "json"
        else:
            content_type = "markdown"
        
        # Determine target path
        category = self._categorize_file(file_path)
        target_folder = self.output_root / "extracted" / category.value
        target_filename = target_name or Path(file_path).name
        target_path = target_folder / target_filename
        
        # Apply transformations if requested
        transformation_notes = []
        if transform:
            content, notes = self._transform_content(content, content_type, branch)
            transformation_notes.extend(notes)
        
        # Save extracted content
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        asset = ExtractedAsset(
            source_branch=branch,
            source_path=file_path,
            target_path=str(target_path),
            content=content,
            content_type=content_type,
            extraction_reason=f"Extracted from {branch} for CORTEX 6.0",
            transformation_notes=transformation_notes
        )
        
        # Log extraction
        self._log_extraction(asset)
        
        return asset
    
    def _transform_content(
        self,
        content: str,
        content_type: str,
        source_branch: str
    ) -> Tuple[str, List[str]]:
        """Apply transformations to extracted content."""
        notes = []
        
        # Add source header
        header = f"# Extracted from {source_branch}\n# Extraction date: {datetime.now().isoformat()}\n"
        if content_type == "python":
            header = f'"""\n{header}"""\n\n'
        elif content_type in ["yaml", "markdown"]:
            header = f"# {header}\n"
        
        notes.append(f"Added source header from {source_branch}")
        
        # Update version references
        if "5.5" in content or "5.0" in content or "4.0" in content:
            notes.append("Contains version references that may need updating")
        
        # Update import paths if Python
        if content_type == "python":
            if "from src." in content or "import src." in content:
                notes.append("Contains src.* imports - verify compatibility")
        
        return header + content, notes
    
    def _log_extraction(self, asset: ExtractedAsset):
        """Log extraction to manifest."""
        manifest_path = self.output_root / "extraction-manifest.json"
        
        manifest = []
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        
        manifest.append({
            "source_branch": asset.source_branch,
            "source_path": asset.source_path,
            "target_path": asset.target_path,
            "content_type": asset.content_type,
            "extracted_at": datetime.now().isoformat(),
            "transformation_notes": asset.transformation_notes
        })
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def extract_category(
        self,
        category: SearchCategory,
        branch: Optional[str] = None
    ) -> List[ExtractedAsset]:
        """
        Extract all files in a category from a branch.
        
        Args:
            category: Category to extract
            branch: Source branch (default: highest version with content)
            
        Returns:
            List of extracted assets
        """
        if not branch:
            # Find best branch for this category
            for b in self.TARGET_BRANCHES:
                if b in self.branch_indexes:
                    if self.branch_indexes[b].categories.get(category.value, 0) > 0:
                        branch = b
                        break
        
        if not branch:
            branch = self.TARGET_BRANCHES[0]
        
        results = self.search("", categories=[category], branches=[branch], max_results=100)
        assets = []
        
        for result in results:
            asset = self.extract_asset(result.branch, result.file_path)
            if asset:
                assets.append(asset)
        
        return assets
    
    def generate_requirements_integration(
        self,
        search_results: List[GitSearchResult]
    ) -> Dict[str, Any]:
        """
        Generate CX6-requirements integration from search results.
        
        Args:
            search_results: Results to integrate
            
        Returns:
            Dictionary ready for CX6-requirements schema
        """
        integration = {
            "schema_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "source": "git-history-intelligence",
            "recovered_assets": [],
            "recommended_ac_ids": [],
            "integration_notes": []
        }
        
        for result in search_results:
            asset_entry = {
                "source_branch": result.branch,
                "source_path": result.file_path,
                "category": result.category.value,
                "relevance": result.relevance_score,
                "matched_terms": result.matched_terms,
                "status": "pending_review"
            }
            integration["recovered_assets"].append(asset_entry)
            
            # Suggest AC-IDs based on category
            ac_prefix = {
                SearchCategory.GOVERNANCE: "AC-GOV",
                SearchCategory.ORCHESTRATOR: "AC-ORCH",
                SearchCategory.INFRASTRUCTURE: "AC-INFRA",
                SearchCategory.TOOLS: "AC-TOOL",
            }.get(result.category, "AC-MISC")
            
            integration["recommended_ac_ids"].append(
                f"{ac_prefix}-RECOVERED-{len(integration['recommended_ac_ids']) + 1:03d}"
            )
        
        # Save integration file
        output_file = self.output_root / "cx6-requirements-integration.yaml"
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(integration, f, default_flow_style=False, sort_keys=False)
        
        return integration
    
    # =========================================================================
    # CLI Interface
    # =========================================================================
    
    def cli_search(self, query: str) -> str:
        """CLI-friendly search output."""
        results = self.search(query)
        
        if not results:
            return f"No results found for: {query}"
        
        output = [f"## Search Results for: {query}", f"Found {len(results)} matches\n"]
        
        for i, result in enumerate(results, 1):
            output.append(f"### {i}. {result.file_path}")
            output.append(f"- **Branch:** {result.branch}")
            output.append(f"- **Category:** {result.category.value}")
            output.append(f"- **Relevance:** {result.relevance_score:.2f}")
            output.append(f"- **Matched:** {', '.join(result.matched_terms)}")
            output.append(f"- **Lines:** {result.line_count}")
            output.append("")
        
        return "\n".join(output)
    
    def cli_extract(self, branch: str, file_path: str) -> str:
        """CLI-friendly extraction."""
        asset = self.extract_asset(branch, file_path)
        
        if not asset:
            return f"Failed to extract {branch}:{file_path}"
        
        return f"""## Extracted Asset

- **Source:** {asset.source_branch}:{asset.source_path}
- **Target:** {asset.target_path}
- **Type:** {asset.content_type}
- **Notes:** {', '.join(asset.transformation_notes) or 'None'}
"""


# =============================================================================
# Standalone CLI
# =============================================================================

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Git History Intelligence Tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Build search index")
    index_parser.add_argument("--force", action="store_true", help="Force rebuild")
    index_parser.add_argument("--branches", nargs="+", help="Specific branches to index")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search git history")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", help="Limit to category")
    search_parser.add_argument("--branch", help="Limit to branch")
    search_parser.add_argument("--max", type=int, default=20, help="Max results")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract asset")
    extract_parser.add_argument("branch", help="Source branch")
    extract_parser.add_argument("path", help="File path")
    extract_parser.add_argument("--name", help="Target filename")
    
    # Batch extract command
    batch_parser = subparsers.add_parser("batch", help="Batch extract category")
    batch_parser.add_argument("category", help="Category to extract")
    batch_parser.add_argument("--branch", help="Source branch")
    
    args = parser.parse_args()
    
    tool = GitHistoryIntelligence()
    
    if args.command == "index":
        tool.build_index(branches=args.branches, force=args.force)
        print("Index built successfully")
    
    elif args.command == "search":
        categories = [SearchCategory(args.category)] if args.category else None
        branches = [args.branch] if args.branch else None
        results = tool.search(args.query, categories=categories, branches=branches, max_results=args.max)
        print(tool.cli_search(args.query))
    
    elif args.command == "extract":
        print(tool.cli_extract(args.branch, args.path))
    
    elif args.command == "batch":
        category = SearchCategory(args.category)
        assets = tool.extract_category(category, branch=args.branch)
        print(f"Extracted {len(assets)} assets in category {args.category}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
