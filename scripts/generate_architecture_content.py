#!/usr/bin/env python3
"""
Architecture Page Content Generator
====================================

Generates detailed content for the CORTEX Architecture page
following the approved glassmorphism theme with 7-color palette.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from bs4 import BeautifulSoup
import sys

def generate_architecture_content():
    """Generate complete architecture page content"""
    
    workspace = Path.cwd()
    html_path = workspace / "docs" / "architecture" / "index.html"
    
    if not html_path.exists():
        print(f"❌ Error: {html_path} not found")
        return False
        
    print(f"🎨 Generating detailed content for architecture view...")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    main = soup.find('main', id='main-content')
    
    if not main:
        print("❌ Error: Could not find main content area")
        return False
        
    # Clear ALL existing sections (except the page title card which has class 'hero-introduction')
    for section in main.find_all('section'):
        if 'hero-introduction' not in section.get('class', []):
            section.decompose()
    
    # Generate sections with glassmorphism styling
    sections = [
        generate_executive_summary(),
        generate_system_diagram(),
        generate_four_tier_brain(),
        generate_tier_details(),
        generate_agent_system(),
        generate_orchestrator_ecosystem(),
        generate_integration_flow(),
        generate_performance_metrics(),
        generate_quick_reference()
    ]
    
    # Append sections to main
    for section_html in sections:
        section_soup = BeautifulSoup(section_html, 'html.parser')
        main.append(section_soup)
        
    # Save
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
        
    print(f"✅ Content generated successfully!")
    print(f"📄 View at: http://localhost:8000/architecture/index.html")
    
    return True


def generate_executive_summary():
    """Generate executive summary section"""
    return '''
    <section class="glass-card-display glass-panel-emerald">
        <h2 class="section-title">
            <i class="fas fa-brain"></i>
            Executive Summary
        </h2>
        
        <p class="hero-description">
            CORTEX is a <strong>state-aware AI assistant</strong> with long-term memory, 
            context awareness, and strategic planning capabilities. Built on a revolutionary 
            <strong>4-tier brain architecture</strong> governed by Tier 0 SKULL protection rules, 
            CORTEX orchestrates complex multi-step workflows through specialized agents and 
            autonomous orchestrators.
        </p>
        
        <div class="masonry-grid">
            <a href="four-tier-brain.html" class="glass-card-clickable card-variant-primary">
                <div class="card-header-centered">
                    <i class="card-icon-primary fas fa-layer-group"></i>
                    <h3 class="card-title">4-Tier Brain</h3>
                </div>
                <p class="card-description">
                    Hierarchical memory system from Tier 0 (Governance) through 
                    Tier 3 (Developer Context) with semantic search and knowledge graphs.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-primary"><i class="fas fa-crown"></i> Tier 0 Governance</span>
                    <span class="stat-info"><i class="fas fa-database"></i> SQLite Backend</span>
                    <span class="stat-success"><i class="fas fa-search"></i> Semantic Search</span>
                </div>
            </a>
            
            <a href="skull-protection.html" class="glass-card-clickable card-variant-info">
                <div class="card-header-centered">
                    <i class="card-icon-info fas fa-shield-alt"></i>
                    <h3 class="card-title">SKULL Protection</h3>
                </div>
                <p class="card-description">
                    5 governance rules enforce TDD, holistic discovery, git isolation, 
                    planning separation, and autonomous hand-off protocols.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-info"><i class="fas fa-vial"></i> TDD Enforcement</span>
                    <span class="stat-warning"><i class="fas fa-code-branch"></i> Git Isolation</span>
                    <span class="stat-primary"><i class="fas fa-hand-paper"></i> Hand-off Protocol</span>
                </div>
            </a>
            
            <a href="agent-system.html" class="glass-card-clickable card-variant-warning">
                <div class="card-header-centered">
                    <i class="card-icon-warning fas fa-robot"></i>
                    <h3 class="card-title">Agent System</h3>
                </div>
                <p class="card-description">
                    2 specialist agents (LLM Intent Classifier, Response Template Renderer) 
                    provide intelligent routing and formatted responses.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-warning"><i class="fas fa-route"></i> Intent Routing</span>
                    <span class="stat-success"><i class="fas fa-palette"></i> Template Rendering</span>
                    <span class="stat-info"><i class="fas fa-percentage"></i> 95% Accuracy</span>
                </div>
            </a>
            
            <a href="orchestrator-ecosystem.html" class="glass-card-clickable card-variant-success">
                <div class="card-header-centered">
                    <i class="card-icon-success fas fa-cogs"></i>
                    <h3 class="card-title">Orchestrators</h3>
                </div>
                <p class="card-description">
                    8 autonomous workflow orchestrators handle planning, TDD, ADO integration, 
                    maintenance, investigation, and more.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-success"><i class="fas fa-gears"></i> 8 Orchestrators</span>
                    <span class="stat-primary"><i class="fas fa-python"></i> Python Runtime</span>
                    <span class="stat-warning"><i class="fas fa-bolt"></i> Autonomous</span>
                </div>
            </a>
        </div>
    </section>
    '''


def generate_system_diagram():
    """Generate system architecture diagram"""
    return '''
    <section class="glass-card-display glass-panel-cyan">
        <h2 class="section-title">
            <i class="fas fa-project-diagram"></i>
            System Architecture Overview
        </h2>
        
        <div class="mermaid-container">
            <pre class="mermaid">
graph TB
    subgraph "Tier 0: Governance Layer"
        SKULL[SKULL Protection Rules]
        TEMPLATES[Response Templates v4]
        GOVERNANCE[Brain Protection Rules]
    end
    
    subgraph "4-Tier Brain"
        T1[Tier 1: Working Memory<br/>Active Plans & Context]
        T2[Tier 2: Knowledge Graph<br/>Semantic Search]
        T3[Tier 3: Dev Context<br/>Code & Configs]
    end
    
    subgraph "Intelligence Layer"
        AGENTS[2 Specialist Agents<br/>Intent Classifier & Renderer]
        ORCH[8 Orchestrators<br/>Planning, TDD, ADO, etc.]
    end
    
    subgraph "Execution Layer"
        COPILOT[GitHub Copilot<br/>Tool Executor]
        PYTHON[Python Runtime<br/>Autonomous Execution]
    end
    
    SKULL --> AGENTS
    GOVERNANCE --> ORCH
    TEMPLATES --> AGENTS
    
    T1 --> AGENTS
    T2 --> AGENTS
    T3 --> AGENTS
    
    AGENTS --> COPILOT
    ORCH --> PYTHON
    
    COPILOT -.Routes to.-> ORCH
    PYTHON -.Updates.-> T1
            </pre>
        </div>
    </section>
    '''


def generate_four_tier_brain():
    """Generate four-tier brain section"""
    return '''
    <section class="glass-card-display glass-panel-teal">
        <h2 class="section-title">
            <i class="fas fa-brain"></i>
            Four-Tier Brain Architecture
        </h2>
        
        <p class="hero-description">
            CORTEX's hierarchical memory system enables persistent context, knowledge discovery, 
            and semantic understanding across conversations.
        </p>
        
        <div class="masonry-grid">
            <a href="four-tier-brain.html#tier0" class="glass-card-clickable card-variant-primary">
                <div class="card-header-centered">
                    <i class="card-icon-primary fas fa-crown"></i>
                    <h3 class="card-title">Tier 0: Governance</h3>
                </div>
                <p class="card-description">
                    <strong>SKULL Protection Rules</strong> enforce operational boundaries through 5 immutable governance rules.
                </p>
                <ul class="card-list">
                    <li><strong>TDD_ENFORCEMENT:</strong> Tests fail before implementation</li>
                    <li><strong>HOLISTIC_DISCOVERY:</strong> Search before create</li>
                    <li><strong>GIT_ISOLATION:</strong> CORTEX code never commits to user repos</li>
                    <li><strong>PLANNING_ISOLATION:</strong> Plans create, not implement</li>
                    <li><strong>HAND_OFF_PROTOCOL:</strong> Autonomous orchestrators execute independently</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-primary"><i class="fas fa-lock"></i> IMMUTABLE</span>
                    <span class="stat-warning"><i class="fas fa-shield-alt"></i> 5 Rules</span>
                </div>
            </a>
            
            <a href="working-memory.html" class="glass-card-clickable card-variant-info">
                <div class="card-header-centered">
                    <i class="card-icon-info fas fa-lightbulb"></i>
                    <h3 class="card-title">Tier 1: Working Memory</h3>
                </div>
                <p class="card-description">
                    Short-term context for current operations with real-time updates and automatic expiry.
                </p>
                <ul class="card-list">
                    <li><strong>Active Plans:</strong> YAML execution plans</li>
                    <li><strong>Session State:</strong> Current conversation context</li>
                    <li><strong>Recent History:</strong> Last 5 interactions</li>
                    <li><strong>Task Tracking:</strong> In-progress work items</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-info"><i class="fas fa-sync"></i> Real-time</span>
                    <span class="stat-warning"><i class="fas fa-clock"></i> 24h Expiry</span>
                </div>
            </a>
            
            <a href="knowledge-graph.html" class="glass-card-clickable card-variant-success">
                <div class="card-header-centered">
                    <i class="card-icon-success fas fa-network-wired"></i>
                    <h3 class="card-title">Tier 2: Knowledge Graph</h3>
                </div>
                <p class="card-description">
                    Semantic knowledge base with relationship mapping and vector embeddings for RAG.
                </p>
                <ul class="card-list">
                    <li><strong>Lessons Learned:</strong> Project insights & patterns</li>
                    <li><strong>User Preferences:</strong> Custom configurations</li>
                    <li><strong>Semantic Search:</strong> Vector embeddings for discovery</li>
                    <li><strong>Relationship Graph:</strong> Entities, concepts, connections</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-success"><i class="fas fa-database"></i> Persistent</span>
                    <span class="stat-primary"><i class="fas fa-search"></i> Semantic Search</span>
                </div>
            </a>
            
            <a href="four-tier-brain.html#tier3" class="glass-card-clickable card-variant-warning">
                <div class="card-header-centered">
                    <i class="card-icon-warning fas fa-code"></i>
                    <h3 class="card-title">Tier 3: Developer Context</h3>
                </div>
                <p class="card-description">
                    Project-specific technical context with automatic synchronization and per-project isolation.
                </p>
                <ul class="card-list">
                    <li><strong>Codebase Map:</strong> File structures & dependencies</li>
                    <li><strong>API Schemas:</strong> Interface definitions</li>
                    <li><strong>Configuration:</strong> Build, test, deployment configs</li>
                    <li><strong>Test Suites:</strong> Unit, integration, E2E tests</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-warning"><i class="fas fa-folder"></i> Per-Project</span>
                    <span class="stat-info"><i class="fas fa-sync-alt"></i> Auto-synced</span>
                </div>
            </a>
        </div>
    </section>
    '''


def generate_tier_details():
    """Generate tier details with 2-column layout"""
    return '''
    <section class="glass-card-display glass-panel-indigo">
        <h2 class="section-title">
            <i class="fas fa-layer-group"></i>
            Tier Storage & Operations
        </h2>
        
        <div class="two-column-layout">
            <div class="column">
                <h3><i class="fas fa-database"></i> Storage Locations</h3>
                <div class="code-block">
                    <pre>cortex-brain/
├── tier0/              # Governance (read-only)
│   ├── brain-protection-rules.yaml
│   └── response-templates-v4.yaml
├── tier1/              # Working memory
│   ├── active-plans/
│   └── session-state.json
├── tier2/              # Knowledge graph
│   ├── database/
│   │   └── brain.db (SQLite)
│   └── embeddings/
└── tier3/              # Dev context
    ├── project-maps/
    └── api-schemas/</pre>
                </div>
            </div>
            
            <div class="column">
                <h3><i class="fas fa-sync"></i> Access Patterns</h3>
                <div class="masonry-grid">
                    <div class="glass-card-display card-variant-primary">
                        <div class="metric-value">READ-ONLY</div>
                        <div class="metric-label">Tier 0 Access</div>
                    </div>
                    <div class="glass-card-display card-variant-success">
                        <div class="metric-value">&lt; 100ms</div>
                        <div class="metric-label">Tier 1 Writes</div>
                    </div>
                    <div class="glass-card-display card-variant-info">
                        <div class="metric-value">Vector Search</div>
                        <div class="metric-label">Tier 2 Queries</div>
                    </div>
                    <div class="glass-card-display card-variant-warning">
                        <div class="metric-value">On-Demand</div>
                        <div class="metric-label">Tier 3 Sync</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    '''


def generate_agent_system():
    """Generate agent system section"""
    return '''
    <section class="glass-card-display glass-panel-pink">
        <h2 class="section-title">
            <i class="fas fa-robot"></i>
            Agent System
        </h2>
        
        <p class="hero-description">
            Two specialized agents provide intelligent routing and response formatting.
        </p>
        
        <div class="masonry-grid">
            <a href="agent-system.html#intent-classifier" class="glass-card-clickable card-variant-primary">
                <div class="card-header-centered">
                    <i class="card-icon-primary fas fa-route"></i>
                    <h3 class="card-title">LLM Intent Classifier</h3>
                </div>
                <p class="card-description">
                    Analyzes user requests using LLM-based classification when regex patterns 
                    don't match. Routes to appropriate orchestrators with confidence scoring.
                </p>
                <ul class="card-list">
                    <li><strong>Input:</strong> User message text</li>
                    <li><strong>Processing:</strong> LLM semantic analysis</li>
                    <li><strong>Output:</strong> Orchestrator + confidence (0.0-1.0)</li>
                    <li><strong>Fallback:</strong> Default to conversation mode</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-primary"><i class="fas fa-bullseye"></i> 95% Accuracy</span>
                    <span class="stat-success"><i class="fas fa-bolt"></i> &lt;200ms</span>
                    <span class="stat-info"><i class="fas fa-brain"></i> LLM-Powered</span>
                </div>
            </a>
            
            <a href="agent-system.html#template-renderer" class="glass-card-clickable card-variant-info">
                <div class="card-header-centered">
                    <i class="card-icon-info fas fa-palette"></i>
                    <h3 class="card-title">Response Template Renderer</h3>
                </div>
                <p class="card-description">
                    Formats responses using templates from response-templates-v4.yaml. 
                    Enforces cognitive load limits and accessibility standards (WCAG AA).
                </p>
                <ul class="card-list">
                    <li><strong>Templates:</strong> 12 response types (INSTANT to COMPREHENSIVE)</li>
                    <li><strong>Modes:</strong> Concise, Balanced, Verbose</li>
                    <li><strong>Features:</strong> Progress bars, token counts, summaries</li>
                    <li><strong>Accessibility:</strong> Screen reader friendly, reduced motion</li>
                </ul>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-info"><i class="fas fa-universal-access"></i> WCAG AA</span>
                    <span class="stat-success"><i class="fas fa-file-alt"></i> 12 Templates</span>
                    <span class="stat-warning"><i class="fas fa-tachometer-alt"></i> 3 Modes</span>
                </div>
            </a>
        </div>
    </section>
    '''


def generate_orchestrator_ecosystem():
    """Generate orchestrator ecosystem section"""
    return '''
    <section class="glass-card-display glass-panel-purple">
        <h2 class="section-title">
            <i class="fas fa-cogs"></i>
            Orchestrator Ecosystem
        </h2>
        
        <p class="hero-description">
            Eight autonomous orchestrators handle complex multi-step workflows via Python execution.
        </p>
        
        <div class="masonry-grid">
            <a href="../orchestrators/planning-v5.html" class="glass-card-clickable card-variant-primary">
                <div class="card-header-centered">
                    <i class="card-icon-primary fas fa-map"></i>
                    <h3 class="card-title">Planning System v5</h3>
                </div>
                <p class="card-description">
                    YAML-based plan generation with 7-phase execution framework and TDD enforcement.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-primary"><i class="fas fa-layer-group"></i> 7 Phases</span>
                    <span class="stat-info"><i class="fas fa-file-code"></i> YAML Format</span>
                    <span class="stat-success"><i class="fas fa-vial"></i> TDD Enforced</span>
                </div>
            </a>
            
            <a href="../orchestrators/tdd-orchestrator.html" class="glass-card-clickable card-variant-warning">
                <div class="card-header-centered">
                    <i class="card-icon-warning fas fa-vial"></i>
                    <h3 class="card-title">TDD v2</h3>
                </div>
                <p class="card-description">
                    Test-Driven Development cycle: RED→GREEN→REFACTOR with coverage tracking.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-warning"><i class="fas fa-traffic-light"></i> RED-GREEN-REFACTOR</span>
                    <span class="stat-primary"><i class="fas fa-percentage"></i> Coverage</span>
                </div>
            </a>
            
            <a href="../orchestrators/ado-operations.html" class="glass-card-clickable card-variant-info">
                <div class="card-header-centered">
                    <i class="card-icon-info fas fa-project-diagram"></i>
                    <h3 class="card-title">ADO v2</h3>
                </div>
                <p class="card-description">
                    Azure DevOps integration for automated work item generation.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-info"><i class="fas fa-sitemap"></i> Auto Hierarchy</span>
                    <span class="stat-success"><i class="fas fa-tasks"></i> Stories/Tasks</span>
                </div>
            </a>
            
            <a href="../orchestrators/cleanup-orchestrator.html" class="glass-card-clickable card-variant-success">
                <div class="card-header-centered">
                    <i class="card-icon-success fas fa-broom"></i>
                    <h3 class="card-title">Cleanup v2</h3>
                </div>
                <p class="card-description">
                    Cache and log file removal with pattern matching and dry-run simulation.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-success"><i class="fas fa-eye"></i> Dry-Run</span>
                    <span class="stat-info"><i class="fas fa-bolt"></i> &lt;5s</span>
                </div>
            </a>
            
            <a href="../orchestrators/system-integrity.html" class="glass-card-clickable card-variant-primary">
                <div class="card-header-centered">
                    <i class="card-icon-primary fas fa-shield-alt"></i>
                    <h3 class="card-title">Vacuum v2</h3>
                </div>
                <p class="card-description">
                    Deep filesystem cleanup with safety validation and git backups.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-primary"><i class="fas fa-trash-alt"></i> Deep Clean</span>
                    <span class="stat-warning"><i class="fas fa-save"></i> Safe</span>
                </div>
            </a>
            
            <a href="../orchestrators/index.html#investigation" class="glass-card-clickable card-variant-warning">
                <div class="card-header-centered">
                    <i class="card-icon-warning fas fa-search"></i>
                    <h3 class="card-title">Investigation v2</h3>
                </div>
                <p class="card-description">
                    Root cause analysis with 5 Whys methodology for debugging.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-warning"><i class="fas fa-question-circle"></i> 5 Whys</span>
                    <span class="stat-info"><i class="fas fa-bug"></i> Debug</span>
                </div>
            </a>
            
            <a href="../orchestrators/index.html#sanitization" class="glass-card-clickable card-variant-info">
                <div class="card-header-centered">
                    <i class="card-icon-info fas fa-user-secret"></i>
                    <h3 class="card-title">Sanitization v2</h3>
                </div>
                <p class="card-description">
                    PII and secret removal for safe sharing with regex pattern matching.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-info"><i class="fas fa-lock"></i> PII Removal</span>
                    <span class="stat-success"><i class="fas fa-shield-alt"></i> Safe</span>
                </div>
            </a>
            
            <a href="../orchestrators/index.html#maintenance" class="glass-card-clickable card-variant-success">
                <div class="card-header-centered">
                    <i class="card-icon-success fas fa-wrench"></i>
                    <h3 class="card-title">Maintenance v2</h3>
                </div>
                <p class="card-description">
                    11-phase health check and repair pipeline with comprehensive validation.
                </p>
                <div class="card-stats card-stats-tetris">
                    <span class="stat-success"><i class="fas fa-heartbeat"></i> Health Check</span>
                    <span class="stat-primary"><i class="fas fa-cog"></i> 11 Phases</span>
                </div>
            </a>
        </div>
    </section>
    '''


def generate_integration_flow():
    """Generate integration & data flow section"""
    return '''
    <section class="glass-card-display glass-panel-amber">
        <h2 class="section-title">
            <i class="fas fa-exchange-alt"></i>
            Integration & Data Flow
        </h2>
        
        <div class="mermaid-container">
            <pre class="mermaid">
sequenceDiagram
    participant User
    participant Copilot
    participant IntentAgent as Intent Classifier
    participant Orchestrator
    participant Brain as 4-Tier Brain
    participant Python as Python Runtime
    
    User->>Copilot: "plan to add feature X"
    Copilot->>IntentAgent: Classify intent
    IntentAgent->>Brain: Query Tier 2 (patterns)
    Brain-->>IntentAgent: Similar requests
    IntentAgent-->>Copilot: Orchestrator=Planning, Confidence=0.95
    Copilot->>Python: Invoke planning orchestrator
    Python->>Brain: Read Tier 1 (active context)
    Python->>Brain: Write Tier 1 (new plan)
    Python-->>Copilot: Plan created
    Copilot->>User: Display plan with progress
            </pre>
        </div>
        
        <div class="masonry-grid">
            <div class="glass-card-display card-variant-success">
                <div class="metric-value">< 200ms</div>
                <div class="metric-label">Intent Classification</div>
            </div>
            <div class="glass-card-display card-variant-info">
                <div class="metric-value">< 2s</div>
                <div class="metric-label">Plan Generation</div>
            </div>
            <div class="glass-card-display card-variant-warning">
                <div class="metric-value">< 50ms</div>
                <div class="metric-label">Brain Read</div>
            </div>
            <div class="glass-card-display card-variant-primary">
                <div class="metric-value">< 100ms</div>
                <div class="metric-label">Brain Write</div>
            </div>
        </div>
    </section>
    '''


def generate_performance_metrics():
    """Generate performance metrics section"""
    return '''
    <section class="glass-card-display glass-panel-emerald">
        <h2 class="section-title">
            <i class="fas fa-tachometer-alt"></i>
            Core Capabilities
        </h2>
        
        <div class="masonry-grid">
            <div class="glass-card-display card-variant-primary metric-card">
                <div class="metric-icon"><i class="fas fa-rocket"></i></div>
                <div class="metric-value">95%</div>
                <div class="metric-label">Intent Accuracy</div>
                <div class="metric-detail">LLM classification precision</div>
            </div>
            
            <div class="glass-card-display card-variant-success metric-card">
                <div class="metric-icon"><i class="fas fa-clock"></i></div>
                <div class="metric-value">&lt; 2s</div>
                <div class="metric-label">Plan Generation</div>
                <div class="metric-detail">From request to YAML</div>
            </div>
            
            <div class="glass-card-display card-variant-info metric-card">
                <div class="metric-icon"><i class="fas fa-database"></i></div>
                <div class="metric-value">100ms</div>
                <div class="metric-label">Brain Latency</div>
                <div class="metric-detail">Tier 1-3 read/write</div>
            </div>
            
            <div class="glass-card-display card-variant-warning metric-card">
                <div class="metric-icon"><i class="fas fa-memory"></i></div>
                <div class="metric-value">4 Tiers</div>
                <div class="metric-label">Memory Hierarchy</div>
                <div class="metric-detail">Governance to Dev context</div>
            </div>
            
            <div class="glass-card-display card-variant-primary metric-card">
                <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                <div class="metric-value">5 Rules</div>
                <div class="metric-label">SKULL Protection</div>
                <div class="metric-detail">Immutable governance</div>
            </div>
            
            <div class="glass-card-display card-variant-success metric-card">
                <div class="metric-icon"><i class="fas fa-users"></i></div>
                <div class="metric-value">2 Agents</div>
                <div class="metric-label">Specialist Agents</div>
                <div class="metric-detail">Intent & Rendering</div>
            </div>
            
            <div class="glass-card-display card-variant-info metric-card">
                <div class="metric-icon"><i class="fas fa-cogs"></i></div>
                <div class="metric-value">8 Flows</div>
                <div class="metric-label">Orchestrators</div>
                <div class="metric-detail">Autonomous workflows</div>
            </div>
            
            <div class="glass-card-display card-variant-warning metric-card">
                <div class="metric-icon"><i class="fas fa-file-code"></i></div>
                <div class="metric-value">12 Types</div>
                <div class="metric-label">Response Templates</div>
                <div class="metric-detail">WCAG AA compliant</div>
            </div>
            
            <div class="glass-card-display card-variant-primary metric-card">
                <div class="metric-icon"><i class="fas fa-search"></i></div>
                <div class="metric-value">Vector</div>
                <div class="metric-label">Semantic Search</div>
                <div class="metric-detail">Tier 2 embeddings</div>
            </div>
        </div>
    </section>
    '''


def generate_quick_reference():
    """Generate quick reference section"""
    return '''
    <section class="glass-card-display glass-panel-cyan">
        <h2 class="section-title">
            <i class="fas fa-book"></i>
            Quick Reference
        </h2>
        
        <div class="two-column-layout">
            <div class="column">
                <h3><i class="fas fa-terminal"></i> Key Commands</h3>
                <div class="code-block">
                    <pre>plan                 → Generate YAML execution plan
tdd                  → Start TDD cycle
ado story            → Create ADO work item
vacuum               → Deep filesystem cleanup
cleanup              → Remove cache/logs
investigate          → Root cause analysis
sanitize             → Remove PII/secrets
maintenance          → 11-phase health check
help                 → List all operations</pre>
                </div>
            </div>
            
            <div class="column">
                <h3><i class="fas fa-folder"></i> File Locations</h3>
                <div class="code-block">
                    <pre>.github/prompts/CORTEX.prompt.md
    → Intent router (source of truth)

cortex-brain/brain-protection-rules.yaml
    → SKULL governance rules

cortex-brain/response-templates-v4.yaml
    → Response formatting templates

cortex-brain/manifests/orchestrators/
    → Orchestrator manifests

src/cortex_agents/
    → Agent implementations

src/orchestrators/
    → Orchestrator implementations</pre>
                </div>
            </div>
        </div>
        
        <div class="hero-stats">
            <a href="../orchestrators/index.html" class="stat-pill stat-primary">
                <i class="fas fa-cogs"></i> View Orchestrators
            </a>
            <a href="../features/index.html" class="stat-pill stat-success">
                <i class="fas fa-star"></i> Explore Features
            </a>
            <a href="../getting-started/index.html" class="stat-pill stat-info">
                <i class="fas fa-rocket"></i> Get Started
            </a>
        </div>
    </section>
    '''


if __name__ == "__main__":
    success = generate_architecture_content()
    sys.exit(0 if success else 1)
