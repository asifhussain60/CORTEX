# CORTEX 2.0 Documentation System

**Document:** 06-documentation-system.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Automate MkDocs documentation maintenance to:
- Auto-generate navigation structure from directory layout
- Detect and remove duplicate documentation
- Validate internal links
- Clean up orphaned documentation
- Keep docs synchronized with code

---

## ❌ Current Pain Points (CORTEX 1.0)

### Problem 1: Manual Navigation Updates
```yaml
# mkdocs.yml - manually maintained
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - Architecture:
    - Overview: architecture/overview.md
    # ❌ New files must be manually added
    # ❌ Renamed files must be manually updated
    # ❌ Deleted files leave broken links
```

### Problem 2: Duplicate Documentation
```
docs/
  getting-started/
    installation.md
    setup.md  # ← Same content as installation.md
  guides/
    installation-guide.md  # ← Another duplicate!
  
# User confusion - which is current?
```

### Problem 3: Broken Links
```markdown
<!-- docs/architecture/overview.md -->
See [Plugin System](../plugins/system.md)

# ❌ File was moved to architecture/plugins.md
# ❌ Link now broken, no detection
```

### Problem 4: Orphaned Documentation
```
Code deleted:
  src/old_feature/processor.py

Documentation still exists:
  docs/guides/old-feature-processing.md
  
# ❌ Stale docs confuse users
```

---

## ✅ CORTEX 2.0 Solution

### Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│       Documentation Manager (NEW)                       │
├────────────────────────────────────────────────────────┤
│  • Auto-generates mkdocs.yml navigation                │
│  • Detects duplicate content (fuzzy matching)          │
│  • Validates all internal links                        │
│  • Finds orphaned documentation                        │
│  • Cleanup recommendations                             │
└─────────────────────┬──────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────────┐        ┌─────▼──────────┐
    │ Nav Generator│        │Content Analyzer │
    ├──────────────┤        ├─────────────────┤
    │• Scan docs/  │        │• Hash comparison│
    │• Build tree  │        │• Similarity     │
    │• Generate nav│        │• Link checking  │
    └──────────────┘        └─────────────────┘
         │                         │
         └────────────┬────────────┘
                      │
         ┌────────────▼──────────────┐
         │  MkDocs Integration       │
         │  • mkdocs.yml generation  │
         │  • .pages meta files      │
         │  • Automated cleanup      │
         └───────────────────────────┘
```

---

## 🏗️ Implementation: Documentation Manager

```python
# src/maintenance/documentation_manager.py

from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
import hashlib
from dataclasses import dataclass
import yaml
import re
from difflib import SequenceMatcher

@dataclass
class DocumentMetadata:
    """Metadata for a documentation file"""
    path: Path
    title: str
    content_hash: str
    word_count: int
    internal_links: List[str]
    external_links: List[str]
    last_modified: float
    
@dataclass
class DuplicateCandidate:
    """Potential duplicate documentation"""
    file1: Path
    file2: Path
    similarity: float
    reason: str  # content_match, title_match, etc.
    
@dataclass
class BrokenLink:
    """Broken internal link"""
    source_file: Path
    link_text: str
    target_path: str
    reason: str  # not_found, moved, etc.

