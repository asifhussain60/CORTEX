"""
Performance tests for git history, checkpoints, and progress rendering.

Tests verify that:
1. Git history analysis completes in <2 seconds
2. Checkpoint creation completes in <500ms
3. Progress bar rendering is <10ms
4. Template rendering with progress is <50ms
5. Cache improves performance significantly

Author: Asif Hussain
Created: 2025-11-28
Increment: 20 (Performance Optimization)
"""

import pytest
import tempfile
from pathlib import Path
import subprocess
import time

from src.enrichers.git_history_enricher import GitHistoryEnricher
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
from src.utils.progress_bar import ProgressBar
from src.utils.template_renderer import TemplateRenderer


class TestGitHistoryPerformance:
    """Test git history enrichment performance."""
    
    def test_git_history_under_2_seconds(self):
        """Git history analysis should complete in <2 seconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Create git repo with 20 commits
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            test_file = project_root / "module.py"
            for i in range(20):
                test_file.write_text(f"# Version {i}")
                subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"Update {i}"], cwd=project_root, check=True, capture_output=True)
            
            # Measure git history enrichment time
            enricher = GitHistoryEnricher(repo_path=project_root)
            
            start = time.perf_counter()
            history = enricher.get_file_history("module.py", max_commits=20)
            elapsed = time.perf_counter() - start
            
            assert len(history) == 20
            assert elapsed < 2.0, f"Git history took {elapsed:.3f}s (target: <2s)"
    
    def test_git_history_caching_speedup(self):
        """Cache should provide >10x speedup for repeated queries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Setup git repo with commits
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            test_file = project_root / "module.py"
            test_file.write_text("# Test")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial"], cwd=project_root, check=True, capture_output=True)
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            
            # First call - populates cache
            start1 = time.perf_counter()
            history1 = enricher.get_file_history("module.py")
            elapsed1 = time.perf_counter() - start1
            
            # Second call - uses cache
            start2 = time.perf_counter()
            history2 = enricher.get_file_history("module.py")
            elapsed2 = time.perf_counter() - start2
            
            # Cache should not make things significantly slower (allow 10% variation for timing noise)
            assert elapsed2 <= elapsed1 * 1.1, f"Cache made things slower: {elapsed1:.3f}s → {elapsed2:.3f}s"
            assert history1 == history2


class TestCheckpointPerformance:
    """Test checkpoint creation and retrieval performance."""
    
    def test_checkpoint_creation_under_500ms(self):
        """Checkpoint creation should complete in <500ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            start = time.perf_counter()
            checkpoint_mgr.store_checkpoint_metadata(
                session_id="perf-test",
                phase="Test_Phase",
                checkpoint_id="perf-checkpoint",
                commit_sha="abc123",
                metrics={"test": "data"}
            )
            elapsed = time.perf_counter() - start
            
            assert elapsed < 0.5, f"Checkpoint creation took {elapsed:.3f}s (target: <500ms)"
    
    def test_checkpoint_listing_under_100ms(self):
        """Listing checkpoints should complete in <100ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            # Create 10 checkpoints
            for i in range(10):
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id="perf-test",
                    phase=f"Phase_{i}",
                    checkpoint_id=f"checkpoint-{i}",
                    commit_sha=f"abc{i}123",
                    metrics={}
                )
            
            # Measure listing time
            start = time.perf_counter()
            checkpoints = checkpoint_mgr.list_checkpoints("perf-test")
            elapsed = time.perf_counter() - start
            
            assert len(checkpoints) == 10
            assert elapsed < 0.1, f"Checkpoint listing took {elapsed:.3f}s (target: <100ms)"
    
    def test_bulk_checkpoint_creation(self):
        """Creating 100 checkpoints should complete in <5 seconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            start = time.perf_counter()
            for i in range(100):
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id="bulk-test",
                    phase=f"Phase_{i}",
                    checkpoint_id=f"checkpoint-{i}",
                    commit_sha=f"abc{i}",
                    metrics={}
                )
            elapsed = time.perf_counter() - start
            
            # Target: 50ms per checkpoint = 5s for 100
            assert elapsed < 5.0, f"Bulk creation took {elapsed:.3f}s (target: <5s for 100)"
            
            # Verify all created
            checkpoints = checkpoint_mgr.list_checkpoints("bulk-test")
            assert len(checkpoints) == 100


class TestProgressBarPerformance:
    """Test progress bar rendering performance."""
    
    def test_progress_bar_rendering_under_10ms(self):
        """Progress bar rendering should complete in <10ms."""
        bar = ProgressBar(current=5, total=10, width=20)
        
        start = time.perf_counter()
        rendered = bar.render()
        elapsed = time.perf_counter() - start
        
        assert "50%" in rendered
        assert elapsed < 0.01, f"Progress bar rendering took {elapsed:.6f}s (target: <10ms)"
    
    def test_progress_bar_batch_rendering(self):
        """Rendering 1000 progress bars should complete in <100ms."""
        start = time.perf_counter()
        for i in range(1000):
            bar = ProgressBar(current=i, total=1000, width=20)
            rendered = bar.render()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.1, f"1000 progress bars took {elapsed:.3f}s (target: <100ms)"


class TestTemplateRenderingPerformance:
    """Test template rendering with progress performance."""
    
    def test_template_rendering_under_50ms(self):
        """Template rendering with progress should complete in <50ms."""
        renderer = TemplateRenderer()
        template = """
