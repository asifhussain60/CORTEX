"""
Context-Aware Documentation Generator - Domain Intelligence Integration
Feature 5.6: Knowledge Graph Powered Documentation

Uses project context from CORTEX Brain knowledge graph to generate more relevant
and targeted documentation based on domain expertise and best practices.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from .brain_connector import BrainConnector, PatternRecord
from .pattern_learning import PatternLearningEngine


@dataclass
class ProjectContext:
    """Enhanced project context with domain intelligence"""
    project_id: str
    domain: str  # 'web', 'backend', 'ml', 'enterprise', 'research'
    architecture_style: str  # 'monolith', 'microservices', 'serverless', 'distributed'
    technology_stack: List[str]
    business_domain: str  # 'fintech', 'healthcare', 'e-commerce', 'education'
    team_expertise: List[str]
    project_maturity: str  # 'prototype', 'development', 'production', 'legacy'
    compliance_requirements: List[str]
    performance_criticality: str  # 'low', 'medium', 'high', 'critical'
    audience_types: List[str]  # 'developers', 'architects', 'business', 'users'
    documentation_goals: List[str]


@dataclass
class DomainKnowledge:
    """Domain-specific knowledge and patterns"""
    domain: str
    best_practices: List[str]
    common_patterns: List[str]
    required_sections: List[str]
    recommended_tools: List[str]
    quality_criteria: Dict[str, float]
    typical_challenges: List[str]
    documentation_standards: Dict[str, Any]


@dataclass
class ContextualRecommendation:
    """Context-aware recommendation for documentation"""
    recommendation_type: str  # 'content', 'structure', 'tool', 'pattern'
    description: str
    rationale: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    confidence: float
    domain_relevance: float
    implementation_notes: List[str]
    related_patterns: List[str]


class ContextAwareGenerator:
    """
    Intelligent documentation generator that uses project context and domain
    knowledge from CORTEX Brain to create highly relevant, targeted documentation.
    """
    
    def __init__(
        self,
        brain_connector: Optional[BrainConnector] = None,
        pattern_engine: Optional[PatternLearningEngine] = None
    ):
        """
        Initialize context-aware documentation generator
        
        Args:
            brain_connector: Connection to CORTEX Brain
            pattern_engine: Pattern learning engine
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain_connector
        self.pattern_engine = pattern_engine or PatternLearningEngine(brain_connector)
        
        # Domain knowledge cache
        self._domain_knowledge: Dict[str, DomainKnowledge] = {}
        self._load_domain_knowledge()
        
        # Context patterns cache
        self._context_patterns: Dict[str, List[PatternRecord]] = {}
        
        # Best practices registry
        self.best_practices = self._initialize_best_practices()
        
        self.logger.info("ContextAwareGenerator initialized")

    def analyze_project_context(
        self,
        project_path: Path,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> ProjectContext:
        """
        Analyze project to extract comprehensive context information
        
        Args:
            project_path: Path to project root
            existing_context: Pre-existing context data
            
        Returns:
            Comprehensive project context
        """
        try:
            # Basic project analysis
            tech_analysis = self._analyze_technology_stack(project_path)
            architecture_analysis = self._analyze_architecture_style(project_path)
            domain_analysis = self._analyze_business_domain(project_path, existing_context)
            
            # Merge with existing context
            base_context = existing_context or {}
            
            project_context = ProjectContext(
                project_id=base_context.get('project_id', str(hash(str(project_path)))),
                domain=tech_analysis.get('primary_domain', 'general'),
                architecture_style=architecture_analysis.get('style', 'monolith'),
                technology_stack=tech_analysis.get('technologies', []),
                business_domain=domain_analysis.get('business_domain', 'general'),
                team_expertise=base_context.get('team_expertise', []),
                project_maturity=self._assess_project_maturity(project_path),
                compliance_requirements=base_context.get('compliance_requirements', []),
                performance_criticality=base_context.get('performance_criticality', 'medium'),
                audience_types=base_context.get('audience_types', ['developers']),
                documentation_goals=base_context.get('documentation_goals', ['technical_reference'])
            )
            
            self.logger.info(f"Analyzed context for {project_context.domain} project")
            return project_context
            
        except Exception as e:
            self.logger.error(f"Error analyzing project context: {e}")
            return self._create_fallback_context(project_path, existing_context)

    def _analyze_technology_stack(self, project_path: Path) -> Dict[str, Any]:
        """Analyze technology stack from project files"""
        technologies = []
        primary_domain = 'general'
        
        try:
            # Language detection
            language_files = {
                'python': ['*.py', 'requirements.txt', 'setup.py', 'Pipfile'],
                'javascript': ['*.js', '*.jsx', 'package.json', '*.ts', '*.tsx'],
                'java': ['*.java', 'pom.xml', 'build.gradle'],
                'csharp': ['*.cs', '*.csproj', '*.sln'],
                'go': ['*.go', 'go.mod'],
                'rust': ['*.rs', 'Cargo.toml'],
                'php': ['*.php', 'composer.json'],
                'ruby': ['*.rb', 'Gemfile']
            }
            
            detected_languages = []
            for language, patterns in language_files.items():
                for pattern in patterns:
                    if list(project_path.rglob(pattern)):
                        detected_languages.append(language)
                        break
            
            technologies.extend(detected_languages)
            
            # Framework detection
            framework_indicators = {
                'react': ['package.json:react', '*.jsx', '*.tsx'],
                'vue': ['package.json:vue', '*.vue'],
                'angular': ['package.json:@angular', 'angular.json'],
                'django': ['manage.py', 'settings.py'],
                'flask': ['app.py', 'requirements.txt:flask'],
                'fastapi': ['requirements.txt:fastapi'],
                'spring': ['pom.xml:spring', 'build.gradle:spring'],
                'express': ['package.json:express'],
                'nextjs': ['next.config.js', 'package.json:next']
            }
            
            for framework, indicators in framework_indicators.items():
                if self._check_framework_indicators(project_path, indicators):
                    technologies.append(framework)
            
            # Determine primary domain
            if any(tech in technologies for tech in ['react', 'vue', 'angular', 'nextjs']):
                primary_domain = 'web'
            elif any(tech in technologies for tech in ['django', 'flask', 'fastapi', 'spring', 'express']):
                primary_domain = 'backend'
            elif 'python' in technologies and any(file.name in ['requirements.txt'] for file in project_path.rglob('*.txt')):
                # Check for ML libraries
                req_files = list(project_path.rglob('requirements.txt'))
                if req_files:
                    content = req_files[0].read_text()
                    if any(lib in content for lib in ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy']):
                        primary_domain = 'ml'
            
            return {
                'technologies': technologies,
                'primary_domain': primary_domain,
                'languages': detected_languages
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing technology stack: {e}")
            return {'technologies': [], 'primary_domain': 'general', 'languages': []}

    def _check_framework_indicators(self, project_path: Path, indicators: List[str]) -> bool:
        """Check if framework indicators are present"""
        for indicator in indicators:
            if ':' in indicator:
                # File content check
                file_pattern, content_pattern = indicator.split(':')
                files = list(project_path.rglob(file_pattern))
                for file in files:
                    try:
                        if content_pattern in file.read_text():
                            return True
                    except:
                        continue
            else:
                # File existence check
                if list(project_path.rglob(indicator)):
                    return True
        return False

    def _analyze_architecture_style(self, project_path: Path) -> Dict[str, str]:
        """Analyze architectural style from project structure"""
        try:
            # Look for microservices indicators
            if (project_path / 'docker-compose.yml').exists():
                return {'style': 'microservices'}
            
            # Look for serverless indicators
            serverless_files = ['serverless.yml', 'template.yaml', 'sam.yaml']
            if any((project_path / f).exists() for f in serverless_files):
                return {'style': 'serverless'}
            
            # Look for distributed system indicators
            if any((project_path / f).exists() for f in ['kubernetes', 'k8s', 'helm']):
                return {'style': 'distributed'}
            
            # Check for service directories
            service_dirs = [d for d in project_path.iterdir() 
                          if d.is_dir() and 'service' in d.name.lower()]
            if len(service_dirs) > 2:
                return {'style': 'microservices'}
            
            return {'style': 'monolith'}
            
        except Exception as e:
            self.logger.error(f"Error analyzing architecture: {e}")
            return {'style': 'monolith'}

    def _analyze_business_domain(self, project_path: Path, context: Optional[Dict]) -> Dict[str, str]:
        """Analyze business domain from context and project indicators"""
        if context and 'business_domain' in context:
            return {'business_domain': context['business_domain']}
        
        # Domain keywords in project files
        domain_keywords = {
            'fintech': ['payment', 'banking', 'finance', 'trading', 'wallet'],
            'healthcare': ['medical', 'patient', 'health', 'clinical', 'hospital'],
            'e-commerce': ['shop', 'cart', 'order', 'product', 'payment'],
            'education': ['student', 'course', 'lesson', 'learning', 'school'],
            'enterprise': ['employee', 'hr', 'crm', 'erp', 'workflow']
        }
        
        try:
            # Check README and documentation for domain indicators
            readme_files = list(project_path.rglob('README*'))
            content_to_check = []
            
            for readme in readme_files[:3]:  # Check first few READMEs
                try:
                    content_to_check.append(readme.read_text().lower())
                except:
                    continue
            
            # Check package names and directories
            dir_names = [d.name.lower() for d in project_path.rglob('*') if d.is_dir()]
            content_to_check.extend(dir_names)
            
            all_content = ' '.join(content_to_check)
            
            for domain, keywords in domain_keywords.items():
                if any(keyword in all_content for keyword in keywords):
                    return {'business_domain': domain}
            
            return {'business_domain': 'general'}
            
        except Exception as e:
            self.logger.error(f"Error analyzing business domain: {e}")
            return {'business_domain': 'general'}

    def _assess_project_maturity(self, project_path: Path) -> str:
        """Assess project maturity level"""
        try:
            # Check for production indicators
            prod_indicators = [
                'Dockerfile', 'docker-compose.yml', '.github/workflows',
                'CI.yml', 'deployment', 'terraform', 'ansible'
            ]
            
            if any((project_path / indicator).exists() for indicator in prod_indicators):
                return 'production'
            
            # Check for development indicators
            dev_indicators = ['tests', 'test', '__tests__', 'spec']
            test_dirs = [d for d in project_path.rglob('*') 
                        if d.is_dir() and any(indicator in d.name.lower() for indicator in dev_indicators)]
            
            if test_dirs:
                return 'development'
            
            # Check project size and complexity
            py_files = list(project_path.rglob('*.py'))
            js_files = list(project_path.rglob('*.js'))
            total_files = len(py_files) + len(js_files)
            
            if total_files > 50:
                return 'development'
            elif total_files > 5:
                return 'prototype'
            else:
                return 'prototype'
                
        except Exception as e:
            self.logger.error(f"Error assessing project maturity: {e}")
            return 'development'

    def generate_contextual_recommendations(
        self,
        context: ProjectContext,
        current_config: Optional[Dict[str, Any]] = None
    ) -> List[ContextualRecommendation]:
        """
        Generate context-aware recommendations for documentation
        
        Args:
            context: Project context information
            current_config: Current documentation configuration
            
        Returns:
            List of contextual recommendations
        """
        recommendations = []
        
        try:
            # Domain-specific recommendations
            domain_recs = self._get_domain_recommendations(context)
            recommendations.extend(domain_recs)
            
            # Architecture-specific recommendations
            arch_recs = self._get_architecture_recommendations(context)
            recommendations.extend(arch_recs)
            
            # Business domain recommendations
            business_recs = self._get_business_domain_recommendations(context)
            recommendations.extend(business_recs)
            
            # Audience-specific recommendations
            audience_recs = self._get_audience_recommendations(context)
            recommendations.extend(audience_recs)
            
            # Pattern-based recommendations
            if self.pattern_engine:
                pattern_recs = self._get_pattern_based_recommendations(context)
                recommendations.extend(pattern_recs)
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda r: (
                {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[r.priority],
                r.confidence
            ), reverse=True)
            
            self.logger.info(f"Generated {len(recommendations)} contextual recommendations")
            return recommendations[:15]  # Top 15 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []

    def _get_domain_recommendations(self, context: ProjectContext) -> List[ContextualRecommendation]:
        """Get domain-specific documentation recommendations"""
        recommendations = []
        domain = context.domain
        
        domain_guidance = {
            'web': {
                'sections': ['component_architecture', 'ui_patterns', 'responsive_design'],
                'tools': ['storybook', 'figma_integration'],
                'patterns': ['component_documentation', 'user_journey_mapping']
            },
            'backend': {
                'sections': ['api_documentation', 'data_flow', 'security_considerations'],
                'tools': ['swagger', 'postman_collections'],
                'patterns': ['endpoint_documentation', 'database_schema']
            },
            'ml': {
                'sections': ['model_architecture', 'data_pipeline', 'performance_metrics'],
                'tools': ['tensorboard', 'mlflow'],
                'patterns': ['experiment_tracking', 'model_versioning']
            },
            'enterprise': {
                'sections': ['integration_points', 'compliance_matrix', 'scalability_analysis'],
                'tools': ['enterprise_diagrams', 'compliance_tracking'],
                'patterns': ['enterprise_patterns', 'governance_documentation']
            }
        }
        
        if domain in domain_guidance:
            guidance = domain_guidance[domain]
            
            # Section recommendations
            for section in guidance['sections']:
                recommendations.append(ContextualRecommendation(
                    recommendation_type='content',
                    description=f"Include {section.replace('_', ' ')} section",
                    rationale=f"Essential for {domain} projects",
                    priority='high',
                    confidence=0.85,
                    domain_relevance=0.9,
                    implementation_notes=[f"Document {section} with domain-specific details"],
                    related_patterns=[]
                ))
            
            # Tool recommendations
            for tool in guidance['tools']:
                recommendations.append(ContextualRecommendation(
                    recommendation_type='tool',
                    description=f"Integrate {tool.replace('_', ' ')} for enhanced documentation",
                    rationale=f"Standard tool for {domain} documentation",
                    priority='medium',
                    confidence=0.8,
                    domain_relevance=0.85,
                    implementation_notes=[f"Set up {tool} integration"],
                    related_patterns=[]
                ))
        
        return recommendations

    def _get_architecture_recommendations(self, context: ProjectContext) -> List[ContextualRecommendation]:
        """Get architecture-specific recommendations"""
        recommendations = []
        arch_style = context.architecture_style
        
        arch_guidance = {
            'microservices': [
                {
                    'type': 'structure',
                    'desc': 'Service interaction diagrams',
                    'priority': 'critical',
                    'rationale': 'Essential for understanding service boundaries'
                },
                {
                    'type': 'content',
                    'desc': 'API contracts and versioning',
                    'priority': 'critical',
                    'rationale': 'Critical for service interoperability'
                }
            ],
            'serverless': [
                {
                    'type': 'content',
                    'desc': 'Function trigger documentation',
                    'priority': 'high',
                    'rationale': 'Clarifies event-driven architecture'
                },
                {
                    'type': 'content',
                    'desc': 'Cold start considerations',
                    'priority': 'medium',
                    'rationale': 'Important performance consideration'
                }
            ],
            'monolith': [
                {
                    'type': 'structure',
                    'desc': 'Module dependency mapping',
                    'priority': 'high',
                    'rationale': 'Helps understand internal structure'
                }
            ]
        }
        
        if arch_style in arch_guidance:
            for guidance in arch_guidance[arch_style]:
                recommendations.append(ContextualRecommendation(
                    recommendation_type=guidance['type'],
                    description=guidance['desc'],
                    rationale=guidance['rationale'],
                    priority=guidance['priority'],
                    confidence=0.9,
                    domain_relevance=0.95,
                    implementation_notes=[f"Focus on {arch_style} specific concerns"],
                    related_patterns=[]
                ))
        
        return recommendations

    def _get_business_domain_recommendations(self, context: ProjectContext) -> List[ContextualRecommendation]:
        """Get business domain specific recommendations"""
        recommendations = []
        business_domain = context.business_domain
        
        compliance_guidance = {
            'fintech': ['PCI-DSS', 'SOX', 'data_encryption'],
            'healthcare': ['HIPAA', 'patient_privacy', 'audit_trails'],
            'e-commerce': ['GDPR', 'payment_security', 'user_data_protection']
        }
        
        if business_domain in compliance_guidance:
            for requirement in compliance_guidance[business_domain]:
                recommendations.append(ContextualRecommendation(
                    recommendation_type='content',
                    description=f"Document {requirement.replace('_', ' ')} compliance",
                    rationale=f"Required for {business_domain} compliance",
                    priority='critical',
                    confidence=0.95,
                    domain_relevance=1.0,
                    implementation_notes=[f"Include {requirement} documentation"],
                    related_patterns=['compliance_documentation']
                ))
        
        return recommendations

    def _get_audience_recommendations(self, context: ProjectContext) -> List[ContextualRecommendation]:
        """Get audience-specific recommendations"""
        recommendations = []
        
        audience_guidance = {
            'developers': {
                'focus': 'technical_details',
                'sections': ['setup_guide', 'api_reference', 'troubleshooting'],
                'style': 'technical'
            },
            'architects': {
                'focus': 'system_design', 
                'sections': ['architecture_overview', 'design_decisions', 'trade-offs'],
                'style': 'high_level'
            },
            'business': {
                'focus': 'value_proposition',
                'sections': ['business_value', 'roi_analysis', 'user_benefits'],
                'style': 'executive'
            },
            'users': {
                'focus': 'user_experience',
                'sections': ['user_guide', 'tutorials', 'faq'],
                'style': 'user_friendly'
            }
        }
        
        for audience in context.audience_types:
            if audience in audience_guidance:
                guidance = audience_guidance[audience]
                
                recommendations.append(ContextualRecommendation(
                    recommendation_type='structure',
                    description=f"Optimize for {audience} audience with {guidance['focus']} focus",
                    rationale=f"Tailored to {audience} information needs",
                    priority='high',
                    confidence=0.8,
                    domain_relevance=0.7,
                    implementation_notes=[f"Use {guidance['style']} writing style"],
                    related_patterns=['audience_specific_documentation']
                ))
        
        return recommendations

    def _get_pattern_based_recommendations(self, context: ProjectContext) -> List[ContextualRecommendation]:
        """Get recommendations based on learned patterns"""
        recommendations = []
        
        try:
            # Search for relevant patterns
            context_tags = [
                context.domain,
                context.architecture_style,
                context.business_domain,
                context.project_maturity
            ] + context.technology_stack
            
            relevant_patterns = []
            if self.brain:
                for tag in context_tags:
                    patterns = self.brain.search_patterns_by_intent(
                        f"documentation {tag}",
                        context_tags
                    )
                    relevant_patterns.extend(patterns)
            
            # Create recommendations from high-confidence patterns
            for pattern in relevant_patterns:
                if pattern.confidence > 0.8:
                    recommendations.append(ContextualRecommendation(
                        recommendation_type='pattern',
                        description=f"Apply pattern: {pattern.name}",
                        rationale=f"Successful pattern with {pattern.success_count} successes",
                        priority='medium',
                        confidence=pattern.confidence,
                        domain_relevance=0.8,
                        implementation_notes=[pattern.description],
                        related_patterns=[pattern.pattern_id]
                    ))
            
        except Exception as e:
            self.logger.error(f"Error getting pattern recommendations: {e}")
        
        return recommendations

    def enhance_documentation_config(
        self,
        base_config: Dict[str, Any],
        context: ProjectContext,
        recommendations: List[ContextualRecommendation]
    ) -> Dict[str, Any]:
        """
        Enhance documentation configuration with context-aware optimizations
        
        Args:
            base_config: Base documentation configuration
            context: Project context
            recommendations: Contextual recommendations
            
        Returns:
            Enhanced configuration with context optimizations
        """
        enhanced_config = base_config.copy()
        
        try:
            # Apply domain-specific enhancements
            enhanced_config = self._apply_domain_enhancements(enhanced_config, context)
            
            # Apply architecture-specific enhancements
            enhanced_config = self._apply_architecture_enhancements(enhanced_config, context)
            
            # Apply recommendation-based enhancements
            enhanced_config = self._apply_recommendation_enhancements(
                enhanced_config, recommendations
            )
            
            # Add context metadata
            enhanced_config['context_metadata'] = {
                'domain': context.domain,
                'architecture': context.architecture_style,
                'business_domain': context.business_domain,
                'maturity': context.project_maturity,
                'audiences': context.audience_types,
                'enhancement_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("Configuration enhanced with context awareness")
            return enhanced_config
            
        except Exception as e:
            self.logger.error(f"Error enhancing configuration: {e}")
            return enhanced_config

    def _apply_domain_enhancements(self, config: Dict[str, Any], context: ProjectContext) -> Dict[str, Any]:
        """Apply domain-specific configuration enhancements"""
        domain = context.domain
        
        domain_configs = {
            'web': {
                'include_ui_components': True,
                'visual_priority': True,
                'responsive_design_docs': True
            },
            'backend': {
                'api_documentation': True,
                'include_performance_metrics': True,
                'security_documentation': True
            },
            'ml': {
                'include_model_metrics': True,
                'data_pipeline_docs': True,
                'experiment_tracking': True
            }
        }
        
        if domain in domain_configs:
            config.update(domain_configs[domain])
        
        return config

    def _apply_architecture_enhancements(self, config: Dict[str, Any], context: ProjectContext) -> Dict[str, Any]:
        """Apply architecture-specific enhancements"""
        arch_style = context.architecture_style
        
        arch_configs = {
            'microservices': {
                'service_boundary_diagrams': True,
                'api_contract_docs': True,
                'distributed_tracing_docs': True
            },
            'serverless': {
                'function_trigger_docs': True,
                'event_flow_diagrams': True,
                'cold_start_optimization_docs': True
            },
            'monolith': {
                'module_dependency_diagrams': True,
                'internal_api_docs': True
            }
        }
        
        if arch_style in arch_configs:
            config.update(arch_configs[arch_style])
        
        return config

    def _apply_recommendation_enhancements(
        self, 
        config: Dict[str, Any],
        recommendations: List[ContextualRecommendation]
    ) -> Dict[str, Any]:
        """Apply enhancements based on recommendations"""
        high_priority_recs = [r for r in recommendations 
                             if r.priority in ['critical', 'high'] and r.confidence > 0.8]
        
        for rec in high_priority_recs:
            if rec.recommendation_type == 'content':
                # Add recommended content sections
                if 'additional_sections' not in config:
                    config['additional_sections'] = []
                section_name = rec.description.lower().replace(' ', '_')
                config['additional_sections'].append(section_name)
            
            elif rec.recommendation_type == 'tool':
                # Enable recommended tools
                tool_name = rec.description.split()[1]  # Extract tool name
                config[f'enable_{tool_name}'] = True
            
            elif rec.recommendation_type == 'structure':
                # Apply structural recommendations
                if 'diagram' in rec.description.lower():
                    config['enhanced_diagrams'] = True
                if 'interaction' in rec.description.lower():
                    config['interaction_diagrams'] = True
        
        return config

    def _load_domain_knowledge(self):
        """Load domain knowledge from brain or initialize defaults"""
        # In full implementation, this would load from brain knowledge graph
        self._initialize_default_domain_knowledge()

    def _initialize_default_domain_knowledge(self):
        """Initialize default domain knowledge"""
        domains = ['web', 'backend', 'ml', 'enterprise', 'general']
        
        for domain in domains:
            self._domain_knowledge[domain] = DomainKnowledge(
                domain=domain,
                best_practices=[f"{domain}_best_practice_1", f"{domain}_best_practice_2"],
                common_patterns=[f"{domain}_pattern_1", f"{domain}_pattern_2"],
                required_sections=[f"{domain}_section_1", f"{domain}_section_2"],
                recommended_tools=[f"{domain}_tool_1", f"{domain}_tool_2"],
                quality_criteria={'readability': 0.8, 'completeness': 0.85},
                typical_challenges=[f"{domain}_challenge_1"],
                documentation_standards={'format': 'markdown', 'style': 'technical'}
            )

    def _initialize_best_practices(self) -> Dict[str, List[str]]:
        """Initialize best practices registry"""
        return {
            'general': [
                'Use clear, concise language',
                'Include code examples',
                'Provide setup instructions',
                'Document error handling'
            ],
            'web': [
                'Document component props',
                'Include responsive design notes',
                'Provide browser compatibility info',
                'Document accessibility features'
            ],
            'backend': [
                'Document API endpoints',
                'Include authentication details',
                'Provide error response formats',
                'Document rate limiting'
            ]
        }

    def _create_fallback_context(
        self,
        project_path: Path,
        existing_context: Optional[Dict[str, Any]]
    ) -> ProjectContext:
        """Create minimal fallback context when analysis fails"""
        return ProjectContext(
            project_id=str(hash(str(project_path))),
            domain='general',
            architecture_style='monolith',
            technology_stack=[],
            business_domain='general',
            team_expertise=[],
            project_maturity='development',
            compliance_requirements=[],
            performance_criticality='medium',
            audience_types=['developers'],
            documentation_goals=['technical_reference']
        )

    def get_context_analytics(self) -> Dict[str, Any]:
        """Get analytics on context analysis and recommendations"""
        return {
            "domain_knowledge_loaded": len(self._domain_knowledge),
            "pattern_cache_size": len(self._context_patterns),
            "available_domains": list(self._domain_knowledge.keys()),
            "best_practices_count": sum(len(practices) for practices in self.best_practices.values()),
            "context_analysis_capabilities": [
                "technology_stack_detection",
                "architecture_style_analysis", 
                "business_domain_inference",
                "project_maturity_assessment"
            ]
        }