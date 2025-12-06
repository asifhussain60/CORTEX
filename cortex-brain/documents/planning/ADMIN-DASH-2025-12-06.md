# Admin Dashboard Enhancement Plan
**Feature ID:** ADMIN-DASH-2025-12-06  
**Created:** December 6, 2025  
**Status:** 🔄 In Progress (Phase 2 Complete)  
**Priority:** High  
**Estimated Effort:** 24 hours across 8 phases (updated)

---

## 📋 Vision Statement

Transform the CORTEX admin dashboard into a self-maintaining, extensible, and comprehensive repository analysis platform that automatically discovers new repositories, performs deep analysis, and presents insights through a polished, branded interface.

---

## 🎯 Objectives

### Primary Goals
1. **Auto-Discovery:** Dashboard automatically detects and wires new repositories on launch
2. **Dynamic UI:** Left panel updates in real-time as features are added
3. **Deep Analysis:** Data collectors perform comprehensive analysis (not shallow scans)
4. **Extensible Config:** Centralized configuration for all paths and settings
5. **Branded UI:** Replace text header with prominent CORTEX logo
6. **Clean Tests:** Remove obsolete Flask-based tests

### Success Criteria
- Zero manual configuration for new repositories
- Data collection discovers 100+ metrics per repository
- Sub-second dashboard refresh after adding repositories
- Single source of truth for all path configurations
- Professional branded dashboard appearance
- Test suite only contains relevant, passing tests

---

## 📊 Definition of Ready (DoR)

### Prerequisites
- [x] Current dashboard structure documented
- [x] Existing data collectors analyzed
- [x] Test suite inventory completed
- [x] Path references mapped across codebase
- [x] Logo asset requirements identified

### Technical Context
- **Current Structure:** `cortex-brain/dashboards/data/repos/{repo-name}/`
- **Active Collectors:** 7 data files per repository (health, tech-stack, security, etc.)
- **Test Status:** 83 passing, 34 failing/errored (Flask-related)
- **Path Management:** Hardcoded in 15+ files
- **UI Framework:** Vanilla JS with D3.js/Chart.js visualizations

### Resources Available
- Existing dashboard UI (`ui/index.html`)
- Data collector framework (`src/orchestrators/dashboard_collector.py`)
- Admin launcher module (`src/operations/modules/admin_dashboard_launcher_module.py`)
- Schema validators (`data/schema/`)

---

## 🏗️ Implementation Phases

### Phase 1: Centralized Configuration System
**Objective:** Create single source of truth for all dashboard paths and settings

**Tasks:**
1. Create `cortex-brain/dashboards/dashboard-config.yaml`
   ```yaml
   version: "1.0"
   paths:
     data_root: "cortex-brain/dashboards/data"
     repos: "cortex-brain/dashboards/data/repos"
     mock: "cortex-brain/dashboards/data/mock"
     schema: "cortex-brain/dashboards/data/schema"
     templates: "cortex-brain/dashboards/data/templates"
     ui: "cortex-brain/dashboards/ui"
   
   collectors:
     timeout: 300  # seconds
     parallel_workers: 4
     deep_analysis: true
   
   ui:
     logo_path: "static/images/cortex-logo.png"
     logo_width: 180
     logo_height: 60
     refresh_interval: 5000  # ms
   
   discovery:
     auto_scan: true
     scan_interval: 30  # seconds
     remove_missing: true
   ```

2. Create `src/config/dashboard_config.py` loader
   ```python
   class DashboardConfig:
       @staticmethod
       def load() -> Dict[str, Any]:
           # Load YAML, validate, return config
       
       @staticmethod
       def get_path(key: str) -> Path:
           # Return resolved absolute path
   ```

3. Update all files to use config (15 files identified)

**DoD:**
- [ ] Config file created with comprehensive settings
- [ ] Config loader with validation implemented
- [ ] All hardcoded paths replaced with config references
- [ ] Tests pass with config-driven paths
- [ ] Config documented in README

**Estimated:** 3 hours

---

### Phase 2: Repository Auto-Discovery System
**Objective:** Automatically detect, validate, and wire new repositories into dashboard

**Tasks:**
1. Create `src/operations/modules/repository_discovery_module.py`
   ```python
   class RepositoryDiscoveryService:
       def scan_repositories(self) -> List[RepoMetadata]:
           """Scan data/repos/ for valid repositories"""
       
       def validate_repository(self, path: Path) -> bool:
           """Check for required data files"""
       
       def register_repository(self, repo: RepoMetadata) -> None:
           """Add to dashboard registry"""
       
       def remove_missing_repositories(self) -> List[str]:
           """Remove repos that no longer exist"""
   ```

