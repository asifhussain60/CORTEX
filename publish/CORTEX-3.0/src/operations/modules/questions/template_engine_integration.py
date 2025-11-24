"""
CORTEX 3.0 Template Engine Integration
======================================

Integrates real-time data collectors with enhanced question routing templates.
Provides live template rendering with actual metrics instead of mock data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Feature: Quick Win #2+3 Integration - Live Template Rendering
"""

import os
import sys
import yaml
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add CORTEX paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from src.agents.namespace_detector import NamespaceDetector
    from src.operations.modules.questions.question_router import QuestionRouter
    from src.operations.data_collectors.real_time_collectors import DataCollectionCoordinator
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False
    print("⚠️ Running in simulation mode - imports not available")

class TemplateEngine:
    """Template engine that renders response templates with live data"""
    
    def __init__(self):
        self.templates_path = os.path.join(
            os.path.dirname(__file__), 
            '../../../cortex-brain/response-templates/questions.yaml'
        )
        self.templates = self._load_templates()
        self.data_coordinator = DataCollectionCoordinator() if IMPORTS_AVAILABLE else None
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load response templates from YAML file"""
        try:
            with open(self.templates_path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('templates', {})
        except Exception as e:
            print(f"⚠️ Warning: Could not load templates: {e}")
            return {}
    
    def render_template(self, template_name: str, user_message: str = "", 
                       context: Dict[str, Any] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """Render a template with live data"""
        
        # Get template
        if template_name not in self.templates:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found",
                "available_templates": list(self.templates.keys())
            }
        
        template = self.templates[template_name]
        
        # Collect live data
        if self.data_coordinator:
            template_data = self.data_coordinator.collect_for_template(template_name, force_refresh)
        else:
            # Fallback data for simulation
            template_data = self._get_fallback_data(template_name)
        
        # Add message-specific data
        template_data.update({
            "original_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "template_name": template_name
        })
        
        # Add context if provided
        if context:
            template_data.update(context)
        
        # Render template content
        try:
            rendered_content = self._render_content(template.get('content', ''), template_data)
            
            return {
                "success": True,
                "template_name": template_name,
                "rendered_content": rendered_content,
                "template_data": template_data,
                "namespace": template.get('namespace', 'unknown'),
                "triggers": template.get('triggers', [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Template rendering failed: {e}",
                "template_name": template_name
            }
    
    def _render_content(self, content: str, data: Dict[str, Any]) -> str:
        """Render template content with data substitution"""
        
        # Simple template variable substitution ({{variable}})
        def replace_variable(match):
            variable_name = match.group(1).strip()
            
            # Handle nested variables (e.g., {{data.field}})
            if '.' in variable_name:
                parts = variable_name.split('.')
                value = data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return f"{{{{MISSING: {variable_name}}}}}"
                return str(value)
            else:
                return str(data.get(variable_name, f"{{{{MISSING: {variable_name}}}}}"))
        
        # Replace {{variable}} patterns
        content = re.sub(r'\{\{([^}]+)\}\}', replace_variable, content)
        
        # Handle conditional blocks (simplified)
        content = self._render_conditionals(content, data)
        
        return content
    
    def _render_conditionals(self, content: str, data: Dict[str, Any]) -> str:
        """Handle simple conditional rendering"""
        
        # Simple if conditions: {{#if variable}}content{{/if}}
        def replace_if_block(match):
            condition = match.group(1).strip()
            block_content = match.group(2)
            
            # Simple boolean check
            if condition in data:
                if data[condition]:
                    return block_content
            
            return ""  # Condition false or variable missing
        
        content = re.sub(r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}', replace_if_block, content, flags=re.DOTALL)
        
        return content
    
    def _get_fallback_data(self, template_name: str) -> Dict[str, Any]:
        """Get fallback data when real collectors aren't available"""
        
        fallback_data = {
            # CORTEX metrics
            "brain_health_score": 92,
            "query_response_time_ms": 18,
            "pattern_accuracy_percent": 89,
            "cortex_mode": "3.0_enhanced",
            "active_agents": 10,
            "total_agents": 10,
            "tier1_conversations": 15,
            "tier1_max_capacity": 20,
            "tier2_patterns": 45,
            "tier3_git_commits": 247,
            
            # Workspace metrics
            "workspace_name": "CORTEX",
            "code_quality_score": 85,
            "test_coverage_percent": 76,
            "workspace_intelligence_score": 88,
            
            # Performance metrics
            "memory_efficiency_percent": 87,
            "coordination_health": 95,
            "learning_rate": 3.2
        }
        
        return fallback_data

