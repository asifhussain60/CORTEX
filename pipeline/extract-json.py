#!/usr/bin/env python3
"""
CORTEX Documentation JSON Extractor

Extracts structured content from markdown files in cortex-docs/content/src/
and generates assets/data/content.json for client-side rendering.

Usage:
    python cortex-docs/pipeline/extract-json.py

Output:
    cortex-docs/assets/data/content.json
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import markdown
except ImportError:
    # Fallback if markdown not available
    markdown = None


class ContentExtractor:
    """Extracts and structures markdown content for static site rendering."""
    
    def __init__(self, content_root: Path, output_path: Path):
        self.content_root = content_root
        self.output_path = output_path
        self.content_data = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "categories": [],
            "roles": self._define_roles()
        }
    
    def _define_roles(self) -> Dict[str, Any]:
        """Define role configurations for content filtering."""
        return {
            "business-leader": {
                "id": "business-leader",
                "label": "Business Leader",
                "icon": "👔",
                "focus": "ROI, Governance, Risk Mitigation, Strategy",
                "categories": ["capabilities", "governance", "infrastructure", "overview"],
                "keywords": ["ROI", "governance", "risk", "compliance", "business value"]
            },
            "product-owner": {
                "id": "product-owner",
                "label": "Product Owner",
                "icon": "📋",
                "focus": "Use Cases, Feature Flow, Definition of Ready",
                "categories": ["capabilities", "orchestration", "mcp", "overview"],
                "keywords": ["feature", "workflow", "use case", "orchestrator", "MCP"]
            },
            "software-engineer": {
                "id": "software-engineer",
                "label": "Software Engineer",
                "icon": "💻",
                "focus": "Wiring, LENS Analysis, TDD, Registry Logic",
                "categories": ["capabilities", "lens", "toolkit", "orchestration", "mcp", "infrastructure", "diagrams", "learning"],
                "keywords": ["implementation", "TDD", "LENS", "orchestrator", "wiring"]
            }
        }
    
    def run(self) -> Dict[str, Any]:
        """Execute full extraction pipeline."""
        print("📄 Extracting markdown content...")
        
        # Discover categories
        categories = self._discover_categories()
        
        # Extract content from each category
        for category_path in categories:
            category_data = self._extract_category(category_path)
            if category_data:
                self.content_data["categories"].append(category_data)
        
        # Add root files (index, glossary)
        self._extract_root_files()
        
        # Write output
        self._write_json()
        
        total_files = sum(len(cat["files"]) for cat in self.content_data["categories"])
        print(f"✅ Extracted {total_files} files across {len(self.content_data['categories'])} categories")
        
        return self.content_data
    
    def _discover_categories(self) -> List[Path]:
        """Discover all category directories in content/src/."""
        categories = []
        for item in self.content_root.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                categories.append(item)
        return sorted(categories, key=lambda p: p.name)
    
    def _extract_category(self, category_path: Path) -> Optional[Dict[str, Any]]:
        """Extract all markdown files from a category directory."""
        category_id = category_path.name
        
        files_data = []
        md_files = list(category_path.glob("*.md"))
        
        for md_file in sorted(md_files):
            if md_file.name.startswith("_"):
                continue
            
            file_data = self._extract_file(md_file, category_id)
            if file_data:
                files_data.append(file_data)
        
        if not files_data:
            return None
        
        return {
            "id": category_id,
            "title": category_id.replace("-", " ").title(),
            "file_count": len(files_data),
            "files": files_data
        }
    
    def _extract_file(self, file_path: Path, category_id: str) -> Optional[Dict[str, Any]]:
        """Extract content and metadata from a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)
            
            # Extract markdown body
            body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            
            # Convert to HTML
            if markdown:
                html_content = markdown.markdown(
                    body,
                    extensions=['extra', 'codehilite', 'toc', 'tables']
                )
            else:
                # Fallback: basic markdown to HTML (headers only)
                html_content = body.replace('\n## ', '\n<h2>').replace('\n# ', '\n<h1>')
                html_content = html_content.replace('\n### ', '\n<h3>')
            
            # Generate excerpt
            excerpt = self._generate_excerpt(body)
            
            # Determine role visibility
            roles = self._determine_roles(frontmatter, content, category_id)
            
            slug = file_path.stem
            
            return {
                "slug": slug,
                "title": frontmatter.get("title", self._slugify_title(slug)),
                "category": category_id,
                "audience": frontmatter.get("audience", []),
                "roles": roles,
                "excerpt": excerpt,
                "content_html": html_content,
                "word_count": frontmatter.get("word_count", len(body.split())),
                "last_verified": frontmatter.get("last_verified", ""),
                "related_diagrams": frontmatter.get("related_diagrams", [])
            }
        
        except Exception as e:
            print(f"⚠️  Error extracting {file_path.name}: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown content."""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}
        
        try:
            data = yaml.safe_load(match.group(1)) or {}
            # Convert date objects to ISO strings for JSON serialization
            for key, value in data.items():
                if hasattr(value, 'isoformat'):  # datetime.date or datetime.datetime
                    data[key] = value.isoformat()
            return data
        except yaml.YAMLError:
            return {}
    
    def _generate_excerpt(self, body: str, max_length: int = 200) -> str:
        """Generate excerpt from markdown body."""
        # Remove markdown syntax
        clean = re.sub(r'#.*?\n', '', body)  # Remove headers
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)  # Remove links
        clean = re.sub(r'[*_`]', '', clean)  # Remove formatting
        clean = re.sub(r'\n+', ' ', clean)  # Collapse newlines
        clean = clean.strip()
        
        if len(clean) <= max_length:
            return clean
        
        return clean[:max_length].rsplit(' ', 1)[0] + '...'
    
    def _determine_roles(self, frontmatter: Dict[str, Any], content: str, category_id: str) -> List[str]:
        """Determine which roles should see this content."""
        roles = []
        
        # Check frontmatter audience
        audience = frontmatter.get("audience", [])
        audience_map = {
            "Business Leaders": "business-leader",
            "Product Owners": "product-owner",
            "Software Developers": "software-engineer",
            "Architects": "software-engineer"
        }
        
        for aud in audience:
            role_id = audience_map.get(aud)
            if role_id and role_id not in roles:
                roles.append(role_id)
        
        # Check category-based visibility
        for role_id, role_config in self.content_data["roles"].items():
            if category_id in role_config["categories"] and role_id not in roles:
                roles.append(role_id)
        
        # Keyword matching
        content_lower = content.lower()
        for role_id, role_config in self.content_data["roles"].items():
            for keyword in role_config["keywords"]:
                if keyword.lower() in content_lower:
                    if role_id not in roles:
                        roles.append(role_id)
                    break
        
        # Default: software-engineer sees all
        if not roles or category_id in ["diagrams", "toolkit", "learning"]:
            if "software-engineer" not in roles:
                roles.append("software-engineer")
        
        return sorted(roles)
    
    def _slugify_title(self, slug: str) -> str:
        """Convert slug to readable title."""
        return slug.replace("-", " ").replace("_", " ").title()
    
    def _extract_root_files(self) -> None:
        """Extract index.md and glossary.md from root."""
        root_files = ["index.md", "glossary.md"]
        
        for filename in root_files:
            file_path = self.content_root / filename
            if file_path.exists():
                file_data = self._extract_file(file_path, "overview")
                if file_data:
                    # Add to overview category or create it
                    overview_cat = next(
                        (cat for cat in self.content_data["categories"] if cat["id"] == "overview"),
                        None
                    )
                    if overview_cat:
                        overview_cat["files"].append(file_data)
                        overview_cat["file_count"] += 1
                    else:
                        self.content_data["categories"].insert(0, {
                            "id": "overview",
                            "title": "Overview",
                            "file_count": 1,
                            "files": [file_data]
                        })
    
    def _write_json(self) -> None:
        """Write content data to JSON file."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.content_data, f, indent=2, ensure_ascii=False)
        
        size_kb = self.output_path.stat().st_size / 1024
        print(f"📦 Generated {self.output_path.name} ({size_kb:.1f} KB)")


def main():
    """Main entry point."""
    cortex_root = Path(__file__).parent.parent.parent
    content_root = cortex_root / "cortex-docs" / "content" / "src"
    output_path = cortex_root / "cortex-docs" / "assets" / "data" / "content.json"
    
    if not content_root.exists():
        print(f"❌ Content directory not found: {content_root}")
        return 1
    
    extractor = ContentExtractor(content_root, output_path)
    extractor.run()
    
    return 0


if __name__ == "__main__":
    exit(main())
