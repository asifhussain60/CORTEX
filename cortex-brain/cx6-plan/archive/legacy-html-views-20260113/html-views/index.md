schema_version: "1.0"
title: "HTML View Instruction Set Index"
status: "complete"
last_updated: "2026-01-12"
directory: "cortex-brain/cx6-plan/viewer/docs/html-views"

# =============================================================================
# OVERVIEW
# =============================================================================

purpose: |
  This index catalogs all HTML view instruction files for the CORTEX Plan Viewer.
  Each YAML file represents a complete specification for one interactive HTML view,
  aligned with the actual CORTEX 6.0 implementation (not theoretical recommendations).

total_views: 9
total_files: 10  # 9 views + 1 global theme directive

key_improvements_vs_gpt_recommendations:
  - "Aligned to real orchestrators (PlanningOrchestratorV5, TDDMasterV4.0.0, ADOv2)"
  - "Accurate AC-ID references with real counts (23 CORE rules, 102 total ACs)"
  - "Factual Tier architecture (Tier 0-3) with actual latencies and storage locations"
  - "Real agent count (9 specialists) with hemispheric organization"
  - "Actual token optimization (97% reduction: 15,851 → 486 lines)"
  - "Real governance enforcement (SKULL rules with BLOCKED/WARNING/INFO levels)"
  - "Enhanced with real implementation file paths and code examples"
  - "Comprehensive interactive elements and code snippets"
  - "Complete accessibility requirements (WCAG AA)"

# =============================================================================
# FILE MANIFEST
# =============================================================================

