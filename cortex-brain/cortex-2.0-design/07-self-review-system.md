# CORTEX 2.0 Self-Review System

**Document:** 07-self-review-system.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Enable CORTEX to maintain its own health through:
- Comprehensive system health checks
- Rule compliance validation
- Automated remediation of safe issues
- Performance monitoring
- Degradation detection and prevention

---

## ❌ Current Pain Points (CORTEX 1.0)

### Problem 1: No Systematic Health Checks
```
Question: "Is CORTEX working correctly?"
Current approach:
  ❌ Manual inspection of databases
  ❌ Manual test runs
  ❌ No holistic health view
  ❌ Issues discovered reactively (when something breaks)
```

### Problem 2: Rule Compliance Unknown
```
Question: "Are all 27 rules being followed?"
Current approach:
  ❌ No automated verification
  ❌ Rule #22 (Brain Protector) works, but others?
  ❌ Can't prove compliance
  ❌ Manual audit required
```

### Problem 3: No Preventive Maintenance
```
Issues discovered too late:
  - Database fragmentation at 45% (should VACUUM at 20%)
  - Knowledge graph has 127 low-confidence patterns (should prune)
  - Tier 1 has 18/20 conversations (FIFO not triggered yet)
  - 47 orphaned event logs (> 90 days old, not archived)
```

### Problem 4: No Self-Healing
```
Fixable issues require manual intervention:
  - Reindex database → Manual command
  - Archive old conversations → Manual script
  - Prune low-confidence patterns → Manual query
  - Update stale timestamps → Manual fix
```

---

## ✅ CORTEX 2.0 Solution

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│           Self-Review Engine (NEW)                        │
├──────────────────────────────────────────────────────────┤
│  • Runs comprehensive health checks                      │
│  • Validates rule compliance                             │
│  • Detects degradation patterns                          │
│  • Auto-fixes safe issues                                │
│  • Generates health reports                              │
└─────────────────────┬────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────────┐        ┌─────▼──────────┐
    │Health Monitors│        │ Rule Validators│
    ├───────────────┤        ├─────────────────┤
    │• Database     │        │• Tier 0 rules  │
    │• Performance  │        │• TDD checks    │
    │• Storage      │        │• SOLID checks  │
    │• Tests        │        │• DoR/DoD       │
    └───────┬───────┘        └────────┬────────┘
            │                         │
            └────────────┬────────────┘
                         │
            ┌────────────▼──────────────┐
            │   Auto-Fix Engine         │
            │  • Safe fixes only        │
            │  • Backup before changes  │
            │  • Rollback on failure    │
            └───────────────────────────┘
```

---

## 🏗️ Implementation: Self-Review Engine

```python
# src/maintenance/self_review.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import json

class HealthStatus(Enum):
    """Overall health status"""
    EXCELLENT = "excellent"  # 90-100% score
    GOOD = "good"            # 70-89% score
    FAIR = "fair"            # 50-69% score
    POOR = "poor"            # 30-49% score
    CRITICAL = "critical"    # <30% score

class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"    # System breaking
    HIGH = "high"            # Major degradation
    MEDIUM = "medium"        # Minor issues
    LOW = "low"              # Optimization opportunities
    INFO = "info"            # Informational

@dataclass
class HealthIssue:
    """Represents a health issue"""
    category: str
    severity: IssueSeverity
    title: str
    description: str
    detected_at: datetime
    auto_fixable: bool
    fix_description: Optional[str] = None
    impact: Optional[str] = None
    recommendation: Optional[str] = None

@dataclass
class HealthReport:
    """Complete health report"""
    timestamp: datetime
    overall_status: HealthStatus
    overall_score: float  # 0.0-1.0
    
    # Category scores
    database_score: float
    performance_score: float
    rule_compliance_score: float
    test_coverage_score: float
    storage_score: float
    
    # Issues by severity
    critical_issues: List[HealthIssue]
    high_issues: List[HealthIssue]
    medium_issues: List[HealthIssue]
    low_issues: List[HealthIssue]
    
    # Auto-fix summary
    auto_fixable_count: int
    fixed_count: int
    
    # Recommendations
    recommendations: List[str]

