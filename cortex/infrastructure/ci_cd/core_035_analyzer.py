#!/usr/bin/env python3
"""
CORE-035 Remediation Script
Maps all duplicate registry imports and validates consolidation plan
"""

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


class Core035Analyzer:
    """Analyze CORE-035 duplicates and generate remediation steps."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.duplicates = {
            'TemplateRegistry': [
                'cortex/orchestrators/response/response_templates.py',
                'cortex/brain/core/template_engine.py',
                'cortex/tools/scaffolder_templates.py',
            ],
            'OrchestratorDependencyRegistry': [
                'cortex/brain/core/orchestrator_dependency_registry.py',
                'cortex/core/orchestrator_dependency_registry.py',
            ],
            'EventRegistry': [
                'cortex/brain/core/orchestrator/terminal_events.py',
                'cortex/core/orchestrator/terminal_events.py',
            ],
            'DomainPluginRegistry': [
                'cortex/brain/domain_orchestrators/business/plugins.py',
                'cortex/domain_orchestrators/business/plugins.py',
            ],
            'GovernanceRegistry': [
                'cortex/brain/core/governance_registry.py',
                'cortex/orchestrators/core/governance_registry.py',
            ],
            'OrchestratorRegistry': [
                'cortex/orchestrators/registry/__init__.py',
                'cortex/orchestrators/registry/discovery_engine.py',
                'cortex/brain/core/decorators/orchestrator.py',
            ],
            'IGovernanceRegistry': [
                'cortex/brain/core/interfaces/i_audit_logger.py',
                'cortex/brain/core/interfaces.py',
            ],
        }

        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.canonical = {
            'TemplateRegistry': 'cortex/tools/scaffolder_templates.py',
            'OrchestratorDependencyRegistry': 'cortex/core/orchestrator_dependency_registry.py',
            'EventRegistry': 'cortex/core/orchestrator/terminal_events.py',
            'DomainPluginRegistry': 'cortex/domain_orchestrators/business/plugins.py',
            'GovernanceRegistry': 'cortex/orchestrators/core/governance_registry.py',
            'OrchestratorRegistry': 'cortex/orchestrators/registry/__init__.py',
            'IGovernanceRegistry': 'cortex/brain/core/interfaces.py',
        }

    def find_imports(self) -> Dict[str, Set[str]]:
        """Find all imports of duplicate classes."""
        imports = defaultdict(set)

        # Scan all Python files for imports
        for py_file in self.repo_root.rglob('*.py'):
            if '.pytest_cache' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for class_name in self.duplicates.keys():
                    # Find imports like "from ... import ClassName"
                    pattern = rf'from\s+[\w.]+\s+import\s+.*\b{class_name}\b'
                    if re.search(pattern, content):
                        rel_path = str(py_file.relative_to(self.repo_root))
                        imports[class_name].add(rel_path)

            except Exception as e:
                print(f"Error reading {py_file}: {e}")

        self.imports = imports
        return imports

    def generate_report(self) -> str:
        """Generate remediation report."""
        report = []
        report.append("=" * 80)
        report.append("CORE-035 REMEDIATION ANALYSIS")
        report.append("=" * 80)
        report.append("")

        for class_name in sorted(self.duplicates.keys()):
            locations = self.duplicates[class_name]
            canonical = self.canonical[class_name]
            importers = self.imports.get(class_name, set())

            report.append(f"\n### {class_name}")
            report.append(f"Status: {len(locations)} locations (1 canonical + {len(locations)-1} duplicates)")
            report.append(f"Canonical: {canonical}")
            report.append("")
            report.append("Locations:")
            for loc in locations:
                marker = "✅ CANONICAL" if loc == canonical else "❌ DUPLICATE"
                report.append(f"  {marker}: {loc}")

            report.append("")
            report.append(f"Imported by ({len(importers)} files):")
            if importers:
                for importer in sorted(importers):
                    report.append(f"  - {importer}")
            else:
                report.append("  (No imports found)")

            report.append("")

        report.append("=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)
        report.append(f"Total duplicates: {len(self.duplicates)}")
        report.append(f"Total duplicate locations: {sum(len(locs)-1 for locs in self.duplicates.values())}")
        report.append(f"Total files affected: {sum(len(importers) for importers in self.imports.values())}")

        return "\n".join(report)

    def print_report(self):
        """Print the analysis report."""
        print(self.generate_report())

if __name__ == '__main__':
    analyzer = Core035Analyzer('/Users/asifhussain/PROJECTS/CORTEX')
    analyzer.find_imports()
    analyzer.print_report()

    print("\n\n" + "=" * 80)
    print("USAGE")
    print("=" * 80)
    print("""
Execute remediation phases:

Phase 8.1 - Template Registry Renames:
  python cortex/ci_cd/phase_8_1_template_renames.py

Phase 8.2 - Dependency Registry Consolidation:
  python cortex/ci_cd/phase_8_2_dependency_consolidation.py

Phase 8.3 - Registry Consolidation:
  python cortex/ci_cd/phase_8_3_registry_consolidation.py

Phase 8.4 - Validation:
  python cortex/ci_cd/phase_8_4_validation.py

Full remediation:
  python cortex/ci_cd/core_035_full_remediation.py
""")
