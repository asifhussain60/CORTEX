"""
Tests for StreamingPlanWriter

Purpose: Validate memory-efficient plan writing with progress tracking
Coverage: File writing, progress updates, checkpoints, markdown formatting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.workflows.streaming_plan_writer import (
    StreamingPlanWriter,
    CheckpointedPlanWriter,
    WriteProgress
)


@pytest.fixture
def output_dir(tmp_path):
    """Create temporary output directory"""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def output_file(output_dir):
    """Create output file path"""
    return output_dir / "test-plan.md"


@pytest.fixture
def writer(output_file):
    """Create StreamingPlanWriter instance"""
    return StreamingPlanWriter(output_file)


class TestStreamingPlanWriter:
    """Test suite for StreamingPlanWriter"""
    
    def test_initialization(self, writer, output_file):
        """Test writer initializes correctly"""
        assert writer.output_path == output_file
        assert writer.encoding == 'utf-8'
        assert writer.buffer_size == 8192
        assert writer.is_open is False
        assert writer.is_finalized is False
        assert writer.progress.bytes_written == 0
        assert writer.progress.sections_written == 0
    
    def test_custom_encoding_and_buffer(self, output_file):
        """Test writer accepts custom encoding and buffer size"""
        writer = StreamingPlanWriter(
            output_file,
            encoding='latin-1',
            buffer_size=4096
        )
        
        assert writer.encoding == 'latin-1'
        assert writer.buffer_size == 4096
    
    def test_write_header(self, writer, output_file):
        """Test header writing with metadata"""
        metadata = {
            'Author': 'Test Author',
            'Date': '2025-11-26',
            'Version': '1.0'
        }
        
        writer.write_header('Test Plan', metadata)
        writer.finalize()
        
        content = output_file.read_text()
        
        # Verify title
        assert '# Test Plan' in content
        
        # Verify metadata
        assert '**Author:** Test Author' in content
        assert '**Date:** 2025-11-26' in content
        assert '**Version:** 1.0' in content
        
        # Verify separator
        assert '---' in content
    
    def test_write_header_without_metadata(self, writer, output_file):
        """Test header writing without metadata"""
        writer.write_header('Simple Plan')
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '# Simple Plan' in content
        assert '---' in content
    
    def test_write_section(self, writer, output_file):
        """Test section writing"""
        writer.set_total_sections(2)
        writer.write_section('Introduction', 'This is the introduction.')
        writer.write_section('Requirements', 'These are the requirements.')
        writer.finalize()
        
        content = output_file.read_text()
        
        # Verify sections
        assert '## Introduction' in content
        assert 'This is the introduction.' in content
        assert '## Requirements' in content
        assert 'These are the requirements.' in content
        
        # Verify progress
        assert writer.progress.sections_written == 2
        assert writer.progress.percentage_complete == 100.0
    
    def test_write_section_custom_heading_level(self, writer, output_file):
        """Test section writing with custom heading level"""
        writer.write_section('Subsection', 'Content here', heading_level=3)
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '### Subsection' in content
    
    def test_write_phase(self, writer, output_file):
        """Test phase writing with multiple sections"""
        sections = [
            {'name': 'Section 1', 'content': 'Content 1'},
            {'name': 'Section 2', 'content': 'Content 2'},
            {'name': 'Section 3', 'content': 'Content 3'}
        ]
        
        writer.set_total_sections(3)
        writer.write_phase('Phase 1: Foundation', sections)
        writer.finalize()
        
        content = output_file.read_text()
        
        # Verify phase heading
        assert '## Phase 1: Foundation' in content
        
        # Verify sections (level 3)
        assert '### Section 1' in content
        assert 'Content 1' in content
        assert '### Section 2' in content
        assert 'Content 2' in content
        assert '### Section 3' in content
        assert 'Content 3' in content
    
    def test_write_list_unordered(self, writer, output_file):
        """Test writing unordered list"""
        items = ['Item 1', 'Item 2', 'Item 3']
        writer.write_list(items, ordered=False)
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '- Item 1' in content
        assert '- Item 2' in content
        assert '- Item 3' in content
    
    def test_write_list_ordered(self, writer, output_file):
        """Test writing ordered list"""
        items = ['First', 'Second', 'Third']
        writer.write_list(items, ordered=True)
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '1. First' in content
        assert '2. Second' in content
        assert '3. Third' in content
    
    def test_write_table(self, writer, output_file):
        """Test table writing"""
        headers = ['Name', 'Status', 'Priority']
        rows = [
            ['Feature A', 'Complete', 'High'],
            ['Feature B', 'In Progress', 'Medium'],
            ['Feature C', 'Planned', 'Low']
        ]
        
        writer.write_table(headers, rows)
        writer.finalize()
        
        content = output_file.read_text()
        
        # Verify headers
        assert '| Name | Status | Priority |' in content
        
        # Verify separator
        assert '| --- | --- | --- |' in content
        
        # Verify rows
        assert '| Feature A | Complete | High |' in content
        assert '| Feature B | In Progress | Medium |' in content
        assert '| Feature C | Planned | Low |' in content
    
    def test_write_code_block(self, writer, output_file):
        """Test code block writing"""
        code = 'def hello():\n    print("Hello, World!")'
        writer.write_code_block(code, language='python')
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '```python' in content
        assert 'def hello():' in content
        assert 'print("Hello, World!")' in content
        assert '```' in content
    
    def test_write_code_block_no_language(self, writer, output_file):
        """Test code block without language specification"""
        code = 'Generic code block'
        writer.write_code_block(code)
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '```' in content
        assert 'Generic code block' in content
    
    def test_write_checkpoint_marker(self, writer, output_file):
        """Test checkpoint marker writing"""
        writer.write_checkpoint_marker('cp-1', 'Phase 1 complete')
        writer.finalize()
        
        content = output_file.read_text()
        
        assert '<!-- CHECKPOINT: cp-1 -->' in content
        assert '<!-- Message: Phase 1 complete -->' in content
    
    def test_progress_tracking(self, writer):
        """Test progress updates correctly"""
        writer.set_total_sections(4)
        
        assert writer.progress.total_sections == 4
        assert writer.progress.sections_written == 0
        assert writer.progress.percentage_complete == 0.0
        
        writer.write_section('Section 1', 'Content')
        assert writer.progress.sections_written == 1
        assert writer.progress.percentage_complete == 25.0
        
        writer.write_section('Section 2', 'Content')
        assert writer.progress.sections_written == 2
        assert writer.progress.percentage_complete == 50.0
        
        writer.write_section('Section 3', 'Content')
        writer.write_section('Section 4', 'Content')
        assert writer.progress.sections_written == 4
        assert writer.progress.percentage_complete == 100.0
        
        writer.finalize()
    
    def test_bytes_written_tracking(self, writer):
        """Test bytes written tracking"""
        assert writer.progress.bytes_written == 0
        
        writer.write_section('Test', 'A' * 100)
        
        # Should have written more than 100 bytes (section header + content)
        assert writer.progress.bytes_written > 100
        
        writer.finalize()
    
    def test_get_progress_summary(self, writer):
        """Test progress summary generation"""
        writer.set_total_sections(2)
        writer.write_section('Section 1', 'Content')
        
        summary = writer.get_progress_summary()
        
        assert 'Progress: 50.0%' in summary
        assert '(1/2 sections)' in summary
        assert 'Bytes written:' in summary
        assert 'Current section: Section 1' in summary
        assert 'Elapsed time:' in summary
    
    def test_context_manager(self, output_file):
        """Test writer as context manager"""
        with StreamingPlanWriter(output_file) as writer:
            writer.write_header('Test Plan')
            writer.write_section('Section 1', 'Content')
        
        # File should be closed and finalized
        content = output_file.read_text()
        assert '# Test Plan' in content
        assert '## Section 1' in content
    
    def test_flush(self, writer):
        """Test manual flush"""
        writer.write_section('Test', 'Content')
        writer.flush()
        
        # File should still be open after flush
        assert writer.is_open is True
        
        writer.finalize()
    
    def test_finalize_idempotent(self, writer):
        """Test finalize can be called multiple times safely"""
        writer.write_section('Test', 'Content')
        
        writer.finalize()
        assert writer.is_finalized is True
        
        # Second call should be no-op
        writer.finalize()
        assert writer.is_finalized is True
    
    def test_complete_document_workflow(self, writer, output_file):
        """Test writing complete planning document"""
        # Header
        writer.write_header('User Authentication Plan', {
            'Author': 'Test Author',
            'Date': '2025-11-26',
            'Version': '1.0'
        })
        
        # Phase 1
        writer.set_total_sections(9)
        writer.write_phase('Phase 1: Foundation', [
            {'name': 'Requirements', 'content': 'Detailed requirements here'},
            {'name': 'Dependencies', 'content': 'List of dependencies'},
            {'name': 'Architecture', 'content': 'Architecture design'}
        ])
        
        writer.write_checkpoint_marker('cp-1', 'Phase 1 complete')
        
        # Phase 2
        writer.write_phase('Phase 2: Implementation', [
            {'name': 'Implementation Plan', 'content': 'Step-by-step plan'},
            {'name': 'Test Strategy', 'content': 'Testing approach'},
            {'name': 'Integration Points', 'content': 'API endpoints'}
        ])
        
        writer.write_checkpoint_marker('cp-2', 'Phase 2 complete')
        
        # Phase 3
        writer.write_phase('Phase 3: Validation', [
            {'name': 'Acceptance Criteria', 'content': 'Success criteria'},
            {'name': 'Security Review', 'content': 'Security checklist'},
            {'name': 'Deployment Plan', 'content': 'Deployment steps'}
        ])
        
        writer.finalize()
        
        # Verify complete document
        content = output_file.read_text()
        
        assert '# User Authentication Plan' in content
        assert '## Phase 1: Foundation' in content
        assert '## Phase 2: Implementation' in content
        assert '## Phase 3: Validation' in content
        assert '<!-- CHECKPOINT: cp-1 -->' in content
        assert '<!-- CHECKPOINT: cp-2 -->' in content
        
        # Verify progress
        assert writer.progress.sections_written == 9
        assert writer.progress.percentage_complete == 100.0


class TestCheckpointedPlanWriter:
    """Test suite for CheckpointedPlanWriter"""
    
    def test_initialization(self, output_file):
        """Test checkpointed writer initialization"""
        writer = CheckpointedPlanWriter(output_file)
        
        assert writer.checkpoint_dir.exists()
        assert writer.checkpoint_dir.name == '.checkpoints'
        assert len(writer.checkpoints) == 0
    
    def test_custom_checkpoint_dir(self, output_file, output_dir):
        """Test writer with custom checkpoint directory"""
        checkpoint_dir = output_dir / 'custom_checkpoints'
        writer = CheckpointedPlanWriter(
            output_file,
            checkpoint_dir=checkpoint_dir
        )
        
        assert writer.checkpoint_dir == checkpoint_dir
        assert checkpoint_dir.exists()
    
    def test_save_checkpoint(self, output_file):
        """Test checkpoint saving"""
        writer = CheckpointedPlanWriter(output_file)
        
        writer.write_header('Test Plan')
        writer.write_section('Section 1', 'Content 1')
        writer.save_checkpoint('cp-1')
        
        # Verify checkpoint file exists
        checkpoint_file = writer.checkpoint_dir / 'cp-1.md'
        assert checkpoint_file.exists()
        
        # Verify checkpoint contains current content
        checkpoint_content = checkpoint_file.read_text()
        assert '# Test Plan' in checkpoint_content
        assert '## Section 1' in checkpoint_content
        
        writer.finalize()
    
    def test_restore_checkpoint(self, output_file):
        """Test checkpoint restoration"""
        writer = CheckpointedPlanWriter(output_file)
        
        # Write initial content and checkpoint
        writer.write_header('Test Plan')
        writer.write_section('Section 1', 'Content 1')
        writer.save_checkpoint('cp-1')
        
        # Write more content
        writer.write_section('Section 2', 'Content 2')
        writer.write_section('Section 3', 'Content 3')
        writer.finalize()
        
        # Restore to checkpoint
        result = writer.restore_checkpoint('cp-1')
        assert result is True
        
        # Verify content restored
        content = output_file.read_text()
        assert '## Section 1' in content
        assert '## Section 2' not in content
        assert '## Section 3' not in content
        
        writer.finalize()
    
    def test_restore_nonexistent_checkpoint(self, output_file):
        """Test restoring checkpoint that doesn't exist"""
        writer = CheckpointedPlanWriter(output_file)
        
        result = writer.restore_checkpoint('cp-999')
        
        assert result is False
    
    def test_list_checkpoints(self, output_file):
        """Test listing saved checkpoints"""
        writer = CheckpointedPlanWriter(output_file)
        
        assert writer.list_checkpoints() == []
        
        writer.write_section('Test', 'Content')
        writer.save_checkpoint('cp-1')
        writer.save_checkpoint('cp-2')
        
        checkpoints = writer.list_checkpoints()
        assert len(checkpoints) == 2
        assert 'cp-1' in checkpoints
        assert 'cp-2' in checkpoints
        
        writer.finalize()
    
    def test_cleanup_checkpoints(self, output_file):
        """Test checkpoint cleanup"""
        writer = CheckpointedPlanWriter(output_file)
        
        writer.write_section('Test', 'Content')
        writer.save_checkpoint('cp-1')
        writer.save_checkpoint('cp-2')
        
        # Verify checkpoints exist
        assert len(writer.list_checkpoints()) == 2
        
        # Cleanup
        writer.cleanup_checkpoints()
        
        # Verify checkpoints removed
        assert len(writer.list_checkpoints()) == 0
        assert not (writer.checkpoint_dir / 'cp-1.md').exists()
        assert not (writer.checkpoint_dir / 'cp-2.md').exists()
        
        writer.finalize()
    
    def test_workflow_with_checkpoint_resume(self, output_file):
        """Test complete workflow with checkpoint and resume"""
        writer = CheckpointedPlanWriter(output_file)
        
        # Write Phase 1
        writer.write_header('Feature Plan')
        writer.write_section('Requirements', 'Requirements content')
        writer.write_section('Dependencies', 'Dependencies content')
        writer.save_checkpoint('phase-1-complete')
        
        # Write Phase 2
        writer.write_section('Implementation', 'Implementation content')
        writer.save_checkpoint('phase-2-complete')
        
        # Simulate error - restore to Phase 1
        writer.restore_checkpoint('phase-1-complete')
        
        # Re-write Phase 2 (different content)
        writer.write_section('Implementation', 'Revised implementation content')
        
        writer.finalize()
        
        # Verify final content
        content = output_file.read_text()
        assert 'Requirements content' in content
        assert 'Dependencies content' in content
        assert 'Revised implementation content' in content


