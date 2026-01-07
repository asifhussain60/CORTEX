#!/usr/bin/env python3
"""
📊 CORTEX Intelligent Diagram Enhancer
========================================

Adds purpose-driven D3.js and Mermaid diagrams to high-priority Level 2 pages
based on content analysis and learning objectives.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DiagramSpec:
    """Specification for a diagram to add."""
    page_file: str
    diagram_type: str  # mermaid-flowchart, mermaid-sequence, mermaid-mindmap, d3-force, d3-tree
    placement: str  # hero, section-start, section-end, sidebar
    title: str
    content: str
    priority: int  # 1-5, 1=highest


class IntelligentDiagramEnhancer:
    """Enhances pages with intelligent diagram placement."""
    
    def __init__(self, docs_dir: Path = Path("docs")):
        self.docs_dir = Path(docs_dir)
        self.specs: List[DiagramSpec] = []
        
    def generate_diagram_specs(self) -> List[DiagramSpec]:
        """Generate diagram specifications for high-priority pages."""
        specs = []
        
        # 1. Architecture - Four-Tier Brain
        specs.append(DiagramSpec(
            page_file="architecture/four-tier-brain.html",
            diagram_type="mermaid-flowchart",
            placement="hero",
            title="CORTEX 4-Tier Brain Architecture",
            priority=1,
            content="""
graph TD
    T0[Tier 0: Governance<br/>SKULL Rules, Constraints]
    T1[Tier 1: Working Memory<br/>Active Plans, Conversation State]
    T2[Tier 2: Knowledge Graph<br/>Lessons, Relationships, Patterns]
    T3[Tier 3: Dev Context<br/>Project Files, Git, Dependencies]
    
    T0 -->|Guards| T1
    T1 -->|Queries| T2
    T2 -->|Enriches| T3
    T3 -->|Feeds| T1
    
    MO[Master Orchestrator<br/>Intent Router]
    
    MO -->|Enforces| T0
    MO -->|Reads/Writes| T1
    MO -->|Learns| T2
    MO -->|Executes| T3
    
    style T0 fill:#ff6b6b,stroke:#fff,stroke-width:2px,color:#fff
    style T1 fill:#ffd700,stroke:#fff,stroke-width:2px,color:#000
    style T2 fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
    style T3 fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style MO fill:#7c7cff,stroke:#fff,stroke-width:3px,color:#fff
"""
        ))
        
        # 2. Architecture - Agent System
        specs.append(DiagramSpec(
            page_file="architecture/agent-system.html",
            diagram_type="mermaid-flowchart",
            placement="section-start",
            title="CORTEX Agent Collaboration Model",
            priority=1,
            content="""
graph LR
    User[User Request] --> MO[Master Orchestrator]
    
    MO --> Agent1[Planning Agent<br/>Strategic Design]
    MO --> Agent2[Execution Agent<br/>Code Implementation]
    
    Agent1 -->|Plan| StateDB[(Planning State DB)]
    Agent2 -->|Query Plan| StateDB
    
    Agent1 --> T1[(Tier 1<br/>Working Memory)]
    Agent2 --> T1
    
    Agent2 -->|Results| User
    
    style User fill:#7c7cff,stroke:#fff,stroke-width:2px,color:#fff
    style MO fill:#00d4ff,stroke:#fff,stroke-width:3px,color:#000
    style Agent1 fill:#ffd700,stroke:#fff,stroke-width:2px,color:#000
    style Agent2 fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style StateDB fill:#ff6b6b,stroke:#fff,stroke-width:2px,color:#fff
    style T1 fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
"""
        ))
        
        # 3. Architecture - Working Memory
        specs.append(DiagramSpec(
            page_file="architecture/working-memory.html",
            diagram_type="mermaid-mindmap",
            placement="hero",
            title="Tier 1 Working Memory Structure",
            priority=1,
            content="""
mindmap
  root((Tier 1<br/>Working Memory))
    Active Plans
      Current Phase
      Progress Tracking
      Acceptance Criteria
      Git Checkpoints
    Conversation Context
      Last 3 Sessions
      User Preferences
      Intent History
    State Coordination
      Planning State DB
      Orchestrator Status
      Agent Handoffs
    Performance Cache
      Token Usage
      Execution Metrics
      Hot Paths
"""
        ))
        
        # 4. Features - Orchestrators Overview
        specs.append(DiagramSpec(
            page_file="features/orchestrators.html",
            diagram_type="mermaid-flowchart",
            placement="hero",
            title="Orchestrator Ecosystem",
            priority=1,
            content="""