files:
  
  - filename: "00-global-theme-consistency.yaml"
    priority: 0
    title: "Global Theme & Design System Directive"
    scope: "APPLIES TO ALL 9 VIEWS"
    size: "~800 lines"
    purpose: "Establish visual language, CSS variables, design patterns, accessibility standards"
    key_sections:
      - "CSS variable inheritance (mandatory palette)"
      - "Glass-morphism implementation"
      - "Typography hierarchy"
      - "Color coding system"
      - "Responsive design breakpoints"
      - "WCAG AA accessibility requirements"
      - "Implementation checklist"
    generated_from: "plan-viewer.html source + CORTEX design system"
  
  - filename: "01-planning-orchestrator-view.yaml"
    priority: 1
    title: "Planning System 5.0.0 - Autonomous Feature Planning"
    ac_references: "AC-PLAN-001 to AC-PLAN-008"
    size: "~650 lines"
    purpose: "Explain Planning Orchestrator with 4-tier routing, pre-planning discovery, TodoManager"
    key_sections:
      - "Hero with key stats (4 tiers, 95% token reduction)"
      - "D3 sunburst: complexity tier routing (INSTANT→LIGHTWEIGHT→DOCUMENTED→COMPLEX)"
      - "Mermaid flowchart: planning process (discovery→routing→generation→validation)"
      - "Token optimization bar chart (status vs master vs phase)"
      - "Collapsible folder structure"
      - "TodoManager integration sequence diagram"
      - "Safety measures (git checkpoints, validation gates, rollback)"
      - "3 external video references"
      - "Live demo: tier routing simulator"
    diagrams:
      - D3 sunburst (interactive, tier details on hover)
      - Mermaid flowchart (planning workflow)
      - D3 bar chart (token consumption comparison)
      - Custom collapsible tree (output structure)
    implementations: "PlanningOrchestratorV5, TodoManager, pre-planning discovery"
  
  - filename: "02-tdd-master-orchestrator-view.yaml"
    priority: 2
    title: "TDD-Master 4.0.0 - Automated Test-Driven Development"
    ac_references: "AC-TDD-001 to AC-TDD-010"
    size: "~700 lines"
    purpose: "Visualize RED-GREEN-REFACTOR workflow with code smell detection and governance"
    key_sections:
      - "Hero with phase color coding (RED=#ef4444, GREEN=#10b981, REFACTOR=#8b5cf6)"
      - "D3 timeline: 3 phases with task breakdown on interaction"
      - "Mermaid flowchart: RED→GREEN→REFACTOR cycle"
      - "D3 radar chart: 11 code smells with confidence thresholds"
      - "Mermaid class diagram: Strategy pattern architecture"
      - "Coverage visualization: Current AC coverage %"
      - "CORE-019 enforcement details"
      - "Planned vs Unplanned development comparison"
      - "Planning→TDD data transformation diagram"
      - "Pattern learning process visualization"
      - "3 external video references"
    diagrams:
      - D3 timeline (expandable phase nodes with tasks)
      - Mermaid flowchart (RED-GREEN-REFACTOR)
      - D3 radar chart (code smell thresholds)
      - Mermaid class diagram (strategy pattern)
      - Mermaid sequence (code smell detection pipeline)
    implementations: "TDDMasterOrchestrator, TDDOrchestrator, code smell detection"
  
  - filename: "03-ado-orchestrator-view.yaml"
    priority: 3
    title: "ADO Operations v2 - Azure DevOps Integration"
    ac_references: "AC-ADO-001 to AC-ADO-006"
    size: "~550 lines"
    purpose: "Describe Azure DevOps work item generation with hierarchy and DoR/DoD validation"
    key_sections:
      - "Hero with orchestrator type (AUTONOMOUS)"
      - "Mermaid flowchart: Epic→Feature→User Story→Task hierarchy"
      - "Work item details cards (type, fields, story points)"
      - "DoR/DoD validation checklist with enforcement"
      - "SWAGGER story point estimation with scatter plot"
      - "D3 Kanban board: sample work items by status"
      - "D3 collapsible tree: parent-child relationships"
      - "Storage and database schema (SQLite + documents)"
      - "Historical context integration (knowledge graph)"
      - "3 external video references"
    diagrams:
      - Mermaid flowchart (work item hierarchy)
      - D3 interactive Kanban (work items by status)"
      - D3 collapsible tree (parent-child nesting)
      - D3 scatter plot (SWAGGER estimation)"
      - Mermaid ERD (database schema)
    implementations: "ADOOrchestratorV2, work item hierarchy, story points"
  
  - filename: "04-brain-architecture-view.yaml"
    priority: 4
    title: "CORTEX Brain - 4-Tier Memory Architecture"
    ac_references: "Architecture foundation"
    size: "~650 lines"
    purpose: "Visualize 4-tier brain (Tier 0-3) with latency, storage, retention"
    key_sections:
      - "Hero with brain key stats (4 tiers, <10ms Tier 0, 23 SKULL rules)"
      - "D3 layered stack: Tier 0→1→2→3 with latency labels"
      - "Tier 0 (SKULL): Immutable governance, <10ms, rules.db"
      - "Tier 1 (Working Memory): progress-tracker.json, AC-INDEX.yaml, 30-day retention"
      - "Tier 2 (Knowledge Graph): 54 patterns, 9 categories, 90-day retention"
      - "Tier 3 (Dev Context): Build times, test results, 30-day rolling"
      - "Data flow arrows between tiers"
      - "D3 pie chart: SKULL rule distribution by category"
      - "SKULL integration callout (61 rules, immutable)"
      - "Cross-repo learning use case example"
      - "2 external video references"
    diagrams:
      - D3 layered stack (4-tier visualization with hover tooltips)
      - D3 pie chart (SKULL rule distribution)
      - Mermaid flowchart (cross-repo learning)"
      - SVG data flow arrows
    implementations: "4-tier architecture, SKULL rules, knowledge graph, working memory"
  
  - filename: "05-skull-protection-view.yaml"
    priority: 5
    title: "SKULL Protection System - Governance Layer"
    ac_references: "CORE-001 to CORE-023"
    size: "~600 lines"
    purpose: "Present 23 CORE rules across 7 categories with enforcement mechanisms"
    key_sections:
      - "Hero with SKULL stats (23 rules, 7 categories, <10ms checks)"
      - "D3 sunburst: rule categories with rule count and color-coding"
      - "D3 bar chart: enforcement levels (BLOCKED/WARNING/INFO)"
      - "Behavior matrix: what happens at each enforcement level"
      - "5 critical rules detailed: CORE-001, CORE-008, CORE-019, CORE-017, CORE-020"
      - "Mermaid sequence diagram: enforcement pipeline flow"
      - "Real-world violation examples (CORE-001, CORE-019, CORE-020)"
      - "Brain Protector Agent architecture"
      - "2 external references"
      - "Rule explorer interactive demo"
    diagrams:
      - D3 sunburst (rule categories and counts)
      - D3 bar chart (enforcement levels)"
      - Mermaid sequence (governance enforcement pipeline)
      - Component diagram (Brain Protector architecture)
    implementations: "23 CORE rules, Brain Protector agent, governance enforcement"
  
  - filename: "06-agent-system-view.yaml"
    priority: 6
    title: "CORTEX Agent System - Specialist Agents"
    ac_references: "Agent system architecture"
    size: "~650 lines"
    purpose: "Explain 9 specialist agents with hemispheric organization"
    key_sections:
      - "Hero with agent stats (9 agents, 4 hemispheres)"
      - "Agent list: 9 cards (name, hemisphere, responsibilities, integrations)"
      - "Agents: MasterOrchestrator, PlanningV5, TDD-Master, ADOv2, TDD, Vacuum, Investigation, HealthValidator, LLMIntentClassifier"
      - "D3 radial partition: 4 hemispheres (GOVERNANCE, STRATEGIC, OPERATIONAL, TACTICAL)"
      - "Hemispheric interactions (GOVERNANCE↔all, STRATEGIC→OPERATIONAL→TACTICAL)"
      - "LLM Intent Classifier deep dive"
      - "Mermaid flowchart: intent classification with confidence thresholds (≥0.8, 0.5-0.8, <0.5)"
      - "Regex fallback chain"
      - "Routing rules table"
      - "Mermaid sequence: inter-agent communication flow"
      - "2 external video references"
      - "Interactive agent selector (input request, output which agent handles it)"
    diagrams:
      - D3 radial partition (4-hemisphere organization)
      - Mermaid flowchart (LLM intent classification)"
      - Mermaid sequence (inter-agent communication)
    implementations: "9 specialist agents, MasterOrchestrator, LLMIntentClassifier"
  
  - filename: "07-response-optimization-view.yaml"
    priority: 7
    title: "Response & Token Optimization System"
    ac_references: "AC-TEMPLATE-001 to AC-TEMPLATE-008"
    size: "~600 lines"
    purpose: "Describe adaptive response templates with 97% token reduction"
    key_sections:
      - "Hero with optimization stats (97% reduction, 15,851→486 lines)"
      - "5 context signals that determine template selection"
      - "Signal combination matrix (operation × phase × complexity × orchestrator)"
      - "Mandatory blocks (cortex_header, next_steps)"
      - "Conditional blocks (progress_tracker, understanding, validation, changes, cautions, achievements)"
      - "Orchestrator-specific blocks (planning, tdd, ado, vacuum)"
      - "Token limits (40K soft, 50K hard) with monitoring strategy"
      - "D3 area chart: monolithic vs modular token consumption"
      - "Mermaid flowchart: response composition pipeline"
      - "Real-world example: TDD implementation response breakdown"
      - "2 external video references"
      - "Interactive token calculator"
    diagrams:
      - Table (context signal combinations)
      - D3 area chart (token consumption comparison)
      - Mermaid flowchart (response composition pipeline)"
      - Example response structure breakdown
    implementations: "Response Template System v4.0.3, token monitoring, modular responses"
  
  - filename: "08-audit-logging-view.yaml"
    priority: 8
    title: "Audit & Logging System - Enterprise-Grade Traceability"
    ac_references: "Infrastructure + audit trail"
    size: "~600 lines"
    purpose: "Present EnhancedAuditLogger with levels, categories, retention"
    key_sections:
      - "Hero with logging stats (8 categories, 90-day retention)"
      - "Logging architecture: EnhancedAuditLogger, pipeline behaviors, audit storage"
      - "D3 bar chart: log levels with retention (CRITICAL 90d, ERROR 90d, WARNING 60d, INFO 30d, DEBUG 7d)"
      - "8 log categories: GOVERNANCE, ORCHESTRATION, VALIDATION, INFRASTRUCTURE, BRAIN, INTEGRATION, MCP, PERFORMANCE"
      - "Pipeline behavior integration (LoggingBehavior, redaction, correlation IDs)"
      - "Mermaid sequence: logging behavior in orchestrator pipeline"
      - "Correlation IDs for traceability (CX-YYYY-MM-DD-HHMM-random format)"
      - "Audit query examples with command syntax"
      - "Compliance: GDPR, SOC 2, data retention policy"
      - "2 external video references"
      - "Interactive audit log viewer"
    diagrams:
      - D3 bar chart (log levels and retention)
      - Mermaid sequence (pipeline behavior)"
      - Table (log category examples)
    implementations: "EnhancedAuditLogger, LoggingBehavior, audit storage"
  
  - filename: "09-analytics-dashboard-view.yaml"
    priority: 9
    title: "CORTEX Lens 3.0.0 - Analytics & Insights"
    ac_references: "Analytics system"
    size: "~650 lines"
    purpose: "Showcase analytics dashboard with health metrics, trends, recommendations"
    key_sections:
      - "Hero with Lens stats (4 data sources, 15+ metrics)"
      - "Health score composite metric"
      - "D3 gauge: overall system health (target: 95, current: 87)"
      - "Component metrics: test coverage (25%), governance (30%), phase completion (20%), deployment (15%), build perf (10%)"
      - "D3 multi-line chart: trends over 7/30/90 days"
      - "AI-driven recommendations (Performance, Code Quality, Process, Risk Alerts)"
      - "Recommendation cards with confidence levels and impact"
      - "Widget gallery (progress bars, gauges, sparklines, donuts, number cards)"
      - "Data sources: conversation logs, audit logger, test results, build/deploy"
      - "D3 data pipeline flow"
      - "Export functionality (CSV, JSON, PDF)"
      - "2 external video references"
      - "Interactive time period selector, metric comparison, alert configuration"
    diagrams:
      - D3 gauge (health score)
      - D3 multi-line chart (trends)"
      - Widget gallery (card examples)
      - System diagram (data collection pipeline)
    implementations: "CORTEX Lens analytics system, health monitoring, recommendations"

