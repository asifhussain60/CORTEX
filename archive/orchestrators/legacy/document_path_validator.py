"""
Document Path Validator - Feature 3
Enforces cortex-brain/documents/{category}/ structure and prevents root-level docs

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class DocumentCategory(Enum):
    """Valid document categories"""
    REPORTS = "reports"
    ANALYSIS = "analysis"
    SUMMARIES = "summaries"
    INVESTIGATIONS = "investigations"
    PLANNING = "planning"
    IMPLEMENTATION_GUIDES = "implementation-guides"


@dataclass
class ValidationResult:
    """Result of path validation"""
    valid: bool
    reason: str = ""
    suggested_path: Optional[str] = None
    should_block_creation: bool = False
    category: Optional[DocumentCategory] = None
    
    def __post_init__(self):
        if not self.valid:
            self.should_block_creation = True


class PatternMatcher:
    """
    Regex pattern matcher for document paths
    
    Handles:
    - Forbidden patterns (root-level, .review folders)
    - Required patterns (cortex-brain/documents structure)
    - Cross-platform path normalization
    """
    
    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        r"^CORTEX/[^/]+\.md$",              # Root-level CORTEX/file.md
        r"\.review[/\\]",                   # Any .review/ folder (Unix or Windows)
        r"^[^/]*summary\.md$",              # summary.md at root
        r"^[^/]+\.md$",                     # Any .md at root
    ]
    
    # Required pattern for valid paths
    REQUIRED_PATTERN = r"^cortex-brain/documents/(reports|analysis|summaries|investigations|planning|implementation-guides)/[a-z0-9][a-z0-9-]*\.md$"
    
    @staticmethod
    def matches_any_forbidden(path: str) -> tuple[bool, str]:
        """
        Check if path matches any forbidden pattern
        
        Returns:
            Tuple of (matches, pattern_type) where pattern_type helps with error messages
        """
        # Check for .review first (before normalization)
        if ".review" in path:
            return (True, "review")
        
        normalized = PatternMatcher._normalize_path(path)
        
        # Check CORTEX root-level
        if re.match(r"^CORTEX/[^/]+\.md$", normalized):
            return (True, "cortex_root")
        
        # Check generic root-level
        if re.match(r"^[^/]+\.md$", normalized):
            return (True, "root")
        
        # Check summary at root
        if re.match(r"^[^/]*summary\.md$", normalized):
            return (True, "root_summary")
        
        return (False, "")
    
    @staticmethod
    def matches_required(path: str) -> bool:
        """Check if path matches required pattern"""
        normalized = PatternMatcher._normalize_path(path)
        return bool(re.match(PatternMatcher.REQUIRED_PATTERN, normalized))
    
    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path to Unix-style forward slashes"""
        # Convert Windows backslashes to forward slashes
        normalized = path.replace("\\", "/")
        
        # Remove Windows drive letters for pattern matching
        normalized = re.sub(r"^[A-Z]:/", "", normalized)
        
        # Remove absolute Unix paths for pattern matching
        if normalized.startswith("/Users/") or normalized.startswith("/home/"):
            # Extract relative path after workspace
            match = re.search(r"/(CORTEX|cortex-brain)/", normalized)
            if match:
                normalized = normalized[match.start() + 1:]
        
        return normalized


