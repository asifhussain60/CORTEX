"""
CORTEX Governance Token Budget Validator

Validates token budget compliance for governance files to prevent
GitHub Copilot premature summarization (98K baseline → 17K target).

Token Budgets:
    - CORTEX.prompt.md: 5,000 tokens
    - brain-protection-rules.yaml: 8,000 tokens
    - response-templates.yaml: 3,000 tokens
    - copilot-instructions.md: 1,000 tokens
    - TOTAL: 17,000 tokens

Commands:
    validate    - Check all governance files against token budgets
    analyze     - Identify content extraction candidates
    report      - Generate detailed token usage report
    optimize    - Apply automated token optimization (Phase 1)

Usage:
    # From command line
    python3 -m src.operations.modules.admin.governance_tokens validate
    
    # From Python code
    from src.operations.modules.admin.governance_tokens import validate_token_budgets
    result = validate_token_budgets()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
Created: 2025-12-01 (TOKEN_EFFICIENCY_ENFORCEMENT implementation)
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import centralized config for cross-platform paths
from src.config import config

logger = logging.getLogger(__name__)


def safe_print(message: str) -> None:
    """Print with Unicode fallback for Windows console encoding issues."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace emojis with ASCII equivalents
        ascii_message = (message
            .replace('🧠', '[BRAIN]')
            .replace('✅', '[OK]')
            .replace('⚠️', '[WARN]')
            .replace('❌', '[FAIL]')
            .replace('📊', '[REPORT]')
            .replace('🔍', '[ANALYZE]')
            .replace('⚡', '[OPTIMIZE]')
            .replace('━', '-')
        )
        print(ascii_message)


@dataclass
class GovernanceFile:
    """Governance file token budget configuration."""
    name: str
    path: Path
    max_tokens: int
    current_tokens: int = 0
    char_count: int = 0
    line_count: int = 0
    
    @property
    def is_compliant(self) -> bool:
        """Check if file is within token budget."""
        return self.current_tokens <= self.max_tokens
    
    @property
    def overage_tokens(self) -> int:
        """Tokens over budget (negative if under)."""
        return self.current_tokens - self.max_tokens
    
    @property
    def overage_percent(self) -> float:
        """Percentage over budget."""
        if self.max_tokens == 0:
            return 0.0
        return (self.overage_tokens / self.max_tokens) * 100
    
    @property
    def reduction_needed(self) -> float:
        """Percentage reduction needed to reach budget."""
        if self.current_tokens == 0:
            return 0.0
        return (self.overage_tokens / self.current_tokens) * 100


