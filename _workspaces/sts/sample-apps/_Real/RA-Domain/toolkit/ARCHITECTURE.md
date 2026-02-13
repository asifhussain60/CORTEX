# RA Domain Analysis Toolkit: Unified Architecture

**Version:** 1.0  
**Created:** December 11, 2025  
**Author:** Asif Hussain  
**Purpose:** Integrate CORTEX dashboard collector pattern with RA domain analysis

---

## 🎯 Architecture Overview

**Design Philosophy:** Extend proven CORTEX dashboard collector architecture to support deep domain analysis with AST scanning and regulatory validation.

**Key Innovation:** Combine real-time data collection (CORTEX pattern) with batch-oriented AST analysis (RA domain pattern) into unified toolkit.

---

## 🏗️ System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│  - Admin Dashboard (repository selector, progress tracking)     │
│  - CLI Commands (powershell/python scripts)                     │
│  - Progress Reports (markdown + JSON)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                           │
│  - RADomainOrchestrator (master coordinator)                    │
│  - BatchExecutor (20-batch workflow manager)                    │
│  - DataEnrichmentPipeline (Phase 7→8→9 pattern)                │
│  - ProgressTracker (real-time status updates)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DATA COLLECTION LAYER                          │
│  ┌────────────────────┬────────────────────┬──────────────────┐ │
│  │  AST COLLECTORS    │  TEST COLLECTORS   │  REGULATORY      │ │
│  │  - EntityCollector │  - CoverageCollector│  - RegulatoryAgencyValidator │ │
│  │  - DTOCollector    │  - TestMapCollector│  - PrivacyRegulationChecker │ │
│  │  - ServiceCollector│  - GapAnalyzer     │  - PCIDSSScanner│ │
│  │  - InterfaceColletr│  - ScenarioGen     │  - ComplianceRpt│ │
│  └────────────────────┴────────────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                           │
│  - cortex_brain/dashboards/data/repos/{repo_name}/              │
│    ├── ast-outputs/        # AST scan results (JSON)            │
│    ├── test-coverage/      # Coverage reports                   │
│    ├── regulatory/         # Compliance findings                │
│    ├── business-logic/     # Extracted rules                    │
│    └── dashboard.json      # Template-ready data                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Design

### 1. Base Collector (Inherited from CORTEX)

**Source:** `src/dashboard/data/base_collector.py`

**Features:**
- Abstract base class for all collectors
- File I/O helpers (`_file_exists`, `_read_file`)
- Safe parsing (JSON, YAML, XML)
- Logging infrastructure
- Error handling

**RA Domain Extension:**
```python
class RABaseCollector(BaseDataCollector):
    """Extended base collector for RA domain analysis"""
    
    def __init__(self, repo_path: Path, output_dir: Path):
        super().__init__(repo_path)
        self.output_dir = output_dir
        self.ast_parser = TreeSitterParser('c_sharp')  # NEW
        self.regulatory_rules = self._load_regulatory_rules()  # NEW
    
    def _parse_csharp_file(self, file_path: Path) -> Dict[str, Any]:
        """NEW: Parse C# file using tree-sitter AST"""
        pass
    
    def _validate_compliance(self, entity: Dict) -> List[str]:
        """NEW: Validate against RegulatoryAgency/PrivacyRegulation/PaymentSecurity rules"""
        pass
```

### 2. AST Collectors (NEW - Domain-Specific)

**Pattern:** Batch-oriented collectors for systematic code analysis

#### EntityCollector
```python
class EntityCollector(RABaseCollector):
    """
    Extract entity metadata from C# domain models
    
    Batch: 3.1-3.3 (30 entities, 10 per batch)
    Output: ast-outputs/entities-batch-{n}.json
    """
    
    def collect_batch(self, start_idx: int, end_idx: int) -> Dict[str, Any]:
        entities = []
        for file in self._get_entity_files()[start_idx:end_idx]:
            entity_data = {
                'name': self._extract_class_name(file),
                'namespace': self._extract_namespace(file),
                'properties': self._extract_properties(file),
                'relationships': self._extract_relationships(file),
                'compliance_flags': self._check_phi_pci_fields(file)  # PrivacyRegulation/PCI
            }
            entities.append(entity_data)
        
        return {
            'batch': f'3.{(start_idx // 10) + 1}',
            'entities': entities,
            'count': len(entities),
            'compliance_issues': self._aggregate_compliance_issues(entities)
        }
```

#### ServiceCollector
```python
class ServiceCollector(RABaseCollector):
    """
    Extract service methods and business logic
    
    Batch: 5.1-5.2 (19 services, 10 per batch)
    Output: ast-outputs/services-batch-{n}.json
    
    Special Focus: ExampleDomainService (20 methods)
    """
    
    def collect_service_methods(self, service_file: Path) -> Dict[str, Any]:
        methods = []
        tree = self.ast_parser.parse_file(service_file)
        
        for method_node in self._find_methods(tree):
            method_data = {
                'name': self._get_method_name(method_node),
                'signature': self._get_signature(method_node),
                'parameters': self._extract_parameters(method_node),
                'return_type': self._get_return_type(method_node),
                'business_logic': self._extract_logic_summary(method_node),
                'regulatory_keywords': self._scan_for_irs_keywords(method_node)
            }
            methods.append(method_data)
        
        return {
            'service': service_file.stem,
            'methods': methods,
            'regulatory_analysis': self._analyze_regulatory_compliance(methods)
        }
```

### 3. Test Coverage Collectors (NEW)

#### CoverageAnalyzer
```python
class CoverageAnalyzer(RABaseCollector):
    """
    Map test files to production code
    
    Batch: 11 (4 test projects)
    Output: test-coverage/coverage-report.json
    """
    
    def analyze_coverage(self) -> Dict[str, Any]:
        # 1. Discover test files
        test_files = self._scan_test_projects()
        
        # 2. Extract test methods
        test_map = self._map_tests_to_production_code(test_files)
        
        # 3. Calculate coverage by layer
        coverage = {
            'domain_layer': self._calc_domain_coverage(test_map),
            'service_layer': self._calc_service_coverage(test_map),
            'job_layer': self._calc_job_coverage(test_map)
        }
        
        # 4. Identify gaps
        gaps = self._identify_untested_critical_paths(coverage)
        
        # 5. Generate regulatory test scenarios
        scenarios = self._generate_regulatory_scenarios()
        
        return {
            'coverage': coverage,
            'gaps': gaps,
            'scenarios': scenarios,
            'recommendations': self._prioritize_test_creation(gaps)
        }
```

### 4. Regulatory Validators (NEW)

