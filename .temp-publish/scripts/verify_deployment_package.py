#!/usr/bin/env python3
"""
CORTEX Deployment Package Verification Script

Verifies that all critical CORTEX files are included in the deployment package.
Ensures brain protection, schemas, entry points, and essential docs are present.

Usage:
    python scripts/verify_deployment_package.py ./dist/cortex-user-v2.0.0
    python scripts/verify_deployment_package.py ./dist/cortex-user-v2.0.0 --verbose

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

# CRITICAL files that MUST be present in deployment package
CRITICAL_FILES = {
    # Brain Protection (Tier 0)
    'cortex-brain/protection/brain-protection-rules.yaml': 'Brain governance rules',
    
    # Database Schema (Combined)
    'cortex-brain/schema.sql': 'Combined database schema (Tier 0, 1, 2, 3)',
    
    # CORTEX Entry Points
    '.github/prompts/CORTEX.prompt.md': 'Universal CORTEX entry point',
    '.github/copilot-instructions.md': 'Baseline Copilot context',
    
    # Core Configuration
    'cortex.config.template.json': 'Configuration template',
    'cortex-operations.yaml': 'Operations manifest',
    'requirements.txt': 'Python dependencies',
    
    # Essential Documentation (user-facing only)
    'prompts/shared/story.md': 'The Intern with Amnesia story',
    'prompts/shared/setup-guide.md': 'Installation guide',
    'prompts/shared/tracking-guide.md': 'Conversation memory setup',
    'prompts/shared/technical-reference.md': 'Architecture reference',
    'prompts/shared/agents-guide.md': 'Agent system guide',
    'prompts/shared/configuration-reference.md': 'Configuration settings',
    'prompts/shared/plugin-system.md': 'Plugin development',
    'prompts/shared/operations-reference.md': 'Operations reference',
    
    # TDD Mastery Components
    'cortex-brain/documents/implementation-guides/test-strategy.yaml': 'TDD test strategy',
    'cortex-brain/templates/response-templates.yaml': 'Response templates (includes TDD workflows)',
    '.github/prompts/modules/template-guide.md': 'Template guide (TDD templates)',
    '.github/prompts/modules/response-format.md': 'Response format guide',
    '.github/prompts/modules/planning-system-guide.md': 'Planning system (DoR/DoD)',
    
    # Ambient Daemon
    'scripts/cortex/auto_capture_daemon.py': 'Ambient conversation capture daemon',
    
    # Legal
    'README.md': 'User README',
    'LICENSE': 'License terms',
}

# Core source modules that must be present
CORE_MODULES = {
    'src/tier0/brain_protector.py': 'Brain protection agent',
    'src/tier1/working_memory.py': 'Tier 1 working memory',
    'src/tier3/context_intelligence.py': 'Tier 3 context intelligence',
    'src/plugins/base_plugin.py': 'Plugin base class',
    'src/operations/base_operation_module.py': 'Operation module base class',
    'src/operations/operations_orchestrator.py': 'Operations orchestrator',
    'src/operations/optimize_operation.py': 'Optimize operation (entry point)',
    'src/operations/healthcheck_operation.py': 'Health check operation (entry point)',
    'src/feedback/feedback_collector.py': 'Feedback collector',
    'src/feedback/report_generator.py': 'Feedback report generator',
    'src/feedback/github_formatter.py': 'GitHub Issue formatter',
    'src/feedback/entry_point.py': 'Feedback entry point',
    'src/application/validation/validator_registry.py': 'Validator registry (TDD infrastructure)',
    'src/application/validation/validator.py': 'Base validator',
}

# Files that should NOT be in user package
FORBIDDEN_FILES = {
    'tests/',
    'workflow_checkpoints/',
    '.github/workflows/',
    'docs/architecture/',
    'examples/admin/',
    'scripts/admin/',
    'scripts/test_*',
    'scripts/debug_*',
    '*IMPLEMENTATION*.md',
    '*STATUS*.md',
    '*PLAN*.md',
    '*SESSION*.md',
    '*PROGRESS*.md',
    '*HOLISTIC-REVIEW*.md',
    '*LEARNING-SYSTEM*.md',
    '*CLEANUP-ORCHESTRATOR*.md',
    '*BRAIN-PROTECTION-TEST*.md',
    '*CODE-REFACTORING*.md',
    '*DOC-REFRESH*.md',
    '*E2E-WORKFLOW*.md',
    '*FILE-GENERATION*.md',
    '*HARDCODED-DATA*.md',
    '*HONEST-STATUS*.md',
    '*IMPLICIT-PART1*.md',
    '*MAC-TRACK*.md',
    '*MAC-UNIVERSAL*.md',
    '*MACOS-COMPATIBILITY*.md',
    '*MODULE-INTEGRATION*.md',
    'cortex-brain/cortex-2.0-design/',
    '*.db',  # No database files
    '*.db-journal',
    '.coverage',
    '__pycache__/',
}


def verify_bootstrap_installers(package_dir: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Verify bootstrap installers are present in publish root."""
    print("\n" + "="*80)
    print("BOOTSTRAP INSTALLERS CHECK")
    print("="*80)
    
    # Bootstrap installers should be in parent directory (publish/)
    publish_dir = package_dir.parent
    
    required_installers = {
        'install-cortex-windows.ps1': 'Windows bootstrap installer',
        'install-cortex-unix.sh': 'Unix/macOS bootstrap installer',
        'install_cortex.py': 'Python installer',
        'INSTALL.md': 'Installation guide',
    }
    
    missing = []
    present = []
    
    for installer, description in required_installers.items():
        installer_path = publish_dir / installer
        if installer_path.exists():
            present.append(installer)
            if verbose:
                print(f"OK {installer}")
                print(f"   {description}")
        else:
            missing.append(installer)
            print(f"MISSING: {installer}")
            print(f"   {description}")
    
    print(f"\n📊 Summary: {len(present)}/{len(required_installers)} bootstrap installers present")
    
    if missing:
        print(f"\nCRITICAL: {len(missing)} bootstrap installers missing!")
        return False, missing
    
    print("All bootstrap installers present")
    return True, []


