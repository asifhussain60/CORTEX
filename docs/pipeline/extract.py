#!/usr/bin/env python3
"""
MD to JSON Extraction Pipeline

Extracts metadata and content from markdown files for SPA consumption.
Preserves full prose (read-only), generates structured JSON.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any
import json


class ContentExtractor:
    """Extracts structured data from markdown documentation."""
    
    def __init__(self, content_dir: Path, output_dir: Path):
        self.content_dir = content_dir
        self.output_dir = output_dir
        self.content_index = {
            "generated_at": "",
            "documents": []
        }
    
    def run(self) -> None:
        """Execute full extraction pipeline."""
        print("📦 Starting content extraction...")
        
        self.extract_all_documents()
        self.generate_content_index()
        
        print(f"✅ Extraction complete: {len(self.content_index['documents'])} documents")
    
    def extract_all_documents(self) -> None:
        """Extract all markdown documents."""
        if not self.content_dir.exists():
            print(f"⚠️  Content directory not found: {self.content_dir}")
            return
        
        for md_file in self.content_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            
            print(f"  Processing: {md_file.relative_to(self.content_dir)}")
            
            doc_data = self.extract_document(md_file)
            if doc_data:
                self.content_index["documents"].append(doc_data)
    
    def extract_document(self, md_file: Path) -> Dict[str, Any]:
        """Extract metadata and content from a single markdown file."""
        content = md_file.read_text(encoding="utf-8")
        
        # Extract YAML frontmatter
        frontmatter = self._extract_frontmatter(content)
        
        # Extract role-tagged sections
        role_sections = self._extract_role_sections(content)
        
        # Extract diagrams
        diagrams = self._extract_diagrams(content)
        
        # Compute word count
        word_count = len(re.findall(r'\w+', content))
        
        return {
            "id": md_file.stem,
            "path": str(md_file.relative_to(self.content_dir)),
            "frontmatter": frontmatter,
            "role_sections": role_sections,
            "diagrams": diagrams,
            "word_count": word_count,
            "full_content": content  # Preserved for read-only access
        }
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return {}
        return {}
    
    def _extract_role_sections(self, content: str) -> Dict[str, str]:
        """Extract role-tagged sections."""
        roles = {}
        
        # Pattern: <!-- role:business --> ... next section
        pattern = r'<!--\s*role:(\w+)\s*-->(.*?)(?=<!--\s*role:|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            role = match.group(1)
            section_content = match.group(2).strip()
            roles[role] = section_content
        
        return roles
    
    def _extract_diagrams(self, content: str) -> List[Dict[str, Any]]:
        """Extract diagram metadata."""
        diagrams = []
        
        # Pattern: YAML frontmatter followed by mermaid/d3 code block
        pattern = r'---\s*\n(.*?)\n---\s*\n```(?:mermaid|json)\s*\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                metadata = yaml.safe_load(match.group(1))
                if isinstance(metadata, dict) and "id" in metadata:
                    diagrams.append({
                        "id": metadata.get("id"),
                        "title": metadata.get("title"),
                        "type": metadata.get("diagram_type"),
                        "audience": metadata.get("audience", []),
                        "code": match.group(2).strip()
                    })
            except yaml.YAMLError:
                continue
        
        return diagrams
    
    def generate_content_index(self) -> None:
        """Generate content index JSON."""
        from datetime import datetime
        
        self.content_index["generated_at"] = datetime.now().isoformat()
        
        output_file = self.output_dir / "content.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(self.content_index, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Content index written to: {output_file}")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent
    content_dir = base_dir / "content"
    output_dir = base_dir / "site" / "public" / "data"
    
    extractor = ContentExtractor(content_dir, output_dir)
    extractor.run()


if __name__ == "__main__":
    main()
