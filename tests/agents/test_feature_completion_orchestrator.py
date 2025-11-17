"""
Test Suite for Feature Completion Orchestrator

Comprehensive test suite covering all FCO components:
- Feature completion pattern detection
- Brain ingestion functionality
- End-to-end orchestration workflow
- Error handling and recovery
- Performance and metrics

Author: Asif Hussain
Created: November 17, 2025
Version: 1.0
"""

import pytest
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List

# Mock the CORTEX dependencies for testing
import sys
sys.modules['src.agents.base_agent'] = MagicMock()
sys.modules['src.tier2.knowledge_graph'] = MagicMock()
sys.modules['src.tier3.context_intelligence'] = MagicMock()
sys.modules['src.utils.entity_extractor'] = MagicMock()
sys.modules['src.utils.metrics_collector'] = MagicMock()

# Import our modules under test
from src.agents.feature_completion_orchestrator import (
    FeatureCompletionOrchestrator, AlignmentReport, BrainData, ImplementationData,
    DocumentationUpdates, VisualAssets, HealthReport, Entity, Pattern,
    ContextUpdate, ImplementationScan
)
from src.agents.brain_ingestion_agent import BrainIngestionAgentImpl

class TestFeatureCompletionOrchestrator:
    """Test suite for FeatureCompletionOrchestrator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fco = FeatureCompletionOrchestrator()
        
    def test_pattern_detection_success(self):
        """Test successful feature completion pattern detection"""
        test_cases = [
            ("authentication feature is complete", "authentication"),
            ("finished implementing user dashboard", "user dashboard"),
            ("mark payment system as done", "payment system"),
            ("finalize user authentication", "user authentication"),
            ("login feature is ready", "login"),
            ("completed building the API service", "API service"),
            ("user profile module is finished", "user profile"),
            ("just finished the notification system", "notification"),
            ("payment processing is complete", "payment processing"),
            ("authentication system is ready", "authentication system"),
        ]
        
        for input_text, expected_feature in test_cases:
            detected_feature = self.fco.detect_feature_completion(input_text)
            assert detected_feature == expected_feature, \
                f"Expected '{expected_feature}' but got '{detected_feature}' for input '{input_text}'"
    
    def test_pattern_detection_failure(self):
        """Test pattern detection with non-matching inputs"""
        non_matching_inputs = [
            "hello world",
            "how are you doing",
            "please help me with something",
            "I need assistance",
            "what is the status"
        ]
        
        for input_text in non_matching_inputs:
            detected_feature = self.fco.detect_feature_completion(input_text)
            assert detected_feature is None, \
                f"Expected None but got '{detected_feature}' for input '{input_text}'"
    
    def test_pattern_detection_edge_cases(self):
        """Test pattern detection with edge cases"""
        edge_cases = [
            ("THE authentication FEATURE IS COMPLETE", "authentication"),  # Case insensitive
            ("   authentication feature is complete   ", "authentication"),  # Whitespace
            ("authentication feature is complete!", "authentication"),  # Punctuation
            ("a authentication feature is complete", "authentication"),  # Article removal
            ("the user login system is ready", "user login system"),  # Complex names
        ]
        
        for input_text, expected_feature in edge_cases:
            detected_feature = self.fco.detect_feature_completion(input_text)
            assert detected_feature == expected_feature, \
                f"Expected '{expected_feature}' but got '{detected_feature}' for input '{input_text}'"
    
    def test_initialization(self):
        """Test FCO initialization"""
        assert self.fco.name == "feature-completion-orchestrator"
        assert self.fco.hemisphere == "coordination"
        assert len(self.fco.capabilities) == 6
        assert "brain_ingestion" in self.fco.capabilities
        assert "implementation_discovery" in self.fco.capabilities
    
    def test_subagents_readiness_check(self):
        """Test sub-agents readiness checking"""
        # Initially, sub-agents should not be ready (None)
        assert not self.fco._are_subagents_ready()
        
        # Mock all sub-agents
        self.fco.brain_ingestion_agent = AsyncMock()
        self.fco.discovery_engine = AsyncMock()
        self.fco.doc_intelligence = AsyncMock()
        self.fco.visual_generator = AsyncMock()
        self.fco.optimization_monitor = AsyncMock()
        
        # Now should be ready
        assert self.fco._are_subagents_ready()
    
    @pytest.mark.asyncio
    async def test_safe_execute_success(self):
        """Test safe execution with successful function"""
        async def mock_function(arg1, arg2):
            return f"result: {arg1}, {arg2}"
        
        result = await self.fco._safe_execute(mock_function, "test1", "test2", stage_name="Test Stage")
        assert result == "result: test1, test2"
    
    @pytest.mark.asyncio
    async def test_safe_execute_failure(self):
        """Test safe execution with failing function"""
        async def failing_function():
            raise Exception("Test error")
        
        result = await self.fco._safe_execute(failing_function, stage_name="Test Stage")
        assert result is None
    
    def test_empty_data_creation(self):
        """Test creation of empty/default data structures"""
        brain_data = self.fco._get_empty_brain_data()
        assert isinstance(brain_data, BrainData)
        assert len(brain_data.entities) == 0
        assert len(brain_data.patterns) == 0
        
        impl_data = self.fco._get_empty_implementation_data()
        assert isinstance(impl_data, ImplementationData)
        assert len(impl_data.code_changes) == 0
        
        doc_updates = self.fco._get_empty_doc_updates()
        assert isinstance(doc_updates, DocumentationUpdates)
        assert len(doc_updates.files_updated) == 0
        
        visual_assets = self.fco._get_empty_visual_assets()
        assert isinstance(visual_assets, VisualAssets)
        assert len(visual_assets.mermaid_diagrams) == 0
        
        health_report = self.fco._get_empty_health_report()
        assert isinstance(health_report, HealthReport)
        assert health_report.overall_health_score == 0.0

class TestBrainIngestionAgent:
    """Test suite for BrainIngestionAgent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = BrainIngestionAgentImpl()
    
    def test_initialization(self):
        """Test agent initialization"""
        assert self.agent.cortex_root is not None
        assert len(self.agent.entity_patterns) == 4  # file, class, function, concept
        assert 'file' in self.agent.entity_patterns
        assert 'class' in self.agent.entity_patterns
        assert 'function' in self.agent.entity_patterns
        assert 'concept' in self.agent.entity_patterns
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self):
        """Test entity extraction from feature description"""
        test_text = "Implemented AuthService.cs with login and authenticate functions for user authentication"
        
        entities = await self.agent._extract_entities(test_text)
        
        # Should extract entities
        assert len(entities) > 0
        
        # Check entity types
        entity_types = [e.type for e in entities]
        assert 'file' in entity_types  # AuthService.cs
        assert 'function' in entity_types  # login, authenticate
        assert 'concept' in entity_types  # authentication
        
        # Check confidence scores
        for entity in entities:
            assert 0.0 <= entity.confidence <= 1.0
            assert entity.context is not None
    
    def test_confidence_calculation(self):
        """Test entity confidence calculation"""
        # High confidence entity
        confidence = self.agent._calculate_entity_confidence(
            "AuthService.cs", "file", "implement authservice.cs with login functions"
        )
        assert confidence >= 0.8
        
        # Lower confidence entity
        confidence = self.agent._calculate_entity_confidence(
            "test", "concept", "this is a test"
        )
        assert confidence < 0.8
    
    def test_entity_deduplication(self):
        """Test entity deduplication"""
        entities = [
            Entity("file", "test.cs", 0.9, "context1"),
            Entity("file", "Test.cs", 0.7, "context2"),  # Should be deduplicated
            Entity("file", "other.cs", 0.8, "context3"),
        ]
        
        deduplicated = self.agent._deduplicate_entities(entities)
        
        # Should keep highest confidence version
        assert len(deduplicated) == 2
        file_entities = [e for e in deduplicated if e.value.lower() == "test.cs"]
        assert len(file_entities) == 1
        assert file_entities[0].confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_implementation_scan(self):
        """Test implementation scanning (mock)"""
        scan = await self.agent._scan_implementation_changes()
        
        assert isinstance(scan, ImplementationScan)
        assert isinstance(scan.files_changed, list)
        assert isinstance(scan.modules_added, list)
        assert isinstance(scan.apis_discovered, list)
        assert isinstance(scan.tests_found, list)
    
    def test_workflow_pattern_creation(self):
        """Test workflow pattern creation"""
        # Authentication workflow
        pattern = self.agent._create_workflow_pattern(
            "user authentication system", 
            [Entity("concept", "authentication", 0.9, "context")]
        )
        assert pattern is not None
        assert pattern.pattern_type == "authentication_workflow"
        assert pattern.confidence == 0.9
        
        # UI workflow
        pattern = self.agent._create_workflow_pattern(
            "user dashboard interface",
            [Entity("concept", "dashboard", 0.9, "context")]
        )
        assert pattern is not None
        assert pattern.pattern_type == "ui_workflow"
        
        # API workflow
        pattern = self.agent._create_workflow_pattern(
            "REST API service",
            [Entity("concept", "api", 0.9, "context")]
        )
        assert pattern is not None
        assert pattern.pattern_type == "api_workflow"
        
        # Unknown workflow
        pattern = self.agent._create_workflow_pattern(
            "random feature",
            [Entity("concept", "random", 0.9, "context")]
        )
        assert pattern is None
    
    @pytest.mark.asyncio
    async def test_context_updates(self):
        """Test context intelligence updates"""
        implementation_scan = ImplementationScan(
            files_changed=["test.cs", "test2.cs"],
            modules_added=["TestModule"],
            apis_discovered=["/api/test"],
            tests_found=["test_file.cs"]
        )
        
        updates = await self.agent._update_context_intelligence(
            "test feature", implementation_scan
        )
        
        assert len(updates) == 4  # file, module, api, test updates
        update_types = [u.update_type for u in updates]
        assert "file_activity" in update_types
        assert "module_growth" in update_types
        assert "api_expansion" in update_types
        assert "test_coverage" in update_types

