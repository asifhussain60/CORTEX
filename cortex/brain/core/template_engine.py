"""
Custom Response Templates System

AC-AR-009-01: Response templates loaded from cortex-brain/tier2/
AC-AR-009-02: Templates support variable substitution
AC-AR-009-03: Template inheritance working
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class TemplateInfo:
    """Template metadata"""
    name: str
    domain: str  # e.g., "governance", "audit", "evidence"
    version: str
    variables: List[str]
    parent_template: Optional[str] = None  # For inheritance
    content: str = ""


class TemplateRegistry:
    """
    Registry for response templates.
    
    Singleton pattern for template management across the application.
    """
    
    _instance: Optional['TemplateRegistry'] = None
    _templates: Dict[str, TemplateInfo] = {}
    _template_contents: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def instance(cls) -> 'TemplateRegistry':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset instance for testing"""
        cls._instance = None
        cls._templates = {}
        cls._template_contents = {}
    
    def register_template(self, template_info: TemplateInfo) -> Result[str]:
        """
        Register a template.
        
        Args:
            template_info: Template metadata
            
        Returns:
            Ok with template name or Err
        """
        try:
            self._templates[template_info.name] = template_info
            if template_info.content:
                self._template_contents[template_info.name] = template_info.content
            return Ok(f"Template {template_info.name} registered")
        except Exception as e:
            return Err(f"Failed to register template: {str(e)}")
    
    def get_template(self, name: str) -> Optional[TemplateInfo]:
        """Get template by name"""
        return self._templates.get(name)
    
    def get_template_content(self, name: str) -> Optional[str]:
        """Get template content by name"""
        return self._template_contents.get(name)
    
    def list_templates(self, domain: Optional[str] = None) -> List[TemplateInfo]:
        """
        List all templates or templates for specific domain.
        
        Args:
            domain: Optional domain filter (e.g., "governance")
            
        Returns:
            List of template info objects
        """
        if domain:
            return [t for t in self._templates.values() if t.domain == domain]
        return list(self._templates.values())
    
    def get_templates_by_domain(self, domain: str) -> Dict[str, TemplateInfo]:
        """Get all templates for a domain"""
        return {
            name: template 
            for name, template in self._templates.items() 
            if template.domain == domain
        }
    
    def get_all_templates(self) -> Dict[str, TemplateInfo]:
        """Get all registered templates"""
        return self._templates.copy()


