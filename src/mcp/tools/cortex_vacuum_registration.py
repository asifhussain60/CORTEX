"""
CORTEX Vacuum Tool Registration

MCP integration and registration for vacuum tools.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Optional, Dict
from src.mcp.tools.cortex_vacuum_analyzer import CortexVacuumAnalyzer
from src.mcp.tools.cortex_vacuum_executor import CortexVacuumExecutor


def register_vacuum_tools(registry):
    """Register vacuum tools with MCP registry."""
    
    @registry.tool()
    def vacuum_analyze(repo_root: str, output_dir: Optional[str] = None) -> Dict:
        """
        Analyze repository structure and generate migration plan.
        
        Args:
            repo_root: Root directory of CORTEX repository
            output_dir: Optional directory to save analysis results
            
        Returns:
            Analysis report dictionary
        """
        analyzer = CortexVacuumAnalyzer(repo_root)
        return analyzer.analyze()
    
    @registry.tool()
    def vacuum_execute(
        repo_root: str,
        migration_plan: Dict,
        dry_run: bool = True,
        auto_approve: bool = False
    ) -> Dict:
        """
        Execute repository reorganization with safety guarantees.
        
        Args:
            repo_root: Root directory of CORTEX repository
            migration_plan: Migration plan from analysis
            dry_run: If True, simulate without making changes (default: True)
            auto_approve: If True, skip confirmation (default: False)
            
        Returns:
            Execution report dictionary
        """
        executor = CortexVacuumExecutor(repo_root, migration_plan, dry_run=dry_run)
        return executor.execute(auto_approve=auto_approve)
    
    @registry.tool()
    def vacuum_verify(repo_root: str) -> Dict:
        """
        Verify repository structure compliance.
        
        Args:
            repo_root: Root directory of CORTEX repository
            
        Returns:
            Verification report
        """
        analyzer = CortexVacuumAnalyzer(repo_root)
        analyzer._scan_repository()
        analyzer._identify_file_issues()
        
        return {
            'compliant': len(analyzer.issues) == 0,
            'total_issues': len(analyzer.issues),
            'issues': [
                {
                    'file': issue.file_path,
                    'type': issue.issue_type,
                    'description': issue.description,
                    'suggestion': issue.suggested_action
                }
                for issue in analyzer.issues
            ]
        }


__all__ = ['register_vacuum_tools']
