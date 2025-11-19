"""
Test Documentation File Creation - Verify Files Actually Created

This test MUST be run after every document generation entry point module execution
to verify that files are ACTUALLY created in the expected folders.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDocumentationFileCreation:
    """Test suite to verify documentation files are actually created"""
    
    @pytest.fixture
    def project_root(self):
        """Get project root"""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def docs_path(self, project_root):
        """Get docs folder"""
        return project_root / "docs"
    
    @pytest.fixture
    def expected_folders(self, docs_path):
        """Define all expected documentation folders"""
        return {
            "architecture": docs_path / "architecture",
            "demos": docs_path / "demos",
            "getting-started": docs_path / "getting-started",
            "guides": docs_path / "guides",
            "operations": docs_path / "operations",
            "plugins": docs_path / "plugins",
            "reference": docs_path / "reference",
            "diagrams": docs_path / "diagrams",
            "performance": docs_path / "performance",
            "recommendations": docs_path / "recommendations",
            "project": docs_path / "project",
            "telemetry": docs_path / "telemetry",
            "summaries": docs_path / "summaries",
            "generated": docs_path / "generated",  # Currently empty
            "test-generated": docs_path / "test-generated"
        }
    
    @pytest.fixture
    def minimum_expected_files(self):
        """Minimum expected file counts per folder (after generation)"""
        return {
            "architecture": 3,  # At least 3 files (agents.md, brain-protection.md, overview.md, tier-system.md exist)
            "getting-started": 2,  # At least 2 files (configuration.md, installation.md, quick-start.md exist)
            "guides": 3,  # At least 3 files
            "operations": 3,  # At least 3 files
            "reference": 2,  # At least 2 files
            "generated": 5,  # Should have files after generation (currently 0)
            "test-generated": 2  # Has 3 files (README.md, metrics.md, project-overview.md)
        }
    
    def test_folders_exist(self, expected_folders):
        """Test 1: Verify all expected folders exist"""
        logger.info("=" * 80)
        logger.info("TEST 1: Verifying documentation folders exist")
        logger.info("=" * 80)
        
        missing_folders = []
        for folder_name, folder_path in expected_folders.items():
            if not folder_path.exists():
                missing_folders.append(folder_name)
                logger.error(f"❌ Missing folder: {folder_name} ({folder_path})")
            else:
                logger.info(f"✓ Folder exists: {folder_name}")
        
        assert len(missing_folders) == 0, f"Missing folders: {', '.join(missing_folders)}"
    
    def test_folders_not_empty(self, expected_folders, minimum_expected_files):
        """Test 2: Verify folders have actual files (not empty)"""
        logger.info("=" * 80)
        logger.info("TEST 2: Verifying folders are not empty")
        logger.info("=" * 80)
        
        empty_folders = []
        insufficient_files = []
        
        for folder_name, folder_path in expected_folders.items():
            if not folder_path.exists():
                continue
            
            # Count actual files (excluding subdirectories)
            files = list(folder_path.glob("*.md"))
            file_count = len(files)
            
            # Check if folder is completely empty
            if file_count == 0:
                empty_folders.append(folder_name)
                logger.error(f"❌ Empty folder: {folder_name} (0 files)")
                continue
            
            # Check if folder has minimum expected files
            expected_min = minimum_expected_files.get(folder_name, 1)
            if file_count < expected_min:
                insufficient_files.append((folder_name, file_count, expected_min))
                logger.warning(f"⚠️  {folder_name}: {file_count} files (expected at least {expected_min})")
            else:
                logger.info(f"✓ {folder_name}: {file_count} files (≥ {expected_min} expected)")
                # List first 3 files as sample
                for i, file in enumerate(files[:3]):
                    logger.info(f"    - {file.name}")
        
        # Report results
        if empty_folders:
            logger.error(f"\n❌ EMPTY FOLDERS: {', '.join(empty_folders)}")
        
        if insufficient_files:
            logger.warning(f"\n⚠️  INSUFFICIENT FILES:")
            for folder, actual, expected in insufficient_files:
                logger.warning(f"   {folder}: {actual} files (expected ≥ {expected})")
        
        # Assertion: No folders should be completely empty
        assert len(empty_folders) == 0, f"Empty folders found: {', '.join(empty_folders)}"
    
    def test_generated_folder_has_content(self, docs_path):
        """Test 3: Verify 'generated' folder has content after generation"""
        logger.info("=" * 80)
        logger.info("TEST 3: Verifying 'generated' folder has content")
        logger.info("=" * 80)
        
        generated_path = docs_path / "generated"
        
        if not generated_path.exists():
            pytest.fail(f"Generated folder does not exist: {generated_path}")
        
        # Count files
        md_files = list(generated_path.glob("*.md"))
        all_files = [f for f in generated_path.iterdir() if f.is_file()]
        
        logger.info(f"Generated folder: {generated_path}")
        logger.info(f"  Markdown files: {len(md_files)}")
        logger.info(f"  All files: {len(all_files)}")
        
        if len(all_files) == 0:
            logger.error("❌ CRITICAL: 'generated' folder is empty!")
            logger.error("    This indicates document generation is NOT working.")
            logger.error("    Files should be created in docs/generated/ during generation.")
            pytest.fail("Generated folder is empty - document generation not creating files")
        else:
            logger.info(f"✓ Generated folder contains {len(all_files)} files")
            for file in all_files[:5]:  # Show first 5
                logger.info(f"    - {file.name}")
    
    def test_file_creation_timestamps(self, docs_path):
        """Test 4: Verify files were recently created/modified"""
        logger.info("=" * 80)
        logger.info("TEST 4: Verifying file creation timestamps")
        logger.info("=" * 80)
        
        # Check files in test-generated (known to have content)
        test_generated_path = docs_path / "test-generated"
        
        if not test_generated_path.exists():
            pytest.skip("test-generated folder not found")
        
        files = list(test_generated_path.glob("*.md"))
        
        if len(files) == 0:
            pytest.skip("No files in test-generated folder")
        
        now = datetime.now()
        recent_files = []
        old_files = []
        
        for file in files:
            modified_time = datetime.fromtimestamp(file.stat().st_mtime)
            age_days = (now - modified_time).days
            
            if age_days <= 7:  # Modified within last week
                recent_files.append((file.name, age_days))
            else:
                old_files.append((file.name, age_days))
        
        logger.info(f"Recent files (< 7 days): {len(recent_files)}")
        for filename, age in recent_files:
            logger.info(f"  ✓ {filename} ({age} days old)")
        
        if old_files:
            logger.info(f"\nOlder files (> 7 days): {len(old_files)}")
            for filename, age in old_files:
                logger.info(f"  - {filename} ({age} days old)")
        
        # At least some files should be recent if generation ran recently
        assert len(recent_files) > 0, "No recently modified files found"
    
    def test_enterprise_documentation_execution(self, project_root):
        """Test 5: Execute enterprise documentation and verify file creation"""
        logger.info("=" * 80)
        logger.info("TEST 5: Execute enterprise documentation generation")
        logger.info("=" * 80)
        
        try:
            # Import operation executor
            from src.operations import execute_operation
            
            # Execute in dry-run mode first to check what would be generated
            logger.info("Step 1: Dry-run mode (validation only)")
            dry_run_result = execute_operation(
                "generate documentation",
                profile="quick",
                project_root=project_root,
                dry_run=True
            )
            
            logger.info(f"Dry-run result: {dry_run_result.status}")
            logger.info(f"Success: {dry_run_result.success}")
            
            if dry_run_result.data:
                logger.info("Expected files to be generated:")
                files = dry_run_result.data.get("files_to_generate", [])
                for file in files[:10]:  # Show first 10
                    logger.info(f"  - {file}")
            
            # Execute in live mode (actual generation)
            logger.info("\nStep 2: Live mode (actual generation)")
            logger.warning("⚠️  This will generate real files!")
            
            live_result = execute_operation(
                "generate documentation",
                profile="standard",
                project_root=project_root,
                dry_run=False
            )
            
            logger.info(f"Live execution result: {live_result.status}")
            logger.info(f"Success: {live_result.success}")
            
            if live_result.data:
                files_generated = live_result.data.get("files_generated", {})
                logger.info(f"Files generated: {len(files_generated)}")
                
                # Verify files actually exist
                for file_path in list(files_generated.keys())[:10]:
                    file = Path(file_path)
                    if file.exists():
                        logger.info(f"  ✓ {file.name} (exists)")
                    else:
                        logger.error(f"  ❌ {file.name} (MISSING)")
            
            # Check generated folder again
            generated_path = project_root / "docs" / "generated"
            after_count = len(list(generated_path.glob("*.md"))) if generated_path.exists() else 0
            
            logger.info(f"\nGenerated folder after execution: {after_count} files")
            
            assert live_result.success, "Documentation generation failed"
            assert after_count > 0, "Generated folder still empty after execution"
            
        except ImportError as e:
            pytest.skip(f"Cannot import operations module: {e}")
    
    # REMOVED: test_page_generator_directly - EPM PageGenerator module deleted
    # This test imported src.epm.modules.page_generator which no longer exists


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
