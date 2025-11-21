"""
Test Suite for CORTEX Documentation Generation System
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path

from src.documentation.discovery.capability_scanner import CapabilityScanner, Capability
from src.documentation.templates.template_engine import TemplateEngine
from src.documentation.orchestrator import DocumentationOrchestrator


class TestCapabilityScanner:
    """Test capability discovery engine"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def scanner(self, temp_workspace):
        """Create scanner instance"""
        return CapabilityScanner(temp_workspace)
    
    def test_scanner_initialization(self, scanner, temp_workspace):
        """Test scanner initializes correctly"""
        assert scanner.workspace_root == Path(temp_workspace)
        assert isinstance(scanner.capabilities, dict)
    
    def test_scan_yaml_configs(self, scanner, temp_workspace):
        """Test YAML config scanning"""
        # Create test YAML file
        yaml_dir = Path(temp_workspace) / 'cortex-brain'
        yaml_dir.mkdir(parents=True, exist_ok=True)
        
        test_yaml = yaml_dir / 'cortex-operations.yaml'
        test_yaml.write_text("""
operations:
  test_operation:
    description: "Test operation"
    status: "active"
    category: "testing"
""", encoding='utf-8')
        
        scanner.scan_yaml_configs()
        
        assert len(scanner.capabilities) > 0
        assert any('test_operation' in key for key in scanner.capabilities.keys())
    
    def test_scan_source_code(self, scanner, temp_workspace):
        """Test Python source code scanning"""
        # Create test Python file
        src_dir = Path(temp_workspace) / 'src'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = src_dir / 'test_module.py'
        test_file.write_text("""
class TestAgent:
    '''Test agent implementation'''
    pass

class TestPlugin:
    '''Test plugin implementation'''
    pass
""", encoding='utf-8')
        
        scanner.scan_source_code()
        
        # Should find TestAgent and TestPlugin
        agent_keys = [k for k in scanner.capabilities.keys() if 'TestAgent' in k]
        plugin_keys = [k for k in scanner.capabilities.keys() if 'TestPlugin' in k]
        
        assert len(agent_keys) > 0
        assert len(plugin_keys) > 0
    
    def test_get_by_type(self, scanner):
        """Test filtering capabilities by type"""
        # Add test capabilities
        scanner.capabilities['op:test1'] = Capability('test1', 'operation', 'Test 1', 'active')
        scanner.capabilities['mod:test2'] = Capability('test2', 'module', 'Test 2', 'active')
        scanner.capabilities['op:test3'] = Capability('test3', 'operation', 'Test 3', 'active')
        
        operations = scanner.get_by_type('operation')
        modules = scanner.get_by_type('module')
        
        assert len(operations) == 2
        assert len(modules) == 1
    
    def test_export_registry(self, scanner, temp_workspace):
        """Test capability registry export"""
        scanner.capabilities['test:cap'] = Capability('TestCap', 'test', 'Test capability', 'active')
        
        output_path = Path(temp_workspace) / 'registry.json'
        scanner.export_registry(str(output_path))
        
        assert output_path.exists()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'generated_at' in data
        assert 'total_capabilities' in data
        assert 'capabilities' in data
        assert data['total_capabilities'] > 0


class TestTemplateEngine:
    """Test template engine"""
    
    @pytest.fixture
    def engine(self):
        """Create template engine instance"""
        return TemplateEngine()
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert isinstance(engine.templates, dict)
        assert 'capabilities' in engine.templates
        assert 'awakening_story' in engine.templates
    
    def test_generate_capabilities_doc(self, engine):
        """Test capabilities document generation"""
        test_data = {
            'version': '3.0',
            'updated': '2025-11-21',
            'status': '✅ Production Ready',
            'capabilities': {}
        }
        
        content = engine.generate_capabilities_doc(test_data)
        
        assert '# CORTEX AI Assistant - Executive Summary' in content
        assert 'What is CORTEX' in content
        assert 'Key Differentiators' in content
        assert 'Core Capabilities' in content
    
    def test_generate_awakening_story(self, engine):
        """Test awakening story generation"""
        content = engine.generate_awakening_story()
        
        assert '# The Awakening of CORTEX' in content
        assert 'Prologue' in content
        assert 'Chapter' in content
        assert 'Epilogue' in content
    
    def test_generate_chatgpt_prompts(self, engine):
        """Test ChatGPT image prompt generation"""
        prompts = ['architecture', 'agent_interaction', 'memory_system', 'workflow']
        
        for prompt_type in prompts:
            content = engine.generate_chatgpt_image_prompt(prompt_type)
            
            assert len(content) > 100
            assert 'Create' in content or 'Style' in content
    
    def test_generate_mermaid_diagrams(self, engine):
        """Test Mermaid diagram generation"""
        diagrams = ['system_overview', 'tier_structure']
        
        for diagram_type in diagrams:
            content = engine.generate_mermaid_diagram(diagram_type, {})
            
            assert '```mermaid' in content
            assert 'graph' in content or 'flowchart' in content or 'sequenceDiagram' in content