2. Update `admin_dashboard_launcher_module.py`
   ```python
   def execute(self, context):
       # NEW: Auto-discover repositories before launch
       discovery = RepositoryDiscoveryService()
       repos = discovery.scan_repositories()
       discovery.register_all(repos)
       discovery.remove_missing_repositories()
       
       # Continue with existing launch logic
   ```

3. Create repository registry (`data/repository-registry.json`)
   ```json
   {
     "repositories": [
       {
         "id": "tcbulk",
         "name": "TCBULK",
         "path": "data/repos/tcbulk",
         "discovered": "2025-12-06T08:05:48",
         "last_updated": "2025-12-06T08:05:49",
         "status": "active",
         "data_files": 7
       }
     ],
     "last_scan": "2025-12-06T08:15:00"
   }
   ```

4. Update `ui/data-loader.js` to fetch from registry

**DoD:**
- [ ] Discovery service scans and validates repositories
- [ ] Registry file auto-generated and maintained
- [ ] Missing repositories automatically removed
- [ ] UI loads from registry dynamically
- [ ] Discovery runs on every dashboard launch
- [ ] Tests verify auto-discovery workflow

**Estimated:** 4 hours

---

### Phase 2.5: Data Collection Benchmarking & Validation
**Objective:** Establish baseline file sizes and validate collector success

**Rationale:** Need to verify that "deep analysis" collectors actually produce comprehensive data. Benchmarks stored in config allow automatic validation of collection success.

**Implementation:**

1. **Add Benchmarks to Config**
   ```yaml
   # cortex-brain/dashboards/config/dashboard-config.yaml
   
   collectors:
     # ... existing settings ...
     
     # Expected file size benchmarks (bytes)
     benchmarks:
       health-data:
         min_size: 5120      # 5KB minimum
         target_size: 10240  # 10KB target
         max_variance: 0.3   # ±30% acceptable
       
       tech-stack:
         min_size: 3072      # 3KB minimum
         target_size: 5120   # 5KB target
         max_variance: 0.25
       
       security:
         min_size: 10240     # 10KB minimum
         target_size: 20480  # 20KB target
         max_variance: 0.4
       
       architecture:
         min_size: 15360     # 15KB minimum
         target_size: 25600  # 25KB target
         max_variance: 0.35
       
       code-organization:
         min_size: 20480     # 20KB minimum
         target_size: 30720  # 30KB target
         max_variance: 0.3
       
       team-metrics:
         min_size: 2048      # 2KB minimum
         target_size: 4096   # 4KB target
         max_variance: 0.25
       
       vendors:
         min_size: 1024      # 1KB minimum
         target_size: 2048   # 2KB target
         max_variance: 0.2
   ```

2. **Add Validation Module**
   ```python
   # src/orchestrators/dashboard_validation.py
   
   from src.dashboard_config import get_config
   from pathlib import Path
   from typing import Dict, List, Tuple
   
   class CollectionValidator:
       """Validate data collection against benchmarks"""
       
       def __init__(self):
           self.config = get_config()
           self.benchmarks = self.config.get_collector_config().benchmarks
       
       def validate_collection(self, repo_path: Path) -> Dict[str, Any]:
           """
           Validate all collected data files against benchmarks.
           
           Returns:
               {
                   "success": bool,
                   "files_checked": int,
                   "passed": int,
                   "failed": int,
                   "warnings": List[str],
                   "details": {...}
               }
           """
           results = {
               "success": True,
               "files_checked": 0,
               "passed": 0,
               "failed": 0,
               "warnings": [],
               "details": {}
           }
           
           for file_type, benchmark in self.benchmarks.items():
               file_path = repo_path / f"{file_type}.json"
               
               if not file_path.exists():
                   results["failed"] += 1
                   results["warnings"].append(f"Missing: {file_type}.json")
                   results["success"] = False
                   continue
               
               file_size = file_path.stat().st_size
               results["files_checked"] += 1
               
               # Check against benchmark
               status = self._check_file_size(
                   file_size,
                   benchmark["min_size"],
                   benchmark["target_size"],
                   benchmark["max_variance"]
               )
               
               results["details"][file_type] = {
                   "size": file_size,
                   "min_expected": benchmark["min_size"],
                   "target": benchmark["target_size"],
                   "status": status,
                   "percentage_of_target": (file_size / benchmark["target_size"]) * 100
               }
               
               if status == "passed":
                   results["passed"] += 1
               elif status == "warning":
                   results["warnings"].append(
                       f"{file_type}: Size {file_size}B is below target {benchmark['target_size']}B"
                   )
                   results["passed"] += 1  # Warning, not failure
               else:
                   results["failed"] += 1
                   results["warnings"].append(
                       f"{file_type}: Size {file_size}B below minimum {benchmark['min_size']}B"
                   )
                   results["success"] = False
           
           return results
       
       def _check_file_size(
           self,
           actual: int,
           min_size: int,
           target: int,
           variance: float
       ) -> str:
           """Check file size against benchmarks"""
           if actual < min_size:
               return "failed"
           elif actual < target:
               return "warning"
           elif actual > target * (1 + variance):
               return "warning"  # Unexpectedly large
           else:
               return "passed"
   ```

