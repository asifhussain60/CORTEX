"""Test ambient daemon check integration in optimize orchestrator"""

from src.operations.modules.optimize.optimize_cortex_orchestrator import OptimizeCortexOrchestrator

# Create orchestrator
orchestrator = OptimizeCortexOrchestrator()

# Run optimization
print("\n" + "="*80)
print("Testing Ambient Daemon Check Integration")
print("="*80 + "\n")

result = orchestrator.execute({'profile': 'quick', 'scan_coverage': False})

# Print results
health_report = result.data.get('health_report', {})
stats = health_report.get('statistics', {})

print("\n" + "="*80)
print("AMBIENT DAEMON STATUS")
print("="*80)
print(f"Daemon Running: {stats.get('ambient_daemon_running', 'unknown')}")
if 'ambient_daemon_pid' in stats:
    print(f"Daemon PID: {stats['ambient_daemon_pid']}")
print()

# Check for daemon-related issues
daemon_issues = [
    issue for issue in health_report.get('issues', [])
    if issue.get('category') == 'daemon'
]

if daemon_issues:
    print("Daemon Issues Found:")
    for issue in daemon_issues:
        print(f"  - {issue['title']}")
        print(f"    Severity: {issue['severity']}")
        print(f"    Recommendation: {issue['recommendation']}")
        print()
else:
    print("✅ No daemon issues found")
    print()

print("="*80)
print(f"Overall Health: {health_report.get('overall_health', 'unknown').upper()}")
print(f"Health Score: {health_report.get('health_score', 0):.1f}/100")
print(f"Total Issues: {len(health_report.get('issues', []))}")
print("="*80 + "\n")
