# EPM Health Audit - Integration Design

**Version:** 1.0  
**Status:** DRAFT  
**Author:** Asif Hussain  
**Date:** 2025-11-14

## 🎯 Overview

Design for integrating the Health Audit feature into the existing EPM (Execution Plan Module) system, providing seamless command registration, workflow orchestration, and user experience.

## 🏗️ EPM Integration Architecture

### Current EPM System Analysis

```
Existing EPM Structure:
├── EPM Core Engine
├── Command Registry
├── Workflow Orchestration
├── Progress Tracking
├── Output Management
└── Plugin Integration Layer
```

### Health Audit Integration Points

```
EPM Health Audit Integration:
├── Command Registration
│   ├── Primary Command: /health-audit
│   ├── Aliases: /health, /audit, /diagnose
│   └── Natural Language: "check system health", "run health audit"
├── Workflow Integration
│   ├── Pre-execution Validation
│   ├── Progress Reporting
│   ├── Cancellation Support
│   └── Result Caching
├── Output Management
│   ├── Markdown Report Generation
│   ├── JSON Export Option
│   ├── HTML Dashboard (future)
│   └── Email/Slack Notifications (future)
└── Plugin System Integration
    ├── Scanner Plugin Registration
    ├── Custom Issue Detectors
    └── Report Format Plugins
```

## 🔌 Command Registration

### Primary Command Structure

```python
@register_epm_command
class HealthAuditCommand:
    """Comprehensive CORTEX system health analysis"""
    
    command = "/health-audit"
    aliases = ["/health", "/audit", "/diagnose"]
    natural_language_patterns = [
        "check system health",
        "run health audit", 
        "diagnose issues",
        "scan for problems",
        "analyze system health"
    ]
    
    def __init__(self):
        self.scanner_framework = HealthScannerFramework()
        self.report_generator = HealthReportGenerator()
        self.issue_classifier = IssueClassificationEngine()
    
    def execute(self, context: EPMContext, options: HealthAuditOptions) -> EPMResult:
        """Execute health audit with EPM integration"""
        return self._run_health_audit(context, options)
```

### Command Options

```python
@dataclass
class HealthAuditOptions:
    """Configuration options for health audit command"""
    
    # Scope Control
    tiers: List[str] = None              # ["tier0", "tier1", "tier2", "tier3"]
    components: List[str] = None         # ["agents", "plugins", "tests"]
    
    # Filter Control  
    min_severity: str = "info"           # "critical", "high", "medium", "low", "info"
    categories: List[str] = None         # Specific issue categories
    
    # Output Control
    output_format: str = "markdown"      # "markdown", "json", "html"
    output_file: str = None              # Custom output path
    include_suggestions: bool = True     # Include fix suggestions
    include_dependencies: bool = True    # Include dependency analysis
    
    # Execution Control
    quick_scan: bool = False            # Skip deep analysis
    parallel_execution: bool = True     # Run scanners in parallel
    timeout: int = 300                  # Max execution time (seconds)
    
    # Advanced Options
    historical_comparison: bool = True   # Compare with previous runs
    export_baseline: bool = False       # Save as baseline for future comparisons
    auto_fix: List[str] = []            # Auto-fix categories (if available)
```

## 🔄 Workflow Integration

### EPM Workflow Phases

```python
class HealthAuditWorkflow(EPMWorkflow):
    """Health audit workflow integrated with EPM orchestration"""
    
    def get_phases(self) -> List[WorkflowPhase]:
        return [
            ValidationPhase(),      # Pre-execution validation
            ScanningPhase(),       # Run health scanners
            AnalysisPhase(),       # Analyze and classify issues
            ReportingPhase(),      # Generate reports
            ActionPhase(),         # Suggest/execute fixes
            CleanupPhase()         # Post-execution cleanup
        ]
    
    def get_estimated_duration(self, options: HealthAuditOptions) -> timedelta:
        """Estimate total execution time based on options"""
        if options.quick_scan:
            return timedelta(minutes=2)
        elif options.tiers and len(options.tiers) == 1:
            return timedelta(minutes=5)
        else:
            return timedelta(minutes=15)
```

### Phase Implementation

#### 1. Validation Phase