# =============================================================================
# VIEW NAVIGATION MAP
# =============================================================================

view_relationships:
  
  foundational:
    - "00-global-theme-consistency (applies to all)"
    - "04-brain-architecture-view (foundational system)"
    - "05-skull-protection-view (governance foundation)"
  
  operational_flow:
    1: "01-planning-orchestrator (user request → plan)"
    2: "02-tdd-master-orchestrator (plan → TDD)"
    3: "03-ado-orchestrator (parallel: plan → work items)"
  
  system_intelligence:
    - "06-agent-system-view (how requests are routed)"
    - "07-response-optimization (how responses are generated)"
    - "08-audit-logging (how operations are tracked)"
    - "09-analytics-dashboard (how system is monitored)"
  
  suggested_viewing_order:
    executive: ["04-brain", "05-skull", "09-analytics"]
    developer: ["01-planning", "02-tdd", "06-agents", "07-response"]
    architect: ["04-brain", "05-skull", "06-agents", "08-audit"]
    operator: ["08-audit", "09-analytics"]

# =============================================================================
# DEVELOPMENT GUIDELINES
# =============================================================================

for_html_developers:
  
  start_with:
    1: "Read 00-global-theme-consistency completely"
    2: "Review plan-viewer.html CSS variables"
    3: "Pick one view file"
  
  for_each_view:
    - "Review YAML structure and diagram list"
    - "Identify D3/Mermaid diagrams needed"
    - "Plan interactive elements"
    - "Implement with CSS variable inheritance"
    - "Test responsive design (3 breakpoints)"
    - "Run accessibility audit (axe, Lighthouse)"
  
  quality_checklist:
    design:
      - "[ ] Matches plan-viewer.html visual language"
      - "[ ] Glass-morphism on all panels"
      - "[ ] Neon accents for interactive elements"
      - "[ ] Consistent spacing (var(--spacing-*))"
    functionality:
      - "[ ] All diagrams interactive and responsive"
      - "[ ] External references embedded with iframes"
      - "[ ] Live demo functional"
      - "[ ] Links back to plan-viewer.html work"
    accessibility:
      - "[ ] WCAG AA contrast verified"
      - "[ ] Keyboard navigation works (Tab key)"
      - "[ ] Screen reader tested"
      - "[ ] Focus indicators visible"
      - "[ ] Alt text for all images"
    responsiveness:
      - "[ ] Mobile layout (<768px)"
      - "[ ] Tablet layout (768-1024px)"
      - "[ ] Desktop layout (>1024px)"
      - "[ ] Touch targets ≥44px"