class DocumentPathValidator:
    """
    Validates document paths against CORTEX organization rules
    
    Rules:
    - NO root-level .md files (CORTEX/summary.md)
    - NO .review/ folders in user repos
    - YES cortex-brain/documents/{category}/filename.md
    - Filenames must be lowercase-hyphenated
    
    Usage:
        validator = DocumentPathValidator()
        result = validator.validate_path("summary.md")
        if not result.valid:
            print(f"Error: {result.reason}")
            print(f"Use instead: {result.suggested_path}")
    """
    
    # Category descriptions for user guidance
    CATEGORY_DESCRIPTIONS = {
        DocumentCategory.REPORTS: "Status reports, test results, validation reports",
        DocumentCategory.ANALYSIS: "Code analysis, architecture analysis, performance analysis",
        DocumentCategory.SUMMARIES: "Project summaries, progress summaries, session summaries",
        DocumentCategory.INVESTIGATIONS: "Bug investigations, RCA documents, troubleshooting",
        DocumentCategory.PLANNING: "Feature plans, ADO items, roadmaps, enhancement plans",
        DocumentCategory.IMPLEMENTATION_GUIDES: "How-to guides, setup tutorials, user guides"
    }
    
    # Keywords for category detection
    CATEGORY_KEYWORDS = {
        DocumentCategory.REPORTS: ["test", "results", "report", "status", "validation"],
        DocumentCategory.ANALYSIS: ["analysis", "review", "architecture", "performance", "code"],
        DocumentCategory.SUMMARIES: ["summary", "recap", "overview", "progress"],
        DocumentCategory.INVESTIGATIONS: ["bug", "investigation", "rca", "troubleshoot", "incident"],
        DocumentCategory.PLANNING: ["plan", "feature", "roadmap", "enhancement", "ado", "story"],
        DocumentCategory.IMPLEMENTATION_GUIDES: ["guide", "tutorial", "howto", "setup", "install"]
    }
    
    def __init__(self):
        """Initialize validator"""
        self.matcher = PatternMatcher()
    
    def validate_path(self, path: str) -> ValidationResult:
        """
        Validate document path against organization rules
        
        Args:
            path: File path to validate
            
        Returns:
            ValidationResult with validity, reason, and suggestions
        """
        # Check forbidden patterns first
        is_forbidden, pattern_type = self.matcher.matches_any_forbidden(path)
        if is_forbidden:
            return self._handle_forbidden_path(path, pattern_type)
        
        # Check required pattern
        if self.matcher.matches_required(path):
            return ValidationResult(valid=True)
        
        # Path doesn't match required pattern
        return self._handle_invalid_path(path)
    
    def _handle_forbidden_path(self, path: str, pattern_type: str) -> ValidationResult:
        """Handle paths matching forbidden patterns"""
        # Detect specific forbidden pattern
        if pattern_type == "review":
            reason = (
                "Files in .review/ folders are forbidden. "
                "CORTEX documents must be in cortex-brain/documents/{category}/. "
                f"Available categories: {', '.join(c.value for c in DocumentCategory)}"
            )
        elif pattern_type == "cortex_root":
            reason = (
                "Root-level documents in CORTEX/ are forbidden. "
                "Use cortex-brain/documents/{category}/ instead. "
                f"Available categories: {', '.join(c.value for c in DocumentCategory)}"
            )
        else:
            reason = (
                "Root-level .md files are forbidden. "
                "Documents must be in cortex-brain/documents/{category}/. "
                f"Available categories: {', '.join(c.value for c in DocumentCategory)}"
            )
        
        # Generate suggestion
        filename = Path(path).name
        suggested_path = self._suggest_path(filename)
        
        return ValidationResult(
            valid=False,
            reason=reason,
            suggested_path=suggested_path
        )
    
    def _handle_invalid_path(self, path: str) -> ValidationResult:
        """Handle paths not matching required pattern"""
        normalized = self.matcher._normalize_path(path)
        
        # Check if in cortex-brain but wrong structure
        if normalized.startswith("cortex-brain/documents/"):
            if normalized.count("/") < 3:
                reason = (
                    "Files cannot be directly in cortex-brain/documents/. "
                    "A category subdirectory is required. "
                    f"Valid categories: {', '.join(c.value for c in DocumentCategory)}"
                )
            else:
                # Invalid category or filename format
                parts = normalized.split("/")
                category = parts[2] if len(parts) > 2 else ""
                filename = parts[-1] if parts else ""
                
                valid_categories = [c.value for c in DocumentCategory]
                if category not in valid_categories:
                    reason = (
                        f"Invalid category '{category}'. "
                        f"Valid categories: {', '.join(valid_categories)}"
                    )
                elif not re.match(r"^[a-z0-9][a-z0-9-]*\.md$", filename):
                    reason = (
                        f"Invalid filename format '{filename}'. "
                        "Filenames must be lowercase-hyphenated (e.g., my-document.md)"
                    )
                else:
                    reason = "Path does not match required structure"
        else:
            reason = (
                "Documents must be in cortex-brain/documents/{category}/. "
                f"Valid categories: {', '.join(c.value for c in DocumentCategory)}"
            )
        
        # Generate suggestion
        filename = Path(path).name
        suggested_path = self._suggest_path(filename)
        
        return ValidationResult(
            valid=False,
            reason=reason,
            suggested_path=suggested_path
        )
    
    def _suggest_path(self, filename: str) -> str:
        """
        Suggest correct path for a filename
        
        Args:
            filename: Original filename
            
        Returns:
            Suggested path in cortex-brain/documents/{category}/
        """
        # Normalize filename to lowercase-hyphenated (also normalizes path separators)
        normalized_filename = self._normalize_filename(filename)
        
        # Detect category from filename
        category = self.detect_category(normalized_filename)
        
        return f"cortex-brain/documents/{category.value}/{normalized_filename}"
    
    def _normalize_filename(self, filename: str) -> str:
        """
        Normalize filename to lowercase-hyphenated format
        
        Args:
            filename: Original filename
            
        Returns:
            Normalized filename
        """
        # Convert Windows backslashes to forward slashes first
        filename = filename.replace("\\", "/")
        
        # Remove path if present
        filename = Path(filename).name
        
        # Split on extension
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "md")
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace underscores and spaces with hyphens
        name = name.replace("_", "-")
        name = name.replace(" ", "-")
        
        # Remove multiple consecutive hyphens
        name = re.sub(r"-+", "-", name)
        
        # Remove leading/trailing hyphens
        name = name.strip("-")
        
        return f"{name}.{ext}"
    
    def detect_category(self, filename: str) -> DocumentCategory:
        """
        Detect appropriate category from filename keywords
        
        Args:
            filename: Filename to analyze
            
        Returns:
            DocumentCategory (defaults to SUMMARIES if ambiguous)
        """
        filename_lower = filename.lower()
        
        # Score each category by keyword matches
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in filename_lower)
            if score > 0:
                scores[category] = score
        
        # Return highest scoring category
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default to SUMMARIES for ambiguous files
        return DocumentCategory.SUMMARIES
    
    def validate_before_creation(self, path: str) -> ValidationResult:
        """
        Validation hook for orchestrators before file creation
        
        Args:
            path: Path to validate before creating file
            
        Returns:
            ValidationResult with should_block_creation flag
        """
        return self.validate_path(path)
    
    def get_category_suggestions(self, description: str) -> List[DocumentCategory]:
        """
        Get category suggestions based on description
        
        Args:
            description: Description of document content
            
        Returns:
            List of suggested categories (ranked by relevance)
        """
        description_lower = description.lower()
        
        # Score categories
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                scores[category] = score
        
        # Return sorted by score (highest first)
        if scores:
            sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [cat for cat, _ in sorted_categories]
        
        # Return all categories if no matches
        return list(DocumentCategory)


if __name__ == "__main__":
    # Example usage
    validator = DocumentPathValidator()
    
    print("Testing Document Path Validator\n")
    print("=" * 60)
    
    test_paths = [
        "summary.md",
        "CORTEX/summary.md",
        ".review/analysis.md",
        "cortex-brain/documents/reports/test-results.md",
        "cortex-brain/documents/invalid-category/file.md",
        "cortex-brain/documents/reports/MyTestResults.md"
    ]
    
    for path in test_paths:
        result = validator.validate_path(path)
        print(f"\nPath: {path}")
        print(f"Valid: {result.valid}")
        if not result.valid:
            print(f"Reason: {result.reason}")
            print(f"Suggested: {result.suggested_path}")