@dataclass
class TokenValidationReport:
    """Complete token validation report for all governance files."""
    timestamp: datetime
    files: List[GovernanceFile] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def total_current_tokens(self) -> int:
        """Total current token usage across all files."""
        return sum(f.current_tokens for f in self.files)
    
    @property
    def total_budget_tokens(self) -> int:
        """Total token budget across all files."""
        return sum(f.max_tokens for f in self.files)
    
    @property
    def total_overage_tokens(self) -> int:
        """Total tokens over budget."""
        return self.total_current_tokens - self.total_budget_tokens
    
    @property
    def is_compliant(self) -> bool:
        """True if all files are within budget."""
        return all(f.is_compliant for f in self.files)
    
    @property
    def compliant_count(self) -> int:
        """Number of files within budget."""
        return sum(1 for f in self.files if f.is_compliant)
    
    @property
    def total_count(self) -> int:
        """Total number of files checked."""
        return len(self.files)
    
    def format_console(self) -> str:
        """Format report for console output."""
        lines = [
            "🧠 CORTEX Governance Token Budget Validation",
            "━" * 80,
            ""
        ]
        
        # Individual file results
        for file in self.files:
            if file.is_compliant:
                icon = "✅"
                status = f"OK (under by {abs(file.overage_tokens):,} tokens)"
            else:
                icon = "❌"
                status = f"OVER BUDGET by {file.overage_tokens:,} tokens ({file.overage_percent:+.1f}%)"
            
            lines.extend([
                f"{icon} {file.name}",
                f"   Current: {file.current_tokens:,} tokens ({file.char_count:,} chars, {file.line_count:,} lines)",
                f"   Budget:  {file.max_tokens:,} tokens",
                f"   Status:  {status}",
                ""
            ])
        
        # Summary
        lines.extend([
            "━" * 80,
            f"Total Token Usage:   {self.total_current_tokens:,} tokens",
            f"Total Token Budget:  {self.total_budget_tokens:,} tokens",
        ])
        
        if self.is_compliant:
            lines.append(f"Status: ✅ ALL FILES COMPLIANT ({self.compliant_count}/{self.total_count} files within budget)")
        else:
            overage = self.total_overage_tokens
            overage_pct = (overage / self.total_budget_tokens) * 100
            lines.extend([
                f"Status: ❌ OVER BUDGET by {overage:,} tokens ({overage_pct:+.1f}%)",
                f"        {self.compliant_count}/{self.total_count} files within budget",
            ])
        
        lines.append(f"Execution Time: {self.execution_time:.2f}s")
        
        # Add next steps if non-compliant
        if not self.is_compliant:
            lines.extend([
                "",
                "📝 Next Steps:",
                "   1. Run 'align governance-tokens analyze' to identify extraction candidates",
                "   2. Run 'align governance-tokens optimize' to apply automated fixes",
                "   3. Manual optimization: Extract content to .github/prompts/modules/",
                "   4. See TOKEN-OPTIMIZATION-HOLISTIC-PLAN.md for 4-phase strategy",
            ])
        
        return "\n".join(lines)


class GovernanceTokenValidator:
    """Validates token budgets for CORTEX governance files."""
    
    # Token budget definitions (from TOKEN_EFFICIENCY_ENFORCEMENT)
    GOVERNANCE_FILES = {
        "CORTEX.prompt.md": {
            "path": ".github/prompts/CORTEX.prompt.md",
            "max_tokens": 5000,
            "char_to_token_ratio": 4  # ~4 chars per token
        },
        "brain-protection-rules.yaml": {
            "path": "cortex-brain/brain-protection-rules.yaml",
            "max_tokens": 8000,
            "char_to_token_ratio": 4
        },
        "response-templates.yaml": {
            "path": "cortex-brain/response-templates.yaml",
            "max_tokens": 3000,
            "char_to_token_ratio": 4
        },
        "copilot-instructions.md": {
            "path": ".github/copilot-instructions.md",
            "max_tokens": 1000,
            "char_to_token_ratio": 4
        }
    }
    
    def __init__(self):
        """Initialize validator with CORTEX root path."""
        self.root_path = Path(config.root_path)
        logger.info(f"Governance token validator initialized with root: {self.root_path}")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from character count.
        
        Uses simple heuristic: ~4 characters per token
        This is consistent with GPT tokenization for English text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        char_count = len(text)
        return char_count // 4  # Integer division for token estimate
    
    def count_lines(self, text: str) -> int:
        """Count non-empty lines in text."""
        return len([line for line in text.split('\n') if line.strip()])
    
    def validate_file(self, name: str, config: Dict[str, Any]) -> GovernanceFile:
        """
        Validate a single governance file against its token budget.
        
        Args:
            name: File name (e.g., "CORTEX.prompt.md")
            config: File configuration with path, max_tokens, char_to_token_ratio
            
        Returns:
            GovernanceFile with validation results
        """
        file_path = self.root_path / config['path']
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"Governance file not found: {file_path}")
            return GovernanceFile(
                name=name,
                path=file_path,
                max_tokens=config['max_tokens'],
                current_tokens=0,
                char_count=0,
                line_count=0
            )
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return GovernanceFile(
                name=name,
                path=file_path,
                max_tokens=config['max_tokens'],
                current_tokens=0,
                char_count=0,
                line_count=0
            )
        
        # Calculate metrics
        char_count = len(content)
        line_count = self.count_lines(content)
        token_count = self.estimate_tokens(content)
        
        return GovernanceFile(
            name=name,
            path=file_path,
            max_tokens=config['max_tokens'],
            current_tokens=token_count,
            char_count=char_count,
            line_count=line_count
        )
    
    def validate_all(self) -> TokenValidationReport:
        """
        Validate all governance files against token budgets.
        
        Returns:
            TokenValidationReport with results for all files
        """
        import time
        start_time = time.time()
        
        files = []
        for name, file_config in self.GOVERNANCE_FILES.items():
            gov_file = self.validate_file(name, file_config)
            files.append(gov_file)
        
        execution_time = time.time() - start_time
        
        return TokenValidationReport(
            timestamp=datetime.now(),
            files=files,
            execution_time=execution_time
        )