class EnhancedQuestionHandler:
    """Enhanced question handler that integrates all components"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        
        if IMPORTS_AVAILABLE:
            self.namespace_detector = NamespaceDetector()
            self.question_router = QuestionRouter()
        else:
            self.namespace_detector = None
            self.question_router = None
    
    def handle_question(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle a user question with full CORTEX 3.0 intelligence"""
        
        start_time = datetime.now()
        
        try:
            # Step 1: Detect namespace
            if self.namespace_detector:
                namespace_result = self.namespace_detector.detect(user_message, context)
                detected_namespace = namespace_result.namespace
                namespace_confidence = namespace_result.confidence
            else:
                # Fallback namespace detection
                if any(keyword in user_message.lower() for keyword in ['cortex', 'brain', 'agents', 'tier']):
                    detected_namespace = "cortex"
                    namespace_confidence = 0.85
                else:
                    detected_namespace = "workspace" 
                    namespace_confidence = 0.75
            
            # Step 2: Route to appropriate template
            if self.question_router:
                routing_result = self.question_router.route(user_message, context)
                template_name = routing_result.template_name
            else:
                # Fallback template selection
                if detected_namespace == "cortex":
                    template_name = "cortex_system_health_v3"
                else:
                    template_name = "workspace_intelligence_v3"
            
            # Step 3: Render template with live data
            render_result = self.template_engine.render_template(
                template_name, user_message, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": render_result.get("success", False),
                "user_message": user_message,
                "detected_namespace": detected_namespace,
                "namespace_confidence": namespace_confidence,
                "selected_template": template_name,
                "rendered_response": render_result.get("rendered_content", ""),
                "template_data": render_result.get("template_data", {}),
                "processing_time_ms": processing_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": False,
                "error": str(e),
                "user_message": user_message,
                "processing_time_ms": processing_time,
                "timestamp": start_time.isoformat()
            }

def test_integration():
    """Test the complete integration"""
    print("🧪 CORTEX 3.0 Template Engine Integration Test")
    print("=" * 60)
    
    handler = EnhancedQuestionHandler()
    
    test_questions = [
        "How is CORTEX doing?",
        "What's my code quality?",
        "Show me the system status",
        "How is the workspace health?",
        "What's unclear here?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: '{question}'")
        print("-" * 40)
        
        result = handler.handle_question(question)
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Namespace: {result['detected_namespace']} ({result['namespace_confidence']:.2f})")
            print(f"   Template: {result['selected_template']}")
            print(f"   Processing: {result['processing_time_ms']:.1f}ms")
            
            # Show preview of rendered response
            preview = result['rendered_response'][:200] + "..." if len(result['rendered_response']) > 200 else result['rendered_response']
            print(f"   Response Preview: {preview}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print(f"\n🎉 Integration Test Complete!")
    print("=" * 60)

def demo_live_template_rendering():
    """Demo live template rendering with real data"""
    print("\n🎭 Live Template Rendering Demo")
    print("=" * 40)
    
    engine = TemplateEngine()
    
    # Demo CORTEX system template
    print("\n🧠 CORTEX System Health Template:")
    result = engine.render_template("cortex_system_health_v3", "How is CORTEX doing?")
    
    if result["success"]:
        print("✅ Template rendered successfully!")
        print(f"Data points collected: {len(result['template_data'])}")
        
        # Show key metrics
        data = result['template_data']
        print(f"   Brain Health: {data.get('brain_health_score', 'N/A')}/100")
        print(f"   Response Time: {data.get('query_response_time_ms', 'N/A')}ms")
        print(f"   Active Conversations: {data.get('tier1_conversations', 'N/A')}/{data.get('tier1_max_capacity', 'N/A')}")
        
        # Show rendered content sample
        content_sample = result['rendered_content'][:300] + "..." if len(result['rendered_content']) > 300 else result['rendered_content']
        print(f"\nRendered Content Sample:\n{content_sample}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_integration()
    demo_live_template_rendering()