class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fco = FeatureCompletionOrchestrator()
        
        # Mock all sub-agents
        self.fco.brain_ingestion_agent = AsyncMock()
        self.fco.discovery_engine = AsyncMock()
        self.fco.doc_intelligence = AsyncMock()
        self.fco.visual_generator = AsyncMock()
        self.fco.optimization_monitor = AsyncMock()
        
        # Setup return values
        self.fco.brain_ingestion_agent.ingest_feature.return_value = BrainData(
            entities=[Entity("concept", "auth", 0.9, "context")],
            patterns=[Pattern("test", 0.8, {})],
            context_updates=[ContextUpdate("test", {}, datetime.now())],
            implementation_scan=ImplementationScan(["test.cs"], ["TestModule"], ["/api/test"], ["test.cs"])
        )
        
        self.fco.discovery_engine.scan_implementation.return_value = ImplementationData(
            code_changes=[],
            git_analysis=MagicMock(),
            api_changes=[],
            test_analysis=MagicMock(),
            modules_affected=["TestModule"]
        )
        
        self.fco.doc_intelligence.analyze_and_update.return_value = DocumentationUpdates(
            gaps_found=[],
            content_updates=[],
            cross_ref_updates=[],
            files_updated=["README.md"]
        )
        
        self.fco.visual_generator.create_assets.return_value = VisualAssets(
            mermaid_diagrams=[],
            architecture_diagrams=[],
            image_prompts=[],
            saved_files=["diagram.mmd"]
        )
        
        self.fco.optimization_monitor.validate_system.return_value = HealthReport(
            performance_analysis=MagicMock(),
            architecture_review=MagicMock(),
            security_review=MagicMock(),
            optimization_recommendations=[],
            overall_health_score=95.0
        )
    
    @pytest.mark.asyncio
    async def test_successful_orchestration(self):
        """Test successful end-to-end orchestration"""
        report = await self.fco.orchestrate_feature_completion("test authentication feature")
        
        # Verify report structure
        assert isinstance(report, AlignmentReport)
        assert report.feature_description == "test authentication feature"
        assert report.execution_status == 'complete'
        assert len(report.errors) == 0
        assert report.files_updated == 1  # README.md
        assert report.health_report.overall_health_score == 95.0
        
        # Verify all stages were called
        self.fco.brain_ingestion_agent.ingest_feature.assert_called_once()
        self.fco.discovery_engine.scan_implementation.assert_called_once()
        self.fco.doc_intelligence.analyze_and_update.assert_called_once()
        self.fco.visual_generator.create_assets.assert_called_once()
        self.fco.optimization_monitor.validate_system.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_partial_failure_orchestration(self):
        """Test orchestration with partial failures"""
        # Make one stage fail
        self.fco.doc_intelligence.analyze_and_update.side_effect = Exception("Test failure")
        
        report = await self.fco.orchestrate_feature_completion("test feature")
        
        # Should complete with partial status
        assert report.execution_status == 'partial'
        assert len(report.errors) == 1
        assert "Documentation intelligence failed" in report.errors[0]
        
        # Other stages should still have been called
        self.fco.brain_ingestion_agent.ingest_feature.assert_called_once()
        self.fco.discovery_engine.scan_implementation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_critical_failure_orchestration(self):
        """Test orchestration with critical failure"""
        # Make FCO fail at initialization check
        self.fco.brain_ingestion_agent = None
        
        report = await self.fco.orchestrate_feature_completion("test feature")
        
        # Should fail completely
        assert report.execution_status == 'failed'
        assert len(report.errors) > 0
        assert report.files_updated == 0

