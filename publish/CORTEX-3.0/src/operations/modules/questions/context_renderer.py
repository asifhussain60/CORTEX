"""
CORTEX 3.0 Phase 2 - Context Renderer
====================================

Context-aware response rendering with dynamic template parameter injection.
Renders templates with intelligent context adaptation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Advanced Response Handling (Task 1)
Integration: Template Selector → Context-Aware Response Rendering
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import re
import time
import logging
from datetime import datetime
import json

# Import from template selector
try:
    from .template_selector import TemplateSelectionResult
except ImportError:
    from src.operations.modules.questions.template_selector import TemplateSelectionResult


@dataclass
class RenderResult:
    """Result of context-aware rendering."""
    rendered_content: str
    template_used: str
    context_applied: Dict[str, Any]
    render_time_ms: float
    warnings: List[str]
    success: bool


class ContextRenderer:
    """
    Context-aware response renderer that adapts templates based on user context.
    
    Features:
    - Dynamic parameter injection
    - Context-aware formatting
    - Namespace-specific styling
    - Performance optimization
    """
    
    def __init__(self, brain_path: str = None):
        """
        Initialize context renderer.
        
        Args:
            brain_path: Path to CORTEX brain directory
        """
        self.brain_path = brain_path
        
        # Context enhancement patterns
        self.enhancement_patterns = {
            'timestamp': self._get_timestamp,
            'current_time': self._get_current_time,
            'user_name': self._get_user_name,
            'project_name': self._get_project_name,
            'file_context': self._get_file_context,
            'brain_status': self._get_brain_status,
            'performance_metrics': self._get_performance_metrics
        }
        
        # Namespace-specific formatting
        self.namespace_styles = {
            'CORTEX_FRAMEWORK': {
                'header_emoji': '🧠',
                'style': 'technical',
                'detail_level': 'detailed'
            },
            'WORKSPACE_CODE': {
                'header_emoji': '🔧',
                'style': 'practical',
                'detail_level': 'focused'
            },
            'GENERAL': {
                'header_emoji': '💡',
                'style': 'helpful',
                'detail_level': 'balanced'
            }
        }
    
    def render(self, template_result: TemplateSelectionResult, context: Dict[str, Any] = None) -> RenderResult:
        """
        Render template with context-aware enhancements.
        
        Args:
            template_result: Result from TemplateSelector
            context: Additional rendering context
            
        Returns:
            RenderResult with rendered content
        """
        start_time = time.time()
        context = context or {}
        warnings = []
        
        try:
            # Step 1: Prepare rendering context
            render_context = self._prepare_render_context(template_result, context)
            
            # Step 2: Get template content
            template_content = self._extract_template_content(template_result)
            
            # Step 3: Apply namespace-specific styling
            styled_content = self._apply_namespace_styling(template_content, template_result.namespace, render_context)
            
            # Step 4: Render template with context
            rendered = self._render_template(styled_content, render_context, warnings)
            
            # Step 5: Post-processing
            final_content = self._post_process(rendered, template_result.namespace, render_context)
            
            render_time_ms = (time.time() - start_time) * 1000
            
            return RenderResult(
                rendered_content=final_content,
                template_used=template_result.template_name,
                context_applied=render_context,
                render_time_ms=render_time_ms,
                warnings=warnings,
                success=True
            )
            
        except Exception as e:
            render_time_ms = (time.time() - start_time) * 1000
            logging.error(f"Rendering failed: {e}")
            
            return RenderResult(
                rendered_content=f"⚠️ Rendering Error: {str(e)}",
                template_used=template_result.template_name,
                context_applied=context,
                render_time_ms=render_time_ms,
                warnings=[f"Rendering failed: {e}"],
                success=False
            )
    
    def _prepare_render_context(self, template_result: TemplateSelectionResult, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive rendering context."""
        render_context = {
            # Base context
            **context,
            **template_result.parameters,
            
            # Template metadata
            'template_name': template_result.template_name,
            'namespace': template_result.namespace,
            'confidence': template_result.confidence,
            'reasoning': template_result.reasoning,
            
            # Auto-generated context
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'render_id': f"render_{int(time.time() * 1000)}"
        }
        
        # Apply context enhancements
        for pattern_name, enhancer in self.enhancement_patterns.items():
            if pattern_name not in render_context:
                try:
                    render_context[pattern_name] = enhancer(render_context)
                except Exception as e:
                    logging.warning(f"Context enhancement failed for {pattern_name}: {e}")
        
        return render_context
    
    def _extract_template_content(self, template_result: TemplateSelectionResult) -> str:
        """Extract renderable content from template."""
        template = template_result.template_content
        
        if isinstance(template, dict):
            # Try different content keys
            for key in ['content', 'template', 'response', 'text']:
                if key in template:
                    return template[key]
            
            # If no content key found, use the template structure
            return self._format_template_structure(template)
        
        elif isinstance(template, str):
            return template
        
        else:
            return str(template)
    
    def _format_template_structure(self, template: Dict[str, Any]) -> str:
        """Format template structure as readable content."""
        name = template.get('name', 'Response')
        
        # Build structured response
        parts = [f"**{name}**"]
        
        if 'description' in template:
            parts.append(f"*{template['description']}*")
        
        if 'response_type' in template:
            response_type = template['response_type']
            if response_type == 'structured':
                parts.append("### Structured Response")
            elif response_type == 'detailed':
                parts.append("### Detailed Information")
            elif response_type == 'table':
                parts.append("### Summary Table")
        
        # Add any specific content
        if 'message' in template:
            parts.append(template['message'])
        
        return '\n\n'.join(parts)
    
    def _apply_namespace_styling(self, content: str, namespace: str, context: Dict[str, Any]) -> str:
        """Apply namespace-specific styling to content."""
        style_config = self.namespace_styles.get(namespace, self.namespace_styles['GENERAL'])
        
        # Add appropriate header
        emoji = style_config['header_emoji']
        styled_content = f"{emoji} **CORTEX {context.get('template_name', 'Response')}**\n"
        styled_content += f"Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX\n\n"
        
        # Add namespace-specific sections based on mandatory format
        styled_content += f"🎯 **My Understanding Of Your Request:**\n"
        styled_content += f"   [Based on {namespace.lower()} namespace detection]\n\n"
        
        styled_content += f"⚠️ **Challenge:** ✓ **Accept**\n"
        styled_content += f"   Template selected with {context.get('confidence', 0):.1f} confidence.\n\n"
        
        styled_content += f"💬 **Response:**\n"
        styled_content += f"{content}\n\n"
        
        styled_content += f"📝 **Your Request:** {context.get('question', '[Request]')}\n\n"
        
        styled_content += f"🔍 **Next Steps:**\n"
        styled_content += f"   1. [Context-specific recommendations]\n"
        styled_content += f"   2. [Additional options]\n"
        styled_content += f"   3. [Further assistance]"
        
        return styled_content
    
    def _render_template(self, content: str, context: Dict[str, Any], warnings: List[str]) -> str:
        """Render template with variable substitution."""
        rendered = content
        
        # Find all template variables {{variable}}
        variables = re.findall(r'\{\{(\w+)\}\}', content)
        
        for var in variables:
            if var in context:
                value = context[var]
                
                # Format value based on type
                if isinstance(value, (dict, list)):
                    formatted_value = json.dumps(value, indent=2)
                elif isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                rendered = rendered.replace(f"{{{{{var}}}}}", formatted_value)
            else:
                warnings.append(f"Missing template variable: {var}")
                rendered = rendered.replace(f"{{{{{var}}}}}", f"[{var}]")
        
        return rendered
    
    def _post_process(self, content: str, namespace: str, context: Dict[str, Any]) -> str:
        """Post-process rendered content."""
        # Clean up extra whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Add footer if needed
        if namespace == 'CORTEX_FRAMEWORK':
            content += f"\n\n---\n*Rendered at {context.get('timestamp')} | Template: {context.get('template_name')}*"
        
        return content.strip()
    
    # Context enhancement methods
    def _get_timestamp(self, context: Dict[str, Any]) -> str:
        """Get current timestamp."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_current_time(self, context: Dict[str, Any]) -> str:
        """Get current time only."""
        return datetime.now().strftime('%H:%M:%S')
    
    def _get_user_name(self, context: Dict[str, Any]) -> str:
        """Get user name from context."""
        return context.get('user_name', 'User')
    
    def _get_project_name(self, context: Dict[str, Any]) -> str:
        """Get project name from context."""
        return context.get('project_name', 'Current Project')
    
    def _get_file_context(self, context: Dict[str, Any]) -> str:
        """Get current file context."""
        current_file = context.get('current_file', 'No file selected')
        return f"Working on: {current_file}"
    
    def _get_brain_status(self, context: Dict[str, Any]) -> str:
        """Get CORTEX brain status."""
        # This would integrate with brain health monitoring
        return "Brain operational (Tier 1: ✅, Tier 2: ✅, Tier 3: ✅)"
    
    def _get_performance_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'selection_time_ms': context.get('selection_time_ms', 0),
            'render_time_ms': 0,  # Will be filled in
            'total_time_ms': 0    # Will be calculated
        }


# Convenience function for integrated template selection and rendering
def render_response_for_question(question: str, context: Dict[str, Any] = None, brain_path: str = None) -> RenderResult:
    """
    Integrated function: Select template and render response for a question.
    
    Args:
        question: User's question
        context: Optional context
        brain_path: Optional brain path
        
    Returns:
        RenderResult with fully rendered response
    """
    # Import here to avoid circular imports
    try:
        from .template_selector import TemplateSelector
    except ImportError:
        from template_selector import TemplateSelector
    
    # Select template
    selector = TemplateSelector(brain_path)
    template_result = selector.select_template(question, context)
    
    # Render with context
    renderer = ContextRenderer(brain_path)
    return renderer.render(template_result, context)


if __name__ == "__main__":
    # Test the context renderer
    print("🧠 CORTEX 3.0 Phase 2 - Context Renderer Test")
    print("=" * 60)
    
    # Test questions
    test_cases = [
        {
            'question': "Show me CORTEX brain health status",
            'context': {'current_file': 'main.py', 'project_name': 'MyProject'}
        },
        {
            'question': "How do I debug my application?",
            'context': {'current_file': 'app.py', 'error_type': 'RuntimeError'}
        },
        {
            'question': "What's the best authentication approach?",
            'context': {'framework': 'Django', 'security_level': 'high'}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['question']}")
        
        try:
            result = render_response_for_question(test_case['question'], test_case['context'])
            
            print(f"   ✅ Success: {result.success}")
            print(f"   Template: {result.template_used}")
            print(f"   Render Time: {result.render_time_ms:.1f}ms")
            print(f"   Warnings: {len(result.warnings)}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"      ⚠️ {warning}")
            
            print("\n   📄 Rendered Content (first 200 chars):")
            print(f"   {result.rendered_content[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()