3. **Integrate with Data Collector**
   ```python
   # src/orchestrators/dashboard_collector.py
   
   from src.orchestrators.dashboard_validation import CollectionValidator
   
   class DashboardDataCollector:
       def collect_all(self):
           """Collect all data with validation"""
           # ... existing collection code ...
           
           # VALIDATION
           validator = CollectionValidator()
           validation = validator.validate_collection(self.output_dir)
           
           if not validation["success"]:
               logger.error(
                   f"Data collection validation FAILED for {self.repo_name}:\n"
                   f"  Passed: {validation['passed']}/{validation['files_checked']}\n"
                   f"  Failed: {validation['failed']}\n"
                   f"  Warnings: {', '.join(validation['warnings'])}"
               )
           else:
               logger.info(
                   f"Data collection validation PASSED for {self.repo_name}: "
                   f"{validation['passed']}/{validation['files_checked']} files"
               )
           
           # Add validation results to metadata
           metadata["validation"] = validation
   ```

4. **Update Progress Script**
   ```python
   # scripts/collect_dashboard_data_with_progress.py
   
   # After collection
   validator = CollectionValidator()
   validation = validator.validate_collection(repo_output_dir)
   
   if validation["success"]:
       print(f"✅ Validation: {validation['passed']}/{validation['files_checked']} files passed")
   else:
       print(f"⚠️  Validation: {validation['failed']} files below minimum")
       for warning in validation["warnings"]:
           print(f"    - {warning}")
   ```

**DoD:**
- [ ] Benchmarks added to dashboard-config.yaml
- [ ] CollectionValidator module created
- [ ] Validation integrated into data collector
- [ ] Validation results stored in metadata.json
- [ ] Collection script shows validation summary
- [ ] Tests verify validation logic
- [ ] Documentation updated with benchmark guidelines

**Benefits:**
- Automatic detection of failed/incomplete collections
- Quality assurance for deep analysis
- Early warning system for collector degradation
- Benchmarks guide enhancement efforts
- Validation results trackable over time

**Estimated:** 2 hours

---

### Phase 3: Deep Data Collection Enhancement
**Objective:** Transform collectors from shallow scans to comprehensive analysis

**Current Issue:** Data collection too fast (1-6 seconds) indicates shallow analysis

**Enhanced Collectors:**

1. **Health Data Collector** (currently 0.52KB → target 5-10KB)
   - Add complexity metrics (cyclomatic, cognitive)
   - Calculate maintainability index per file
   - Detect code smells and anti-patterns
   - Measure test coverage accurately
   - Analyze dependency health

2. **Tech Stack Analyzer** (currently 0.59-0.69KB → target 3-5KB)
   - Deep framework detection (check imports, configs)
   - Version detection from lock files
   - Compatibility analysis
   - End-of-life checking for dependencies
   - Performance characteristics

3. **Security Analyzer** (currently 0.22KB → target 10-20KB)
   - Pattern-based vulnerability scanning
   - Hardcoded secrets detection
   - SQL injection vulnerability patterns
   - XSS vulnerability patterns
   - Insecure deserialization checks
   - Dependency vulnerability lookup (CVE database)

4. **Architecture Analyzer** (currently 0.21KB → target 15-25KB)
   - Call graph generation
   - Dependency tree analysis
   - Layer violation detection
   - Circular dependency identification
   - Module cohesion metrics
   - Component relationship mapping

