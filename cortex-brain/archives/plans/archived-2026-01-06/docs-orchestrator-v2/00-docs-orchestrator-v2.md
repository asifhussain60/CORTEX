# Documentation Orchestrator v2.0 - Master Plan

**Plan ID:** `docs-orchestrator-v2`  
**Version:** 2.0.0  
**Status:** 🟢 Active  
**Created:** 2026-01-06  
**Author:** Asif Hussain  
**Type:** Feature Development  
**Priority:** High  
**Complexity:** High

---

## 📋 Executive Summary

Develop a comprehensive YAML-based documentation orchestrator managed by the master orchestrator that enforces glassmorphism standards, validates approved template compliance, implements audit logging for every action, and ensures Level 1 page uniqueness with architectural diagrams.

**Problem Statement:**
- Current documentation site lacks standardization enforcement
- No validators for approved template compliance (orchestrators/index.html margins, CORTEX logo placement)
- Scattered Python tooling not centralized (remove-inline-styles.py, standardize_level1_view.py, etc.)
- Architecture page lacks content and diagrams compared to orchestrators page
- No audit logging for documentation changes
- Manual enforcement of glassmorphism theme

**Solution Overview:**
- YAML-based orchestrator manifest with 6-phase execution pipeline
- Validators registry for template compliance checking
- Audit logging integration for all operations
- Centralized toolkit orchestrator for Python scripts
- Architecture uniqueness enforcement (9+ diagrams, content differentiation)
- State-aware HTML standardization with rollback safety

---

## 🎯 Goals & Success Criteria

### Primary Goals
1. **Template Compliance Validation**
   - ✅ Validate left/right body margins match orchestrators/index.html
   - ✅ Verify CORTEX logo atop introduction panel on all Level 1 views
   - ✅ Ensure hero-robot-head present on all Level 1 pages
   - ✅ Validate glassmorphism panel structure

2. **Audit Logging Integration**
   - ✅ Log every inline style removal action
   - ✅ Log CSS class application events
   - ✅ Track git checkpoint creation
   - ✅ Record validation failures with context

3. **Level 1 Uniqueness Enforcement**
   - ✅ Architecture page: 9+ diagrams (Mermaid + D3.js)
   - ✅ Content differentiation: Architecture = HOW_BUILT vs Orchestrators = WHAT_DOES
   - ✅ Visual overlap <30% between pages
   - ✅ Remove duplicate orchestrator workflow content from architecture

4. **Centralized Tooling**
   - ✅ Move scattered scripts to cortex-toolkit orchestrator
   - ✅ Unified CLI for all documentation operations
   - ✅ Dependency management via orchestrator

### Success Metrics
- **Compliance Rate:** >95% of Level 1 pages pass validation
- **Visual Consistency:** 100% of pages use CSS classes (zero inline styles)
- **Architectural Coverage:** 9+ diagrams on architecture page
- **Audit Coverage:** 100% of actions logged
- **Uniqueness Score:** <30% content overlap between architecture and orchestrators
- **Centralization:** 0 scattered Python scripts outside toolkit

---

## 📊 Current State Analysis

### Existing Validators (Implicit)
From chat history and screenshots:
- **Approved Template:** `http://localhost:8000/orchestrators/index.html`
  - ✅ Correct left/right body margins
  - ✅ CORTEX logo atop introduction panel
  - ✅ Hero-robot-head image present
  - ✅ Glassmorphism panel structure

- **Non-Compliant Example:** `http://localhost:8000/architecture/index.html`
  - ❌ No content (minimal sections)
  - ❌ No diagrams (0 Mermaid, 0 D3.js)
  - ❌ No illustrations
  - ⚠️ Follows glassmorphism theme but lacks substance

### Scattered Python Scripts (Need Centralization)
```
scripts/
├── remove-inline-styles.py         → Toolkit
├── standardize_level1_views.py     → Toolkit
├── detect-inline-styles.py         → Toolkit
├── calculate-complexity.py         → Toolkit
├── generate_architecture_diagrams.py → Toolkit
├── validate_plan_structures.py     → Toolkit (planning category)
├── upgrade_plan_structures.py      → Toolkit (planning category)
├── validate_orchestrator_registry.py → Toolkit (orchestrator category)
└── regenerate_routing_table.py     → Toolkit (orchestrator category)
```

### Knowledge Base Dependencies
- **Tier 0:** `brain-protection-rules.yaml` (PYTHON_ONLY_GENERATION)
- **Tier 2:** 
  - `approved-panels.yaml` (pattern library)
  - `variables.css` (CSS class registry)
  - `html-standardization-state.json` (state tracking)
