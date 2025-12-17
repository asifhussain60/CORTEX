"""
Plan File Format Resolver

Transparently resolves MD references to YAML for efficient processing.
Users reference natural .md files, orchestrators use structured YAML internally.

Design Pattern:
- User: "continue with #file:00-master-plan.md"
- Orchestrator: Automatically uses YAML if available, converts MD if needed
- Caching: Converted plans cached as YAML for future use

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0
"""

import hashlib
import logging
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PlanResolutionResult:
    """Result of plan file resolution."""
    success: bool
    data: Optional[Dict[str, Any]]
    source_format: str  # 'yaml', 'markdown', 'cache'
    source_path: Path
    yaml_path: Optional[Path]  # Path to YAML (original or converted)
    error_message: Optional[str] = None
    cached: bool = False
    conversion_time: float = 0.0


class PlanFileResolver:
    """
    Resolves plan file references to structured YAML data.
    
    Priority:
    1. Check for .yaml version in manifests/orchestrators/
    2. Check for .md in documents/planning/
    3. Convert MD → YAML and cache
    4. Return structured dict
    """
    
    def __init__(self, brain_path: Path, cache_dir: Optional[Path] = None):
        """
        Initialize resolver.
        
        Args:
            brain_path: Path to cortex-brain directory
            cache_dir: Directory for caching converted YAML (default: cortex-brain/cache/plan-conversions)
        """
        self.brain_path = Path(brain_path)
        self.cache_dir = cache_dir or self.brain_path / "cache" / "plan-conversions"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifests_dir = self.brain_path / "manifests" / "orchestrators"
        self.planning_docs_dir = self.brain_path / "documents" / "planning"
        
        logger.info(f"PlanFileResolver initialized:")
        logger.info(f"  Brain path: {self.brain_path}")
        logger.info(f"  Manifests: {self.manifests_dir}")
        logger.info(f"  Planning docs: {self.planning_docs_dir}")
        logger.info(f"  Cache: {self.cache_dir}")
    
    def resolve_plan_file(self, user_reference: str) -> PlanResolutionResult:
        """
        Resolve plan file reference to YAML data.
        
        Args:
            user_reference: File reference like "00-master-plan.md", "#file:plan.md", 
                          or full path
        
        Returns:
            PlanResolutionResult with structured data or error
        
        Examples:
            >>> resolver.resolve_plan_file("00-master-plan.md")
            >>> resolver.resolve_plan_file("#file:planning/active/cortex-v1/00-master-plan.md")
            >>> resolver.resolve_plan_file("/full/path/to/plan.md")
        """
        start_time = datetime.now()
        
        # Extract filename from various formats
        filename = self._extract_filename(user_reference)
        base_name = Path(filename).stem
        
        # Priority 1: Check for .yaml in orchestrator-manifests
        yaml_manifest_path = self.manifests_dir / f"{base_name}.yaml"
        if yaml_manifest_path.exists():
            logger.info(f"✅ Found YAML manifest: {yaml_manifest_path}")
            return self._load_yaml_file(yaml_manifest_path, source_format='yaml')
        
        # Priority 2: Find .md file in planning directory structure
        md_path = self._find_markdown_file(user_reference)
        if md_path and md_path.exists():
            logger.info(f"📄 Found Markdown plan: {md_path}")
            
            # Check if cached YAML exists and is valid
            cached_yaml_path = self._get_cache_path(md_path)
            if self._is_cache_valid(md_path, cached_yaml_path):
                logger.info(f"✅ Using cached YAML: {cached_yaml_path}")
                result = self._load_yaml_file(cached_yaml_path, source_format='cache')
                result.cached = True
                return result
            
            # Convert MD → YAML
            logger.info(f"🔄 Converting Markdown → YAML: {md_path}")
            result = self._convert_markdown_to_yaml(md_path)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            result.conversion_time = elapsed
            
            return result
        
        # Not found
        error_msg = f"Plan file not found: {user_reference}\n"
        error_msg += f"  Searched in:\n"
        error_msg += f"    - {self.manifests_dir}/{base_name}.yaml\n"
        error_msg += f"    - {self.planning_docs_dir}/**/{filename}"
        
        return PlanResolutionResult(
            success=False,
            data=None,
            source_format='none',
            source_path=Path(user_reference),
            yaml_path=None,
            error_message=error_msg
        )
    
    def _extract_filename(self, reference: str) -> str:
        """Extract filename from various reference formats."""
        # Remove #file: prefix
        reference = reference.replace("#file:", "").strip()
        
        # If it's a full path, get just the filename
        path = Path(reference)
        
        # If it's already just a filename or relative path
        if not path.is_absolute():
            return reference
        
        # Extract last segment
        return path.name
    
    def _find_markdown_file(self, reference: str) -> Optional[Path]:
        """
        Find markdown file in planning directory structure.
        
        Searches:
        1. Exact path if provided (absolute or relative to planning_docs_dir)
        2. Recursive search in documents/planning/**/{filename} (last resort)
        """
        reference = reference.replace("#file:", "").strip()
        path = Path(reference)
        
        # Check if absolute path exists
        if path.is_absolute() and path.exists():
            return path
        
        # Check relative to planning_docs_dir with full path structure preserved
        candidate = self.planning_docs_dir / reference
        if candidate.exists():
            return candidate
        
        # If no path separators, do recursive search as last resort
        if '/' not in reference and '\\' not in reference:
            filename = path.name
            matches = list(self.planning_docs_dir.rglob(filename))
            
            if matches:
                if len(matches) > 1:
                    logger.warning(
                        f"Multiple matches found for {filename}:\n" +
                        "\n".join(f"  - {m}" for m in matches) +
                        f"\nUsing first: {matches[0]}\n" +
                        "💡 Tip: Provide full path to avoid ambiguity: 'active/plan-name/00-master-plan.md'"
                    )
                return matches[0]
        
        return None
    
    def _load_yaml_file(self, yaml_path: Path, source_format: str) -> PlanResolutionResult:
        """Load and parse YAML file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return PlanResolutionResult(
                success=True,
                data=data,
                source_format=source_format,
                source_path=yaml_path,
                yaml_path=yaml_path
            )
        
        except Exception as e:
            logger.error(f"Failed to load YAML: {yaml_path}", exc_info=True)
            return PlanResolutionResult(
                success=False,
                data=None,
                source_format=source_format,
                source_path=yaml_path,
                yaml_path=None,
                error_message=f"YAML parsing error: {str(e)}"
            )
    
    def _convert_markdown_to_yaml(self, md_path: Path) -> PlanResolutionResult:
        """
        Convert Markdown plan to YAML structure.
        
        Extracts:
        - Plan metadata (ID, date, complexity, status)
        - Phases with progress tracking
        - Continuation prompt
        - Visual progress tracker data
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse markdown structure
            plan_data = self._parse_markdown_plan(content, md_path)
            
            # Cache as YAML
            cache_path = self._get_cache_path(md_path)
            with open(cache_path, 'w', encoding='utf-8') as f:
                yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"✅ Cached YAML: {cache_path}")
            
            return PlanResolutionResult(
                success=True,
                data=plan_data,
                source_format='markdown',
                source_path=md_path,
                yaml_path=cache_path,
                cached=False
            )
        
        except Exception as e:
            logger.error(f"Failed to convert Markdown to YAML: {md_path}", exc_info=True)
            return PlanResolutionResult(
                success=False,
                data=None,
                source_format='markdown',
                source_path=md_path,
                yaml_path=None,
                error_message=f"Conversion error: {str(e)}"
            )
    
    def _parse_markdown_plan(self, content: str, md_path: Path) -> Dict[str, Any]:
        """
        Parse structured Markdown plan into YAML dict.
        
        Expected structure:
        - Title line with "CORTEX - {Plan Name}"
        - Metadata section (Plan ID, Date, Complexity)
        - Executive Summary
        - Visual Progress Tracker (table)
        - Continuation Prompt
        """
        lines = content.split('\n')
        
        plan_data: Dict[str, Any] = {
            'metadata': {},
            'summary': '',
            'phases': [],
            'progress': {},
            'continuation_prompt': '',
            'source_file': str(md_path)
        }
        
        # Extract title
        title_match = re.search(r'🧠 CORTEX - (.+?)$', lines[0] if lines else '', re.MULTILINE)
        if title_match:
            plan_data['metadata']['title'] = title_match.group(1).strip()
        
        # Extract metadata fields
        for line in lines[:50]:  # Check first 50 lines
            if match := re.match(r'\*\*Plan ID:\*\*\s*(.+)', line):
                plan_data['metadata']['plan_id'] = match.group(1).strip()
            elif match := re.match(r'\*\*Date:\*\*\s*(.+)', line):
                plan_data['metadata']['date'] = match.group(1).strip()
            elif match := re.match(r'\*\*Complexity Tier:\*\*\s*(.+)', line):
                plan_data['metadata']['complexity_tier'] = match.group(1).strip()
        
        # Extract Executive Summary
        summary_start = None
        for i, line in enumerate(lines):
            if '## 🎯 Executive Summary' in line:
                summary_start = i + 1
                break
        
        if summary_start:
            summary_lines = []
            for line in lines[summary_start:]:
                if line.strip().startswith('##'):
                    break
                if line.strip():
                    summary_lines.append(line.strip())
            plan_data['summary'] = ' '.join(summary_lines)
        
        # Extract Visual Progress Tracker table
        progress_table_start = None
        for i, line in enumerate(lines):
            if '## 📊 Visual Progress Tracker' in line:
                progress_table_start = i + 1
                break
        
        if progress_table_start:
            # Parse progress percentage
            for line in lines[progress_table_start:progress_table_start + 10]:
                if match := re.search(r'\[([█░]+)\]\s*(\d+)%\s*\(([^)]+)\)', line):
                    plan_data['progress']['percentage'] = int(match.group(2))
                    plan_data['progress']['phases_complete'] = match.group(3).strip()
                elif match := re.search(r'\*\*Total Actual:\*\*\s*(.+?)\s*\|', line):
                    plan_data['progress']['actual_time'] = match.group(1).strip()
                elif match := re.search(r'\*\*Total Elapsed:\*\*\s*(.+)', line):
                    plan_data['progress']['elapsed_time'] = match.group(1).strip()
            
            # Parse phase table
            table_start = None
            for i in range(progress_table_start, min(progress_table_start + 20, len(lines))):
                if lines[i].strip().startswith('|') and 'Phase' in lines[i]:
                    table_start = i + 2  # Skip header and separator
                    break
            
            if table_start:
                phases = []
                for line in lines[table_start:]:
                    if not line.strip().startswith('|'):
                        break
                    
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 5:
                        phase = {
                            'id': parts[0],
                            'name': re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', parts[1]),  # Remove MD links
                            'status': parts[2],
                            'actual_time': parts[3],
                            'elapsed_time': parts[4]
                        }
                        phases.append(phase)
                
                plan_data['phases'] = phases
        
        # Extract Continuation Prompt
        continuation_start = None
        for i, line in enumerate(lines):
            if '## 🔄 Continuation Prompt' in line:
                continuation_start = i + 1
                break
        
        if continuation_start:
            # Find code block
            in_code_block = False
            continuation_lines = []
            for line in lines[continuation_start:]:
                if '```' in line:
                    if in_code_block:
                        break
                    in_code_block = True
                    continue
                if in_code_block:
                    continuation_lines.append(line)
            
            plan_data['continuation_prompt'] = '\n'.join(continuation_lines).strip()
        
        return plan_data
    
    def _get_cache_path(self, md_path: Path) -> Path:
        """Get cache path for converted YAML."""
        # Create hash from file path for unique cache name
        path_hash = hashlib.md5(str(md_path).encode()).hexdigest()[:8]
        base_name = md_path.stem
        return self.cache_dir / f"{base_name}_{path_hash}.yaml"
    
    def _is_cache_valid(self, md_path: Path, cache_path: Path) -> bool:
        """Check if cached YAML is valid (exists and newer than MD)."""
        if not cache_path.exists():
            return False
        
        md_mtime = md_path.stat().st_mtime
        cache_mtime = cache_path.stat().st_mtime
        
        return cache_mtime > md_mtime


# Convenience function for quick access
def resolve_plan_file(user_reference: str, brain_path: Optional[Path] = None) -> PlanResolutionResult:
    """
    Quick function to resolve plan file reference.
    
    Args:
        user_reference: File reference like "00-master-plan.md" or "#file:plan.md"
        brain_path: Path to cortex-brain (auto-detected if None)
    
    Returns:
        PlanResolutionResult with structured data
    
    Example:
        >>> result = resolve_plan_file("#file:00-master-plan.md")
        >>> if result.success:
        >>>     print(result.data['metadata']['plan_id'])
    """
    if brain_path is None:
        # Auto-detect brain path
        brain_path = Path.cwd() / "cortex-brain"
        if not brain_path.exists():
            # Try parent directory
            brain_path = Path.cwd().parent / "cortex-brain"
    
    resolver = PlanFileResolver(brain_path)
    return resolver.resolve_plan_file(user_reference)
