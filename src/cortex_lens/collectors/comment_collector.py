"""
Comment Collector

Extracts and categorizes code comments for documentation and narrative generation.
Uses pypdf for PDF document extraction when applicable.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from .base import BaseCollector

logger = logging.getLogger(__name__)


class CommentCollector(BaseCollector):
    """
    Collect and categorize code comments
    
    Extracts:
    - Docstrings (classes, functions, modules)
    - Inline comments
    - TODO/FIXME/HACK markers
    - Regulatory keywords (GDPR, HIPAA, PCI, etc.)
    - Business logic annotations
    - API documentation (OpenAPI, JSDoc, XML docs)
    
    Used for:
    - Narrative generation
    - Business rule extraction
    - Compliance auditing
    - Documentation quality assessment
    """
    
    # Comment patterns by language
    COMMENT_PATTERNS = {
        'python': {
            'single': r'#\s*(.+)$',
            'docstring': r'"""([^"]*?)"""|\'\'\'([^\']*?)\'\'\'',
            'multiline_start': None,  # Python uses docstrings
        },
        'csharp': {
            'single': r'//\s*(.+)$',
            'multiline_start': r'/\*',
            'multiline_end': r'\*/',
            'xml_doc': r'///\s*(.+)$',
        },
        'javascript': {
            'single': r'//\s*(.+)$',
            'multiline_start': r'/\*',
            'multiline_end': r'\*/',
            'jsdoc': r'/\*\*([^*]*(?:\*(?!/)[^*]*)*)\*/',
        },
        'sql': {
            'single': r'--\s*(.+)$',
            'multiline_start': r'/\*',
            'multiline_end': r'\*/',
        }
    }
    
    # TODO/FIXME markers
    MARKER_PATTERNS = {
        'todo': r'\b(TODO|To Do|TO-DO)[\s:]+(.+)',
        'fixme': r'\b(FIXME|FIX ME|FIX-ME)[\s:]+(.+)',
        'hack': r'\b(HACK|WORKAROUND)[\s:]+(.+)',
        'note': r'\b(NOTE|NB|N\.B\.)[\s:]+(.+)',
        'warning': r'\b(WARNING|WARN|CAUTION)[\s:]+(.+)',
        'deprecated': r'\b(DEPRECATED|OBSOLETE)[\s:]+(.+)',
        'review': r'\b(REVIEW|NEEDS REVIEW)[\s:]+(.+)',
    }
    
    # Regulatory and compliance keywords
    REGULATORY_KEYWORDS = {
        'gdpr': ['personal data', 'data subject', 'consent', 'right to erasure', 
                 'data protection', 'gdpr', 'privacy', 'pii'],
        'hipaa': ['phi', 'protected health', 'hipaa', 'medical record', 
                  'patient data', 'healthcare'],
        'pci': ['pci', 'card data', 'payment card', 'credit card', 'cvv', 
                'cardholder', 'pci-dss'],
        'sox': ['sox', 'sarbanes', 'financial control', 'audit trail', 
                'segregation of duties'],
        'security': ['encryption', 'authentication', 'authorization', 'sensitive',
                    'credential', 'secret', 'token', 'password', 'api key'],
    }
    
    # Business logic indicators
    BUSINESS_PATTERNS = {
        'rule': r'\b(business rule|rule:|policy:|requirement:)\s*(.+)',
        'validation': r'\b(validate|validation|must be|should be|required)\s*(.+)',
        'calculation': r'\b(calculate|formula|algorithm|compute)\s*(.+)',
        'workflow': r'\b(workflow|process:|step \d|phase \d)\s*(.+)',
    }
    
    @property
    def name(self) -> str:
        return 'comment'
    
    @property
    def description(self) -> str:
        return 'Extracts and categorizes code comments for narrative generation'
    
    @property
    def required_for(self) -> list:
        return []  # Optional for all types, but useful
    
    def collect(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect comment information
        
        Args:
            repo_path: Repository root
            classification: Classification results
            
        Returns:
            {
                'docstrings': [...],
                'markers': {'todo': [...], 'fixme': [...]},
                'regulatory': {'gdpr': [...], 'hipaa': [...]},
                'business_rules': [...],
                'metrics': {...}
            }
        """
        logger.info("Collecting code comments...")
        
        docstrings = []
        inline_comments = []
        markers = defaultdict(list)
        regulatory = defaultdict(list)
        business_rules = []
        
        # Define file extensions to scan
        extensions = {
            '.py': 'python',
            '.pyw': 'python',
            '.cs': 'csharp',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',  # Similar comment style
            '.tsx': 'javascript',
            '.sql': 'sql',
        }
        
        for ext, lang in extensions.items():
            for file_path in repo_path.rglob(f'*{ext}'):
                if self._should_skip(file_path):
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(file_path.relative_to(repo_path))
                    
                    # Extract docstrings
                    file_docstrings = self._extract_docstrings(content, lang, rel_path)
                    docstrings.extend(file_docstrings)
                    
                    # Extract inline comments
                    file_comments = self._extract_inline_comments(content, lang, rel_path)
                    inline_comments.extend(file_comments)
                    
                    # Find markers (TODO, FIXME, etc.)
                    file_markers = self._find_markers(content, rel_path)
                    for marker_type, items in file_markers.items():
                        markers[marker_type].extend(items)
                    
                    # Find regulatory keywords
                    file_regulatory = self._find_regulatory_keywords(content, rel_path)
                    for reg_type, items in file_regulatory.items():
                        regulatory[reg_type].extend(items)
                    
                    # Extract business rules
                    file_rules = self._extract_business_rules(content, rel_path)
                    business_rules.extend(file_rules)
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
        
        # Calculate metrics
        metrics = {
            'total_docstrings': len(docstrings),
            'total_inline_comments': len(inline_comments),
            'total_markers': sum(len(v) for v in markers.values()),
            'marker_breakdown': {k: len(v) for k, v in markers.items()},
            'regulatory_mentions': {k: len(v) for k, v in regulatory.items()},
            'business_rules_found': len(business_rules),
            'documentation_coverage': self._calculate_doc_coverage(docstrings),
        }
        
        result = {
            'docstrings': docstrings[:100],  # Limit
            'inline_comments': inline_comments[:200],  # Limit
            'markers': dict(markers),
            'regulatory': dict(regulatory),
            'business_rules': business_rules[:50],  # Limit
            'metrics': metrics
        }
        
        logger.info(f"✅ Comments collected: {len(docstrings)} docstrings, "
                   f"{len(inline_comments)} inline, {metrics['total_markers']} markers")
        
        return result
    
    def collect_safe(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            return self.collect(repo_path, classification)
        except Exception as e:
            logger.error(f"Comment collection failed: {e}")
            return {
                'docstrings': [],
                'inline_comments': [],
                'markers': {},
                'regulatory': {},
                'business_rules': [],
                'metrics': {},
                'error': str(e)
            }
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'node_modules', '__pycache__', 'venv', '.venv',
            'dist', 'build', '.git', 'migrations'
        ]
        return any(p in str(file_path) for p in skip_patterns)
    
    def _extract_docstrings(
        self,
        content: str,
        lang: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract docstrings from code"""
        docstrings = []
        
        if lang == 'python':
            # Python docstrings
            pattern = r'(?:class|def)\s+(\w+).*?:\s*(?:\n\s*)?(?:"""([^"]*?)"""|\'\'\'([^\']*?)\'\'\')'
            for match in re.finditer(pattern, content, re.DOTALL):
                name = match.group(1)
                doc = match.group(2) or match.group(3) or ''
                if doc.strip():
                    docstrings.append({
                        'name': name,
                        'docstring': doc.strip()[:500],  # Limit length
                        'file': file_path,
                        'type': 'class/function'
                    })
            
            # Module docstring
            module_match = re.match(r'^[\s]*(?:"""([^"]*?)"""|\'\'\'([^\']*?)\'\'\')', content, re.DOTALL)
            if module_match:
                doc = module_match.group(1) or module_match.group(2) or ''
                if doc.strip():
                    docstrings.append({
                        'name': file_path.split('/')[-1],
                        'docstring': doc.strip()[:500],
                        'file': file_path,
                        'type': 'module'
                    })
        
        elif lang == 'csharp':
            # XML documentation comments
            pattern = r'///\s*<summary>\s*(.*?)\s*</summary>'
            for match in re.finditer(pattern, content, re.DOTALL):
                doc = re.sub(r'///\s*', '', match.group(1))
                if doc.strip():
                    docstrings.append({
                        'name': 'xml_doc',
                        'docstring': doc.strip()[:500],
                        'file': file_path,
                        'type': 'xml_doc'
                    })
        
        elif lang == 'javascript':
            # JSDoc comments
            pattern = r'/\*\*\s*(.*?)\s*\*/'
            for match in re.finditer(pattern, content, re.DOTALL):
                doc = re.sub(r'\s*\*\s*', ' ', match.group(1))
                if doc.strip() and len(doc.strip()) > 10:
                    docstrings.append({
                        'name': 'jsdoc',
                        'docstring': doc.strip()[:500],
                        'file': file_path,
                        'type': 'jsdoc'
                    })
        
        return docstrings
    
    def _extract_inline_comments(
        self,
        content: str,
        lang: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract inline comments"""
        comments = []
        lines = content.split('\n')
        
        if lang in self.COMMENT_PATTERNS:
            pattern = self.COMMENT_PATTERNS[lang]['single']
            
            for line_num, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    comment_text = match.group(1).strip()
                    # Skip short comments and markers (handled separately)
                    if len(comment_text) > 10 and not any(
                        marker in comment_text.upper() 
                        for marker in ['TODO', 'FIXME', 'HACK', 'NOTE']
                    ):
                        comments.append({
                            'text': comment_text[:200],
                            'file': file_path,
                            'line': line_num
                        })
        
        return comments
    
    def _find_markers(
        self,
        content: str,
        file_path: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find TODO, FIXME, etc. markers"""
        markers = defaultdict(list)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for marker_type, pattern in self.MARKER_PATTERNS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    markers[marker_type].append({
                        'text': match.group(2).strip()[:200] if len(match.groups()) > 1 else match.group(1),
                        'file': file_path,
                        'line': line_num
                    })
        
        return dict(markers)
    
    def _find_regulatory_keywords(
        self,
        content: str,
        file_path: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find regulatory compliance keywords"""
        regulatory = defaultdict(list)
        content_lower = content.lower()
        lines = content.split('\n')
        
        for reg_type, keywords in self.REGULATORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    # Find the line containing the keyword
                    for line_num, line in enumerate(lines, 1):
                        if keyword.lower() in line.lower():
                            regulatory[reg_type].append({
                                'keyword': keyword,
                                'file': file_path,
                                'line': line_num,
                                'context': line.strip()[:100]
                            })
                            break  # Only record first occurrence per file
        
        return dict(regulatory)
    
    def _extract_business_rules(
        self,
        content: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract business rule annotations"""
        rules = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for rule_type, pattern in self.BUSINESS_PATTERNS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    rules.append({
                        'type': rule_type,
                        'text': match.group(2).strip()[:200] if len(match.groups()) > 1 else match.group(0),
                        'file': file_path,
                        'line': line_num
                    })
        
        return rules
    
    def _calculate_doc_coverage(
        self,
        docstrings: List[Dict[str, Any]]
    ) -> str:
        """Calculate documentation coverage grade"""
        count = len(docstrings)
        
        if count >= 50:
            return 'A - Excellent'
        elif count >= 25:
            return 'B - Good'
        elif count >= 10:
            return 'C - Fair'
        elif count >= 5:
            return 'D - Poor'
        else:
            return 'F - Minimal'
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate collected data"""
        return 'docstrings' in data and 'markers' in data