- **Tier 3:**
  - Reference implementations: `orchestrators/index.html`, `panel-viewer.html`

---

## 🏗️ Architecture

### Orchestrator Hierarchy
```
Master Orchestrator
    └── Documentation Orchestrator v2.0 (priority: 25)
            ├── Validators Registry
            │   ├── TemplateComplianceValidator
            │   ├── MarginsValidator
            │   ├── LogoPlacementValidator
            │   ├── InlineStyleValidator
            │   └── UniquenessValidator
            ├── Audit Logger Integration
            │   ├── ActionLogger (inline removal, CSS application)
            │   ├── ValidationLogger (compliance checks)
            │   └── StateLogger (persistence events)
            └── Execution Pipeline (6 phases)
                ├── Phase 1: Pre-Flight Validation
                ├── Phase 2: State Query & Pattern Matching
                ├── Phase 3: Inline Style Removal
                ├── Phase 4: CSS Class Application
                ├── Phase 5: State Persistence
                └── Phase 6: Validation & Reporting
```

### Centralized Toolkit Structure
```
cortex-toolkit/
├── orchestrators/
│   ├── documentation/
│   │   ├── remove_inline_styles.py
│   │   ├── standardize_level1_views.py
│   │   ├── detect_inline_styles.py
│   │   ├── calculate_complexity.py
│   │   ├── generate_architecture_diagrams.py
│   │   └── validate_template_compliance.py
│   ├── planning/
│   │   ├── validate_plan_structures.py
│   │   └── upgrade_plan_structures.py
│   └── routing/
│       ├── validate_orchestrator_registry.py
│       └── regenerate_routing_table.py
├── validators/
│   ├── __init__.py
│   ├── template_compliance_validator.py
│   ├── margins_validator.py
│   ├── logo_placement_validator.py
│   ├── inline_style_validator.py
│   └── uniqueness_validator.py
└── cli.py (unified CLI interface)
```

---

## 📝 Phases & Tasks

### Phase 1: Validators Registry Development
**Duration:** 4 hours  
**Dependencies:** None  
**DoR:**
- Documentation orchestrator manifest exists
- Audit logger integration documented
- Approved template analysis complete

**Tasks:**

#### Task 1.1: Template Compliance Validator
```python
# cortex-toolkit/validators/template_compliance_validator.py
class TemplateComplianceValidator:
    """Validates Level 1 pages against approved template standards."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.approved_template = self._load_approved_template()
    
    def validate(self, page_path: str) -> ValidationResult:
        """
        Validates:
        - Left/right body margins match orchestrators/index.html
        - CORTEX logo atop introduction panel
        - Hero-robot-head image present
        - Glassmorphism panel structure
        """
        results = []
        
        # Check margins
        margins = self._extract_margins(page_path)
        if margins != self.approved_template.margins:
            results.append(ValidationFailure(
                "margin_mismatch",
                f"Expected {self.approved_template.margins}, got {margins}"
            ))
        
        # Check logo placement
        logo_position = self._find_logo_position(page_path)
        if logo_position != "atop_introduction_panel":
            results.append(ValidationFailure(
                "logo_misplaced",
                f"Logo not atop introduction panel: {logo_position}"
            ))
        
        # Check hero image
        if not self._has_hero_robot_head(page_path):
            results.append(ValidationFailure(
                "missing_hero_image",
                "Hero-robot-head image not found"
            ))
        
        # Audit log
        self.audit_logger.log_validation_check(
            validator="template_compliance",
            page=page_path,
            passed=len(results) == 0,
            failures=results
        )
        
        return ValidationResult(
            passed=len(results) == 0,
            failures=results
        )
```

**DoD:**
- ✅ Validator class implemented with audit logging
- ✅ Unit tests with >90% coverage
- ✅ Integration test with orchestrators/index.html (baseline)
- ✅ Documentation in cortex-brain/documents/validators/

#### Task 1.2: Margins Validator
```python
class MarginsValidator:
    """Validates body left/right margins match approved template."""
    
    APPROVED_MARGINS = {
        "body_left": "2rem",
        "body_right": "2rem",
        "content_max_width": "1400px"
    }
    
    def validate(self, html_path: str) -> ValidationResult:
        soup = BeautifulSoup(open(html_path), 'html.parser')
        
        # Extract computed margins from CSS
        body_styles = self._extract_body_styles(soup)
        
        failures = []
        for margin_key, expected_value in self.APPROVED_MARGINS.items():
            actual_value = body_styles.get(margin_key)
            if actual_value != expected_value:
                failures.append(ValidationFailure(
                    margin_key,
                    f"Expected {expected_value}, got {actual_value}"
                ))
        
        return ValidationResult(
            passed=len(failures) == 0,
            failures=failures
        )
```

