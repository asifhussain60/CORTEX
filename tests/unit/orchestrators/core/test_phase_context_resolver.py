"""
Tests for PhaseContextResolver - Multi-Session Continuity System

Tests cover:
1. Phase extraction from chat sessions
2. Last completed phase detection
3. Queued phase discovery
4. Phase numbering system detection
5. Phase reference resolution
6. Continuation context building
"""

import pytest
from pathlib import Path
import tempfile
import yaml
from cortex.orchestrators.core.phase_context_resolver import (
    PhaseContextResolver,
    PhaseContext,
    extract_session_context,
    resolve_phase,
)


class TestPhaseContextExtraction:
    """Test extraction of phase context from chat sessions."""
    
    def test_extract_phases_numeric_numbering(self):
        """Test extraction of numeric phases (0-6)."""
        chat_content = """
## 🚀 Phase Preview: Phase 1 (JSON Adapter)
...
## 🚀 Phase Preview: Phase 2 (JSON Data Generator)
...
## 🚀 Phase Preview: Phase 3 (Repository Onboarding)
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            
            assert len(phases) >= 3
            assert any("1" in p["id"] for p in phases)
            assert any("2" in p["id"] for p in phases)
            assert any("3" in p["id"] for p in phases)
    
    def test_extract_phases_letter_numbering(self):
        """Test extraction of letter-based phases (A, B, C)."""
        chat_content = """
Phase A: Foundation
Phase B: Planning
Phase C: Cleanup
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            
            assert any("A" in p["id"] for p in phases)
            assert any("B" in p["id"] for p in phases)
            assert any("C" in p["id"] for p in phases)
    
    def test_detect_numbering_system_numeric(self):
        """Test detection of numeric numbering system."""
        phases = [
            {"id": "phase-0", "title": "Foundation"},
            {"id": "phase-1", "title": "Planning"},
            {"id": "phase-2", "title": "Execution"},
        ]
        
        resolver = PhaseContextResolver("/fake/path")
        numbering = resolver._detect_numbering_system(phases)
        assert numbering == "numeric"
    
    def test_detect_numbering_system_letter(self):
        """Test detection of letter-based numbering system."""
        phases = [
            {"id": "phase-A", "title": "Foundation"},
            {"id": "phase-B", "title": "Planning"},
            {"id": "phase-C", "title": "Cleanup"},
        ]
        
        resolver = PhaseContextResolver("/fake/path")
        numbering = resolver._detect_numbering_system(phases)
        assert numbering == "letter"
    
    def test_detect_numbering_system_mixed(self):
        """Test detection of mixed numbering system."""
        phases = [
            {"id": "phase-0", "title": "Foundation"},
            {"id": "phase-1A", "title": "Planning"},
            {"id": "phase-2B", "title": "Execution"},
        ]
        
        resolver = PhaseContextResolver("/fake/path")
        numbering = resolver._detect_numbering_system(phases)
        assert numbering == "mixed"


class TestLastCompletedPhaseDetection:
    """Test detection of last completed phase."""
    
    def test_find_last_completed_green_marker(self):
        """Test detection using ✅ GREEN marker."""
        chat_content = """
## Phase 1 Summary
✅ Phase 1 GREEN: All 14 tests passing

## Phase 2 Summary
✅ Phase 2 GREEN: All 18 tests passing

## Phase 3 Summary
📋 Phase 3 QUEUED
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            last_completed = resolver._find_last_completed_phase(chat_content, phases)
            
            assert last_completed is not None
            assert "2" in last_completed["id"]
    
    def test_find_last_completed_all_tests_passing(self):
        """Test detection using 'all X tests passing' marker."""
        chat_content = """
Phase 4: MCP Tool Schema
All 12 tests passing, GREEN ✅

Phase 5: SPA Dashboard
Status: In Progress
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            last_completed = resolver._find_last_completed_phase(chat_content, phases)
            
            assert last_completed is not None
            assert "4" in last_completed["id"]
    
    def test_find_last_completed_no_completion_found(self):
        """Test when no completed phases are found."""
        chat_content = """
Phase 1: Foundation
Status: In Progress

Phase 2: Planning
Status: Queued
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            last_completed = resolver._find_last_completed_phase(chat_content, phases)
            
            assert last_completed is None


class TestQueuedPhasesDiscovery:
    """Test discovery of queued phases."""
    
    def test_find_queued_phases_from_table(self):
        """Test extraction from phase table."""
        chat_content = """
## Remaining Phases (In Queue)

