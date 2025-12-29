"""
Dashboard templates for different repository types.

6 Built-in Templates:
1. fullstack_web - Full-stack applications (7 tabs)
2. api_service - API services (6 tabs)
3. database_project - Database projects (5 tabs)
4. console_app - Console applications (5 tabs)
5. microservices - Microservices architecture (7 tabs)
6. library_package - Libraries/packages (5 tabs)

Template Structure:
- base/ - Shared components (CSS, JS, UI widgets)
- {template_name}/ - Template-specific files
  - manifest.json - Tab configuration
  - index.html - Main dashboard
  - tabs/ - Tab modules

Registry:
- TemplateRegistry: Maps repo types to templates
"""

from pathlib import Path
from typing import List

class TemplateRegistry:
    """
    Central registry for dashboard templates.
    
    Templates are selected based on repo classification.
    """
    
    TEMPLATE_DIR = Path(__file__).parent
    
    TEMPLATES = {
        'fullstack_web': 'fullstack_web',
        'api_service': 'api_service',
        'database_project': 'database_project',
        'console_app': 'console_app',
        'microservices': 'microservices',
        'library_package': 'library_package',
    }
    
    @classmethod
    def get_template_path(cls, template_name: str) -> Path:
        """Get path to template directory."""
        if template_name not in cls.TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        return cls.TEMPLATE_DIR / cls.TEMPLATES[template_name]
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List all available templates."""
        return list(cls.TEMPLATES.keys())

__all__ = ['TemplateRegistry']