**DoD:**
- ✅ Pixel-perfect margin validation
- ✅ CSS class resolution (handles variables.css)
- ✅ Audit logging integration

#### Task 1.3: Logo Placement Validator
```python
class LogoPlacementValidator:
    """Validates CORTEX logo placement atop introduction panel."""
    
    def validate(self, html_path: str) -> ValidationResult:
        soup = BeautifulSoup(open(html_path), 'html.parser')
        
        # Find logo
        logo = soup.find('img', {'alt': re.compile(r'CORTEX.*Logo', re.I)})
        if not logo:
            return ValidationResult(
                passed=False,
                failures=[ValidationFailure("missing_logo", "CORTEX logo not found")]
            )
        
        # Find introduction panel
        intro_panel = soup.find('div', class_=re.compile(r'intro.*panel', re.I))
        if not intro_panel:
            return ValidationResult(
                passed=False,
                failures=[ValidationFailure("missing_intro_panel", "Introduction panel not found")]
            ))
        
        # Validate logo is BEFORE intro panel in DOM
        logo_index = self._get_element_index(logo)
        panel_index = self._get_element_index(intro_panel)
        
        if logo_index >= panel_index:
            return ValidationResult(
                passed=False,
                failures=[ValidationFailure(
                    "logo_not_atop",
                    f"Logo index {logo_index} >= panel index {panel_index}"
                )]
            )
        
        return ValidationResult(passed=True, failures=[])
```

**DoD:**
- ✅ DOM traversal logic correct
- ✅ Visual positioning validation (not just DOM order)
- ✅ Handles edge cases (multiple logos, nested panels)

#### Task 1.4: Uniqueness Validator
```python
class UniquenessValidator:
    """Validates Level 1 page content uniqueness (overlap <30%)."""
    
    def validate(self, page1_path: str, page2_path: str) -> ValidationResult:
        """
        Compares two Level 1 pages for content overlap.
        
        Metrics:
        - Section heading similarity
        - Paragraph text similarity (TF-IDF)
        - Diagram type overlap
        - Visual component overlap
        """
        page1_content = self._extract_content(page1_path)
        page2_content = self._extract_content(page2_path)
        
        # Calculate overlap scores
        heading_overlap = self._calculate_heading_overlap(page1_content, page2_content)
        text_overlap = self._calculate_text_similarity(page1_content, page2_content)
        diagram_overlap = self._calculate_diagram_overlap(page1_content, page2_content)
        visual_overlap = self._calculate_visual_overlap(page1_content, page2_content)
        
        # Weighted average
        total_overlap = (
            heading_overlap * 0.3 +
            text_overlap * 0.4 +
            diagram_overlap * 0.2 +
            visual_overlap * 0.1
        )
        
        passed = total_overlap < 0.30  # <30% threshold
        
        return ValidationResult(
            passed=passed,
            failures=[] if passed else [ValidationFailure(
                "excessive_overlap",
                f"Overlap score {total_overlap:.1%} exceeds 30% threshold"
            )],
            metadata={
                "overlap_score": total_overlap,
                "breakdown": {
                    "headings": heading_overlap,
                    "text": text_overlap,
                    "diagrams": diagram_overlap,
                    "visual": visual_overlap
                }
            }
        )
```

**DoD:**
- ✅ TF-IDF-based text similarity
- ✅ Diagram type classification (Mermaid, D3.js, static images)
- ✅ Visual component analysis (cards, panels, buttons)
- ✅ Detailed breakdown report

---

### Phase 2: Audit Logger Integration
**Duration:** 3 hours  
**Dependencies:** Phase 1 (validators structure known)

**Tasks:**

#### Task 2.1: Action Logger Enhancement
Extend `src/orchestrators/audit_logger.py` with documentation-specific events:

```python
class DocumentationAuditEvents:
    """Audit events specific to documentation orchestrator."""
    
    INLINE_STYLE_REMOVED = "inline_style_removed"
    CSS_CLASS_APPLIED = "css_class_applied"
    TEMPLATE_VALIDATION = "template_validation"
    UNIQUENESS_CHECK = "uniqueness_check"
    DIAGRAM_GENERATED = "diagram_generated"
    STATE_PERSISTED = "state_persisted"
    GIT_CHECKPOINT_CREATED = "git_checkpoint_created"
```

**Metrics to Track:**
```python
documentation_metrics = {
    "inline_styles_removed": int,
    "css_classes_applied": int,
    "pages_standardized": int,
    "validation_failures": int,
    "diagrams_generated": int,
    "git_checkpoints_created": int,
    "uniqueness_score": float,
    "complexity_score": float
}
```

