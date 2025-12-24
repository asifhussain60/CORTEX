# Phase 7: CORTEX Self-Discovery & Documentation Automation

**Objective:** Enable Discovery Orchestrator to analyze CORTEX itself and automatically update all user-facing documentation, templates, and manifests.

**Duration:** 1 week  
**Status:** Not Started  
**Dependencies:** Phases 1-6 complete

---

## 🎯 Overview

This phase extends the Discovery Orchestrator with **self-awareness** capabilities - the ability to analyze CORTEX's own codebase, operations, orchestrators, and capabilities, then automatically generate/update documentation for different audiences (leadership, engineers, product owners).

### Why This Matters

- **Always Current:** Documentation stays in sync with codebase
- **Multi-Audience:** Auto-generates tailored views (executive, technical, product)
- **Zero Manual Work:** No more stale docs or missed features
- **Discovery-Driven:** Every new feature automatically documented

---

## 📋 Tasks

### Task 7.1: CORTEX Operations Discoverer

**Objective:** Scan `cortex-operations.yaml` and extract all operations, capabilities, and metadata.

**Implementation:**

```python
# src/operations/modules/discovery/cortex_operations_discoverer.py

class CORTEXOperationsDiscoverer:
    """Discover all CORTEX operations and capabilities."""
    
    def discover_operations(self) -> Dict[str, Any]:
        """
        Parse cortex-operations.yaml and extract:
        - Operation names and descriptions
        - Execution methods (cli_wrapper, copilot_chat, internal)
        - Natural language triggers
        - Module mappings
        - Examples
        - Implementation status
        """
        
    def discover_orchestrators(self) -> List[OrchestratorInfo]:
        """
        Scan src/operations/modules/orchestration/ and extract:
        - Orchestrator classes
        - Phase structures
        - Integration points
        - Capabilities
        """
        
    def discover_agents(self) -> List[AgentInfo]:
        """
        Scan src/cortex_agents/ and extract:
        - Agent purposes
        - Capabilities
        - Integration points
        """
        
    def discover_utilities(self) -> List[UtilityInfo]:
        """
        Scan src/operations/modules/ and extract:
        - Utility modules
        - Function counts
        - Capabilities
        """
```

**Deliverables:**
- `cortex_operations_discoverer.py`
- Unit tests for YAML parsing
- Integration test with actual cortex-operations.yaml

**Acceptance Criteria:**
- [ ] Discovers 100% of operations in cortex-operations.yaml
- [ ] Extracts all metadata (execution_method, natural_language, etc.)
- [ ] Handles YAML parsing errors gracefully
- [ ] Performance: <1s for full discovery

---

### Task 7.2: Template Auto-Updater

**Objective:** Automatically update `cortex-brain/response-templates.yaml` with newly discovered operations.

**Implementation:**

```python
# src/operations/modules/discovery/template_updater.py

class TemplateAutoUpdater:
    """Automatically update response templates with new operations."""
    
    def update_intro_templates(self, operations: Dict[str, Any]) -> None:
        """
        Update introduction templates (leadership, engineering, product) with:
        - Complete operation list
        - Capability summaries
        - Integration points
        - Success metrics
        """
        
    def update_help_template(self, operations: Dict[str, Any]) -> None:
        """
        Update help template with:
        - Command reference table
        - Usage examples
        - Category groupings
        """
        
    def validate_template_sync(self) -> List[str]:
        """
        Validate that all operations have corresponding templates.
        Return list of missing templates.
        """
```

**Deliverables:**
- `template_updater.py`
- Template validation tests
- Sync verification script

**Acceptance Criteria:**
- [ ] Updates intro templates for all 3 audiences
- [ ] Updates help template with complete command list
- [ ] Validates no missing templates
- [ ] Creates backup before updates
- [ ] Generates diff report

---

### Task 7.3: Deployment Manifest Updater

**Objective:** Automatically update `deployment-manifest.yaml` with production-ready features.

**Implementation:**

```python
# src/operations/modules/discovery/manifest_updater.py

class DeploymentManifestUpdater:
    """Automatically update deployment manifest with discovered features."""
    
    def discover_production_features(self) -> List[FeatureInfo]:
        """
        Scan codebase for production-ready features:
        - Module path
        - Function count
        - Test coverage
        - Integration status
        """
        
    def update_manifest(self, features: List[FeatureInfo]) -> None:
        """
        Update deployment-manifest.yaml with:
        - New production features
        - Capability lists
        - Validation status
        - Version tracking
        """
        
    def validate_feature_gates(self) -> Dict[str, bool]:
        """
        Validate each feature passes deployment gates:
        - Has tests (90%+ coverage)
        - No critical errors
        - Documentation exists
        - Integration tests pass
        """
```

**Deliverables:**
- `manifest_updater.py`
- Feature gate validator
- Manifest sync tests

**Acceptance Criteria:**
- [ ] Discovers all production-ready modules
- [ ] Validates feature gates (tests, docs, coverage)
- [ ] Updates manifest with accurate capability lists
- [ ] Preserves manual edits
- [ ] Generates change report

---

### Task 7.4: Living Feature Documentation Generator

