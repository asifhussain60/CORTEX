"""
Project Reference Validator - Validates .csproj references match Clean Architecture rules

Purpose:
    Ensure project references follow Clean Architecture dependency rules:
    - Domain has NO references
    - Use Case references Domain ONLY
    - Internal Infrastructure references Domain ONLY
    - External Infrastructure references Use Case + (optional) Domain
    - Presentation references Domain + Use Case (code), ALL (DI setup allowed)

Usage:
    python scripts/architecture/project_reference_validator.py --solution Platform.Classic.sln
    python scripts/architecture/project_reference_validator.py --project RA.DomainCore/RA.DomainCore.csproj
    python scripts/architecture/project_reference_validator.py --domain RA

Author: Asif Hussain (CORTEX)
Version: 1.0
"""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum


class LayerType(Enum):
    """Clean Architecture layer types"""
    DOMAIN = "DomainCore"
    USE_CASE = "UseCase"
    INTERNAL_INFRA = "Data"
    EXTERNAL_INFRA = "Client"
    PRESENTATION = "Host"


@dataclass
class ProjectReference:
    """Represents a project reference"""
    from_project: str
    to_project: str
    from_layer: LayerType
    to_layer: LayerType


@dataclass
class ReferenceViolation:
    """Represents an invalid project reference"""
    from_project: str
    to_project: str
    from_layer: LayerType
    to_layer: LayerType
    reason: str
    severity: str  # ERROR, WARNING


