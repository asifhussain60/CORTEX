"""
Fix Generator - Generate fix proposals from root causes

Creates actionable fix suggestions with multiple solution paths,
confidence scoring, and impact assessment.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FixGenerator:
    """Generates fix proposals from root cause analysis."""
    
    # Fix templates for common patterns
    FIX_TEMPLATES = {
        "missing_dependency": {
            "title": "Add Missing Import",
            "approach": "import_addition",
            "template": "Add the missing import statement to the affected file",
            "confidence_base": 0.9,
        },
        "logic": {
            "title": "Fix Logic Error",
            "approach": "logic_correction",
            "template": "Correct the conditional logic or assertion",
            "confidence_base": 0.7,
        },
        "type_mismatch": {
            "title": "Fix Type Mismatch",
            "approach": "type_conversion",
            "template": "Add type conversion or change function signature",
            "confidence_base": 0.8,
        },
        "io": {
            "title": "Fix File Path",
            "approach": "path_correction",
            "template": "Correct the file path or ensure file exists",
            "confidence_base": 0.85,
        },
    }
    
    def __init__(self):
        """Initialize fix generator."""
        self.logger = logger
    
    def generate_fixes(
        self,
        root_causes: List[Dict[str, Any]],
        error_data: Dict[str, Any],
        max_proposals: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate fix proposals from root causes.
        
        Args:
            root_causes: Ranked list of root causes
            error_data: Original error data
            max_proposals: Maximum number of proposals to generate
            
        Returns:
            List of fix proposals with confidence scores
        """
        self.logger.info(f"Generating up to {max_proposals} fix proposals")
        
        proposals = []
        
        for root_cause in root_causes[:max_proposals]:
            proposal = self._generate_proposal_from_root_cause(
                root_cause, error_data
            )
            if proposal:
                proposals.append(proposal)
        
        # Rank by confidence
        proposals.sort(key=lambda p: p.get("confidence", 0), reverse=True)
        
        return proposals[:max_proposals]
    
    def _generate_proposal_from_root_cause(
        self,
        root_cause: Dict[str, Any],
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a fix proposal from a single root cause."""
        category = root_cause.get("category", "unknown")
        hypothesis = root_cause.get("hypothesis", "")
        root_confidence = root_cause.get("confidence", 0.5)
        
        # Get fix template for category
        template = self.FIX_TEMPLATES.get(category, {
            "title": "Generic Fix",
            "approach": "manual_correction",
            "template": "Manually correct the issue based on root cause analysis",
            "confidence_base": 0.5,
        })
        
        # Generate specific fix steps
        fix_steps = self._generate_fix_steps(category, root_cause, error_data)
        
        # Calculate confidence (combine root cause confidence and template confidence)
        confidence = (root_confidence + template["confidence_base"]) / 2
        
        # Assess impact
        impact = self._assess_impact(category, error_data)
        
        proposal = {
            "title": template["title"],
            "approach": template["approach"],
            "description": template["template"],
            "hypothesis_addressed": hypothesis,
            "root_cause_rank": root_cause.get("rank", 0),
            "confidence": confidence,
            "fix_steps": fix_steps,
            "impact": impact,
            "category": category,
            "affected_files": error_data.get("affected_files", []),
            "automated": self._is_automatable(category),
        }
        
        return proposal
    
    def _generate_fix_steps(
        self,
        category: str,
        root_cause: Dict[str, Any],
        error_data: Dict[str, Any]
    ) -> List[str]:
        """Generate specific fix steps based on category."""
        steps = []
        
        if category == "missing_dependency":
            evidence = root_cause.get("evidence", {})
            error_type = evidence.get("error_type", "ImportError")
            
            if "ImportError" in error_type or "ModuleNotFoundError" in error_type:
                steps = [
                    "1. Identify the missing module name from error message",
                    "2. Add import statement at top of affected file",
                    "3. Verify import path is correct",
                    "4. Run tests to verify fix",
                ]
        
        elif category == "logic":
            steps = [
                "1. Review the failing assertion or logic condition",
                "2. Examine input values that triggered the failure",
                "3. Correct the conditional logic or assertion",
                "4. Add test case to prevent regression",
            ]
        
        elif category == "type_mismatch":
            steps = [
                "1. Identify the expected vs actual types",
                "2. Add type conversion or type check",
                "3. Update function signature if needed",
                "4. Run type checker (mypy) to validate",
            ]
        
        elif category == "io":
            steps = [
                "1. Verify the file path in the code",
                "2. Check if file exists at expected location",
                "3. Update path or create missing file",
                "4. Add existence check before file access",
            ]
        
        else:
            steps = [
                "1. Analyze the root cause hypothesis",
                "2. Make necessary code changes",
                "3. Run tests to verify fix",
                "4. Update documentation if needed",
            ]
        
        return steps
    
    def _assess_impact(self, category: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of applying the fix."""
        affected_files = error_data.get("affected_files", [])
        affected_components = error_data.get("affected_components", [])
        test_failures = error_data.get("test_failures", [])
        
        # Determine scope
        if len(affected_files) > 5:
            scope = "high"
        elif len(affected_files) > 2:
            scope = "medium"
        else:
            scope = "low"
        
        # Determine risk
        if category in ["missing_dependency", "io"]:
            risk = "low"  # Usually safe fixes
        elif category in ["type_mismatch"]:
            risk = "medium"  # May affect other code
        else:
            risk = "medium"  # Logic changes can be risky
        
        return {
            "scope": scope,
            "risk": risk,
            "affected_file_count": len(affected_files),
            "affected_component_count": len(affected_components),
            "test_failure_count": len(test_failures),
        }
    
    def _is_automatable(self, category: str) -> bool:
        """Check if fix can be applied automatically."""
        # Some fixes are more automatable than others
        automatable_categories = ["missing_dependency", "io"]
        return category in automatable_categories
