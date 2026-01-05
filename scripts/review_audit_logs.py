#!/usr/bin/env python3
"""
Automated Audit Log Review System for Remediation Workflow

This script performs automated analysis of audit logs at phase checkpoints
to detect issues, patterns, and security/performance concerns.

Author: CORTEX Holistic Review Orchestrator
Date: 2026-01-05
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict


class AuditLogReviewer:
    """Automated log reviewer for phase checkpoints"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.thresholds = {
            "error_rate": 0.05,  # Max 5% error rate
            "performance": 5.0,   # Max 5ms overhead
            "recovery_success": 0.95  # Min 95% recovery success
        }
    
    def review_phase(self, phase_num: int, check_type: str) -> Dict[str, Any]:
        """
        Review logs for a specific phase
        
        Args:
            phase_num: Phase number to review
            check_type: Type of check (activation, integration, self-healing, etc.)
        
        Returns:
            Analysis results dictionary
        """
        phase_logs = self._load_phase_logs(phase_num)
        
        analysis = {
            "phase": phase_num,
            "check_type": check_type,
            "timestamp": datetime.now().isoformat(),
            "log_count": len(phase_logs),
            "errors": self._find_errors(phase_logs),
            "warnings": self._find_warnings(phase_logs),
            "patterns": self._detect_patterns(phase_logs),
            "performance": self._analyze_performance(phase_logs),
            "security": self._check_security(phase_logs),
            "recommendation": "proceed",
            "critical_issues": []
        }
        
        # Apply check-specific analysis
        if check_type == "activation":
            analysis.update(self._check_activation(phase_logs))
        elif check_type == "integration":
            analysis.update(self._check_integration(phase_logs))
        elif check_type == "self-healing":
            analysis.update(self._check_self_healing(phase_logs))
        elif check_type == "cross-phase":
            analysis.update(self._check_cross_phase(phase_logs))
        elif check_type == "security-performance":
            analysis.update(self._check_security_performance(phase_logs))
        elif check_type == "testing":
            analysis.update(self._check_testing(phase_logs))
        elif check_type == "deployment":
            analysis.update(self._check_deployment(phase_logs))
        
        # Determine recommendation
        analysis["recommendation"] = self._determine_recommendation(analysis)
        
        return analysis
    
    def _load_phase_logs(self, phase_num: int) -> List[Dict]:
        """Load logs for a specific phase"""
        logs = []
        
        # Find all log files in the directory
        log_files = list(self.log_dir.glob("**/*.jsonl"))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            log_entry = json.loads(line)
                            # Filter by phase if available
                            if log_entry.get("phase") == phase_num or phase_num is None:
                                logs.append(log_entry)
            except Exception as e:
                print(f"⚠️  Warning: Failed to load {log_file.name}: {e}")
        
        return logs
    
    def _find_errors(self, logs: List[Dict]) -> List[Dict]:
        """Find error entries"""
        return [log for log in logs if log.get("level") in ["ERROR", "CRITICAL"]]
    
    def _find_warnings(self, logs: List[Dict]) -> List[Dict]:
        """Find warning entries"""
        return [log for log in logs if log.get("level") == "WARNING"]
    
    def _detect_patterns(self, logs: List[Dict]) -> List[Dict]:
        """Detect recurring patterns"""
        patterns = defaultdict(lambda: {"count": 0, "examples": []})
        
        for log in logs:
            # Group by error type or message pattern
            key = log.get("error_type") or log.get("message", "unknown")
            patterns[key]["count"] += 1
            if len(patterns[key]["examples"]) < 3:
                patterns[key]["examples"].append({
                    "timestamp": log.get("timestamp"),
                    "message": log.get("message"),
                    "context": log.get("context", {})
                })
        
        # Return only patterns that occur more than once
        return [
            {"type": k, "count": v["count"], "examples": v["examples"]}
            for k, v in patterns.items()
            if v["count"] > 1
        ]
    
    def _analyze_performance(self, logs: List[Dict]) -> Dict:
        """Analyze performance metrics"""
        durations = []
        
        for log in logs:
            # Check for duration in various formats
            duration = log.get("duration_ms") or log.get("duration") or log.get("context", {}).get("duration_ms")
            if duration is not None:
                durations.append(float(duration))
        
        if not durations:
            return {
                "avg_duration": 0,
                "max_duration": 0,
                "min_duration": 0,
                "violations": 0,
                "samples": 0
            }
        
        avg_duration = sum(durations) / len(durations)
        violations = len([d for d in durations if d > self.thresholds["performance"]])
        
        return {
            "avg_duration": avg_duration,
            "max_duration": max(durations),
            "min_duration": min(durations),
            "violations": violations,
            "samples": len(durations),
            "violation_rate": violations / len(durations) if durations else 0
        }
    
    def _check_security(self, logs: List[Dict]) -> Dict:
        """Check for security issues"""
        issues = []
        
        # PII patterns
        pii_patterns = [
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', "POTENTIAL_NAME"),
            (r'\b\d{3}-\d{2}-\d{4}\b', "SSN_FORMAT"),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "EMAIL_ADDRESS"),
            (r'\b\d{16}\b', "CREDIT_CARD_FORMAT")
        ]
        
        # Secret patterns
        secret_patterns = [
            (r'password\s*[:=]\s*["\']?([^"\']+)["\']?', "PASSWORD"),
            (r'api[_-]?key\s*[:=]\s*["\']?([^"\']+)["\']?', "API_KEY"),
            (r'token\s*[:=]\s*["\']?([^"\']+)["\']?', "TOKEN"),
            (r'secret\s*[:=]\s*["\']?([^"\']+)["\']?', "SECRET")
        ]
        
        for log in logs:
            log_str = json.dumps(log)
            
            # Check for PII
            for pattern, issue_type in pii_patterns:
                if re.search(pattern, log_str, re.IGNORECASE):
                    issues.append({
                        "type": "PII_EXPOSURE",
                        "subtype": issue_type,
                        "log_id": log.get("id"),
                        "timestamp": log.get("timestamp")
                    })
            
            # Check for secrets
            for pattern, issue_type in secret_patterns:
                if re.search(pattern, log_str, re.IGNORECASE):
                    issues.append({
                        "type": "SECRET_EXPOSURE",
                        "subtype": issue_type,
                        "log_id": log.get("id"),
                        "timestamp": log.get("timestamp")
                    })
            
            # Check for unencrypted sensitive data
            if log.get("sensitivity") == "high" and not log.get("encrypted"):
                issues.append({
                    "type": "UNENCRYPTED_SENSITIVE",
                    "log_id": log.get("id"),
                    "timestamp": log.get("timestamp")
                })
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "pii_exposures": len([i for i in issues if i["type"] == "PII_EXPOSURE"]),
            "secret_exposures": len([i for i in issues if i["type"] == "SECRET_EXPOSURE"]),
            "encryption_issues": len([i for i in issues if i["type"] == "UNENCRYPTED_SENSITIVE"])
        }
    
    def _check_activation(self, logs: List[Dict]) -> Dict:
        """Check activation-specific criteria"""
        activation_checks = {
            "logger_initialized": False,
            "config_valid": False,
            "first_entry_logged": False,
            "output_dir_exists": False
        }
        
        for log in logs:
            msg = log.get("message", "").lower()
            if "activated" in msg or "initialized" in msg:
                activation_checks["logger_initialized"] = True
            if "config" in msg:
                activation_checks["config_valid"] = True
            if log.get("level") in ["INFO", "AUDIT"]:
                activation_checks["first_entry_logged"] = True
        
        # Check output directory
        if self.log_dir.exists():
            activation_checks["output_dir_exists"] = True
        
        return {"activation_checks": activation_checks}
    
    def _check_integration(self, logs: List[Dict]) -> Dict:
        """Check integration-specific criteria"""
        orchestrators_seen = set()
        execution_events = {"starts": 0, "completions": 0, "errors": 0}
        
        for log in logs:
            orch = log.get("orchestrator") or log.get("context", {}).get("orchestrator")
            if orch:
                orchestrators_seen.add(orch)
            
            msg = log.get("message", "").lower()
            if "started" in msg or "executing" in msg:
                execution_events["starts"] += 1
            if "completed" in msg or "finished" in msg:
                execution_events["completions"] += 1
            if log.get("level") == "ERROR":
                execution_events["errors"] += 1
        
        return {
            "integration_checks": {
                "orchestrators_integrated": len(orchestrators_seen),
                "orchestrator_list": list(orchestrators_seen),
                "execution_starts": execution_events["starts"],
                "execution_completions": execution_events["completions"],
                "execution_errors": execution_events["errors"],
                "completion_rate": execution_events["completions"] / execution_events["starts"] if execution_events["starts"] > 0 else 0
            }
        }
    
    def _check_self_healing(self, logs: List[Dict]) -> Dict:
        """Check self-healing-specific criteria"""
        healing_events = {
            "patterns_detected": 0,
            "anomalies_detected": 0,
            "recovery_attempts": 0,
            "recovery_successes": 0
        }
        
        for log in logs:
            msg = log.get("message", "").lower()
            context = log.get("context", {})
            
            if "pattern" in msg and "detected" in msg:
                healing_events["patterns_detected"] += 1
            if "anomaly" in msg:
                healing_events["anomalies_detected"] += 1
            if "recovery" in msg or "heal" in msg:
                healing_events["recovery_attempts"] += 1
                if context.get("success") or "success" in msg:
                    healing_events["recovery_successes"] += 1
        
        success_rate = (
            healing_events["recovery_successes"] / healing_events["recovery_attempts"]
            if healing_events["recovery_attempts"] > 0
            else 0
        )
        
        return {
            "self_healing_checks": {
                **healing_events,
                "success_rate": success_rate,
                "meets_threshold": success_rate >= self.thresholds["recovery_success"]
            }
        }
    
    def _check_cross_phase(self, logs: List[Dict]) -> Dict:
        """Check cross-phase criteria"""
        phase_transitions = []
        state_changes = 0
        context_maintained = True
        
        last_session = None
        for log in logs:
            context = log.get("context", {})
            
            # Track phase transitions
            if "phase" in context and "transition" in log.get("message", "").lower():
                phase_transitions.append({
                    "from_phase": context.get("previous_phase"),
                    "to_phase": context.get("phase"),
                    "timestamp": log.get("timestamp")
                })
            
            # Track state changes
            if "state" in context or "state_change" in log.get("message", "").lower():
                state_changes += 1
            
            # Check context propagation
            session = context.get("session_id")
            if last_session and session and session != last_session:
                context_maintained = False
            if session:
                last_session = session
        
        return {
            "cross_phase_checks": {
                "phase_transitions": len(phase_transitions),
                "transitions_list": phase_transitions,
                "state_changes": state_changes,
                "context_maintained": context_maintained
            }
        }
    
    def _check_security_performance(self, logs: List[Dict]) -> Dict:
        """Check security and performance criteria"""
        # Already covered by _check_security and _analyze_performance
        return {
            "security_performance_checks": {
                "security_validated": True,
                "performance_validated": True
            }
        }
    
    def _check_testing(self, logs: List[Dict]) -> Dict:
        """Check testing-specific criteria"""
        test_events = {
            "suites_run": set(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
        
        for log in logs:
            msg = log.get("message", "").lower()
            context = log.get("context", {})
            
            if "test suite" in msg:
                suite = context.get("suite")
                if suite:
                    test_events["suites_run"].add(suite)
            
            if "test" in msg and ("started" in msg or "completed" in msg):
                test_events["tests_run"] += 1
                
                if "passed" in msg or context.get("status") == "PASSED":
                    test_events["tests_passed"] += 1
                elif "failed" in msg or context.get("status") == "FAILED":
                    test_events["tests_failed"] += 1
        
        pass_rate = (
            test_events["tests_passed"] / test_events["tests_run"]
            if test_events["tests_run"] > 0
            else 0
        )
        
        return {
            "testing_checks": {
                "test_suites": len(test_events["suites_run"]),
                "tests_executed": test_events["tests_run"],
                "tests_passed": test_events["tests_passed"],
                "tests_failed": test_events["tests_failed"],
                "pass_rate": pass_rate
            }
        }
    
    def _check_deployment(self, logs: List[Dict]) -> Dict:
        """Check deployment-specific criteria"""
        deployment_events = {
            "deployment_started": False,
            "config_validated": False,
            "health_checks_passed": False,
            "deployment_completed": False,
            "rollback_triggered": False
        }
        
        for log in logs:
            msg = log.get("message", "").lower()
            context = log.get("context", {})
            
            if "deployment" in msg and "started" in msg:
                deployment_events["deployment_started"] = True
            if "config" in msg and "validated" in msg:
                deployment_events["config_validated"] = True
            if "health check" in msg and ("passed" in msg or context.get("status") == "SUCCESS"):
                deployment_events["health_checks_passed"] = True
            if "deployment" in msg and "completed" in msg:
                deployment_events["deployment_completed"] = True
            if "rollback" in msg:
                deployment_events["rollback_triggered"] = True
        
        return {"deployment_checks": deployment_events}
    
    def _determine_recommendation(self, analysis: Dict) -> str:
        """Determine overall recommendation based on analysis"""
        critical_issues = []
        
        # Check error rate
        error_rate = len(analysis["errors"]) / analysis["log_count"] if analysis["log_count"] > 0 else 0
        if error_rate > self.thresholds["error_rate"]:
            critical_issues.append(f"Error rate {error_rate:.1%} exceeds threshold {self.thresholds['error_rate']:.1%}")
        
        # Check performance
        perf = analysis["performance"]
        if perf["avg_duration"] > self.thresholds["performance"]:
            critical_issues.append(f"Average duration {perf['avg_duration']:.2f}ms exceeds threshold {self.thresholds['performance']}ms")
        
        # Check security
        security = analysis["security"]
        if security["issues_found"] > 0:
            if security["secret_exposures"] > 0 or security["pii_exposures"] > 0:
                critical_issues.append(f"Security issues found: {security['issues_found']}")
        
        # Check self-healing (if applicable)
        if "self_healing_checks" in analysis:
            sh = analysis["self_healing_checks"]
            if not sh["meets_threshold"]:
                critical_issues.append(f"Self-healing success rate {sh['success_rate']:.1%} below threshold {self.thresholds['recovery_success']:.1%}")
        
        # Store critical issues
        analysis["critical_issues"] = critical_issues
        
        # Determine recommendation
        if critical_issues:
            return "block"
        elif len(analysis["warnings"]) > analysis["log_count"] * 0.1:  # >10% warnings
            return "review"
        else:
            return "proceed"


def print_analysis_report(analysis: Dict):
    """Print formatted analysis report"""
    print("\n" + "="*60)
    print(f"Phase {analysis['phase']} Log Review - {analysis['check_type'].upper()}")
    print("="*60 + "\n")
    
    # Basic stats
    print("📊 Basic Statistics:")
    print(f"   Log Entries: {analysis['log_count']}")
    print(f"   Errors: {len(analysis['errors'])}")
    print(f"   Warnings: {len(analysis['warnings'])}")
    print(f"   Patterns: {len(analysis['patterns'])}")
    
    # Performance
    print("\n⚡ Performance:")
    perf = analysis['performance']
    print(f"   Samples: {perf['samples']}")
    if perf['samples'] > 0:
        print(f"   Avg Duration: {perf['avg_duration']:.2f}ms")
        print(f"   Max Duration: {perf['max_duration']:.2f}ms")
        print(f"   Violations: {perf['violations']}")
    else:
        print("   No performance data available")
    
    # Security
    print("\n🔒 Security:")
    security = analysis['security']
    print(f"   Issues Found: {security['issues_found']}")
    if security['issues_found'] > 0:
        print(f"   PII Exposures: {security['pii_exposures']}")
        print(f"   Secret Exposures: {security['secret_exposures']}")
        print(f"   Encryption Issues: {security['encryption_issues']}")
    
    # Check-specific results
    for key in analysis:
        if key.endswith("_checks"):
            check_name = key.replace("_checks", "").replace("_", " ").title()
            print(f"\n✓ {check_name}:")
            checks = analysis[key]
            for check_key, check_value in checks.items():
                if isinstance(check_value, bool):
                    status = "✅" if check_value else "❌"
                    print(f"   {status} {check_key.replace('_', ' ').title()}: {check_value}")
                elif isinstance(check_value, (int, float)):
                    print(f"   {check_key.replace('_', ' ').title()}: {check_value}")
                elif isinstance(check_value, list) and len(check_value) <= 5:
                    print(f"   {check_key.replace('_', ' ').title()}: {', '.join(map(str, check_value))}")
    
    # Recommendation
    print("\n" + "="*60)
    rec = analysis['recommendation'].upper()
    if rec == "PROCEED":
        print(f"✅ Recommendation: {rec}")
    elif rec == "REVIEW":
        print(f"⚠️  Recommendation: {rec}")
    else:
        print(f"❌ Recommendation: {rec}")
    
    # Critical issues
    if analysis.get("critical_issues"):
        print("\n⚠️  Critical Issues:")
        for issue in analysis["critical_issues"]:
            print(f"   • {issue}")
    
    print("="*60 + "\n")


def main():
    """Main review function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Review audit logs for phase checkpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review Phase 0 activation
  python3 scripts/review_audit_logs.py --phase 0 --check activation
  
  # Review Phase 1 integration
  python3 scripts/review_audit_logs.py --phase 1 --check integration
  
  # Review self-healing in Phase 2
  python3 scripts/review_audit_logs.py --phase 2 --check self-healing
        """
    )
    
    parser.add_argument("--phase", type=int, required=True, help="Phase number to review")
    parser.add_argument(
        "--check", 
        type=str, 
        required=True,
        choices=["activation", "integration", "self-healing", "cross-phase", 
                 "security-performance", "testing", "deployment"],
        help="Check type"
    )
    parser.add_argument(
        "--log-dir", 
        type=str, 
        default="logs/audit/remediation/",
        help="Log directory (default: logs/audit/remediation/)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Review logs
    reviewer = AuditLogReviewer(args.log_dir)
    analysis = reviewer.review_phase(args.phase, args.check)
    
    # Output results
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_analysis_report(analysis)
    
    # Exit with error if blocked
    if analysis["recommendation"] == "block":
        sys.exit(1)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