**Objective:** Create auto-updating feature list document for stakeholders.

**Implementation:**

```python
# src/operations/modules/discovery/feature_doc_generator.py

class FeatureDocGenerator:
    """Generate living feature documentation for stakeholders."""
    
    def generate_feature_catalog(self) -> Path:
        """
        Generate comprehensive feature catalog:
        - Executive summary
        - Feature matrix (by audience)
        - Capability deep-dives
        - Integration map
        - Roadmap
        """
        
    def generate_audience_views(self) -> Dict[str, Path]:
        """
        Generate audience-specific views:
        - Leadership: Business value, ROI, strategic fit
        - Engineering: Technical details, APIs, integration
        - Product: Features, use cases, user stories
        """
        
    def generate_changelog(self) -> Path:
        """
        Generate auto-changelog from git commits:
        - New features added
        - Improvements
        - Bug fixes
        - Breaking changes
        """
```

**Deliverables:**
- `feature_doc_generator.py`
- Multi-audience document templates
- Auto-changelog generator

**Acceptance Criteria:**
- [ ] Generates complete feature catalog
- [ ] Creates 3 audience-specific views
- [ ] Auto-generates changelog from git
- [ ] Updates on every discovery run
- [ ] Formats beautifully (Markdown + HTML)

---

### Task 7.5: Folder Structure for Living Docs

**Objective:** Create dedicated, clean folder structure for auto-generated documentation.

**Structure:**

```
cortex-brain/
└── discovery/                          # New: Discovery system outputs
    ├── README.md                       # Overview of discovery system
    ├── features/                       # Living feature documentation
    │   ├── FEATURE-CATALOG.md          # Complete feature catalog (auto-generated)
    │   ├── FEATURE-MATRIX.md           # Feature comparison matrix
    │   ├── CHANGELOG.md                # Auto-generated from git
    │   └── audiences/
    │       ├── leadership-view.md      # Executive summary
    │       ├── engineering-view.md     # Technical deep-dive
    │       └── product-view.md         # Product features & use cases
    ├── operations/                     # Operation discovery results
    │   ├── operations-catalog.json     # Raw discovery data
    │   ├── operations-summary.md       # Human-readable summary
    │   └── operation-tree.txt          # Hierarchical view
    ├── orchestrators/                  # Orchestrator analysis
    │   ├── orchestrator-map.json       # All orchestrators with metadata
    │   ├── integration-graph.dot       # Integration visualization
    │   └── capability-matrix.md        # Orchestrator capabilities
    ├── utilities/                      # Utility module discovery
    │   ├── utility-catalog.json        # All utilities with functions
    │   └── utility-summary.md          # Grouped by category
    ├── templates/                      # Template analysis
    │   ├── template-coverage.json      # Operations → Templates mapping
    │   └── missing-templates.md        # Templates to create
    ├── deployment/                     # Deployment readiness
    │   ├── production-features.json    # Features passing gates
    │   ├── feature-gates.md            # Gate validation results
    │   └── deployment-report.md        # Ready-to-deploy summary
    └── reports/                        # Discovery run reports
        └── {timestamp}-discovery-report.md
```

**Deliverables:**
- Folder structure creation script
- README for each folder
- `.gitignore` rules (exclude large JSON files)

**Acceptance Criteria:**
- [ ] Clean, organized folder structure
- [ ] READMEs explain each folder's purpose
- [ ] Git ignores large auto-generated files
- [ ] Easy navigation for stakeholders
- [ ] Supports versioning (timestamps)

---

### Task 7.6: Discovery Scheduler & Automation

**Objective:** Run discovery automatically on key events.

**Implementation:**

```python
# src/operations/modules/discovery/discovery_scheduler.py

class DiscoveryScheduler:
    """Schedule automatic discovery runs on trigger events."""
    
    def on_git_commit(self) -> None:
        """Run discovery after significant commits."""
        
    def on_orchestrator_change(self) -> None:
        """Run discovery when orchestrators modified."""
        
    def on_operation_change(self) -> None:
        """Run discovery when cortex-operations.yaml changes."""
        
    def on_deployment(self) -> None:
        """Run discovery before deployment (validation)."""
        
    def scheduled_daily(self) -> None:
        """Run discovery daily to catch drift."""
```

**Triggers:**
- Git pre-commit hook (optional)
- CI/CD pipeline integration
- Manual trigger: `cortex discover`
- Daily scheduled run (cron)

**Deliverables:**
- `discovery_scheduler.py`
- Git hook integration script
- CI/CD workflow example

**Acceptance Criteria:**
- [ ] Triggers on git commits (opt-in)
- [ ] Runs in CI/CD pipeline
- [ ] Manual trigger works
- [ ] Generates change reports
- [ ] Fast enough for pre-commit (<5s)

---

## 🔗 Integration with Existing Systems

### With Maintenance Orchestrator

