"""
Response Template Auto-Generator for CORTEX Align v2.0

Automatically generates response templates for operations that don't have them.
Analyzes operation files to create contextually appropriate templates.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateGenerationResult:
    """Result of template generation."""
    success: bool
    operation_name: str
    template_content: str = ""
    error_message: str = ""


class ResponseTemplateAutoGenerator:
    """Automatically generates response templates for operations."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize the template generator.
        
        Args:
            cortex_root: Root directory of CORTEX installation
        """
        self.cortex_root = cortex_root
        self.templates_file = cortex_root / "cortex-brain" / "response-templates.yaml"
        self.operations_dir = cortex_root / "src" / "operations"
        self.orchestrators_dir = cortex_root / "src" / "orchestrators"
        self.workflows_dir = cortex_root / "src" / "workflows"
        self.agents_dir = cortex_root / "src" / "cortex_agents"
    
    def extract_operation_metadata(self, operation_name: str) -> Dict[str, str]:
        """
        Extract metadata from operation file.
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            Dictionary with operation metadata
        """
        metadata = {
            'description': f"Execute {operation_name.replace('_', ' ')} operation",
            'category': 'general',
            'common_challenges': 'No Challenge',
            'next_steps_format': 'numbered'
        }
        
        # Try to find and read operation file in all locations
        search_locations = [
            self.operations_dir / f"{operation_name}.py",
            self.orchestrators_dir / f"{operation_name}.py",
            self.workflows_dir / f"{operation_name}.py",
            self.agents_dir / f"{operation_name}.py",
        ]
        
        op_file = None
        for potential_file in search_locations:
            if potential_file.exists():
                op_file = potential_file
                break
        
        # If not found in top-level, try modules directory
        if not op_file:
            modules_dir = self.operations_dir / "modules"
            for subdir in modules_dir.iterdir():
                if subdir.is_dir():
                    potential_file = subdir / f"{operation_name}.py"
                    if potential_file.exists():
                        op_file = potential_file
                        break
        
        if op_file.exists():
            try:
                content = op_file.read_text(encoding='utf-8')
                
                # Extract docstring
                doc_pattern = r'"""(.*?)"""'
                doc_match = re.search(doc_pattern, content, re.DOTALL)
                if doc_match:
                    docstring = doc_match.group(1)
                    
                    # Extract description (first non-empty line)
                    lines = [line.strip() for line in docstring.split('\n') if line.strip()]
                    if lines:
                        metadata['description'] = lines[0]
                    
                    # Infer category from keywords
                    docstring_lower = docstring.lower()
                    if any(kw in docstring_lower for kw in ['plan', 'planning', 'feature']):
                        metadata['category'] = 'planning'
                    elif any(kw in docstring_lower for kw in ['workflow', 'orchestrat', 'pipeline']):
                        metadata['category'] = 'workflow'
                    elif any(kw in docstring_lower for kw in ['agent', 'ai', 'intelligence', 'analyze']):
                        metadata['category'] = 'agent'
                    elif any(kw in docstring_lower for kw in ['test', 'tdd', 'debug']):
                        metadata['category'] = 'development'
                    elif any(kw in docstring_lower for kw in ['commit', 'git', 'checkpoint']):
                        metadata['category'] = 'git'
                    elif any(kw in docstring_lower for kw in ['deploy', 'release']):
                        metadata['category'] = 'deployment'
                    elif any(kw in docstring_lower for kw in ['align', 'cleanup', 'optimize']):
                        metadata['category'] = 'maintenance'
                    elif any(kw in docstring_lower for kw in ['review', 'analyze']):
                        metadata['category'] = 'analysis'
                    
                    # Check for complex operations (use checkboxes)
                    if any(kw in docstring_lower for kw in ['workflow', 'phases', 'steps', 'stages']):
                        metadata['next_steps_format'] = 'checkboxes'
                    
            except Exception as e:
                logger.warning(f"Failed to extract metadata from {op_file}: {e}")
        
        return metadata
    
    def generate_template(self, operation_name: str) -> str:
        """
        Generate a response template for an operation.
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            YAML template content
        """
        metadata = self.extract_operation_metadata(operation_name)
        
        # Create readable operation title
        title = operation_name.replace('_', ' ').title()
        
        template = f"""
  {operation_name}:
    trigger_phrases:
      - "{operation_name}"
      - "{operation_name.replace('_', ' ')}"
    response_profile: "standard"
    template_sections:
      header:
        title: "{title}"
        icon: "🧠"
        include_author: true
      understanding:
        content: "You want to execute the {operation_name.replace('_', ' ')} operation."
      challenge:
        default: "No Challenge"
        auto_detect: true
      response:
        content: "{metadata['description']}"
        include_details: true
      request_echo:
        enabled: true
      next_steps:
        format: "{metadata['next_steps_format']}"
        auto_generate: true
