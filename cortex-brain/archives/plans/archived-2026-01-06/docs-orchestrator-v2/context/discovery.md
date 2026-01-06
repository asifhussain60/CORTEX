# Documentation Orchestrator v2.0 - Context Discovery

**Generated:** 2026-01-06  
**Plan:** docs-orchestrator-v2  
**Phase:** Context Discovery

---

## 🔍 Problem Space Analysis

### Current Documentation Site Issues

**From Screenshots Analysis:**
1. **Orchestrators Page (http://localhost:8000/orchestrators/index.html)** ✅ APPROVED TEMPLATE
   - Correct left/right body margins (2rem)
   - CORTEX logo prominently placed atop introduction panel
   - Hero-robot-head image present
   - Glassmorphism panel structure well-implemented
   - 10 orchestrators showcased with rich metadata
   - Three-tier information hierarchy (title, description, statistics)
   - Categorized presentation (Planning, Execution, System Ops, etc.)

2. **Architecture Page (http://localhost:8000/architecture/index.html)** ❌ NEEDS WORK
   - Follows glassmorphism theme visually
   - NO substantial content (minimal placeholder text)
   - ZERO diagrams (no Mermaid, no D3.js)
   - NO illustrations or architectural visualizations
   - Failure to establish CORTEX as sophisticated multi-orchestrator system
   - Missing: Four-tier brain hierarchy, system components, data flows, agent architecture

### Gap Analysis: Architecture vs Orchestrators

**Content Completeness Gap:**
- Orchestrators page: Displays all 10 orchestrators with complete details
- Architecture page: Shows only 2 orchestrators out of 10 in minimal "Orchestrator Ecosystem" section
- Gap Impact: Architecture page undermines credibility, fails architectural storytelling

**Visual Storytelling Gap:**
- Both pages: Zero Mermaid diagrams deployed, zero D3.js visualizations
- Architecture page should include: 9+ structural diagrams (data flow, tier communication, agent coordination, database schema, SKULL enforcement points)
- Orchestrators page should include: 5+ operational diagrams (lifecycle, category interactions, TDD cycle, planning phases)
- Current state: Pure card-grid presentation with no architectural context

**Content Uniqueness Gap:**
- Architecture page contains "Orchestrator Ecosystem" section (belongs on orchestrators page)
- No clear separation: Architecture should focus on HOW BUILT (structure), Orchestrators on WHAT DOES (operations)
- Visual overlap >30% (exceeds threshold)

---

## 🎯 User Requirements

**From User Request:**
1. **Running List of Validators:**
   - Template compliance validator (left/right margins, logo placement)
   - Inline style validator (zero tolerance)
   - Uniqueness validator (Architecture vs Orchestrators <30% overlap)
   - Diagram coverage validator (9+ diagrams on architecture page)

2. **Audit Logging Requirement:**
   - Log every action for review and fix
   - Track: inline style removal, CSS class application, validation failures, git checkpoints
   - Enable post-execution analysis and debugging

3. **Holistic Chat Review:**
   - Plan structure validation (5-subfolder standard from upgrade prompt)
   - Filename governance (10-45 chars, kebab-case)
   - Level 1 uniqueness enforcement (from chat01.md)
   - Recommended actions automation (diagram generation, plan migration)

4. **Centralized Tooling:**
   - Move scattered Python scripts to cortex-toolkit orchestrator
   - Unified CLI interface
   - Category-based organization (documentation, planning, routing)

5. **YAML-Based Orchestrator:**
   - Managed by master orchestrator
   - State-aware execution (tracks previous applications)
   - Rollback-safe operations (git checkpoints mandatory)

---

## 🏛️ Architecture Context

### Current Orchestrator Landscape

**Master Orchestrators (10 total):**
1. Planning v5 (priority 10) - YAML-based project planning
2. TDD Mastery v2 (priority 20) - Test-driven development
3. ADO Operations v2 (priority 30) - Azure DevOps work items
4. Sanitization v2 (priority 40) - PII/secret removal
5. Vacuum v2 (priority 45) - Deep filesystem cleanup
6. Cleanup v2 (priority 55) - Selective cache/log cleanup
7. Investigation (priority 60) - Root cause analysis
8. Refinement v2 (priority 60) - 7-phase improvement
9. Debug v2 (priority 61) - Autonomous debugging
10. Maintenance v2 (priority 50) - 12-phase health pipeline

**Documentation Orchestrator Positioning:**
- Priority: 25 (between TDD and ADO)
- Rationale: Documentation changes should not block feature development but are higher priority than data operations
- Pattern: `^(standardize|apply glassmorphism|docs standardization).*$`
- Type: Autonomous (no guided mode)

### Four-Tier Brain Integration

**Tier 0: Governance**
- Brain protection rule: `PYTHON_ONLY_GENERATION` (CRITICAL)
  - Blocks Copilot from directly editing HTML files
  - Enforces Python-only generation
  - Violation action: reject_request

**Tier 2: Knowledge Graph**
- `approved-panels.yaml` - Pattern library for glassmorphism components
- `variables.css` - CSS class registry (all classes must be registered)
- `html-standardization-state.json` - State tracking for page applications

**Tier 3: Dev Context**
- Reference implementations: `orchestrators/index.html`, `panel-viewer.html`
- Approved templates for validators to compare against

---

## 🔧 Technical Constraints

### Brain Protection (SKULL) Rules
1. **PYTHON_ONLY_GENERATION (CRITICAL):**
   - Copilot MUST NOT edit HTML files directly
   - All HTML changes via Python scripts
   - Enforcement: Block Copilot tool usage for HTML edits

2. **CSS_REGISTRY_ENFORCEMENT (CRITICAL):**
   - All CSS classes must exist in variables.css
   - No ad-hoc class creation
   - Validation before application

3. **INLINE_STYLE_PROHIBITION (CRITICAL):**
   - Zero inline styles allowed
   - Atomic removal before CSS application
   - Blocks execution if detected

4. **GIT_CHECKPOINT_REQUIRED (HIGH):**
   - Mandatory git checkpoint before destructive operations
   - Rollback-safe execution model

5. **STATE_PERSISTENCE (HIGH):**
   - Track all standardization applications
   - Prevent duplicate work
   - Enable incremental improvements

### Performance Requirements
- Page standardization: <2 minutes
- Diagram generation: <30 seconds per diagram
- Validator execution: <5 seconds per page
- Audit log query: <100ms response time

### Compatibility Requirements
- Python 3.11+ (for pattern matching and type hints)
- Cross-platform (Windows, macOS, Linux)
- VS Code integration (via run_in_terminal)
- Browser-agnostic HTML/CSS output

---

## 📊 Success Criteria

### Functional Criteria
- ✅ 95%+ template compliance rate
- ✅ Zero inline styles across all pages
- ✅ 9+ diagrams on architecture page
- ✅ <30% content overlap (architecture vs orchestrators)
- ✅ 100% audit logging coverage
- ✅ All scattered scripts centralized

### Quality Criteria
- ✅ >90% validator code coverage
- ✅ <2 minute page standardization
- ✅ Zero false positives in validation
- ✅ Git checkpoint safety (rollback tested)

### User Experience Criteria
- ✅ Single CLI command for full standardization
- ✅ Clear validation failure messages
- ✅ Visual progress indicators
- ✅ Copy-paste fix commands (when validation fails)

---

## 🗺️ Discovery Findings

### Scattered Python Scripts Audit

**Documentation Category (5 scripts):**
1. `scripts/remove-inline-styles.py` → `cortex-toolkit/orchestrators/documentation/`
2. `scripts/standardize_level1_views.py` → `cortex-toolkit/orchestrators/documentation/`
3. `scripts/detect-inline-styles.py` → `cortex-toolkit/orchestrators/documentation/`
4. `scripts/calculate-complexity.py` → `cortex-toolkit/orchestrators/documentation/`
5. `scripts/generate_architecture_diagrams.py` → `cortex-toolkit/orchestrators/documentation/`

**Planning Category (2 scripts):**
1. `scripts/validate_plan_structures.py` → `cortex-toolkit/orchestrators/planning/`
2. `scripts/upgrade_plan_structures.py` → `cortex-toolkit/orchestrators/planning/`

**Routing Category (2 scripts):**
1. `scripts/validate_orchestrator_registry.py` → `cortex-toolkit/orchestrators/routing/`
2. `scripts/regenerate_routing_table.py` → `cortex-toolkit/orchestrators/routing/`

**Total Scripts to Centralize:** 9

### Validator Requirements Analysis

**Template Compliance Validator:**
- Input: HTML page path, reference template path
- Checks: Margins, logo placement, hero image, panel structure
- Output: ValidationResult (passed, failures list)
- Priority: CRITICAL (blocks execution)

**Margins Validator:**
- Input: HTML page path
- Checks: body_left=2rem, body_right=2rem, content_max_width=1400px
- Output: Pixel-perfect validation result
- Priority: HIGH

**Logo Placement Validator:**
- Input: HTML page path
- Checks: CORTEX logo atop introduction panel (DOM order + visual position)
- Output: ValidationResult with positioning details
- Priority: HIGH

**Inline Style Validator:**
- Input: HTML page path
- Checks: Zero inline style attributes allowed
- Output: Count + list of elements with inline styles
- Priority: CRITICAL (zero tolerance)

**Uniqueness Validator:**
- Input: Two HTML page paths (e.g., architecture vs orchestrators)
- Checks: Content overlap via TF-IDF, heading similarity, diagram type overlap, visual component overlap
- Output: Overlap score (target <30%)
- Priority: MEDIUM (not blocking)

---

## 🎨 Architectural Diagram Inventory

**Required Diagrams for Architecture Page (9+):**

1. **Four-Tier Brain Hierarchy** (D3.js sunburst)
   - Visualizes Tier 0 → Tier 1 → Tier 2 → Tier 3
   - Shows data capacity and access patterns per tier

2. **System Component Overview** (D3.js force-directed graph)
   - Central "CORTEX Core" node
   - Connected to: 4 tiers, 10 orchestrators, 2 agents
   - Interactive node expansion

3. **Data Flow Pipeline** (Mermaid flowchart)
   - User Request → Router → Tier 0 → Tier 1 → Tier 2 → Tier 3 → Execution → Response
   - Shows data traversal through brain hierarchy

4. **Agent Coordination Protocol** (Mermaid sequence diagram)
   - LLMIntentClassifier routing logic
   - Right Brain (CodeGenerationAgent) vs Left Brain (TestGenerationAgent) collaboration
   - Corpus callosum communication

5. **Database Schema Relationships** (Mermaid ER diagram)
   - 5 databases: cortex-brain.db, metrics, alerts, status, compliance
   - Table relationships and foreign keys

6. **Tier Access Patterns** (D3.js Sankey diagram)
   - Data flow volumes between tiers
   - Hot/warm/cold data paths
   - Memory management architecture

7. **Module Dependency Graph** (D3.js chord diagram)
   - Module-to-module dependencies
   - Circular dependency detection
   - Import analysis

8. **Git Checkpoint Architecture** (Mermaid flowchart)
   - Checkpoint creation triggers
   - Rollback decision tree
   - Safety net layers

9. **SKULL Rule Enforcement Points** (Mermaid deployment diagram)
   - Where each SKULL rule is enforced
   - Orchestrator integration points
   - Violation handling flow

**Diagram Types Summary:**
- Mermaid: 5 diagrams (flowchart, sequence, ER, flowchart, deployment)
- D3.js: 4 diagrams (sunburst, force-directed, Sankey, chord)

---

## 📝 Next Steps (Context → Planning)

1. **Phase 1: Validators Development**
   - Implement 5 validator classes with audit logging
   - Unit tests with >90% coverage
   - Integration tests with real HTML files

2. **Phase 2: Audit Logger Integration**
   - Extend audit_logger.py with documentation events
   - Define metrics schema
   - Create log directory structure

3. **Phase 3: Orchestrator Manifest Enhancement**
   - Add validators section to YAML manifest
   - Define execution hooks
   - Configure failure handling

4. **Phase 4: Centralized Toolkit**
   - Move 9 scripts to cortex-toolkit/
   - Create unified CLI (Click-based)
   - Register toolkit orchestrator

5. **Phase 5: Architecture Uniqueness**
   - Audit architecture page content
   - Generate 9+ diagrams (Mermaid + D3.js)
   - Enforce uniqueness (<30% overlap)

6. **Phase 6: Integration & Testing**
   - End-to-end orchestrator test
   - Toolkit CLI test suite
   - Performance validation

---

**Discovery Status:** ✅ Complete  
**Readiness for Phase 1:** ✅ Ready  
**Risk Assessment:** Low (well-defined requirements, existing patterns)