```python
# Phase: Refresh Prompts
def refresh_prompts_phase(self):
    """
    Enhanced with discovery:
    1. Run CORTEX self-discovery
    2. Update templates
    3. Update manifest
    4. Generate feature docs
    5. Validate sync
    """
    discovery = DiscoveryOrchestrator(self.project_root)
    
    result = discovery.execute({
        'scope': 'cortex_self_discovery',
        'update_templates': True,
        'update_manifest': True,
        'generate_docs': True
    })
    
    return result
```

### With Deployment Orchestrator

```python
# Pre-deployment validation
def pre_deployment_checks(self):
    """
    Run discovery to validate deployment readiness:
    - All features documented
    - All templates synced
    - Manifest up-to-date
    - Feature gates passing
    """
    discovery = DiscoveryOrchestrator(self.project_root)
    
    validation = discovery.execute({
        'scope': 'deployment_validation',
        'strict': True
    })
    
    if not validation.data['all_gates_passing']:
        raise DeploymentBlockedError(validation.data['failures'])
```

---

## 📊 Success Metrics

### Functional Metrics

- **Discovery Accuracy:** 100% of operations discovered
- **Sync Status:** 0 missing templates/manifest entries
- **Update Speed:** <5s for full discovery + updates
- **Documentation Quality:** Passes readability checks

### Quality Metrics

- **Template Coverage:** 100% operations have templates
- **Manifest Accuracy:** 100% production features listed
- **Documentation Freshness:** Updated within 24 hours of code change
- **Change Detection:** Catches 100% of new operations

### Business Metrics

- **Stakeholder Satisfaction:** 9/10 rating for documentation
- **Time Savings:** 95% reduction in manual doc updates
- **Discovery Frequency:** 1+ runs per day (automated)
- **Zero Drift:** Docs always match code

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_operations_discoverer():
    """Test operations discovery from cortex-operations.yaml"""
    
def test_template_updater():
    """Test template update logic"""
    
def test_manifest_updater():
    """Test deployment manifest updates"""
    
def test_feature_doc_generator():
    """Test feature documentation generation"""
```

### Integration Tests

```python
def test_full_discovery_and_update():
    """End-to-end test: discover → update → validate"""
    
def test_multi_audience_docs():
    """Test all 3 audience views generated correctly"""
    
def test_change_detection():
    """Test detection of new operations/features"""
```

### Validation Tests

```python
def test_template_coverage():
    """Validate every operation has template"""
    
def test_manifest_accuracy():
    """Validate manifest matches codebase"""
    
def test_documentation_quality():
    """Validate docs are readable and complete"""
```

---

## 📋 Acceptance Criteria

### Must Have

- [ ] Discovers 100% of CORTEX operations
- [ ] Updates response templates automatically
- [ ] Updates deployment manifest automatically
- [ ] Generates living feature catalog
- [ ] Creates 3 audience-specific views
- [ ] Runs in <5s for full discovery
- [ ] Integrates with Maintenance Orchestrator
- [ ] Validates sync (0 drift)

### Should Have

- [ ] Git hook integration (pre-commit)
- [ ] CI/CD pipeline integration
- [ ] Auto-changelog generation
- [ ] Change report generation
- [ ] Backup before updates
- [ ] Rollback capability

### Nice to Have

- [ ] HTML export for feature docs
- [ ] Visualization graphs (D3.js)
- [ ] API documentation generation
- [ ] Video walkthrough generation
- [ ] Interactive feature explorer

---

## 🚨 Risks & Mitigations

### Risk 1: Breaking Existing Templates

**Impact:** High  
**Likelihood:** Medium  
**Mitigation:**
- Create backup before every update
- Validate template structure before writing
- Test with sample data first
- Preserve manual edits (comment markers)
- Rollback capability

### Risk 2: YAML Parsing Errors

**Impact:** High  
**Likelihood:** Low  
**Mitigation:**
- Validate YAML schema before parsing
- Handle malformed YAML gracefully
- Provide clear error messages
- Test with edge cases
- Fallback to previous version

### Risk 3: Documentation Quality

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:**
- Use templates for consistency
- Run readability checks (Flesch-Kincaid)
- Get stakeholder feedback early
- Iterate based on usage
- Include examples in docs

---

## 🔍 Next Steps After Phase 7

1. **Deploy to Production**
   - Validate all discovery features
   - Run full CORTEX self-discovery
   - Update all templates/manifest
   - Generate initial feature catalog

2. **Enable Automation**
   - Set up git hooks (opt-in)
   - Configure CI/CD integration
   - Schedule daily discovery runs
   - Monitor for drift

3. **Stakeholder Rollout**
   - Share feature catalog with leadership
   - Get feedback on audience views
   - Iterate based on usage
   - Train team on discovery system

4. **Continuous Improvement**
   - Monitor discovery metrics
   - Improve documentation quality
   - Add visualizations
   - Expand automation

---

## 📚 References

- **Operations YAML:** `cortex-operations.yaml`
- **Response Templates:** `cortex-brain/response-templates.yaml`
- **Deployment Manifest:** `deployment-manifest.yaml`
- **Maintenance Orchestrator:** `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`

---

**Status:** 🟡 Ready for Implementation  
**Dependencies:** Phases 1-6  
**Estimated Duration:** 1 week  
**Priority:** HIGH (enables CORTEX self-awareness)
