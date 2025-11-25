# Investigation Router - CORTEX 3.0 Guided Deep Dive Implementation
# Purpose: Handle "Investigate why..." commands with intelligent token budget management
# Architecture: Phased investigation with user checkpoints and relationship confidence scoring

import logging
from typing import Dict, List, Tuple, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
import asyncio

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.cortex_agents.intent_router import IntentRouter

from src.cortex_agents.health_validator.agent import HealthValidator
from src.tier2.knowledge_graph import KnowledgeGraph


class InvestigationPhase(Enum):
    """Investigation phases with token budgets"""
    DISCOVERY = "discovery"      # 1,500 tokens - Initial scope and immediate context
    ANALYSIS = "analysis"        # 2,000 tokens - Deep dive with relationship traversal
    SYNTHESIS = "synthesis"      # 1,500 tokens - Findings consolidation and recommendations


@dataclass
class TokenBudget:
    """Token budget allocation for investigation phases"""
    phase: InvestigationPhase
    allocated: int
    consumed: int = 0
    remaining: int = 0
    
    def __post_init__(self):
        self.remaining = self.allocated - self.consumed
    
    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= 0
    
    def consume(self, tokens: int) -> bool:
        """Consume tokens from budget. Returns True if budget allows."""
        if tokens > self.remaining:
            return False
        self.consumed += tokens
        self.remaining -= tokens
        return True


@dataclass
class InvestigationContext:
    """Context for investigation including target, relationships, and findings"""
    target_entity: str
    entity_type: str  # 'file', 'component', 'function', 'issue'
    initial_query: str
    current_phase: InvestigationPhase
    budget: TokenBudget
    
    # Investigation data
    direct_relationships: List[Dict[str, Any]] = None
    confidence_threshold: float = 0.7
    findings: List[Dict[str, Any]] = None
    user_checkpoints: List[str] = None
    
    def __post_init__(self):
        if self.direct_relationships is None:
            self.direct_relationships = []
        if self.findings is None:
            self.findings = []
        if self.user_checkpoints is None:
            self.user_checkpoints = []


