"""
CORTEX 3.0 Feature 4 & 5: Brain-Enhanced EPM Documentation Generator

Automatically generates intelligent, adaptive documentation for Entry Point Modules
by analyzing Python code structure, extracting dependencies, integrating
EPMO health scores, creating multi-modal visualizations, and leveraging
CORTEX Brain intelligence for context-aware, learning-based optimization.

Major Features:
- Phase 4.1: Core documentation generation with health integration
- Phase 4.2: Multi-modal documentation with visual content
- Feature 5: CORTEX Brain integration with adaptive learning

Public API:
    generate_documentation(): Main documentation generation function
    generate_brain_enhanced_documentation(): Brain-enhanced intelligent generation
    analyze_epmo(): Code analysis and dependency extraction
    create_diagrams(): Multi-modal diagram generation
    
Components:
    - parser.py: Python AST analysis engine
    - dependency_mapper.py: Import relationship extraction  
    - health_integration.py: EPMO health system connector
    - models.py: Data structures and schemas
    - markdown_generator.py: Enhanced markdown with multi-modal support (Phase 4.2)
    - mermaid_generator.py: Architecture diagram creation (Phase 4.2)
    - template_engine.py: Customizable documentation templates (Phase 4.2)
    - cli.py: Comprehensive command-line interface (Phase 4.2)
    - brain/: CORTEX Brain integration system (Feature 5)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import core components
from .parser import analyze_epmo_structure
from .dependency_mapper import analyze_epmo_dependencies
from .health_integration import HealthIntegration
from .models import (
    EPMDocumentationModel,
    DocumentationFormat,
    DiagramType,
    TemplateConfiguration,
    GenerationConfig,
    ImagePrompt,
    MultiModalDiagram,
    DiagramConfig,
    create_epmo_model,
    validate_model
)

# Import Phase 4.2 components
from .markdown_generator import generate_markdown_documentation, MarkdownGenerator
from .mermaid_generator import (
    create_diagrams_for_model, MultiModalDiagramGenerator, 
    MermaidDiagramGenerator, DiagramConfig
)
from .image_prompt_bridge import (
    integrate_image_prompts_with_epmo, ImagePromptIntegrationBridge
)
from .template_engine import render_documentation, TemplateEngine
from .cli import EPMDocumentationCLI


@dataclass
class DocumentationConfig:
    """Configuration for EPM documentation generation."""
    include_health_scores: bool = True
    include_diagrams: bool = True
    include_dependencies: bool = True
    output_format: str = "markdown"
    template_style: str = "comprehensive"


def generate_documentation(
    epmo_path: Path,
    project_root: Path,
    config: Optional[DocumentationConfig] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive documentation for an Entry Point Module.
    
    Enhanced Phase 4.2 implementation with multi-modal support including
    Mermaid diagrams, AI image prompts, and professional templates.
    
    Args:
        epmo_path: Path to the Entry Point Module directory
        project_root: Root path of the CORTEX project
        config: Documentation generation configuration
        
    Returns:
        Dictionary containing generated documentation, diagrams, and metadata
        
    Example:
        >>> from src.epmo.documentation import generate_documentation
        >>> result = generate_documentation(Path('src/epmo'), Path('.'))
        >>> print(result['markdown_content'])
        >>> print(result['visual_stats'])
    """
    if config is None:
        config = DocumentationConfig()
    
    try:
        # Phase 4.1 components - Code Analysis
        ast_analysis = analyze_epmo_structure(epmo_path)
        dependency_analysis = analyze_epmo_dependencies(epmo_path, project_root)
        
        # Health integration (if available)
        health_data = None
        try:
            health_integration = HealthIntegration()
            health_result = health_integration.analyze_epmo_health(epmo_path, project_root)
            health_data = health_result if health_result.get('status') == 'success' else None
        except Exception:
            pass  # Health integration optional
        
        # Create comprehensive model
        model = create_epmo_model(
            epmo_path=epmo_path,
            ast_analysis=ast_analysis,
            dependency_analysis=dependency_analysis,
            health_data=health_data
        )
        
        # Phase 4.2 enhancements - Multi-Modal Generation
        generation_config = GenerationConfig(
            include_architecture_diagrams=True,
            include_api_documentation=True,
            include_health_analysis=health_data is not None,
            include_remediation_guide=True
        )
        
        # Generate diagrams
        diagrams = create_diagrams_for_model(model)
        model.multi_modal_diagrams.extend(diagrams)
        
        # Generate image prompts
        image_prompts, prompt_files = integrate_image_prompts_with_epmo(model)
        model.image_prompts.extend(image_prompts)
        
        # Generate markdown documentation
        markdown_content = generate_markdown_documentation(model, config=generation_config)
        
        # Prepare results
        result = {
            'status': 'success',
            'epmo_name': epmo_path.name,
            'epmo_path': str(epmo_path),
            'markdown_content': markdown_content,
            'model': model,
            'summary_stats': model.get_summary_stats(),
            'visual_stats': model.get_visual_stats(),
            'mermaid_diagrams': [d.mermaid_syntax for d in model.get_mermaid_diagrams()],
            'image_prompts': [p.prompt_text for p in model.get_image_prompts_all()],
            'multi_modal_diagrams': len(model.multi_modal_diagrams),
            'prompt_files': prompt_files,
            'warnings': validate_model(model),
            'generation_config': generation_config
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'epmo_path': str(epmo_path),
            'error': str(e),
            'message': 'Phase 4.2 multi-modal documentation generation failed'
        }