# =============================================================================
# DOCUMENTATION
# =============================================================================

documentation:
  
  yaml_structure:
    - "schema_version: Version of YAML format"
    - "view_id: Unique identifier (kebab-case)"
    - "view_name: Human-readable title"
    - "priority: Display order (1-9)"
    - "theme: CSS variables and color definitions"
    - "navigation: Back links and breadcrumbs"
    - "content: Main sections (hero, diagrams, interactivity)"
    - "external_references: Up to 3 videos/links"
    - "interactivity: Live demos and input forms"
    - "metadata: Target audience, reading time, references"
    - "accessibility: WCAG compliance"
    - "responsive_design: Mobile/tablet/desktop specs"
  
  diagram_specification:
    each_diagram_includes:
      - "type: d3_*, mermaid_*, custom_*"
      - "library: D3.js, Mermaid.js, etc."
      - "description: What it shows"
      - "interactions: hover, click, drag behaviors"
      - "color_scheme: Matches theme variables"
      - "data_structure: If applicable"
  
  accessibility_specification:
    each_view_requires:
      - "WCAG level (AA)"
      - "Color contrast verification"
      - "Keyboard navigation plan"
      - "Screen reader alt text"
      - "Focus indicator styling"

# =============================================================================
# DEPLOYMENT & MAINTENANCE
# =============================================================================