class ProjectReferenceValidator:
    """Validates project references against Clean Architecture rules"""
    
    # Dependency rules: {from_layer: [allowed_to_layers]}
    DEPENDENCY_RULES = {
        LayerType.DOMAIN: [],  # Domain can't reference anything
        LayerType.USE_CASE: [LayerType.DOMAIN],
        LayerType.INTERNAL_INFRA: [LayerType.DOMAIN],
        LayerType.EXTERNAL_INFRA: [LayerType.USE_CASE, LayerType.DOMAIN],
        LayerType.PRESENTATION: [LayerType.DOMAIN, LayerType.USE_CASE]  # Code only
    }
    
    # Presentation can reference infrastructure for DI setup (warning, not error)
    PRESENTATION_DI_ALLOWED = [LayerType.INTERNAL_INFRA, LayerType.EXTERNAL_INFRA]
    
    def __init__(self):
        self.violations: List[ReferenceViolation] = []
        self.warnings: List[ReferenceViolation] = []
        self.valid_references: List[ProjectReference] = []
    
    def _get_layer_type(self, project_name: str) -> LayerType:
        """Determine layer type from project name"""
        if '.DomainCore' in project_name:
            return LayerType.DOMAIN
        elif '.UseCase' in project_name:
            return LayerType.USE_CASE
        elif '.Data.' in project_name:
            return LayerType.INTERNAL_INFRA
        elif '.Client.' in project_name:
            return LayerType.EXTERNAL_INFRA
        elif '.Host' in project_name or '.Api.' in project_name or '.Jobs.' in project_name:
            return LayerType.PRESENTATION
        
        raise ValueError(f"Cannot determine layer type for project: {project_name}")
    
    def _parse_project_references(self, csproj_path: Path) -> List[str]:
        """Extract ProjectReference elements from .csproj file"""
        try:
            tree = ET.parse(csproj_path)
            root = tree.getroot()
            
            references = []
            for item_group in root.findall('.//ItemGroup'):
                for proj_ref in item_group.findall('ProjectReference'):
                    include = proj_ref.get('Include')
                    if include:
                        # Extract project name from path
                        project_name = Path(include).stem
                        references.append(project_name)
            
            return references
        
        except Exception as e:
            print(f"Error parsing {csproj_path}: {e}")
            return []
    
    def validate_project(self, csproj_path: Path) -> List[ReferenceViolation]:
        """Validate references in a single project"""
        violations = []
        
        project_name = csproj_path.stem
        
        try:
            from_layer = self._get_layer_type(project_name)
        except ValueError as e:
            print(f"Skipping {project_name}: {e}")
            return violations
        
        referenced_projects = self._parse_project_references(csproj_path)
        
        for ref_project in referenced_projects:
            try:
                to_layer = self._get_layer_type(ref_project)
            except ValueError:
                # Not a Clean Architecture project, skip
                continue
            
            # Check if reference is allowed
            allowed_layers = self.DEPENDENCY_RULES.get(from_layer, [])
            
            if to_layer not in allowed_layers:
                # Special case: Presentation can reference infrastructure for DI
                if from_layer == LayerType.PRESENTATION and to_layer in self.PRESENTATION_DI_ALLOWED:
                    self.warnings.append(ReferenceViolation(
                        from_project=project_name,
                        to_project=ref_project,
                        from_layer=from_layer,
                        to_layer=to_layer,
                        reason=f"{from_layer.value} → {to_layer.value} allowed ONLY for DI setup in Startup/Program.cs",
                        severity="WARNING"
                    ))
                else:
                    violations.append(ReferenceViolation(
                        from_project=project_name,
                        to_project=ref_project,
                        from_layer=from_layer,
                        to_layer=to_layer,
                        reason=f"{from_layer.value} layer cannot reference {to_layer.value} layer",
                        severity="ERROR"
                    ))
            else:
                self.valid_references.append(ProjectReference(
                    from_project=project_name,
                    to_project=ref_project,
                    from_layer=from_layer,
                    to_layer=to_layer
                ))
        
        self.violations.extend(violations)
        return violations
    
    def validate_solution(self, solution_path: Path, domain_filter: str = None) -> List[ReferenceViolation]:
        """Validate all projects in a solution"""
        violations = []
        
        # Find all .csproj files
        for csproj in solution_path.parent.rglob('*.csproj'):
            # Filter by domain if specified
            if domain_filter and domain_filter not in str(csproj):
                continue
            
            violations.extend(self.validate_project(csproj))
        
        return violations
    
    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 80)
        report.append("PROJECT REFERENCE VALIDATION REPORT")
        report.append("=" * 80)
        
        # Summary
        total_refs = len(self.valid_references) + len(self.violations) + len(self.warnings)
        report.append(f"\nTotal References Checked: {total_refs}")
        report.append(f"✅ Valid: {len(self.valid_references)}")
        report.append(f"⚠️  Warnings: {len(self.warnings)}")
        report.append(f"❌ Errors: {len(self.violations)}")
        
        # Errors
        if self.violations:
            report.append("\n" + "=" * 80)
            report.append("❌ ERRORS (Must Fix)")
            report.append("=" * 80)
            
            for v in self.violations:
                report.append(f"\n{v.from_project} ({v.from_layer.value})")
                report.append(f"  → references → {v.to_project} ({v.to_layer.value})")
                report.append(f"  Reason: {v.reason}")
                report.append(f"  Fix: Remove this reference and use abstraction/interface")
        
        # Warnings
        if self.warnings:
            report.append("\n" + "=" * 80)
            report.append("⚠️  WARNINGS (Review for DI-only usage)")
            report.append("=" * 80)
            
            for w in self.warnings:
                report.append(f"\n{w.from_project} ({w.from_layer.value})")
                report.append(f"  → references → {w.to_project} ({w.to_layer.value})")
                report.append(f"  Note: {w.reason}")
                report.append(f"  Ensure: Only used in Startup.cs/Program.cs for DI registration")
        
        # Valid References Summary
        if self.valid_references:
            report.append("\n" + "=" * 80)
            report.append("✅ VALID REFERENCES")
            report.append("=" * 80)
            
            # Group by layer
            by_layer: Dict[LayerType, List[ProjectReference]] = {}
            for ref in self.valid_references:
                by_layer.setdefault(ref.from_layer, []).append(ref)
            
            for layer in [LayerType.USE_CASE, LayerType.INTERNAL_INFRA, 
                         LayerType.EXTERNAL_INFRA, LayerType.PRESENTATION]:
                refs = by_layer.get(layer, [])
                if refs:
                    report.append(f"\n{layer.value} layer ({len(refs)} references):")
                    for ref in refs:
                        report.append(f"  ✓ {ref.from_project} → {ref.to_project}")
        
        # Architecture compliance score
        if total_refs > 0:
            compliance_score = ((len(self.valid_references) + len(self.warnings)) / total_refs) * 100
            report.append("\n" + "=" * 80)
            report.append(f"ARCHITECTURE COMPLIANCE: {compliance_score:.1f}%")
            report.append("=" * 80)
            
            if compliance_score == 100:
                report.append("✅ Perfect compliance!")
            elif compliance_score >= 90:
                report.append("✅ Good compliance (review warnings)")
            elif compliance_score >= 75:
                report.append("⚠️  Needs improvement")
            else:
                report.append("❌ Critical violations - refactoring required")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Validate project references against Clean Architecture rules"
    )
    parser.add_argument('--solution', help='Path to .sln file')
    parser.add_argument('--project', help='Path to .csproj file')
    parser.add_argument('--domain', help='Filter by domain (e.g., RA, Finance)')
    parser.add_argument('--output', help='Output report file (optional)')
    
    args = parser.parse_args()
    
    if not (args.solution or args.project):
        parser.error("Must specify --solution or --project")
    
    validator = ProjectReferenceValidator()
    
    if args.project:
        violations = validator.validate_project(Path(args.project))
    elif args.solution:
        violations = validator.validate_solution(Path(args.solution), args.domain)
    
    report = validator.generate_report()
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {args.output}")
    
    # Exit with error code if violations found
    exit(1 if violations else 0)


if __name__ == '__main__':
    main()