#### RegulatoryAgencyComplianceValidator
```python
class RegulatoryAgencyComplianceValidator(RABaseCollector):
    """
    Validate RegulatoryAgency tax code compliance
    
    Batch: 2.5 + ongoing validation
    Output: regulatory/irs-compliance-report.json
    
    Checks:
    - Contribution limits (FlexAccount: $3,200, HealthSavings: $4,150/$8,300)
    - Rollover limits (FlexAccount: $640 max, HealthSavings: unlimited)
    - Grace period mutual exclusion
    - Qualified expense validation
    """
    
    def validate_contribution_limits(self) -> List[Dict]:
        issues = []
        
        # Scan for hardcoded limits
        limit_checks = self._scan_for_limit_validation_code()
        
        for check in limit_checks:
            if check['fsa_limit'] != 3200:
                issues.append({
                    'severity': 'P0',
                    'type': 'RegulatoryAgency_LIMIT_MISMATCH',
                    'expected': 3200,
                    'found': check['fsa_limit'],
                    'file': check['file'],
                    'line': check['line']
                })
        
        return issues
```

---

## 📊 Data Flow Architecture

### Phase-Based Execution (Inspired by Dashboard Orchestrator)

**Pattern:** Sequential phases with data enrichment between stages

```python
class RADomainOrchestrator:
    """
    Master orchestrator for RA domain analysis
    
    Execution Flow:
    1. Phase 1: Repository scan (Batch 1)
    2. Phase 2: Business domain mapping (Batch 2)
    3. Phase 3: Entity extraction (Batches 3.1-3.3)
    4. Phase 4: DTO extraction (Batches 4.1-4.5)
    5. Phase 5: Service extraction (Batches 5.1-5.2)
    6. Phase 6: Test coverage analysis (Batch 11)
    7. Phase 7: Regulatory validation (Batch 2.5 + ongoing)
    8. Phase 8: Business logic synthesis (Batches 8-14)
    9. Phase 9: Dashboard integration (Batch 20)
    """
    
    def execute_all_phases(self) -> Dict[str, Any]:
        print("🚀 Starting RA Domain Analysis...")
        
        # Phase 1: Structural Analysis
        print("\n📊 Phase 1: Repository Metrics")
        structural_data = StructuralAnalyzer(self.repo_path).collect()
        self._save_phase_output(1, structural_data)
        
        # Phase 2: Business Domain Mapping
        print("\n🎯 Phase 2: Business Domain Mapping")
        domain_data = BusinessDomainMapper(self.repo_path).collect()
        self._save_phase_output(2, domain_data)
        
        # Phase 3: Entity Extraction (batched)
        print("\n🗃️ Phase 3: Entity Extraction (3 batches)")
        entity_data = []
        for batch_num in range(1, 4):
            start_idx = (batch_num - 1) * 10
            end_idx = start_idx + 10
            batch_data = EntityCollector(self.repo_path, self.output_dir).collect_batch(start_idx, end_idx)
            entity_data.append(batch_data)
            self._save_batch_output(3, batch_num, batch_data)
        
        # ... (continue for all 20 batches)
        
        # Final: Generate dashboard.json
        print("\n📊 Generating dashboard.json...")
        dashboard_data = self._consolidate_all_phases()
        self._save_dashboard_json(dashboard_data)
        
        return dashboard_data
```

---

## 🗂️ Data Storage Architecture

**Pattern:** Aligned with CORTEX dashboard data structure

```
cortex_brain/dashboards/data/repos/Product.Example/
├── dashboard.json                      # Master dashboard data (template-ready)
├── registry-metadata.json              # Repository metadata
│
├── ast-outputs/                        # AST scan results by batch
│   ├── structural-analysis.json        # Batch 1
│   ├── business-domain-map.json        # Batch 2
│   ├── entities-batch-1.json           # Batch 3.1
│   ├── entities-batch-2.json           # Batch 3.2
│   ├── entities-batch-3.json           # Batch 3.3
│   ├── dtos-batch-{1-5}.json           # Batch 4.1-4.5
│   ├── services-batch-{1-2}.json       # Batch 5.1-5.2
│   └── rollover-service-methods.json  # Deep dive
│
├── test-coverage/                      # Test analysis results
│   ├── coverage-report.json            # Overall coverage
│   ├── coverage-by-layer.json          # Domain/Service/Job breakdown
│   ├── untested-critical-paths.json    # Risk assessment
│   └── regulatory-test-scenarios.json  # 40+ test cases
│
├── regulatory/                         # Compliance validation
│   ├── irs-compliance-report.json      # RegulatoryAgency Pub 969, IRC §223
│   ├── hipaa-audit-findings.json       # PrivacyRegulation §164.312
│   ├── pci-dss-scan-results.json       # PaymentSecurity Req 3.2/3.4
│   └── p0-issues-tracking.json         # Critical gaps
│
├── business-logic/                     # Extracted business rules
│   ├── rollover-rules-simplified.md   # Decision trees
│   ├── plan-type-matrix.json           # FlexAccount/HealthSavings/HealthReimbursement/DependentCare
│   ├── workflow-definitions.json       # 7 core workflows
│   └── business-glossary.json          # 80+ terms
│
└── reports/                            # Executive summaries
    ├── executive-summary.md            # EXECUTIVE-SUMMARY-BATCHES-1-7.md
    ├── progress-tracker.json           # Batch completion status
    └── ast-enhancement-backlog.json    # Scanner improvements needed
```

---

## 🔄 Integration with CORTEX Dashboard

### Repository Registration

**Pattern:** Auto-discovery + manual registration

```python
# src/operations/modules/dashboard/repository_discovery_service.py

def discover_and_register_ra_domain():
    """
    Discover RA domain analysis results and register with dashboard
    """
    ra_domain_path = Path('C:/PROJECTS/Product.Example')
    output_path = Path('cortex_brain/dashboards/data/repos/Product.Example')
    
    # Check if analysis exists
    if (output_path / 'dashboard.json').exists():
        registry_entry = {
            'id': 'ra-domain-analysis',
            'name': 'Product.Example',
            'type': 'external_csharp',
            'path': str(ra_domain_path),
            'dashboard_data': str(output_path),
            'analysis_version': '2.0',
            'batches_completed': _count_completed_batches(output_path),
            'last_updated': _get_last_update_time(output_path),
            'capabilities': [
                'ast_analysis',
                'test_coverage',
                'regulatory_compliance',
                'business_logic_extraction'
            ]
        }
        
        return registry_entry
    
    return None
```

### Dashboard Data Transformation

**Pattern:** Transform RA domain data into dashboard.json format