class TestDataStructures:
    """Test data structure functionality"""
    
    def test_brain_data_fingerprint(self):
        """Test brain data fingerprint generation"""
        brain_data = BrainData(
            entities=[Entity("file", "test.cs", 0.9, "context")],
            patterns=[Pattern("test", 0.8, {"key": "value"})],
            context_updates=[],
            implementation_scan=ImplementationScan(["test.cs"], [], [], [])
        )
        
        fingerprint = brain_data.get_feature_fingerprint()
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16  # MD5 hash truncated to 16 chars
    
    def test_implementation_data_impact_score(self):
        """Test implementation data impact score calculation"""
        impl_data = ImplementationData(
            code_changes=[MagicMock(), MagicMock()],  # 2 changes
            git_analysis=MagicMock(),
            api_changes=[MagicMock()],  # 1 API change
            test_analysis=MagicMock(),
            modules_affected=["Module1", "Module2"]  # 2 modules
        )
        
        score = impl_data.change_impact_score
        expected = min(1.0, 2 * 0.1 + 1 * 0.3 + 2 * 0.2)  # 0.9
        assert score == expected
    
    def test_alignment_report_summary(self):
        """Test alignment report summary generation"""
        report = AlignmentReport(
            feature_description="test feature",
            execution_start=datetime.now(),
            execution_duration=5.5,
            brain_data=MagicMock(),
            implementation_data=MagicMock(),
            documentation_updates=MagicMock(),
            visual_assets=MagicMock(),
            health_report=MagicMock(overall_health_score=95.0),
            files_updated=5,
            diagrams_created=3,
            gaps_resolved=2,
            optimizations_found=1,
            issues_detected=0,
            execution_status='complete'
        )
        
        summary = report.generate_summary()
        assert "test feature" in summary or "Feature Completion Analysis" in summary
        assert "5" in summary  # files updated
        assert "3" in summary  # diagrams created
        assert "95" in summary  # health score
        assert "5.5" in summary  # duration

