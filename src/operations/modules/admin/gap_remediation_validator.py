"""
Gap Remediation Validator
==========================

Validates Phase 1-4 gap remediation components for system alignment.

Author: Asif Hussain
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.operations.modules.admin.alignment_models import AlignmentReport

logger = logging.getLogger(__name__)


class GapRemediationValidator:
    """Validates Phase 1-4 gap remediation components."""
    
    def __init__(self, project_root: Path):
        """
        Initialize gap remediation validator.
        
        Args:
            project_root: Project root path
        """
        self.project_root = project_root
    
    def validate(self, report: AlignmentReport) -> None:
        """
        Validate Phase 1-4 gap remediation components.
        
        Validates:
        - GitHub Actions workflows (feedback-aggregation.yml)
        - Template format compliance (H1 headers, Challenge field)
        - Brain protection rule severity (NO_ROOT_FILES blocked enforcement)
        - Configuration schemas (plan-schema.yaml, lint-rules.yaml)
        
        Args:
            report: AlignmentReport to populate with gap remediation validation results
        """
        # 1. Validate GitHub Actions workflows
        workflows_path = self.project_root / ".github" / "workflows"
        feedback_workflow = workflows_path / "feedback-aggregation.yml"
        
        if not feedback_workflow.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_workflow",
                "message": "Missing feedback-aggregation.yml workflow (Gap #7 - Feedback Automation)"
            })
        else:
            # Validate workflow structure
            try:
                import yaml
                with open(feedback_workflow, "r", encoding="utf-8") as f:
                    workflow_content = yaml.safe_load(f)
                    
                if "schedule" not in workflow_content.get("on", {}):
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "workflow_config",
                        "message": "feedback-aggregation.yml missing schedule trigger"
                    })
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "workflow_parse",
                    "message": f"Failed to parse feedback-aggregation.yml: {e}"
                })
        
        # 2. Validate template format compliance
        templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
        
        if not templates_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_templates",
                "message": "Missing cortex-brain/response-templates.yaml"
            })
        else:
            try:
                import yaml
                with open(templates_path, "r", encoding="utf-8") as f:
                    templates = yaml.safe_load(f)
                
                # Validate new template architecture
                template_issues = []
                base_templates = templates.get("base_templates", {})
                template_defs = templates.get("templates", {})
                
                # Check for base template architecture (v3.2+)
                if not base_templates:
                    template_issues.append("Missing base_templates section (v3.2 architecture)")
                else:
                    # Validate base templates have required structure
                    for base_name, base_data in base_templates.items():
                        if "base_structure" not in base_data:
                            template_issues.append(f"Base template '{base_name}' missing base_structure")
                
                # Check for H1 header format in templates (# 🧠 CORTEX)
                for template_name, template_data in template_defs.items():
                    # New architecture: templates inherit from base_templates via YAML anchors
                    if "base_structure" in template_data:
                        # Using new composition model - validate placeholders
                        base_structure = template_data.get("base_structure", "")
                        if not base_structure.startswith("# "):
                            template_issues.append(f"{template_name}: Base structure missing H1 header")
                    else:
                        # Traditional template with direct content
                        content = template_data.get("content", "")
                        if content and not content.startswith("# ") and not content.startswith("##"):
                            template_issues.append(f"{template_name}: Missing H1 header")
                    
                    # Validate Challenge field format (should not have old [✓ Accept OR ⚡ Challenge])
                    content_str = str(template_data.get("content", "")) + str(template_data.get("base_structure", ""))
                    if "[✓ Accept OR ⚡ Challenge]" in content_str or "[Accept|Challenge]" in content_str:
                        template_issues.append(f"{template_name}: Old Challenge format detected")
                
                # Check for schema version
                schema_version = templates.get("schema_version", "unknown")
                if schema_version not in ["3.2", "3.3"]:
                    template_issues.append(f"Outdated schema_version: {schema_version} (expected 3.2+)")
                
                if template_issues:
                    report.warnings += len(template_issues)
                    for issue in template_issues[:3]:  # Show first 3
                        report.suggestions.append({
                            "type": "template_format",
                            "message": f"Template format issue: {issue}"
                        })
                    
                    if len(template_issues) > 3:
                        report.suggestions.append({
                            "type": "template_format",
                            "message": f"...and {len(template_issues) - 3} more template format issues"
                        })
            
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "template_parse",
                    "message": f"Failed to parse response-templates.yaml: {e}"
                })
        
        # 3. Validate brain protection rule severity
        brain_rules_path = self.project_root / "cortex-brain" / "brain-protection-rules.yaml"
        
        if not brain_rules_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_brain_rules",
                "message": "Missing cortex-brain/brain-protection-rules.yaml"
            })
        else:
            try:
                import yaml
                with open(brain_rules_path, "r", encoding="utf-8") as f:
                    brain_rules = yaml.safe_load(f)
                
                # Check NO_ROOT_FILES protection level
                layers = brain_rules.get("layers", {})
                layer_8 = layers.get("layer_8_document_organization", {})
                rules = layer_8.get("rules", [])
                
                no_root_files_rule = next(
                    (r for r in rules if r.get("id") == "NO_ROOT_FILES"),
                    None
                )
                
                if no_root_files_rule:
                    severity = no_root_files_rule.get("severity")
                    if severity != "blocked":
                        report.warnings += 1
                        report.suggestions.append({
                            "type": "brain_protection",
                            "message": f"NO_ROOT_FILES protection is '{severity}', should be 'blocked' (Gap #5 strengthening)"
                        })
                else:
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "brain_protection",
                        "message": "NO_ROOT_FILES protection rule not found in Layer 8"
                    })
                
                # Verify DOCUMENT_ORGANIZATION_ENFORCEMENT in Tier 0 instincts
                tier0_instincts = brain_rules.get("tier0_instincts", [])
                if "DOCUMENT_ORGANIZATION_ENFORCEMENT" not in tier0_instincts:
                    report.warnings += 1
                    report.suggestions.append({
                        "type": "brain_protection",
                        "message": "DOCUMENT_ORGANIZATION_ENFORCEMENT missing from Tier 0 instincts"
                    })
            
            except Exception as e:
                report.warnings += 1
                report.suggestions.append({
                    "type": "brain_rules_parse",
                    "message": f"Failed to parse brain-protection-rules.yaml: {e}"
                })
        
        # 4. Validate configuration schemas
        config_path = self.project_root / "cortex-brain" / "config"
        plan_schema = config_path / "plan-schema.yaml"
        lint_rules = config_path / "lint-rules.yaml"
        
        if not plan_schema.exists():
            report.warnings += 1
            report.suggestions.append({
                "type": "missing_schema",
                "message": "Missing cortex-brain/config/plan-schema.yaml (Gap #4 - Planning System)"
            })
        
        if not lint_rules.exists():
            report.warnings += 1
            report.suggestions.append({
                "type": "missing_config",
                "message": "Missing cortex-brain/config/lint-rules.yaml (Gap #3 - Lint Validation)"
            })
        
        # 5. Validate orchestrator presence (auto-discovered, but check key ones)
        expected_orchestrators = [
            "GitCheckpointOrchestrator",
            "MetricsTracker",
            "LintValidationOrchestrator",
            "SessionCompletionOrchestrator",
            "PlanningOrchestrator",
            "UpgradeOrchestrator"
        ]
        
        discovered_names = {score.feature_name for score in report.feature_scores.values()}
        missing_orchestrators = [name for name in expected_orchestrators if name not in discovered_names]
        
        if missing_orchestrators:
            report.critical_issues += len(missing_orchestrators)
            for name in missing_orchestrators:
                report.suggestions.append({
                    "type": "missing_orchestrator",
                    "message": f"Gap remediation orchestrator not discovered: {name}"
                })
        
        # 6. Validate feedback aggregator
        feedback_aggregator_path = self.project_root / "src" / "feedback" / "feedback_aggregator.py"
        
        if not feedback_aggregator_path.exists():
            report.critical_issues += 1
            report.suggestions.append({
                "type": "missing_module",
                "message": "Missing src/feedback/feedback_aggregator.py (Gap #7 - Feedback Automation)"
            })