```python
def transform_ra_data_to_dashboard_format(ra_output_dir: Path) -> Dict[str, Any]:
    """
    Transform RA domain analysis results into dashboard.json format
    
    Maps:
    - ast-outputs/*.json → dashboard['code_structure']
    - test-coverage/*.json → dashboard['test_quality']
    - regulatory/*.json → dashboard['compliance']
    - business-logic/*.json → dashboard['business_capabilities']
    """
    
    dashboard_data = {
        'metadata': {
            'repository': 'Product.Example',
            'analysis_type': 'ra_domain_deep_dive',
            'generated_at': datetime.now().isoformat(),
            'batches_completed': _count_completed_batches(ra_output_dir)
        },
        
        'overview': {
            'total_files': 302,
            'csharp_files': 256,
            'total_projects': 12,
            'application_projects': 5,
            'library_projects': 2,
            'test_projects': 4
        },
        
        'code_structure': {
            'entities': _load_json(ra_output_dir / 'ast-outputs' / 'entities-*.json'),
            'dtos': _load_json(ra_output_dir / 'ast-outputs' / 'dtos-*.json'),
            'services': _load_json(ra_output_dir / 'ast-outputs' / 'services-*.json'),
            'interfaces': _load_json(ra_output_dir / 'ast-outputs' / 'interfaces.json')
        },
        
        'test_quality': _load_json(ra_output_dir / 'test-coverage' / 'coverage-report.json'),
        
        'compliance': {
            'irs': _load_json(ra_output_dir / 'regulatory' / 'irs-compliance-report.json'),
            'hipaa': _load_json(ra_output_dir / 'regulatory' / 'hipaa-audit-findings.json'),
            'pci_dss': _load_json(ra_output_dir / 'regulatory' / 'pci-dss-scan-results.json'),
            'p0_issues': _load_json(ra_output_dir / 'regulatory' / 'p0-issues-tracking.json')
        },
        
        'business_capabilities': _load_json(ra_output_dir / 'business-logic' / 'workflow-definitions.json'),
        
        'recommendations': _generate_recommendations(ra_output_dir)
    }
    
    return dashboard_data
```

---

## 🚀 Execution Methods

### 1. CLI Execution (Quick Scan)

```powershell
# Quick structural scan (Batch 1 only)
.\01_quick_scan.ps1 -RepoPath "C:\PROJECTS\Product.Example"

# Full analysis (all 20 batches)
python 06_master_orchestrator.py --repo-path "C:\PROJECTS\Product.Example" --execute-all

# Specific batch execution
python 06_master_orchestrator.py --repo-path "C:\PROJECTS\Product.Example" --batch 11
```

### 2. Admin Dashboard Integration

```python
# Launch admin dashboard with RA domain selector
python -m src.orchestrators.dashboard_launcher --source "Product.Example"

# Dashboard will show:
# - Progress tracker (3/20 batches complete)
# - AST outputs (entities, DTOs, services)
# - Test coverage metrics
# - Regulatory compliance status
# - Business logic visualizations
```

### 3. Programmatic API

```python
from src.operations.ra_domain.orchestrator import RADomainOrchestrator

# Create orchestrator
orchestrator = RADomainOrchestrator(
    repo_path='C:/PROJECTS/Product.Example',
    output_dir='cortex_brain/dashboards/data/repos/Product.Example'
)

# Execute specific phase
entity_data = orchestrator.execute_phase(3)  # Entity extraction

# Execute all phases
dashboard_data = orchestrator.execute_all_phases()

# Query results
coverage = orchestrator.get_test_coverage()
compliance_issues = orchestrator.get_p0_compliance_issues()
business_rules = orchestrator.get_business_logic_summary()
```

---

## 📈 Progress Tracking

### Real-Time Progress Updates

**Pattern:** Same as CORTEX dashboard progress tracking

```python
class ProgressTracker:
    """
    Track batch execution progress in real-time
    
    Persists to: cortex_brain/dashboards/data/repos/{repo}/reports/progress-tracker.json
    """
    
    def update_batch_status(self, batch_num: int, status: str, duration_min: float):
        progress = self._load_progress()
        
        progress['batches'][batch_num] = {
            'status': status,  # 'pending', 'running', 'complete', 'failed'
            'duration_min': duration_min,
            'completed_at': datetime.now().isoformat() if status == 'complete' else None
        }
        
        progress['overall'] = {
            'completed': sum(1 for b in progress['batches'].values() if b['status'] == 'complete'),
            'total': 20,
            'percent': (progress['completed'] / 20) * 100,
            'estimated_remaining_hours': self._calculate_remaining_time(progress)
        }
        
        self._save_progress(progress)
        self._update_dashboard_json(progress)
```

---

## 🔧 Configuration

### Toolkit Configuration

```yaml
# cortex_brain/admin/RA-Domain/toolkit/config/analysis-config.yaml

repository:
  path: "C:/PROJECTS/Product.Example"
  name: "Product.Example"
  type: "external_csharp"

output:
  base_dir: "cortex_brain/dashboards/data/repos/Product.Example"
  formats:
    - json
    - markdown
  
batches:
  enabled: [1, 2, 2.5, 3.1, 3.2, 3.3, 7, 11, 13, 20]  # Prioritized batches
  batch_size:
    entities: 10
    dtos: 9
    services: 10
  
ast_parser:
  language: "c_sharp"
  max_file_size_mb: 5
  timeout_seconds: 30
  
regulatory:
  enabled_validators:
    - irs_compliance
    - hipaa_audit
    - pci_dss_scan
  
  irs_limits:
    fsa_annual_max: 3200
    fsa_carryover_max: 640
    hsa_individual_max: 4150
    hsa_family_max: 8300
    dependent_care_max: 5000
  
test_coverage:
  minimum_threshold: 80
  critical_paths_required: true
  
dashboard_integration:
  auto_register: true
  auto_transform: true
  refresh_interval_minutes: 5
```

---

## 🎯 Key Design Decisions

### 1. **Inheritance from CORTEX Dashboard Pattern**
- **Rationale:** Proven architecture with 15+ collectors, orchestration, data storage
- **Benefits:** Reuse infrastructure, consistent data format, admin dashboard integration

### 2. **Batch-Oriented Execution**
- **Rationale:** Large codebase (302 files) requires systematic processing
- **Benefits:** Progress tracking, resumability, controlled memory usage

### 3. **Three-Layer Data Model**
- **AST Outputs:** Raw parsed data (machine-readable)
- **Aggregated Reports:** Synthesized insights (human + machine)
- **Dashboard JSON:** Template-ready visualization data

### 4. **Regulatory Validation as First-Class Concern**
- **Rationale:** Healthcare domain requires RegulatoryAgency/PrivacyRegulation/PaymentSecurity compliance
- **Benefits:** P0 issue detection, risk mitigation, audit readiness

### 5. **Dashboard Integration via Registry**
- **Rationale:** Multi-repository dashboard requires standardized registration
- **Benefits:** Dropdown selector, auto-discovery, unified UI

---

## 📈 Business Value Enhancements (v1.1)

**Based on actual repository scan results - provides immediate ROI for management**

### 1. Team Onboarding Accelerator (NEW)

**Problem:** New developers need 13+ hours to understand RA codebase, causing project delays.