class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_pattern_detection_performance(self):
        """Test pattern detection performance with many inputs"""
        import time
        
        fco = FeatureCompletionOrchestrator()
        test_inputs = [
            f"feature number {i} is complete" for i in range(100)
        ]
        
        start_time = time.time()
        for input_text in test_inputs:
            fco.detect_feature_completion(input_text)
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second)
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Pattern detection too slow: {execution_time}s"
    
    @pytest.mark.asyncio
    async def test_entity_extraction_performance(self):
        """Test entity extraction performance"""
        import time
        
        agent = BrainIngestionAgentImpl()
        large_text = "Implemented AuthService.cs with login and authenticate functions " * 100
        
        start_time = time.time()
        entities = await agent._extract_entities(large_text)
        end_time = time.time()
        
        # Should complete in reasonable time
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Entity extraction too slow: {execution_time}s"
        assert len(entities) <= 20  # Should be limited

# ====================================================================================
# TEST EXECUTION AND REPORTING
# ====================================================================================

def run_all_tests():
    """Run all tests and generate report"""
    import pytest
    import sys
    
    # Configure pytest to run our tests
    test_args = [
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "-x",  # Stop on first failure
    ]
    
    print("🧪 Running Feature Completion Orchestrator Test Suite...")
    print("=" * 60)
    
    # Run tests
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    # Quick validation test
    print("🧪 Feature Completion Orchestrator Test Validation")
    print("=" * 50)
    
    # Test pattern detection
    fco = FeatureCompletionOrchestrator()
    test_result = fco.detect_feature_completion("authentication feature is complete")
    print(f"✅ Pattern detection test: {test_result}")
    
    # Test brain ingestion agent
    brain_agent = BrainIngestionAgentImpl()
    print(f"✅ Brain ingestion agent created: {brain_agent.__class__.__name__}")
    
    # Test data structures
    brain_data = BrainData([], [], [], ImplementationScan([], [], [], []))
    fingerprint = brain_data.get_feature_fingerprint()
    print(f"✅ Data structures test: fingerprint={fingerprint}")
    
    print("\n🎯 Test validation complete!")
    print("Run with pytest for full test suite:")
    print(f"pytest {__file__} -v")