def verify_critical_files(package_dir: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Verify all critical files are present."""
    print("\n" + "="*80)
    print("CRITICAL FILES VERIFICATION")
    print("="*80)
    
    missing = []
    present = []
    
    for file_path, description in CRITICAL_FILES.items():
        full_path = package_dir / file_path
        if full_path.exists():
            present.append(file_path)
            if verbose:
                print(f"✅ {file_path}")
                print(f"   {description}")
        else:
            missing.append(file_path)
            print(f"❌ MISSING: {file_path}")
            print(f"   {description}")
    
    print(f"\n📊 Summary: {len(present)}/{len(CRITICAL_FILES)} critical files present")
    
    if missing:
        print(f"\n🚨 CRITICAL: {len(missing)} files missing!")
        return False, missing
    
    print("✅ All critical files present")
    return True, []


def verify_core_modules(package_dir: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Verify core source modules are present."""
    print("\n" + "="*80)
    print("CORE MODULES VERIFICATION")
    print("="*80)
    
    missing = []
    present = []
    
    for module_path, description in CORE_MODULES.items():
        full_path = package_dir / module_path
        if full_path.exists():
            present.append(module_path)
            if verbose:
                print(f"✅ {module_path}")
                print(f"   {description}")
        else:
            missing.append(module_path)
            print(f"⚠️  MISSING: {module_path}")
            print(f"   {description}")
    
    print(f"\n📊 Summary: {len(present)}/{len(CORE_MODULES)} core modules present")
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} core modules missing")
        return False, missing
    
    print("✅ All core modules present")
    return True, []


