"""
Demonstration: LLM Content Generator for Phase Detail Pages

This script demonstrates how to use the LLM Content Generator to create
comprehensive content for phase detail pages.

Usage:
    python3 examples/demo_llm_content_generation.py

Author: Asif Hussain
"""

import yaml
from pathlib import Path
from cortex.visualization.llm_content_generator import (
    LLMContentGenerator,
    GeneratedContent
)


def demo_basic_content_generation():
    """Demonstrate basic content generation"""
    print("=" * 80)
    print("DEMO: Basic Content Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator(enable_cache=True)
    
    # Sample phase data
    phase = {
        "phase_id": "01",
        "title": "Event Bus Infrastructure",
        "objectives": [
            "Enable event-driven communication between orchestrators",
            "Remove tight coupling via pub-sub patterns"
        ],
        "key_features": [
            {"name": "AsyncIO Event Bus"},
            {"name": "Message Routing"},
            {"name": "Event History"}
        ]
    }
    
    # Generate overview
    overview = generator.generate_overview(phase)
    print(f"\n📝 OVERVIEW ({len(overview)} characters):")
    print("-" * 80)
    print(overview)
    print()


def demo_story_context_generation():
    """Demonstrate story context with phase linking"""
    print("=" * 80)
    print("DEMO: Story Context Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator()
    
    # Define phases
    all_phases = [
        {"phase_id": "06", "title": "Testing Framework"},
        {"phase_id": "07", "title": "Configuration System"},
        {"phase_id": "08", "title": "Deployment Pipeline"}
    ]
    
    current_phase = all_phases[1]  # Phase 07
    
    # Generate story context
    story_context = generator.create_story_links(current_phase, all_phases)
    
    print(f"\n🔗 STORY CONTEXT for Phase {current_phase['phase_id']}:")
    print("-" * 80)
    if story_context.previous_phase:
        print(f"Previous Phase: {story_context.previous_phase['phase_id']} - {story_context.previous_phase['title']}")
    print(f"Current Phase:  {current_phase['phase_id']} - {current_phase['title']}")
    if story_context.next_phase:
        print(f"Next Phase:     {story_context.next_phase['phase_id']} - {story_context.next_phase['title']}")
    print(f"\n📖 Transition Narrative:")
    if story_context.transition_narrative:
        print(story_context.transition_narrative)
    else:
        print("(No transition narrative available)")
    print()


def demo_technical_narrative():
    """Demonstrate technical narrative generation"""
    print("=" * 80)
    print("DEMO: Technical Narrative Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator()
    
    phase = {
        "phase_id": "01",
        "title": "Event Bus",
        "implementation": {
            "components": ["EventBus", "MessageRouter", "EventHandler"],
            "patterns": ["Publisher-Subscriber", "Event Sourcing"]
        },
        "technical_decisions": [
            {
                "decision": "Use AsyncIO for event handling",
                "rationale": "Non-blocking I/O improves throughput"
            },
            {
                "decision": "Implement event replay capability",
                "rationale": "Enables debugging and audit trails"
            }
        ]
    }
    
    narrative = generator.generate_technical_narrative(phase)
    
    print(f"\n🔧 TECHNICAL NARRATIVE:")
    print("-" * 80)
    print(narrative)
    print()


def demo_diagram_specs():
    """Demonstrate diagram specification generation"""
    print("=" * 80)
    print("DEMO: Diagram Specification Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator()
    
    phase = {
        "phase_id": "01",
        "title": "Event Bus",
        "architecture": {
            "components": ["EventBus", "MessageRouter", "EventHandler", "DeadLetterQueue"],
            "relationships": [
                {"from": "EventBus", "to": "MessageRouter"},
                {"from": "MessageRouter", "to": "EventHandler"},
                {"from": "EventHandler", "to": "DeadLetterQueue"}
            ]
        },
        "workflow": {
            "steps": [
                "Receive event from publisher",
                "Route event to appropriate handler",
                "Execute handler logic",
                "Emit result event",
                "Store in event history"
            ]
        },
        "data_flow": {
            "inputs": ["UserRequest", "SystemEvent"],
            "transformations": ["Validate", "Route", "Process"],
            "outputs": ["Response", "EventLog"]
        }
    }
    
    diagram_specs = generator.generate_diagram_specs(phase)
    
    print(f"\n📊 DIAGRAM SPECIFICATIONS ({len(diagram_specs)} total):")
    print("-" * 80)
    
    for spec in diagram_specs:
        print(f"\n{spec.type.upper()} DIAGRAM: {spec.title}")
        if spec.components:
            print(f"  Components: {', '.join(spec.components)}")
        if spec.steps:
            print(f"  Steps: {len(spec.steps)} workflow steps")
        if spec.relationships:
            print(f"  Relationships: {len(spec.relationships)} connections")
    print()


def demo_content_caching():
    """Demonstrate content caching for performance"""
    print("=" * 80)
    print("DEMO: Content Caching Performance")
    print("=" * 80)
    
    import time
    
    generator = LLMContentGenerator(enable_cache=True)
    
    phase = {
        "phase_id": "01",
        "title": "Event Bus",
        "objectives": ["Enable event-driven communication"]
    }
    
    # First generation (uncached)
    start = time.time()
    overview1 = generator.generate_overview(phase)
    time1 = (time.time() - start) * 1000
    
    # Second generation (cached)
    start = time.time()
    overview2 = generator.generate_overview(phase)
    time2 = (time.time() - start) * 1000
    
    print(f"\n⚡ PERFORMANCE COMPARISON:")
    print("-" * 80)
    print(f"First call (no cache):  {time1:.2f}ms")
    print(f"Second call (cached):   {time2:.2f}ms")
    print(f"Speed improvement:      {time1/time2:.1f}x faster")
    print(f"Cache hits:             {generator.cache_hits}")
    print(f"Content identical:      {overview1 == overview2}")
    print()


def demo_multi_phase_story():
    """Demonstrate generating consistent story across multiple phases"""
    print("=" * 80)
    print("DEMO: Multi-Phase Story Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator()
    
    phases = [
        {"phase_id": "01", "title": "Event Bus Infrastructure"},
        {"phase_id": "02", "title": "Testing Framework"},
        {"phase_id": "03", "title": "Configuration System"},
        {"phase_id": "04", "title": "Documentation Engine"}
    ]
    
    print(f"\n📚 GENERATING STORY FOR {len(phases)} PHASES:")
    print("-" * 80)
    
    for i, phase in enumerate(phases):
        context = {"previous_phases": phases[:i]} if i > 0 else None
        overview = generator.generate_overview(phase, context=context)
        
        print(f"\n▶ Phase {phase['phase_id']}: {phase['title']}")
        print(f"  {overview[:200]}...")
        
        # Show connection to previous phase
        if context and context["previous_phases"]:
            prev = context["previous_phases"][-1]
            if f"Phase {prev['phase_id']}" in overview or prev['title'] in overview:
                print(f"  ✓ Links to previous phase: {prev['title']}")
    print()


def demo_real_phase_content():
    """Demonstrate with real phase file if available"""
    print("=" * 80)
    print("DEMO: Real Phase Content Generation")
    print("=" * 80)
    
    generator = LLMContentGenerator()
    
    # Try to load Phase 01 from registry
    phase_file = Path("cortex-registry/_cortex-master/phases/completed/2026/phase-01-orchestrator-event-bus.yaml")
    
    if phase_file.exists():
        print(f"\n✓ Loading real phase file: {phase_file.name}")
        with open(phase_file, 'r') as f:
            phase_data = yaml.safe_load(f)
        
        # Generate comprehensive content
        overview = generator.generate_overview(phase_data)
        narrative = generator.generate_technical_narrative(phase_data)
        
        print(f"\n📝 OVERVIEW:")
        print("-" * 80)
        print(overview)
        
        print(f"\n🔧 TECHNICAL NARRATIVE:")
        print("-" * 80)
        print(narrative)
        
        print(f"\n✓ Content generated from real phase data")
    else:
        print(f"\n⚠ Phase file not found: {phase_file}")
        print("  Using sample data instead...")
        
        phase_data = {
            "phase_id": "01",
            "title": "Event Bus Infrastructure",
            "objectives": ["Enable event-driven communication"]
        }
        overview = generator.generate_overview(phase_data)
        print(f"\n📝 OVERVIEW:\n{overview}")
    
    print()


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LLM CONTENT GENERATOR DEMO" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    demos = [
        ("Basic Content Generation", demo_basic_content_generation),
        ("Story Context Generation", demo_story_context_generation),
        ("Technical Narrative", demo_technical_narrative),
        ("Diagram Specifications", demo_diagram_specs),
        ("Content Caching", demo_content_caching),
        ("Multi-Phase Story", demo_multi_phase_story),
        ("Real Phase Content", demo_real_phase_content)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")
            print("\n")
    
    print("=" * 80)
    print("✅ ALL DEMOS COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