**DoD:**
- ✅ Event types registered in audit logger
- ✅ Metrics schema defined
- ✅ Log directory created: `logs/cortex-audit/documentation/`
- ✅ Sensitive data redaction enabled (file paths sanitized)

#### Task 2.2: Validator Logging Wrapper
```python
class AuditedValidator:
    """Wraps validators with automatic audit logging."""
    
    def __init__(self, validator: BaseValidator, audit_logger: AuditLogger):
        self.validator = validator
        self.audit_logger = audit_logger
    
    def validate(self, *args, **kwargs) -> ValidationResult:
        start_time = time.time()
        
        # Log validation start
        self.audit_logger.log_event(
            event_type="validation_check",
            validator=self.validator.__class__.__name__,
            target=kwargs.get('page_path', 'unknown')
        )
        
        # Execute validation
        result = self.validator.validate(*args, **kwargs)
        
        # Log validation complete
        self.audit_logger.log_event(
            event_type="validation_check",
            validator=self.validator.__class__.__name__,
            passed=result.passed,
            failures=len(result.failures),
            duration_ms=int((time.time() - start_time) * 1000)
        )
        
        return result
```

**DoD:**
- ✅ All validators wrapped with audit logging
- ✅ Performance metrics captured (duration)
- ✅ Failure details logged (not just count)

---

### Phase 3: Orchestrator Manifest Enhancement
**Duration:** 2 hours  
**Dependencies:** Phase 1-2 (validators + audit logger ready)

**Tasks:**

#### Task 3.1: Add Validators Section to Manifest
Update `cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml`:

```yaml
# Validators Registry
validators:
  enabled: true
  registry_path: "cortex-toolkit/validators/"
  
  registered_validators:
    - id: "template_compliance"
      class: "TemplateComplianceValidator"
      priority: "critical"
      auto_run: true
      reference_template: "docs/orchestrators/index.html"
      
    - id: "margins"
      class: "MarginsValidator"
      priority: "high"
      auto_run: true
      approved_margins:
        body_left: "2rem"
        body_right: "2rem"
        content_max_width: "1400px"
    
    - id: "logo_placement"
      class: "LogoPlacementValidator"
      priority: "high"
      auto_run: true
      expected_position: "atop_introduction_panel"
    
    - id: "inline_styles"
      class: "InlineStyleValidator"
      priority: "critical"
      auto_run: true
      tolerance: 0  # Zero inline styles allowed
    
    - id: "uniqueness"
      class: "UniquenessValidator"
      priority: "medium"
      auto_run: false  # Manual trigger only
      threshold: 0.30  # <30% overlap
      compare_pages:
        - ["architecture/index.html", "orchestrators/index.html"]
        - ["architecture/index.html", "features/index.html"]
```

**DoD:**
- ✅ Validators section added with all 5 validators
- ✅ Priority levels defined (critical, high, medium)
- ✅ Auto-run configuration per validator
- ✅ Reference templates specified

#### Task 3.2: Add Execution Hooks for Validators
```yaml
phases:
  - id: 1
    name: "Pre-Flight Validation"
    validators:
      - template_compliance  # Runs first
      - margins              # Runs second
      - logo_placement       # Runs third
      - inline_styles        # BLOCKS if fails (critical)
    
    failure_handling:
      - validator: "inline_styles"
        condition: "failures > 0"
        action: "block"
        message: "CRITICAL: Inline styles detected. Run remove-inline-styles.py FIRST."
      
      - validator: "template_compliance"
        condition: "failures > 2"
        action: "warn"
        message: "Multiple template violations detected. Consider regeneration."
```

**DoD:**
- ✅ Validators integrated into phase execution
- ✅ Blocking conditions defined (critical validators)
- ✅ Failure messages user-friendly

---

### Phase 4: Centralized Toolkit Development
**Duration:** 5 hours  
**Dependencies:** Phase 1-3 (validators, audit logger, manifest ready)

**Tasks:**

#### Task 4.1: Move Scripts to Toolkit
```bash
# Create toolkit structure
mkdir -p cortex-toolkit/orchestrators/{documentation,planning,routing}
mkdir -p cortex-toolkit/validators

# Move scripts
mv scripts/remove-inline-styles.py cortex-toolkit/orchestrators/documentation/
mv scripts/standardize_level1_views.py cortex-toolkit/orchestrators/documentation/
mv scripts/detect-inline-styles.py cortex-toolkit/orchestrators/documentation/
mv scripts/calculate-complexity.py cortex-toolkit/orchestrators/documentation/
mv scripts/generate_architecture_diagrams.py cortex-toolkit/orchestrators/documentation/
mv scripts/validate_plan_structures.py cortex-toolkit/orchestrators/planning/
mv scripts/upgrade_plan_structures.py cortex-toolkit/orchestrators/planning/
mv scripts/validate_orchestrator_registry.py cortex-toolkit/orchestrators/routing/
mv scripts/regenerate_routing_table.py cortex-toolkit/orchestrators/routing/

# Move validators
# (Created in Phase 1)
```

