#!/usr/bin/env python3
"""
CORTEX Autonomous Execution - Deployment Verification Script
Version: 1.0 | Date: 2026-02-09 | Authority: Phase 56 Architect
Status: Production-Ready
"""

import os
import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, List


class VerificationReport:
    """Autonomous execution deployment verification"""
    
    def __init__(self):
        self.workspace_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        self.registry_root = self.workspace_root / "cortex-registry" / "_cortex-master"
        self.phase_manager = self.workspace_root / "cortex" / "phase_management"
        self.checks: List[Dict] = []
        self.all_passed = True
        
    def verify_all(self) -> bool:
        """Run all verification checks"""
        print("\n" + "="*80)
        print("🔍 CORTEX AUTONOMOUS EXECUTION - DEPLOYMENT VERIFICATION")
        print("="*80 + "\n")
        
        # Core files
        self.check_file_exists("Executor Module", self.phase_manager / "autonomous_executor.py")
        self.check_file_exists("Execution Config", self.registry_root / "execution-queue-config.yaml")
        self.check_file_exists("Machine Registry", self.registry_root / "execution" / "machine-registry.yaml")
        self.check_file_exists("Teardown Template", self.registry_root / "directives" / "PHASE-TEARDOWN-TEMPLATE.yaml")
        
        # Documentation
        self.check_file_exists("Agent Enhancement", Path(".github/agents/core/AGENT-ENHANCEMENT-AUTONOMOUS-EXECUTION.md"))
        self.check_file_exists("README", self.registry_root / "AUTONOMOUS-EXECUTION-README.md")
        self.check_file_exists("Implementation Complete", Path("AUTONOMOUS-EXECUTION-IMPLEMENTATION-COMPLETE.md"))
        self.check_file_exists("Files Structure", Path("AUTONOMOUS-EXECUTION-FILES-STRUCTURE.md"))
        self.check_file_exists("Complete Index", Path("AUTONOMOUS-EXECUTION-COMPLETE-INDEX.md"))
        
        # YAML validation
        self.check_yaml_valid("Execution Queue Config", self.registry_root / "execution-queue-config.yaml")
        self.check_yaml_valid("Machine Registry", self.registry_root / "execution" / "machine-registry.yaml")
        
        # Python module validation
        self.check_python_module()
        
        # Phase configuration
        self.check_phase_configuration()
        
        # Machine identity
        self.check_machine_identity()
        
        # Print report
        self.print_report()
        
        return self.all_passed
    
    def check_file_exists(self, name: str, path: Path) -> None:
        """Verify file exists"""
        full_path = self.workspace_root / path if not path.is_absolute() else path
        
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            self.checks.append({
                "check": name,
                "status": "✅ PASS",
                "details": f"Found ({size_kb:.1f} KB)"
            })
        else:
            self.checks.append({
                "check": name,
                "status": "❌ FAIL",
                "details": f"Not found at {full_path}"
            })
            self.all_passed = False
    
    def check_yaml_valid(self, name: str, path: Path) -> None:
        """Verify YAML syntax"""
        full_path = self.workspace_root / path if not path.is_absolute() else path
        
        if not full_path.exists():
            self.checks.append({
                "check": f"{name} (YAML)",
                "status": "⚪ SKIP",
                "details": "File not found"
            })
            return
        
        try:
            with open(full_path) as f:
                yaml.safe_load(f)
            self.checks.append({
                "check": f"{name} (YAML)",
                "status": "✅ PASS",
                "details": "Valid YAML syntax"
            })
        except yaml.YAMLError as e:
            self.checks.append({
                "check": f"{name} (YAML)",
                "status": "❌ FAIL",
                "details": f"YAML error: {str(e)[:50]}"
            })
            self.all_passed = False
    
    def check_python_module(self) -> None:
        """Verify Python module imports"""
        try:
            sys.path.insert(0, str(self.workspace_root))
            from cortex.phase_management.autonomous_executor import (
                AutonomousPhaseExecutor,
                MachineIdentity,
                PhaseExecutionRecord,
                ExecutionCheckpoint
            )
            
            # Try to create an instance
            executor = AutonomousPhaseExecutor()
            machine = MachineIdentity.current()
            
            self.checks.append({
                "check": "Python Module Import",
                "status": "✅ PASS",
                "details": f"Executor initialized on {machine.hostname}"
            })
        except Exception as e:
            self.checks.append({
                "check": "Python Module Import",
                "status": "❌ FAIL",
                "details": f"Import error: {str(e)[:50]}"
            })
            self.all_passed = False
    
    def check_phase_configuration(self) -> None:
        """Verify phase queue configuration"""
        config_path = self.registry_root / "execution-queue-config.yaml"
        
        if not config_path.exists():
            self.checks.append({
                "check": "Phase Configuration",
                "status": "⚪ SKIP",
                "details": "Config file not found"
            })
            return
        
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            required = ["sequential_chain", "parallel_groups", "execution_records"]
            missing = [f for f in required if f not in config]
            
            if missing:
                self.checks.append({
                    "check": "Phase Configuration",
                    "status": "❌ FAIL",
                    "details": f"Missing fields: {missing}"
                })
                self.all_passed = False
            else:
                chain = config.get("sequential_chain", [])
                self.checks.append({
                    "check": "Phase Configuration",
                    "status": "✅ PASS",
                    "details": f"Valid config with {len(chain)} phases"
                })
        except Exception as e:
            self.checks.append({
                "check": "Phase Configuration",
                "status": "❌ FAIL",
                "details": f"Error: {str(e)[:50]}"
            })
            self.all_passed = False
    
    def check_machine_identity(self) -> None:
        """Verify machine identity calculation"""
        try:
            sys.path.insert(0, str(self.workspace_root))
            from cortex.phase_management.autonomous_executor import MachineIdentity
            
            identity = MachineIdentity.current()
            
            self.checks.append({
                "check": "Machine Identity",
                "status": "✅ PASS",
                "details": f"{identity.hostname} ({identity.os_type}/{identity.arch})"
            })
        except Exception as e:
            self.checks.append({
                "check": "Machine Identity",
                "status": "❌ FAIL",
                "details": f"Error: {str(e)[:50]}"
            })
            self.all_passed = False
    
    def print_report(self) -> None:
        """Print formatted verification report"""
        print("\n" + "─"*80)
        print("VERIFICATION RESULTS")
        print("─"*80)
        
        for check in self.checks:
            status = check["status"]
            check_name = check["check"]
            details = check["details"]
            print(f"{status} | {check_name:40} | {details}")
        
        print("─"*80 + "\n")
        
        if self.all_passed:
            print("✅ ALL CHECKS PASSED - SYSTEM READY FOR DEPLOYMENT\n")
            print("Next Steps:")
            print("  1. Start executor: python3 -m cortex.phase_management.autonomous_executor")
            print("  2. Monitor: tail -f cortex-registry/_cortex-master/execution/logs/execution.log")
            print("  3. Check status: cat cortex-registry/_cortex-master/execution/machine-registry.yaml\n")
        else:
            print("❌ SOME CHECKS FAILED - REVIEW ABOVE\n")
            sys.exit(1)


def main():
    """Run verification"""
    verifier = VerificationReport()
    success = verifier.verify_all()
    
    # Print summary
    total = len(verifier.checks)
    passed = sum(1 for c in verifier.checks if "✅" in c["status"])
    skipped = sum(1 for c in verifier.checks if "⚪" in c["status"])
    
    print(f"📊 Summary: {passed}/{total} passed, {skipped} skipped")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🚀 Status: {'READY' if success else 'BLOCKED'}\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