def verify_forbidden_files(package_dir: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Verify forbidden files/directories are NOT present."""
    print("\n" + "="*80)
    print("FORBIDDEN FILES CHECK")
    print("="*80)
    
    found_forbidden = []
    
    for pattern in FORBIDDEN_FILES:
        # Check directories
        if pattern.endswith('/'):
            dir_name = pattern.rstrip('/')
            matches = list(package_dir.rglob(dir_name))
            if matches:
                for match in matches:
                    if match.is_dir():
                        found_forbidden.append(str(match.relative_to(package_dir)))
                        print(f"❌ FORBIDDEN DIR: {match.relative_to(package_dir)}")
        # Check file patterns
        elif '*' in pattern:
            matches = list(package_dir.rglob(pattern))
            if matches:
                for match in matches:
                    found_forbidden.append(str(match.relative_to(package_dir)))
                    print(f"❌ FORBIDDEN FILE: {match.relative_to(package_dir)}")
        # Check specific files
        else:
            if (package_dir / pattern).exists():
                found_forbidden.append(pattern)
                print(f"❌ FORBIDDEN: {pattern}")
    
    if not found_forbidden:
        print("✅ No forbidden files found")
        return True, []
    
    print(f"\n🚨 WARNING: {len(found_forbidden)} forbidden files/dirs found!")
    return False, found_forbidden


def calculate_package_stats(package_dir: Path) -> Dict:
    """Calculate package statistics."""
    print("\n" + "="*80)
    print("PACKAGE STATISTICS")
    print("="*80)
    
    stats = {
        'total_files': 0,
        'total_dirs': 0,
        'total_size_mb': 0.0,
        'file_types': {},
        'largest_files': []
    }
    
    all_files = list(package_dir.rglob('*'))
    
    for item in all_files:
        if item.is_dir():
            stats['total_dirs'] += 1
        elif item.is_file():
            stats['total_files'] += 1
            size = item.stat().st_size
            stats['total_size_mb'] += size / (1024 * 1024)
            
            # Track file types
            ext = item.suffix or 'no_extension'
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
            
            # Track largest files
            stats['largest_files'].append((item.relative_to(package_dir), size))
    
    # Sort largest files
    stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
    stats['largest_files'] = [(str(path), size) for path, size in stats['largest_files'][:10]]
    
    print(f"📁 Total files: {stats['total_files']}")
    print(f"📂 Total directories: {stats['total_dirs']}")
    print(f"💾 Total size: {stats['total_size_mb']:.2f} MB")
    
    print(f"\n📊 File types:")
    for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {ext}: {count}")
    
    print(f"\n📈 Largest files:")
    for file_path, size in stats['largest_files']:
        print(f"   {size/(1024*1024):.2f} MB - {file_path}")
    
    return stats


def generate_verification_report(
    package_dir: Path,
    bootstrap_ok: bool,
    bootstrap_missing: List[str],
    critical_ok: bool,
    critical_missing: List[str],
    modules_ok: bool,
    modules_missing: List[str],
    forbidden_ok: bool,
    forbidden_found: List[str],
    stats: Dict
) -> None:
    """Generate verification report JSON."""
    report = {
        'package_dir': str(package_dir),
        'timestamp': '2025-11-12',
        'verification': {
            'bootstrap_installers': {
                'passed': bootstrap_ok,
                'missing': bootstrap_missing
            },
            'critical_files': {
                'passed': critical_ok,
                'total': len(CRITICAL_FILES),
                'missing': critical_missing
            },
            'core_modules': {
                'passed': modules_ok,
                'total': len(CORE_MODULES),
                'missing': modules_missing
            },
            'forbidden_files': {
                'passed': forbidden_ok,
                'found': forbidden_found
            }
        },
        'statistics': stats,
        'overall_pass': bootstrap_ok and critical_ok and modules_ok and forbidden_ok
    }
    
    report_path = package_dir / 'VERIFICATION-REPORT.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Verification report saved: {report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify CORTEX deployment package integrity'
    )
    parser.add_argument(
        'package_dir',
        type=Path,
        help='Path to deployment package directory'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed verification output'
    )
    
    args = parser.parse_args()
    
    package_dir = args.package_dir
    
    if not package_dir.exists():
        print(f"❌ Package directory not found: {package_dir}")
        return 1
    
    print("="*80)
    print("CORTEX DEPLOYMENT PACKAGE VERIFICATION")
    print("="*80)
    print(f"Package: {package_dir}")
    print(f"Verbose: {args.verbose}")
    
    # Run verifications
    bootstrap_ok, bootstrap_missing = verify_bootstrap_installers(package_dir, args.verbose)
    critical_ok, critical_missing = verify_critical_files(package_dir, args.verbose)
    modules_ok, modules_missing = verify_core_modules(package_dir, args.verbose)
    forbidden_ok, forbidden_found = verify_forbidden_files(package_dir, args.verbose)
    stats = calculate_package_stats(package_dir)
    
    # Generate report
    generate_verification_report(
        package_dir,
        bootstrap_ok,
        bootstrap_missing,
        critical_ok,
        critical_missing,
        modules_ok,
        modules_missing,
        forbidden_ok,
        forbidden_found,
        stats
    )
    
    # Final summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    overall_pass = bootstrap_ok and critical_ok and modules_ok and forbidden_ok
    
    if bootstrap_ok:
        print("✅ Bootstrap installers: PASS")
    else:
        print(f"❌ Bootstrap installers: FAIL ({len(bootstrap_missing)} missing)")
    
    if critical_ok:
        print("✅ Critical files: PASS")
    else:
        print(f"❌ Critical files: FAIL ({len(critical_missing)} missing)")
    
    if modules_ok:
        print("✅ Core modules: PASS")
    else:
        print(f"⚠️  Core modules: PARTIAL ({len(modules_missing)} missing)")
    
    if forbidden_ok:
        print("✅ Forbidden files: PASS (none found)")
    else:
        print(f"⚠️  Forbidden files: WARNING ({len(forbidden_found)} found)")
    
    print(f"\n📦 Package size: {stats['total_size_mb']:.2f} MB")
    print(f"📁 Total files: {stats['total_files']}")
    
    print("\n" + "="*80)
    if overall_pass:
        print("✅ VERIFICATION PASSED - Package is deployment-ready!")
        print("="*80)
        return 0
    else:
        print("❌ VERIFICATION FAILED - Fix issues before deployment")
        print("="*80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
