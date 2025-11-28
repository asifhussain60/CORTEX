"""
Remediation Suggestions Generator
==================================

Generates auto-remediation suggestions for incomplete features.

Author: Asif Hussain
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.operations.modules.admin.alignment_models import AlignmentReport, RemediationSuggestion
from src.validation.file_organization_validator import FileOrganizationValidator
from src.validation.template_header_validator import TemplateHeaderValidator
from src.governance.document_governance import DocumentGovernance

logger = logging.getLogger(__name__)


class RemediationSuggestionsGenerator:
    """Generates auto-remediation suggestions for incomplete features."""
    
    def __init__(self, project_root: Path):
        """
        Initialize remediation suggestions generator.
        
        Args:
            project_root: Project root path
        """
        self.project_root = project_root
    
    def generate(
        self,
        report: AlignmentReport,
        orchestrators: Dict[str, Dict[str, Any]],
        agents: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Generate auto-remediation suggestions for incomplete features.
        
        Args:
            report: AlignmentReport to populate with remediation suggestions
            orchestrators: Discovered orchestrators
            agents: Discovered agents
        """
        # Lazy load remediation generators
        from src.remediation.wiring_generator import WiringGenerator
        from src.remediation.test_skeleton_generator import TestSkeletonGenerator
        from src.remediation.documentation_generator import DocumentationGenerator
        
        wiring_gen = WiringGenerator(self.project_root)
        test_gen = TestSkeletonGenerator(self.project_root)
        doc_gen = DocumentationGenerator(self.project_root)
        
        # Collect features needing remediation
        for name, score in report.feature_scores.items():
            # Get feature metadata
            metadata = orchestrators.get(name) or agents.get(name)
            if not metadata:
                continue
            
            feature_path = metadata.get("file_path", "")
            docstring = metadata.get("docstring")
            methods = metadata.get("methods", [])
            
            # Generate wiring suggestion if not wired
            if not score.wired:
                wiring_suggestion = wiring_gen.generate_wiring_suggestion(
                    feature_name=name,
                    feature_path=feature_path,
                    docstring=docstring
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="wiring",
                    content=wiring_suggestion["yaml_template"] + "\n\n" + wiring_suggestion["prompt_section"],
                    file_path=None  # Suggestions shown in report, not saved
                ))
            
            # Generate test skeleton if not tested
            if not score.tested:
                test_skeleton = test_gen.generate_test_skeleton(
                    feature_name=name,
                    feature_path=feature_path,
                    methods=methods
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="test",
                    content=test_skeleton["test_code"],
                    file_path=test_skeleton["test_path"]
                ))
            
            # Generate documentation if not documented
            if not score.documented:
                doc_template = doc_gen.generate_documentation_template(
                    feature_name=name,
                    feature_path=feature_path,
                    docstring=docstring,
                    methods=methods
                )
                
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=name,
                    suggestion_type="documentation",
                    content=doc_template["doc_content"],
                    file_path=doc_template["doc_path"]
                ))
        
        # Add file organization remediation suggestions
        if hasattr(report, 'organization_violations'):
            org_validator = FileOrganizationValidator(self.project_root)
            org_validator.violations = report.organization_violations
            org_templates = org_validator.generate_remediation_templates()
            
            for template in org_templates:
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name="File Organization",
                    suggestion_type="organization",
                    content=f"{template['description']}\n\nCommand: {template.get('command', 'N/A')}",
                    file_path=template.get('destination')
                ))
        
        # Add template header remediation suggestions
        if hasattr(report, 'header_violations'):
            templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
            header_validator = TemplateHeaderValidator(templates_path)
            header_validator.violations = report.header_violations
            header_templates = header_validator.generate_remediation_templates()
            
            for template in header_templates:
                report.remediation_suggestions.append(RemediationSuggestion(
                    feature_name=template['template_name'],
                    suggestion_type="header_compliance",
                    content=f"{template['description']}\n\n{template.get('header_content', '')}",
                    file_path=None
                ))
        
        # Add documentation governance remediation suggestions
        if hasattr(report, 'doc_governance_violations'):
            governance = DocumentGovernance(self.project_root)
            
            for violation in report.doc_governance_violations:
                if violation.get('type') == 'duplicate_document':
                    # Create consolidation suggestion
                    file1 = self.project_root / violation['file']
                    file2 = self.project_root / violation['duplicate']
                    
                    # Determine which file to keep (prefer older/more established)
                    keep_file = file1 if file1.stat().st_mtime < file2.stat().st_mtime else file2
                    remove_file = file2 if keep_file == file1 else file1
                    
                    suggestion_content = (
                        f"Duplicate detected: {violation['similarity']} similarity via {violation['algorithm']}\n"
                        f"File 1: {violation['file']}\n"
                        f"File 2: {violation['duplicate']}\n\n"
                        f"Recommended action:\n"
                        f"1. Review both documents and merge unique content into: {keep_file.relative_to(self.project_root)}\n"
                        f"2. Archive/delete: {remove_file.relative_to(self.project_root)}\n"
                        f"3. Update any references to point to the consolidated document\n\n"
                        f"{violation['recommendation']}"
                    )
                    
                    report.remediation_suggestions.append(RemediationSuggestion(
                        feature_name="Documentation Governance",
                        suggestion_type="duplicate_consolidation",
                        content=suggestion_content,
                        file_path=str(keep_file)
                    ))