5. **Code Organization** (currently 0.27KB → target 20-30KB)
   - Hotspot detection (high complexity + high churn)
   - Duplication analysis
   - Function/class size metrics
   - Naming convention analysis
   - Comment ratio analysis
   - Dead code detection

**Implementation:**
```python
# src/orchestrators/dashboard_collector.py

def collect_health_data(self) -> Dict[str, Any]:
    """Enhanced health data collection"""
    logger.info("Performing deep health analysis...")
    
    # Progress feedback
    yield_progress(0, 100, "Scanning files...")
    
    # 1. File analysis
    files = self._scan_all_files()  # 10s
    yield_progress(20, 100, f"Analyzed {len(files)} files")
    
    # 2. Complexity analysis
    complexity = self._calculate_complexity(files)  # 15s
    yield_progress(50, 100, "Complexity analysis complete")
    
    # 3. Code smells
    smells = self._detect_code_smells(files)  # 10s
    yield_progress(75, 100, "Code smell detection complete")
    
    # 4. Test coverage
    coverage = self._analyze_test_coverage()  # 10s
    yield_progress(100, 100, "Health analysis complete")
    
    return {
        "overall_health_score": self._calculate_score(complexity, smells, coverage),
        "detailed_metrics": {...},  # Comprehensive data
        "analysis_duration": "45 seconds"
    }
```

**Target Performance:**
- Small repos (<1000 files): 30-60 seconds
- Medium repos (1000-5000 files): 1-3 minutes
- Large repos (5000+ files): 3-10 minutes

**DoD:**
- [ ] All 7 collectors enhanced with deep analysis
- [ ] Progress feedback during long operations
- [ ] Data files 10-50x larger with rich metrics
- [ ] Performance benchmarks documented
- [ ] Collectors respect `deep_analysis` config flag
- [ ] Tests verify comprehensive data collection

**Estimated:** 6 hours

---

### Phase 4: Dynamic UI Updates
**Objective:** Left panel and features update in real-time without page refresh

**Implementation:**

1. **WebSocket Server** (optional for real-time, or use polling)
   ```python
   # src/operations/modules/dashboard_websocket_server.py
   
   class DashboardWebSocketServer:
       def notify_repository_added(self, repo: RepoMetadata):
           """Push update to all connected clients"""
       
       def notify_feature_added(self, feature: str):
           """Notify UI of new feature availability"""
   ```

2. **Polling Alternative** (simpler, no WebSocket needed)
   ```javascript
   // ui/repository-monitor.js
   
   class RepositoryMonitor {
       constructor() {
           this.registryUrl = '/data/repository-registry.json';
           this.pollInterval = 5000; // 5 seconds
       }
       
       async checkForUpdates() {
           const response = await fetch(this.registryUrl);
           const registry = await response.json();
           
           // Compare with local cache
           const newRepos = this.findNewRepositories(registry);
           const removedRepos = this.findRemovedRepositories(registry);
           
           if (newRepos.length > 0) {
               this.updateLeftPanel(newRepos);
               this.showNotification(`${newRepos.length} new repositories discovered`);
           }
           
           if (removedRepos.length > 0) {
               this.removeFromLeftPanel(removedRepos);
           }
       }
   }
   ```

3. **Dynamic Feature Detection**
   ```javascript
   // ui/feature-detector.js
   
   class FeatureDetector {
       async detectAvailableFeatures(repoId) {
           // Check which data files exist
           const features = await this.scanDataFiles(repoId);
           
           // Update left panel sections
           this.updateFeatureSections(features);
       }
   }
   ```

4. **Left Panel Component** (update existing)
   ```javascript
   // ui/components/left-panel.js
   
   class LeftPanel {
       addRepository(repo) {
           const item = this.createRepoListItem(repo);
           this.repositoryList.appendChild(item);
           this.playAddAnimation(item);
       }
       
       removeRepository(repoId) {
           const item = this.findRepoItem(repoId);
           this.playRemoveAnimation(item);
           setTimeout(() => item.remove(), 300);
       }
       
       updateFeatures(features) {
           // Show/hide feature sections based on availability
           features.forEach(feature => {
               const section = this.findFeatureSection(feature);
               if (section) section.classList.remove('hidden');
           });
       }
   }
   ```

