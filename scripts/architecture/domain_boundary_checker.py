"""
Domain Boundary Checker - Validates Clean Architecture layer boundaries

Purpose:
    Detect violations of Clean Architecture principles:
    - Entity exposure (domain entities in API responses)
    - Layer dependency violations (Domain → Infrastructure, etc.)
    - Cross-domain entity exposure
    - Project reference violations

Usage:
    python scripts/architecture/domain_boundary_checker.py --project RA.Api.Host
    python scripts/architecture/domain_boundary_checker.py --solution Platform.Classic.sln
    python scripts/architecture/domain_boundary_checker.py --file Controllers/FundingInvoiceController.cs

Author: Asif Hussain (CORTEX)
Version: 1.0
"""

import argparse
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ViolationType(Enum):
    """Types of boundary violations"""
    ENTITY_EXPOSURE = "Entity Exposure"
    LAYER_DEPENDENCY = "Layer Dependency Violation"
    CROSS_DOMAIN = "Cross-Domain Entity Exposure"
    PROJECT_REFERENCE = "Invalid Project Reference"


@dataclass
class Violation:
    """Represents a single boundary violation"""
    violation_type: ViolationType
    file_path: str
    line_number: int
    description: str
    severity: str  # ERROR, WARNING
    suggestion: str


class DomainBoundaryChecker:
    """Checks for Clean Architecture boundary violations"""
    
    # Prohibited entities that should never be exposed directly
    CROSS_DOMAIN_ENTITIES = [
        'Employer', 'EmployerPlan', 'EmployerGroup',
        'Member', 'MemberEnrollment', 'MemberDemographics',
        'Plan', 'PlanBenefit', 'BenefitGroup',
        'PayrollSchedule', 'PayrollDeduction'
    ]
    
    # Layer dependency rules (what can reference what)
    ALLOWED_DEPENDENCIES = {
        'DomainCore': [],  # Domain can't reference anything
        'UseCase': ['DomainCore'],
        'Data': ['DomainCore'],
        'Client': ['UseCase', 'DomainCore'],
        'Api.Host': ['DomainCore', 'UseCase'],  # Code only
        'Jobs.Host': ['DomainCore', 'UseCase']
    }
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.violations: List[Violation] = []
    
    def check_file(self, file_path: Path) -> List[Violation]:
        """Check a single C# file for violations"""
        violations = []
        
        if not file_path.suffix == '.cs':
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check for entity exposure in return types
                violations.extend(self._check_entity_exposure(file_path, line_num, line))
                
                # Check for cross-domain entities
                violations.extend(self._check_cross_domain_entities(file_path, line_num, line))
                
                # Check for layer dependency violations in using statements
                violations.extend(self._check_layer_dependencies(file_path, line_num, line))
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        return violations
    
    def _check_entity_exposure(self, file_path: Path, line_num: int, line: str) -> List[Violation]:
        """Check if controllers/API return domain entities directly"""
        violations = []
        
        # Only check in API/Controller files
        if 'Controller' not in str(file_path) and 'Api' not in str(file_path):
            return violations
        
        # Pattern: public ActionResult<EntityName>
        # Pattern: public Task<EntityName>
        # Pattern: return Ok(entityVariable)
        
        entity_return_pattern = r'ActionResult<(\w+)>|Task<(\w+)>|Task<ActionResult<(\w+)>>'
        matches = re.findall(entity_return_pattern, line)
        
        for match in matches:
            entity_name = next((m for m in match if m), None)
            
            # Skip DTOs/Requests/Responses
            if any(suffix in entity_name for suffix in ['Request', 'Response', 'Dto', 'DTO', 'Model']):
                continue
            
            # Check if it's a domain entity (heuristic: PascalCase singular noun)
            if entity_name and entity_name[0].isupper():
                violations.append(Violation(
                    violation_type=ViolationType.ENTITY_EXPOSURE,
                    file_path=str(file_path),
                    line_number=line_num,
                    description=f"Controller returns domain entity '{entity_name}' directly",
                    severity="ERROR",
                    suggestion=f"Create a {entity_name}Response DTO and map the entity to it"
                ))
        
        return violations
    
    def _check_cross_domain_entities(self, file_path: Path, line_num: int, line: str) -> List[Violation]:
        """Check if RA domain code references entities from other domains"""
        violations = []
        
        # Only check RA domain files
        if '.RA.' not in str(file_path):
            return violations
        
        for entity in self.CROSS_DOMAIN_ENTITIES:
            # Look for entity usage (variable declarations, parameters, properties)
            patterns = [
                rf'\b{entity}\b\s+\w+',  # Employer employer
                rf'<{entity}>',  # List<Employer>
                rf'\({entity}\s',  # (Employer param)
                rf':\s*{entity}\b'  # : Employer
            ]
            
            for pattern in patterns:
                if re.search(pattern, line):
                    violations.append(Violation(
                        violation_type=ViolationType.CROSS_DOMAIN,
                        file_path=str(file_path),
                        line_number=line_num,
                        description=f"RA domain references cross-domain entity '{entity}'",
                        severity="ERROR",
                        suggestion=f"Create RA{entity}Summary DTO wrapper in RA.Api.Host/Models/"
                    ))
                    break
        
        return violations
    
    def _check_layer_dependencies(self, file_path: Path, line_num: int, line: str) -> List[Violation]:
        """Check if layers reference forbidden layers via using statements"""
        violations = []
        
        # Extract namespace from using statement
        using_match = re.match(r'using\s+([\w\.]+);', line.strip())
        if not using_match:
            return violations
        
        referenced_namespace = using_match.group(1)
        
        # Determine current layer from file path
        current_layer = self._get_layer_from_path(file_path)
        if not current_layer:
            return violations
        
        # Determine referenced layer from namespace
        referenced_layer = self._get_layer_from_namespace(referenced_namespace)
        if not referenced_layer:
            return violations
        
        # Check if reference is allowed
        allowed = self.ALLOWED_DEPENDENCIES.get(current_layer, [])
        
        if referenced_layer not in allowed and referenced_layer != current_layer:
            violations.append(Violation(
                violation_type=ViolationType.LAYER_DEPENDENCY,
                file_path=str(file_path),
                line_number=line_num,
                description=f"{current_layer} layer cannot reference {referenced_layer} layer",
                severity="ERROR",
                suggestion=f"Remove using statement or refactor to use abstraction (interface in {current_layer})"
            ))
        
        return violations
    
    def _get_layer_from_path(self, file_path: Path) -> str:
        """Extract layer name from file path"""
        path_str = str(file_path)
        
        if '.DomainCore' in path_str:
            return 'DomainCore'
        elif '.UseCase' in path_str:
            return 'UseCase'
        elif '.Data.' in path_str:
            return 'Data'
        elif '.Client.' in path_str:
            return 'Client'
        elif '.Api.Host' in path_str:
            return 'Api.Host'
        elif '.Jobs.Host' in path_str:
            return 'Jobs.Host'
        
        return None
    
    def _get_layer_from_namespace(self, namespace: str) -> str:
        """Extract layer name from namespace"""
        if '.DomainCore' in namespace:
            return 'DomainCore'
        elif '.UseCase' in namespace:
            return 'UseCase'
        elif '.Data.' in namespace:
            return 'Data'
        elif '.Client.' in namespace:
            return 'Client'
        elif '.Api.Host' in namespace:
            return 'Api.Host'
        elif '.Jobs.Host' in namespace:
            return 'Jobs.Host'
        
        return None
    
    def check_project(self, project_path: Path) -> List[Violation]:
        """Check all C# files in a project"""
        violations = []
        
        for cs_file in project_path.rglob('*.cs'):
            violations.extend(self.check_file(cs_file))
        
        self.violations.extend(violations)
        return violations
    
    def check_solution(self, solution_path: Path) -> List[Violation]:
        """Check all projects in a solution"""
        violations = []
        
        # Find all .csproj files
        for csproj in solution_path.parent.rglob('*.csproj'):
            project_dir = csproj.parent
            violations.extend(self.check_project(project_dir))
        
        self.violations.extend(violations)
        return violations
    
    def generate_report(self) -> str:
        """Generate a human-readable report of violations"""
        if not self.violations:
            return "✅ No boundary violations detected!"
        
        report = []
        report.append(f"🚨 Found {len(self.violations)} boundary violations\n")
        report.append("=" * 80)
        
        # Group by violation type
        by_type: Dict[ViolationType, List[Violation]] = {}
        for v in self.violations:
            by_type.setdefault(v.violation_type, []).append(v)
        
        for vtype, violations in by_type.items():
            report.append(f"\n{vtype.value}: {len(violations)} violations")
            report.append("-" * 80)
            
            for v in violations:
                report.append(f"\n{v.severity}: {v.file_path}:{v.line_number}")
                report.append(f"  Issue: {v.description}")
                report.append(f"  Fix: {v.suggestion}")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Check Clean Architecture boundary violations"
    )
    parser.add_argument('--project', help='Path to project directory')
    parser.add_argument('--solution', help='Path to .sln file')
    parser.add_argument('--file', help='Path to single .cs file')
    parser.add_argument('--output', help='Output report file (optional)')
    
    args = parser.parse_args()
    
    if not (args.project or args.solution or args.file):
        parser.error("Must specify --project, --solution, or --file")
    
    checker = DomainBoundaryChecker(os.getcwd())
    
    if args.file:
        violations = checker.check_file(Path(args.file))
    elif args.project:
        violations = checker.check_project(Path(args.project))
    elif args.solution:
        violations = checker.check_solution(Path(args.solution))
    
    report = checker.generate_report()
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {args.output}")
    
    # Exit with error code if violations found
    exit(1 if violations else 0)


if __name__ == '__main__':
    main()