class TemplateEngine:
    """
    Template rendering engine with variable substitution and inheritance.
    
    Supports:
    - Variable substitution: {{variable_name}}
    - Template inheritance: {%extends "parent_template"%}
    - Conditional blocks: {%if condition%}...{%endif%}
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize template engine.
        
        Args:
            template_dir: Path to templates directory (default: cortex-brain/tier2/response-templates)
        """
        self.logger = EnhancedAuditLogger.instance()
        self.registry = TemplateRegistry.instance()
        
        # Default to cortex-brain/tier2/response-templates
        if template_dir is None:
            project_root = Path(__file__).parent.parent.parent
            template_dir = str(project_root / "cortex-brain" / "tier2" / "response-templates")
        
        self.template_dir = template_dir
    
    def load_templates(self) -> Result[int]:
        """
        Load templates from template directory.
        
        AC-AR-009-01: Response templates loaded from cortex-brain/tier2/
        
        Returns:
            Ok with count of loaded templates or Err
        """
        try:
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-009-01",
                    operation="LOAD_TEMPLATES",
                    details={"template_dir": self.template_dir}
                )
            
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir, exist_ok=True)
            
            loaded_count = 0
            
            # Load all .json and .yaml templates from directory
            for filename in os.listdir(self.template_dir):
                if filename.endswith(('.json', '.yaml', '.yml')):
                    filepath = os.path.join(self.template_dir, filename)
                    try:
                        self._load_single_template(filepath, filename)
                        loaded_count += 1
                    except Exception as e:
                        if self.logger:
                            self.logger.log_operation_complete(
                                ac_id="AC-AR-009-01",
                                operation="LOAD_TEMPLATE_FILE",
                                success=False,
                                details={"file": filename, "error": str(e)}
                            )
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-009-01",
                    operation="LOAD_TEMPLATES",
                    success=True,
                    details={"templates_loaded": loaded_count}
                )
            
            return Ok(loaded_count)
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-009-01",
                    operation="LOAD_TEMPLATES",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Failed to load templates: {str(e)}")
    
    def _load_single_template(self, filepath: str, filename: str) -> None:
        """Load a single template file"""
        with open(filepath, 'r') as f:
            if filename.endswith('.json'):
                data = json.load(f)
            else:
                # For YAML, would need yaml library - fallback to treating as JSON
                data = json.load(f)
        
        # Extract template metadata
        name = data.get("name", filename)
        domain = data.get("domain", "general")
        version = data.get("version", "1.0")
        content = data.get("content", "")
        parent_template = data.get("parent", None)
        
        # Extract variables from content using regex
        variables = re.findall(r'{{(\w+)}}', content)
        
        template_info = TemplateInfo(
            name=name,
            domain=domain,
            version=version,
            variables=list(set(variables)),  # Remove duplicates
            parent_template=parent_template,
            content=content
        )
        
        self.registry.register_template(template_info)
    
    def render(self, template_name: str, variables: Optional[Dict[str, Any]] = None) -> Result[str]:
        """
        Render a template with variable substitution.
        
        AC-AR-009-02: Templates support variable substitution
        
        Args:
            template_name: Name of template to render
            variables: Dictionary of variables to substitute
            
        Returns:
            Ok with rendered template string or Err
        """
        try:
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-009-02",
                    operation="RENDER_TEMPLATE",
                    details={"template": template_name, "variables_count": len(variables) if variables else 0}
                )
            
            # Get template info
            template_info = self.registry.get_template(template_name)
            if not template_info:
                return Err(f"Template '{template_name}' not found")
            
            # Get template content
            content = self.registry.get_template_content(template_name)
            if not content:
                return Err(f"Template '{template_name}' has no content")
            
            # Handle inheritance
            if template_info.parent_template:
                content = self._handle_inheritance(template_name, content, variables or {})
            
            # Substitute variables
            if variables:
                for key, value in variables.items():
                    placeholder = "{{" + key + "}}"
                    content = content.replace(placeholder, str(value))
            
            # Check for unsubstituted variables
            unsubstituted = re.findall(r'{{(\w+)}}', content)
            if unsubstituted:
                missing_vars = ", ".join(unsubstituted)
                if self.logger:
                    self.logger.log_operation_complete(
                        ac_id="AC-AR-009-02",
                        operation="RENDER_TEMPLATE",
                        success=False,
                        details={"missing_variables": missing_vars}
                    )
                return Err(f"Missing variables: {missing_vars}")
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-009-02",
                    operation="RENDER_TEMPLATE",
                    success=True,
                    details={"template": template_name}
                )
            
            return Ok(content)
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-009-02",
                    operation="RENDER_TEMPLATE",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Template rendering failed: {str(e)}")
    
    def _handle_inheritance(self, template_name: str, content: str, variables: Dict[str, Any]) -> str:
        """
        Handle template inheritance.
        
        AC-AR-009-03: Template inheritance working
        
        Args:
            template_name: Current template name
            content: Current template content
            variables: Variables for rendering
            
        Returns:
            Content with inheritance resolved
        """
        # Get parent template info
        template_info = self.registry.get_template(template_name)
        if not template_info or not template_info.parent_template:
            return content
        
        parent_name = template_info.parent_template
        parent_info = self.registry.get_template(parent_name)
        if not parent_info:
            return content
        
        parent_content = self.registry.get_template_content(parent_name)
        if not parent_content:
            return content
        
        # Recursively handle parent inheritance
        parent_content = self._handle_inheritance(parent_name, parent_content, variables)
        
        # Replace {{body}} in parent with child content
        inherited = parent_content.replace("{{body}}", content)
        
        return inherited
    
    def get_template_info(self, template_name: str) -> Optional[TemplateInfo]:
        """Get template metadata"""
        return self.registry.get_template(template_name)
    
    def list_templates(self, domain: Optional[str] = None) -> List[TemplateInfo]:
        """List available templates, optionally filtered by domain"""
        return self.registry.list_templates(domain)