**DoD:**
- [ ] Repository changes detected within 5 seconds
- [ ] Left panel updates without page refresh
- [ ] Smooth animations for add/remove
- [ ] Feature sections show/hide dynamically
- [ ] Visual notifications for changes
- [ ] No memory leaks from polling

**Estimated:** 3 hours

---

### Phase 5: Logo Integration & Branding
**Objective:** Replace text header with prominent CORTEX logo

**Tasks:**

1. **Create/Obtain Logo Asset**
   - Source: `static/images/cortex-logo.png`
   - Dimensions: 180x60px (configurable)
   - Format: PNG with transparency
   - Quality: High-resolution for clarity

2. **Update HTML Header**
   ```html
   <!-- ui/index.html -->
   
   <!-- OLD -->
   <div class="dashboard-header">
       <h1>CORTEX Health Dashboard</h1>
   </div>
   
   <!-- NEW -->
   <div class="dashboard-header">
       <img src="../static/images/cortex-logo.png" 
            alt="CORTEX" 
            class="dashboard-logo"
            width="180" 
            height="60">
       <span class="dashboard-subtitle">Admin Dashboard</span>
   </div>
   ```

3. **Update CSS Styling**
   ```css
   /* ui/styles/main.css */
   
   .dashboard-logo {
       max-width: 180px;
       height: auto;
       margin-right: 1rem;
       filter: drop-shadow(0 2px 8px rgba(0, 212, 255, 0.3));
       transition: filter 0.3s ease;
   }
   
   .dashboard-logo:hover {
       filter: drop-shadow(0 4px 12px rgba(0, 212, 255, 0.5));
   }
   
   .dashboard-subtitle {
       font-size: 0.875rem;
       color: var(--text-secondary);
       font-weight: 400;
   }
   ```

4. **Responsive Design**
   ```css
   @media (max-width: 768px) {
       .dashboard-logo {
           max-width: 120px;
       }
       
       .dashboard-subtitle {
           display: none;
       }
   }
   ```

**DoD:**
- [ ] Logo asset created/sourced and stored
- [ ] Header updated with logo image
- [ ] Styling provides prominence and polish
- [ ] Responsive design for mobile
- [ ] Logo configurable via dashboard-config.yaml
- [ ] Visual regression test added

**Estimated:** 1 hour

---

### Phase 6: Test Cleanup
**Objective:** Remove obsolete Flask-based tests and dependencies

**Tests to Remove:**

1. **Flask Template Tests** (9 failing)
   - `test_css.py` - CSS file tests for old templates
   - `test_js.py` - JS file tests for old templates
   - `test_templates.py` - Flask template rendering tests
   - `test_integration.py` - Flask route integration tests
   - `test_application_switcher.py` - Flask-based app switching

2. **Associated Fixtures and Helpers**
   - Flask app fixtures in `conftest.py`
   - Template loader helpers
   - Route testing utilities

**Cleanup Process:**
```bash
# Remove obsolete test files
rm tests/dashboard/presentation/test_css.py
rm tests/dashboard/presentation/test_js.py
rm tests/dashboard/presentation/test_templates.py
rm tests/dashboard/presentation/test_integration.py
rm tests/dashboard/presentation/test_application_switcher.py

# Clean up conftest.py
# Remove Flask-related fixtures

# Verify test suite
pytest tests/dashboard/ -v
# Expected: 83 passing, 0 failing
```

**DoD:**
- [ ] All Flask-based test files removed
- [ ] Flask fixtures removed from conftest.py
- [ ] Test suite runs with 100% pass rate
- [ ] No orphaned test utilities
- [ ] Documentation updated to reflect test structure

**Estimated:** 1 hour

---

### Phase 7: Final Refactor & Cleanup
**Objective:** Comprehensive reorganization and cleanup to ensure pristine folder structure and code quality

**Tasks:**