class DocumentationManager:
    """Manages MkDocs documentation lifecycle"""
    
    def __init__(self, docs_root: Path, workspace_root: Path):
        """
        Initialize documentation manager
        
        Args:
            docs_root: Path to docs/ directory
            workspace_root: Project root for code reference
        """
        self.docs_root = docs_root
        self.workspace_root = workspace_root
        self.mkdocs_yml = workspace_root / "mkdocs.yml"
        
        # Caches
        self._doc_metadata: Dict[Path, DocumentMetadata] = {}
        self._navigation_tree: Dict = {}
    
    def scan_documentation(self) -> Dict[Path, DocumentMetadata]:
        """
        Scan all documentation files and extract metadata
        
        Returns:
            Dictionary mapping file paths to metadata
        """
        self._doc_metadata = {}
        
        for md_file in self.docs_root.rglob("*.md"):
            metadata = self._extract_metadata(md_file)
            self._doc_metadata[md_file] = metadata
        
        return self._doc_metadata
    
    def generate_navigation(self, 
                          exclude_patterns: Optional[List[str]] = None) -> Dict:
        """
        Auto-generate navigation structure from directory layout
        
        Args:
            exclude_patterns: Glob patterns to exclude
        
        Returns:
            Navigation dictionary for mkdocs.yml
        """
        exclude_patterns = exclude_patterns or ["_*", ".*"]
        
        # Build navigation tree
        nav = []
        
        # Process top-level index
        index_file = self.docs_root / "index.md"
        if index_file.exists():
            nav.append({"Home": "index.md"})
        
        # Process directories
        for item in sorted(self.docs_root.iterdir()):
            if not item.is_dir():
                continue
            
            # Skip excluded
            if any(item.match(pattern) for pattern in exclude_patterns):
                continue
            
            # Build section
            section = self._build_section(item, item.name)
            if section:
                nav.append(section)
        
        self._navigation_tree = {"nav": nav}
        return self._navigation_tree
    
    def detect_duplicates(self, 
                        similarity_threshold: float = 0.85) -> List[DuplicateCandidate]:
        """
        Detect duplicate or very similar documentation
        
        Args:
            similarity_threshold: Minimum similarity (0.0-1.0) to flag
        
        Returns:
            List of duplicate candidates
        """
        duplicates = []
        
        # Ensure metadata is loaded
        if not self._doc_metadata:
            self.scan_documentation()
        
        files = list(self._doc_metadata.keys())
        
        # Compare all pairs
        for i, file1 in enumerate(files):
            meta1 = self._doc_metadata[file1]
            
            for file2 in files[i+1:]:
                meta2 = self._doc_metadata[file2]
                
                # Check 1: Identical content hash
                if meta1.content_hash == meta2.content_hash:
                    duplicates.append(DuplicateCandidate(
                        file1=file1,
                        file2=file2,
                        similarity=1.0,
                        reason="identical_content"
                    ))
                    continue
                
                # Check 2: Similar titles
                title_similarity = self._text_similarity(meta1.title, meta2.title)
                if title_similarity > 0.9:
                    # Also check content similarity
                    content_similarity = self._file_similarity(file1, file2)
                    if content_similarity > similarity_threshold:
                        duplicates.append(DuplicateCandidate(
                            file1=file1,
                            file2=file2,
                            similarity=content_similarity,
                            reason="similar_title_and_content"
                        ))
                        continue
                
                # Check 3: Very similar content
                content_similarity = self._file_similarity(file1, file2)
                if content_similarity > similarity_threshold:
                    duplicates.append(DuplicateCandidate(
                        file1=file1,
                        file2=file2,
                        similarity=content_similarity,
                        reason="similar_content"
                    ))
        
        return duplicates
    
    def validate_links(self) -> List[BrokenLink]:
        """
        Validate all internal links in documentation
        
        Returns:
            List of broken links found
        """
        broken_links = []
        
        # Ensure metadata is loaded
        if not self._doc_metadata:
            self.scan_documentation()
        
        for doc_file, metadata in self._doc_metadata.items():
            for link in metadata.internal_links:
                # Resolve relative link
                target = self._resolve_link(doc_file, link)
                
                if not target.exists():
                    # Try to find if file was moved
                    possible_locations = self._find_file(target.name)
                    
                    reason = "not_found"
                    if possible_locations:
                        reason = f"moved_to_{possible_locations[0].relative_to(self.docs_root)}"
                    
                    broken_links.append(BrokenLink(
                        source_file=doc_file,
                        link_text=link,
                        target_path=str(target),
                        reason=reason
                    ))
        
        return broken_links
    
    def find_orphaned_docs(self) -> List[Path]:
        """
        Find documentation that references deleted code
        
        Returns:
            List of potentially orphaned documentation files
        """
        orphaned = []
        
        # Scan for code references in docs
        for doc_file in self.docs_root.rglob("*.md"):
            content = doc_file.read_text(encoding='utf-8')
            
            # Extract code references (e.g., `src/module/file.py`)
            code_refs = self._extract_code_references(content)
            
            for ref in code_refs:
                code_file = self.workspace_root / ref
                
                # Check if referenced code exists
                if not code_file.exists():
                    orphaned.append(doc_file)
                    break  # One missing reference is enough
        
        return orphaned
    
    def cleanup_recommendations(self) -> Dict[str, List]:
        """
        Generate comprehensive cleanup recommendations
        
        Returns:
            Dictionary with different types of recommendations
        """
        recommendations = {
            "duplicates": [],
            "broken_links": [],
            "orphaned": [],
            "empty_sections": [],
            "outdated": []
        }
        
        # Detect duplicates
        duplicates = self.detect_duplicates()
        for dup in duplicates:
            recommendations["duplicates"].append({
                "file1": str(dup.file1.relative_to(self.docs_root)),
                "file2": str(dup.file2.relative_to(self.docs_root)),
                "similarity": f"{dup.similarity:.0%}",
                "reason": dup.reason,
                "action": f"Review and merge {dup.file1.name} into {dup.file2.name}"
            })
        
        # Validate links
        broken = self.validate_links()
        for link in broken:
            recommendations["broken_links"].append({
                "file": str(link.source_file.relative_to(self.docs_root)),
                "link": link.link_text,
                "target": link.target_path,
                "reason": link.reason,
                "action": "Update or remove link"
            })
        
        # Find orphaned docs
        orphaned = self.find_orphaned_docs()
        for doc in orphaned:
            recommendations["orphaned"].append({
                "file": str(doc.relative_to(self.docs_root)),
                "action": "Review and update or delete"
            })
        
        # Find empty sections (directories with no content files)
        empty_dirs = self._find_empty_sections()
        for dir_path in empty_dirs:
            recommendations["empty_sections"].append({
                "directory": str(dir_path.relative_to(self.docs_root)),
                "action": "Remove empty directory"
            })
        
        return recommendations
    
    def update_mkdocs_config(self, backup: bool = True):
        """
        Update mkdocs.yml with generated navigation
        
        Args:
            backup: Create backup before updating
        """
        if backup and self.mkdocs_yml.exists():
            backup_path = self.mkdocs_yml.with_suffix(".yml.backup")
            backup_path.write_text(self.mkdocs_yml.read_text())
        
        # Load existing config
        if self.mkdocs_yml.exists():
            config = yaml.safe_load(self.mkdocs_yml.read_text())
        else:
            config = {}
        
        # Generate new navigation
        nav = self.generate_navigation()
        
        # Update nav section
        config["nav"] = nav["nav"]
        
        # Write back
        with open(self.mkdocs_yml, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def generate_report(self) -> str:
        """Generate human-readable documentation health report"""
        recommendations = self.cleanup_recommendations()
        
        report = ["=" * 70]
        report.append("DOCUMENTATION HEALTH REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        total_issues = sum(len(items) for items in recommendations.values())
        if total_issues == 0:
            report.append("✅ No issues found! Documentation is clean.")
            return "\n".join(report)
        
        report.append(f"Found {total_issues} issues:")
        report.append("")
        
        # Duplicates
        if recommendations["duplicates"]:
            report.append(f"📋 DUPLICATES: {len(recommendations['duplicates'])}")
            report.append("-" * 70)
            for dup in recommendations["duplicates"][:3]:
                report.append(f"  • {dup['file1']} ≈ {dup['file2']} ({dup['similarity']})")
            if len(recommendations["duplicates"]) > 3:
                report.append(f"  ... and {len(recommendations['duplicates']) - 3} more")
            report.append("")
        
        # Broken links
        if recommendations["broken_links"]:
            report.append(f"🔗 BROKEN LINKS: {len(recommendations['broken_links'])}")
            report.append("-" * 70)
            for link in recommendations["broken_links"][:3]:
                report.append(f"  • {link['file']}: {link['link']}")
            if len(recommendations["broken_links"]) > 3:
                report.append(f"  ... and {len(recommendations['broken_links']) - 3} more")
            report.append("")
        
        # Orphaned docs
        if recommendations["orphaned"]:
            report.append(f"📄 ORPHANED DOCS: {len(recommendations['orphaned'])}")
            report.append("-" * 70)
            for orphan in recommendations["orphaned"][:3]:
                report.append(f"  • {orphan['file']}")
            if len(recommendations["orphaned"]) > 3:
                report.append(f"  ... and {len(recommendations['orphaned']) - 3} more")
            report.append("")
        
        # Empty sections
        if recommendations["empty_sections"]:
            report.append(f"📁 EMPTY SECTIONS: {len(recommendations['empty_sections'])}")
            report.append("-" * 70)
            for section in recommendations["empty_sections"]:
                report.append(f"  • {section['directory']}/")
            report.append("")
        
        report.append("Run with --auto-clean to apply safe fixes automatically.")
        
        return "\n".join(report)
    
    # Helper methods
    
    def _extract_metadata(self, md_file: Path) -> DocumentMetadata:
        """Extract metadata from a markdown file"""
        content = md_file.read_text(encoding='utf-8')
        
        # Extract title (first # heading or filename)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Count words
        word_count = len(content.split())
        
        # Extract links
        internal_links = re.findall(r'\[.+?\]\((?!http)(.+?)\)', content)
        external_links = re.findall(r'\[.+?\]\((https?://.+?)\)', content)
        
        return DocumentMetadata(
            path=md_file,
            title=title,
            content_hash=content_hash,
            word_count=word_count,
            internal_links=internal_links,
            external_links=external_links,
            last_modified=md_file.stat().st_mtime
        )
    
    def _build_section(self, dir_path: Path, section_name: str) -> Optional[Dict]:
        """Build navigation section from directory"""
        items = []
        
        # Check for section index
        index_file = dir_path / "index.md"
        if index_file.exists():
            rel_path = index_file.relative_to(self.docs_root)
            items.append({self._title_case(section_name): str(rel_path)})
        
        # Add markdown files
        for md_file in sorted(dir_path.glob("*.md")):
            if md_file.name == "index.md":
                continue
            
            title = self._extract_title(md_file)
            rel_path = md_file.relative_to(self.docs_root)
            items.append({title: str(rel_path)})
        
        # Add subdirectories
        for subdir in sorted(dir_path.iterdir()):
            if subdir.is_dir() and not subdir.name.startswith(("_", ".")):
                subsection = self._build_section(subdir, subdir.name)
                if subsection:
                    items.append(subsection)
        
        if not items:
            return None
        
        return {self._title_case(section_name): items}
    
    def _extract_title(self, md_file: Path) -> str:
        """Extract title from markdown file"""
        try:
            content = md_file.read_text(encoding='utf-8')
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1)
        except:
            pass
        return self._title_case(md_file.stem)
    
    def _title_case(self, text: str) -> str:
        """Convert text to title case"""
        return text.replace("-", " ").replace("_", " ").title()
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _file_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate similarity between two files"""
        content1 = file1.read_text(encoding='utf-8')
        content2 = file2.read_text(encoding='utf-8')
        
        # Normalize whitespace
        content1 = ' '.join(content1.split())
        content2 = ' '.join(content2.split())
        
        return SequenceMatcher(None, content1, content2).ratio()
    
    def _resolve_link(self, source: Path, link: str) -> Path:
        """Resolve relative link to absolute path"""
        # Remove anchors
        link = link.split('#')[0]
        
        # Resolve relative to source file's directory
        source_dir = source.parent
        target = (source_dir / link).resolve()
        
        return target
    
    def _find_file(self, filename: str) -> List[Path]:
        """Find all files with given name in docs"""
        return list(self.docs_root.rglob(filename))
    
    def _extract_code_references(self, content: str) -> List[str]:
        """Extract code file references from documentation"""
        # Match patterns like `src/module/file.py` or `tests/test_*.py`
        patterns = [
            r'`(src/[^`]+\.(py|ts|js|cs))`',
            r'`(tests/[^`]+\.(py|ts|js|cs))`',
        ]
        
        refs = []
        for pattern in patterns:
            refs.extend(re.findall(pattern, content))
        
        # Extract just the path (first capture group)
        return [ref[0] if isinstance(ref, tuple) else ref for ref in refs]
    
    def _find_empty_sections(self) -> List[Path]:
        """Find empty directories in docs"""
        empty = []
        
        for dir_path in self.docs_root.rglob("*"):
            if not dir_path.is_dir():
                continue
            
            # Check if directory has any markdown files
            md_files = list(dir_path.glob("*.md"))
            if not md_files:
                # Also check subdirectories
                has_content = any(dir_path.rglob("*.md"))
                if not has_content:
                    empty.append(dir_path)
        
        return empty
```

---

## 🔌 Plugin Integration

```python
# src/plugins/documentation_plugin.py

from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from maintenance.documentation_manager import DocumentationManager

class Plugin(BasePlugin):
    """Auto-refresh documentation plugin"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="documentation_plugin",
            name="Documentation Auto-Refresh",
            version="1.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.NORMAL,
            description="Automatically refreshes MkDocs navigation and detects issues",
            author="CORTEX",
            dependencies=[],
            hooks=[
                HookPoint.AFTER_BRAIN_UPDATE.value,
                HookPoint.ON_DOC_REFRESH.value
            ],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        self.doc_manager = DocumentationManager(
            docs_root=Path(self.config.get("docs_root", "docs")),
            workspace_root=Path(self.config.get("workspace_root", "."))
        )
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh"""
        
        # Scan documentation
        self.doc_manager.scan_documentation()
        
        # Generate navigation
        self.doc_manager.update_mkdocs_config(backup=True)
        
        # Generate report
        report = self.doc_manager.generate_report()
        
        return {
            "success": True,
            "message": "Documentation refreshed",
            "report": report
        }
```

---

## 📊 CLI Commands

```bash
# Refresh navigation
python scripts/docs-manager.py --refresh-nav

# Detect duplicates
python scripts/docs-manager.py --find-duplicates

# Validate links
python scripts/docs-manager.py --validate-links

# Find orphaned docs
python scripts/docs-manager.py --find-orphaned

# Full health check
python scripts/docs-manager.py --health-check

# Generate report
python scripts/docs-manager.py --report --output docs-report.txt

# Auto-clean (safe fixes only)
python scripts/docs-manager.py --auto-clean
```

---

## ✅ Benefits

### 1. Zero Manual Navigation Updates
```yaml
# Before: Manual updates
nav:
  - Getting Started:
    - Installation: getting-started/installation.md
    # ❌ Forgot to add new quick-start.md

# After: Auto-generated
nav:
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quick-start.md  # ✅ Auto-added
```

### 2. Duplicate Detection
```
Found duplicates:
  • docs/getting-started/installation.md ≈ docs/guides/install.md (92%)
  
Recommendation: Merge into getting-started/installation.md
```

### 3. Link Validation
```
Broken links:
  • docs/architecture/overview.md → ../plugins/system.md
    Reason: moved_to_architecture/plugins.md
    
Auto-fix: Update link to architecture/plugins.md
```

### 4. Orphan Detection
```
Orphaned docs (code deleted):
  • docs/features/old-processor.md (references deleted src/old_feature/)
  
Recommendation: Remove or update
```

---

**Next:** 07-self-review-system.md (Comprehensive health checks and auto-fix)
