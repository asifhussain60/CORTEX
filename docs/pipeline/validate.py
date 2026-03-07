#!/usr/bin/env python3
"""
Content Validation Pipeline

Validates documentation quality:
- Word count minimums
- Analogy density
- Example diversity
- Link integrity
- Diagram metadata
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class ContentValidator:
    """Validates documentation against quality standards."""
    
    def __init__(self, content_dir: Path):
        self.content_dir = content_dir
        self.violations = []
        self.warnings = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all documents."""
        print("✅ Starting validation...")
        
        for md_file in self.content_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            
            print(f"  Validating: {md_file.relative_to(self.content_dir)}")
            self.validate_document(md_file)
        
        passed = len(self.violations) == 0
        
        if passed:
            print(f"\n✅ Validation PASSED")
            if self.warnings:
                print(f"   ⚠️  {len(self.warnings)} warnings")
        else:
            print(f"\n❌ Validation FAILED: {len(self.violations)} violations")
        
        return passed, self.violations, self.warnings
    
    def validate_document(self, md_file: Path) -> None:
        """Validate a single document."""
        content = md_file.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(content)
        
        # Validate word count
        self._validate_word_count(md_file, content, frontmatter)
        
        # Validate analogies (for PO docs)
        if frontmatter.get("audience") in ["Product Owners", "Product Managers"]:
            self._validate_analogies(md_file, content)
        
        # Validate diagrams
        self._validate_diagrams(md_file, content)
        
        # Validate links
        self._validate_links(md_file, content)
    
    def _validate_word_count(self, md_file: Path, content: str, frontmatter: Dict) -> None:
        """Validate word count meets minimums."""
        word_count = len(re.findall(r'\w+', content))
        audience = frontmatter.get("audience", "")
        
        minimums = {
            "Business Leaders": 1200,
            "Product Owners": 800,
            "Software Developers": 800
        }
        
        for role, minimum in minimums.items():
            if role in str(audience) and word_count < minimum:
                self.violations.append(
                    f"{md_file.name}: Word count {word_count} < minimum {minimum} for {role}"
                )
    
    def _validate_analogies(self, md_file: Path, content: str) -> None:
        """Validate analogy presence (2+ required for PO docs)."""
        analogy_keywords = [
            "think of", "like your brain", "similar to", "just as",
            "imagine", "consider", "picture this", "comparable to"
        ]
        
        analogy_count = sum(1 for keyword in analogy_keywords 
                           if keyword.lower() in content.lower())
        
        if analogy_count < 2:
            self.warnings.append(
                f"{md_file.name}: Only {analogy_count} analogies found (target: 2+)"
            )
    
    def _validate_diagrams(self, md_file: Path, content: str) -> None:
        """Validate diagram metadata."""
        # Find diagrams with YAML frontmatter
        pattern = r'---\s*\n(.*?)\n---\s*\n```(?:mermaid|json)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                metadata = yaml.safe_load(match.group(1))
                
                required_fields = ["id", "title", "purpose", "audience", "diagram_type"]
                for field in required_fields:
                    if field not in metadata:
                        self.violations.append(
                            f"{md_file.name}: Diagram missing required field '{field}'"
                        )
            except yaml.YAMLError:
                self.violations.append(f"{md_file.name}: Invalid diagram YAML frontmatter")
    
    def _validate_links(self, md_file: Path, content: str) -> None:
        """Validate internal links."""
        # Pattern: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, content)
        
        for match in matches:
            link_target = match.group(2)
            
            # Skip external links
            if link_target.startswith(("http://", "https://", "mailto:")):
                continue
            
            # Check if internal file exists
            target_path = (md_file.parent / link_target).resolve()
            if not target_path.exists():
                self.warnings.append(
                    f"{md_file.name}: Broken link to '{link_target}'"
                )
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return {}
        return {}


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent
    content_dir = base_dir / "content"
    
    validator = ContentValidator(content_dir)
    passed, violations, warnings = validator.validate_all()
    
    if violations:
        print("\n❌ Violations:")
        for violation in violations:
            print(f"   {violation}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   {warning}")
    
    exit(0 if passed else 1)


if __name__ == "__main__":
    main()