class InvestigationRouter:
    """
    Routes and manages investigation commands with guided deep dive pattern.
    
    Handles "Investigate why this view..." type requests by:
    1. Intelligent scope detection from query
    2. Phased investigation with token budgets
    3. User checkpoints between phases
    4. Relationship confidence scoring
    """
    
    def __init__(self, intent_router, health_validator: HealthValidator, knowledge_graph: KnowledgeGraph):
        self.logger = logging.getLogger(__name__)
        self.intent_router = intent_router
        self.health_validator = health_validator
        self.knowledge_graph = knowledge_graph
        
        # Initialize Enhanced Health Validator for investigation-specific analysis
        try:
            from src.cortex_agents.health_validator.enhanced_validator import EnhancedHealthValidator
            # Use enhanced validator if available, fall back to base validator
            if isinstance(health_validator, EnhancedHealthValidator):
                self.enhanced_validator = health_validator
            else:
                # Wrap existing validator with enhanced capabilities
                self.enhanced_validator = EnhancedHealthValidator(
                    name="enhanced_health_validator",
                    tier1_api=getattr(health_validator, 'tier1_api', None),
                    tier2_kg=getattr(health_validator, 'tier2_kg', None),
                    tier3_context=getattr(health_validator, 'tier3_context', None)
                )
        except ImportError:
            self.enhanced_validator = health_validator  # Fallback to base validator
        
        # Investigation patterns for entity detection
        self.investigation_patterns = {
            'view_analysis': r'investigate\s+(?:why\s+)?(?:this\s+)?view\s+(\w+)',
            'component_issue': r'investigate\s+(?:why\s+)?(?:the\s+)?(\w+)\s+(?:component|module)',
            'function_behavior': r'investigate\s+(?:why\s+)?(?:the\s+)?(\w+)\s+(?:function|method)',
            'file_dependency': r'investigate\s+(?:why\s+)?(?:the\s+)?(\w+\.?\w*)\s+(?:file|dependency)',
            'general_issue': r'investigate\s+(?:why\s+)?(.+?)(?:\s+(?:is|isn\'t|doesn\'t|won\'t)|\s*$)'
        }
    
    async def handle_investigation(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for investigation commands.
        
        Args:
            query: User's investigation request
            context: Optional context from VS Code or other sources
            
        Returns:
            Investigation results with phase completion status
        """
        self.logger.info(f"Starting investigation: {query}")
        
        # Phase 1: Discovery - Initial scope and entity detection
        investigation_context = await self._discovery_phase(query, context)
        
        if not investigation_context:
            return {
                "success": False,
                "error": "Could not identify investigation target from query",
                "suggestion": "Try: 'Investigate why the UserLoginView component...' or 'Investigate why this file...'"
            }
        
        # Check if user wants to proceed to analysis phase
        user_response = await self._user_checkpoint(
            investigation_context,
            f"Found {investigation_context.target_entity} with {len(investigation_context.direct_relationships)} direct relationships. "
            f"Continue with deep analysis? (Budget: {investigation_context.budget.remaining} tokens remaining)"
        )
        
        if not user_response.get('proceed', True):
            return self._generate_discovery_report(investigation_context)
        
        # Phase 2: Analysis - Deep relationship traversal
        await self._analysis_phase(investigation_context)
        
        # Check if user wants synthesis phase
        user_response = await self._user_checkpoint(
            investigation_context,
            f"Analysis complete with {len(investigation_context.findings)} findings. "
            f"Generate synthesis report? (Budget: {investigation_context.budget.remaining} tokens remaining)"
        )
        
        if not user_response.get('proceed', True):
            return self._generate_analysis_report(investigation_context)
        
        # Phase 3: Synthesis - Consolidate findings and recommendations
        await self._synthesis_phase(investigation_context)
        
        return self._generate_final_report(investigation_context)
    
    async def _discovery_phase(self, query: str, context: Dict[str, Any] = None) -> Optional[InvestigationContext]:
        """
        Phase 1: Discovery - Detect target entity and immediate relationships
        Budget: 1,500 tokens
        """
        budget = TokenBudget(InvestigationPhase.DISCOVERY, 1500)
        
        # Entity detection from query
        target_entity, entity_type = self._extract_target_entity(query)
        if not target_entity:
            return None
        
        investigation_context = InvestigationContext(
            target_entity=target_entity,
            entity_type=entity_type,
            initial_query=query,
            current_phase=InvestigationPhase.DISCOVERY,
            budget=budget
        )
        
        # Get immediate context - consume tokens
        token_cost = len(query.split()) * 2  # Rough estimate
        if not budget.consume(token_cost):
            self.logger.warning("Discovery phase budget exhausted during entity detection")
            return investigation_context
        
        # Find direct relationships using Knowledge Graph
        try:
            relationships = await self._get_direct_relationships(target_entity, entity_type)
            investigation_context.direct_relationships = relationships
            
            # Estimate token cost for relationships
            relationship_tokens = len(str(relationships)) // 4  # Rough estimate: 4 chars per token
            budget.consume(relationship_tokens)
            
        except Exception as e:
            self.logger.error(f"Error getting relationships for {target_entity}: {e}")
        
        # Get current workspace context if available
        if context and context.get('current_file'):
            workspace_context = await self._get_workspace_context(context['current_file'])
            investigation_context.findings.append({
                'type': 'workspace_context',
                'data': workspace_context,
                'confidence': 0.9
            })
        
        self.logger.info(f"Discovery phase complete. Budget: {budget.consumed}/{budget.allocated} tokens used")
        return investigation_context
    
    async def _analysis_phase(self, investigation_context: InvestigationContext) -> None:
        """
        Phase 2: Analysis - Deep relationship traversal with confidence scoring
        Budget: 2,000 tokens
        """
        investigation_context.current_phase = InvestigationPhase.ANALYSIS
        investigation_context.budget = TokenBudget(InvestigationPhase.ANALYSIS, 2000)
        
        # Traverse relationships by confidence level
        high_confidence_rels = [r for r in investigation_context.direct_relationships 
                               if r.get('confidence', 0) >= 0.8]
        medium_confidence_rels = [r for r in investigation_context.direct_relationships 
                                 if 0.6 <= r.get('confidence', 0) < 0.8]
        
        # Process high confidence relationships first
        for relationship in high_confidence_rels:
            if investigation_context.budget.is_exhausted:
                break
                
            finding = await self._analyze_relationship(relationship, investigation_context)
            if finding:
                investigation_context.findings.append(finding)
        
        # Process medium confidence if budget allows
        if not investigation_context.budget.is_exhausted:
            for relationship in medium_confidence_rels:
                if investigation_context.budget.is_exhausted:
                    break
                    
                finding = await self._analyze_relationship(relationship, investigation_context)
                if finding:
                    investigation_context.findings.append(finding)
        
        # Use Enhanced Health Validator for additional insights
        if not investigation_context.budget.is_exhausted:
            health_insights = await self._get_health_insights(
                investigation_context.target_entity,
                investigation_context.entity_type
            )
            if health_insights:
                investigation_context.findings.extend(health_insights)
        
        # Execute specialized analysis plugins
        if not investigation_context.budget.is_exhausted:
            plugin_findings = await self._execute_analysis_plugins(investigation_context)
            if plugin_findings:
                investigation_context.findings.extend(plugin_findings)
        
        self.logger.info(f"Analysis phase complete. {len(investigation_context.findings)} findings generated")
    
    async def _synthesis_phase(self, investigation_context: InvestigationContext) -> None:
        """
        Phase 3: Synthesis - Consolidate findings and generate recommendations
        Budget: 1,500 tokens
        """
        investigation_context.current_phase = InvestigationPhase.SYNTHESIS
        investigation_context.budget = TokenBudget(InvestigationPhase.SYNTHESIS, 1500)
        
        # Group findings by type and confidence
        grouped_findings = self._group_findings(investigation_context.findings)
        
        # Generate synthesis insights
        synthesis_findings = []
        
        # Pattern analysis
        patterns = self._identify_patterns(grouped_findings)
        if patterns:
            synthesis_findings.append({
                'type': 'pattern_analysis',
                'data': patterns,
                'confidence': 0.85
            })
        
        # Root cause analysis
        root_causes = self._identify_root_causes(grouped_findings, investigation_context.initial_query)
        if root_causes:
            synthesis_findings.append({
                'type': 'root_cause_analysis',
                'data': root_causes,
                'confidence': 0.8
            })
        
        # Recommendations
        recommendations = self._generate_recommendations(grouped_findings, investigation_context)
        if recommendations:
            synthesis_findings.append({
                'type': 'recommendations',
                'data': recommendations,
                'confidence': 0.75
            })
        
        investigation_context.findings.extend(synthesis_findings)
        self.logger.info(f"Synthesis phase complete. Investigation finished.")
    
    async def _execute_analysis_plugins(self, investigation_context: InvestigationContext) -> List[Dict[str, Any]]:
        """
        Execute specialized analysis plugins during investigation
        
        Args:
            investigation_context: Current investigation context
            
        Returns:
            List of findings from plugins
        """
        plugin_findings = []
        
        try:
            # Import plugin registry
            from src.plugins.plugin_registry import get_registry
            
            registry = get_registry()
            available_plugins = registry.get_all_plugins()
            
            # Filter plugins that handle investigation analysis
            analysis_plugins = [
                plugin for plugin in available_plugins
                if hasattr(plugin.metadata, 'hooks') and 
                'on_investigation_analysis' in plugin.metadata.hooks
            ]
            
            self.logger.info(f"Found {len(analysis_plugins)} investigation analysis plugins")
            
            # Prepare plugin context
            plugin_context = {
                'target_entity': investigation_context.target_entity,
                'entity_type': investigation_context.entity_type,
                'current_phase': investigation_context.current_phase.value,
                'budget_remaining': investigation_context.budget.remaining,
                'initial_query': investigation_context.initial_query,
                'existing_findings': investigation_context.findings,
                'file_content': await self._get_file_content(investigation_context.target_entity) if investigation_context.entity_type == 'file' else None
            }
            
            # Execute each plugin with budget awareness
            for plugin in analysis_plugins:
                if investigation_context.budget.is_exhausted:
                    self.logger.warning("Investigation budget exhausted, skipping remaining plugins")
                    break
                
                try:
                    self.logger.info(f"Executing plugin: {plugin.metadata.name}")
                    
                    # Execute plugin
                    result = plugin.execute(plugin_context)
                    
                    if result.get('success'):
                        # Extract findings from plugin result
                        if 'findings' in result:
                            for finding in result['findings']:
                                plugin_findings.append(finding)
                        elif 'suggestions' in result:
                            for suggestion in result['suggestions']:
                                plugin_findings.append(suggestion)
                        elif 'result' in result:
                            plugin_findings.append(result['result'])
                        
                        # Update budget consumption
                        tokens_consumed = result.get('tokens_consumed', 0)
                        investigation_context.budget.consume(tokens_consumed)
                        
                        self.logger.info(f"Plugin {plugin.metadata.name} completed successfully, consumed {tokens_consumed} tokens")
                    else:
                        self.logger.warning(f"Plugin {plugin.metadata.name} execution failed: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    self.logger.error(f"Error executing plugin {plugin.metadata.name}: {e}")
                    continue
            
        except ImportError:
            self.logger.warning("Plugin registry not available, skipping plugin execution")
        except Exception as e:
            self.logger.error(f"Error during plugin execution: {e}")
        
        return plugin_findings
    
    async def _get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get file content for plugin analysis
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None if not accessible
        """
        try:
            # In a real implementation, this would read the actual file
            # For now, return placeholder
            from pathlib import Path
            
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # File might be a component reference or doesn't exist
                return None
        except Exception as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def _extract_target_entity(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract target entity and type from investigation query"""
        import re
        
        query_lower = query.lower()
        
        for pattern_name, pattern in self.investigation_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                entity = match.group(1).strip()
                entity_type = self._infer_entity_type(entity, pattern_name)
                return entity, entity_type
        
        return None, None
    
    def _infer_entity_type(self, entity: str, pattern_name: str) -> str:
        """Infer entity type from pattern match and entity characteristics"""
        if pattern_name == 'view_analysis':
            return 'component'
        elif pattern_name == 'file_dependency':
            return 'file'
        elif pattern_name == 'function_behavior':
            return 'function'
        elif pattern_name == 'component_issue':
            return 'component'
        else:
            # Smart inference based on entity characteristics
            if entity.endswith(('.cs', '.js', '.py', '.tsx', '.razor')):
                return 'file'
            elif entity.lower().endswith(('view', 'component', 'controller')):
                return 'component'
            elif '(' in entity or entity.lower().startswith(('get', 'set', 'create', 'update', 'delete')):
                return 'function'
            else:
                return 'entity'
    
    async def _get_direct_relationships(self, entity: str, entity_type: str) -> List[Dict[str, Any]]:
        """Get direct relationships for entity from Knowledge Graph"""
        try:
            if entity_type == 'file':
                relationships = await self.knowledge_graph.get_file_relationships(entity)
            else:
                relationships = await self.knowledge_graph.search_patterns(
                    query=entity,
                    filters={'entity_type': entity_type}
                )
            
            return relationships or []
        except Exception as e:
            self.logger.error(f"Error getting relationships for {entity}: {e}")
            return []
    
    async def _analyze_relationship(self, relationship: Dict[str, Any], context: InvestigationContext) -> Optional[Dict[str, Any]]:
        """Analyze a specific relationship and return findings"""
        try:
            # Estimate token cost
            relationship_size = len(str(relationship))
            token_cost = relationship_size // 4  # Rough estimate
            
            if not context.budget.consume(token_cost):
                return None
            
            # Analyze relationship based on type
            rel_type = relationship.get('type', 'unknown')
            
            if rel_type == 'co_modification':
                return {
                    'type': 'dependency_analysis',
                    'data': {
                        'relationship': relationship,
                        'insight': f"Files {context.target_entity} and {relationship.get('related_file', 'unknown')} "
                                 f"are modified together {relationship.get('strength', 0)*100:.1f}% of the time",
                        'risk_level': self._assess_risk_level(relationship.get('strength', 0))
                    },
                    'confidence': relationship.get('confidence', 0.7)
                }
            elif rel_type == 'import_dependency':
                return {
                    'type': 'import_analysis',
                    'data': {
                        'relationship': relationship,
                        'insight': f"Dependency chain: {context.target_entity} imports {relationship.get('imported_entity', 'unknown')}",
                        'potential_issues': self._check_import_issues(relationship)
                    },
                    'confidence': relationship.get('confidence', 0.8)
                }
            else:
                return {
                    'type': 'general_relationship',
                    'data': relationship,
                    'confidence': relationship.get('confidence', 0.6)
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing relationship: {e}")
            return None
    
    async def _get_health_insights(self, entity: str, entity_type: str) -> List[Dict[str, Any]]:
        """Get health insights for entity using Enhanced Health Validator"""
        try:
            if entity_type == 'file':
                health_data = await self.enhanced_validator.analyze_file_health(entity)
            else:
                health_data = await self.enhanced_validator.analyze_component_health(entity)
            
            if health_data:
                return [{
                    'type': 'health_analysis',
                    'data': health_data,
                    'confidence': 0.85
                }]
        except Exception as e:
            self.logger.error(f"Error getting health insights for {entity}: {e}")
        
        return []
    
    async def _get_workspace_context(self, current_file: str) -> Dict[str, Any]:
        """Get current workspace context for investigation"""
        return {
            'current_file': current_file,
            'workspace_root': '/Users/asifhussain/PROJECTS/CORTEX',  # Could be dynamic
            'active_context': 'investigation'
        }
    
    def _group_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group findings by type for synthesis"""
        grouped = {}
        for finding in findings:
            finding_type = finding.get('type', 'unknown')
            if finding_type not in grouped:
                grouped[finding_type] = []
            grouped[finding_type].append(finding)
        return grouped
    
    def _identify_patterns(self, grouped_findings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify patterns across findings"""
        patterns = []
        
        # Look for repeated dependency issues
        if 'dependency_analysis' in grouped_findings:
            dep_findings = grouped_findings['dependency_analysis']
            if len(dep_findings) > 2:
                patterns.append({
                    'pattern_type': 'high_coupling',
                    'description': f"Entity has {len(dep_findings)} strong dependencies, indicating potential high coupling",
                    'severity': 'medium'
                })
        
        # Look for health issues
        if 'health_analysis' in grouped_findings:
            health_findings = grouped_findings['health_analysis']
            for finding in health_findings:
                health_data = finding.get('data', {})
                if health_data.get('issues'):
                    patterns.append({
                        'pattern_type': 'health_concern',
                        'description': f"Health issues detected: {health_data.get('issues')}",
                        'severity': 'high'
                    })
        
        return patterns
    
    def _identify_root_causes(self, grouped_findings: Dict[str, List[Dict[str, Any]]], query: str) -> List[Dict[str, Any]]:
        """Identify potential root causes based on findings"""
        root_causes = []
        
        # Analyze query intent for root cause hints
        if 'slow' in query.lower() or 'performance' in query.lower():
            # Look for performance-related causes
            perf_causes = self._find_performance_causes(grouped_findings)
            root_causes.extend(perf_causes)
        
        if 'error' in query.lower() or 'fail' in query.lower():
            # Look for error-related causes
            error_causes = self._find_error_causes(grouped_findings)
            root_causes.extend(error_causes)
        
        if 'not working' in query.lower():
            # Look for functional causes
            functional_causes = self._find_functional_causes(grouped_findings)
            root_causes.extend(functional_causes)
        
        return root_causes
    
    def _generate_recommendations(self, grouped_findings: Dict[str, List[Dict[str, Any]]], context: InvestigationContext) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on findings"""
        recommendations = []
        
        # Dependency-based recommendations
        if 'dependency_analysis' in grouped_findings:
            recommendations.append({
                'type': 'architecture',
                'priority': 'medium',
                'action': 'Consider reducing coupling between frequently co-modified files',
                'rationale': 'High co-modification rates suggest tight coupling'
            })
        
        # Health-based recommendations
        if 'health_analysis' in grouped_findings:
            recommendations.append({
                'type': 'maintenance',
                'priority': 'high',
                'action': 'Address identified health issues to prevent future problems',
                'rationale': 'Health issues can compound over time'
            })
        
        # Pattern-based recommendations
        patterns = [f for f in context.findings if f.get('type') == 'pattern_analysis']
        if patterns:
            for pattern_finding in patterns:
                pattern_data = pattern_finding.get('data', [])
                for pattern in pattern_data:
                    if pattern.get('severity') == 'high':
                        recommendations.append({
                            'type': 'urgent',
                            'priority': 'high',
                            'action': f"Address {pattern.get('pattern_type')}: {pattern.get('description')}",
                            'rationale': 'High severity pattern detected'
                        })
        
        return recommendations
    
    def _assess_risk_level(self, strength: float) -> str:
        """Assess risk level based on relationship strength"""
        if strength >= 0.8:
            return 'high'
        elif strength >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _check_import_issues(self, relationship: Dict[str, Any]) -> List[str]:
        """Check for potential import-related issues"""
        issues = []
        # This would be enhanced with actual analysis logic
        if relationship.get('circular_dependency'):
            issues.append('Circular dependency detected')
        if relationship.get('unused_import'):
            issues.append('Potentially unused import')
        return issues
    
    def _find_performance_causes(self, grouped_findings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find performance-related root causes"""
        # Implementation would analyze findings for performance indicators
        return []
    
    def _find_error_causes(self, grouped_findings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find error-related root causes"""
        # Implementation would analyze findings for error indicators
        return []
    
    def _find_functional_causes(self, grouped_findings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find functional issue root causes"""
        # Implementation would analyze findings for functional indicators
        return []
    
    async def _user_checkpoint(self, context: InvestigationContext, message: str) -> Dict[str, Any]:
        """
        Create a user checkpoint for phase continuation decision.
        In a real implementation, this would integrate with the UI.
        For now, it defaults to proceeding.
        """
        context.user_checkpoints.append(message)
        
        # In real implementation, this would present UI choice to user
        # For now, default to proceeding
        return {'proceed': True, 'message': message}
    
    def _generate_discovery_report(self, context: InvestigationContext) -> Dict[str, Any]:
        """Generate discovery phase report"""
        return {
            'success': True,
            'phase': 'discovery',
            'target_entity': context.target_entity,
            'entity_type': context.entity_type,
            'relationships_found': len(context.direct_relationships),
            'budget_used': context.budget.consumed,
            'findings': context.findings,
            'next_phase': 'analysis'
        }
    
    def _generate_analysis_report(self, context: InvestigationContext) -> Dict[str, Any]:
        """Generate analysis phase report"""
        return {
            'success': True,
            'phase': 'analysis',
            'target_entity': context.target_entity,
            'findings_count': len(context.findings),
            'budget_used': context.budget.consumed,
            'findings': context.findings,
            'next_phase': 'synthesis'
        }
    
    def _generate_final_report(self, context: InvestigationContext) -> Dict[str, Any]:
        """Generate final investigation report"""
        # Separate findings by type for structured presentation
        findings_by_type = self._group_findings(context.findings)
        
        return {
            'success': True,
            'phase': 'complete',
            'target_entity': context.target_entity,
            'entity_type': context.entity_type,
            'total_findings': len(context.findings),
            'findings_by_type': findings_by_type,
            'user_checkpoints': context.user_checkpoints,
            'investigation_summary': self._create_summary(context),
            'completed_at': 'timestamp_placeholder'
        }
    
    def _create_summary(self, context: InvestigationContext) -> str:
        """Create a human-readable summary of the investigation"""
        findings_count = len(context.findings)
        relationships_count = len(context.direct_relationships)
        
        summary = f"Investigation of {context.entity_type} '{context.target_entity}' completed. "
        summary += f"Found {relationships_count} direct relationships and generated {findings_count} findings. "
        
        # Add key insights
        high_confidence_findings = [f for f in context.findings if f.get('confidence', 0) >= 0.8]
        if high_confidence_findings:
            summary += f"{len(high_confidence_findings)} high-confidence insights identified. "
        
        return summary