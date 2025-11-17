"""
CORTEX EPM - Page Generator Module
Generates documentation pages from Jinja2 templates and source data

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any
import yaml
import json
import logging
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class PageGenerator:
    """Generates documentation pages from templates and data sources"""
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.brain_path = root_path / "cortex-brain"
        self.templates_path = self.brain_path / "templates" / "doc-templates"
        self.output_path = root_path / "docs"
        self.dry_run = dry_run
        
        # Initialize Jinja2 environment
        if self.templates_path.exists():
            self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_path)))
        else:
            logger.warning(f"Templates path not found: {self.templates_path}")
            self.jinja_env = None
    
    def generate_all_pages(self, definitions_file: Path, source_mapping: Dict) -> Dict:
        """
        Generate all documentation pages defined in page-definitions.yaml
        
        Returns:
            Dictionary with generation statistics
        """
        pages_generated = []
        
        # Load page definitions
        with open(definitions_file, 'r') as f:
            definitions = yaml.safe_load(f)
        
        for page_def in definitions.get('pages', []):
            template_name = page_def['template']
            output_file = self.output_path / page_def['output_path']
            data_sources = page_def.get('data_sources', [])
            
            # Collect data from sources
            page_data = self._collect_page_data(data_sources, source_mapping)
            
            # Render template
            if self.dry_run:
                logger.info(f"[DRY RUN] Would generate: {output_file}")
            else:
                content = self._render_template(template_name, page_data)
                
                # Write output
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✓ Generated: {output_file}")
            
            pages_generated.append(str(output_file))
        
        return {
            "pages_generated": len(pages_generated),
            "files": pages_generated
        }
    
    def _collect_page_data(self, data_sources: list, source_mapping: Dict) -> Dict[str, Any]:
        """Collect data from specified sources for template rendering"""
        page_data = {}
        
        for source_key in data_sources:
            if source_key not in source_mapping:
                logger.warning(f"Data source not found in mapping: {source_key}")
                continue
            
            source_config = source_mapping[source_key]
            source_type = source_config['type']
            source_path = self.root_path / source_config['path']
            
            if source_type == 'yaml':
                page_data[source_key] = self._read_yaml_source(source_path)
            elif source_type == 'json':
                page_data[source_key] = self._read_json_source(source_path)
            elif source_type == 'markdown':
                page_data[source_key] = self._read_markdown_source(source_path)
            elif source_type == 'python_module':
                page_data[source_key] = self._analyze_python_module(source_path)
            elif source_type == 'directory':
                page_data[source_key] = self._scan_directory(source_path)
            else:
                logger.warning(f"Unknown source type: {source_type}")
        
        return page_data
    
    def _read_yaml_source(self, path: Path) -> Dict:
        """Read YAML data source"""
        if not path.exists():
            logger.warning(f"YAML source not found: {path}")
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # For MkDocs config with Python tags, use BaseLoader to skip execution
                if 'mkdocs' in str(path):
                    # Just load the structure without executing Python tags
                    yaml.add_multi_constructor('tag:yaml.org,2002:python/', lambda loader, suffix, node: None)
                    data = yaml.load(f, Loader=yaml.BaseLoader)
                else:
                    data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            logger.warning(f"Failed to load YAML {path}: {e}")
            return {}
    
    def _read_json_source(self, path: Path) -> Dict:
        """Read JSON data source"""
        if not path.exists():
            logger.warning(f"JSON source not found: {path}")
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load JSON {path}: {e}")
            return {}
    
    def _read_markdown_source(self, path: Path) -> Dict:
        """Read markdown source and extract metadata"""
        if not path.exists():
            logger.warning(f"Markdown source not found: {path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter if present
        # TODO: Implement proper YAML front matter parsing
        
        return {
            "content": content,
            "path": str(path)
        }
    
    def _analyze_python_module(self, path: Path) -> Dict:
        """Analyze Python module structure"""
        if not path.exists():
            logger.warning(f"Python module not found: {path}")
            return {}
        
        # TODO: Implement AST-based analysis to extract:
        # - Classes and their methods
        # - Functions and signatures
        # - Docstrings
        # - Module-level constants
        
        return {
            "path": str(path),
            "name": path.stem,
            "classes": [],
            "functions": []
        }
    
    def _scan_directory(self, path: Path) -> Dict:
        """Scan directory and build structure map"""
        if not path.exists():
            logger.warning(f"Directory not found: {path}")
            return {}
        
        structure = {
            "files": [],
            "directories": [],
            "total_files": 0,
            "total_size_mb": 0.0
        }
        
        for item in path.rglob("*"):
            if item.is_file():
                structure["files"].append({
                    "name": item.name,
                    "path": str(item.relative_to(path)),
                    "size_kb": item.stat().st_size / 1024
                })
                structure["total_files"] += 1
                structure["total_size_mb"] += item.stat().st_size / (1024 * 1024)
            elif item.is_dir():
                structure["directories"].append(str(item.relative_to(path)))
        
        return structure
    
    def _render_template(self, template_name: str, data: Dict) -> str:
        """Render Jinja2 template with data"""
        if not self.jinja_env:
            raise RuntimeError("Jinja2 environment not initialized")
        
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise
