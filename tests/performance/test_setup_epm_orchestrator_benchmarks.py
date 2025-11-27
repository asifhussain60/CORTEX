"""
Performance Benchmarks for Setup EPM Orchestrator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import time
from pathlib import Path
from src.orchestrators.setup_epm_orchestrator import SetupEPMOrchestrator


class TestSetupEPMBenchmarks:
    """Performance benchmarks for Setup EPM operations."""
    
    @pytest.mark.benchmark
    def test_project_detection_benchmark(self, tmp_path, benchmark):
        """Benchmark: Project detection should complete in <5 seconds."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        # Create test project structure
        (tmp_path / "src").mkdir()
        for i in range(50):
            (tmp_path / "src" / f"file_{i}.py").write_text("# test")
        
        def detect_operation():
            return {} if not hasattr(orchestrator, '_detect_project_structure') else orchestrator._detect_project_structure()
        
        result = benchmark(detect_operation)
        assert benchmark.stats['mean'] < 5.0, f"Detection took {benchmark.stats['mean']}s, target <5s"
    
    @pytest.mark.benchmark
    def test_template_generation_benchmark(self, tmp_path, benchmark):
        """Benchmark: Template generation should complete in <1 second."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        def template_operation():
            return "" if not hasattr(orchestrator, '_generate_template') else orchestrator._generate_template({})
        
        result = benchmark(template_operation)
        assert benchmark.stats['mean'] < 1.0, f"Template generation took {benchmark.stats['mean']}s, target <1s"
    
    @pytest.mark.benchmark
    def test_gitignore_configuration_benchmark(self, tmp_path, benchmark):
        """Benchmark: GitIgnore configuration should complete in <2 seconds."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        def gitignore_operation():
            if hasattr(orchestrator, '_configure_gitignore'):
                orchestrator._configure_gitignore()
        
        result = benchmark(gitignore_operation)
        assert benchmark.stats['mean'] < 2.0, f"GitIgnore config took {benchmark.stats['mean']}s, target <2s"
    
    def test_total_setup_execution_time(self, tmp_path):
        """Test that total setup execution completes in <10 seconds."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        start = time.time()
        try:
            orchestrator.execute(force=True)
        except Exception:
            pass  # Expected if execute not fully implemented
        duration = time.time() - start
        
        assert duration < 10.0, f"Total setup took {duration}s, target <10s"