1. **Folder Structure Audit & Reorganization**
   ```
   # Validate final structure
   cortex-brain/dashboards/
   ├── data/
   │   ├── repos/           # Repository-specific data (8+ repos)
   │   ├── mock/            # Mock data for testing
   │   ├── schema/          # JSON schemas & validators
   │   ├── templates/       # Data templates
   │   └── cache/           # NEW: Computed aggregations
   │       ├── summary.json
   │       ├── comparisons.json
   │       └── registry-cache.json
   ├── ui/
   │   ├── components/      # UI components (organized)
   │   │   ├── panels/      # Left panel, header, etc.
   │   │   ├── tabs/        # Tab content components
   │   │   └── visualizations/  # Charts, graphs
   │   ├── services/        # NEW: Data services, monitors
   │   │   ├── repository-monitor.js
   │   │   ├── data-loader.js
   │   │   └── feature-detector.js
   │   ├── styles/          # Organized stylesheets
   │   │   ├── main.css
   │   │   ├── components.css
   │   │   └── themes.css
   │   ├── utils/           # NEW: Utility functions
   │   └── index.html       # Main entry point
   ├── config/              # NEW: Configuration files
   │   ├── dashboard-config.yaml
   │   └── schema-versions.json
   └── README.md            # Updated documentation
   ```

2. **Code Organization Cleanup**
   - Move all repository discovery logic to `src/operations/modules/dashboard/`
   - Consolidate data collector enhancements into unified module
   - Extract reusable UI components to `ui/components/`
   - Move service layer to `ui/services/`
   - Create utility module for common functions

3. **Remove Temporary & Development Artifacts**
   ```bash
   # Remove development files
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} +
   find . -name ".DS_Store" -delete
   
   # Remove old backups
   rm -rf cortex-brain/dashboards/*.backup
   rm -rf cortex-brain/dashboards/*.old
   rm -rf cortex-brain/dashboards/data/repos/.tmp*
   
   # Clean up test artifacts
   rm -rf .pytest_cache/
   rm -rf .coverage*
   ```

4. **Naming Convention Standardization**
   - Ensure all Python modules use `snake_case`
   - Ensure all JavaScript files use `kebab-case`
   - Ensure all classes use `PascalCase`
   - Ensure all constants use `UPPER_SNAKE_CASE`
   - Validate file naming consistency across project

5. **Deprecated Code Removal**
   - Remove old data loader paths (pre-reorganization)
   - Remove unused Flask integration code
   - Remove legacy dashboard launcher functions
   - Clean up commented-out code blocks
   - Remove orphaned utility functions

6. **Documentation Consolidation**
   ```
   cortex-brain/documents/
   ├── implementation-guides/
   │   ├── dashboard-admin-guide.md       # NEW: Comprehensive admin guide
   │   ├── dashboard-configuration.md     # NEW: Config reference
   │   ├── data-collector-extension.md    # NEW: How to extend collectors
   │   └── dashboard-troubleshooting.md   # NEW: Common issues
   ├── architecture/
   │   └── dashboard-architecture-v2.md   # NEW: Updated architecture doc
   └── planning/
       ├── ADMIN-DASH-2025-12-06.md       # This plan (archived after completion)
       └── dashboard-onboarding-alignment-plan.md  # Previous plan
   ```

7. **Import Statement Optimization**
   - Remove unused imports across all modified files
   - Consolidate duplicate imports
   - Sort imports (standard → third-party → local)
   - Use absolute imports consistently

8. **Configuration File Consolidation**
   - Merge any duplicate config files
   - Remove hardcoded configurations
   - Validate all config paths are relative
   - Document all configuration options

9. **Test Suite Reorganization**
   ```
   tests/dashboard/
   ├── unit/
   │   ├── test_repository_discovery.py
   │   ├── test_data_collectors_enhanced.py
   │   ├── test_config_loader.py
   │   └── test_dynamic_ui.py
   ├── integration/
   │   ├── test_dashboard_workflow.py
   │   ├── test_auto_discovery_pipeline.py
   │   └── test_end_to_end.py
   ├── performance/
   │   ├── test_collector_performance.py
   │   └── test_ui_responsiveness.py
   └── fixtures/
       ├── mock_repositories.py
       └── sample_data.py
   ```

10. **Static Analysis & Linting**
    ```bash
    # Run static analysis
    pylint src/operations/modules/dashboard/ --rcfile=.pylintrc
    mypy src/operations/modules/dashboard/ --strict
    
    # Run JavaScript linting
    eslint cortex-brain/dashboards/ui/**/*.js --fix
    
    # Check for security issues
    bandit -r src/operations/modules/dashboard/
    
    # Format code
    black src/operations/modules/dashboard/
    prettier --write "cortex-brain/dashboards/ui/**/*.js"
    ```

11. **Dependency Cleanup**
    - Remove unused dependencies from requirements
    - Update dependency versions
    - Verify no version conflicts
    - Document all dashboard-specific dependencies