```python
class ValidationPhase(WorkflowPhase):
    """Validate system readiness for health audit"""
    
    def execute(self, context: EPMContext) -> PhaseResult:
        validations = [
            self._check_cortex_installation(),
            self._verify_dependencies(),
            self._validate_permissions(),
            self._check_disk_space(),
            self._verify_scanner_availability()
        ]
        
        return PhaseResult(
            success=all(v.success for v in validations),
            data={"validations": validations},
            next_phase="scanning" if all_valid else None
        )
```

#### 2. Scanning Phase

```python
class ScanningPhase(WorkflowPhase):
    """Execute health scanners across all tiers"""
    
    def execute(self, context: EPMContext) -> PhaseResult:
        scanner_framework = HealthScannerFramework()
        
        # Get enabled scanners based on options
        scanners = scanner_framework.get_scanners(
            tiers=context.options.tiers,
            components=context.options.components
        )
        
        # Execute scanners (parallel or sequential)
        if context.options.parallel_execution:
            results = self._execute_parallel(scanners, context)
        else:
            results = self._execute_sequential(scanners, context)
        
        return PhaseResult(
            success=True,
            data={"scan_results": results},
            progress={"completed": len(results), "total": len(scanners)}
        )
```

#### 3. Analysis Phase

```python
class AnalysisPhase(WorkflowPhase):
    """Analyze scan results and classify issues"""
    
    def execute(self, context: EPMContext) -> PhaseResult:
        classifier = IssueClassificationEngine()
        scan_results = context.get_phase_data("scanning")["scan_results"]
        
        # Classify and prioritize issues
        classified_issues = []
        for scanner_result in scan_results:
            for raw_issue in scanner_result.issues:
                classified_issue = classifier.classify(raw_issue)
                classified_issues.append(classified_issue)
        
        # Generate priority matrix and dependency analysis
        priority_matrix = self._generate_priority_matrix(classified_issues)
        dependencies = self._analyze_dependencies(classified_issues)
        
        return PhaseResult(
            success=True,
            data={
                "classified_issues": classified_issues,
                "priority_matrix": priority_matrix,
                "dependencies": dependencies
            }
        )
```

#### 4. Reporting Phase

```python
class ReportingPhase(WorkflowPhase):
    """Generate health audit reports"""
    
    def execute(self, context: EPMContext) -> PhaseResult:
        report_generator = HealthReportGenerator()
        analysis_data = context.get_phase_data("analysis")
        
        # Generate reports in requested formats
        reports = {}
        
        if context.options.output_format in ["markdown", "all"]:
            reports["markdown"] = report_generator.generate_markdown_report(
                analysis_data, context.options
            )
        
        if context.options.output_format in ["json", "all"]:
            reports["json"] = report_generator.generate_json_report(
                analysis_data, context.options
            )
        
        # Save reports to files
        output_files = self._save_reports(reports, context.options)
        
        return PhaseResult(
            success=True,
            data={
                "reports": reports,
                "output_files": output_files
            }
        )
```

## 📊 Progress Tracking Integration

### Real-time Progress Updates

```python
class HealthAuditProgressTracker(EPMProgressTracker):
    """Track health audit progress with EPM system"""
    
    def __init__(self, context: EPMContext):
        super().__init__("health-audit", context)
        self.scanner_progress = {}
        
    def on_scanner_start(self, scanner_name: str):
        """Called when a scanner starts"""
        self.scanner_progress[scanner_name] = {
            "status": "running",
            "start_time": datetime.now(),
            "progress": 0
        }
        self.emit_progress_update()
    
    def on_scanner_progress(self, scanner_name: str, progress: int):
        """Called when scanner reports progress"""
        if scanner_name in self.scanner_progress:
            self.scanner_progress[scanner_name]["progress"] = progress
            self.emit_progress_update()
    
    def on_scanner_complete(self, scanner_name: str, issues_found: int):
        """Called when scanner completes"""
        self.scanner_progress[scanner_name].update({
            "status": "completed",
            "end_time": datetime.now(),
            "progress": 100,
            "issues_found": issues_found
        })
        self.emit_progress_update()
    
    def get_overall_progress(self) -> ProgressUpdate:
        """Calculate overall progress across all scanners"""
        if not self.scanner_progress:
            return ProgressUpdate(phase="validation", progress=0)
        
        total_progress = sum(s["progress"] for s in self.scanner_progress.values())
        avg_progress = total_progress / len(self.scanner_progress)
        
        return ProgressUpdate(
            phase="scanning",
            progress=avg_progress,
            details={
                "scanners": self.scanner_progress,
                "estimated_completion": self._estimate_completion()
            }
        )
```

