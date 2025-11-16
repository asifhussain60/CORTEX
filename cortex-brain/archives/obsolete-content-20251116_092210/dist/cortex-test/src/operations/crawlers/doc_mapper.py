"""
Documentation Mapper Crawler

Maps documentation structure and assesses completeness.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
import re

from .base_crawler import BaseCrawler


class DocMapperCrawler(BaseCrawler):
    """
    Maps documentation to analyze:
    - Total documentation files
    - Documentation types (user guides, API docs, design docs)
    - Documentation coverage
    - README quality
    - Help system availability
    """
    
    # Documentation directories to scan
    DOC_DIRS = ['docs', 'documentation', 'prompts', 'cortex-brain']
    
    # Documentation file patterns
    DOC_PATTERNS = ['*.md', '*.rst', '*.txt', '*.adoc']
    
    def get_name(self) -> str:
        return "Documentation Mapper"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Map and analyze documentation structure.
        
        Returns:
            Dict containing documentation analysis
        """
        self.log_info("Starting documentation mapping")
        
        doc_data = {
            'total_docs': 0,
            'user_guides': 0,
            'api_docs': 0,
            'design_docs': 0,
            'readme_quality': 0.0,
            'readme_exists': False,
            'documented_modules': 0,
            'undocumented_modules': 0,
            'help_system': None,
            'doc_directories': []
        }
        
        project_path = Path(self.project_root)
        
        # Find all documentation files
        all_docs = self._find_documentation_files(project_path)
        doc_data['total_docs'] = len(all_docs)
        
        # Categorize documentation
        for doc_path in all_docs:
            category = self._categorize_doc(doc_path)
            if category == 'user_guide':
                doc_data['user_guides'] += 1
            elif category == 'api_doc':
                doc_data['api_docs'] += 1
            elif category == 'design_doc':
                doc_data['design_docs'] += 1
        
        # Analyze README
        readme_path = self._find_readme(project_path)
        if readme_path:
            doc_data['readme_exists'] = True
            doc_data['readme_quality'] = self._assess_readme_quality(readme_path)
        
        # Check for help system
        doc_data['help_system'] = self._detect_help_system(project_path)
        
        # Find documentation directories
        doc_data['doc_directories'] = self._find_doc_directories(project_path)
        
        # Assess module documentation coverage
        coverage = self._assess_module_coverage(project_path)
        doc_data.update(coverage)
        
        self.log_info(
            f"Documentation mapping complete: {doc_data['total_docs']} docs, "
            f"README quality: {doc_data['readme_quality']:.1f}/10"
        )
        
        return {
            "success": True,
            "data": doc_data
        }
    
    def _find_documentation_files(self, project_path: Path) -> List[Path]:
        """
        Find all documentation files in project.
        
        Args:
            project_path: Project root path
            
        Returns:
            List of documentation file paths
        """
        docs = []
        
        for doc_dir in self.DOC_DIRS:
            dir_path = project_path / doc_dir
            if dir_path.exists():
                for pattern in self.DOC_PATTERNS:
                    docs.extend(dir_path.rglob(pattern))
        
        # Also check root for README, CHANGELOG, etc.
        for pattern in self.DOC_PATTERNS:
            docs.extend(project_path.glob(pattern))
        
        return list(set(docs))  # Remove duplicates
    
    def _categorize_doc(self, doc_path: Path) -> str:
        """
        Categorize documentation file.
        
        Args:
            doc_path: Path to documentation file
            
        Returns:
            Category: 'user_guide', 'api_doc', 'design_doc', or 'other'
        """
        path_str = str(doc_path).lower()
        filename = doc_path.name.lower()
        
        # User guides
        if any(keyword in path_str for keyword in ['guide', 'tutorial', 'howto', 'getting-started']):
            return 'user_guide'
        
        # API documentation
        if any(keyword in path_str for keyword in ['api', 'reference', 'technical']):
            return 'api_doc'
        
        # Design documentation
        if any(keyword in path_str for keyword in ['design', 'architecture', 'cortex-2.0-design']):
            return 'design_doc'
        
        return 'other'
    
    def _find_readme(self, project_path: Path) -> Path:
        """Find README file."""
        for name in ['README.md', 'README.rst', 'README.txt', 'README']:
            readme = project_path / name
            if readme.exists():
                return readme
        return None
    
    def _assess_readme_quality(self, readme_path: Path) -> float:
        """
        Assess README quality (0-10 score).
        
        Args:
            readme_path: Path to README file
            
        Returns:
            Quality score from 0-10
        """
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return 0.0
        
        score = 0.0
        
        # Basic existence (2 points)
        score += 2.0
        
        # Length (2 points - should be substantial)
        lines = len(content.split('\n'))
        if lines > 50:
            score += 2.0
        elif lines > 20:
            score += 1.0
        
        # Sections (4 points - check for key sections)
        sections = {
            'installation': r'##?\s+(installation|install|setup|getting started)',
            'usage': r'##?\s+(usage|how to use|quick start)',
            'features': r'##?\s+(features|capabilities|what)',
            'contributing': r'##?\s+(contributing|contribution)',
        }
        
        for section, pattern in sections.items():
            if re.search(pattern, content, re.IGNORECASE):
                score += 1.0
        
        # Code examples (1 point)
        if '```' in content or '    ' in content:
            score += 1.0
        
        # Links (1 point)
        if 'http' in content or '[' in content:
            score += 1.0
        
        return min(10.0, score)
    
    def _detect_help_system(self, project_path: Path) -> str:
        """
        Detect what kind of help system is available.
        
        Args:
            project_path: Project root path
            
        Returns:
            Help system type or None
        """
        # Check for response templates
        templates_path = project_path / 'cortex-brain' / 'response-templates.yaml'
        if templates_path.exists():
            try:
                with open(templates_path, 'r') as f:
                    content = f.read()
                    pattern_count = content.count('trigger:')
                return f"response-templates ({pattern_count} patterns)"
            except Exception:
                pass
        
        # Check for CLI help
        if (project_path / 'src' / 'cli.py').exists():
            return "CLI help system"
        
        return None
    
    def _find_doc_directories(self, project_path: Path) -> List[str]:
        """Find all directories containing documentation."""
        doc_dirs = []
        
        for doc_dir in self.DOC_DIRS:
            dir_path = project_path / doc_dir
            if dir_path.exists():
                doc_dirs.append(doc_dir)
        
        return doc_dirs
    
    def _assess_module_coverage(self, project_path: Path) -> Dict[str, int]:
        """
        Assess how many Python modules have documentation.
        
        Args:
            project_path: Project root path
            
        Returns:
            Dict with documented and undocumented module counts
        """
        src_dir = project_path / 'src'
        
        if not src_dir.exists():
            return {'documented_modules': 0, 'undocumented_modules': 0}
        
        # Find all Python modules
        modules = list(src_dir.rglob('*.py'))
        modules = [m for m in modules if '__pycache__' not in str(m)]
        
        documented = 0
        
        for module in modules:
            try:
                with open(module, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for docstrings
                    if '"""' in content or "'''" in content:
                        documented += 1
            except Exception:
                pass
        
        total = len(modules)
        undocumented = total - documented
        
        return {
            'documented_modules': documented,
            'undocumented_modules': undocumented
        }