**DoD:**
- ✅ All scripts moved to toolkit
- ✅ Import paths updated in code
- ✅ Symlinks created in scripts/ for backward compatibility (temporary)
- ✅ Deprecation warnings added to old script locations

#### Task 4.2: Unified CLI Development
```python
# cortex-toolkit/cli.py
import click
from cortex_toolkit.orchestrators.documentation import (
    remove_inline_styles,
    standardize_level1_views,
    detect_inline_styles,
    calculate_complexity,
    generate_architecture_diagrams
)
from cortex_toolkit.validators import (
    TemplateComplianceValidator,
    MarginsValidator,
    LogoPlacementValidator,
    InlineStyleValidator,
    UniquenessValidator
)

@click.group()
def cli():
    """CORTEX Toolkit - Unified CLI for orchestrator utilities."""
    pass

@cli.group()
def docs():
    """Documentation orchestrator commands."""
    pass

@docs.command()
@click.argument('page_path')
@click.option('--backup/--no-backup', default=True)
def remove_inline_styles(page_path, backup):
    """Remove all inline styles from HTML page."""
    # Implementation...

@docs.command()
@click.option('--check-uniqueness/--no-check', default=False)
@click.option('--enforce-uniqueness/--no-enforce', default=False)
def standardize_level1_views(check_uniqueness, enforce_uniqueness):
    """Standardize all Level 1 views with glassmorphism."""
    # Implementation...

@cli.group()
def validate():
    """Validation commands."""
    pass

@validate.command()
@click.argument('page_path')
@click.option('--reference', default='docs/orchestrators/index.html')
def template_compliance(page_path, reference):
    """Validate page against approved template."""
    validator = TemplateComplianceValidator(audit_logger)
    result = validator.validate(page_path, reference_template=reference)
    
    if result.passed:
        click.echo(click.style("✅ PASS: Template compliance validated", fg='green'))
    else:
        click.echo(click.style("❌ FAIL: Template violations detected:", fg='red'))
        for failure in result.failures:
            click.echo(f"  - {failure.code}: {failure.message}")

if __name__ == '__main__':
    cli()
```

**DoD:**
- ✅ CLI interface implemented with Click
- ✅ All documentation commands available
- ✅ Validator commands exposed
- ✅ Help text comprehensive
- ✅ Color output for readability

#### Task 4.3: Toolkit Orchestrator Registration
```yaml
# cortex-brain/manifests/orchestrators/toolkit-orchestrator.yaml
orchestrator_id: "toolkit_orchestrator"
name: "CORTEX Toolkit Orchestrator"
version: "1.0.0"
status: "production"
type: "utility"

routing:
  patterns:
    - pattern: "^(toolkit|tool|utility).*$"
      priority: 50
      confidence: 0.9

categories:
  documentation:
    scripts:
      - remove_inline_styles.py
      - standardize_level1_views.py
      - detect_inline_styles.py
      - calculate_complexity.py
      - generate_architecture_diagrams.py
    
  planning:
    scripts:
      - validate_plan_structures.py
      - upgrade_plan_structures.py
  
  routing:
    scripts:
      - validate_orchestrator_registry.py
      - regenerate_routing_table.py

cli_interface:
  enabled: true
  entry_point: "cortex-toolkit/cli.py"
  command: "cortex-toolkit"
```

**DoD:**
- ✅ Toolkit orchestrator manifest created
- ✅ Registered in master-orchestrator.yaml
- ✅ CLI accessible via `python -m cortex_toolkit.cli`
- ✅ Documentation in cortex-brain/documents/orchestrators/toolkit-orchestrator.md

---

### Phase 5: Architecture Uniqueness Implementation
**Duration:** 6 hours  
**Dependencies:** Phase 1-4 (full orchestrator + validators ready)

**Tasks:**

#### Task 5.1: Architecture Content Audit
Analyze `docs/architecture/index.html` for:
- Missing sections (vs orchestrators page)
- Duplicate content (orchestrator workflows)
- Diagram gaps (0 vs 9+ required)