12. **Git Housekeeping**
    ```bash
    # Clean up git history markers
    git gc --prune=now
    
    # Update .gitignore for dashboard artifacts
    echo "cortex-brain/dashboards/data/cache/" >> .gitignore
    echo "cortex-brain/dashboards/data/repos/.tmp/" >> .gitignore
    echo "*.log" >> .gitignore
    
    # Verify no large files committed
    git ls-files | xargs ls -lh | sort -k5 -hr | head -20
    ```

13. **Performance Optimization Review**
    - Profile data collectors for bottlenecks
    - Optimize database queries
    - Minimize UI reflows/repaints
    - Implement lazy loading where appropriate
    - Add caching layer for expensive operations

14. **Security Audit**
    - Validate input sanitization in all collectors
    - Check for path traversal vulnerabilities
    - Ensure no sensitive data in logs
    - Verify config files don't contain secrets
    - Review file permissions

15. **Final Validation Checklist**
    ```bash
    # Run all tests
    pytest tests/dashboard/ -v --cov=src/operations/modules/dashboard
    
    # Check code quality
    pylint src/operations/modules/dashboard/ --fail-under=8.5
    
    # Verify folder structure
    tree cortex-brain/dashboards/ -L 3
    
    # Check for TODOs
    grep -r "TODO\|FIXME\|HACK" src/operations/modules/dashboard/
    
    # Validate documentation
    markdown-link-check cortex-brain/documents/**/*.md
    
    # Performance baseline
    python scripts/benchmark_dashboard_collectors.py
    ```

**DoD:**
- [ ] Folder structure matches planned organization (100%)
- [ ] All temporary/development files removed
- [ ] Naming conventions consistent across codebase
- [ ] Zero deprecated code or commented-out blocks
- [ ] All documentation consolidated and updated
- [ ] Import statements optimized and sorted
- [ ] Configuration files consolidated
- [ ] Test suite properly organized by type
- [ ] Static analysis passes with >8.5/10 score
- [ ] No unused dependencies in requirements
- [ ] Git repository clean and optimized
- [ ] Performance benchmarks documented
- [ ] Security audit completed with no critical issues
- [ ] Final validation checklist 100% green
- [ ] Code coverage maintained >85%

**Estimated:** 4 hours

**Critical Success Factors:**
- Leave codebase cleaner than we found it
- Every file has a clear purpose and location
- Zero technical debt introduced
- Documentation reflects actual implementation
- Future maintainers can easily understand structure

---

## 🔍 Definition of Done (DoD)

### Functional Requirements
- [ ] Dashboard auto-discovers new repositories on launch
- [ ] Left panel updates within 5 seconds of repository changes
- [ ] Data collectors generate 10-50x more comprehensive data
- [ ] All paths managed through centralized config
- [ ] CORTEX logo prominently displayed in header
- [ ] Test suite 100% passing (obsolete tests removed)
- [ ] Folder structure clean and well-organized
- [ ] Zero technical debt or deprecated code

### Technical Requirements
- [ ] Configuration system validated and documented
- [ ] Repository discovery service with comprehensive tests
- [ ] Enhanced collectors with progress feedback
- [ ] Dynamic UI updates without page refresh
- [ ] Logo integration responsive and accessible
- [ ] Code coverage maintained >85%

### Quality Requirements
- [ ] All changes peer reviewed
- [ ] Integration tests cover new workflows
- [ ] Performance benchmarks documented
- [ ] No regressions in existing functionality
- [ ] Documentation updated (README, guides)
- [ ] Static analysis score >8.5/10
- [ ] Security audit completed with no critical issues
- [ ] Import statements optimized and sorted
- [ ] Naming conventions consistent throughout

### User Experience
- [ ] Dashboard feels responsive and alive
- [ ] Progress feedback during long operations
- [ ] Professional, branded appearance
- [ ] Intuitive repository management
- [ ] Clear status indicators

---

## 📈 Risk Analysis

### High Risk
**Risk:** Deep collectors timeout on very large repositories (10,000+ files)  
**Mitigation:** 
- Implement configurable timeout (300s default)
- Add incremental analysis (resume from checkpoint)
- Provide "quick scan" vs "deep scan" options
- Show progress during analysis

### Medium Risk
**Risk:** Dynamic UI updates cause memory leaks from polling  
**Mitigation:**
- Implement cleanup on component unmount
- Use efficient diffing algorithm
- Limit polling frequency (5s minimum)
- Add memory profiling tests