graph TD
    User[User Intent] --> Router[Master Orchestrator<br/>Intent Router]
    
    Router -->|Pattern Match| Planning[🛡️ Planning v5<br/>Autonomous]
    Router -->|Pattern Match| ADO[🛡️ ADO v2<br/>Wizard/Auto]
    Router -->|Pattern Match| Vacuum[🛡️ Vacuum v2<br/>Cleanup]
    Router -->|Pattern Match| TDD[📋 TDD<br/>Guided]
    Router -->|Pattern Match| Debug[📋 Debug<br/>Guided]
    Router -->|Pattern Match| Refine[📋 Refinement<br/>Guided]
    
    Planning --> StateDB[(Planning State DB)]
    ADO --> ADOInt[Interactive Wizard]
    TDD --> RED[RED→GREEN→REFACTOR]
    
    Planning -->|Creates| Artifacts[Plan Documents]
    TDD -->|Validates| Tests[Test Results]
    Refine -->|Improves| Code[Enhanced Code]
    
    style Router fill:#7c7cff,stroke:#fff,stroke-width:3px,color:#fff
    style Planning fill:#ffd700,stroke:#fff,stroke-width:2px,color:#000
    style ADO fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
    style Vacuum fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style TDD fill:#ff6b6b,stroke:#fff,stroke-width:2px,color:#fff
    style Debug fill:#ff9f40,stroke:#fff,stroke-width:2px,color:#000
    style Refine fill:#00bfff,stroke:#fff,stroke-width:2px,color:#000
"""
        ))
        
        # 5. Features - TDD Mastery
        specs.append(DiagramSpec(
            page_file="features/tdd-mastery.html",
            diagram_type="mermaid-flowchart",
            placement="section-start",
            title="TDD Orchestrator Workflow",
            priority=2,
            content="""
graph TD
    Start[Start TDD Session] --> RED[🔴 RED Phase<br/>Write Failing Test]
    RED --> Validate{Test Fails?}
    
    Validate -->|No| Error[❌ Error: Test Must Fail First<br/>SKULL: TDD_ENFORCEMENT]
    Validate -->|Yes| GREEN[🟢 GREEN Phase<br/>Minimal Implementation]
    
    GREEN --> Pass{Test Passes?}
    Pass -->|No| Fix[Fix Implementation]
    Fix --> Pass
    Pass -->|Yes| REFACTOR[🔵 REFACTOR Phase<br/>Cleanup & Optimize]
    
    REFACTOR --> Quality{Quality Check}
    Quality -->|Issues| REFACTOR
    Quality -->|✅ Pass| Done[✅ Complete Cycle]
    
    Done --> More{More Features?}
    More -->|Yes| RED
    More -->|No| End[End Session]
    
    Error --> RED
    
    style RED fill:#ff6b6b,stroke:#fff,stroke-width:2px,color:#fff
    style GREEN fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style REFACTOR fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
    style Error fill:#ff9f40,stroke:#fff,stroke-width:2px,color:#000
    style Done fill:#7c7cff,stroke:#fff,stroke-width:2px,color:#fff
"""
        ))
        
        # 6. Features - ADO Operations
        specs.append(DiagramSpec(
            page_file="features/ado-operations.html",
            diagram_type="mermaid-sequence",
            placement="section-start",
            title="ADO Work Item Generation Flow",
            priority=2,
            content="""
sequenceDiagram
    actor User
    participant MO as Master Orchestrator
    participant ADO as ADO v2 Orchestrator
    participant Wizard as Interactive Wizard
    participant API as Azure DevOps API
    
    User->>MO: "ado story: User Authentication"
    MO->>ADO: Route to ADO v2
    
    alt Wizard Mode
        ADO->>Wizard: Launch Interactive Session
        Wizard->>User: Query Project/Area
        User->>Wizard: Provide Details
        Wizard->>API: Create Work Item
    else Auto Mode
        ADO->>API: Auto-generate from context
    end
    
    API-->>ADO: Work Item ID
    ADO->>ADO: Generate Acceptance Criteria
    ADO->>ADO: Add Related Tasks
    ADO-->>User: Work Item Summary + Link
    
    Note over User,API: Supports: User Stories, Features, Bugs, Tasks