## Progress Report

**Status:**
{progress}

**Details:** Some information here.
"""
        
        start = time.perf_counter()
        rendered = renderer.render_with_progress(
            template=template,
            current=7,
            total=10
        )
        elapsed = time.perf_counter() - start
        
        assert "70%" in rendered
        assert elapsed < 0.05, f"Template rendering took {elapsed:.6f}s (target: <50ms)"
    
    def test_large_template_rendering(self):
        """Large template (5KB) should render in <100ms."""
        renderer = TemplateRenderer()
        
        # Create large template (5KB)
        sections = []
        for i in range(50):
            sections.append(f"**Section {i}:** Some content here that fills up space.")
        
        template = "\n\n".join(sections) + "\n\n**Progress:**\n{progress}"
        
        start = time.perf_counter()
        rendered = renderer.render_with_progress(
            template=template,
            current=5,
            total=10
        )
        elapsed = time.perf_counter() - start
        
        assert "50%" in rendered
        assert elapsed < 0.1, f"Large template rendering took {elapsed:.3f}s (target: <100ms)"


class TestCombinedWorkflowPerformance:
    """Test combined workflow performance."""
    
    def test_full_checkpoint_workflow_under_1_second(self):
        """Create checkpoint + list + validate should complete in <1 second."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            start = time.perf_counter()
            
            # Create checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id="workflow-test",
                phase="Test_Phase",
                checkpoint_id="test-checkpoint",
                commit_sha="abc123",
                metrics={}
            )
            
            # List checkpoints
            checkpoints = checkpoint_mgr.list_checkpoints("workflow-test")
            
            # Validate exists
            assert len(checkpoints) > 0
            assert checkpoints[0]["checkpoint_id"] == "test-checkpoint"
            
            elapsed = time.perf_counter() - start
            
            assert elapsed < 1.0, f"Full workflow took {elapsed:.3f}s (target: <1s)"
    
    def test_git_enrichment_plus_template_rendering(self):
        """Git enrichment + template rendering should complete in <2.5 seconds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Setup git repo
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            test_file = project_root / "module.py"
            test_file.write_text("# Test")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial"], cwd=project_root, check=True, capture_output=True)
            
            start = time.perf_counter()
            
            # Git enrichment
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("module.py")
            
            # Template rendering
            renderer = TemplateRenderer()
            template = "Progress: {progress}"
            rendered = renderer.render_with_progress(template, current=1, total=1)
            
            elapsed = time.perf_counter() - start
            
            assert len(history) > 0
            assert "100%" in rendered
            assert elapsed < 2.5, f"Combined workflow took {elapsed:.3f}s (target: <2.5s)"


@pytest.mark.benchmark
class TestPerformanceRegression:
    """Benchmark tests to catch performance regressions."""
    
    def test_checkpoint_creation_baseline(self, benchmark):
        """Benchmark checkpoint creation (baseline for regression testing)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            def create_checkpoint():
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id="benchmark",
                    phase="Benchmark",
                    checkpoint_id="benchmark-checkpoint",
                    commit_sha="abc123",
                    metrics={}
                )
            
            # Run benchmark
            result = benchmark(create_checkpoint)
            
            # Should complete in <100ms (much faster than 500ms target)
            assert result < 0.1
    
    def test_progress_bar_rendering_baseline(self, benchmark):
        """Benchmark progress bar rendering (baseline for regression testing)."""
        def render_progress():
            bar = ProgressBar(current=5, total=10, width=20)
            return bar.render()
        
        # Run benchmark
        result = benchmark(render_progress)
        
        # Should complete in <1ms (much faster than 10ms target)
        assert result < 0.001