### Low Risk
**Risk:** Logo asset not available or wrong format  
**Mitigation:**
- Provide fallback to text header
- Document logo requirements clearly
- Include example logo in repository

---

## 🧪 Testing Strategy

### Unit Tests
- Configuration loader validation
- Repository discovery logic
- Data collector individual methods
- UI component state management

### Integration Tests
- End-to-end discovery → dashboard update workflow
- Config changes propagate correctly
- Collector data flows to UI
- Logo loading and fallback

### Performance Tests
- Large repository analysis (<10 min target)
- UI responsiveness with 50+ repositories
- Memory usage during polling
- Collector parallel execution efficiency

### Manual Tests
- Visual inspection of logo placement
- Real-time updates user experience
- Config modifications take effect
- Error handling and recovery

---

## 📚 Documentation Updates

### User Documentation
- [ ] Admin dashboard quick start guide
- [ ] Configuration reference
- [ ] Repository onboarding process
- [ ] Troubleshooting common issues

### Developer Documentation
- [ ] Architecture decision records (ADRs)
- [ ] Data collector extension guide
- [ ] UI component development guide
- [ ] Configuration schema documentation

---

## 🎯 Success Metrics

### Quantitative
- Repository discovery: <1 second for scanning
- Data collection: 10-50x more comprehensive data
- UI updates: <5 second latency
- Test pass rate: 100%
- Code coverage: >85%

### Qualitative
- Dashboard feels "alive" and responsive
- Professional appearance with logo
- Easy to add new repositories
- Configuration is intuitive
- Collectors provide deep insights

---

## 📅 Execution Timeline

**Total Estimated Effort:** 22 hours

| Phase | Tasks | Estimated | Dependencies |
|-------|-------|-----------|--------------|
| 1. Configuration | Config system | 3h | None |
| 2. Auto-Discovery | Repository scanning | 4h | Phase 1 |
| 3. Deep Collectors | Enhanced analysis | 6h | Phase 1 |
| 4. Dynamic UI | Real-time updates | 3h | Phase 2 |
| 5. Logo Integration | Branding | 1h | None |
| 6. Test Cleanup | Remove obsolete | 1h | None |
| 7. Final Refactor | Cleanup & reorg | 4h | Phases 1-6 |

**Parallel Opportunities:**
- Phases 1 + 5 + 6 can run in parallel (5 hours)
- Phases 2-4 sequential (13 hours)
- Phase 7 runs after all others complete (4 hours)

**Critical Path:** Phases 1 → 2 → 3 → 4 → 7 (20 hours)

---

## 🔄 Rollback Plan

### If Issues Occur
1. **Config System:** Revert to hardcoded paths (tagged commit)
2. **Auto-Discovery:** Disable feature flag, use manual registration
3. **Deep Collectors:** Toggle `deep_analysis: false` in config
4. **Dynamic UI:** Disable polling, require manual refresh
5. **Logo:** Revert to text header
6. **Tests:** Restore from git if needed
7. **Refactor:** Restore pre-refactor structure from git tag `pre-phase7-refactor`

### Rollback Commands
```bash
# Revert specific phase
git revert <commit-hash>

# Disable features via config
echo "discovery.auto_scan: false" >> dashboard-config.yaml
echo "collectors.deep_analysis: false" >> dashboard-config.yaml
```

---

## 🎓 Lessons for Future

### Design Principles Applied
- Configuration over hard-coding
- Progressive enhancement
- Fail-safe defaults
- Comprehensive monitoring

### Patterns to Reuse
- Auto-discovery pattern for other resources
- Config-driven architecture
- Dynamic UI update mechanism
- Deep vs shallow analysis toggle
- Final refactor phase for all major features
- Comprehensive cleanup checklist approach

---

## ✅ Approval Checklist

Before implementation:
- [ ] Plan reviewed by stakeholders
- [ ] Technical approach validated
- [ ] Risk mitigation strategies approved
- [ ] Timeline accepted
- [ ] Resources allocated

**Plan Status:** 🎯 Ready for Approval

**Next Steps:**
1. Review and approve this plan
2. Create GitHub issues/ADO items for each phase
3. Begin Phase 1 (Configuration System)
4. Progress tracking via plan file updates

---

**Plan File:** `cortex-brain/documents/planning/ADMIN-DASH-2025-12-06.md`  
**Maintainer:** CORTEX Development Team  
**Last Updated:** December 6, 2025