"""
        
        return template.strip()
    
    def add_template(
        self, 
        operation_name: str,
        dry_run: bool = False
    ) -> TemplateGenerationResult:
        """
        Add a response template for an operation.
        
        Args:
            operation_name: Name of the operation
            dry_run: If True, don't modify files
        
        Returns:
            TemplateGenerationResult
        """
        try:
            # Generate template content
            template_content = self.generate_template(operation_name)
            
            if dry_run:
                return TemplateGenerationResult(
                    success=True,
                    operation_name=operation_name,
                    template_content=template_content,
                    error_message=""
                )
            
            # Read existing templates file
            if not self.templates_file.exists():
                logger.error(f"Response templates file not found: {self.templates_file}")
                return TemplateGenerationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message="response-templates.yaml not found"
                )
            
            content = self.templates_file.read_text(encoding='utf-8')
            
            # Find the templates: section
            if 'templates:' not in content:
                logger.error("templates: section not found in YAML")
                return TemplateGenerationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message="templates: section not found"
                )
            
            # Find where to insert: END of templates section (before next top-level key)
            lines = content.split('\n')
            insert_index = -1
            
            # Find templates: line first
            templates_index = -1
            for i, line in enumerate(lines):
                if line.strip() == 'templates:' and not line.startswith(' '):
                    templates_index = i
                    break
            
            if templates_index == -1:
                logger.error("Could not find templates: section start")
                return TemplateGenerationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message="templates: section start not found"
                )
            
            # Find next top-level section after templates: (not indented)
            # This marks the end of templates section
            for i in range(templates_index + 1, len(lines)):
                line = lines[i]
                # Check if it's a top-level key (no leading whitespace, has colon)
                if line and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
                    insert_index = i
                    break
            
            if insert_index == -1:
                # No next section found, append at end
                insert_index = len(lines)
            
            # Insert template (already has proper indentation from generate_template)
            lines.insert(insert_index, template_content)
            
            # Write back
            self.templates_file.write_text('\n'.join(lines), encoding='utf-8')
            
            logger.info(f"   ✅ Generated template for {operation_name}")
            
            return TemplateGenerationResult(
                success=True,
                operation_name=operation_name,
                template_content=template_content,
                error_message=""
            )
            
        except Exception as e:
            logger.error(f"Failed to generate template for {operation_name}: {e}")
            return TemplateGenerationResult(
                success=False,
                operation_name=operation_name,
                error_message=str(e)
            )
    
    def generate_missing_templates(
        self,
        missing_operations: List[str],
        dry_run: bool = False
    ) -> List[TemplateGenerationResult]:
        """
        Generate templates for multiple operations.
        
        Args:
            missing_operations: List of operation names
            dry_run: If True, don't modify files
        
        Returns:
            List of TemplateGenerationResult
        """
        results = []
        
        logger.info(f"   🔧 Generating templates for {len(missing_operations)} operations...")
        
        for op_name in missing_operations:
            result = self.add_template(op_name, dry_run=dry_run)
            results.append(result)
            
            if not result.success:
                logger.warning(f"   ⚠️  Failed to generate template for {op_name}: {result.error_message}")
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"   ✅ Successfully generated {successful}/{len(missing_operations)} templates")
        
        return results