class TestDocumentationOrchestrator:
    """Test documentation orchestrator"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        
        # Create minimal structure
        (Path(temp_dir) / 'src').mkdir(parents=True, exist_ok=True)
        (Path(temp_dir) / 'cortex-brain').mkdir(parents=True, exist_ok=True)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def orchestrator(self, temp_workspace):
        """Create orchestrator instance"""
        return DocumentationOrchestrator(temp_workspace)
    
    def test_orchestrator_initialization(self, orchestrator, temp_workspace):
        """Test orchestrator initializes correctly"""
        assert orchestrator.workspace_root == Path(temp_workspace)
        assert isinstance(orchestrator.scanner, CapabilityScanner)
        assert isinstance(orchestrator.template_engine, TemplateEngine)
    
    def test_executive_summary_generation(self, orchestrator):
        """Test executive summary generation"""
        capabilities = {}
        registry = {'total_capabilities': 0}
        
        output_path = orchestrator._generate_executive_summary(capabilities, registry)
        
        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding='utf-8')
        assert '# CORTEX Executive Summary' in content
    
    def test_capabilities_matrix_generation(self, orchestrator):
        """Test capabilities matrix generation"""
        capabilities = {}
        registry = {}
        
        output_path = orchestrator._generate_capabilities_matrix(capabilities, registry)
        
        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding='utf-8')
        assert 'CORTEX AI Assistant' in content
    
    def test_awakening_story_generation(self, orchestrator):
        """Test awakening story generation"""
        capabilities = {}
        registry = {}
        
        output_path = orchestrator._generate_awakening_story(capabilities, registry)
        
        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding='utf-8')
        assert 'The Awakening of CORTEX' in content
    
    def test_chatgpt_prompt_generation(self, orchestrator):
        """Test ChatGPT prompt generation"""
        capabilities = {}
        registry = {}
        
        output_path = orchestrator._generate_chatgpt_prompt(capabilities, registry, 'architecture')
        
        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding='utf-8')
        assert len(content) > 50
    
    def test_mermaid_diagram_generation(self, orchestrator):
        """Test Mermaid diagram generation"""
        capabilities = {}
        registry = {}
        
        output_path = orchestrator._generate_mermaid_diagram(capabilities, registry, 'architecture', 'system-overview')
        
        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding='utf-8')
        assert '```mermaid' in content
    
    def test_safe_generate(self, orchestrator):
        """Test safe generation wrapper"""
        def mock_success():
            return "success"
        
        def mock_failure():
            raise ValueError("Test error")
        
        result_success = orchestrator._safe_generate('test_success', mock_success)
        assert result_success['status'] == 'success'
        
        result_failure = orchestrator._safe_generate('test_failure', mock_failure)
        assert result_failure['status'] == 'failed'
        assert 'Test error' in result_failure['error']
    
    @pytest.mark.slow
    def test_full_generation_pipeline(self, orchestrator):
        """Test full documentation generation pipeline"""
        # This is a slow test that generates all components
        report = orchestrator.generate_all(parallel=False)
        
        assert 'started_at' in report
        assert 'completed_at' in report
        assert 'duration_seconds' in report
        assert 'results' in report


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from discovery to generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal workspace structure
            workspace = Path(temp_dir)
            (workspace / 'src').mkdir()
            (workspace / 'cortex-brain').mkdir()
            
            # Create test capability file
            test_yaml = workspace / 'cortex-brain' / 'cortex-operations.yaml'
            test_yaml.write_text("""
operations:
  test_op:
    description: "Test operation"
    status: "active"
""", encoding='utf-8')
            
            # Run discovery
            scanner = CapabilityScanner(str(workspace))
            capabilities = scanner.scan_all()
            
            assert len(capabilities) > 0
            
            # Generate documentation
            orchestrator = DocumentationOrchestrator(str(workspace))
            
            # Generate a few components (not full pipeline for speed)
            capabilities_dict = scanner.capabilities
            registry = {'total_capabilities': len(capabilities)}
            
            exec_summary = orchestrator._generate_executive_summary(capabilities_dict, registry)
            assert Path(exec_summary).exists()
            
            caps_matrix = orchestrator._generate_capabilities_matrix(capabilities_dict, registry)
            assert Path(caps_matrix).exists()
            
            story = orchestrator._generate_awakening_story(capabilities_dict, registry)
            assert Path(story).exists()


# Performance tests
class TestPerformance:
    """Performance tests"""
    
    def test_discovery_performance(self):
        """Test that discovery completes in reasonable time"""
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / 'src').mkdir()
            (workspace / 'cortex-brain').mkdir()
            
            scanner = CapabilityScanner(str(workspace))
            
            start_time = time.time()
            scanner.scan_all()
            duration = time.time() - start_time
            
            # Should complete in < 5 seconds for small workspace
            assert duration < 5.0
    
    def test_generation_performance(self):
        """Test that component generation is fast"""
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / 'src').mkdir()
            (workspace / 'cortex-brain').mkdir()
            
            orchestrator = DocumentationOrchestrator(str(workspace))
            
            start_time = time.time()
            orchestrator._generate_executive_summary({}, {})
            duration = time.time() - start_time
            
            # Single component should generate in < 1 second
            assert duration < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
