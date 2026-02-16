"""
Toolkit Validate MCP Tool.

Exposes GovernanceValidator for production readiness and compliance checking.

Author: CORTEX Framework
Phase: 90 (Toolkit Centralization)
"""

from typing import Any, Dict
from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.toolkit.validation import GovernanceValidator


class ToolkitValidateTool(ConsolidatedTool):
    """
    MCP tool for governance validation and production readiness.
    
    Exposes GovernanceValidator functionality via MCP protocol.
    """
    
    @property
    def name(self) -> str:
        return "toolkit_validate"
    
    @property
    def description(self) -> str:
        return "Validate governance compliance and production readiness"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.GOVERNANCE
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="validation_type",
                type="string",
                required=False,
                description="Type of validation to perform",
                default="all",
                enum=["governance", "production", "security", "compliance", "all"]
            ),
            ToolParameter(
                name="dry_run",
                type="boolean",
                required=False,
                description="Preview validation without side effects",
                default=False
            )
        ]
    
    @property
    def supported_operations(self) -> list:
        return ["governance", "production", "security", "compliance", "all"]
    
    def execute(self, validation_type: str = "all", dry_run: bool = False, **kwargs) -> ToolResult:
        """
        Execute governance validation.
        
        Args:
            validation_type: Type of validation (governance, production, security, compliance, all)
            dry_run: Preview validation without side effects
        
        Returns:
            ToolResult with validation results
        """
        try:
            validator = GovernanceValidator()
            
            if validation_type == "all" or validation_type == "production":
                report = validator.validate_production_readiness(dry_run=dry_run)
                formatted_report = validator.generate_readiness_report(report)
                
                return ToolResult(
                    success=report.overall_status == "PRODUCTION READY",
                    data={
                        "report": report.__dict__,
                        "formatted": formatted_report
                    },
                    metadata={"validation_type": validation_type, "dry_run": dry_run}
                )
            
            elif validation_type == "governance":
                result = validator.check_governance_alignment()
                
                return ToolResult(
                    success=result,
                    data={"governance_aligned": result},
                    metadata={"validation_type": validation_type}
                )
            
            elif validation_type == "security":
                result = validator.assess_security_posture()
                
                return ToolResult(
                    success=result.get("score", 0) >= 70.0,
                    data=result,
                    metadata={"validation_type": validation_type}
                )
            
            elif validation_type == "compliance":
                # Compliance is a combination of governance + security
                governance_result = validator.check_governance_alignment()
                security_result = validator.assess_security_posture()
                
                return ToolResult(
                    success=governance_result and security_result.get("score", 0) >= 70.0,
                    data={
                        "governance": governance_result,
                        "security": security_result
                    },
                    metadata={"validation_type": validation_type}
                )
            
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown validation_type: {validation_type}",
                    metadata={"available_types": self.supported_operations}
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Validation failed: {str(e)}",
                metadata={"validation_type": validation_type, "dry_run": dry_run}
            )
