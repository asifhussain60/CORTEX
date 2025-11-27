"""
CORTEX Documentation Governance System
Version: 1.0
Purpose: Prevent duplicate documentation, enforce canonical names, maintain structure integrity

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import yaml
import hashlib


@dataclass
class DocumentMetadata:
    """Metadata for a documentation file"""
    path: Path
    category: str
    title: str
    created: datetime
    modified: datetime
    word_count: int
    checksum: str


@dataclass
class DuplicateMatch:
    """Represents a potential duplicate document"""
    existing_path: Path
    similarity_score: float
    algorithm: str
    recommendation: str


class DocumentGovernance:
    """
    Documentation governance system that prevents duplicates, enforces canonical names,
    and maintains structure integrity.
    
    Core Principles:
    1. Search before creating
    2. Update over duplicate
    3. Canonical names enforced
    4. Index awareness maintained
    5. Consistency enforcement
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize documentation governance system.
        
        Args:
            cortex_root: Root path of CORTEX installation (auto-detected if None)
        """
        self.cortex_root = cortex_root or self._detect_cortex_root()
        self.brain_path = self.cortex_root / "cortex-brain"
        self.documents_path = self.brain_path / "documents"
        self.modules_path = self.cortex_root / ".github" / "prompts" / "modules"
        
        # Load governance rules
        self.rules = self._load_governance_rules()
        
        # Document index (cached)
        self._document_index: Optional[Dict[str, DocumentMetadata]] = None
    
    def _detect_cortex_root(self) -> Path:
        """Auto-detect CORTEX root directory"""
        current = Path(__file__).resolve()
        
        # Walk up until we find cortex-brain/
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("Could not detect CORTEX root directory")
    
    def _load_governance_rules(self) -> Dict:
        """Load governance rules from YAML configuration"""
        governance_file = self.brain_path / "documents" / "governance" / "documentation-governance.yaml"
        
        if not governance_file.exists():
            raise FileNotFoundError(f"Governance rules not found: {governance_file}")
        
        with open(governance_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_document_creation(
        self, 
        proposed_path: Path, 
        content: str
    ) -> Tuple[bool, List[str], List[DuplicateMatch]]:
        """
        Validate that a new document can be created without violating governance rules.
        
        Args:
            proposed_path: Proposed file path for new document
            content: Content of the proposed document
        
        Returns:
            Tuple of (is_valid, error_messages, duplicate_matches)
        """
        errors = []
        duplicates = []
        
        # Rule 1: Validate category
        category_valid, category_error = self._validate_category(proposed_path)
        if not category_valid:
            errors.append(category_error)
        
        # Rule 2: Validate naming pattern
        pattern_valid, pattern_error = self._validate_naming_pattern(proposed_path)
        if not pattern_valid:
            errors.append(pattern_error)
        
        # Rule 3: Check for duplicates
        if self.rules['governance_rules']['search_before_create']['enabled']:
            duplicates = self.find_duplicates(proposed_path, content)
            
            if duplicates:
                # Filter by threshold
                threshold = self.rules['governance_rules']['search_before_create']['similarity_threshold']
                high_similarity = [d for d in duplicates if d.similarity_score >= threshold]
                
                if high_similarity:
                    errors.append(
                        f"Duplicate documents detected (similarity >= {threshold:.0%}): "
                        f"{', '.join(str(d.existing_path.relative_to(self.cortex_root)) for d in high_similarity)}"
                    )
        
        # Rule 4: Validate canonical name (for module guides)
        if self._is_module_guide(proposed_path):
            canonical_valid, canonical_error = self._validate_canonical_name(proposed_path)
            if not canonical_valid:
                errors.append(canonical_error)
        
        # Rule 5: Check index references
        index_valid, index_warnings = self._check_index_references(proposed_path)
        if not index_valid:
            errors.extend(index_warnings)
        
        is_valid = len(errors) == 0
        return is_valid, errors, duplicates
    
    def _validate_category(self, path: Path) -> Tuple[bool, str]:
        """Validate that the document is in a valid category"""
        try:
            rel_path = path.relative_to(self.documents_path)
            category = rel_path.parts[0] if rel_path.parts else None
        except ValueError:
            # Not in documents path - check if module guide
            if self._is_module_guide(path):
                return True, ""
            return False, f"Document must be in cortex-brain/documents/ or .github/prompts/modules/"
        
        valid_categories = self.rules['documentation_structure']['fixed_categories'].keys()
        
        if category not in valid_categories:
            return False, f"Invalid category '{category}'. Valid categories: {', '.join(valid_categories)}"
        
        return True, ""
    
    def _validate_naming_pattern(self, path: Path) -> Tuple[bool, str]:
        """Validate that the filename follows the category's naming pattern"""
        try:
            rel_path = path.relative_to(self.documents_path)
            category = rel_path.parts[0] if rel_path.parts else None
        except ValueError:
            # Module guide - naming is flexible
            return True, ""
        
        if not category:
            return False, "Could not determine category"
        
        category_rules = self.rules['documentation_structure']['fixed_categories'].get(category)
        if not category_rules:
            return True, ""  # No specific pattern defined
        
        pattern = category_rules.get('naming_pattern')
        if not pattern:
            return True, ""  # No pattern enforcement
        
        filename = path.name
        
        # Pattern validation (simplified - could be enhanced with regex)
        if category == 'reports' and not re.match(r'^[A-Z\-]+\d{8}.*\.md$', filename, re.IGNORECASE):
            return False, f"Report filename should follow pattern: [TYPE]-[DATE]-[DESCRIPTION].md"
        
        if category == 'planning' and not re.match(r'^(PLAN|ADO)-.*\.md$', filename):
            return False, f"Planning filename should follow pattern: PLAN-[DATE]-[FEATURE].md or ADO-[ID]-*.md"
        
        return True, ""
    
    def _is_module_guide(self, path: Path) -> bool:
        """Check if path is a module guide"""
        try:
            rel_path = path.relative_to(self.modules_path)
            return True
        except ValueError:
            return False
    
    def _validate_canonical_name(self, path: Path) -> Tuple[bool, str]:
        """Validate that module guide uses canonical name"""
        if not self.rules['governance_rules']['canonical_names']['enabled']:
            return True, ""
        
        canonical_names = self.rules['documentation_structure']['module_guides']['canonical_names']
        filename = path.name
        
        # Check if filename matches any canonical name
        is_canonical = filename in canonical_names.values()
        
        if not is_canonical:
            # Try to find similar canonical name
            for topic, canonical in canonical_names.items():
                if topic in filename.lower() or filename in canonical:
                    return False, f"Use canonical name '{canonical}' instead of '{filename}'"
        
        return True, ""
    
    def _check_index_references(self, path: Path) -> Tuple[bool, List[str]]:
        """Check if document should be referenced in index files"""
        warnings = []
        
        if not self.rules['governance_rules']['index_awareness']['enabled']:
            return True, warnings
        
        # Module guides should be referenced in CORTEX.prompt.md
        if self._is_module_guide(path):
            cortex_prompt = self.cortex_root / ".github" / "prompts" / "CORTEX.prompt.md"
            
            if cortex_prompt.exists():
                with open(cortex_prompt, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if path.name not in content:
                    warnings.append(f"Module guide '{path.name}' not referenced in CORTEX.prompt.md")
        
        return len(warnings) == 0, warnings
    
    def find_duplicates(
        self, 
        proposed_path: Path, 
        content: str
    ) -> List[DuplicateMatch]:
        """
        Find potential duplicate documents using multiple algorithms.
        
        Args:
            proposed_path: Path of proposed new document
            content: Content of proposed document
        
        Returns:
            List of duplicate matches sorted by similarity score (highest first)
        """
        duplicates = []
        
        # Build document index if not cached
        if self._document_index is None:
            self._document_index = self._build_document_index()
        
        # Algorithm 1: Exact filename match
        filename = proposed_path.name
        for doc_path, metadata in self._document_index.items():
            if Path(doc_path).name == filename:
                duplicates.append(DuplicateMatch(
                    existing_path=Path(doc_path),
                    similarity_score=1.0,
                    algorithm="exact_filename_match",
                    recommendation=f"File with same name exists: {doc_path}"
                ))
        
        # Algorithm 2: Title similarity
        proposed_title = self._extract_title(content)
        if proposed_title:
            for doc_path, metadata in self._document_index.items():
                title_similarity = self._calculate_title_similarity(proposed_title, metadata.title)
                
                if title_similarity >= 0.80:  # 80% threshold for titles
                    duplicates.append(DuplicateMatch(
                        existing_path=Path(doc_path),
                        similarity_score=title_similarity,
                        algorithm="title_similarity",
                        recommendation=f"Similar title found: '{metadata.title}' in {doc_path}"
                    ))
        
        # Algorithm 3: Keyword overlap
        proposed_keywords = self._extract_keywords(content)
        for doc_path, metadata in self._document_index.items():
            # Read existing document for keyword comparison
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                existing_keywords = self._extract_keywords(existing_content)
                keyword_overlap = self._calculate_keyword_overlap(proposed_keywords, existing_keywords)
                
                if keyword_overlap >= 0.60:  # 60% threshold for keywords
                    duplicates.append(DuplicateMatch(
                        existing_path=Path(doc_path),
                        similarity_score=keyword_overlap,
                        algorithm="keyword_overlap",
                        recommendation=f"High keyword overlap ({keyword_overlap:.0%}) with {doc_path}"
                    ))
            except Exception:
                continue  # Skip files that can't be read
        
        # Sort by similarity score (highest first)
        duplicates.sort(key=lambda d: d.similarity_score, reverse=True)
        
        return duplicates
    
    def _build_document_index(self) -> Dict[str, DocumentMetadata]:
        """Build index of all existing documents"""
        index = {}
        
        # Index documents in cortex-brain/documents/
        if self.documents_path.exists():
            for md_file in self.documents_path.rglob("*.md"):
                if md_file.is_file():
                    try:
                        metadata = self._extract_metadata(md_file)
                        index[str(md_file)] = metadata
                    except Exception:
                        continue  # Skip files that can't be processed
        
        # Index module guides in .github/prompts/modules/
        if self.modules_path.exists():
            for md_file in self.modules_path.glob("*.md"):
                if md_file.is_file():
                    try:
                        metadata = self._extract_metadata(md_file)
                        index[str(md_file)] = metadata
                    except Exception:
                        continue
        
        return index
    
    def _extract_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract metadata from a document file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stats = file_path.stat()
        
        return DocumentMetadata(
            path=file_path,
            category=self._determine_category(file_path),
            title=self._extract_title(content),
            created=datetime.fromtimestamp(stats.st_ctime),
            modified=datetime.fromtimestamp(stats.st_mtime),
            word_count=len(content.split()),
            checksum=hashlib.md5(content.encode()).hexdigest()
        )
    
    def _determine_category(self, file_path: Path) -> str:
        """Determine category from file path"""
        try:
            rel_path = file_path.relative_to(self.documents_path)
            return rel_path.parts[0] if rel_path.parts else "unknown"
        except ValueError:
            if self._is_module_guide(file_path):
                return "module_guides"
            return "unknown"
    
    def _extract_title(self, content: str) -> str:
        """Extract title from document content"""
        # Look for first H1 heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            # Remove emojis and icons
            title = re.sub(r'[🧠🎯⚠️💬📝🔍]', '', match.group(1))
            return title.strip()
        
        return ""
    
    def _extract_keywords(self, content: str) -> set:
        """Extract keywords from document content"""
        # Simple keyword extraction (could be enhanced with NLP)
        # Remove markdown syntax, code blocks, and special characters
        text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Extract words, filter common words
        words = text.lower().split()
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = {w for w in words if len(w) > 3 and w not in stopwords}
        
        return keywords
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        if not title1 or not title2:
            return 0.0
        
        # Normalize titles
        t1 = set(title1.lower().split())
        t2 = set(title2.lower().split())
        
        # Jaccard similarity
        intersection = len(t1 & t2)
        union = len(t1 | t2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_keyword_overlap(self, keywords1: set, keywords2: set) -> float:
        """Calculate keyword overlap between two documents"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def suggest_consolidation(
        self, 
        duplicates: List[DuplicateMatch]
    ) -> List[str]:
        """
        Suggest consolidation strategies for duplicate documents.
        
        Args:
            duplicates: List of duplicate matches
        
        Returns:
            List of consolidation suggestions
        """
        suggestions = []
        
        for dup in duplicates:
            category = self._determine_category(dup.existing_path)
            strategy = self.rules['merge_strategies'].get(
                self._get_strategy_key(category), 
                {}
            ).get('strategy', 'update_in_place')
            
            if strategy == 'update_in_place':
                suggestions.append(
                    f"Update existing document: {dup.existing_path.relative_to(self.cortex_root)}"
                )
            elif strategy == 'append_phases':
                suggestions.append(
                    f"Append new phase to: {dup.existing_path.relative_to(self.cortex_root)}"
                )
            elif strategy == 'create_timestamped':
                suggestions.append(
                    f"Create timestamped version alongside: {dup.existing_path.relative_to(self.cortex_root)}"
                )
            else:
                suggestions.append(
                    f"Consider merging with: {dup.existing_path.relative_to(self.cortex_root)}"
                )
        
        return suggestions
    
    def _get_strategy_key(self, category: str) -> str:
        """Map category to merge strategy key"""
        mapping = {
            'module_guides': 'module_guides',
            'implementation-guides': 'implementation_guides',
            'reports': 'reports',
            'analysis': 'analysis'
        }
        return mapping.get(category, 'reports')
    
    def get_canonical_name(self, topic: str) -> Optional[str]:
        """Get canonical filename for a topic"""
        canonical_names = self.rules['documentation_structure']['module_guides']['canonical_names']
        return canonical_names.get(topic.lower())
    
    def invalidate_cache(self):
        """Invalidate the document index cache"""
        self._document_index = None