### User Experience

```bash
# Example command execution with progress
$ cortex health-audit --tiers tier1,tier2 --output-format markdown

🧠 CORTEX Health Audit Starting...

✅ Validation Phase (2s)
  ✅ CORTEX installation verified
  ✅ Dependencies available  
  ✅ Permissions validated
  ✅ Disk space sufficient
  ✅ 8 scanners ready

🔄 Scanning Phase (15s estimated)
  ✅ Tier1MemoryScanner      [████████████████████] 100% (3 issues)
  🔄 Tier2KnowledgeScanner   [████████████▌       ] 65%  (12 issues so far)
  ⏳ AgentSystemScanner     [██████              ] 30%
  ⏳ PluginScanner          [                    ] 0%
  ⏳ TestCoverageScanner    [                    ] 0%
  ⏳ DocumentationScanner   [                    ] 0%
  ⏳ ConfigurationScanner   [                    ] 0%
  ⏳ SecurityScanner        [                    ] 0%

🔄 Analysis Phase (3s estimated)
  🔄 Classifying 47 issues found...
  🔄 Building priority matrix...
  🔄 Analyzing dependencies...

📊 Reporting Phase (2s estimated)
  🔄 Generating Markdown report...
  💾 Saving to: cortex-health-audit-2025-11-14-15-30-42.md

✅ Health Audit Complete! (22s total)

📊 Summary: 47 issues found (2 critical, 8 high, 23 medium, 14 low)
📄 Report: cortex-health-audit-2025-11-14-15-30-42.md
🎯 Next: Review critical issues first, then follow action plan
```

## 🔧 Output Management Integration

### File Management

```python
class HealthAuditOutputManager(EPMOutputManager):
    """Manage health audit outputs within EPM framework"""
    
    def __init__(self, base_output_dir: Path):
        super().__init__(base_output_dir)
        self.health_audit_dir = base_output_dir / "health-audits"
        self.health_audit_dir.mkdir(exist_ok=True)
    
    def generate_output_filename(self, options: HealthAuditOptions) -> str:
        """Generate standardized filename for health audit"""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        scope = self._generate_scope_suffix(options)
        format_ext = self._get_format_extension(options.output_format)
        
        return f"cortex-health-audit-{timestamp}{scope}.{format_ext}"
    
    def save_report(self, report_content: str, options: HealthAuditOptions) -> Path:
        """Save health audit report with proper organization"""
        filename = options.output_file or self.generate_output_filename(options)
        output_path = self.health_audit_dir / filename
        
        # Save main report
        output_path.write_text(report_content)
        
        # Create symlink to latest
        latest_link = self.health_audit_dir / f"latest.{self._get_format_extension(options.output_format)}"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(filename)
        
        return output_path
```

### Result Caching

```python
class HealthAuditCache(EPMCache):
    """Cache health audit results for performance and comparison"""
    
    def __init__(self, cache_dir: Path):
        super().__init__(cache_dir / "health-audit-cache")
        self.max_cached_results = 10
    
    def get_cache_key(self, options: HealthAuditOptions) -> str:
        """Generate cache key for health audit configuration"""
        key_components = [
            options.tiers or ["all"],
            options.components or ["all"],
            options.min_severity,
            options.quick_scan
        ]
        return hashlib.sha256(str(key_components).encode()).hexdigest()[:16]
    
    def get_cached_result(self, options: HealthAuditOptions) -> Optional[HealthAuditResult]:
        """Get cached result if available and not stale"""
        cache_key = self.get_cache_key(options)
        cached_file = self.cache_dir / f"{cache_key}.json"
        
        if cached_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cached_file.stat().st_mtime)
            if cache_age < timedelta(hours=1):  # Cache valid for 1 hour
                return HealthAuditResult.from_json(cached_file.read_text())
        
        return None
    
    def cache_result(self, result: HealthAuditResult, options: HealthAuditOptions):
        """Cache health audit result"""
        cache_key = self.get_cache_key(options)
        cached_file = self.cache_dir / f"{cache_key}.json"
        
        # Save result with metadata
        cache_data = {
            "result": result.to_dict(),
            "cached_at": datetime.now().isoformat(),
            "options": options.__dict__
        }
        
        cached_file.write_text(json.dumps(cache_data, indent=2))
        self._cleanup_old_cache()
```