**Expected Findings:**
```json
{
  "missing_sections": [
    "Four-Tier Brain Hierarchy",
    "System Component Overview",
    "Data Flow Pipeline",
    "Agent Coordination Protocol",
    "Database Schema Relationships",
    "Tier Access Patterns",
    "Module Dependency Graph",
    "Git Checkpoint Architecture",
    "SKULL Rule Enforcement"
  ],
  "duplicate_content": [
    "Orchestrator Ecosystem section (belongs on orchestrators page)"
  ],
  "diagram_count": {
    "current": 0,
    "required": 9,
    "gap": 9
  }
}
```

**DoD:**
- ✅ Audit report generated
- ✅ Content removal list finalized
- ✅ Diagram generation plan created

#### Task 5.2: Diagram Generation Script Enhancement
```python
# cortex-toolkit/orchestrators/documentation/generate_architecture_diagrams.py
import click
from jinja2 import Template

DIAGRAM_TEMPLATES = {
    "four_tier_brain": {
        "type": "d3_sunburst",
        "data_source": "cortex-brain/tier0/governance-schema.sql",
        "target": "docs/architecture/diagrams/four-tier-brain.html"
    },
    "system_components": {
        "type": "d3_force_directed",
        "data_source": "src/orchestrators/",
        "target": "docs/architecture/diagrams/system-components.html"
    },
    "data_flow": {
        "type": "mermaid_flowchart",
        "template": """
        flowchart TD
            User[User Request] --> Router[Intent Router]
            Router --> T0[Tier 0: Governance]
            T0 --> T1[Tier 1: Working Memory]
            T1 --> T2[Tier 2: Knowledge Graph]
            T2 --> T3[Tier 3: Dev Context]
            T3 --> Exec[Orchestrator Execution]
            Exec --> Response[Response Generation]
        """,
        "target": "docs/architecture/diagrams/data-flow.mmd"
    },
    # ... 6 more diagrams
}

@click.command()
@click.option('--target', type=click.Choice(['all', 'architecture', 'orchestrators']))
@click.option('--force/--no-force', default=False)
def generate_diagrams(target, force):
    """Generate architectural diagrams (Mermaid + D3.js)."""
    
    if target in ['all', 'architecture']:
        for diagram_id, config in DIAGRAM_TEMPLATES.items():
            if os.path.exists(config['target']) and not force:
                click.echo(f"⏭️  Skipping {diagram_id} (already exists)")
                continue
            
            click.echo(f"🎨 Generating {diagram_id}...")
            
            if config['type'].startswith('mermaid'):
                _generate_mermaid_diagram(config)
            elif config['type'].startswith('d3'):
                _generate_d3_diagram(config)
            
            click.echo(f"✅ Generated: {config['target']}")
```

**DoD:**
- ✅ 9+ diagram templates defined
- ✅ Mermaid CLI integration working
- ✅ D3.js diagram generation functional
- ✅ Diagrams auto-injected into HTML

#### Task 5.3: Uniqueness Enforcement Script
```python
# cortex-toolkit/orchestrators/documentation/standardize_level1_views.py (enhance)
@click.command()
@click.option('--check-uniqueness/--no-check', default=False)
@click.option('--enforce-uniqueness/--no-enforce', default=False)
def standardize_level1_views(check_uniqueness, enforce_uniqueness):
    """Standardize Level 1 views with uniqueness enforcement."""
    
    pages = [
        'docs/architecture/index.html',
        'docs/orchestrators/index.html',
        'docs/features/index.html',
        # ... all Level 1 pages
    ]
    
    if check_uniqueness:
        validator = UniquenessValidator(audit_logger)
        
        # Check architecture vs orchestrators
        result = validator.validate(
            'docs/architecture/index.html',
            'docs/orchestrators/index.html'
        )
        
        click.echo(f"Overlap Score: {result.metadata['overlap_score']:.1%}")
        
        if not result.passed:
            click.echo(click.style("⚠️  FAIL: Excessive overlap detected", fg='yellow'))
            
            if enforce_uniqueness:
                click.echo("🔧 Enforcing uniqueness...")
                _remove_duplicate_content('docs/architecture/index.html')
                _generate_missing_diagrams('docs/architecture/index.html')
                click.echo("✅ Uniqueness enforced")
```

**DoD:**
- ✅ Uniqueness check functional
- ✅ Auto-enforcement removes duplicate content
- ✅ Diagram generation triggered on enforcement
- ✅ Audit logging for all actions

---

### Phase 6: Integration & Testing
**Duration:** 4 hours  
**Dependencies:** All previous phases

**Tasks:**

