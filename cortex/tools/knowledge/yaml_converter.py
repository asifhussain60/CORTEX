#!/usr/bin/env python3
"""
YAML Converter for CORTEX Knowledge Base

Converts external documentation (Markdown, HTML) to CORTEX YAML format.
Assists in curating knowledge from authoritative sources.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Pattern:
    """Represents a single pattern or best practice."""
    id: str
    name: str
    category: str
    description: str
    example: Optional[str] = None
    benefit: Optional[str] = None


class YAMLConverter:
    """Converts external docs to CORTEX YAML format."""
    
    def __init__(self) -> None:
        """Initialize instance."""
        self.patterns: List[Pattern] = []
    
    def convert_markdown_section(self, content: str, domain: str) -> str:
        """
        Convert Markdown content to YAML structure.
        
        This is a template/helper - manual curation still required.
        """
        yaml_template = f"""---
metadata:
  domain: "{domain}"
  version: "1.0.0"
  source: "[FILL: Source URL or document]"
  authority: "[FILL: Authority (e.g., Microsoft, Google)]"
  date: "{datetime.now().strftime('%Y-%m-%d')}"
  description: "[FILL: Brief description]"
  tags: ["[FILL]", "[FILL]"]

patterns:
  - id: "[FILL: DOMAIN-CAT-001]"
    name: "[FILL: Pattern Name]"
    category: "[FILL: Category]"
    description: "[FILL: Description]"
    example: "[FILL: Code example or usage]"
    benefit: "[FILL: Why this matters]"
    
  # Add more patterns...

best_practices:
  - "[FILL: Best practice 1]"
  - "[FILL: Best practice 2]"

anti_patterns:
  - name: "[FILL: Anti-pattern name]"
    why: "[FILL: Why it's bad]"
    fix: "[FILL: How to fix]"

references:
  - name: "[FILL: Reference name]"
    url: "[FILL: URL]"
"""
        return yaml_template
    
    def extract_code_blocks(self, markdown: str) -> List[str]:
        """Extract code blocks from Markdown."""
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, markdown, re.DOTALL)
        return matches
    
    def extract_headings(self, markdown: str) -> List[tuple]:
        """Extract headings and levels from Markdown."""
        pattern = r"^(#{1,6})\s+(.+)$"
        matches = re.findall(pattern, markdown, re.MULTILINE)
        return [(len(level), heading.strip()) for level, heading in matches]
    
    def suggest_structure(self, markdown_file: Path) -> Dict[str, List[str]]:
        """
        Analyze Markdown and suggest YAML structure.
        
        Returns suggested categories and patterns.
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        headings = self.extract_headings(content)
        code_blocks = self.extract_code_blocks(content)
        
        suggestions = {
            "categories": [h[1] for h in headings if h[0] == 2],  # ## headings
            "patterns": [h[1] for h in headings if h[0] == 3],    # ### headings
            "code_examples_count": len(code_blocks)
        }
        
        return suggestions


def print_help() -> None:
    """Print usage help."""
    print("""
CORTEX YAML Converter

Usage:
  python yaml_converter.py template <domain>     Generate empty template
  python yaml_converter.py analyze <file.md>    Analyze Markdown structure
  
Examples:
  python yaml_converter.py template "TypeScript Best Practices"
  python yaml_converter.py analyze microsoft-docs.md

Note: This tool provides templates and suggestions.
Manual curation is required to ensure quality and accuracy.
""")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    converter = YAMLConverter()
    
    if command == "template":
        if len(sys.argv) < 3:
            print("❌ Usage: yaml_converter.py template <domain>")
            sys.exit(1)
        
        domain = sys.argv[2]
        yaml_content = converter.convert_markdown_section("", domain)
        print(yaml_content)
    
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Usage: yaml_converter.py analyze <markdown_file>")
            sys.exit(1)
        
        markdown_file = Path(sys.argv[2])
        if not markdown_file.exists():
            print(f"❌ File not found: {markdown_file}")
            sys.exit(1)
        
        suggestions = converter.suggest_structure(markdown_file)
        
        print(f"\n📊 Analysis of {markdown_file.name}:\n")
        print(f"Suggested categories ({len(suggestions['categories'])}):")
        for cat in suggestions['categories'][:10]:
            print(f"  - {cat}")
        
        print(f"\nSuggested patterns ({len(suggestions['patterns'])}):")
        for pattern in suggestions['patterns'][:10]:
            print(f"  - {pattern}")
        
        print(f"\nCode examples found: {suggestions['code_examples_count']}")
        print("\n💡 Use 'template' command to generate starter YAML")
    
    else:
        print(f"❌ Unknown command: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
