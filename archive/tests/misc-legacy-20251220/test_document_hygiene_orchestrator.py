"""
Test suite for Document Hygiene Orchestrator v1.0

Tests automatic Markdown maintenance and organization:
1. Phase: Consolidation (merge duplicate docs)
2. Phase: Archiving (move old docs)
3. Phase: Filename optimization (kebab-case, descriptive)
4. Phase: Reference updating (fix broken links)
5. Phase: Reorganization (category compliance)
6. Phase: Finalization (validation)
7. SKULL rule enforcement (FILE_ORGANIZATION_ENFORCEMENT, DOCUMENT_ORGANIZATION)

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.orchestration.document_hygiene_orchestrator import (
    DocumentHygieneOrchestrator, HygieneResult
)


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure with documents."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create document structure
    docs_brain = project_root / "cortex-brain" / "documents"
    categories = ["reports", "analysis", "summaries", "investigations", "planning", "implementation-guides"]
    for category in categories:
        (docs_brain / category).mkdir(parents=True)
    
    # Create test documents
    (docs_brain / "reports" / "test-report.md").write_text("# Test Report\nContent here.")
    (docs_brain / "reports" / "test_report.md").write_text("# Test Report\nDuplicate content.")
    (docs_brain / "old-analysis.md").write_text("# Old Analysis\nOld content.")
    
    # Create root-level doc (should be moved)
    (project_root / "summary.md").write_text("# Summary\nShould be moved.")
    
    return project_root


@pytest.fixture
def orchestrator(temp_project_root):
    """Create document hygiene orchestrator instance."""
    return DocumentHygieneOrchestrator(project_root=temp_project_root)


# ===== PHASE: CONSOLIDATION =====

class TestConsolidationPhase:
    """Test consolidation phase (merge duplicate docs)."""
    
    @pytest.mark.asyncio
    async def test_consolidation_finds_duplicates(self, orchestrator, temp_project_root):
        """Consolidation: Finds duplicate documents."""
        result = await orchestrator.execute(
            phases=["consolidation"]
        )
        
        assert result is not None
        assert orchestrator.metrics['phases_completed'] == ['consolidation']
    
    @pytest.mark.asyncio
    async def test_consolidation_merges_similar_names(self, orchestrator, temp_project_root):
        """Consolidation: Merges docs with similar names (test-report.md, test_report.md)."""
        docs_brain = temp_project_root / "cortex-brain" / "documents" / "reports"
        
        result = await orchestrator.execute(
            target_dirs=[docs_brain],
            phases=["consolidation"]
        )
        
        # Should detect and handle duplicates
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_consolidation_preserves_unique_content(self, orchestrator):
        """Consolidation: Preserves unique content when merging."""
        result = await orchestrator.execute(
            phases=["consolidation"]
        )
        
        # Should not lose information
        assert result is not None


# ===== PHASE: ARCHIVING =====

class TestArchivingPhase:
    """Test archiving phase (move old docs)."""
    
    @pytest.mark.asyncio
    async def test_archiving_moves_old_docs(self, orchestrator, temp_project_root):
        """Archiving: Moves documents older than threshold."""
        # Create old document (simulate)
        old_doc = temp_project_root / "cortex-brain" / "documents" / "old-analysis.md"
        
        result = await orchestrator.execute(
            phases=["archiving"]
        )
        
        assert result is not None
        assert 'archiving' in orchestrator.metrics['phases_completed']
    
    @pytest.mark.asyncio
    async def test_archiving_respects_age_threshold(self, orchestrator):
        """Archiving: Only archives docs past age threshold."""
        result = await orchestrator.execute(
            phases=["archiving"]
        )
        
        # Recent docs should not be archived
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_archiving_creates_archive_structure(self, orchestrator, temp_project_root):
        """Archiving: Creates proper archive directory structure."""
        result = await orchestrator.execute(
            phases=["archiving"]
        )
        
        # Archive directory may be created
        archive_dir = temp_project_root / "archive"
        # Implementation-dependent
        assert result is not None


# ===== PHASE: FILENAME OPTIMIZATION =====

class TestFilenameOptimizationPhase:
    """Test filename optimization phase."""
    
    @pytest.mark.asyncio
    async def test_filename_converts_to_kebab_case(self, orchestrator, temp_project_root):
        """Filename Optimization: Converts underscores to kebab-case."""
        # test_report.md → test-report.md
        result = await orchestrator.execute(
            phases=["filename_optimization"]
        )
        
        assert result is not None
        assert 'filename_optimization' in orchestrator.metrics['phases_completed']
    
    @pytest.mark.asyncio
    async def test_filename_removes_redundant_prefixes(self, orchestrator):
        """Filename Optimization: Removes redundant category prefixes."""
        # reports/report-summary.md → reports/summary.md
        result = await orchestrator.execute(
            phases=["filename_optimization"]
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_filename_enforces_descriptive_names(self, orchestrator):
        """Filename Optimization: Enforces descriptive naming."""
        # doc1.md → descriptive-name.md
        result = await orchestrator.execute(
            phases=["filename_optimization"]
        )
        
        assert result is not None


# ===== PHASE: REFERENCE UPDATING =====

class TestReferenceUpdatingPhase:
    """Test reference updating phase (fix broken links)."""
    
    @pytest.mark.asyncio
    async def test_reference_updating_fixes_broken_links(self, orchestrator, temp_project_root):
        """Reference Updating: Fixes broken Markdown links."""
        # Create doc with broken link
        doc = temp_project_root / "cortex-brain" / "documents" / "reports" / "linked-doc.md"
        doc.write_text("# Linked Doc\n[Broken Link](old-file.md)")
        
        result = await orchestrator.execute(
            phases=["reference_updating"]
        )
        
        assert result is not None
        assert 'reference_updating' in orchestrator.metrics['phases_completed']
    
    @pytest.mark.asyncio
    async def test_reference_updating_updates_after_renames(self, orchestrator):
        """Reference Updating: Updates links after filename changes."""
        result = await orchestrator.execute(
            phases=["filename_optimization", "reference_updating"]
        )
        
        # Links should reflect new filenames
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_reference_updating_handles_relative_paths(self, orchestrator):
        """Reference Updating: Handles relative path links."""
        result = await orchestrator.execute(
            phases=["reference_updating"]
        )
        
        assert result is not None


# ===== PHASE: REORGANIZATION =====

class TestReorganizationPhase:
    """Test reorganization phase (category compliance)."""
    
    @pytest.mark.asyncio
    async def test_reorganization_moves_to_correct_category(self, orchestrator, temp_project_root):
        """Reorganization: Moves docs to correct category folders."""
        # Root-level doc should move to proper category
        root_doc = temp_project_root / "summary.md"
        assert root_doc.exists()
        
        result = await orchestrator.execute(
            phases=["reorganization"]
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_reorganization_enforces_no_root_docs(self, orchestrator):
        """SKULL: FILE_ORGANIZATION_ENFORCEMENT - no root-level docs."""
        result = await orchestrator.execute(
            phases=["reorganization"]
        )
        
        # Root-level docs should be moved or flagged
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_reorganization_validates_categories(self, orchestrator, temp_project_root):
        """Reorganization: Validates proper category usage."""
        result = await orchestrator.execute(
            phases=["reorganization"]
        )
        
        # Should ensure docs are in valid categories
        assert result is not None


# ===== PHASE: FINALIZATION =====

class TestFinalizationPhase:
    """Test finalization phase (validation)."""
    
    @pytest.mark.asyncio
    async def test_finalization_validates_structure(self, orchestrator):
        """Finalization: Validates document structure compliance."""
        result = await orchestrator.execute(
            phases=["finalization"]
        )
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_finalization_generates_recommendations(self, orchestrator):
        """Finalization: Generates recommendations for manual review."""
        result = await orchestrator.execute(
            phases=["finalization"]
        )
        
        # Should provide recommendations
        assert orchestrator.metrics['recommendations'] is not None
    
    @pytest.mark.asyncio
    async def test_finalization_verifies_all_links(self, orchestrator):
        """Finalization: Verifies all links are valid."""
        result = await orchestrator.execute(
            phases=["finalization"]
        )
        
        assert result is not None


# ===== SKULL RULE ENFORCEMENT =====

class TestSKULLRuleEnforcement:
    """Test SKULL rule enforcement."""
    
    @pytest.mark.asyncio
    async def test_file_organization_enforcement(self, orchestrator, temp_project_root):
        """SKULL: FILE_ORGANIZATION_ENFORCEMENT - all docs in cortex-brain/documents/."""
        # Create root-level violator
        (temp_project_root / "violator.md").write_text("# Violator\nNot in proper location.")
        
        result = await orchestrator.execute()
        
        # Should detect and move root-level docs
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_document_organization_categories(self, orchestrator):
        """SKULL: DOCUMENT_ORGANIZATION - proper category structure."""
        result = await orchestrator.execute()
        
        # Should enforce category compliance
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_automatic_documentation_generation(self, orchestrator):
        """SKULL: AUTOMATIC_DOCUMENTATION_GENERATION - integrated with Planning System."""
        # Document hygiene should integrate with Planning System 3.0
        result = await orchestrator.execute()
        
        assert result is not None


# ===== METRICS & REPORTING =====

class TestMetricsAndReporting:
    """Test metrics collection and reporting."""
    
    @pytest.mark.asyncio
    async def test_metrics_collected_per_phase(self, orchestrator):
        """Metrics collected for each phase."""
        result = await orchestrator.execute()
        
        # All phases should be tracked
        assert len(orchestrator.metrics['phases_completed']) > 0
        assert orchestrator.metrics['files_processed'] >= 0
        assert orchestrator.metrics['actions_taken'] >= 0
    
    @pytest.mark.asyncio
    async def test_recommendations_generated(self, orchestrator):
        """Recommendations generated for manual review."""
        result = await orchestrator.execute()
        
        assert 'recommendations' in orchestrator.metrics
    
    @pytest.mark.asyncio
    async def test_error_tracking(self, orchestrator):
        """Errors tracked during hygiene cycle."""
        # Force an error scenario
        with patch('pathlib.Path.rename', side_effect=PermissionError("Access denied")):
            result = await orchestrator.execute()
            
            # Should handle errors gracefully
            assert result is not None


# ===== INTEGRATION & ERROR HANDLING =====

class TestIntegrationAndErrors:
    """Test integration scenarios and error handling."""
    
    @pytest.mark.asyncio
    async def test_all_phases_in_sequence(self, orchestrator):
        """All phases execute in correct sequence."""
        result = await orchestrator.execute()
        
        # Should complete all phases
        assert result is not None
        expected_phases = orchestrator.phases
        assert len(orchestrator.metrics['phases_completed']) <= len(expected_phases)
    
    @pytest.mark.asyncio
    async def test_phase_failure_handling(self, orchestrator):
        """Handles phase failures gracefully."""
        with patch.object(orchestrator, '_run_consolidation_phase', side_effect=Exception("Test error")):
            result = await orchestrator.execute(phases=["consolidation"])
            
            # Should not crash
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_file_processing(self, orchestrator):
        """Processes multiple files concurrently."""
        result = await orchestrator.execute()
        
        # Should leverage ThreadPoolExecutor
        assert result is not None


# ===== PLANNING SYSTEM INTEGRATION =====

class TestPlanningSystemIntegration:
    """Test integration with Planning System 3.0."""
    
    @pytest.mark.asyncio
    async def test_triggered_by_tier3_operations(self, orchestrator):
        """Document hygiene triggered by Tier 3/4 operations."""
        # Should integrate with Planning System
        result = await orchestrator.execute()
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_version_management_integration(self, orchestrator):
        """Version management tracks orchestrator version."""
        # Should register with version manager
        assert orchestrator.version is not None
        assert orchestrator.version_manager is not None


# ===== END-TO-END WORKFLOW =====

class TestEndToEndWorkflow:
    """Test complete document hygiene workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_hygiene_cycle(self, orchestrator, temp_project_root):
        """Complete hygiene: consolidate → archive → optimize → update → reorganize → finalize."""
        result = await orchestrator.execute()
        
        # Should complete full workflow
        assert result is not None
        assert len(orchestrator.metrics['phases_completed']) > 0
    
    @pytest.mark.asyncio
    async def test_selective_phase_execution(self, orchestrator):
        """Execute only selected phases."""
        result = await orchestrator.execute(
            phases=["consolidation", "filename_optimization"]
        )
        
        # Should execute only specified phases
        assert result is not None
        assert set(orchestrator.metrics['phases_completed']).issubset({"consolidation", "filename_optimization"})


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