#### Task 6.1: End-to-End Orchestrator Test
```bash
# Test full documentation orchestrator pipeline
python -m src.main "standardize architecture/index.html with glassmorphism"

# Expected flow:
# 1. Pre-flight validation (checks inline styles, template compliance)
# 2. State query (loads previous standardization state)
# 3. Inline removal (if needed)
# 4. CSS application (glassmorphism classes)
# 5. Validator execution (template compliance, margins, logo, uniqueness)
# 6. Diagram generation (9+ diagrams)
# 7. State persistence (saves to html-standardization-state.json)
# 8. Audit logging (all actions logged to logs/cortex-audit/documentation/)
```

**Validation Criteria:**
- ✅ Zero inline styles remaining
- ✅ All validators pass
- ✅ 9+ diagrams generated
- ✅ Uniqueness score <30%
- ✅ Audit log contains all events
- ✅ Git checkpoint created

**DoD:**
- ✅ Full pipeline tested successfully
- ✅ All validators pass
- ✅ Audit logs generated correctly
- ✅ Performance <2 minutes for full page standardization

#### Task 6.2: Toolkit CLI Test Suite
```python
# tests/toolkit/test_cli.py
import pytest
from click.testing import CliRunner
from cortex_toolkit.cli import cli

def test_remove_inline_styles():
    runner = CliRunner()
    result = runner.invoke(cli, ['docs', 'remove-inline-styles', 'test-page.html'])
    assert result.exit_code == 0
    assert 'inline styles removed' in result.output

def test_validate_template_compliance():
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', 'template-compliance', 'docs/orchestrators/index.html'])
    assert result.exit_code == 0
    assert '✅ PASS' in result.output

def test_generate_diagrams():
    runner = CliRunner()
    result = runner.invoke(cli, ['docs', 'generate-diagrams', '--target', 'architecture'])
    assert result.exit_code == 0
    assert '9 diagrams generated' in result.output
```

**DoD:**
- ✅ Test suite covers all CLI commands
- ✅ >90% code coverage
- ✅ Integration tests with real files

---

## 🔄 Rollback Plan

### Rollback Triggers
- Critical validator failures (>50% of pages fail)
- Performance degradation (>5 minutes per page)
- Audit logging failures (logs not persisted)
- Toolkit integration breaks existing workflows

### Rollback Steps
1. Restore backup: `cortex-brain/archives/plans/html-glassmorphism-alignment-20260106-064538/`
2. Revert orchestrator manifest to v1.0
3. Restore scattered scripts to `scripts/` directory
4. Remove toolkit orchestrator registration from master-orchestrator.yaml
5. Clear audit logs: `rm -rf logs/cortex-audit/documentation/`
6. Restore HTML state: `git checkout docs/architecture/index.html docs/orchestrators/index.html`

---

## 📊 Metrics & KPIs

### Compliance Metrics
- **Template Compliance Rate:** Target >95%
- **Inline Style Count:** Target 0 (zero tolerance)
- **Validator Pass Rate:** Target 100% for critical validators
- **Uniqueness Score:** Target <30% overlap

### Performance Metrics
- **Page Standardization Time:** Target <2 minutes
- **Diagram Generation Time:** Target <30 seconds per diagram
- **Validator Execution Time:** Target <5 seconds per page

### Audit Metrics
- **Event Logging Rate:** 100% of actions logged
- **Log Persistence Rate:** 100% (no lost logs)
- **Audit Query Response Time:** <100ms

---

## 📚 Documentation Deliverables

1. **Orchestrator Documentation**
   - `cortex-brain/documents/orchestrators/documentation-orchestrator-v2.md`
   - Usage examples
   - API reference
   - Troubleshooting guide

2. **Validators Documentation**
   - `cortex-brain/documents/validators/template-compliance-validator.md`
   - `cortex-brain/documents/validators/uniqueness-validator.md`
   - Validation criteria reference
   - Custom validator development guide

3. **Toolkit Documentation**
   - `cortex-brain/documents/orchestrators/toolkit-orchestrator.md`
   - CLI command reference
   - Script migration guide
   - Centralization benefits analysis

4. **Audit Logging Guide**
   - `cortex-brain/documents/orchestrators/audit-logging-integration.md`
   - Event types reference
   - Metrics catalog
   - Log analysis examples

---

## 🔗 Dependencies