class TestWriteProgress:
    """Test suite for WriteProgress dataclass"""
    
    def test_initialization(self):
        """Test WriteProgress initialization"""
        progress = WriteProgress(
            bytes_written=1000,
            sections_written=2,
            total_sections=5,
            percentage_complete=40.0,
            current_section='Section 2',
            start_time=datetime.now()
        )
        
        assert progress.bytes_written == 1000
        assert progress.sections_written == 2
        assert progress.total_sections == 5
        assert progress.percentage_complete == 40.0
        assert progress.current_section == 'Section 2'
    
    def test_get_elapsed_time(self):
        """Test elapsed time calculation"""
        import time
        
        progress = WriteProgress(
            bytes_written=0,
            sections_written=0,
            total_sections=1,
            percentage_complete=0.0,
            current_section='',
            start_time=datetime.now()
        )
        
        time.sleep(0.1)
        elapsed = progress.get_elapsed_time()
        
        assert elapsed >= 0.1
    
    def test_get_eta_seconds(self):
        """Test ETA calculation"""
        progress = WriteProgress(
            bytes_written=500,
            sections_written=1,
            total_sections=2,
            percentage_complete=50.0,
            current_section='Section 1',
            start_time=datetime.now()
        )
        
        eta = progress.get_eta_seconds()
        
        # ETA should be close to elapsed time (50% complete)
        assert eta is not None
        assert eta >= 0
    
    def test_get_eta_at_start(self):
        """Test ETA returns None at 0% progress"""
        progress = WriteProgress(
            bytes_written=0,
            sections_written=0,
            total_sections=5,
            percentage_complete=0.0,
            current_section='',
            start_time=datetime.now()
        )
        
        eta = progress.get_eta_seconds()
        
        assert eta is None
