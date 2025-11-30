"""
Brain Ingestion Agent - Feature Intelligence Extraction

This module implements the BrainIngestionAgent that extracts feature intelligence
and stores it in CORTEX brain (Tier 2 Knowledge Graph and Tier 3 Context Intelligence).

The agent parses feature descriptions, extracts entities, analyzes implementation
changes, and updates the knowledge graph with new patterns and relationships.

Author: Asif Hussain
Created: November 17, 2025
Version: 1.0
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Set, Any, Optional
from pathlib import Path

# Import data structures from main FCO module
from src.agents.feature_completion_orchestrator import (
    BrainIngestionAgent, BrainData, Entity, Pattern, ContextUpdate, 
    ImplementationScan
)

logger = logging.getLogger(__name__)

class BrainIngestionAgentImpl(BrainIngestionAgent):
    """
    Implementation of Brain Ingestion Agent that extracts feature intelligence
    and stores it in CORTEX brain tiers.
    """
    
    def __init__(self, cortex_root: str = None):
        """
        Initialize brain ingestion agent.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root) if cortex_root else Path.cwd()
        
        # Entity extraction patterns
        self.entity_patterns = {
            'file': [
                r'(\w+\.\w+)',  # filename.ext
                r'(\w+/\w+\.\w+)',  # path/filename.ext
                r'([A-Z][a-zA-Z]*\.(?:cs|py|js|ts|java|cpp|h))',  # ClassName.ext
            ],
            'class': [
                r'([A-Z][a-zA-Z]*Service)',  # XxxService
                r'([A-Z][a-zA-Z]*Controller)',  # XxxController
                r'([A-Z][a-zA-Z]*Manager)',  # XxxManager
                r'([A-Z][a-zA-Z]*Handler)',  # XxxHandler
                r'([A-Z][a-zA-Z]*Agent)',  # XxxAgent
            ],
            'function': [
                r'([a-z_][a-zA-Z_]*)\(',  # function_name(
                r'(authenticate|login|logout|validate|process|handle|create|update|delete)',
            ],
            'concept': [
                r'(authentication|authorization|login|logout|security)',
                r'(dashboard|panel|interface|UI|frontend)',
                r'(API|endpoint|service|backend)',
                r'(database|storage|persistence)',
                r'(test|testing|validation|verification)',
            ]
        }
        
        # Pattern confidence weights
        self.pattern_weights = {
            'exact_match': 0.9,
            'partial_match': 0.7,
            'context_match': 0.5,
            'keyword_match': 0.3
        }
    
    async def ingest_feature(self, feature_description: str) -> BrainData:
        """
        Extract feature intelligence and store in CORTEX brain.
        
        Args:
            feature_description: Description of the completed feature
            
        Returns:
            BrainData with extracted entities, patterns, and context updates
        """
        logger.info(f"Starting brain ingestion for feature: {feature_description}")
        
        # Extract entities from feature description
        entities = await self._extract_entities(feature_description)
        
        # Scan implementation for actual changes
        implementation_scan = await self._scan_implementation_changes()
        
        # Store patterns in knowledge graph (mock for now)
        patterns = await self._store_feature_patterns(
            feature_description, entities, implementation_scan
        )
        
        # Update context intelligence (mock for now)
        context_updates = await self._update_context_intelligence(
            feature_description, implementation_scan
        )
        
        brain_data = BrainData(
            entities=entities,
            patterns=patterns,
            context_updates=context_updates,
            implementation_scan=implementation_scan
        )
        
        logger.info(f"Brain ingestion complete: {len(entities)} entities, {len(patterns)} patterns")
        return brain_data
    
    async def _extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities (files, classes, functions, concepts) from feature description.
        
        Args:
            text: Feature description text
            
        Returns:
            List of extracted entities with confidence scores
        """
        entities = []
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity_value = match.group(1) if match.groups() else match.group(0)
                    
                    # Calculate confidence based on match type
                    confidence = self._calculate_entity_confidence(
                        entity_value, entity_type, text_lower
                    )
                    
                    # Extract context around the match
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 20)
                    context = text[start:end].strip()
                    
                    entities.append(Entity(
                        type=entity_type,
                        value=entity_value,
                        confidence=confidence,
                        context=context
                    ))
        
        # Remove duplicates and sort by confidence
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda e: e.confidence, reverse=True)
        
        return entities[:20]  # Limit to top 20 entities
    
    def _calculate_entity_confidence(self, entity_value: str, entity_type: str, context: str) -> float:
        """Calculate confidence score for extracted entity"""
        confidence = 0.0
        
        # Base confidence by entity type
        type_confidence = {
            'file': 0.8,
            'class': 0.7,
            'function': 0.6,
            'concept': 0.5
        }
        confidence += type_confidence.get(entity_type, 0.3)
        
        # Boost if entity appears multiple times
        entity_count = context.count(entity_value.lower())
        confidence += min(0.2, entity_count * 0.05)
        
        # Boost for certain keywords in context
        boost_keywords = ['implement', 'create', 'add', 'build', 'develop']
        for keyword in boost_keywords:
            if keyword in context:
                confidence += 0.1
                break
        
        return min(1.0, confidence)
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities, keeping highest confidence"""
        seen = {}
        
        for entity in entities:
            key = f"{entity.type}:{entity.value.lower()}"
            
            if key not in seen or entity.confidence > seen[key].confidence:
                seen[key] = entity
        
        return list(seen.values())
    
    async def _scan_implementation_changes(self) -> ImplementationScan:
        """
        Scan for recent implementation changes in the codebase.
        
        Returns:
            ImplementationScan with discovered changes
        """
        # For now, return mock data
        # TODO: Implement actual git analysis and file scanning
        
        return ImplementationScan(
            files_changed=[
                "src/agents/feature_completion_orchestrator.py",
                "src/agents/brain_ingestion_agent.py",
                "cortex-brain/documents/planning/FEATURE-COMPLETION-ORCHESTRATOR-DESIGN.md"
            ],
            modules_added=[
                "FeatureCompletionOrchestrator",
                "BrainIngestionAgent"
            ],
            apis_discovered=[
                "/api/features/complete",
                "/api/brain/ingest"
            ],
            tests_found=[
                "tests/agents/test_feature_completion_orchestrator.py",
                "tests/agents/test_brain_ingestion_agent.py"
            ]
        )
    
    async def _store_feature_patterns(
        self, 
        feature_description: str, 
        entities: List[Entity],
        implementation_scan: ImplementationScan
    ) -> List[Pattern]:
        """
        Store feature patterns in Tier 2 knowledge graph.
        
        Args:
            feature_description: Feature description
            entities: Extracted entities
            implementation_scan: Implementation scan results
            
        Returns:
            List of stored patterns
        """
        patterns = []
        
        # Create feature implementation pattern
        feature_pattern = Pattern(
            pattern_type="feature_implementation",
            confidence=0.8,
            data={
                "feature_name": feature_description,
                "entities": [e.value for e in entities],
                "files_changed": implementation_scan.files_changed,
                "modules_added": implementation_scan.modules_added,
                "timestamp": datetime.now().isoformat(),
                "entity_types": list(set(e.type for e in entities))
            }
        )
        patterns.append(feature_pattern)
        
        # Create entity relationship patterns
        for entity in entities[:10]:  # Top 10 entities
            if entity.confidence > 0.7:
                entity_pattern = Pattern(
                    pattern_type="entity_usage",
                    confidence=entity.confidence,
                    data={
                        "entity_type": entity.type,
                        "entity_value": entity.value,
                        "context": entity.context,
                        "feature": feature_description,
                        "usage_frequency": 1
                    }
                )
                patterns.append(entity_pattern)
        
        # Create workflow pattern based on feature type
        workflow_pattern = self._create_workflow_pattern(feature_description, entities)
        if workflow_pattern:
            patterns.append(workflow_pattern)
        
        # TODO: Actually store in Tier 2 knowledge graph database
        logger.info(f"Stored {len(patterns)} patterns in knowledge graph")
        
        return patterns
    
    def _create_workflow_pattern(self, feature_description: str, entities: List[Entity]) -> Optional[Pattern]:
        """Create workflow pattern based on feature type"""
        feature_lower = feature_description.lower()
        
        # Authentication workflow
        if any(word in feature_lower for word in ['auth', 'login', 'security']):
            return Pattern(
                pattern_type="authentication_workflow",
                confidence=0.9,
                data={
                    "workflow_type": "authentication",
                    "typical_files": ["AuthService", "LoginController", "AuthTests"],
                    "typical_apis": ["/api/auth/login", "/api/auth/logout"],
                    "security_considerations": ["password hashing", "session management", "JWT tokens"],
                    "test_requirements": ["unit tests", "integration tests", "security tests"]
                }
            )
        
        # Dashboard/UI workflow
        elif any(word in feature_lower for word in ['dashboard', 'ui', 'interface', 'panel']):
            return Pattern(
                pattern_type="ui_workflow",
                confidence=0.9,
                data={
                    "workflow_type": "user_interface",
                    "typical_files": ["Component.razor", "style.css", "UITests"],
                    "typical_apis": ["/api/ui/data", "/api/ui/config"],
                    "ui_considerations": ["responsive design", "accessibility", "user experience"],
                    "test_requirements": ["component tests", "visual tests", "e2e tests"]
                }
            )
        
        # API/Service workflow
        elif any(word in feature_lower for word in ['api', 'service', 'endpoint']):
            return Pattern(
                pattern_type="api_workflow",
                confidence=0.9,
                data={
                    "workflow_type": "api_service",
                    "typical_files": ["Controller", "Service", "Model", "ApiTests"],
                    "typical_apis": ["/api/service/endpoint"],
                    "api_considerations": ["validation", "error handling", "documentation"],
                    "test_requirements": ["unit tests", "integration tests", "api tests"]
                }
            )
        
        return None
    
    async def _update_context_intelligence(
        self, 
        feature_description: str,
        implementation_scan: ImplementationScan
    ) -> List[ContextUpdate]:
        """
        Update Tier 3 context intelligence with feature context.
        
        Args:
            feature_description: Feature description
            implementation_scan: Implementation scan results
            
        Returns:
            List of context updates
        """
        context_updates = []
        
        # File activity update
        if implementation_scan.files_changed:
            file_update = ContextUpdate(
                update_type="file_activity",
                data={
                    "files_changed": implementation_scan.files_changed,
                    "change_reason": f"Feature completion: {feature_description}",
                    "change_type": "feature_implementation",
                    "impact_score": len(implementation_scan.files_changed) * 0.1
                },
                timestamp=datetime.now()
            )
            context_updates.append(file_update)
        
        # Module growth update
        if implementation_scan.modules_added:
            module_update = ContextUpdate(
                update_type="module_growth",
                data={
                    "modules_added": implementation_scan.modules_added,
                    "growth_reason": f"Feature: {feature_description}",
                    "complexity_increase": len(implementation_scan.modules_added) * 0.2
                },
                timestamp=datetime.now()
            )
            context_updates.append(module_update)
        
        # API expansion update
        if implementation_scan.apis_discovered:
            api_update = ContextUpdate(
                update_type="api_expansion",
                data={
                    "apis_added": implementation_scan.apis_discovered,
                    "feature_context": feature_description,
                    "api_complexity": len(implementation_scan.apis_discovered) * 0.3
                },
                timestamp=datetime.now()
            )
            context_updates.append(api_update)
        
        # Test coverage update
        if implementation_scan.tests_found:
            test_update = ContextUpdate(
                update_type="test_coverage",
                data={
                    "tests_added": implementation_scan.tests_found,
                    "feature_tested": feature_description,
                    "coverage_improvement": len(implementation_scan.tests_found) * 0.1
                },
                timestamp=datetime.now()
            )
            context_updates.append(test_update)
        
        # TODO: Actually update Tier 3 context intelligence database
        logger.info(f"Created {len(context_updates)} context updates")
        
        return context_updates

