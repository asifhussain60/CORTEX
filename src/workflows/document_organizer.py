"""
Document Organizer for CORTEX Brain

Automatically organizes documents into structured categories within cortex-brain/documents/
following the mandatory document organization rules.

Categories:
- reports/ - Status reports, test results, validation reports
- analysis/ - Code analysis, architecture analysis
- summaries/ - Project summaries, progress summaries
- investigations/ - Bug investigations, issue analysis
- planning/ - Feature plans, ADO work items
- conversation-captures/ - Imported conversations
- implementation-guides/ - How-to guides, tutorials

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil


class DocumentCategory:
    """Document category definitions with pattern matching."""
    
    REPORTS = "reports"
    ANALYSIS = "analysis"
    SUMMARIES = "summaries"
    INVESTIGATIONS = "investigations"
    PLANNING = "planning"
    CONVERSATION_CAPTURES = "conversation-captures"
    IMPLEMENTATION_GUIDES = "implementation-guides"
    
    @classmethod
    def all_categories(cls) -> List[str]:
        """Get all valid category names."""
        return [
            cls.REPORTS,
            cls.ANALYSIS,
            cls.SUMMARIES,
            cls.INVESTIGATIONS,
            cls.PLANNING,
            cls.CONVERSATION_CAPTURES,
            cls.IMPLEMENTATION_GUIDES
        ]
    
    @classmethod
    def get_patterns(cls) -> Dict[str, List[str]]:
        """Get filename patterns for each category."""
        return {
            cls.REPORTS: [
                r".*report.*\.md$",
                r".*-report\.md$",
                r".*_report\.md$",
                r".*test.*results?.*\.md$",
                r".*validation.*\.md$",
                r".*status.*\.md$",
                r"SESSION-.*\.md$",
                r"TDD-SESSION-.*\.md$",
                r"SPRINT-.*COMPLETE\.md$"
            ],
            cls.ANALYSIS: [
                r".*analysis.*\.md$",
                r".*-analysis\.md$",
                r".*_analysis\.md$",
                r".*architecture.*\.md$",
                r".*design.*\.md$",
                r".*code-review.*\.md$"
            ],
            cls.SUMMARIES: [
                r".*summary.*\.md$",
                r".*-summary\.md$",
                r".*_summary\.md$",
                r".*progress.*\.md$",
                r".*overview.*\.md$"
            ],
            cls.INVESTIGATIONS: [
                r".*investigation.*\.md$",
                r".*-investigation\.md$",
                r".*bug.*\.md$",
                r".*issue.*\.md$",
                r".*-fix\.md$",
                r".*troubleshoot.*\.md$",
                r".*debug.*\.md$"
            ],
            cls.PLANNING: [
                r"PLAN-.*\.md$",
                r"ADO-.*\.md$",
                r".*-plan\.md$",
                r".*_plan\.md$",
                r".*-planning\.md$",
                r".*roadmap.*\.md$",
                r".*strategy.*\.md$"
            ],
            cls.CONVERSATION_CAPTURES: [
                r"capture_.*\.md$",
                r"conversation-.*\.md$",
                r"chat-.*\.md$",
                r".*-capture\.md$"
            ],
            cls.IMPLEMENTATION_GUIDES: [
                r".*-guide\.md$",
                r".*_guide\.md$",
                r".*how-to.*\.md$",
                r".*tutorial.*\.md$",
                r".*instructions.*\.md$",
                r".*setup.*\.md$"
            ]
        }


class DocumentOrganizer:
    """
    Organizes CORTEX brain documents into structured categories.
    
    Features:
    - Auto-detection of document type from filename/content
    - Safe file moving with collision detection
    - Category index generation
    - Batch organization operations
    - Dry-run mode for preview
    
    Usage:
        organizer = DocumentOrganizer(brain_path)
        category = organizer.detect_category("SESSION-REPORT.md")
        new_path = organizer.organize_document(doc_path, category)
    """
    
    def __init__(self, brain_path: Path):
        """
        Initialize DocumentOrganizer.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.documents_path = self.brain_path / "documents"
        self.patterns = DocumentCategory.get_patterns()
        
        # Ensure all category directories exist
        self._ensure_categories()
    
    def _ensure_categories(self):
        """Create all category directories if they don't exist."""
        for category in DocumentCategory.all_categories():
            category_path = self.documents_path / category
            category_path.mkdir(parents=True, exist_ok=True)
    
    def detect_category(self, filename: str, content: Optional[str] = None) -> Optional[str]:
        """
        Detect document category from filename and optionally content.
        
        Args:
            filename: Document filename
            content: Optional document content for deeper analysis
            
        Returns:
            Category name or None if no match
        """
        filename_lower = filename.lower()
        
        # Check filename patterns for each category
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.match(pattern, filename_lower, re.IGNORECASE):
                    return category
        
        # If content provided, analyze for category hints
        if content:
            content_lower = content.lower()
            
            # TDD session reports
            if "tdd session" in content_lower or "test-driven development" in content_lower:
                return DocumentCategory.REPORTS
            
            # Planning documents
            if "definition of ready" in content_lower or "definition of done" in content_lower:
                return DocumentCategory.PLANNING
            
            # Analysis documents
            if "architecture" in content_lower[:500] or "design pattern" in content_lower[:500]:
                return DocumentCategory.ANALYSIS
        
        return None
    
    def organize_document(
        self, 
        source_path: Path, 
        category: Optional[str] = None,
        dry_run: bool = False
    ) -> Tuple[Optional[Path], str]:
        """
        Organize a document into its proper category.
        
        Args:
            source_path: Path to document to organize
            category: Target category (auto-detected if None)
            dry_run: If True, only return target path without moving
            
        Returns:
            Tuple of (new_path, message)
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            return None, f"Source file not found: {source_path}"
        
        # Detect category if not provided
        if category is None:
            # Try to read content for detection, handle encoding errors gracefully
            content = None
            if source_path.stat().st_size < 1_000_000:
                try:
                    content = source_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # Try with latin-1 encoding as fallback
                    try:
                        content = source_path.read_text(encoding='latin-1')
                    except Exception:
                        # Skip content detection if encoding fails
                        content = None
            category = self.detect_category(source_path.name, content)
        
        if category is None:
            return None, f"Could not detect category for: {source_path.name}"
        
        # Validate category
        if category not in DocumentCategory.all_categories():
            return None, f"Invalid category: {category}"
        
        # Build target path
        target_dir = self.documents_path / category
        target_path = target_dir / source_path.name
        
        # Handle collisions with timestamp suffix
        if target_path.exists() and target_path != source_path:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            stem = source_path.stem
            suffix = source_path.suffix
            target_path = target_dir / f"{stem}-{timestamp}{suffix}"
        
        # Dry run - just return target path
        if dry_run:
            return target_path, f"Would move: {source_path.name} → {category}/"
        
        # Move the file
        try:
            # Skip if already in correct location
            if source_path.parent == target_dir:
                return target_path, f"Already organized: {source_path.name} in {category}/"
            
            shutil.move(str(source_path), str(target_path))
            return target_path, f"Organized: {source_path.name} → {category}/"
        except Exception as e:
            return None, f"Error moving {source_path.name}: {str(e)}"
    
    def organize_directory(
        self, 
        directory: Path,
        recursive: bool = True,
        dry_run: bool = False
    ) -> Dict[str, List[str]]:
        """
        Organize all documents in a directory.
        
        Args:
            directory: Directory to scan
            recursive: If True, scan subdirectories
            dry_run: If True, preview without moving files
            
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        directory = Path(directory)
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        # Get markdown files
        pattern = "**/*.md" if recursive else "*.md"
        md_files = list(directory.glob(pattern))
        
        for md_file in md_files:
            # Skip README files
            if md_file.name.upper() == "README.MD":
                results["skipped"].append(f"Skipped README: {md_file.name}")
                continue
            
            # Skip INDEX.md files
            if md_file.name.upper() == "INDEX.MD":
                results["skipped"].append(f"Skipped INDEX: {md_file.name}")
                continue
            
            # Organize the file
            new_path, message = self.organize_document(md_file, dry_run=dry_run)
            
            if new_path:
                results["success"].append(message)
            else:
                results["failed"].append(message)
        
        return results
    
    def generate_category_index(self, category: str) -> str:
        """
        Generate an index of all documents in a category.
        
        Args:
            category: Category name
            
        Returns:
            Markdown-formatted index
        """
        if category not in DocumentCategory.all_categories():
            return f"Invalid category: {category}"
        
        category_path = self.documents_path / category
        
        if not category_path.exists():
            return f"Category directory not found: {category}"
        
        # Get all markdown files
        md_files = sorted(category_path.glob("*.md"))
        
        # Build index
        lines = [
            f"# {category.replace('-', ' ').title()} Index",
            "",
            f"**Total Documents:** {len(md_files)}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]
        
        if not md_files:
            lines.append("*No documents in this category yet.*")
        else:
            # Group by date if filenames have dates
            grouped = {}
            ungrouped = []
            
            for md_file in md_files:
                # Try to extract date from filename (YYYY-MM-DD or YYYYMMDD)
                date_match = re.search(r'(\d{4})-?(\d{2})-?(\d{2})', md_file.name)
                if date_match:
                    date_key = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    if date_key not in grouped:
                        grouped[date_key] = []
                    grouped[date_key].append(md_file)
                else:
                    ungrouped.append(md_file)
            
            # Add grouped documents
            for date in sorted(grouped.keys(), reverse=True):
                lines.append(f"## {date}")
                lines.append("")
                for md_file in sorted(grouped[date]):
                    lines.append(f"- [{md_file.name}](./{md_file.name})")
                lines.append("")
            
            # Add ungrouped documents
            if ungrouped:
                lines.append("## Other Documents")
                lines.append("")
                for md_file in sorted(ungrouped):
                    lines.append(f"- [{md_file.name}](./{md_file.name})")
                lines.append("")
        
        return "\n".join(lines)
    
    def update_all_indexes(self) -> Dict[str, str]:
        """
        Update indexes for all categories.
        
        Returns:
            Dictionary mapping category names to index file paths
        """
        results = {}
        
        for category in DocumentCategory.all_categories():
            index_content = self.generate_category_index(category)
            index_path = self.documents_path / category / "INDEX.md"
            
            try:
                index_path.write_text(index_content, encoding='utf-8')
                results[category] = str(index_path)
            except Exception as e:
                results[category] = f"Error: {str(e)}"
        
        return results
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get organization statistics.
        
        Returns:
            Dictionary with counts per category and totals
        """
        stats = {
            "categories": {},
            "total_documents": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        for category in DocumentCategory.all_categories():
            category_path = self.documents_path / category
            if category_path.exists():
                # Count only actual documents (exclude INDEX.md and README.md)
                all_md_files = list(category_path.glob("*.md"))
                count = len([f for f in all_md_files 
                           if f.name.upper() not in ["INDEX.MD", "README.MD"]])
                stats["categories"][category] = count
                stats["total_documents"] += count
            else:
                stats["categories"][category] = 0
        
        return stats


# Convenience function for quick organization
def organize_brain_documents(brain_path: Path, dry_run: bool = False) -> Dict[str, any]:
    """
    Organize all documents in cortex-brain/documents/ recursively.
    
    Args:
        brain_path: Path to cortex-brain directory
        dry_run: If True, preview without moving files
        
    Returns:
        Organization results and statistics
    """
    organizer = DocumentOrganizer(brain_path)
    documents_root = brain_path / "documents"
    
    # Organize all documents
    results = organizer.organize_directory(documents_root, recursive=True, dry_run=dry_run)
    
    # Update indexes if not dry run
    if not dry_run:
        organizer.update_all_indexes()
    
    # Get statistics
    stats = organizer.get_statistics()
    
    return {
        "results": results,
        "statistics": stats
    }