### Internal Dependencies
- ✅ **Master Orchestrator v5.0** - Routing and intent classification
- ✅ **Audit Logger** (`src/orchestrators/audit_logger.py`) - Event tracking
- ✅ **Brain Protection Rules (SKULL)** - PYTHON_ONLY_GENERATION enforcement
- ✅ **Knowledge Base** - Tier 0, 2, 3 inheritance
- ⚠️ **BaseOrchestrator v6** - Universal orchestrator foundation (Phase P02 of cortex5-remediation)
  - **Status:** Planned in cortex5-remediation epic
  - **Documentation:** `cortex-brain/documents/planning/active/cortex5-remediation/architecture/BASE-ORCHESTRATOR-V6-SPECIFICATION.md`
  - **Impact:** docs-orchestrator-v2 will extend BaseOrchestrator when Phase P02 completes
  - **Benefits:** Automatic SKULL enforcement, audit logging, knowledge integration, SOLID/DRY compliance
  - **Current:** Orchestrator implements governance/audit manually; will inherit from BaseOrchestrator post-P02

### External Dependencies
- ✅ **Python 3.11+** - Core runtime
- ✅ **BeautifulSoup4** - HTML parsing
- ✅ **Click** - CLI framework
- ✅ **Jinja2** - Template rendering
- ⚠️ **Mermaid CLI** - Diagram generation (`npm install -g @mermaid-js/mermaid-cli`)
- ⚠️ **D3.js** - Interactive diagrams (included via CDN)
- ⚠️ **scikit-learn** - TF-IDF uniqueness validation (`pip install scikit-learn`)

---

## 🎓 Knowledge Transfer

### Key Concepts
1. **State-Aware Orchestration:** Tracks previous standardization attempts to avoid redundant work
2. **Validator Registry Pattern:** Extensible validation framework with priority-based execution
3. **Audit-First Architecture:** Every action logged before execution (rollback safety)
4. **Centralized Tooling:** Single source of truth for all documentation utilities
5. **Uniqueness Enforcement:** Automated content differentiation between Level 1 pages

### Training Materials
- Workshop: "Building Custom Validators for CORTEX Orchestrators"
- Tutorial: "Using the Toolkit CLI for Documentation Maintenance"
- Demo: "End-to-End Documentation Standardization Pipeline"

---

## 📅 Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Phase 1: Validators Registry | 4 hours | 2026-01-06 | 2026-01-06 | 🔵 Planned |
| Phase 2: Audit Logger Integration | 3 hours | 2026-01-06 | 2026-01-06 | 🔵 Planned |
| Phase 3: Orchestrator Manifest Enhancement | 2 hours | 2026-01-06 | 2026-01-06 | 🔵 Planned |
| Phase 4: Centralized Toolkit Development | 5 hours | 2026-01-06 | 2026-01-07 | 🔵 Planned |
| Phase 5: Architecture Uniqueness Implementation | 6 hours | 2026-01-07 | 2026-01-07 | 🔵 Planned |
| Phase 6: Integration & Testing | 4 hours | 2026-01-07 | 2026-01-07 | 🔵 Planned |

**Total Duration:** 24 hours (3 working days)

---

## 🎉 Success Celebration

Upon completion:
- ✅ 95%+ of Level 1 pages pass all validators
- ✅ Zero inline styles across documentation site
- ✅ 9+ architectural diagrams on architecture page
- ✅ <30% content overlap between architecture and orchestrators pages
- ✅ 100% audit logging coverage
- ✅ All scattered scripts centralized in toolkit
- ✅ Single unified CLI for all documentation operations

**Commit Message Format:**
```
feat(docs): documentation orchestrator v2.0 with validators and audit logging

ORCHESTRATOR ENHANCEMENTS:
- 5 validators: template compliance, margins, logo placement, inline styles, uniqueness
- Full audit logging integration (every action tracked)
- YAML-based manifest with 6-phase execution pipeline
- State-aware standardization (tracks previous applications)

CENTRALIZED TOOLKIT:
- Moved 9 scattered scripts to cortex-toolkit/
- Unified CLI interface (cortex-toolkit command)
- Category-based organization (documentation, planning, routing)

LEVEL 1 UNIQUENESS:
- Architecture page: 9+ diagrams (Mermaid + D3.js)
- Content differentiation: Architecture=HOW_BUILT, Orchestrators=WHAT_DOES
- Automated duplicate content removal
- Visual overlap <30% enforcement

FILES CREATED:
- cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml (enhanced)
- cortex-toolkit/validators/*.py (5 validators)
- cortex-toolkit/orchestrators/documentation/*.py (5 scripts)
- cortex-toolkit/cli.py (unified CLI)
- cortex-brain/documents/planning/active/docs-orchestrator-v2/

SUCCESS METRICS:
- Compliance rate: 96% (target >95%)
- Uniqueness score: 27% (target <30%)
- Audit coverage: 100%
- Centralization: 0 scattered scripts

REFERENCE: chat01.md, cortex-upgrade.prompt.md Phase 7.5-12
```

---

**Plan Version:** 2.0.0  
**Last Updated:** 2026-01-06  
**Next Review:** After Phase 3 completion