# ====================================================================================
# UTILITY FUNCTIONS
# ====================================================================================

def create_brain_ingestion_agent(cortex_root: str = None) -> BrainIngestionAgentImpl:
    """
    Factory function to create properly configured brain ingestion agent.
    
    Args:
        cortex_root: Path to CORTEX root directory
        
    Returns:
        Configured BrainIngestionAgentImpl
    """
    return BrainIngestionAgentImpl(cortex_root)

# ====================================================================================
# TESTING
# ====================================================================================

async def test_brain_ingestion():
    """Test brain ingestion functionality"""
    agent = BrainIngestionAgentImpl()
    
    test_features = [
        "user authentication system with JWT tokens",
        "dashboard interface for admin panel",
        "payment processing API with Stripe integration",
        "email notification service"
    ]
    
    for feature in test_features:
        print(f"\nTesting: {feature}")
        brain_data = await agent.ingest_feature(feature)
        
        print(f"  Entities: {len(brain_data.entities)}")
        for entity in brain_data.entities[:3]:
            print(f"    {entity.type}: {entity.value} ({entity.confidence:.2f})")
        
        print(f"  Patterns: {len(brain_data.patterns)}")
        for pattern in brain_data.patterns:
            print(f"    {pattern.pattern_type} ({pattern.confidence:.2f})")
        
        print(f"  Context updates: {len(brain_data.context_updates)}")
        print(f"  Files changed: {len(brain_data.implementation_scan.files_changed)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_brain_ingestion())