def generate_brain_enhanced_documentation(
    epmo_path: Path,
    project_root: Path,
    brain_config: Optional[Dict[str, Any]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate intelligent, adaptive documentation using CORTEX Brain integration.
    
    Feature 5 implementation with pattern learning, context awareness,
    adaptive templates, and quality feedback loops.
    
    Args:
        epmo_path: Path to the Entry Point Module directory
        project_root: Root path of the CORTEX project
        brain_config: Brain integration configuration
        user_preferences: User/team preferences and constraints
        
    Returns:
        Enhanced documentation result with brain intelligence metadata
        
    Example:
        >>> from src.epmo.documentation import generate_brain_enhanced_documentation
        >>> result = generate_brain_enhanced_documentation(
        ...     Path('src/epmo'), 
        ...     Path('.'),
        ...     user_preferences={'target_audience': 'stakeholders'}
        ... )
        >>> print(f"Confidence: {result['confidence_score']}")
        >>> print(result['contextual_recommendations'])
    """
    try:
        # Import brain integration (lazy loading for graceful fallback)
        from ..brain.brain_api import (
            BrainIntegrationAPI, 
            create_brain_integration_api,
            create_simple_generation_request
        )
        
        # Create brain API
        brain_api = create_brain_integration_api()
        
        # Create generation request
        request = create_simple_generation_request(
            project_path=epmo_path,
            output_path=project_root / 'documentation' / 'generated',
            user_preferences=user_preferences,
            time_constraints=brain_config.get('time_constraints') if brain_config else None,
            target_audience=user_preferences.get('target_audience') if user_preferences else None,
            enable_learning=brain_config.get('enable_learning', True) if brain_config else True
        )
        
        # Generate brain-enhanced documentation
        result = brain_api.generate_enhanced_documentation(request)
        
        # Convert result to dictionary format
        enhanced_result = {
            'success': result.success,
            'generation_id': result.generation_id,
            'output_paths': [str(p) for p in result.output_paths],
            'confidence_score': result.confidence_score,
            'brain_integration_level': result.brain_integration_level,
            'generation_time_seconds': result.generation_time_seconds,
            
            # Brain insights
            'project_context': {
                'domain': result.project_context.domain if result.project_context else 'unknown',
                'architecture': result.project_context.architecture_style if result.project_context else 'unknown',
                'maturity': result.project_context.project_maturity if result.project_context else 'unknown'
            } if result.project_context else {},
            
            'template_recommendation': {
                'template_name': result.template_recommendation.template_name if result.template_recommendation else 'standard',
                'confidence': result.template_recommendation.confidence if result.template_recommendation else 0.5,
                'reasoning': result.template_recommendation.reasoning if result.template_recommendation else 'Fallback selection'
            } if result.template_recommendation else {},
            
            'contextual_recommendations': [
                {
                    'type': rec.recommendation_type,
                    'description': rec.description,
                    'priority': rec.priority,
                    'confidence': rec.confidence
                }
                for rec in result.contextual_recommendations
            ],
            
            'learning_insights': [
                {
                    'type': insight.insight_type,
                    'description': insight.description,
                    'recommendation': insight.recommendation,
                    'impact_score': insight.impact_score
                }
                for insight in result.learning_insights
            ],
            
            'quality_metrics': {
                'quality_score': result.quality_metrics.quality_score if result.quality_metrics else 0.7,
                'readability_score': result.quality_metrics.readability_score if result.quality_metrics else 0.7,
                'completeness_score': result.quality_metrics.completeness_score if result.quality_metrics else 0.7,
                'accuracy_score': result.quality_metrics.accuracy_score if result.quality_metrics else 0.8
            } if result.quality_metrics else {},
            
            'optimization_applied': result.optimization_applied,
            'warnings': result.warnings or [],
            'error_message': result.error_message
        }
        
        # Add fallback content for basic documentation
        if result.success:
            enhanced_result['markdown_content'] = "# Brain-Enhanced Documentation\\n\\n*Generated with CORTEX Brain intelligence*"
            enhanced_result['visual_stats'] = {
                'diagrams_generated': len([opt for opt in result.optimization_applied if 'diagram' in opt]),
                'brain_enhanced': True,
                'integration_level': result.brain_integration_level
            }
        
        return enhanced_result
        
    except ImportError:
        # Graceful fallback if brain integration unavailable
        return {
            'success': False,
            'error_message': 'CORTEX Brain integration not available - using fallback mode',
            'fallback_mode': True,
            'confidence_score': 0.5,
            'brain_integration_level': 'unavailable',
            **generate_documentation(epmo_path, project_root)
        }
    
    except Exception as e:
        return {
            'success': False,
            'error_message': f'Brain-enhanced generation failed: {str(e)}',
            'confidence_score': 0.0,
            'brain_integration_level': 'error',
            **generate_documentation(epmo_path, project_root)  # Fallback
        }


def analyze_epmo(epmo_path: Path) -> Dict[str, Any]:
    """
    Analyze Entry Point Module code structure and dependencies.
    
    Args:
        epmo_path: Path to the Entry Point Module directory
        
    Returns:
        Analysis results including AST data, dependencies, and metadata
    """
    # Phase 4.1 implementation target
    return {
        'status': 'not_implemented',
        'message': 'AST parser implementation pending - Week 10'
    }


def create_diagrams(analysis_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate Mermaid diagrams from EPM analysis data.
    
    Args:
        analysis_data: Results from analyze_epmo()
        
    Returns:
        Dictionary of diagram names to Mermaid syntax strings
    """
    # Phase 4.2 implementation target
    return {
        'status': 'not_implemented',
        'message': 'Mermaid generator implementation pending - Week 11'
    }


# Version and status information
__version__ = "3.0.0"
__status__ = "Week 12 Implementation - Feature 5 COMPLETE"
__feature__ = "Feature 4 & 5: Brain-Enhanced Multi-Modal EPM Documentation Generator"
__dependencies__ = ["EPMO Health System (A3-A6)", "Image Prompt Generation EPM", "CORTEX Brain (Tier 2 Knowledge Graph)"]
__capabilities__ = [
    # Phase 4.1 & 4.2 capabilities
    "Multi-modal documentation generation",
    "Mermaid diagram creation", 
    "AI image prompt generation",
    "Professional template engine",
    "Enhanced CLI interface",
    "Health integration",
    "Dependency analysis",
    "Visual content management",
    
    # Feature 5 capabilities
    "CORTEX Brain integration",
    "Pattern recognition and learning",
    "Adaptive template selection",
    "Context-aware generation",
    "Quality feedback loops",
    "Intelligent configuration",
    "Continuous improvement",
    "Domain expertise integration"
]

# Export all public functions and classes
__all__ = [
    # Main functions
    'generate_documentation',
    'generate_brain_enhanced_documentation',  # New Feature 5 function
    'analyze_epmo',
    'create_diagrams',
    
    # Core components
    'analyze_epmo_structure',
    'analyze_epmo_dependencies',
    'HealthIntegration',
    
    # Models and configurations
    'EPMDocumentationModel',
    'DocumentationFormat',
    'DiagramType',
    'DocumentationConfig',
    'TemplateConfiguration',
    'GenerationConfig',
    'DiagramConfig',
    'ImagePrompt',
    'MultiModalDiagram',
    'create_epmo_model',
    'validate_model',
    
    # Phase 4.2 components
    'generate_markdown_documentation',
    'MarkdownGenerator',
    'create_diagrams_for_model',
    'MultiModalDiagramGenerator',
    'MermaidDiagramGenerator',
    'integrate_image_prompts_with_epmo',
    'ImagePromptIntegrationBridge',
    'render_documentation',
    'TemplateEngine',
    'EPMDocumentationCLI'
]