**Solution:** Auto-generated onboarding package

```python
class OnboardingAcceleratorCollector(RABaseCollector):
    """
    Generate comprehensive onboarding materials
    
    Business Value:
    - Reduces ramp-up time from 13 hours to 4 hours (70% improvement)
    - Decreases time-to-first-commit from 2 weeks to 3 days
    - Enables managers to onboard 3x faster
    
    Outputs:
    - onboarding/new-developer-guide.md      # Step-by-step learning path
    - onboarding/key-files-reference.md      # Top 20 files to read first
    - onboarding/terminology-guide.md        # 80+ business terms
    - onboarding/who-to-ask.md               # Knowledge ownership map
    - onboarding/architecture-overview.md    # System design explanation
    """
    
    def generate_onboarding_package(self) -> Dict[str, Any]:
        return {
            'learning_path': [
                {'order': 1, 'topic': 'Repository Structure', 'time': '1 hr'},
                {'order': 2, 'topic': 'Domain Model (FlexAccount/HealthSavings/HealthReimbursement)', 'time': '3 hrs'},
                {'order': 3, 'topic': 'ExampleDomainService', 'time': '4 hrs'},
                {'order': 4, 'topic': 'Testing Strategy', 'time': '2 hrs'},
                {'order': 5, 'topic': 'NServiceBus Integration', 'time': '3 hrs'}
            ],
            'key_files': self._prioritize_reading_order(),
            'quick_wins': self._identify_good_first_tasks(),
            'estimated_ramp_up': '4 hours (70% reduction)'
        }
```

**Manager Dashboard Metrics:**
- Developer velocity: Days to first PR
- Knowledge coverage: % of codebase understood
- Onboarding completion: 5-step checklist

---

### 2. Test Coverage Intelligence (CRITICAL - 8.6% vs 90% target)

**Problem:** Coverage at 8.6% (should be 90%) - **HIGH PRODUCTION RISK**

**Solution:** Intelligent test gap analyzer with ROI prioritization

```python
class TestCoverageIntelligenceCollector(RABaseCollector):
    """
    Prioritize test creation by business impact
    
    Business Value:
    - Identifies 220 untested files (81.4% gap to close)
    - Ranks by regulatory risk (RegulatoryAgency/PrivacyRegulation violations)
    - Estimates defect prevention value ($50k-$500k/year)
    
    Outputs:
    - test-coverage/gap-analysis-prioritized.json
    - test-coverage/roi-by-test-scenario.json
    - test-coverage/regulatory-risk-heatmap.json
    - test-coverage/sprint-test-plan.md (batched goals)
    """
    
    def prioritize_test_gaps(self) -> List[Dict]:
        """
        Prioritize untested code by business impact
        
        Returns gaps ranked by:
        1. Regulatory risk (RegulatoryAgency rollover = P0)
        2. Production defect history
        3. Code complexity
        4. User-facing impact
        """
        
        gaps = []
        
        # P0: Rollover logic (RegulatoryAgency compliance risk)
        gaps.append({
            'priority': 'P0',
            'component': 'ExampleDomainService',
            'risk': 'RegulatoryAgency non-compliance, $500k penalty exposure',
            'current_coverage': '0%',
            'target_coverage': '100%',
            'est_test_effort_hours': 16,
            'roi': '$500k risk mitigation / 16 hrs = $31k/hr'
        })
        
        # P0: Balance calculations (financial accuracy)
        gaps.append({
            'priority': 'P0',
            'component': 'ExampleBalanceService',
            'risk': 'Incorrect customer balances, refund liability',
            'current_coverage': '10%',
            'target_coverage': '95%',
            'est_test_effort_hours': 12,
            'roi': '$200k risk mitigation / 12 hrs = $16k/hr'
        })
        
        return sorted(gaps, key=lambda x: self._calculate_roi(x), reverse=True)
```

**Manager Dashboard Metrics:**
- Coverage trend: Weekly % increase
- Risk mitigation: $ value of defects prevented
- Sprint velocity: Tests created per sprint
- Regulatory compliance: % of P0 scenarios covered

**Target Achievement Plan:**
- **Sprint 1-2:** P0 regulatory scenarios (Rollover, Balance) → 30% coverage
- **Sprint 3-4:** P1 financial calculations (Requests, Card) → 60% coverage
- **Sprint 5-6:** P2 business logic (Plan Management) → 90% coverage

---

### 3. Complexity & Technical Debt Tracker

**Problem:** 10 large files (>500 LOC), 3 classes with 20+ methods - **MAINTENANCE RISK**

**Solution:** Automated complexity monitoring with refactoring ROI

```python
class ComplexityIntelligenceCollector(RABaseCollector):
    """
    Track complexity trends and refactoring opportunities
    
    Business Value:
    - Identifies top 10 refactoring candidates by ROI
    - Estimates maintenance cost reduction ($30k-$100k/year)
    - Prevents "Big Ball of Mud" anti-pattern
    
    Outputs:
    - complexity/hotspot-heatmap.json
    - complexity/refactoring-roi-analysis.md
    - complexity/technical-debt-register.json
    - complexity/complexity-trend.json (historical)
    """
    
    def analyze_refactoring_roi(self) -> List[Dict]:
        return [
            {
                'file': 'ExampleDomainService.cs',
                'lines': 717,
                'methods': 20,
                'cyclomatic_complexity': 45,
                'maintenance_cost_annual': '$15k',
                'refactoring_effort_hours': 40,
                'post_refactor_maintenance_cost': '$5k',
                'annual_savings': '$10k',
                'roi': '250%',
                'recommendation': 'Extract 5 sub-services (Validation, Calculation, Persistence, Events, Reporting)'
            }
        ]
```

**Manager Dashboard Metrics:**
- Complexity score: 0-100 (current: 65)
- Tech debt hours: Estimated refactoring backlog
- Velocity impact: % slowdown from complexity
- Defect correlation: Bugs per complexity point

---

### 4. Knowledge Ownership Map (Reduces Bus Factor)

**Problem:** Unknown code ownership creates knowledge silos and delays

**Solution:** Auto-generated knowledge map from git history + code analysis

```python
class KnowledgeOwnershipCollector(RABaseCollector):
    """
    Map code ownership and identify knowledge gaps
    
    Business Value:
    - Identifies single points of failure (bus factor = 1)
    - Enables cross-training plans
    - Reduces code review bottlenecks
    
    Outputs:
    - knowledge/ownership-map.json
    - knowledge/bus-factor-analysis.md
    - knowledge/cross-training-plan.md
    - knowledge/code-review-matrix.json
    """
    
    def generate_ownership_map(self) -> Dict[str, Any]:
        return {
            'components': [
                {
                    'name': 'Rollover Logic',
                    'primary_owner': 'Developer A (80% commits)',
                    'backup_owner': 'None',
                    'bus_factor': 1,  # CRITICAL
                    'risk': 'HIGH - No backup knowledge',
                    'recommendation': 'Cross-train Developer B in Q1 2025'
                },
                {
                    'name': 'Request Processing',
                    'primary_owner': 'Developer C (60% commits)',
                    'backup_owner': 'Developer D (30% commits)',
                    'bus_factor': 2,  # ACCEPTABLE
                    'risk': 'MEDIUM'
                }
            ],
            'cross_training_matrix': self._generate_training_matrix()
        }
```