## 🔌 Plugin System Integration

### Scanner Plugin Interface

```python
class HealthScannerPlugin(EPMPlugin):
    """Base class for health scanner plugins"""
    
    def register_scanners(self) -> List[Type[BaseHealthScanner]]:
        """Register health scanners provided by this plugin"""
        raise NotImplementedError
    
    def get_issue_types(self) -> List[IssueTypeDefinition]:
        """Define custom issue types this plugin can detect"""
        return []
    
    def get_fix_suggestions(self) -> List[FixSuggestionProvider]:
        """Provide automated fix suggestions for issues"""
        return []
```

### Custom Scanner Registration

```python
# Example custom scanner plugin
class GitHealthScannerPlugin(HealthScannerPlugin):
    """Plugin providing Git-specific health scanners"""
    
    def register_scanners(self) -> List[Type[BaseHealthScanner]]:
        return [
            GitBranchHealthScanner,
            GitCommitQualityScanner,
            GitIgnoreScanner,
            GitHookScanner
        ]
    
    def get_issue_types(self) -> List[IssueTypeDefinition]:
        return [
            IssueTypeDefinition(
                type_id="GIT_BRANCH_DIVERGENCE",
                category="GIT_HEALTH",
                severity_range=[Severity.MEDIUM, Severity.HIGH],
                description="Branch has diverged significantly from main"
            )
        ]
```

## 🎯 Natural Language Integration

### Command Routing

```python
class HealthAuditNLProcessor(EPMNaturalLanguageProcessor):
    """Process natural language health audit requests"""
    
    def get_intent_patterns(self) -> List[IntentPattern]:
        return [
            IntentPattern(
                intent="health_audit_full",
                patterns=[
                    "check system health",
                    "run full health audit", 
                    "diagnose all issues",
                    "scan entire system"
                ],
                default_options=HealthAuditOptions()
            ),
            IntentPattern(
                intent="health_audit_quick", 
                patterns=[
                    "quick health check",
                    "fast system scan",
                    "brief health audit"
                ],
                default_options=HealthAuditOptions(quick_scan=True)
            ),
            IntentPattern(
                intent="health_audit_tier",
                patterns=[
                    "check tier {tier} health",
                    "scan {tier} for issues",
                    "audit {tier} system"
                ],
                option_extractors={"tier": self._extract_tier}
            )
        ]
    
    def _extract_tier(self, text: str) -> List[str]:
        """Extract tier specification from natural language"""
        tier_map = {
            "governance": ["tier0"],
            "memory": ["tier1"], 
            "knowledge": ["tier2"],
            "context": ["tier3"],
            "agents": ["agents"],
            "plugins": ["plugins"]
        }
        
        for keyword, tiers in tier_map.items():
            if keyword in text.lower():
                return tiers
        
        return None
```

## 🚀 Future Enhancements

### Planned Integrations

1. **VS Code Extension Integration**
   - Health status in status bar
   - Issue highlights in code
   - Quick fix suggestions

2. **CI/CD Pipeline Integration**
   - Automated health checks on commits
   - Health gate for deployments
   - Trend monitoring

3. **Team Collaboration**
   - Shared health dashboards
   - Issue assignment workflows
   - Progress tracking across team

4. **AI-Powered Analysis**
   - ML-based issue prediction
   - Automated root cause analysis
   - Intelligent fix suggestions

---

## 📋 Implementation Checklist

### Phase 1: Core Integration
- [ ] Implement HealthAuditCommand with EPM registration
- [ ] Create HealthAuditWorkflow with all phases
- [ ] Add progress tracking integration
- [ ] Implement output management

### Phase 2: Enhanced Features  
- [ ] Add result caching system
- [ ] Implement plugin scanner support
- [ ] Create natural language processing
- [ ] Add historical comparison

### Phase 3: Advanced Features
- [ ] VS Code extension integration
- [ ] CI/CD pipeline support
- [ ] Team collaboration features
- [ ] AI-powered analysis

---

**Next Steps:**
1. Review integration design with EPM architecture
2. Begin Phase 1 implementation
3. Create integration tests
4. Validate with existing CORTEX workflows