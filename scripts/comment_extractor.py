"""
C# Comment Extractor for AST-to-Narrative Enhancement

Extracts all comment types from C# files to enrich business narratives with developer insights.

Features:
- XML documentation comments (/// <summary>, <param>, <returns>)
- Single-line comments (// comment)
- Multi-line comments (/* comment */)
- Preprocessor regions (#region, #endregion)
- TODO/FIXME/HACK markers
- Comment classification by business relevance
- Context mapping to AST entities
- Regulatory keyword detection

Usage:
    python scripts/comment_extractor.py --source <path> --output <path>

Output:
    - comment-extraction.json: All extracted comments with context
    - comment-statistics.json: Comment metrics and quality analysis
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Regulatory keywords for compliance detection
REGULATORY_KEYWORDS = {
    'critical': [
        'IRS', 'HIPAA', 'PCI-DSS', 'PCI DSS', 'ERISA', 'ACA', 'Affordable Care Act',
        'Publication 969', 'Pub 969', '§164.312', 'CFR', 'Code of Federal Regulations'
    ],
    'high': [
        'compliance', 'regulation', 'regulatory', 'audit', 'security',
        'privacy', 'protected health information', 'PHI', 'cardholder data'
    ]
}

# Business domain keywords
BUSINESS_KEYWORDS = [
    'grace period', 'forfeiture', 'carry over', 'carryover', 'run-out', 'runout',
    'eligibility', 'contribution limit', 'enrollment', 'reimbursement', 'claim',
    'benefit', 'plan year', 'deductible', 'copay', 'coinsurance', 'out-of-pocket'
]

# Technical debt markers
TECH_DEBT_MARKERS = ['TODO', 'FIXME', 'HACK', 'BUG', 'XXX', 'NOTE', 'OPTIMIZE']


@dataclass
class CommentData:
    """Represents a single extracted comment with metadata"""
    file_path: str
    line_number: int
    comment_type: str  # xml_summary, xml_param, single_line, multi_line, region, tech_debt
    content: str
    context: str  # class/method/property name
    business_relevance: str  # critical, high, medium, low, skip
    regulatory_keywords: List[str]
    business_keywords: List[str]
    tech_debt_marker: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CSharpCommentExtractor:
    """Extracts and classifies comments from C# source files"""
    
    # Regex patterns for C# comments
    XML_DOC_PATTERN = re.compile(r'^\s*///\s*(.+)$', re.MULTILINE)
    SINGLE_LINE_PATTERN = re.compile(r'^\s*//\s*(.+)$', re.MULTILINE)
    MULTI_LINE_PATTERN = re.compile(r'/\*(.+?)\*/', re.DOTALL)
    REGION_PATTERN = re.compile(r'^\s*#region\s+(.+)$', re.MULTILINE)
    
    # XML doc tag extraction
    XML_TAG_PATTERN = re.compile(r'<(\w+)(?:\s+[^>]*)?>(.+?)</\1>|<(\w+)(?:\s+[^>]*)?/>', re.DOTALL)
    
    # Context patterns (class/method/property)
    CLASS_PATTERN = re.compile(r'^\s*(?:public|private|internal|protected)?\s*(?:static|abstract|sealed)?\s*(?:partial)?\s*(?:class|interface|struct|enum)\s+(\w+)', re.MULTILINE)
    METHOD_PATTERN = re.compile(r'^\s*(?:public|private|internal|protected)?\s*(?:static|virtual|override|abstract)?\s*(?:\w+(?:\s*<[^>]+>)?)\s+(\w+)\s*\([^)]*\)', re.MULTILINE)
    PROPERTY_PATTERN = re.compile(r'^\s*(?:public|private|internal|protected)?\s*(?:static|virtual|override)?\s*(?:\w+(?:\s*<[^>]+>)?)\s+(\w+)\s*\{\s*get', re.MULTILINE)
    
    def __init__(self, min_comment_length: int = 10):
        self.min_comment_length = min_comment_length
        self.comments: List[CommentData] = []
        self.stats = defaultdict(int)
        
    def extract_from_file(self, file_path: Path) -> List[CommentData]:
        """Extract all comments from a single C# file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = str(file_path)
            
            # Extract all comment types
            xml_comments = self._extract_xml_comments(content, relative_path)
            single_comments = self._extract_single_line_comments(content, relative_path)
            multi_comments = self._extract_multi_line_comments(content, relative_path)
            region_comments = self._extract_region_comments(content, relative_path)
            
            # Combine and classify
            file_comments = xml_comments + single_comments + multi_comments + region_comments
            
            # Add context (class/method)
            for comment in file_comments:
                comment.context = self._find_context(content, comment.line_number)
                comment.business_relevance = self._classify_relevance(comment)
                comment.regulatory_keywords = self._find_regulatory_keywords(comment.content)
                comment.business_keywords = self._find_business_keywords(comment.content)
                comment.tech_debt_marker = self._find_tech_debt_marker(comment.content)
            
            # Filter low-quality comments
            filtered_comments = [c for c in file_comments if self._is_quality_comment(c)]
            
            self.comments.extend(filtered_comments)
            self.stats['files_processed'] += 1
            self.stats['total_comments'] += len(filtered_comments)
            
            return filtered_comments
            
        except Exception as e:
            logger.warning(f"Error processing {file_path}: {e}")
            self.stats['files_failed'] += 1
            return []
    
    def _extract_xml_comments(self, content: str, file_path: str) -> List[CommentData]:
        """Extract XML documentation comments"""
        comments = []
        lines = content.split('\n')
        
        xml_blocks = []
        current_block = []
        current_line_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('///'):
                if not current_block:
                    current_line_start = i
                current_block.append(line.strip()[3:].strip())
            else:
                if current_block:
                    xml_blocks.append((current_line_start, '\n'.join(current_block)))
                    current_block = []
        
        # Process XML blocks
        for line_num, xml_text in xml_blocks:
            # Parse XML tags
            tags = self.XML_TAG_PATTERN.findall(xml_text)
            
            for tag_match in tags:
                tag_name = tag_match[0] or tag_match[2]
                tag_content = (tag_match[1] or '').strip()
                
                if not tag_content or len(tag_content) < self.min_comment_length:
                    continue
                
                comment_type = f'xml_{tag_name.lower()}'
                
                comments.append(CommentData(
                    file_path=file_path,
                    line_number=line_num,
                    comment_type=comment_type,
                    content=tag_content,
                    context='',
                    business_relevance='',
                    regulatory_keywords=[],
                    business_keywords=[],
                    tech_debt_marker=None
                ))
                self.stats[comment_type] += 1
        
        return comments
    
    def _extract_single_line_comments(self, content: str, file_path: str) -> List[CommentData]:
        """Extract single-line comments (// comment)"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Skip XML doc comments (handled separately)
            if line.strip().startswith('///'):
                continue
                
            match = self.SINGLE_LINE_PATTERN.match(line)
            if match:
                comment_text = match.group(1).strip()
                
                if len(comment_text) < self.min_comment_length:
                    continue
                
                comments.append(CommentData(
                    file_path=file_path,
                    line_number=i,
                    comment_type='single_line',
                    content=comment_text,
                    context='',
                    business_relevance='',
                    regulatory_keywords=[],
                    business_keywords=[],
                    tech_debt_marker=None
                ))
                self.stats['single_line'] += 1
        
        return comments
    
    def _extract_multi_line_comments(self, content: str, file_path: str) -> List[CommentData]:
        """Extract multi-line comments (/* comment */)"""
        comments = []
        
        for match in self.MULTI_LINE_PATTERN.finditer(content):
            comment_text = match.group(1).strip()
            
            if len(comment_text) < self.min_comment_length:
                continue
            
            # Calculate line number
            line_num = content[:match.start()].count('\n') + 1
            
            comments.append(CommentData(
                file_path=file_path,
                line_number=line_num,
                comment_type='multi_line',
                content=comment_text,
                context='',
                business_relevance='',
                regulatory_keywords=[],
                business_keywords=[],
                tech_debt_marker=None
            ))
            self.stats['multi_line'] += 1
        
        return comments
    
    def _extract_region_comments(self, content: str, file_path: str) -> List[CommentData]:
        """Extract #region directives (organizational comments)"""
        comments = []
        
        for match in self.REGION_PATTERN.finditer(content):
            region_name = match.group(1).strip()
            
            if len(region_name) < self.min_comment_length:
                continue
            
            line_num = content[:match.start()].count('\n') + 1
            
            comments.append(CommentData(
                file_path=file_path,
                line_number=line_num,
                comment_type='region',
                content=region_name,
                context='',
                business_relevance='',
                regulatory_keywords=[],
                business_keywords=[],
                tech_debt_marker=None
            ))
            self.stats['region'] += 1
        
        return comments
    
    def _find_context(self, content: str, line_number: int) -> str:
        """Find the class/method/property context for a comment"""
        lines = content.split('\n')
        
        # Search backwards from comment line to find context
        search_start = max(0, line_number - 1)
        search_end = min(len(lines), line_number + 20)
        search_text = '\n'.join(lines[search_start:search_end])
        
        # Try to find method first (most specific)
        method_match = self.METHOD_PATTERN.search(search_text)
        if method_match:
            return f'method {method_match.group(1)}'
        
        # Try property
        property_match = self.PROPERTY_PATTERN.search(search_text)
        if property_match:
            return f'property {property_match.group(1)}'
        
        # Try class (least specific)
        class_match = self.CLASS_PATTERN.search(search_text)
        if class_match:
            return f'class {class_match.group(1)}'
        
        return 'unknown'
    
    def _find_regulatory_keywords(self, text: str) -> List[str]:
        """Find regulatory keywords in comment text"""
        found = []
        text_upper = text.upper()
        
        for level in ['critical', 'high']:
            for keyword in REGULATORY_KEYWORDS.get(level, []):
                if keyword.upper() in text_upper:
                    found.append(keyword)
        
        return list(set(found))
    
    def _find_business_keywords(self, text: str) -> List[str]:
        """Find business domain keywords in comment text"""
        found = []
        text_lower = text.lower()
        
        for keyword in BUSINESS_KEYWORDS:
            if keyword.lower() in text_lower:
                found.append(keyword)
        
        return list(set(found))
    
    def _find_tech_debt_marker(self, text: str) -> Optional[str]:
        """Find technical debt markers (TODO, FIXME, etc.)"""
        text_upper = text.upper()
        
        for marker in TECH_DEBT_MARKERS:
            if marker in text_upper:
                return marker
        
        return None
    
    def _classify_relevance(self, comment: CommentData) -> str:
        """Classify comment business relevance"""
        content_upper = comment.content.upper()
        
        # Critical: Regulatory references
        for keyword in REGULATORY_KEYWORDS['critical']:
            if keyword.upper() in content_upper:
                return 'critical'
        
        # High: Business rules or regulatory-adjacent
        for keyword in REGULATORY_KEYWORDS['high']:
            if keyword.upper() in content_upper:
                return 'high'
        
        # High: Business domain keywords
        for keyword in BUSINESS_KEYWORDS:
            if keyword.lower() in comment.content.lower():
                return 'high'
        
        # Medium: XML documentation
        if comment.comment_type.startswith('xml_'):
            return 'medium'
        
        # Medium: Technical debt markers
        if comment.tech_debt_marker:
            return 'medium'
        
        # Low: Everything else
        return 'low'
    
    def _is_quality_comment(self, comment: CommentData) -> bool:
        """Filter out low-quality comments"""
        content = comment.content.strip()
        
        # Skip if too short
        if len(content) < self.min_comment_length:
            return False
        
        # Skip boilerplate
        boilerplate = [
            'copyright', 'all rights reserved', 'license',
            'auto-generated', 'do not modify', 'code generated'
        ]
        content_lower = content.lower()
        if any(bp in content_lower for bp in boilerplate):
            self.stats['skipped_boilerplate'] += 1
            return False
        
        # Skip empty TODO markers
        if comment.tech_debt_marker and len(content) < 20:
            self.stats['skipped_empty_todo'] += 1
            return False
        
        return True
    
    def generate_statistics(self) -> Dict:
        """Generate comment extraction statistics"""
        total = self.stats['total_comments']
        
        by_type = {
            'xml_summary': self.stats.get('xml_summary', 0),
            'xml_param': self.stats.get('xml_param', 0),
            'xml_returns': self.stats.get('xml_returns', 0),
            'xml_remarks': self.stats.get('xml_remarks', 0),
            'single_line': self.stats.get('single_line', 0),
            'multi_line': self.stats.get('multi_line', 0),
            'region': self.stats.get('region', 0),
        }
        
        by_relevance = defaultdict(int)
        by_tech_debt = defaultdict(int)
        regulatory_count = 0
        business_count = 0
        
        for comment in self.comments:
            by_relevance[comment.business_relevance] += 1
            if comment.tech_debt_marker:
                by_tech_debt[comment.tech_debt_marker] += 1
            if comment.regulatory_keywords:
                regulatory_count += 1
            if comment.business_keywords:
                business_count += 1
        
        return {
            'extraction_summary': {
                'files_processed': self.stats['files_processed'],
                'files_failed': self.stats['files_failed'],
                'total_comments': total,
                'skipped_boilerplate': self.stats.get('skipped_boilerplate', 0),
                'skipped_empty_todo': self.stats.get('skipped_empty_todo', 0),
            },
            'by_type': by_type,
            'by_relevance': dict(by_relevance),
            'by_tech_debt_marker': dict(by_tech_debt),
            'regulatory_comments': regulatory_count,
            'business_comments': business_count,
            'quality_percentage': round((total / max(1, total + self.stats.get('skipped_boilerplate', 0) + self.stats.get('skipped_empty_todo', 0))) * 100, 2)
        }


def main():
    parser = argparse.ArgumentParser(description='Extract comments from C# source files')
    parser.add_argument('--source', type=str, required=True, help='Source directory containing C# files')
    parser.add_argument('--output', type=str, required=True, help='Output directory for JSON files')
    parser.add_argument('--min-length', type=int, default=10, help='Minimum comment length (default: 10)')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    
    if not source_path.exists():
        logger.error(f"Source path does not exist: {source_path}")
        return
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"🔍 Extracting comments from: {source_path}")
    logger.info(f"📊 Output directory: {output_path}")
    
    # Find all C# files
    cs_files = list(source_path.rglob('*.cs'))
    logger.info(f"📁 Found {len(cs_files)} C# files")
    
    # Extract comments
    extractor = CSharpCommentExtractor(min_comment_length=args.min_length)
    
    for i, cs_file in enumerate(cs_files, 1):
        if i % 50 == 0:
            logger.info(f"⏳ Processed {i}/{len(cs_files)} files...")
        extractor.extract_from_file(cs_file)
    
    # Generate outputs
    logger.info(f"✅ Extraction complete!")
    logger.info(f"📈 Total comments extracted: {len(extractor.comments)}")
    
    # Write comment-extraction.json
    comments_output = output_path / 'comment-extraction.json'
    with comments_output.open('w', encoding='utf-8') as f:
        json.dump([c.to_dict() for c in extractor.comments], f, indent=2, ensure_ascii=False)
    logger.info(f"💾 Saved: {comments_output}")
    
    # Write comment-statistics.json
    stats = extractor.generate_statistics()
    stats_output = output_path / 'comment-statistics.json'
    with stats_output.open('w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"💾 Saved: {stats_output}")
    
    # Print summary
    print("\n" + "="*60)
    print("COMMENT EXTRACTION SUMMARY")
    print("="*60)
    print(f"Files Processed: {stats['extraction_summary']['files_processed']}")
    print(f"Total Comments: {stats['extraction_summary']['total_comments']}")
    print(f"Regulatory Comments: {stats['regulatory_comments']}")
    print(f"Business Comments: {stats['business_comments']}")
    print(f"\nBy Relevance:")
    for relevance, count in sorted(stats['by_relevance'].items()):
        print(f"  {relevance}: {count}")
    print(f"\nTechnical Debt Markers:")
    for marker, count in sorted(stats['by_tech_debt_marker'].items()):
        print(f"  {marker}: {count}")
    print("="*60)


if __name__ == '__main__':
    main()
