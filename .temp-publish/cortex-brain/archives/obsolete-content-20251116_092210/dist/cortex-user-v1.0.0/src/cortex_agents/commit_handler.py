"""
CommitHandler Agent

Manages git operations and generates conventional commit messages.
Handles commit message generation, staged file validation, and
git repository operations.

The CommitHandler automates git workflow and ensures consistent
commit message formatting following conventional commit standards.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import subprocess
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class CommitHandler(BaseAgent):
    """
    Manages git operations and commit message generation.
    
    The CommitHandler automates git commit workflow by generating
    conventional commit messages, validating staged changes, and
    executing git operations safely.
    
    Features:
    - Conventional commit message generation
    - Staged file validation
    - Git status checking
    - Commit execution
    - Pre-commit validation
    - Commit message templates (feat, fix, docs, refactor, etc.)
    
    Example:
        handler = CommitHandler(name="Committer", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="commit",
            context={
                "staged_files": ["src/feature.py", "tests/test_feature.py"],
                "type": "feat",
                "description": "Add user authentication"
            },
            user_message="Commit the authentication feature"
        )
        
        response = handler.execute(request)
        # Returns: {
        #   "committed": True,
        #   "message": "feat: Add user authentication",
        #   "files": 2,
        #   "commit_hash": "abc123"
        # }
    """
    
    # Conventional commit types
    COMMIT_TYPES = {
        "feat": "A new feature",
        "fix": "A bug fix",
        "docs": "Documentation only changes",
        "style": "Code style changes (formatting, semicolons, etc)",
        "refactor": "Code refactoring (neither fixes bug nor adds feature)",
        "perf": "Performance improvements",
        "test": "Adding or updating tests",
        "build": "Build system or external dependency changes",
        "ci": "CI/CD configuration changes",
        "chore": "Other changes (maintenance, etc)"
    }
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        """
        Initialize CommitHandler.
        
        Args:
            name: Agent name
            tier1_api: Tier 1 conversation manager API
            tier2_kg: Tier 2 knowledge graph API
            tier3_context: Tier 3 context intelligence API
        """
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.supported_intents = [
            "commit",
            "git_commit",
            "create_commit"
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request to evaluate
            
        Returns:
            True if intent is commit/git operation, False otherwise
        """
        return request.intent in self.supported_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Generate commit message and execute git commit.
        
        Args:
            request: Agent request with commit details in context
            
        Returns:
            AgentResponse with commit result
        """
        start_time = datetime.now()
        
        try:
            # Check for uncommitted changes
            has_changes, staged_files = self._check_git_status()
            if not has_changes:
                return self._error_response(
                    "No staged changes to commit",
                    start_time
                )
            
            # Generate commit message
            commit_message = self._generate_commit_message(request, staged_files)
            
            # Validate commit message
            if not commit_message:
                return self._error_response(
                    "Failed to generate commit message",
                    start_time
                )
            
            # Execute commit (if not in dry-run mode)
            dry_run = request.context.get("dry_run", False)
            if dry_run:
                commit_hash = "DRY_RUN"
                committed = False
            else:
                commit_hash = self._execute_commit(commit_message)
                committed = commit_hash is not None
            
            # Build response
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=committed or dry_run,
                result={
                    "committed": committed,
                    "message": commit_message,
                    "files": len(staged_files),
                    "staged_files": staged_files,
                    "commit_hash": commit_hash,
                    "dry_run": dry_run
                },
                message=f"{'Would commit' if dry_run else 'Committed'} {len(staged_files)} files: {commit_message}",
                agent_name=self.name,
                duration_ms=duration_ms,
                next_actions=[
                    "Push to remote" if committed else "Review commit message",
                    "Update Tier 1 conversation log" if committed else "Execute commit"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Commit failed: {e}", exc_info=True)
            return self._error_response(str(e), start_time)
    
    def _check_git_status(self) -> Tuple[bool, List[str]]:
        """
        Check git status for staged changes.
        
        Returns:
            Tuple of (has_changes, list_of_staged_files)
        """
        try:
            # Run git diff --cached --name-only
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]
            
            return len(staged_files) > 0, staged_files
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git status check failed: {e}")
            return False, []
    
    def _generate_commit_message(
        self, 
        request: AgentRequest, 
        staged_files: List[str]
    ) -> str:
        """
        Generate conventional commit message.
        
        Args:
            request: Agent request with commit details
            staged_files: List of staged files
            
        Returns:
            Formatted commit message
        """
        # Extract commit type and description from context
        commit_type = request.context.get("type", self._infer_commit_type(staged_files))
        description = request.context.get("description", "")
        
        # If no description, try to extract from user message
        if not description:
            description = self._extract_description(request.user_message)
        
        # If still no description, generate from files
        if not description:
            description = self._generate_description_from_files(staged_files)
        
        # Build commit message
        commit_message = f"{commit_type}: {description}"
        
        # Add scope if provided
        scope = request.context.get("scope")
        if scope:
            commit_message = f"{commit_type}({scope}): {description}"
        
        # Add body if provided
        body = request.context.get("body")
        if body:
            commit_message += f"\n\n{body}"
        
        return commit_message
    
    def _infer_commit_type(self, staged_files: List[str]) -> str:
        """
        Infer commit type from staged files.
        
        Args:
            staged_files: List of staged files
            
        Returns:
            Inferred commit type
        """
        # Check file patterns
        has_tests = any("test_" in f or "_test" in f or "/tests/" in f for f in staged_files)
        has_docs = any(f.endswith(".md") or "docs/" in f for f in staged_files)
        has_code = any(f.endswith(".py") and "test" not in f for f in staged_files)
        has_ci = any(".github/" in f or "ci/" in f or ".yml" in f for f in staged_files)
        
        # Infer type
        if has_tests and not has_code:
            return "test"
        elif has_docs and not has_code:
            return "docs"
        elif has_ci:
            return "ci"
        elif has_code:
            # Default to feat for code changes
            return "feat"
        else:
            return "chore"
    
    def _extract_description(self, user_message: str) -> str:
        """
        Extract description from user message.
        
        Args:
            user_message: User's message
            
        Returns:
            Extracted description or empty string
        """
        # Simple extraction - remove common command words
        message_lower = user_message.lower()
        
        # Remove command words
        for cmd in ["commit", "git commit", "create commit", "please", "can you"]:
            message_lower = message_lower.replace(cmd, "")
        
        # Clean up and capitalize
        description = message_lower.strip()
        if description:
            description = description[0].upper() + description[1:]
        
        return description
    
    def _generate_description_from_files(self, staged_files: List[str]) -> str:
        """
        Generate description from staged files.
        
        Args:
            staged_files: List of staged files
            
        Returns:
            Generated description
        """
        if len(staged_files) == 1:
            # Single file
            file_name = Path(staged_files[0]).name
            return f"Update {file_name}"
        else:
            # Multiple files
            file_types = set(Path(f).suffix for f in staged_files)
            if len(file_types) == 1 and ".py" in file_types:
                return f"Update {len(staged_files)} Python files"
            elif len(file_types) == 1 and ".md" in file_types:
                return f"Update {len(staged_files)} documentation files"
            else:
                return f"Update {len(staged_files)} files"
    
    def _execute_commit(self, commit_message: str) -> Optional[str]:
        """
        Execute git commit.
        
        Args:
            commit_message: Commit message
            
        Returns:
            Commit hash or None if failed
        """
        try:
            # Run git commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract commit hash from output
            # Typical output: [branch hash] message
            output = result.stdout.strip()
            if "[" in output and "]" in output:
                # Extract hash between brackets
                parts = output.split("]")[0].split()
                if len(parts) >= 2:
                    return parts[1]
            
            # Fallback: get HEAD hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return hash_result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git commit failed: {e}")
            return None
    
    def _error_response(self, error_msg: str, start_time: datetime) -> AgentResponse:
        """
        Create error response.
        
        Args:
            error_msg: Error message
            start_time: Request start time
            
        Returns:
            AgentResponse with error details
        """
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return AgentResponse(
            success=False,
            result={
                "committed": False,
                "message": "",
                "files": 0
            },
            message=f"Commit failed: {error_msg}",
            agent_name=self.name,
            duration_ms=duration_ms,
            metadata={"error": error_msg}
        )