"""
        ))
        
        # 7. Features - Execution Orchestrator
        specs.append(DiagramSpec(
            page_file="features/execution-orchestrator.html",
            diagram_type="mermaid-flowchart",
            placement="hero",
            title="Execution Orchestrator State Machine",
            priority=2,
            content="""
stateDiagram-v2
    [*] --> Planning: User Request
    
    Planning --> ContextGathering: Plan Created
    ContextGathering --> ToolSelection: Context Loaded
    
    ToolSelection --> Execution: Tools Ready
    
    Execution --> Validation: Action Complete
    Validation --> Execution: Needs Retry
    Validation --> Success: All Valid
    Validation --> Failure: Max Retries
    
    Success --> [*]
    Failure --> [*]
    
    note right of Planning
        Query Tier 1
        Load Plan State
    end note
    
    note right of Execution
        File Operations
        Terminal Commands
        API Calls
    end note
"""
        ))
        
        # 8. Architecture - Multi-Repo
        specs.append(DiagramSpec(
            page_file="architecture/multi-repo.html",
            diagram_type="mermaid-flowchart",
            placement="hero",
            title="Multi-Repository Knowledge Coordination",
            priority=2,
            content="""
graph TD
    CORTEX[CORTEX Repo<br/>Core Intelligence]
    User1[User Repo 1<br/>Project A]
    User2[User Repo 2<br/>Project B]
    User3[User Repo 3<br/>Project C]
    
    Brain[(4-Tier Brain<br/>Shared Memory)]
    
    CORTEX -->|Loads| Brain
    User1 -->|Context| Brain
    User2 -->|Context| Brain
    User3 -->|Context| Brain
    
    Brain -->|Orchestrates| CORTEX
    Brain -->|Applies| User1
    Brain -->|Applies| User2
    Brain -->|Applies| User3
    
    CORTEX -.->|Never Commits To| User1
    CORTEX -.->|Never Commits To| User2
    CORTEX -.->|Never Commits To| User3
    
    style CORTEX fill:#7c7cff,stroke:#fff,stroke-width:3px,color:#fff
    style Brain fill:#ffd700,stroke:#fff,stroke-width:2px,color:#000
    style User1 fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
    style User2 fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style User3 fill:#00bfff,stroke:#fff,stroke-width:2px,color:#000
"""
        ))
        
        # 9. Security - SKULL Protection
        specs.append(DiagramSpec(
            page_file="architecture/skull-protection.html",
            diagram_type="mermaid-flowchart",
            placement="hero",
            title="SKULL Brain Protection Rules",
            priority=1,
            content="""
