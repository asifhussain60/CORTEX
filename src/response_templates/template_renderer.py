"""Template renderer for CORTEX response templates.

This module handles rendering templates with placeholders and verbosity control.

Author: Asif Hussain
Version: 1.0
"""

import re
from typing import Dict, Any, Optional
from .template_loader import Template


class TemplateRenderer:
    """Renders response templates with placeholder substitution and verbosity control."""
    
    def __init__(self):
        """Initialize template renderer."""
        self.placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
        self.conditional_pattern = re.compile(r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}', re.DOTALL)
        self.loop_pattern = re.compile(r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}', re.DOTALL)
        
        # Tech stack to deployment platform mappings
        self.tech_stack_mappings = {
            'azure': {
                'cloud_deployment': 'Azure App Service / AKS',
                'container_orchestration': 'Azure Kubernetes Service (AKS)',
                'cicd_pipeline': 'Azure DevOps Pipelines',
                'iac_tool': 'Azure Resource Manager (ARM) or Terraform',
                'monitoring': 'Azure Monitor / Application Insights',
                'storage': 'Azure Blob Storage / Cosmos DB'
            },
            'aws': {
                'cloud_deployment': 'AWS Elastic Beanstalk / ECS / EKS',
                'container_orchestration': 'Amazon ECS or EKS',
                'cicd_pipeline': 'AWS CodePipeline / GitHub Actions',
                'iac_tool': 'AWS CloudFormation or Terraform',
                'monitoring': 'AWS CloudWatch / X-Ray',
                'storage': 'Amazon S3 / DynamoDB'
            },
            'gcp': {
                'cloud_deployment': 'Google App Engine / GKE',
                'container_orchestration': 'Google Kubernetes Engine (GKE)',
                'cicd_pipeline': 'Cloud Build / GitHub Actions',
                'iac_tool': 'Terraform',
                'monitoring': 'Google Cloud Monitoring',
                'storage': 'Google Cloud Storage / Firestore'
            }
        }
    
    def render(
        self, 
        template: Template, 
        context: Optional[Dict[str, Any]] = None,
        verbosity: Optional[str] = None
    ) -> str:
        """Render template with context and verbosity.
        
        Args:
            template: Template object to render
            context: Dictionary of values for placeholder substitution
            verbosity: Override template verbosity (concise/detailed/expert)
            
        Returns:
            Rendered template string
        """
        context = context or {}
        verbosity = verbosity or template.verbosity
        
        # Enrich context with tech stack deployment options if user profile available
        context = self._enrich_tech_stack_context(context)
        
        content = template.content
        
        # Apply verbosity filtering first
        content = self.apply_verbosity(content, verbosity)
        
        # Process conditionals
        content = self._process_conditionals(content, context)
        
        # Process loops
        content = self._process_loops(content, context)
        
        # Substitute placeholders
        content = self._substitute_placeholders(content, context)
        
        return content.strip()
    
    def _enrich_tech_stack_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with tech stack deployment options from user profile.
        
        Adds tech-specific placeholders like {cloud_deployment}, {container_orchestration}
        based on user's tech_stack_preference profile field.
        
        Args:
            context: Original context dictionary
            
        Returns:
            Enriched context with tech stack placeholders
        """
        # Check if user_profile exists in context
        user_profile = context.get('user_profile', {})
        if not user_profile:
            return context
        
        # Extract tech_stack_preference
        tech_stack = user_profile.get('tech_stack_preference', {})
        if not tech_stack or not isinstance(tech_stack, dict):
            return context
        
        # Get cloud provider from tech stack
        cloud_provider = tech_stack.get('cloud_provider', '').lower()
        
        # Map to deployment options
        if cloud_provider in self.tech_stack_mappings:
            mappings = self.tech_stack_mappings[cloud_provider]
            
            # Add deployment-specific placeholders to context
            context['cloud_deployment'] = mappings.get('cloud_deployment', 'Cloud Platform')
            context['container_orchestration'] = mappings.get('container_orchestration', 'Kubernetes')
            context['cicd_pipeline'] = mappings.get('cicd_pipeline', 'CI/CD Platform')
            context['iac_tool'] = mappings.get('iac_tool', 'Infrastructure as Code')
            context['monitoring_platform'] = mappings.get('monitoring', 'Monitoring Platform')
            context['storage_service'] = mappings.get('storage', 'Cloud Storage')
            
            # Add flag to indicate tech stack is available
            context['has_tech_stack'] = True
            context['cloud_provider_name'] = cloud_provider.upper()
        
        return context
    
    def render_with_placeholders(self, template: Template, **kwargs) -> str:
        """Render template with keyword arguments as placeholders.
        
        Args:
            template: Template object to render
            **kwargs: Placeholder values
            
        Returns:
            Rendered template string
        """
        return self.render(template, context=kwargs)
    
    def apply_verbosity(self, content: str, verbosity: str) -> str:
        """Apply verbosity filtering to content.
        
        Verbosity markers:
        - [concise]...[/concise] - Only in concise mode
        - [detailed]...[/detailed] - Only in detailed mode
        - [expert]...[/expert] - Only in expert mode
        
        Args:
            content: Template content
            verbosity: Target verbosity level
            
        Returns:
            Filtered content
        """
        verbosity_levels = ['concise', 'detailed', 'expert']
        
        if verbosity not in verbosity_levels:
            verbosity = 'concise'
        
        # Remove sections for other verbosity levels
        for level in verbosity_levels:
            if level != verbosity:
                pattern = rf'\[{level}\](.*?)\[/{level}\]'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Remove verbosity markers for current level
        content = re.sub(rf'\[{verbosity}\]', '', content)
        content = re.sub(rf'\[/{verbosity}\]', '', content)
        
        return content
    
    def convert_format(self, content: str, target_format: str) -> str:
        """Convert content to target format.
        
        Args:
            content: Template content
            target_format: Target format (text/markdown/json)
            
        Returns:
            Converted content
        """
        if target_format == 'json':
            # Simple JSON wrapping (can be enhanced)
            return f'{{"response": "{content.replace(chr(34), chr(92) + chr(34))}"}}'
        elif target_format == 'text':
            # Strip markdown formatting
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
            content = re.sub(r'\*(.+?)\*', r'\1', content)  # Italic
            content = re.sub(r'`(.+?)`', r'\1', content)  # Code
            return content
        else:
            # Default: return as markdown
            return content
    
    def _substitute_placeholders(self, content: str, context: Dict[str, Any]) -> str:
        """Substitute {{placeholder}} with values from context.
        
        Args:
            content: Template content with placeholders
            context: Dictionary of values
            
        Returns:
            Content with substituted values
        """
        def replace_placeholder(match):
            key = match.group(1).strip()
            value = context.get(key, f'{{{{MISSING: {key}}}}}')
            return str(value)
        
        return self.placeholder_pattern.sub(replace_placeholder, content)
    
    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#if condition}}...{{/if}} conditionals.
        
        Args:
            content: Template content with conditionals
            context: Dictionary of values
            
        Returns:
            Content with conditionals processed
        """
        def process_conditional(match):
            condition = match.group(1).strip()
            inner_content = match.group(2)
            
            # Evaluate condition
            if condition in context and context[condition]:
                return inner_content
            return ''
        
        return self.conditional_pattern.sub(process_conditional, content)
    
    def _process_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#items}}...{{/items}} loops.
        
        Args:
            content: Template content with loops
            context: Dictionary of values
            
        Returns:
            Content with loops processed
        """
        def process_loop(match):
            list_name = match.group(1).strip()
            inner_content = match.group(2)
            
            if list_name not in context:
                return ''
            
            items = context[list_name]
            if not isinstance(items, list):
                return ''
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    # Substitute placeholders in loop content
                    item_content = self._substitute_placeholders(inner_content, item)
                    result.append(item_content)
                else:
                    # Simple value
                    result.append(str(item))
            
            return '\n'.join(result)
        
        return self.loop_pattern.sub(process_loop, content)