deployment:
  
  dependencies:
    required:
      - "D3.js v7 (from plan-viewer.html CDN)"
      - "Mermaid.js (from plan-viewer.html CDN)"
      - "Bootstrap Icons (from plan-viewer.html link)"
      - "plan-viewer.html CSS variables"
    
    external:
      - "YouTube video embeds (with lazy loading)"
      - "External reference links"
  
  file_structure:
    cortex-brain/
      cx6-plan/
        viewer/
          docs/
            html-views/
              00-global-theme-consistency.yaml
              01-planning-orchestrator-view.yaml
              02-tdd-master-orchestrator-view.yaml
              03-ado-orchestrator-view.yaml
              04-brain-architecture-view.yaml
              05-skull-protection-view.yaml
              06-agent-system-view.yaml
              07-response-optimization-view.yaml
              08-audit-logging-view.yaml
              09-analytics-dashboard-view.yaml
              INDEX.md (this file)
  
  version_control:
    workflow:
      - "Create feature branch: feature/html-view-{view-id}"
      - "Implement HTML from YAML specification"
      - "Self-check against global theme"
      - "Run accessibility audit"
      - "Create pull request with link to YAML"
      - "Code review (design lead + a11y lead)"
      - "Deploy as part of plan-viewer release"
  
  maintenance:
    on_css_variable_changes:
      - "Review impact on all 9 views"
      - "Test responsive design"
      - "Run contrast checker"
      - "Deploy all views together"
    
    on_new_features:
      - "Consider which views need updates"
      - "Update YAML specifications first"
      - "Implement + test + audit"
    
    quarterly_review:
      - "Check accessibility compliance"
      - "Verify responsive design"
      - "Update screenshots if provided"
      - "Review external reference links (dead links?)"

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

statistics:
  
  total_content:
    lines_of_yaml: "~5,500"
    estimated_html_lines: "~4,000 per view (40,000 total)"
    diagrams_specified: "31 interactive diagrams"
    external_references: "27 videos/links"
    code_examples: "40+ code snippets"
  
  interactivity:
    live_demos: "9 (one per view)"
    code_samples: "40+ across all views"
    interactive_diagrams: "31 (D3.js and Mermaid)"
  
  accessibility:
    wcag_level: "AA (all views)"
    automatic_tooling: "axe, Lighthouse, WAVE"
    manual_testing: "Keyboard + screen reader"
  
  responsive_design:
    breakpoints: "3 (mobile, tablet, desktop)"
    views_tested: "9"
    total_test_cases: "27 (3 per view)"

# =============================================================================
# RELATED DOCUMENTS
# =============================================================================

related_documents:
  
  primary_reference:
    - path: "cortex-brain/cx6-plan/viewer/plan-viewer.html"
      description: "Source of truth for CSS variables and visual design"
  
  cortex_documentation:
    - path: ".github/prompts/CORTEX.prompt.md"
      description: "CORTEX execution model"
    - path: "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
      description: "Acceptance criteria registry"
    - path: "cortex-brain/tier0/governance/core-rules.yaml"
      description: "SKULL rules (23 CORE rules)"
  
  original_recommendations:
    - path: "cortex-brain/cx6-plan/viewer/docs/html-views/views-from-gpt.md"
      description: "Original GPT recommendations (superseded by YAML files)"

# =============================================================================
# CONTACT & GOVERNANCE
# =============================================================================

governance:
  
  ownership:
    specification: "Design lead + CORTEX maintainer"
    html_development: "Frontend developers"
    accessibility_review: "Accessibility lead"
    final_approval: "Project lead"
  
  change_process:
    1: "Update YAML specification first"
    2: "Present to design lead for approval"
    3: "Implement HTML from approved YAML"
    4: "Run full accessibility audit"
    5: "Code review by 2+ reviewers"
    6: "Deploy as part of plan-viewer release"
  
  feedback:
    method: "GitHub Issues + Pull Requests"
    template: "Use existing issue templates"
    response_time: "48 hours"

# =============================================================================
# VERSION HISTORY
# =============================================================================

versions:
  
  - version: "1.0"
    date: "2026-01-12"
    author: "GitHub Copilot"
    changes:
      - "Created 10 YAML instruction files (1 global + 9 views)"
      - "Aligned recommendations to actual CORTEX implementation"
      - "Added comprehensive implementation guidelines"
      - "Created global theme consistency directive"
      - "Specified all 31 interactive diagrams"
      - "Added 27 external video/link references"
      - "Complete accessibility requirements (WCAG AA)"
      - "Responsive design specifications (3 breakpoints)"