**Manager Dashboard Metrics:**
- Bus factor: # of people who can modify each component
- Knowledge coverage: % of codebase with 2+ experts
- Review bottlenecks: Days waiting for SME review
- Onboarding pipeline: New developers per component

---

### 5. Business Function Catalog (Product Alignment)

**Problem:** No single source of truth for "what does this system do?"

**Solution:** Auto-generated capability catalog with traceability

```python
class BusinessFunctionCatalogCollector(RABaseCollector):
    """
    Generate product-aligned capability catalog
    
    Business Value:
    - Aligns engineering with product roadmap
    - Enables accurate effort estimation
    - Facilitates feature vs. bug prioritization
    
    Outputs:
    - business-functions/capability-catalog.md
    - business-functions/feature-code-map.json
    - business-functions/roadmap-impact-analysis.md
    - business-functions/api-contracts-summary.md
    """
    
    def generate_catalog(self) -> Dict[str, Any]:
        return {
            'capabilities': [
                {
                    'name': 'Year-End Rollover Processing',
                    'services': ['ExampleDomainService', 'ExampleSharedService'],
                    'background_jobs': ['Rollover.Jobs'],
                    'domain_events': ['BalanceChangedEvent', 'PlanYearEndEvent'],
                    'test_coverage': '8%',  # CRITICAL GAP
                    'complexity': 'HIGH (717 LOC)',
                    'regulatory_compliance': 'RegulatoryAgency Pub 969, IRC §223',
                    'product_alignment': 'Q1 2025 Roadmap - Automated Rollover v2'
                },
                {
                    'name': 'Request Processing',
                    'services': ['ExampleBalanceService'],
                    'background_jobs': [],
                    'test_coverage': '10%',
                    'product_alignment': 'Q2 2025 - Auto-Pay Enhancement'
                }
            ],
            'roadmap_traceability': self._map_roadmap_to_code()
        }
```

**Manager Dashboard Metrics:**
- Feature velocity: Story points per capability
- Code-to-product alignment: % of roadmap mapped
- Estimation accuracy: Planned vs. actual effort
- Technical debt impact: Velocity drag per capability

---

### 6. Documentation Quality Intelligence

**Problem:** Doc score 30/100, no README, only 11 XML comments

**Solution:** Auto-doc generator + quality gates

```python
class DocumentationIntelligenceCollector(RABaseCollector):
    """
    Generate missing docs and enforce quality gates
    
    Business Value:
    - Reduces support escalations (no internal docs)
    - Enables self-service onboarding
    - Improves code review efficiency
    
    Outputs:
    - docs/auto-generated-readme.md
    - docs/api-reference.md (from XML comments)
    - docs/missing-docs-report.md
    - docs/doc-quality-scorecard.json
    """
    
    def generate_documentation(self) -> Dict[str, Any]:
        return {
            'auto_generated_readme': self._generate_readme(),
            'missing_xml_comments': [
                'ExampleDomainService (20 methods undocumented)',
                'ExampleBalanceService (15 methods undocumented)'
            ],
            'quality_gates': {
                'min_xml_comment_coverage': '80%',
                'current_coverage': '15%',
                'gap': '65%',
                'recommended_sprint_goal': '+10% per sprint (reach 80% in 7 sprints)'
            }
        }
```

**Manager Dashboard Metrics:**
- Doc coverage: % of public APIs documented
- Doc freshness: Days since last update
- Support ticket correlation: Tickets per undocumented component
- Onboarding feedback: New dev satisfaction score

---

### 7. Integration Point Catalog (Risk Management)

**Problem:** Unknown external dependencies create deployment risk

**Solution:** Auto-discovered integration map with health monitoring

```python
class IntegrationCatalogCollector(RABaseCollector):
    """
    Map all external integrations and dependencies
    
    Business Value:
    - Prevents surprise outages
    - Enables dependency upgrade planning
    - Facilitates vendor risk assessment
    
    Outputs:
    - integrations/external-dependencies.json
    - integrations/nservicebus-event-map.json
    - integrations/database-schema-map.json
    - integrations/vendor-risk-register.md
    """
    
    def catalog_integrations(self) -> Dict[str, Any]:
        return {
            'messaging': {
                'platform': 'NServiceBus',
                'event_count': 1,  # Scanned: BalanceChangedEvent
                'handler_count': 1,
                'risk': 'MEDIUM - Limited event visibility'
            },
            'databases': {
                'contexts': ['ReimbursementAccountsContext'],
                'entity_count': 30,
                'migration_strategy': 'Entity Framework Code-First'
            },
            'external_libraries': {
                'total_packages': 45,  # Estimated from scan
                'security_alerts': 'TBD (requires NuGet audit)',
                'outdated_packages': 'TBD'
            }
        }
```

**Manager Dashboard Metrics:**
- Dependency health: % up-to-date packages
- Integration test coverage: % of integrations tested
- Vendor SLA compliance: Uptime per integration
- Upgrade readiness: Hours to upgrade dependencies

---

## 🎯 Enhanced Next Steps (Prioritized by Business Value)

### Phase 1: Critical Business Value (Week 1)

1. **Test Coverage Intelligence** (8 hours) - **HIGHEST ROI**
   - [ ] Implement TestCoverageIntelligenceCollector
   - [ ] Generate gap-analysis-prioritized.json
   - [ ] Create sprint test plan (P0 scenarios first)
   - **Business Impact:** $500k+ risk mitigation, regulatory compliance

2. **Team Onboarding Accelerator** (4 hours)
   - [ ] Implement OnboardingAcceleratorCollector
   - [ ] Generate new-developer-guide.md
   - [ ] Create key-files-reference.md
   - **Business Impact:** 70% faster ramp-up, 3x onboarding capacity

3. **Business Function Catalog** (4 hours)
   - [ ] Implement BusinessFunctionCatalogCollector
   - [ ] Map capabilities to code
   - [ ] Align with product roadmap
   - **Business Impact:** Better estimates, roadmap alignment

### Phase 2: Technical Sustainability (Week 2)

4. **Complexity Intelligence** (6 hours)
   - [ ] Implement ComplexityIntelligenceCollector
   - [ ] Generate refactoring-roi-analysis.md
   - [ ] Track technical debt register
   - **Business Impact:** $10k-$30k/year maintenance savings

