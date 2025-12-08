"""
README Deep-Parser

Extracts structured information from README files:
- Purpose statements
- Feature lists
- Installation instructions
- Usage examples
- Section metadata

Includes knowledge graph integration to capture successful README patterns.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
License: Proprietary - Source-Available
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict, field
import json


@dataclass
class ReadmeSection:
    """Represents a section in a README file."""
    title: str
    level: int  # Heading level (1-6)
    content: str
    line_start: int
    line_end: int
    subsections: List['ReadmeSection'] = field(default_factory=list)


@dataclass
class ReadmeMetadata:
    """Structured metadata extracted from README."""
    title: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    features: List[str] = field(default_factory=list)
    installation_steps: List[str] = field(default_factory=list)
    usage_examples: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    sections: List[ReadmeSection] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)


class ReadmeParser:
    """Parse README files and extract structured information."""
    
    # Common section heading patterns
    SECTION_PATTERNS = {
        'purpose': [
            r'##?\s*(purpose|about|overview|description|what is)',
            r'##?\s*🎯\s*(purpose|about|overview)'
        ],
        'features': [
            r'##?\s*(features|capabilities|functionality)',
            r'##?\s*✨\s*features'
        ],
        'installation': [
            r'##?\s*(installation|install|setup|getting started)',
            r'##?\s*📦\s*(installation|setup)'
        ],
        'usage': [
            r'##?\s*(usage|how to use|examples|quick start)',
            r'##?\s*🚀\s*(usage|quick start)'
        ],
        'technology': [
            r'##?\s*(technology|tech stack|built with|technologies)',
            r'##?\s*🛠️?\s*(tech|technology)'
        ]
    }
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def parse_file(self, file_path: Path) -> ReadmeMetadata:
        """
        Parse a README file and extract structured metadata.
        
        Args:
            file_path: Path to README file
        
        Returns:
            ReadmeMetadata with extracted information
        """
        if not file_path.exists():
            raise FileNotFoundError(f"README file not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> ReadmeMetadata:
        """
        Parse README content string.
        
        Args:
            content: README file content
        
        Returns:
            ReadmeMetadata with extracted information
        """
        metadata = ReadmeMetadata()
        lines = content.split('\n')
        
        # Extract title (first heading)
        metadata.title = self._extract_title(lines)
        
        # Extract description (first paragraph after title)
        metadata.description = self._extract_description(lines)
        
        # Parse sections
        metadata.sections = self._parse_sections(lines)
        
        # Extract purpose
        metadata.purpose = self._extract_purpose(metadata.sections, lines)
        
        # Extract features
        metadata.features = self._extract_features(metadata.sections, lines)
        
        # Extract installation steps
        metadata.installation_steps = self._extract_installation(metadata.sections, lines)
        
        # Extract usage examples
        metadata.usage_examples = self._extract_usage(metadata.sections, lines)
        
        # Extract technologies
        metadata.technologies = self._extract_technologies(metadata.sections, lines)
        
        # Extract badges
        metadata.badges = self._extract_badges(content)
        
        # Extract links
        metadata.links = self._extract_links(content)
        
        # Update knowledge graph with successful patterns
        self._update_knowledge_graph(metadata)
        
        return metadata
    
    def _extract_title(self, lines: List[str]) -> Optional[str]:
        """Extract title from first heading."""
        for line in lines[:20]:  # Check first 20 lines
            if line.startswith('# '):
                return line[2:].strip()
        return None
    
    def _extract_description(self, lines: List[str]) -> Optional[str]:
        """Extract description from first paragraph after title."""
        found_title = False
        description_lines = []
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            
            if line.startswith('#'):
                found_title = True
                continue
            
            if found_title and line and not line.startswith('![') and not line.startswith('['):
                if line.startswith('**') or line.startswith('*'):
                    continue  # Skip badges/metadata
                description_lines.append(line)
                if len(description_lines) >= 3:  # Get first 3 lines
                    break
        
        if description_lines:
            return ' '.join(description_lines)
        return None
    
    def _parse_sections(self, lines: List[str]) -> List[ReadmeSection]:
        """Parse all sections with headings."""
        sections = []
        current_section = None
        content_lines = []
        
        for i, line in enumerate(lines):
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
            
            if heading_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(content_lines).strip()
                    current_section.line_end = i - 1
                    sections.append(current_section)
                    content_lines = []
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                current_section = ReadmeSection(
                    title=title,
                    level=level,
                    content='',
                    line_start=i,
                    line_end=i
                )
            elif current_section:
                content_lines.append(line)
        
        # Save last section
        if current_section:
            current_section.content = '\n'.join(content_lines).strip()
            current_section.line_end = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def _extract_purpose(self, sections: List[ReadmeSection], lines: List[str]) -> Optional[str]:
        """Extract purpose/about statement."""
        for section in sections:
            # Check if section title matches purpose patterns (without markdown ##)
            title_lower = section.title.lower()
            if any(keyword in title_lower for keyword in ['purpose', 'about', 'overview', 'description', 'what is']):
                # Get first paragraph of content
                paragraphs = section.content.split('\n\n')
                if paragraphs:
                    return paragraphs[0].strip()
        
        # Fallback: use description
        return None
    
    def _extract_features(self, sections: List[ReadmeSection], lines: List[str]) -> List[str]:
        """Extract feature list."""
        features = []
        
        for section in sections:
            title_lower = section.title.lower()
            if any(keyword in title_lower for keyword in ['feature', 'capabilities', 'functionality']):
                # Extract bullet points
                features.extend(self._extract_list_items(section.content))
        
        return features
    
    def _extract_installation(self, sections: List[ReadmeSection], lines: List[str]) -> List[str]:
        """Extract installation steps."""
        steps = []
        
        for section in sections:
            title_lower = section.title.lower()
            if any(keyword in title_lower for keyword in ['installation', 'install', 'setup', 'getting started']):
                # Extract numbered or bullet list
                steps.extend(self._extract_list_items(section.content))
        
        return steps
    
    def _extract_usage(self, sections: List[ReadmeSection], lines: List[str]) -> List[str]:
        """Extract usage examples."""
        examples = []
        
        for section in sections:
            title_lower = section.title.lower()
            if any(keyword in title_lower for keyword in ['usage', 'how to use', 'example', 'quick start']):
                # Extract code blocks
                code_blocks = re.findall(r'```[\w]*\n(.*?)```', section.content, re.DOTALL)
                examples.extend([block.strip() for block in code_blocks])
        
        return examples
    
    def _extract_technologies(self, sections: List[ReadmeSection], lines: List[str]) -> List[str]:
        """Extract technology stack."""
        technologies = []
        
        for section in sections:
            title_lower = section.title.lower()
            if any(keyword in title_lower for keyword in ['technology', 'tech stack', 'built with', 'technologies']):
                # Extract list items
                technologies.extend(self._extract_list_items(section.content))
        
        return technologies
    
    def _extract_list_items(self, content: str) -> List[str]:
        """Extract bullet points or numbered list items."""
        items = []
        
        # Match bullet points (-, *, +) or numbered lists (1., 2.)
        pattern = r'^[\s]*(?:[-*+]|\d+\.)\s+(.+)$'
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                item = match.group(1).strip()
                # Remove markdown formatting
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Bold
                item = re.sub(r'\*(.+?)\*', r'\1', item)      # Italic
                item = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', item)  # Links
                items.append(item)
        
        return items
    
    def _extract_badges(self, content: str) -> List[str]:
        """Extract badge URLs."""
        badges = []
        
        # Match markdown badges: ![alt](url) or [![alt](img-url)](link-url)
        badge_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        for match in re.finditer(badge_pattern, content):
            badges.append(match.group(2))
        
        return badges
    
    def _extract_links(self, content: str) -> Dict[str, str]:
        """Extract markdown links."""
        links = {}
        
        # Match markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            if not url.startswith('http'):
                continue  # Skip relative links
            links[text] = url
        
        return links
    
    def _update_knowledge_graph(self, metadata: ReadmeMetadata) -> None:
        """Update tier2 knowledge graph with README patterns."""
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            
            kg = KnowledgeGraph()
            
            # Store common section patterns (only if we have multiple sections)
            if len(metadata.sections) >= 3:
                kg.store_pattern(
                    title=f"readme_sections_{len(metadata.sections)}",
                    pattern_type='readme_structure',
                    confidence=0.8,
                    context={
                        'section_count': len(metadata.sections),
                        'section_titles': [s.title for s in metadata.sections[:5]]  # Top 5
                    },
                    scope='intelligence',
                    namespaces=['readme', 'structure']
                )
            
            # Store feature extraction effectiveness
            if metadata.features and len(metadata.features) >= 3:
                kg.store_pattern(
                    title=f"readme_features_{len(metadata.features)}",
                    pattern_type='readme_extraction',
                    confidence=0.9,
                    context={
                        'feature_count': len(metadata.features),
                        'extraction_method': 'list_parsing'
                    },
                    scope='intelligence',
                    namespaces=['readme', 'features']
                )
        
        except ImportError:
            # Knowledge graph not available - continue without it
            pass
        except Exception as e:
            # Log but don't fail
            print(f"Warning: Could not update knowledge graph: {e}")
    
    def to_dict(self, metadata: ReadmeMetadata) -> Dict:
        """Convert metadata to dictionary for serialization."""
        result = asdict(metadata)
        return result
    
    def to_json(self, metadata: ReadmeMetadata, indent: int = 2) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(metadata), indent=indent)


def find_readme(directory: Path) -> Optional[Path]:
    """
    Find README file in directory.
    
    Args:
        directory: Directory to search
    
    Returns:
        Path to README file or None if not found
    """
    readme_patterns = [
        'README.md',
        'readme.md',
        'README.MD',
        'README.txt',
        'README',
        'Readme.md'
    ]
    
    for pattern in readme_patterns:
        readme_path = directory / pattern
        if readme_path.exists():
            return readme_path
    
    return None