| Phase | Title | Status | Tests |
|-------|-------|--------|-------|
| **Phase 5** | SPA Refactor | QUEUED | 15+ |
| **Phase 6** | E2E Tests | QUEUED | 20+ |
| **Phase 7** | Prompt Updates | QUEUED | 5+ |
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            queued = resolver._find_queued_phases(chat_content, phases)
            
            assert "phase-5" in queued
            assert "phase-6" in queued
            assert "phase-7" in queued
    
    def test_find_queued_phases_from_list(self):
        """Test extraction from bulleted list."""
        chat_content = """
## Next Phases

- **Phase 3**: Code-Level Planning
- **Phase 4**: Coherence Validation
- **Phase 5**: Review Orchestrator
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            phases = resolver._extract_phases_from_chat(chat_content)
            queued = resolver._find_queued_phases(chat_content, phases)
            
            assert len(queued) >= 3


class TestPhaseReferenceResolution:
    """Test resolution of user phase references."""
    
    def test_resolve_explicit_numeric_reference(self):
        """Test resolution of 'phase 7' → phase-7."""
        resolver = PhaseContextResolver("/fake/path")
        context = PhaseContext(
            session_file="/fake/path",
            all_phases_map={
                "phase-7": {"title": "Prompt & Agent Updates"},
            }
        )
        
        phase_id, title, confidence = resolver.resolve_phase_reference("phase 7", context)
        
        assert phase_id == "phase-7"
        assert "Prompt" in title
        assert confidence > 0.9
    
    def test_resolve_explicit_letter_reference(self):
        """Test resolution of 'phase C' → phase-C."""
        resolver = PhaseContextResolver("/fake/path")
        context = PhaseContext(
            session_file="/fake/path",
            all_phases_map={
                "phase-C": {"title": "Cleanup & Finalization"},
            }
        )
        
        phase_id, title, confidence = resolver.resolve_phase_reference("phase C", context)
        
        assert "C" in phase_id
        assert "Cleanup" in title
    
    def test_resolve_next_phase_with_queue(self):
        """Test resolution of 'next phase' with queued phases."""
        resolver = PhaseContextResolver("/fake/path")
        context = PhaseContext(
            session_file="/fake/path",
            queued_phases=["phase-5", "phase-6", "phase-7"],
            all_phases_map={
                "phase-5": {"title": "SPA Refactor"},
                "phase-6": {"title": "E2E Tests"},
            }
        )
        
        phase_id, title, confidence = resolver.resolve_phase_reference("continue", context)
        
        assert phase_id == "phase-5"
        assert "SPA" in title
        assert confidence > 0.95
    
    def test_resolve_next_phase_no_queue_raises_error(self):
        """Test that 'next phase' without queue raises error."""
        resolver = PhaseContextResolver("/fake/path")
        context = PhaseContext(
            session_file="/fake/path",
            queued_phases=[],
            last_completed_phase="phase-6",
        )
        
        with pytest.raises(ValueError):
            resolver.resolve_phase_reference("next", context)
    
    def test_resolve_ambiguous_reference_raises_error(self):
        """Test that unresolvable reference raises error."""
        resolver = PhaseContextResolver("/fake/path")
        context = PhaseContext(
            session_file="/fake/path",
            all_phases_map={},
            queued_phases=[],
        )
        
        with pytest.raises(ValueError):
            resolver.resolve_phase_reference("phase 999", context)


class TestContinuationContext:
    """Test building continuation context for multi-session support."""
    
    def test_build_continuation_context(self):
        """Test building comprehensive context."""
        chat_content = """
## Phase 1 Summary
✅ Phase 1 GREEN

## Phase 2 Summary  
✅ Phase 2 GREEN

## Remaining Phases
| **Phase 3** | QUEUED |
| **Phase 4** | QUEUED |
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            context_dict = resolver.build_continuation_context()
            
            assert "last_completed" in context_dict
            assert "queued" in context_dict
            assert "next_recommended" in context_dict
            assert context_dict["numbering_system"] in ["numeric", "letter", "mixed", "unknown"]
    
    def test_continuation_context_json_serializable(self):
        """Test that context is JSON-serializable for MCP exposure."""
        import json
        
        chat_content = "## Phase 1\n✅ Phase 1 GREEN\n\n## Phase 2\n📋 QUEUED"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            resolver = PhaseContextResolver(f.name)
            context_dict = resolver.build_continuation_context()
            
            # Should not raise
            json_str = json.dumps(context_dict, default=str)
            assert json_str is not None


class TestPhaseContextDataclass:
    """Test PhaseContext dataclass functionality."""
    
    def test_phase_context_to_dict(self):
        """Test export to dictionary."""
        context = PhaseContext(
            session_file="/path/to/chat01.md",
            last_completed_phase="phase-5",
            last_completed_title="SPA Refactor",
        )
        
        as_dict = context.to_dict()
        
        assert as_dict["session_file"] == "/path/to/chat01.md"
        assert as_dict["last_completed_phase"] == "phase-5"
    
    def test_phase_context_from_dict(self):
        """Test import from dictionary."""
        data = {
            "session_file": "/path/to/chat01.md",
            "last_completed_phase": "phase-5",
            "last_completed_title": "SPA Refactor",
            "queued_phases": ["phase-6", "phase-7"],
            "all_phases_map": {},
            "phase_numbering": "numeric",
            "extracted_at": "2026-02-04T12:00:00",
            "confidence": 0.95,
        }
        
        context = PhaseContext.from_dict(data)
        
        assert context.session_file == "/path/to/chat01.md"
        assert context.last_completed_phase == "phase-5"


class TestMCPExposure:
    """Test MCP tool functions."""
    
    def test_extract_session_context_function(self):
        """Test convenience function for MCP."""
        chat_content = "## Phase 1\n✅ Phase 1 GREEN"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            result = extract_session_context(f.name)
            
            assert "last_completed" in result
            assert "queued" in result
    
    def test_resolve_phase_function(self):
        """Test convenience function for phase resolution."""
        chat_content = """
## Phase 5
✅ GREEN

## Queue
| Phase 6 | QUEUED |
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(chat_content)
            f.flush()
            
            phase_id, title = resolve_phase("next", f.name)
            
            assert "6" in phase_id
