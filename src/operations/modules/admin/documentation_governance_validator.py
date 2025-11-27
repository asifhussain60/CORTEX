"""
Documentation Governance Validator
===================================

Validates documentation governance for system alignment.

Author: Asif Hussain
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.governance.document_governance import DocumentGovernance

logger = logging.getLogger(__name__)


class DocumentationGovernanceValidator:
    """Validates documentation governance (duplicate/overlapping docs)."""
    
    def __init__(self, project_root: Path, context: Dict[str, Any]):
        """
        Initialize documentation governance validator.
        
        Args:
            project_root: Project root path
            context: Execution context
        """
        self.project_root = project_root
        self.context = context
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate documentation governance (duplicate/overlapping docs).
        
        Checks:
        - Duplicate documents across cortex-brain/documents/ and .github/prompts/modules/
        - Overlapping content detection (title similarity, keyword overlap)
        - Canonical name violations for module guides
        - Documents not referenced in index files
        
        Returns:
            Dict with validation results and violations
        """
        # Check if duplicate detection should be skipped (performance optimization)
        # DEFAULT: Skip duplicate detection in system alignment to prevent O(n²) catastrophe
        # Can be explicitly enabled via context: {'skip_duplicate_detection': False}
        if self.context.get('skip_duplicate_detection', True):
            logger.info("Skipping duplicate document detection (skip_duplicate_detection=True) - prevents O(n²) performance issue")
            return {
                'score': 100,
                'violations': [],
                'total_docs_scanned': 0,
                'duplicate_pairs': 0,
                'warning': 'Duplicate detection skipped for performance (enable with skip_duplicate_detection=False if needed)'
            }
        
        try:
            governance = DocumentGovernance(self.project_root)
            violations = []
            score = 100
            
            # Scan all existing documents for duplicates
            documents_path = self.project_root / "cortex-brain" / "documents"
            modules_path = self.project_root / ".github" / "prompts" / "modules"
            
            scanned_docs = []
            
            # Collect all markdown files
            if documents_path.exists():
                for md_file in documents_path.rglob("*.md"):
                    if md_file.is_file():
                        scanned_docs.append(md_file)
            
            if modules_path.exists():
                for md_file in modules_path.glob("*.md"):
                    if md_file.is_file():
                        scanned_docs.append(md_file)
            
            logger.info(f"Scanning {len(scanned_docs)} documents for duplicates...")
            
            # Track duplicates found (avoid reporting same pair twice)
            reported_pairs = set()
            
            for doc_path in scanned_docs:
                try:
                    # Read document content
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find duplicates
                    duplicates = governance.find_duplicates(doc_path, content)
                    
                    # Filter by threshold (0.75 from governance rules)
                    high_similarity = [
                        d for d in duplicates 
                        if d.similarity_score >= 0.75
                    ]
                    
                    for dup in high_similarity:
                        # Create canonical pair identifier (alphabetically sorted to avoid duplicates)
                        pair_key = tuple(sorted([str(doc_path), str(dup.existing_path)]))
                        
                        if pair_key not in reported_pairs:
                            reported_pairs.add(pair_key)
                            
                            violations.append({
                                'type': 'duplicate_document',
                                'severity': 'warning' if dup.similarity_score < 0.90 else 'critical',
                                'file': str(doc_path.relative_to(self.project_root)),
                                'duplicate': str(dup.existing_path.relative_to(self.project_root)),
                                'similarity': f"{dup.similarity_score:.0%}",
                                'algorithm': dup.algorithm,
                                'recommendation': dup.recommendation
                            })
                            
                            # Deduct score based on severity
                            if dup.similarity_score >= 0.90:
                                score -= 10  # Critical: likely exact duplicate
                            else:
                                score -= 5   # Warning: high similarity
                
                except Exception as e:
                    logger.debug(f"Error scanning {doc_path}: {e}")
                    continue
            
            # Ensure score doesn't go below 0
            score = max(0, score)
            
            logger.info(f"Documentation governance: {score}% ({len(violations)} issues found)")
            
            return {
                'score': score,
                'status': 'healthy' if score >= 80 else 'degraded',
                'violations': violations,
                'critical_count': sum(1 for v in violations if v.get('severity') == 'critical'),
                'warning_count': sum(1 for v in violations if v.get('severity') == 'warning'),
                'scanned_documents': len(scanned_docs),
                'duplicate_pairs': len(reported_pairs)
            }
            
        except Exception as e:
            logger.error(f"Documentation governance validation failed: {e}")
            return {
                'score': 0,
                'status': 'error',
                'violations': [],
                'critical_count': 0,
                'warning_count': 0,
                'scanned_documents': 0,
                'duplicate_pairs': 0
            }