graph TD
    Request[User Request] --> MO[Master Orchestrator]
    
    MO --> SKULL{SKULL Rules Check}
    
    SKULL -->|TDD?| TDD[TDD_ENFORCEMENT<br/>RED→GREEN→REFACTOR]
    SKULL -->|Create?| Discovery[HOLISTIC_DISCOVERY<br/>Search Before Create]
    SKULL -->|Refactor?| Cleanup[REFACTOR_CLEANUP<br/>Remove Duplicates]
    SKULL -->|Git?| Isolation[GIT_ISOLATION<br/>No CORTEX→User Commits]
    SKULL -->|Plan?| Planning[PLANNING_ISOLATION<br/>Plans Don't Implement]
    
    TDD -->|✅ Pass| Execute[Execute Action]
    Discovery -->|✅ Pass| Execute
    Cleanup -->|✅ Pass| Execute
    Isolation -->|✅ Pass| Execute
    Planning -->|✅ Pass| Execute
    
    TDD -->|❌ Violation| Block[Block + Explain]
    Discovery -->|❌ Violation| Block
    Cleanup -->|❌ Violation| Block
    Isolation -->|❌ Violation| Block
    Planning -->|❌ Violation| Block
    
    Execute --> Result[Return Result]
    Block --> Error[Error Message]
    
    style SKULL fill:#ff6b6b,stroke:#fff,stroke-width:3px,color:#fff
    style Execute fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style Block fill:#ff9f40,stroke:#fff,stroke-width:2px,color:#000
"""
        ))
        
        # 10. Features - Planning System
        specs.append(DiagramSpec(
            page_file="features/planning-system.html",
            diagram_type="mermaid-flowchart",
            placement="section-start",
            title="Planning System v5 Architecture",
            priority=1,
            content="""
graph TD
    User[User: "plan feature X"] --> MO[Master Orchestrator]
    MO -->|Route| Planning[Planning v5 Orchestrator]
    
    Planning --> Phase0[Phase 0: Discovery<br/>Search existing code]
    Phase0 --> PhaseM1[Phase -1: Knowledge<br/>Load relevant modules]
    PhaseM1 --> Phases[Phases 1-N<br/>Implementation Steps]
    
    Phases --> REFACTOR[Phase N+1: REFACTOR<br/>Cleanup & Optimize]
    
    Planning -->|Writes| PlanDB[(Planning State DB)]
    Planning -->|Creates| Docs[Plan Documents]
    
    REFACTOR -->|Enforces| SKULL[SKULL Rules<br/>Whole-file cleanup]
    
    PlanDB -->|Queried by| Exec[Execution Orchestrators]
    Docs -->|Guide| User
    
    style Planning fill:#ffd700,stroke:#fff,stroke-width:3px,color:#000
    style Phase0 fill:#00d4ff,stroke:#fff,stroke-width:2px,color:#000
    style PhaseM1 fill:#7c7cff,stroke:#fff,stroke-width:2px,color:#fff
    style REFACTOR fill:#00ff88,stroke:#fff,stroke-width:2px,color:#000
    style SKULL fill:#ff6b6b,stroke:#fff,stroke-width:2px,color:#fff
"""
        ))
        
        return specs
    
    def inject_diagram(self, html_file: Path, spec: DiagramSpec) -> bool:
        """Inject a diagram into an HTML file."""
        try:
            html_content = html_file.read_text(encoding='utf-8')
            
            # Create diagram HTML
            diagram_html = f'''
    <!-- Intelligent Diagram: {spec.title} -->
    <div class="glass-card-display animation-t1 diagram-container">
        <h2 class="section-title"><i class="fas fa-project-diagram pulse-glow-glass--fast"></i> {spec.title}</h2>
        <div class="mermaid-diagram">
            <div class="mermaid">
{spec.content.strip()}
            </div>
        </div>
    </div>
'''
            
            # Find insertion point based on placement
            if spec.placement == "hero":
                # Insert after page title card
                pattern = r'(</div>\s*</div>\s*<!-- Page Title Card.*?-->)'
                replacement = rf'\1\n{diagram_html}'
            elif spec.placement == "section-start":
                # Insert before first content section
                pattern = r'(<!-- Main Content -->.*?<main[^>]*>)'
                replacement = rf'\1\n{diagram_html}'
            else:
                # Default: after main content opening
                pattern = r'(<main[^>]*>\s*<div[^>]*>)'
                replacement = rf'\1\n{diagram_html}'
            
            # Perform replacement
            html_content_new = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)
            
            if html_content_new != html_content:
                html_file.write_text(html_content_new, encoding='utf-8')
                return True
            else:
                print(f"   ⚠️  Could not find insertion point for {html_file.name}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error injecting diagram into {html_file}: {e}")
            return False
    
    def enhance_all_pages(self) -> Dict[str, int]:
        """Enhance all high-priority pages with diagrams."""
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        specs = self.generate_diagram_specs()
        specs.sort(key=lambda x: x.priority)  # Process highest priority first
        
        print(f"\n📊 Generated {len(specs)} diagram specifications")
        print("\n🎨 Injecting diagrams into pages...")
        
        for spec in specs:
            html_file = self.docs_dir / spec.page_file
            
            if not html_file.exists():
                print(f"   ⚠️  {spec.page_file} not found - skipped")
                stats['skipped'] += 1
                continue
            
            # Check if diagram already exists
            content = html_file.read_text(encoding='utf-8')
            if spec.title in content:
                print(f"   ⏭️  {spec.page_file} already has diagram - skipped")
                stats['skipped'] += 1
                continue
            
            if self.inject_diagram(html_file, spec):
                print(f"   ✅ {spec.page_file} → {spec.diagram_type} added")
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        return stats


def main():
    """Main execution function."""
    print("📊 CORTEX Intelligent Diagram Enhancer")
    print("=" * 50)
    
    enhancer = IntelligentDiagramEnhancer()
    
    # Enhance pages
    stats = enhancer.enhance_all_pages()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Enhancement Summary:")
    print(f"   Diagrams Added: {stats['success']}")
    print(f"   Failed: {stats['failed']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Total Specs: {stats['success'] + stats['failed'] + stats['skipped']}")
    
    print("\n🎉 Diagram enhancement complete!")


if __name__ == "__main__":
    main()