class SelfReviewEngine:
    """CORTEX self-review and health monitoring system"""
    
    def __init__(self, 
                 path_resolver,
                 db_connections: Dict[str, Any],
                 config: Dict[str, Any]):
        """
        Initialize self-review engine
        
        Args:
            path_resolver: Path resolution system
            db_connections: Database connections (tier1, tier2, tier3)
            config: CORTEX configuration
        """
        self.paths = path_resolver
        self.dbs = db_connections
        self.config = config
        
        # Issue tracking
        self.issues: List[HealthIssue] = []
        self.fixes_applied: List[str] = []
    
    def run_comprehensive_review(self, auto_fix: bool = False) -> HealthReport:
        """
        Run complete system health review
        
        Args:
            auto_fix: If True, automatically fix safe issues
        
        Returns:
            HealthReport with findings and scores
        """
        self.issues = []
        self.fixes_applied = []
        
        print("🔍 Running comprehensive CORTEX health review...")
        print()
        
        # Run all checks
        db_score = self._check_database_health()
        perf_score = self._check_performance()
        rule_score = self._check_rule_compliance()
        test_score = self._check_test_coverage()
        storage_score = self._check_storage_health()
        
        # Calculate overall score
        overall_score = (
            db_score * 0.25 +
            perf_score * 0.20 +
            rule_score * 0.25 +
            test_score * 0.20 +
            storage_score * 0.10
        )
        
        # Determine status
        if overall_score >= 0.90:
            status = HealthStatus.EXCELLENT
        elif overall_score >= 0.70:
            status = HealthStatus.GOOD
        elif overall_score >= 0.50:
            status = HealthStatus.FAIR
        elif overall_score >= 0.30:
            status = HealthStatus.POOR
        else:
            status = HealthStatus.CRITICAL
        
        # Apply auto-fixes if requested
        auto_fixable = [i for i in self.issues if i.auto_fixable]
        if auto_fix and auto_fixable:
            print(f"\n🔧 Applying {len(auto_fixable)} auto-fixes...")
            self._apply_auto_fixes(auto_fixable)
        
        # Group issues by severity
        critical = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
        high = [i for i in self.issues if i.severity == IssueSeverity.HIGH]
        medium = [i for i in self.issues if i.severity == IssueSeverity.MEDIUM]
        low = [i for i in self.issues if i.severity == IssueSeverity.LOW]
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return HealthReport(
            timestamp=datetime.now(),
            overall_status=status,
            overall_score=overall_score,
            database_score=db_score,
            performance_score=perf_score,
            rule_compliance_score=rule_score,
            test_coverage_score=test_score,
            storage_score=storage_score,
            critical_issues=critical,
            high_issues=high,
            medium_issues=medium,
            low_issues=low,
            auto_fixable_count=len(auto_fixable),
            fixed_count=len(self.fixes_applied),
            recommendations=recommendations
        )
    
    def _check_database_health(self) -> float:
        """Check database health (Tier 1-3)"""
        print("📊 Checking database health...")
        
        score = 1.0
        checks_passed = 0
        total_checks = 0
        
        for tier_name, db in self.dbs.items():
            # Check 1: Fragmentation
            fragmentation = self._get_fragmentation(db)
            total_checks += 1
            
            if fragmentation > 0.30:
                self.issues.append(HealthIssue(
                    category="database",
                    severity=IssueSeverity.HIGH,
                    title=f"{tier_name}: High fragmentation ({fragmentation:.0%})",
                    description=f"Database has {fragmentation:.0%} fragmentation (threshold: 20%)",
                    detected_at=datetime.now(),
                    auto_fixable=True,
                    fix_description="Run VACUUM to defragment",
                    impact="Slower queries, larger file size",
                    recommendation="VACUUM should run automatically at 20% threshold"
                ))
                score -= 0.15
            elif fragmentation > 0.20:
                self.issues.append(HealthIssue(
                    category="database",
                    severity=IssueSeverity.MEDIUM,
                    title=f"{tier_name}: Moderate fragmentation ({fragmentation:.0%})",
                    description=f"Database approaching fragmentation threshold",
                    detected_at=datetime.now(),
                    auto_fixable=True,
                    fix_description="Schedule VACUUM",
                    impact="Minor performance impact"
                ))
                score -= 0.05
            else:
                checks_passed += 1
            
            # Check 2: Index health
            total_checks += 1
            missing_indexes = self._check_indexes(db, tier_name)
            if missing_indexes:
                self.issues.append(HealthIssue(
                    category="database",
                    severity=IssueSeverity.HIGH,
                    title=f"{tier_name}: Missing indexes",
                    description=f"Missing indexes: {', '.join(missing_indexes)}",
                    detected_at=datetime.now(),
                    auto_fixable=False,
                    recommendation="Add missing indexes to schema"
                ))
                score -= 0.10
            else:
                checks_passed += 1
            
            # Check 3: Statistics freshness
            total_checks += 1
            if self._needs_analyze(db):
                self.issues.append(HealthIssue(
                    category="database",
                    severity=IssueSeverity.MEDIUM,
                    title=f"{tier_name}: Stale statistics",
                    description="Query planner statistics are outdated",
                    detected_at=datetime.now(),
                    auto_fixable=True,
                    fix_description="Run ANALYZE",
                    impact="Suboptimal query plans"
                ))
                score -= 0.05
            else:
                checks_passed += 1
            
            # Check 4: Database size
            total_checks += 1
            size_mb = self._get_db_size(db)
            expected_size = self._get_expected_size(tier_name)
            
            if size_mb > expected_size * 2:
                self.issues.append(HealthIssue(
                    category="database",
                    severity=IssueSeverity.MEDIUM,
                    title=f"{tier_name}: Unexpectedly large ({size_mb:.1f} MB)",
                    description=f"Expected ~{expected_size:.1f} MB, actual {size_mb:.1f} MB",
                    detected_at=datetime.now(),
                    auto_fixable=False,
                    recommendation="Check for data bloat or missing archival"
                ))
                score -= 0.05
            else:
                checks_passed += 1
        
        print(f"  ✓ {checks_passed}/{total_checks} database checks passed")
        return max(0.0, score)
    
    def _check_performance(self) -> float:
        """Check performance benchmarks"""
        print("⚡ Checking performance...")
        
        score = 1.0
        checks_passed = 0
        total_checks = 0
        
        # Benchmark Tier 1 queries
        total_checks += 1
        tier1_time = self._benchmark_tier1_query()
        if tier1_time > 0.050:  # 50ms threshold
            self.issues.append(HealthIssue(
                category="performance",
                severity=IssueSeverity.HIGH,
                title=f"Tier 1 queries slow ({tier1_time*1000:.0f}ms)",
                description=f"Tier 1 queries taking {tier1_time*1000:.0f}ms (threshold: 50ms)",
                detected_at=datetime.now(),
                auto_fixable=True,
                fix_description="Optimize database, rebuild indexes",
                impact="Slower conversation retrieval"
            ))
            score -= 0.20
        else:
            checks_passed += 1
        
        # Benchmark Tier 2 queries
        total_checks += 1
        tier2_time = self._benchmark_tier2_search()
        if tier2_time > 0.150:  # 150ms threshold
            self.issues.append(HealthIssue(
                category="performance",
                severity=IssueSeverity.HIGH,
                title=f"Tier 2 search slow ({tier2_time*1000:.0f}ms)",
                description=f"FTS5 search taking {tier2_time*1000:.0f}ms (threshold: 150ms)",
                detected_at=datetime.now(),
                auto_fixable=True,
                fix_description="Rebuild FTS5 index",
                impact="Slower pattern matching"
            ))
            score -= 0.20
        else:
            checks_passed += 1
        
        # Check brain update backlog
        total_checks += 1
        event_backlog = self._get_event_backlog()
        if event_backlog > 100:
            self.issues.append(HealthIssue(
                category="performance",
                severity=IssueSeverity.MEDIUM,
                title=f"Large event backlog ({event_backlog} events)",
                description="Unprocessed events accumulating",
                detected_at=datetime.now(),
                auto_fixable=True,
                fix_description="Trigger brain update",
                impact="Pattern learning delayed"
            ))
            score -= 0.10
        else:
            checks_passed += 1
        
        print(f"  ✓ {checks_passed}/{total_checks} performance checks passed")
        return max(0.0, score)
    
    def _check_rule_compliance(self) -> float:
        """Check compliance with all 27 core rules"""
        print("📜 Checking rule compliance...")
        
        score = 1.0
        checks_passed = 0
        total_checks = 27  # All rules
        
        # Load rules
        rules = self._load_tier0_rules()
        
        for rule in rules:
            compliant = self._verify_rule_compliance(rule)
            
            if compliant:
                checks_passed += 1
            else:
                severity = IssueSeverity.CRITICAL if rule.get("critical") else IssueSeverity.HIGH
                
                self.issues.append(HealthIssue(
                    category="rule_compliance",
                    severity=severity,
                    title=f"Rule #{rule['number']}: {rule['title']} - NOT COMPLIANT",
                    description=rule.get("violation_reason", "Compliance check failed"),
                    detected_at=datetime.now(),
                    auto_fixable=rule.get("auto_fixable", False),
                    fix_description=rule.get("fix_description"),
                    impact="Rule violation may degrade system"
                ))
                
                if severity == IssueSeverity.CRITICAL:
                    score -= 0.10
                else:
                    score -= 0.05
        
        print(f"  ✓ {checks_passed}/{total_checks} rules compliant")
        return max(0.0, score)
    
    def _check_test_coverage(self) -> float:
        """Check test suite health"""
        print("🧪 Checking test coverage...")
        
        score = 1.0
        
        # Run tests
        test_results = self._run_test_suite()
        
        total_tests = test_results["total"]
        passed = test_results["passed"]
        failed = test_results["failed"]
        
        if failed > 0:
            self.issues.append(HealthIssue(
                category="tests",
                severity=IssueSeverity.CRITICAL,
                title=f"{failed} tests failing",
                description=f"{failed}/{total_tests} tests are failing",
                detected_at=datetime.now(),
                auto_fixable=False,
                impact="System functionality compromised",
                recommendation="Fix failing tests immediately"
            ))
            score -= 0.50
        
        # Check coverage
        coverage = test_results.get("coverage", 1.0)
        if coverage < 0.80:
            self.issues.append(HealthIssue(
                category="tests",
                severity=IssueSeverity.MEDIUM,
                title=f"Low test coverage ({coverage:.0%})",
                description=f"Test coverage dropped to {coverage:.0%} (target: 100%)",
                detected_at=datetime.now(),
                auto_fixable=False,
                recommendation="Add tests for uncovered code"
            ))
            score -= 0.10
        
        print(f"  ✓ {passed}/{total_tests} tests passing, {coverage:.0%} coverage")
        return max(0.0, score)
    
    def _check_storage_health(self) -> float:
        """Check storage organization and cleanliness"""
        print("💾 Checking storage health...")
        
        score = 1.0
        checks_passed = 0
        total_checks = 0
        
        # Check for temp files
        total_checks += 1
        temp_files = self._find_temp_files()
        if len(temp_files) > 10:
            self.issues.append(HealthIssue(
                category="storage",
                severity=IssueSeverity.LOW,
                title=f"Excessive temp files ({len(temp_files)})",
                description="Temporary files not cleaned up",
                detected_at=datetime.now(),
                auto_fixable=True,
                fix_description="Remove temp files older than 7 days"
            ))
            score -= 0.05
        else:
            checks_passed += 1
        
        # Check for old logs
        total_checks += 1
        old_logs = self._find_old_logs(days=90)
        if len(old_logs) > 50:
            self.issues.append(HealthIssue(
                category="storage",
                severity=IssueSeverity.LOW,
                title=f"Old log files accumulating ({len(old_logs)})",
                description="Log files older than 90 days not archived",
                detected_at=datetime.now(),
                auto_fixable=True,
                fix_description="Archive or remove old logs"
            ))
            score -= 0.05
        else:
            checks_passed += 1
        
        # Check Tier 1 capacity
        total_checks += 1
        tier1_count = self._get_conversation_count()
        if tier1_count >= 18:  # Near 20 limit
            self.issues.append(HealthIssue(
                category="storage",
                severity=IssueSeverity.INFO,
                title=f"Tier 1 near capacity ({tier1_count}/20)",
                description="Working memory approaching FIFO limit",
                detected_at=datetime.now(),
                auto_fixable=False,
                impact="Oldest conversations will be archived soon"
            ))
        checks_passed += 1
        
        print(f"  ✓ {checks_passed}/{total_checks} storage checks passed")
        return max(0.0, score)
    
    def _apply_auto_fixes(self, fixable_issues: List[HealthIssue]):
        """Apply automatic fixes for safe issues"""
        for issue in fixable_issues:
            try:
                print(f"  🔧 Fixing: {issue.title}")
                
                # Create backup before fix
                self._create_backup(issue.category)
                
                # Apply fix based on category
                if "fragmentation" in issue.title.lower():
                    self._fix_fragmentation(issue)
                elif "statistics" in issue.title.lower() or "stale" in issue.title.lower():
                    self._fix_stale_stats(issue)
                elif "temp files" in issue.title.lower():
                    self._fix_temp_files(issue)
                elif "old log" in issue.title.lower():
                    self._fix_old_logs(issue)
                elif "event backlog" in issue.title.lower():
                    self._fix_event_backlog(issue)
                
                self.fixes_applied.append(issue.title)
                print(f"    ✅ Fixed")
                
            except Exception as e:
                print(f"    ❌ Fix failed: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Critical issues
        critical = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
        if critical:
            recommendations.append(
                f"⚠️  URGENT: Address {len(critical)} critical issue(s) immediately"
            )
        
        # Performance
        perf_issues = [i for i in self.issues if i.category == "performance"]
        if len(perf_issues) >= 2:
            recommendations.append(
                "⚡ Performance degradation detected - run optimization"
            )
        
        # Database maintenance
        db_issues = [i for i in self.issues if i.category == "database"]
        if len(db_issues) >= 3:
            recommendations.append(
                "📊 Schedule database maintenance (VACUUM, ANALYZE, rebuild indexes)"
            )
        
        # Rule compliance
        rule_issues = [i for i in self.issues if i.category == "rule_compliance"]
        if rule_issues:
            recommendations.append(
                f"📜 Fix {len(rule_issues)} rule compliance issue(s)"
            )
        
        # No issues
        if not self.issues:
            recommendations.append("✅ System health excellent - no action needed")
        
        return recommendations
    
    def generate_report(self, report: HealthReport) -> str:
        """Generate human-readable health report"""
        lines = ["=" * 70]
        lines.append("CORTEX HEALTH REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Overall status
        status_emoji = {
            HealthStatus.EXCELLENT: "🟢",
            HealthStatus.GOOD: "🟡",
            HealthStatus.FAIR: "🟠",
            HealthStatus.POOR: "🔴",
            HealthStatus.CRITICAL: "💀"
        }
        
        lines.append(f"Overall Status: {status_emoji[report.overall_status]} {report.overall_status.value.upper()}")
        lines.append(f"Overall Score: {report.overall_score:.1%}")
        lines.append("")
        
        # Category scores
        lines.append("Category Scores:")
        lines.append(f"  Database:       {report.database_score:.1%}")
        lines.append(f"  Performance:    {report.performance_score:.1%}")
        lines.append(f"  Rule Compliance: {report.rule_compliance_score:.1%}")
        lines.append(f"  Test Coverage:  {report.test_coverage_score:.1%}")
        lines.append(f"  Storage:        {report.storage_score:.1%}")
        lines.append("")
        
        # Issues summary
        total_issues = (
            len(report.critical_issues) +
            len(report.high_issues) +
            len(report.medium_issues) +
            len(report.low_issues)
        )
        
        if total_issues == 0:
            lines.append("✅ No issues found! System is healthy.")
        else:
            lines.append(f"Issues Found: {total_issues}")
            
            if report.critical_issues:
                lines.append("")
                lines.append(f"❌ CRITICAL ({len(report.critical_issues)}):")
                lines.append("-" * 70)
                for issue in report.critical_issues[:3]:
                    lines.append(f"  • {issue.title}")
                    if issue.description:
                        lines.append(f"    {issue.description}")
                if len(report.critical_issues) > 3:
                    lines.append(f"  ... and {len(report.critical_issues) - 3} more")
            
            if report.high_issues:
                lines.append("")
                lines.append(f"⚠️  HIGH ({len(report.high_issues)}):")
                lines.append("-" * 70)
                for issue in report.high_issues[:3]:
                    lines.append(f"  • {issue.title}")
                if len(report.high_issues) > 3:
                    lines.append(f"  ... and {len(report.high_issues) - 3} more")
            
            if report.medium_issues:
                lines.append("")
                lines.append(f"⚡ MEDIUM ({len(report.medium_issues)}):")
                for issue in report.medium_issues[:2]:
                    lines.append(f"  • {issue.title}")
                if len(report.medium_issues) > 2:
                    lines.append(f"  ... and {len(report.medium_issues) - 2} more")
        
        # Auto-fix summary
        if report.auto_fixable_count > 0:
            lines.append("")
            lines.append(f"🔧 Auto-Fixable: {report.auto_fixable_count} issue(s)")
            if report.fixed_count > 0:
                lines.append(f"   ✅ Fixed: {report.fixed_count}")
        
        # Recommendations
        if report.recommendations:
            lines.append("")
            lines.append("💡 Recommendations:")
            lines.append("-" * 70)
            for rec in report.recommendations:
                lines.append(f"  {rec}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    # Helper methods (implementations omitted for brevity)
    def _get_fragmentation(self, db) -> float: return 0.15
    def _check_indexes(self, db, tier_name) -> List[str]: return []
    def _needs_analyze(self, db) -> bool: return False
    def _get_db_size(self, db) -> float: return 10.5
    def _get_expected_size(self, tier_name) -> float: return 10.0
    def _benchmark_tier1_query(self) -> float: return 0.025
    def _benchmark_tier2_search(self) -> float: return 0.095
    def _get_event_backlog(self) -> int: return 23
    def _load_tier0_rules(self) -> List[Dict]: return []
    def _verify_rule_compliance(self, rule) -> bool: return True
    def _run_test_suite(self) -> Dict: return {"total": 60, "passed": 60, "failed": 0, "coverage": 1.0}
    def _find_temp_files(self) -> List[Path]: return []
    def _find_old_logs(self, days: int) -> List[Path]: return []
    def _get_conversation_count(self) -> int: return 8
    def _create_backup(self, category: str): pass
    def _fix_fragmentation(self, issue): pass
    def _fix_stale_stats(self, issue): pass
    def _fix_temp_files(self, issue): pass
    def _fix_old_logs(self, issue): pass
    def _fix_event_backlog(self, issue): pass
```

---

## 🔌 Plugin Integration

```python
# src/plugins/self_review_plugin.py

from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from maintenance.self_review import SelfReviewEngine

class Plugin(BasePlugin):
    """Self-review and health monitoring plugin"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="self_review_plugin",
            name="Self-Review System",
            version="1.0.0",
            category=PluginCategory.MAINTENANCE,
            priority=PluginPriority.HIGH,
            description="Comprehensive health checks and auto-remediation",
            author="CORTEX",
            dependencies=[],
            hooks=[
                HookPoint.ON_SELF_REVIEW.value,
                HookPoint.ON_STARTUP.value
            ],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        self.review_engine = SelfReviewEngine(
            path_resolver=self.config["path_resolver"],
            db_connections=self.config["db_connections"],
            config=self.config
        )
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute self-review"""
        
        auto_fix = context.get("auto_fix", False)
        
        # Run comprehensive review
        report = self.review_engine.run_comprehensive_review(auto_fix=auto_fix)
        
        # Generate report text
        report_text = self.review_engine.generate_report(report)
        
        return {
            "success": True,
            "report": report_text,
            "status": report.overall_status.value,
            "score": report.overall_score,
            "issues": len(report.critical_issues) + len(report.high_issues)
        }
```

---

## 📊 CLI Commands

```bash
# Run health check
python scripts/cortex-health.py

# Run with auto-fix
python scripts/cortex-health.py --auto-fix

# Generate detailed report
python scripts/cortex-health.py --report --output health-report.txt

# Check specific category
python scripts/cortex-health.py --category database
python scripts/cortex-health.py --category performance
python scripts/cortex-health.py --category rules

# Schedule periodic review (cron)
0 2 * * * python scripts/cortex-health.py --auto-fix --quiet
```

---

## ⏰ Scheduled Reviews

```yaml
# Recommended schedule
daily:
  time: "02:00"
  command: "cortex-health.py --auto-fix --quiet"
  actions:
    - Check database health
    - Apply safe auto-fixes
    - Archive old logs

weekly:
  time: "Sunday 03:00"
  command: "cortex-health.py --full --report"
  actions:
    - Comprehensive review
    - Generate detailed report
    - Email to admins

monthly:
  time: "1st Sunday 04:00"
  command: "cortex-health.py --deep-analysis"
  actions:
    - Deep pattern analysis
    - Long-term trend review
    - Capacity planning
```

---

## ✅ Benefits

### 1. Proactive Health Monitoring
```
Before: Issue discovered when system breaks
After: Issue detected 2 weeks early, auto-fixed
```

### 2. Automated Remediation
```
Fragmentation at 25%:
  ✅ Auto-detected
  ✅ VACUUM scheduled
  ✅ Fixed overnight
  ✅ Performance restored
```

### 3. Rule Compliance Validation
```
All 27 rules checked automatically:
  ✅ Rule #1-21: Compliant
  ⚠️  Rule #22: Brain Protector - 1 violation
  ✅ Rule #23-27: Compliant

Action: Review Rule #22 violation
```

### 4. Continuous Quality
```
Daily health checks ensure:
  - Database stays optimized
  - Performance stays fast
  - Rules stay followed
  - Tests stay passing
```

---

**Next:** 08-database-maintenance.md (Auto-optimization, archival, retention policies)
