"""Create SKULL Rule Coverage Matrix"""
import re
from pathlib import Path
from collections import defaultdict

# Get tier0_instincts (rule names) from brain-protection-rules.yaml
tier0_instincts = [
    "INCREMENTAL_PLAN_GENERATION",
    "TDD_ENFORCEMENT",
    "RED_PHASE_VALIDATION",
    "GREEN_PHASE_VALIDATION",
    "REFACTOR_CODE_CLEANUP_ENFORCEMENT",
    "HOLISTIC_CODE_DISCOVERY_ENFORCEMENT",
    "TDD_TEST_FILE_VALIDATION",
    "TDD_EMPTY_TEST_DETECTION",
    "FILE_ORGANIZATION_ENFORCEMENT",
    "TIERED_PLANNING_ENFORCEMENT",
    "MANDATORY_PLANNING_ENFORCEMENT",
    "PLAN_ARTIFACT_LOCATION_ENFORCEMENT",
    "VACUUM_CYCLE_ENFORCEMENT",
    "INCREMENTAL_PLAN_CREATION_ENFORCEMENT",
    "PROGRESS_TRACKER_ENFORCEMENT",
    "SENIOR_DEVELOPER_ESTIMATE_ENFORCEMENT",
    "BIDIRECTIONAL_LINKING_ENFORCEMENT",
    "AUTOMATIC_DOCUMENTATION_GENERATION",
    "DEFINITION_OF_READY",
    "DEFINITION_OF_DONE",
    "SOLID_PRINCIPLES",
    "SOLID_SRP",
    "SOLID_DIP",
    "CODE_STYLE_CONSISTENCY",
    "LOCAL_FIRST",
    "BRAIN_PROTECTION_TESTS_MANDATORY",
    "MACHINE_READABLE_FORMATS",
    "SKULL_TEST_BEFORE_CLAIM",
    "SKULL_INTEGRATION_VERIFICATION",
    "SKULL_VISUAL_REGRESSION",
    "SKULL_RETRY_WITHOUT_LEARNING",
    "SKULL_TRANSFORMATION_VERIFICATION",
    "SKULL_PRIVACY_PROTECTION",
    "SKULL_FACULTY_INTEGRITY",
    "GIT_ISOLATION_ENFORCEMENT",
    "DISTRIBUTED_DATABASE_ARCHITECTURE",
    "CORTEX_PROMPT_FILE_PROTECTION",
    "GIT_CHECKPOINT_ENFORCEMENT",
    "PREVENT_DIRTY_STATE_WORK",
    "GIT_COMMIT_PRIVACY_VALIDATION",
    "SECURITY_INJECTION",
    "SECURITY_AUTHENTICATION",
    "THREAT_MODELING_ENFORCEMENT",
    "BRAIN_ARCHITECTURE_INTEGRITY",
    "DEPLOYMENT_VERSION_TRACKING",
    "UPGRADE_BRAIN_PRESERVATION",
    "SCHEMA_MIGRATION_ENFORCEMENT",
    "TEST_LOCATION_SEPARATION",
    "DOCUMENT_ORGANIZATION_ENFORCEMENT",
    "GIT_HISTORY_CONTEXT_REQUIRED",
    "API_DOCUMENTATION_REQUIRED",
    "OPERATIONAL_READINESS_ENFORCEMENT",
    "DEBUG_MARKER_REMOVAL_ENFORCEMENT",
    "ALIGNMENT_STATE_PROTECTION",
    "INLINE_CSS_PROHIBITION",
    "AUTONOMOUS_EXECUTION_PROTECTION",
    "INTERACTIVE_MODE_ENFORCEMENT",
    "TOKEN_OPTIMIZATION_ENFORCEMENT",
    "GIT_CHECKPOINT_PHASE_PROTECTION",
    "NO_EMOJIS_IN_SCRIPTS",
    "KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT",
    "VISION_API_INTEGRATION_ENFORCEMENT",
    "CONTINUOUS_RISK_ANALYSIS_ENFORCEMENT"
]

# Scan test files for rule references
test_root = Path('tests')
rule_coverage = defaultdict(list)

for test_file in test_root.rglob('*.py'):
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for rule in tier0_instincts:
                if rule in content:
                    # Extract test names from this file
                    test_funcs = re.findall(r'def (test_\w+)', content)
                    rule_coverage[rule].append({
                        'file': str(test_file.relative_to(test_root)),
                        'tests': test_funcs
                    })
    except Exception:
        pass

# Generate coverage report
report_lines = []
report_lines.append("# 🛡️ SKULL Rules Coverage Matrix\n")
report_lines.append(f"**Generated:** 2025-12-31\n")
report_lines.append(f"**Total Rules:** {len(tier0_instincts)}\n")
report_lines.append(f"**Covered Rules:** {len(rule_coverage)}\n")
report_lines.append(f"**Coverage:** {len(rule_coverage)/len(tier0_instincts)*100:.1f}%\n\n")

report_lines.append("| Rule | Has Test | Test Files | Status |\n")
report_lines.append("|------|----------|------------|--------|\n")

for rule in tier0_instincts:
    if rule in rule_coverage:
        files = ', '.join(set(item['file'] for item in rule_coverage[rule]))
        if len(files) > 60:
            files = files[:57] + '...'
        status = '✅'
        has_test = 'Yes'
    else:
        files = 'N/A'
        status = '❌'
        has_test = 'No'
    
    report_lines.append(f"| {rule} | {has_test} | {files} | {status} |\n")

report_lines.append(f"\n## 📊 Summary\n\n")
report_lines.append(f"- **Total Rules:** {len(tier0_instincts)}\n")
report_lines.append(f"- **Covered:** {len(rule_coverage)}\n")
report_lines.append(f"- **Missing:** {len(tier0_instincts) - len(rule_coverage)}\n")
report_lines.append(f"- **Coverage:** {len(rule_coverage)/len(tier0_instincts)*100:.1f}%\n\n")

report_lines.append("## ❌ Rules Without Test Coverage\n\n")
for rule in tier0_instincts:
    if rule not in rule_coverage:
        report_lines.append(f"- {rule}\n")

# Write report
report_file = Path('cortex-brain/documents/reports/skull-coverage-matrix.md')
report_file.parent.mkdir(parents=True, exist_ok=True)
with open(report_file, 'w', encoding='utf-8') as f:
    f.writelines(report_lines)

print(f"✅ Coverage matrix generated: {report_file}")
print(f"\n📊 Quick Summary:")
print(f"   Total Rules: {len(tier0_instincts)}")
print(f"   Covered: {len(rule_coverage)}")
print(f"   Missing: {len(tier0_instincts) - len(rule_coverage)}")
print(f"   Coverage: {len(rule_coverage)/len(tier0_instincts)*100:.1f}%")
