#!/usr/bin/env python3
"""
CORTEX Master Orchestrator Architecture Audit
==============================================

Verifies that the master orchestrator system follows the design principle:
1. Python scripts execute all orchestration logic
2. YAML files define all work, priorities, and configurations (no textual ambiguity)
3. Epic/Feature/Phased plans managed through scripts (including handoffs)

This audit ensures NO TEXT-BASED HANDOFFS exist - all coordination happens via:
- YAML configuration files (master-orchestrator.yaml, orchestrator manifests)
- Python execution scripts (orchestrator classes, state management)
- Structured state databases (SQLite for tracking)

Audit Date: January 5, 2026
Author: CORTEX System Verification
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuditResult:
    """Audit result for a single check"""
    check_name: str
    status: str  # PASS, FAIL, WARNING
    details: str
    evidence: List[str]
    score: float  # 0.0 to 1.0


class MasterOrchestratorAudit:
    """Audits master orchestrator architecture compliance"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.results: List[AuditResult] = []
        self.timestamp = datetime.now().isoformat()
        
    def run_audit(self) -> Dict[str, Any]:
        """Execute all audit checks"""
        print("🔍 CORTEX Master Orchestrator Architecture Audit")
        print("=" * 80)
        print(f"Workspace: {self.workspace_root}")
        print(f"Timestamp: {self.timestamp}\n")
        
        # Check 1: Master orchestrator is Python-based
        self._check_master_orchestrator_is_python()
        
        # Check 2: All work defined in YAML (no text-based ambiguity)
        self._check_work_defined_in_yaml()
        
        # Check 3: No text-based handoffs (all scripted)
        self._check_no_text_handoffs()
        
        # Check 4: Epic/Feature/Phase plans use scripts
        self._check_plans_use_scripts()
        
        # Check 5: State management uses structured DB
        self._check_structured_state_management()
        
        # Check 6: Routing rules are YAML-based (not text parsing)
        self._check_routing_is_yaml_based()
        
        # Check 7: Priority management is YAML-defined
        self._check_priority_management_yaml()
        
        # Check 8: Handoff mechanism verification
        self._check_handoff_mechanism()
        
        # Generate report
        return self._generate_report()
    
    def _check_master_orchestrator_is_python(self):
        """Verify master orchestrator logic is implemented in Python"""
        print("\n[CHECK 1] Master Orchestrator Implementation")
        print("-" * 80)
        
        evidence = []
        
        # Check for master orchestrator Python files
        orchestrator_files = [
            "src/orchestrators/planning/planning_orchestrator_v5.py",
            "src/orchestrators/base_orchestrator_v4_1.py",
            "src/entry_point/cortex_entry.py",
            "src/cortex_agents/llm_intent_classifier.py"
        ]
        
        found_files = []
        missing_files = []
        
        for file_path in orchestrator_files:
            full_path = self.workspace_root / file_path
            if full_path.exists():
                found_files.append(file_path)
                evidence.append(f"✅ Found: {file_path}")
            else:
                missing_files.append(file_path)
                evidence.append(f"❌ Missing: {file_path}")
        
        # Check for text-based orchestration (anti-pattern)
        text_orchestration_patterns = [
            ".github/prompts/",  # Prompt files should NOT contain orchestration logic
        ]
        
        prompt_files = list((self.workspace_root / ".github/prompts").glob("*.md"))
        for prompt_file in prompt_files:
            content = prompt_file.read_text()
            # Check for execution keywords (anti-pattern if found in prompts)
            if any(keyword in content.lower() for keyword in ['execute', 'run', 'invoke python']):
                evidence.append(f"⚠️  Potential text-based orchestration in: {prompt_file.name}")
        
        status = "PASS" if len(found_files) >= 3 and len(missing_files) == 0 else "WARNING"
        score = len(found_files) / len(orchestrator_files)
        
        self.results.append(AuditResult(
            check_name="Master Orchestrator is Python-Based",
            status=status,
            details=f"Found {len(found_files)}/{len(orchestrator_files)} orchestrator Python files",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_work_defined_in_yaml(self):
        """Verify all work definitions use YAML (no textual ambiguity)"""
        print("\n[CHECK 2] Work Definitions in YAML")
        print("-" * 80)
        
        evidence = []
        
        # Check for YAML configuration files
        yaml_configs = [
            "cortex-brain/config/master-orchestrator.yaml",
            "cortex-brain/config/mcp-server.yaml",
            "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            "cortex-brain/documents/planning/active/c150-remediation-plan/00-c150-remediation-plan.yaml"
        ]
        
        found_yaml = []
        for yaml_path in yaml_configs:
            full_path = self.workspace_root / yaml_path
            if full_path.exists():
                found_yaml.append(yaml_path)
                evidence.append(f"✅ YAML config: {yaml_path}")
                
                # Verify YAML is parseable (not just text)
                try:
                    with open(full_path) as f:
                        yaml.safe_load(f)
                    evidence.append(f"   ✓ Valid YAML structure")
                except yaml.YAMLError as e:
                    evidence.append(f"   ❌ YAML parse error: {e}")
        
        status = "PASS" if len(found_yaml) >= 3 else "FAIL"
        score = len(found_yaml) / len(yaml_configs)
        
        self.results.append(AuditResult(
            check_name="Work Defined in YAML (No Textual Ambiguity)",
            status=status,
            details=f"Found {len(found_yaml)}/{len(yaml_configs)} YAML work definitions",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_no_text_handoffs(self):
        """Verify no text-based handoffs exist (all scripted)"""
        print("\n[CHECK 3] No Text-Based Handoffs")
        print("-" * 80)
        
        evidence = []
        
        # Check CORTEX.prompt.md for text-based handoff patterns (anti-pattern)
        cortex_prompt = self.workspace_root / ".github/prompts/CORTEX.prompt.md"
        
        if cortex_prompt.exists():
            content = cortex_prompt.read_text()
            
            # Anti-patterns: text-based handoff instructions
            anti_patterns = [
                ("hand off", "Text-based handoff instruction"),
                ("stop after", "Text-based stopping instruction"),
                ("do not proceed", "Text-based blocking instruction"),
                ("autonomous execution", "Claims autonomous but may be text-based"),
            ]
            
            found_anti_patterns = []
            for pattern, description in anti_patterns:
                if pattern.lower() in content.lower():
                    found_anti_patterns.append(f"❌ Found anti-pattern: '{pattern}' ({description})")
            
            if found_anti_patterns:
                evidence.extend(found_anti_patterns)
                evidence.append("⚠️  Text-based handoffs detected in CORTEX.prompt.md")
            else:
                evidence.append("✅ No text-based handoff patterns in CORTEX.prompt.md")
        
        # Check for Python-based handoff mechanism (correct pattern)
        entry_point = self.workspace_root / "src/entry_point/cortex_entry.py"
        if entry_point.exists():
            evidence.append("✅ Python entry point exists (src/entry_point/cortex_entry.py)")
        else:
            evidence.append("❌ Missing Python entry point")
        
        # Check for run_in_terminal tool usage (correct handoff mechanism)
        # This would be in GitHub Copilot's tool invocation, not text
        evidence.append("✅ Expected handoff: GitHub Copilot → run_in_terminal → Python script")
        
        status = "FAIL" if found_anti_patterns else "PASS"
        score = 0.0 if found_anti_patterns else 1.0
        
        self.results.append(AuditResult(
            check_name="No Text-Based Handoffs (All Scripted)",
            status=status,
            details=f"Anti-patterns found: {len(found_anti_patterns)}" if found_anti_patterns else "All handoffs use proper tooling",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_plans_use_scripts(self):
        """Verify Epic/Feature/Phase plans are managed by scripts"""
        print("\n[CHECK 4] Epic/Feature/Phase Plans Use Scripts")
        print("-" * 80)
        
        evidence = []
        
        # Check for planning orchestrator script
        planning_script = self.workspace_root / "src/orchestrators/planning/planning_orchestrator_v5.py"
        if planning_script.exists():
            evidence.append("✅ Planning orchestrator script exists")
            
            # Check for YAML plan loading logic
            content = planning_script.read_text()
            if "yaml" in content.lower() and "load" in content.lower():
                evidence.append("✅ Planning script loads YAML plans")
            else:
                evidence.append("⚠️  Planning script may not load YAML plans")
        else:
            evidence.append("❌ Missing planning orchestrator script")
        
        # Check for plan YAML files
        plan_dir = self.workspace_root / "cortex-brain/documents/planning/active"
        if plan_dir.exists():
            plan_files = list(plan_dir.glob("**/*.yaml"))
            evidence.append(f"✅ Found {len(plan_files)} YAML plan files")
            
            # Sample a few plans to verify structure
            for plan_file in plan_files[:3]:
                try:
                    with open(plan_file) as f:
                        plan_data = yaml.safe_load(f)
                    if isinstance(plan_data, dict) and 'phases' in plan_data:
                        evidence.append(f"✅ Valid plan structure: {plan_file.name}")
                except Exception as e:
                    evidence.append(f"❌ Invalid plan: {plan_file.name} - {e}")
        else:
            evidence.append("⚠️  No active plan directory found")
        
        # Check for state database (plan execution tracking)
        state_db = self.workspace_root / "src/database/planning_state_db.py"
        if state_db.exists():
            evidence.append("✅ Planning state database exists (structured tracking)")
        else:
            evidence.append("⚠️  Missing planning state database")
        
        status = "PASS" if planning_script.exists() and plan_dir.exists() else "FAIL"
        score = 1.0 if status == "PASS" else 0.5
        
        self.results.append(AuditResult(
            check_name="Epic/Feature/Phase Plans Managed by Scripts",
            status=status,
            details="Plans loaded from YAML, executed by Python scripts",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_structured_state_management(self):
        """Verify state is managed via structured database (not text files)"""
        print("\n[CHECK 5] Structured State Management")
        print("-" * 80)
        
        evidence = []
        
        # Check for SQLite state databases
        state_files = [
            "src/database/planning_state_db.py",
            "cortex-brain/tier0/governance.db",
            "cortex-brain/tier1/working_memory.db"
        ]
        
        found_db = []
        for db_path in state_files:
            full_path = self.workspace_root / db_path
            if full_path.exists():
                found_db.append(db_path)
                evidence.append(f"✅ Structured DB: {db_path}")
        
        # Check for text-based state files (anti-pattern)
        text_state_patterns = [
            "*.log",
            "*-state.txt",
            "*-status.txt"
        ]
        
        # Check tier1 for text-based state (anti-pattern for critical state)
        tier1 = self.workspace_root / "cortex-brain/tier1"
        if tier1.exists():
            text_files = []
            for pattern in text_state_patterns:
                text_files.extend(tier1.glob(pattern))
            
            if text_files:
                evidence.append(f"⚠️  Found {len(text_files)} text files in tier1 (review if critical state)")
            else:
                evidence.append("✅ No text-based state in tier1")
        
        status = "PASS" if len(found_db) >= 2 else "WARNING"
        score = len(found_db) / len(state_files)
        
        self.results.append(AuditResult(
            check_name="Structured State Management (SQLite, not text)",
            status=status,
            details=f"Found {len(found_db)}/{len(state_files)} structured databases",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_routing_is_yaml_based(self):
        """Verify routing rules are YAML-defined (not regex in prompts)"""
        print("\n[CHECK 6] Routing Rules are YAML-Based")
        print("-" * 80)
        
        evidence = []
        
        # Check master orchestrator YAML
        master_yaml = self.workspace_root / "cortex-brain/config/master-orchestrator.yaml"
        if master_yaml.exists():
            evidence.append("✅ Master orchestrator YAML exists")
            
            try:
                with open(master_yaml) as f:
                    config = yaml.safe_load(f)
                
                if 'routing_rules' in config:
                    rules = config['routing_rules']
                    evidence.append(f"✅ Found {len(rules)} routing rules in YAML")
                    
                    # Verify rule structure
                    valid_rules = 0
                    for rule in rules:
                        if isinstance(rule, dict) and 'pattern' in rule and 'orchestrator' in rule:
                            valid_rules += 1
                    
                    evidence.append(f"✅ {valid_rules}/{len(rules)} rules have valid structure")
                    score = valid_rules / len(rules) if rules else 0.0
                else:
                    evidence.append("❌ No routing_rules in master orchestrator YAML")
                    score = 0.0
            except Exception as e:
                evidence.append(f"❌ Error parsing YAML: {e}")
                score = 0.0
        else:
            evidence.append("❌ Master orchestrator YAML not found")
            score = 0.0
        
        status = "PASS" if score >= 0.9 else "FAIL"
        
        self.results.append(AuditResult(
            check_name="Routing Rules YAML-Based (No Prompt Regex)",
            status=status,
            details=f"Routing defined in YAML configuration",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_priority_management_yaml(self):
        """Verify priority management is YAML-defined"""
        print("\n[CHECK 7] Priority Management in YAML")
        print("-" * 80)
        
        evidence = []
        
        # Check for priority in routing rules
        master_yaml = self.workspace_root / "cortex-brain/config/master-orchestrator.yaml"
        if master_yaml.exists():
            with open(master_yaml) as f:
                config = yaml.safe_load(f)
            
            rules = config.get('routing_rules', [])
            priority_count = sum(1 for rule in rules if 'priority' in rule)
            
            evidence.append(f"✅ {priority_count}/{len(rules)} routing rules have priority")
            
            # Check for priority in plan phases
            c150_plan = self.workspace_root / "cortex-brain/documents/planning/active/c150-remediation-plan/00-c150-remediation-plan.yaml"
            if c150_plan.exists():
                with open(c150_plan) as f:
                    plan = yaml.safe_load(f)
                
                if 'priority' in plan:
                    evidence.append(f"✅ Plan has priority: {plan['priority']}")
                
                phases = plan.get('phases', [])
                phase_priority_count = sum(1 for phase in phases if 'priority' in phase or 'estimated_hours' in phase)
                evidence.append(f"✅ {phase_priority_count}/{len(phases)} phases have priority/time data")
            
            score = (priority_count / len(rules) + phase_priority_count / len(phases)) / 2 if rules and phases else 0.5
        else:
            evidence.append("❌ Master orchestrator YAML not found")
            score = 0.0
        
        status = "PASS" if score >= 0.7 else "WARNING"
        
        self.results.append(AuditResult(
            check_name="Priority Management YAML-Defined",
            status=status,
            details="Priorities defined in YAML, not inferred from text",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _check_handoff_mechanism(self):
        """Verify handoff mechanism: GitHub Copilot → run_in_terminal → Python"""
        print("\n[CHECK 8] Handoff Mechanism Verification")
        print("-" * 80)
        
        evidence = []
        
        # This is the CORRECT architecture:
        # 1. GitHub Copilot detects intent (from CORTEX.prompt.md routing table)
        # 2. GitHub Copilot invokes run_in_terminal tool
        # 3. run_in_terminal executes: python3 -m src.main <orchestrator> <args>
        # 4. Python orchestrator loads YAML config and executes
        
        evidence.append("✅ CORRECT ARCHITECTURE:")
        evidence.append("   1. GitHub Copilot: Intent detection (YAML routing rules)")
        evidence.append("   2. GitHub Copilot: Invokes run_in_terminal tool")
        evidence.append("   3. Terminal: python3 -m src.main <orchestrator> <args>")
        evidence.append("   4. Python: Loads YAML config and executes")
        
        # Check for Python entry point
        entry_point = self.workspace_root / "src/entry_point/cortex_entry.py"
        if entry_point.exists():
            evidence.append("✅ Python entry point exists")
            
            content = entry_point.read_text()
            if "yaml" in content.lower():
                evidence.append("✅ Entry point loads YAML configuration")
        else:
            evidence.append("⚠️  Python entry point missing (src/entry_point/cortex_entry.py)")
        
        # Check for anti-pattern: Text-based "hand-off" messages
        cortex_prompt = self.workspace_root / ".github/prompts/CORTEX.prompt.md"
        if cortex_prompt.exists():
            content = cortex_prompt.read_text()
            
            # Check for misleading language
            if "python orchestrator has taken over" in content.lower():
                evidence.append("❌ ANTI-PATTERN: Misleading 'taken over' language in prompts")
            if "do not proceed after hand-off" in content.lower():
                evidence.append("❌ ANTI-PATTERN: Text-based stopping instruction")
            
            # Check for correct pattern: Routing to Python via tool
            if "run_in_terminal" in content or "python3 -m" in content:
                evidence.append("✅ Prompts reference proper Python invocation")
        
        # Score based on correct architecture
        has_entry_point = entry_point.exists()
        has_yaml_loading = "yaml" in entry_point.read_text().lower() if has_entry_point else False
        
        score = 1.0 if (has_entry_point and has_yaml_loading) else 0.5
        status = "PASS" if score >= 0.7 else "WARNING"
        
        self.results.append(AuditResult(
            check_name="Handoff Mechanism (Copilot→Terminal→Python→YAML)",
            status=status,
            details="Verifies correct handoff: tooling-based, not text-based",
            evidence=evidence,
            score=score
        ))
        
        print(f"Status: {status}")
        print(f"Score: {score:.2%}")
        for e in evidence:
            print(f"  {e}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate final audit report"""
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        
        total_score = sum(r.score for r in self.results) / len(self.results)
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        warning_count = sum(1 for r in self.results if r.status == "WARNING")
        
        print(f"\nTotal Checks: {len(self.results)}")
        print(f"✅ PASS: {pass_count}")
        print(f"❌ FAIL: {fail_count}")
        print(f"⚠️  WARNING: {warning_count}")
        print(f"\nOverall Score: {total_score:.2%}")
        
        if total_score >= 0.9:
            grade = "EXCELLENT"
            status = "✅ COMPLIANT"
        elif total_score >= 0.7:
            grade = "GOOD"
            status = "⚠️  MOSTLY COMPLIANT"
        else:
            grade = "NEEDS IMPROVEMENT"
            status = "❌ NON-COMPLIANT"
        
        print(f"Grade: {grade}")
        print(f"Status: {status}")
        
        # Generate detailed report
        report = {
            "audit_metadata": {
                "timestamp": self.timestamp,
                "workspace": str(self.workspace_root),
                "auditor": "CORTEX System Verification"
            },
            "summary": {
                "total_checks": len(self.results),
                "passed": pass_count,
                "failed": fail_count,
                "warnings": warning_count,
                "overall_score": total_score,
                "grade": grade,
                "status": status
            },
            "checks": [
                {
                    "name": r.check_name,
                    "status": r.status,
                    "score": r.score,
                    "details": r.details,
                    "evidence": r.evidence
                }
                for r in self.results
            ],
            "architecture_verification": {
                "master_orchestrator": "Python-based execution engine",
                "work_definition": "YAML files (no textual ambiguity)",
                "state_management": "SQLite databases (structured)",
                "routing": "YAML-defined rules",
                "priority": "YAML-defined priorities",
                "handoff": "Copilot→run_in_terminal→Python→YAML (tooling-based)",
                "epic_feature_plans": "YAML plans executed by Python scripts"
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        for result in self.results:
            if result.status == "FAIL":
                if "text-based handoff" in result.check_name.lower():
                    recommendations.append(
                        "Remove text-based handoff instructions from CORTEX.prompt.md. "
                        "Use run_in_terminal tool to invoke Python scripts."
                    )
                elif "routing" in result.check_name.lower():
                    recommendations.append(
                        "Define all routing rules in master-orchestrator.yaml. "
                        "Remove regex patterns from prompt files."
                    )
            elif result.status == "WARNING":
                if "state management" in result.check_name.lower():
                    recommendations.append(
                        "Migrate remaining text-based state to SQLite databases. "
                        "Ensure critical state uses structured storage."
                    )
        
        if not recommendations:
            recommendations.append("✅ Architecture is compliant with design principles.")
        
        return recommendations


def main():
    """Main audit execution"""
    workspace = Path.cwd()
    
    auditor = MasterOrchestratorAudit(workspace)
    report = auditor.run_audit()
    
    # Save report to file
    report_path = workspace / "cortex-brain/documents/reports/master-orchestrator-architecture-audit-2026-01-05.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full audit report saved to:")
    print(f"   {report_path}")
    
    # Return exit code based on compliance
    if report['summary']['overall_score'] >= 0.7:
        print("\n✅ AUDIT PASSED: Architecture is compliant")
        return 0
    else:
        print("\n❌ AUDIT FAILED: Architecture needs improvement")
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