5. **Documentation Quality** (4 hours)
   - [ ] Implement DocumentationIntelligenceCollector
   - [ ] Generate auto-readme
   - [ ] Enforce quality gates
   - **Business Impact:** Reduced support burden, faster reviews

### Phase 3: Risk Management (Week 3)

6. **Knowledge Ownership** (6 hours)
   - [ ] Implement KnowledgeOwnershipCollector (requires git history)
   - [ ] Generate bus-factor-analysis.md
   - [ ] Create cross-training-plan.md
   - **Business Impact:** Reduced bus factor, faster reviews

7. **Integration Catalog** (4 hours)
   - [ ] Implement IntegrationCatalogCollector
   - [ ] Map external dependencies
   - [ ] Assess vendor risk
   - **Business Impact:** Deployment risk reduction, upgrade planning

### Phase 4: OneDrive Site Publishing (Week 4)

8. **OneDrive Site Publisher** (8 hours) - **NEW**
   - [ ] Implement OneDriveSitePublisher
   - [ ] Generate executive dashboard (index.html)
   - [ ] Create manager scorecard pages
   - [ ] Build developer onboarding portal
   - [ ] Generate product catalog views
   - [ ] Auto-deploy to OneDrive sync folder
   - **Business Impact:** Executive visibility, stakeholder self-service, mobile access

**Total Effort:** 44 hours (2 weeks @ 22 hrs/week)

**Total Business Value:** $500k+ risk mitigation + $50k-$100k/year operational savings + executive transparency

---

## 📊 Manager Dashboard Template

**Weekly Scorecard (Auto-Generated)**

| Metric | Current | Target | Trend | Action |
|--------|---------|--------|-------|--------|
| **Test Coverage** | 8.6% | 90% | 📈 +5%/sprint | P0 scenarios in Sprint 1-2 |
| **Onboarding Time** | 13 hrs | 4 hrs | 📉 -3hrs | Use auto-guide |
| **Complexity Score** | 65/100 | <50/100 | → 0 | Refactor CarryoverService (Sprint 3) |
| **Doc Coverage** | 30% | 80% | 📈 +10%/sprint | Enforce XML comments in PRs |
| **Bus Factor** | 1 (Rollover) | 2+ | ⚠️ CRITICAL | Cross-train by EOQ |
| **Technical Debt** | 40 hrs | <20 hrs | 📉 -5hrs | 2 hrs/sprint refactoring |

---

## 🌐 OneDrive Site Publishing (Phase 4)

### Collector: OneDriveSitePublisher

**Purpose:** Transform analysis results into executive-friendly OneDrive pages

**Business Value:**
- **Executive Transparency:** Leadership views metrics without technical tools
- **Stakeholder Self-Service:** Managers, developers, product owners access role-specific dashboards
- **Mobile Access:** Tablet-friendly scorecards for remote review
- **Auto-Refresh:** Updates on each analysis run (weekly/sprint cadence)

### Site Structure

```
OneDrive/RA-Domain-Analysis/
├── index.html                          # Executive dashboard (KPI grid)
│
├── managers/                           # Management views
│   ├── weekly-scorecard.html           # Trend tracking table
│   ├── test-coverage-roadmap.html      # Sprint goals (8.6% → 90%)
│   ├── technical-debt-register.html    # Refactoring pipeline
│   └── team-capacity-planner.html      # Resource allocation
│
├── developers/                         # Engineering views
│   ├── onboarding-guide.html           # 5-step learning path (4 hrs)
│   ├── complexity-heatmap.html         # Code quality visualization
│   ├── knowledge-ownership.html        # Who owns what
│   └── key-files-reference.html        # Top 20 files to read
│
├── product/                            # Product management views
│   ├── capability-catalog.html         # Feature → code mapping
│   ├── roadmap-alignment.html          # Q1 2025 feature → service map
│   ├── estimation-guide.html           # Sizing reference (complexity-based)
│   └── business-glossary.html          # 80+ terms (FlexAccount, HealthSavings, rollover, etc.)
│
├── regulatory/                         # Compliance views
│   ├── compliance-status.html          # RegulatoryAgency/PrivacyRegulation/PaymentSecurity dashboard
│   ├── p0-issues-tracker.html          # Critical gaps ($500k exposure)
│   └── regulatory-test-scenarios.html  # 40+ test cases
│
└── assets/
    ├── style.css                       # Corporate branding
    ├── charts.js                       # Chart.js for visualizations
    └── data/                           # JSON data feeds
        ├── test-coverage.json
        ├── complexity.json
        ├── onboarding.json
        └── business-functions.json
```

### Implementation