def validate_token_budgets() -> Dict[str, Any]:
    """
    Validate all governance files against token budgets.
    
    This is the primary entry point for 'align governance-tokens validate'.
    
    Returns:
        Dict with:
            - success (bool): True if all files within budget
            - message (str): Summary message
            - report_text (str): Full console output
            - report_data (dict): Structured validation data
    """
    try:
        validator = GovernanceTokenValidator()
        report = validator.validate_all()
        
        # Format console output
        console_output = report.format_console()
        safe_print(console_output)
        
        return {
            'success': report.is_compliant,
            'message': f"Token validation: {report.compliant_count}/{report.total_count} files compliant",
            'report_text': console_output,
            'report_data': {
                'timestamp': report.timestamp.isoformat(),
                'execution_time': report.execution_time,
                'total_current_tokens': report.total_current_tokens,
                'total_budget_tokens': report.total_budget_tokens,
                'total_overage_tokens': report.total_overage_tokens,
                'is_compliant': report.is_compliant,
                'compliant_count': report.compliant_count,
                'total_count': report.total_count,
                'files': [
                    {
                        'name': f.name,
                        'path': str(f.path),
                        'current_tokens': f.current_tokens,
                        'max_tokens': f.max_tokens,
                        'char_count': f.char_count,
                        'line_count': f.line_count,
                        'is_compliant': f.is_compliant,
                        'overage_tokens': f.overage_tokens,
                        'overage_percent': f.overage_percent,
                        'reduction_needed': f.reduction_needed
                    }
                    for f in report.files
                ]
            }
        }
    
    except Exception as e:
        error_message = f"Token validation failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {
            'success': False,
            'message': error_message,
            'report_text': error_message,
            'report_data': None
        }


def main():
    """CLI entry point for direct execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Governance Token Budget Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all governance files
  python3 -m src.operations.modules.admin.governance_tokens validate
  
  # Show detailed report
  python3 -m src.operations.modules.admin.governance_tokens report
  
  # Analyze extraction candidates
  python3 -m src.operations.modules.admin.governance_tokens analyze
  
Token Budgets:
  CORTEX.prompt.md:              5,000 tokens
  brain-protection-rules.yaml:   8,000 tokens
  response-templates.yaml:       3,000 tokens
  copilot-instructions.md:       1,000 tokens
  TOTAL:                        17,000 tokens
"""
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='validate',
        choices=['validate', 'report', 'analyze', 'optimize'],
        help='Command to execute (default: validate)'
    )
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'validate' or args.command == 'report':
        result = validate_token_budgets()
    elif args.command == 'analyze':
        safe_print("❌ 'analyze' command not yet implemented")
        safe_print("   Coming soon: Identifies content extraction candidates")
        result = {'success': False}
    elif args.command == 'optimize':
        safe_print("❌ 'optimize' command not yet implemented")
        safe_print("   Coming soon: Applies automated Phase 1 optimizations")
        result = {'success': False}
    else:
        result = validate_token_budgets()
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
