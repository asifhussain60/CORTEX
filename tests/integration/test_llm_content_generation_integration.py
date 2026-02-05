"""
Integration Tests for LLM Content Generator
Tests real-world usage with actual phase YAML files

Author: Asif Hussain
"""

import pytest
import yaml
from pathlib import Path
from cortex.visualization.llm_content_generator import (
    LLMContentGenerator,
    TechnicalDecision,
    StoryContext,
    DiagramSpec,
    GeneratedContent
)


class TestRealPhaseContentGeneration:
    """Test with actual phase YAML files"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        return LLMContentGenerator(enable_cache=True)
    
    @pytest.fixture
    def phase_01_yaml(self):
        """Load Phase 01 YAML"""
        phase_file = Path("cortex-registry/_cortex-master/phases/completed/2026/phase-01-orchestrator-event-bus.yaml")
        if phase_file.exists():
            with open(phase_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            "phase_id": "01",
            "title": "Orchestrator Event Bus",
            "objectives": ["Enable event-driven communication"],
            "key_features": [
                {"name": "AsyncIO Event Bus"},
                {"name": "Message Routing"}
            ]
        }
    
    def test_generate_phase_01_overview(self, generator, phase_01_yaml):
        """Should generate overview for Phase 01"""
        overview = generator.generate_overview(phase_01_yaml)
        
        assert isinstance(overview, str)
        assert len(overview) >= 100
        # Accept both "Phase 01", "Phase 1", or "Phase PHASE-01" format
        phase_mentioned = any(x in overview for x in ["Phase 01", "Phase 1", "Phase PHASE-01", "PHASE-01"])
        assert phase_mentioned, f"Phase not mentioned in overview: {overview[:100]}"
        assert "Event Bus" in overview or "event" in overview.lower()
        print(f"\n✅ Generated Overview ({len(overview)} chars):\n{overview}\n")
    
    def test_generate_technical_narrative_phase_01(self, generator, phase_01_yaml):
        """Should generate technical narrative for Phase 01"""
        narrative = generator.generate_technical_narrative(phase_01_yaml)
        
        assert isinstance(narrative, str)
        assert len(narrative) > 0
        print(f"\n✅ Generated Technical Narrative:\n{narrative}\n")
    
    def test_extract_decisions_from_phase_01(self, generator, phase_01_yaml):
        """Should extract technical decisions"""
        decisions = generator.extract_decisions(phase_yaml=phase_01_yaml)
        
        assert isinstance(decisions, list)
        # May be empty if no decisions in YAML
        print(f"\n✅ Extracted {len(decisions)} decisions")
        for dec in decisions[:3]:  # Show first 3
            print(f"  - {dec.decision}: {dec.rationale}")
    
    def test_create_story_context_for_phase_07(self, generator):
        """Should create story context linking phases"""
        all_phases = [
            {"phase_id": "06", "title": "Phase 06"},
            {"phase_id": "07", "title": "Phase 07"},
            {"phase_id": "08", "title": "Phase 08"}
        ]
        current_phase = all_phases[1]
        
        story_context = generator.create_story_links(current_phase, all_phases)
        
        assert story_context.previous_phase is not None
        assert story_context.previous_phase["phase_id"] == "06"
        assert story_context.next_phase is not None
        assert story_context.next_phase["phase_id"] == "08"
        assert story_context.transition_narrative is not None
        
        print(f"\n✅ Story Context:")
        print(f"  Previous: Phase {story_context.previous_phase['phase_id']}")
        print(f"  Next: Phase {story_context.next_phase['phase_id']}")
        print(f"  Transition: {story_context.transition_narrative}")
    
    def test_generate_diagram_specs(self, generator, phase_01_yaml):
        """Should generate diagram specifications"""
        # Add architecture to test data
        phase_01_yaml["architecture"] = {
            "components": ["EventBus", "MessageRouter", "Handler"],
            "relationships": [
                {"from": "EventBus", "to": "MessageRouter"},
                {"from": "MessageRouter", "to": "Handler"}
            ]
        }
        
        diagram_specs = generator.generate_diagram_specs(phase_01_yaml)
        
        assert len(diagram_specs) > 0
        arch_spec = diagram_specs[0]
        assert arch_spec.type == "architecture"
        assert "EventBus" in arch_spec.components
        
        print(f"\n✅ Generated {len(diagram_specs)} diagram specs")
        for spec in diagram_specs:
            print(f"  - {spec.type}: {spec.title}")
    
    def test_content_caching_performance(self, generator, phase_01_yaml):
        """Should cache content for performance"""
        # First call - generates content
        start_cache_hits = generator.cache_hits
        overview1 = generator.generate_overview(phase_01_yaml)
        
        # Second call - should use cache
        overview2 = generator.generate_overview(phase_01_yaml)
        
        assert overview1 == overview2
        assert generator.cache_hits == start_cache_hits + 1
        
        print(f"\n✅ Cache Hit: {generator.cache_hits} hits")
    
    def test_generate_comprehensive_content(self, generator, phase_01_yaml):
        """Should generate all content types for a phase"""
        # Overview
        overview = generator.generate_overview(phase_01_yaml)
        
        # Technical narrative
        narrative = generator.generate_technical_narrative(phase_01_yaml)
        
        # Decisions
        decisions = generator.extract_decisions(phase_yaml=phase_01_yaml)
        
        # Story context
        all_phases = [
            {"phase_id": "01", "title": "Event Bus"},
            {"phase_id": "02", "title": "Phase 02"}
        ]
        story_context = generator.create_story_links(phase_01_yaml, all_phases)
        
        # Diagram specs
        phase_01_yaml["architecture"] = {
            "components": ["EventBus"],
            "relationships": []
        }
        diagram_specs = generator.generate_diagram_specs(phase_01_yaml)
        
        # Verify all content generated
        assert overview is not None
        assert narrative is not None
        assert isinstance(decisions, list)
        assert story_context is not None
        assert isinstance(diagram_specs, list)
        
        print(f"\n✅ Comprehensive Content Generated:")
        print(f"  Overview: {len(overview)} chars")
        print(f"  Narrative: {len(narrative)} chars")
        print(f"  Decisions: {len(decisions)} items")
        print(f"  Story Context: Previous={story_context.previous_phase is not None}")
        print(f"  Diagrams: {len(diagram_specs)} specs")


class TestMultiPhaseStoryGeneration:
    """Test generating content for multiple phases"""
    
    def test_generate_story_for_phases_1_to_5(self):
        """Should generate consistent story across phases 1-5"""
        generator = LLMContentGenerator()
        
        phases = [
            {"phase_id": "01", "title": "Event Bus"},
            {"phase_id": "02", "title": "Testing Framework"},
            {"phase_id": "03", "title": "Configuration System"},
            {"phase_id": "04", "title": "Documentation Engine"},
            {"phase_id": "05", "title": "Deployment Pipeline"}
        ]
        
        overviews = []
        for i, phase in enumerate(phases):
            # Add context from previous phases
            context = {"previous_phases": phases[:i]} if i > 0 else None
            overview = generator.generate_overview(phase, context=context)
            overviews.append(overview)
            
            print(f"\n✅ Phase {phase['phase_id']} Overview:")
            print(f"  {overview[:150]}...")
        
        # Verify continuity
        assert len(overviews) == 5
        assert all(len(o) >= 100 for o in overviews)


class TestErrorHandlingIntegration:
    """Test error handling with real scenarios"""
    
    def test_handle_missing_phase_file(self):
        """Should handle missing phase file gracefully"""
        generator = LLMContentGenerator()
        
        # Non-existent phase
        fake_phase = {"phase_id": "99", "title": "Non-existent Phase"}
        
        # Should still generate content
        overview = generator.generate_overview(fake_phase)
        assert overview is not None
        assert len(overview) > 0
        
        print(f"\n✅ Fallback content generated for missing phase")
    
    def test_handle_malformed_yaml(self):
        """Should handle malformed YAML gracefully"""
        generator = LLMContentGenerator()
        
        malformed = {"invalid": "structure", "no": "phase_id"}
        
        # Should fall back to template
        overview = generator.generate_overview(malformed)
        assert overview is not None
        
        print(f"\n✅ Handled malformed YAML gracefully")


# Run tests with output
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
