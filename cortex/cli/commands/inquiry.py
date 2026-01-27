"""
CORTEX Inquiry CLI Command - /ask command implementation.

Implements CLI command for asking questions about codebases:
  /ask <question> [--category CATEGORY] [--files FILE1,FILE2]

AC-ID: INQUIRY-015
Author: Asif Hussain
Date: 2026-01-27

Type Hints: Complete | Docstrings: Google-style | Error Handling: Comprehensive
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator
from cortex.models.inquiry_models import InquiryCategory


@dataclass
class CommandResult:
    """Result of CLI command execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class AskCommand:
    """CLI command for asking questions about codebases."""
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """Initialize ask command.
        
        Args:
            repo_path: Optional path to repository (defaults to cwd)
        """
        self.repo_path = repo_path or Path.cwd()
        self.orchestrator = InquiryOrchestrator(repo_path=self.repo_path)
    
    def execute(
        self,
        question: str,
        category: Optional[str] = None,
        files: Optional[List[str]] = None,
    ) -> CommandResult:
        """Execute the ask command.
        
        Args:
            question: The question to ask
            category: Optional category hint (architecture, feature, etc.)
            files: Optional list of file paths to focus on
            
        Returns:
            CommandResult with answer and metadata
        """
        # Validate question
        if not question or not question.strip():
            return self._format_error("Question is required")
        
        try:
            # Convert category string to enum if provided
            category_hint = None
            if category:
                try:
                    category_hint = InquiryCategory[category.upper()]
                except KeyError:
                    return self._format_error(
                        f"Invalid category: {category}. "
                        f"Valid categories: {', '.join(c.value for c in InquiryCategory)}"
                    )
            
            # Execute inquiry
            response = self.orchestrator.ask(
                question=question,
                category_hint=category_hint,
                file_paths=files,
            )
            
            # Format success response
            return self._format_success(
                message=self._format_answer_message(response),
                data=response,
            )
            
        except Exception as e:
            return self._format_error(f"Error executing inquiry: {e}")
    
    def _format_answer_message(self, response: Dict[str, Any]) -> str:
        """Format answer into user-friendly message.
        
        Args:
            response: Response dict from orchestrator
            
        Returns:
            Formatted message string
        """
        answer = response.get("answer", "No answer available")
        confidence = response.get("confidence", 0.0)
        repo_type = response.get("repo_type", "unknown")
        category = response.get("category", "general")
        
        message = f"✅ Answer (confidence: {confidence:.0%}, type: {repo_type}, category: {category})\n"
        message += f"\n{answer}\n"
        
        # Add evidence summary if available
        evidence = response.get("evidence", {})
        if evidence:
            files = evidence.get("files", [])
            if files:
                message += f"\n📁 Evidence from {len(files)} files"
        
        return message
    
    def _format_success(
        self,
        message: str,
        data: Optional[Dict] = None
    ) -> CommandResult:
        """Format successful command result.
        
        Args:
            message: Success message
            data: Optional result data
            
        Returns:
            CommandResult instance
        """
        return CommandResult(
            success=True,
            message=message,
            data=data,
            errors=None,
        )
    
    def _format_error(
        self,
        message: str,
        errors: Optional[List[str]] = None
    ) -> CommandResult:
        """Format error command result.
        
        Args:
            message: Error message
            errors: Optional list of error details
            
        Returns:
            CommandResult instance
        """
        return CommandResult(
            success=False,
            message=message,
            data=None,
            errors=errors or [message],
        )
    
    def get_help(self) -> str:
        """Get help text for the ask command.
        
        Returns:
            Help text string
        """
        return """
CORTEX Ask Command
==================

Ask questions about your codebase using CORTEX intelligence.

Usage:
    cortex ask "<question>" [options]

Options:
    --category CATEGORY    Category hint (architecture, feature, best_practice, 
                          troubleshooting, evolution, code_explanation)
    --files FILE1,FILE2    Comma-separated list of files to focus on

Examples:
    cortex ask "How does authentication work?"
    cortex ask "What design patterns are used?" --category architecture
    cortex ask "What does main.py do?" --files src/main.py
    cortex ask "How has error handling evolved?" --category evolution

Categories:
    architecture       - System design and architecture questions
    feature           - Feature discovery and functionality
    best_practice     - Best practices and patterns
    troubleshooting   - Debugging and troubleshooting help
    evolution         - Code history and evolution
    code_explanation  - General code explanations
"""
    
    def get_examples(self) -> List[str]:
        """Get example commands.
        
        Returns:
            List of example command strings
        """
        return [
            'cortex ask "How does authentication work?"',
            'cortex ask "What design patterns are used?" --category architecture',
            'cortex ask "What does main.py do?" --files src/main.py',
            'cortex ask "How has error handling evolved?" --category evolution',
            'cortex ask "What are the main components?" --category feature',
        ]


def main() -> int:
    """CLI entry point for ask command.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ask questions about your codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "question",
        help="The question to ask",
    )
    
    parser.add_argument(
        "--category",
        choices=["architecture", "feature", "best_practice", "troubleshooting", "evolution", "code_explanation"],
        help="Category hint for better routing",
    )
    
    parser.add_argument(
        "--files",
        help="Comma-separated list of files to focus on",
    )
    
    parser.add_argument(
        "--repo-path",
        type=Path,
        help="Path to repository (defaults to current directory)",
    )
    
    args = parser.parse_args()
    
    # Parse files list
    files = None
    if args.files:
        files = [f.strip() for f in args.files.split(",")]
    
    # Execute command
    command = AskCommand(repo_path=args.repo_path)
    result = command.execute(
        question=args.question,
        category=args.category,
        files=files,
    )
    
    # Print result
    print(result.message)
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