```python
class OneDriveSitePublisher(RABaseCollector):
    """
    Generate OneDrive-ready HTML pages from analysis results
    
    Features:
    - Static HTML (no server required, works in OneDrive)
    - Responsive design (mobile-friendly)
    - Embedded CSS/JS (single-file deployment)
    - Auto-refresh data from JSON feeds
    
    Deployment Methods:
    1. Local Preview: python publisher.py --preview
    2. Manual Upload: Copy output/ folder to OneDrive
    3. Auto-Sync: Generate to OneDrive sync folder
    """
    
    def __init__(self, repo_path: Path, output_dir: Path, onedrive_path: Optional[Path] = None):
        super().__init__(repo_path, output_dir)
        
        # OneDrive deployment path (optional)
        self.onedrive_path = onedrive_path or self._detect_onedrive_path()
        
        # HTML templates
        self.templates_dir = Path(__file__).parent / 'templates' / 'onedrive'
        
    def publish_all_pages(self) -> Dict[str, Any]:
        """
        Generate complete OneDrive site structure
        
        Returns:
            Summary of published pages
        """
        published_pages = []
        
        # 1. Executive Dashboard
        index_html = self._generate_executive_dashboard()
        published_pages.append(self._write_page('index.html', index_html))
        
        # 2. Manager Pages
        scorecard_html = self._generate_weekly_scorecard()
        published_pages.append(self._write_page('managers/weekly-scorecard.html', scorecard_html))
        
        coverage_html = self._generate_coverage_roadmap()
        published_pages.append(self._write_page('managers/test-coverage-roadmap.html', coverage_html))
        
        debt_html = self._generate_tech_debt_register()
        published_pages.append(self._write_page('managers/technical-debt-register.html', debt_html))
        
        # 3. Developer Pages
        onboarding_html = self._generate_onboarding_guide()
        published_pages.append(self._write_page('developers/onboarding-guide.html', onboarding_html))
        
        heatmap_html = self._generate_complexity_heatmap()
        published_pages.append(self._write_page('developers/complexity-heatmap.html', heatmap_html))
        
        ownership_html = self._generate_knowledge_ownership()
        published_pages.append(self._write_page('developers/knowledge-ownership.html', ownership_html))
        
        # 4. Product Pages
        catalog_html = self._generate_capability_catalog()
        published_pages.append(self._write_page('product/capability-catalog.html', catalog_html))
        
        roadmap_html = self._generate_roadmap_alignment()
        published_pages.append(self._write_page('product/roadmap-alignment.html', roadmap_html))
        
        # 5. Regulatory Pages
        compliance_html = self._generate_compliance_status()
        published_pages.append(self._write_page('regulatory/compliance-status.html', compliance_html))
        
        p0_html = self._generate_p0_tracker()
        published_pages.append(self._write_page('regulatory/p0-issues-tracker.html', p0_html))
        
        # 6. Copy assets
        self._copy_assets()
        
        # 7. Generate JSON data feeds
        self._generate_data_feeds()
        
        return {
            'pages_published': len(published_pages),
            'pages': published_pages,
            'output_dir': str(self.output_dir / 'onedrive-site'),
            'onedrive_sync': str(self.onedrive_path) if self.onedrive_path else None
        }
    
    def _generate_executive_dashboard(self) -> str:
        """Generate index.html with KPI grid"""
        
        # Load scan results
        scan_data = self._load_scan_results()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>RA Domain Analysis Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <header>
        <h1>🏥 Payment Accounts Domain Analysis</h1>
        <p class="last-updated">Last Updated: {scan_data.get('scanned_at', 'Unknown')}</p>
    </header>
    
    <div class="kpi-grid">
        {self._render_kpi('Test Coverage', '8.6%', '90%', 'critical', 'managers/test-coverage-roadmap.html')}
        {self._render_kpi('Onboarding Time', '13 hrs', '4 hrs', 'warning', 'developers/onboarding-guide.html')}
        {self._render_kpi('Complexity', '65/100', '<50', 'warning', 'managers/technical-debt-register.html')}
        {self._render_kpi('Business Value', '$500k+', 'Risk Mitigation', 'info', 'regulatory/compliance-status.html')}
    </div>
    
    <div class="quick-links">
        <h2>Quick Access</h2>
        <div class="link-grid">
            <a href="managers/weekly-scorecard.html" class="link-card">
                <span class="icon">📊</span>
                <h3>Manager Scorecard</h3>
                <p>Weekly KPI tracking</p>
            </a>
            <a href="developers/onboarding-guide.html" class="link-card">
                <span class="icon">📚</span>
                <h3>Developer Onboarding</h3>
                <p>4-hour learning path</p>
            </a>
            <a href="product/capability-catalog.html" class="link-card">
                <span class="icon">🎯</span>
                <h3>Product Catalog</h3>
                <p>Feature → code mapping</p>
            </a>
            <a href="regulatory/p0-issues-tracker.html" class="link-card">
                <span class="icon">⚠️</span>
                <h3>Critical Issues</h3>
                <p>P0 compliance gaps</p>
            </a>
        </div>
    </div>
    
    <script src="assets/charts.js"></script>
</body>
</html>
"""
    
    def _render_kpi(self, title: str, current: str, target: str, severity: str, link: str) -> str:
        """Render KPI card HTML"""
        return f"""
        <div class="kpi {severity}">
            <h3>{title}</h3>
            <div class="value">{current}</div>
            <div class="target">Target: {target}</div>
            <a href="{link}" class="kpi-link">View Details →</a>
        </div>
"""
    
    def _detect_onedrive_path(self) -> Optional[Path]:
        """Auto-detect OneDrive sync folder"""
        # Common OneDrive paths
        onedrive_candidates = [
            Path.home() / 'OneDrive',
            Path.home() / 'OneDrive - Company',
            Path('C:/Users') / os.getenv('USERNAME', '') / 'OneDrive'
        ]
        
        for candidate in onedrive_candidates:
            if candidate.exists():
                return candidate / 'RA-Domain-Analysis'
        
        return None
    
    def _write_page(self, relative_path: str, html_content: str) -> Dict[str, str]:
        """Write HTML page to output directory"""
        output_path = self.output_dir / 'onedrive-site' / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_path.write_text(html_content, encoding='utf-8')
        
        # Copy to OneDrive sync folder if configured
        if self.onedrive_path:
            onedrive_dest = self.onedrive_path / relative_path
            onedrive_dest.parent.mkdir(parents=True, exist_ok=True)
            onedrive_dest.write_text(html_content, encoding='utf-8')
        
        return {
            'page': relative_path,
            'local': str(output_path),
            'onedrive': str(self.onedrive_path / relative_path) if self.onedrive_path else None
        }
```

### Deployment Workflow

**Initial Setup (One-time):**
```powershell
# 1. Generate site structure
python scripts/onedrive_site_publisher.py --generate

# 2. Output: cortex_brain/dashboards/data/repos/Product.Example/onedrive-site/

# 3. Copy to OneDrive (manual or auto-sync)
# Option A: Manual
Copy-Item -Recurse "cortex_brain/.../onedrive-site/*" "C:/Users/YourName/OneDrive/RA-Domain-Analysis/"

# Option B: Auto-sync (configure OneDrive path in config)
# Publisher auto-copies to OneDrive sync folder
```

**Ongoing Updates (Automated):**
```powershell
# Run analysis → auto-publishes to OneDrive
python scripts/06_master_orchestrator.py --execute-all

# Phase 8 executes OneDriveSitePublisher
# - Regenerates HTML with latest data
# - Updates JSON feeds
# - Copies to OneDrive sync folder
# - SharePoint auto-syncs to cloud
```

### Access Patterns

**Managers:**
1. Open OneDrive on mobile/desktop
2. Navigate to `RA-Domain-Analysis/managers/weekly-scorecard.html`
3. View KPI trends, drill into test coverage roadmap
4. Share link with stakeholders

**New Developers:**
1. Access `developers/onboarding-guide.html`
2. Follow 5-step checklist (4 hours)
3. Reference `key-files-reference.html` while coding

---

## 8. Dashboard Merger Roadmap

### Vision Statement

**Goal:** Integrate RA Domain Analysis OneDrive site into CORTEX Admin Dashboard as a unified interface for all repository analysis.

**Current State:**
- **Standalone OneDrive Site:** Static HTML/CSS/JS deployed to `C:\Users\ahussain\OneDrive - WAGEWORKS, INC\ASIF\RA-Domain-Analysis`
- **CORTEX Admin Dashboard:** React-based dashboard at `cortex_brain/dashboards/ui/` with glassmorphism design system

**Future State:** Single unified dashboard with:
- Multi-repository support (CORTEX + RA + future repos)
- Shared glassmorphism design language
- Real-time data refresh (JSON → live API)
- Single sign-on, unified navigation
- Responsive mobile/desktop experience

### Technical Approach

#### Phase 1: Data Layer Unification (Q1 2025)
**Goal:** Standardize data format between RA scans and CORTEX dashboard collectors

