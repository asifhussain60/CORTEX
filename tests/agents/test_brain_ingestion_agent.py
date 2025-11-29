"""
Tests for Brain Ingestion Agent

Tests feature intelligence extraction and brain storage functionality.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Mock missing dependencies before importing
import sys
from unittest.mock import MagicMock

sys.modules['src.utils.entity_extractor'] = MagicMock()
sys.modules['src.utils.metrics_collector'] = MagicMock()

from src.agents.brain_ingestion_agent import BrainIngestionAgentImpl, create_brain_ingestion_agent


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root directory."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir(parents=True)
    brain_dir = cortex_root / "cortex-brain"
    brain_dir.mkdir(parents=True)
    return cortex_root


@pytest.fixture
def agent(temp_cortex_root):
    """Create brain ingestion agent instance."""
    return BrainIngestionAgentImpl(cortex_root=str(temp_cortex_root))


class TestBrainIngestionAgentImpl:
    """Test suite for Brain Ingestion Agent Implementation."""
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.cortex_root is not None
        assert isinstance(agent.cortex_root, Path)
    
    def test_initialization_with_default_root(self):
        """Test agent initializes with default cortex_root."""
        agent = BrainIngestionAgentImpl()
        assert agent.cortex_root == Path.cwd()
    
    def test_entity_patterns_loaded(self, agent):
        """Test entity extraction patterns are loaded."""
        assert 'file' in agent.entity_patterns
        assert 'class' in agent.entity_patterns
        assert 'function' in agent.entity_patterns
        assert 'concept' in agent.entity_patterns
        assert len(agent.entity_patterns['file']) > 0
        assert len(agent.entity_patterns['class']) > 0
    
    def test_pattern_weights_configured(self, agent):
        """Test pattern confidence weights are configured."""
        assert 'exact_match' in agent.pattern_weights
        assert 'partial_match' in agent.pattern_weights
        assert 'context_match' in agent.pattern_weights
        assert 'keyword_match' in agent.pattern_weights
        assert agent.pattern_weights['exact_match'] > agent.pattern_weights['partial_match']
    
    @pytest.mark.asyncio
    async def test_ingest_feature_returns_brain_data(self, agent):
        """Test feature ingestion returns BrainData structure."""
        result = await agent.ingest_feature("user authentication with login and logout")
        
        assert result is not None
        assert hasattr(result, 'entities')
        assert hasattr(result, 'patterns')
        assert hasattr(result, 'context_updates')
        assert hasattr(result, 'implementation_scan')
    
    @pytest.mark.asyncio
    async def test_extract_entities_from_feature_description(self, agent):
        """Test entity extraction from feature description."""
        feature = "Add UserController with authenticate() function for login.py"
        entities = await agent._extract_entities(feature)
        
        assert len(entities) > 0
        # Should find file: login.py
        file_entities = [e for e in entities if e.type == 'file']
        assert len(file_entities) > 0
        # Should find class: UserController
        class_entities = [e for e in entities if e.type == 'class']
        assert len(class_entities) > 0
        # Should find function: authenticate
        function_entities = [e for e in entities if e.type == 'function']
        assert len(function_entities) > 0
    
    @pytest.mark.asyncio
    async def test_extract_entities_with_concepts(self, agent):
        """Test entity extraction finds concepts."""
        feature = "Implement authentication system with database storage for API endpoints"
        entities = await agent._extract_entities(feature)
        
        concept_entities = [e for e in entities if e.type == 'concept']
        assert len(concept_entities) > 0
        
        # Should find authentication and database concepts
        concept_values = [e.value.lower() for e in concept_entities]
        assert any('auth' in v for v in concept_values)
    
    @pytest.mark.asyncio
    async def test_entities_have_confidence_scores(self, agent):
        """Test extracted entities have confidence scores."""
        feature = "UserService class with login() method"
        entities = await agent._extract_entities(feature)
        
        for entity in entities:
            assert hasattr(entity, 'confidence')
            assert 0.0 <= entity.confidence <= 1.0
            assert hasattr(entity, 'context')
            assert len(entity.context) > 0
    
    @pytest.mark.asyncio
    async def test_entities_sorted_by_confidence(self, agent):
        """Test entities are sorted by confidence score."""
        feature = "AuthService LoginController authenticate login logout security"
        entities = await agent._extract_entities(feature)
        
        if len(entities) > 1:
            for i in range(len(entities) - 1):
                assert entities[i].confidence >= entities[i+1].confidence
    
    @pytest.mark.asyncio
    async def test_entities_limited_to_top_20(self, agent):
        """Test entity extraction limits results to top 20."""
        # Feature with many potential entities
        feature = " ".join([f"Entity{i} Class{i} function{i}()" for i in range(50)])
        entities = await agent._extract_entities(feature)
        
        assert len(entities) <= 20
    
    def test_calculate_entity_confidence(self, agent):
        """Test entity confidence calculation."""
        context = "implement authentication service with authentication logic"
        
        # File entities should have high confidence
        file_confidence = agent._calculate_entity_confidence(
            "auth.py", "file", context
        )
        assert file_confidence > 0.7
        
        # Concept entities should have moderate confidence
        concept_confidence = agent._calculate_entity_confidence(
            "authentication", "concept", context
        )
        assert concept_confidence > 0.5
    
    def test_confidence_boost_for_multiple_occurrences(self, agent):
        """Test confidence boost when entity appears multiple times."""
        context_single = "implement login service"
        context_multiple = "implement login service for login page with login validation"
        
        confidence_single = agent._calculate_entity_confidence(
            "login", "concept", context_single
        )
        confidence_multiple = agent._calculate_entity_confidence(
            "login", "concept", context_multiple
        )
        
        assert confidence_multiple > confidence_single
    
    def test_confidence_boost_for_implementation_keywords(self, agent):
        """Test confidence boost for implementation keywords in context."""
        context_with_keyword = "implement authentication service"
        context_without_keyword = "authentication service exists"
        
        confidence_with = agent._calculate_entity_confidence(
            "authentication", "concept", context_with_keyword
        )
        confidence_without = agent._calculate_entity_confidence(
            "authentication", "concept", context_without_keyword
        )
        
        assert confidence_with >= confidence_without
    
    def test_deduplicate_entities(self, agent):
        """Test entity deduplication."""
        from src.agents.feature_completion_orchestrator import Entity
        
        entities = [
            Entity(type='file', value='test.py', confidence=0.8, context='first'),
            Entity(type='file', value='TEST.PY', confidence=0.9, context='second'),  # duplicate
            Entity(type='class', value='Service', confidence=0.7, context='third'),
        ]
        
        deduplicated = agent._deduplicate_entities(entities)
        
        assert len(deduplicated) == 2  # test.py and Service
        # Should keep higher confidence version
        test_file = [e for e in deduplicated if e.type == 'file'][0]
        assert test_file.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_scan_implementation_changes(self, agent):
        """Test implementation scanning."""
        scan = await agent._scan_implementation_changes()
        
        assert hasattr(scan, 'files_changed')
        assert hasattr(scan, 'modules_added')
        assert hasattr(scan, 'apis_discovered')
        assert hasattr(scan, 'tests_found')
        assert isinstance(scan.files_changed, list)
    
    @pytest.mark.asyncio
    async def test_store_feature_patterns(self, agent):
        """Test pattern storage in knowledge graph."""
        from src.agents.feature_completion_orchestrator import Entity, ImplementationScan
        
        entities = [
            Entity(type='class', value='AuthService', confidence=0.9, context='test'),
            Entity(type='function', value='login', confidence=0.8, context='test'),
        ]
        
        implementation_scan = ImplementationScan(
            files_changed=['auth.py'],
            modules_added=['AuthService'],
            apis_discovered=['/api/auth/login'],
            tests_found=['test_auth.py']
        )
        
        patterns = await agent._store_feature_patterns(
            "authentication system",
            entities,
            implementation_scan
        )
        
        assert len(patterns) > 0
        assert any(p.pattern_type == "feature_implementation" for p in patterns)
    
    def test_create_workflow_pattern_authentication(self, agent):
        """Test authentication workflow pattern creation."""
        from src.agents.feature_completion_orchestrator import Entity
        
        entities = [Entity(type='concept', value='auth', confidence=0.9, context='test')]
        pattern = agent._create_workflow_pattern("user authentication system", entities)
        
        assert pattern is not None
        assert pattern.pattern_type == "authentication_workflow"
        assert pattern.confidence > 0.8
        assert 'workflow_type' in pattern.data
        assert pattern.data['workflow_type'] == 'authentication'
    
    def test_create_workflow_pattern_ui(self, agent):
        """Test UI workflow pattern creation."""
        from src.agents.feature_completion_orchestrator import Entity
        
        entities = []
        pattern = agent._create_workflow_pattern("dashboard interface for admin panel", entities)
        
        assert pattern is not None
        assert pattern.pattern_type == "ui_workflow"
        assert pattern.data['workflow_type'] == 'user_interface'
    
    def test_create_workflow_pattern_api(self, agent):
        """Test API workflow pattern creation."""
        from src.agents.feature_completion_orchestrator import Entity
        
        entities = []
        pattern = agent._create_workflow_pattern("REST API service endpoints", entities)
        
        assert pattern is not None
        assert pattern.pattern_type == "api_workflow"
        assert pattern.data['workflow_type'] == 'api_service'
    
    def test_create_workflow_pattern_none_for_generic(self, agent):
        """Test no workflow pattern for generic features."""
        from src.agents.feature_completion_orchestrator import Entity
        
        entities = []
        pattern = agent._create_workflow_pattern("miscellaneous bug fixes", entities)
        
        assert pattern is None
    
    @pytest.mark.asyncio
    async def test_update_context_intelligence(self, agent):
        """Test context intelligence updates."""
        from src.agents.feature_completion_orchestrator import ImplementationScan
        
        implementation_scan = ImplementationScan(
            files_changed=['file1.py', 'file2.py'],
            modules_added=['Module1'],
            apis_discovered=['/api/endpoint'],
            tests_found=['test1.py']
        )
        
        updates = await agent._update_context_intelligence(
            "test feature",
            implementation_scan
        )
        
        assert len(updates) > 0
        # Should create update for each scan aspect
        update_types = [u.update_type for u in updates]
        assert 'file_activity' in update_types
        assert 'module_growth' in update_types
        assert 'api_expansion' in update_types
        assert 'test_coverage' in update_types
    
    @pytest.mark.asyncio
    async def test_context_updates_have_timestamps(self, agent):
        """Test context updates include timestamps."""
        from src.agents.feature_completion_orchestrator import ImplementationScan
        
        implementation_scan = ImplementationScan(
            files_changed=['file.py'],
            modules_added=[],
            apis_discovered=[],
            tests_found=[]
        )
        
        updates = await agent._update_context_intelligence(
            "test", implementation_scan
        )
        
        for update in updates:
            assert hasattr(update, 'timestamp')
            assert update.timestamp is not None
    
    def test_factory_function(self, temp_cortex_root):
        """Test factory function creates agent correctly."""
        agent = create_brain_ingestion_agent(cortex_root=str(temp_cortex_root))
        
        assert isinstance(agent, BrainIngestionAgentImpl)
        assert agent.cortex_root == temp_cortex_root
    
    @pytest.mark.asyncio
    async def test_full_ingestion_workflow(self, agent):
        """Test complete feature ingestion workflow."""
        feature_description = "User authentication system with JWT tokens and login/logout"
        
        brain_data = await agent.ingest_feature(feature_description)
        
        # Verify all components populated
        assert len(brain_data.entities) > 0
        assert len(brain_data.patterns) > 0
        assert len(brain_data.context_updates) > 0
        assert brain_data.implementation_scan is not None
        
        # Verify entities contain expected types
        entity_types = set(e.type for e in brain_data.entities)
        assert 'concept' in entity_types  # Should find 'authentication'
        
        # Verify patterns include feature implementation
        pattern_types = [p.pattern_type for p in brain_data.patterns]
        assert 'feature_implementation' in pattern_types
        
        # Verify authentication workflow pattern created
        assert any(p.pattern_type == 'authentication_workflow' for p in brain_data.patterns)