**Tasks:**
1. Extend `cortex_brain/dashboards/data/repos/` structure to include RA
2. Create `product-payment-accounts.json` matching admin dashboard schema
3. Map business_value_scanner.py output to dashboard data model
4. Add RA repository to registry (`cortex_brain/dashboards/data/repository-registry.json`)

**Example Mapping:**
```json
{
  "repository": "Product.Example",
  "scan_date": "2025-12-11",
  "metrics": {
    "test_coverage": 8.6,
    "complexity_score": 65,
    "onboarding_hours": 13,
    "p0_issues": 9
  },
  "collectors": {
    "test_coverage": "analysis-results/business-value-scan.json",
    "complexity": "analysis-results/business-value-scan.json"
  }
}
```

#### Phase 2: UI Component Migration (Q2 2025)
**Goal:** Convert OneDrive HTML pages to React components matching admin dashboard architecture

**Tasks:**
1. Create `cortex_brain/dashboards/ui/src/pages/RA/` directory
2. Convert static HTML to React components:
   - `index.html` → `RADomainOverview.jsx`
   - `managers/weekly-scorecard.html` → `ManagerScorecard.jsx`
   - `developers/onboarding-guide.html` → `OnboardingGuide.jsx`
   - `regulatory/p0-issues-tracker.html` → `P0ComplianceTracker.jsx`
3. Reuse existing glassmorphism components from `dashboards/ui/styles/components/`
4. Add RA nav tab to admin dashboard sidebar

**Component Structure:**
```
dashboards/ui/src/pages/
├── Executive/
├── Overview/
├── TechStack/
├── Security/
├── UseCases/
├── RA/  # NEW
│   ├── RADomainOverview.jsx
│   ├── ManagerScorecard.jsx
│   ├── OnboardingGuide.jsx
│   ├── TestCoverageRoadmap.jsx
│   ├── ComplexityHeatmap.jsx
│   ├── P0ComplianceTracker.jsx
│   └── CapabilityCatalog.jsx
```

#### Phase 3: Navigation Integration (Q2 2025)
**Goal:** Add RA Domain tab to admin dashboard sidebar

**Tasks:**
1. Update `dashboards/ui/index.html` sidebar navigation
2. Add RA icon + label (e.g., "RA Domain 📊")
3. Implement tab switching logic (hide/show RA content)
4. Add repository selector dropdown (CORTEX ↔ RA)

**Navigation Snippet:**
```html
<!-- Add to sidebar-nav in index.html -->
<li class="nav-item">
    <a href="#ra-domain" class="nav-link" data-page="ra">
        <span class="nav-icon">📊</span>
        <span class="nav-label">RA Domain</span>
    </a>
</li>
```

#### Phase 4: Data Refresh Automation (Q3 2025)
**Goal:** Replace static JSON with live data refresh via Python orchestrator

**Tasks:**
1. Schedule `business_value_scanner.py` to run weekly via Windows Task Scheduler
2. Auto-update `cortex_brain/dashboards/data/repos/Product.Example/latest.json`
3. Add "Last Updated" timestamp to dashboard
4. Implement manual refresh button (re-runs scanner on-demand)

**Automation Script:**
```powershell
# Weekly RA scan (runs every Monday 6 AM)
schtasks /create /tn "RA Domain Scan" /tr "python cortex_brain/admin/RA-Domain/toolkit/scripts/business_value_scanner.py" /sc weekly /d MON /st 06:00
```

#### Phase 5: Mobile Optimization (Q4 2025)
**Goal:** Ensure responsive design for manager mobile access

**Tasks:**
1. Test OneDrive site on mobile devices (iOS/Android)
2. Adjust glassmorphism CSS for touch targets (min 44px)
3. Optimize KPI grid for single-column layout
4. Add swipe gestures for navigation

### Migration Benefits

**For Managers:**
- ✅ Single URL instead of multiple OneDrive links
- ✅ Real-time data (auto-refresh weekly)
- ✅ Cross-repo comparisons (CORTEX vs RA metrics)
- ✅ Mobile-optimized dashboard

**For Developers:**
- ✅ Unified onboarding (CORTEX docs + RA docs in one place)
- ✅ Shared complexity heatmap patterns
- ✅ Consistent glassmorphism UI (no context switching)

**For Product/Regulatory:**
- ✅ P0 compliance tracker integrated with security dashboard
- ✅ Capability catalog linked to roadmap planning
- ✅ Audit-ready reports (export to PDF)

### Rollout Plan

| **Quarter** | **Deliverable** | **Effort** | **Owner** |
|-------------|-----------------|------------|-----------|
| Q1 2025 | Data layer unification | 16 hours | Dev Team |
| Q2 2025 | React component migration | 40 hours | Frontend Dev |
| Q2 2025 | Navigation integration | 8 hours | Frontend Dev |
| Q3 2025 | Data refresh automation | 12 hours | DevOps |
| Q4 2025 | Mobile optimization | 20 hours | UX/Frontend |
| **Total** | | **96 hours** | |

**Cost:** $36,000 (@ $375/hr blended rate)  
**ROI:** Unified dashboard reduces context switching (30 min/week saved × 5 managers × 52 weeks = 130 hours/year = $48,750)  
**Payback Period:** 9 months

### Interim State (Current)

**OneDrive Site Active:** Managers/developers use standalone OneDrive HTML pages while merger is in progress.

**Parallel Maintenance:** Updates to OneDrive site will be manually ported to admin dashboard React components during Phase 2.

**No Breaking Changes:** OneDrive site remains functional until Q3 2025 (full migration complete).

### Success Criteria

- ✅ RA data visible in admin dashboard repository selector
- ✅ All 8 RA views converted to React components
- ✅ Navigation tab functional with tab switching
- ✅ Weekly auto-refresh operational
- ✅ Mobile responsive (< 768px viewport)
- ✅ OneDrive site deprecated (301 redirect to admin dashboard)

### Technical Debt Considerations

**Avoid:** Duplicate CSS (OneDrive glass.css + admin dashboard styles)  
**Solution:** Phase 2 migration removes OneDrive CSS entirely, reuses admin dashboard components

**Avoid:** Manual JSON updates (static business-value-scan.json)  
**Solution:** Phase 4 automation ensures dashboard always shows latest RA metrics

**Avoid:** Hard-coded RA paths in admin dashboard  
**Solution:** Repository registry pattern makes adding future repos trivial (e.g., Product.Requests, Product.Eligibility)

---

**Note:** This roadmap documents intent for future implementation. OneDrive site is production-ready as standalone solution while merger planning proceeds.
**Product Owners:**
1. Review `product/capability-catalog.html`
2. Map roadmap features to code components
3. Use `estimation-guide.html` for sprint planning

---

**Author:** Asif Hussain  
**License:** © 2025 Asif Hussain. All rights reserved.  
**Version:** 1.2 - OneDrive Site Publishing Integration
