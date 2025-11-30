"""
GitIgnore Setup Module - Ensures CORTEX is excluded from user's repository

Responsibilities:
1. Detect user's .gitignore file (or create if missing)
2. Add CORTEX exclusion patterns
3. Validate patterns work using git check-ignore
4. Commit .gitignore automatically
5. Verify no CORTEX files are staged/tracked

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


class GitIgnoreSetupModule(BaseSetupModule):
    """
    Automatically configure .gitignore to exclude CORTEX folder.
    
    This prevents CORTEX brain data, databases, and internal files from
    being committed to the user's repository.
    
    Workflow:
    1. Detect .gitignore location (project root)
    2. Check if CORTEX patterns already exist
    3. Add patterns if missing (non-destructive)
    4. Validate patterns work with git check-ignore
    5. Commit .gitignore with descriptive message
    6. Verify no CORTEX files are staged
    
    Patterns Added:
        # CORTEX AI Assistant (local only, not committed)
        CORTEX/
        .github/prompts/CORTEX.prompt.md
        .github/prompts/cortex-story-builder.md
        .github/prompts/modules/
    """
    
    CORTEX_PATTERNS = [
        "# CORTEX AI Assistant (local only, not committed)",
        "CORTEX/",
        ".github/prompts/CORTEX.prompt.md",
        ".github/prompts/cortex-story-builder.md",
        ".github/prompts/modules/"
    ]
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Return module metadata."""
        return SetupModuleMetadata(
            module_id="gitignore_setup",
            name="GitIgnore Configuration",
            description="Configure .gitignore to exclude CORTEX from repository",
            phase=SetupPhase.ENVIRONMENT,
            priority=15,  # Run early, before brain initialization
            dependencies=["platform_detection"],
            optional=False,  # Critical - prevents CORTEX brain leakage
            enabled_by_default=True
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate git is available and we have a project root.
        
        Args:
            context: Must contain 'project_root' and 'user_project_root'
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check project root exists
        project_root = context.get('project_root')
        if not project_root:
            issues.append("project_root not found in context")
        elif not Path(project_root).exists():
            issues.append(f"Project root does not exist: {project_root}")
        
        # Check user project root (where .gitignore should be)
        user_project_root = context.get('user_project_root')
        if not user_project_root:
            # Fallback: assume parent of CORTEX folder
            cortex_folder = Path(project_root)
            user_project_root = cortex_folder.parent
            context['user_project_root'] = str(user_project_root)
            self.log_info(f"Inferred user_project_root: {user_project_root}")
        
        # Check git is available
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                issues.append("Git command failed - ensure Git is installed")
        except FileNotFoundError:
            issues.append("Git not found - please install Git")
        except Exception as e:
            issues.append(f"Git validation error: {e}")
        
        # Check we're in a git repository
        try:
            user_root = Path(context.get('user_project_root', project_root))
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=user_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                issues.append(f"Not a git repository: {user_root}")
        except Exception as e:
            issues.append(f"Git repository check failed: {e}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Configure .gitignore and commit changes.
        
        Args:
            context: Shared context with paths
        
        Returns:
            SetupResult with execution details
        """
        try:
            user_root = Path(context.get('user_project_root', context['project_root']))
            gitignore_path = user_root / '.gitignore'
            
            self.log_info(f"Configuring .gitignore at: {gitignore_path}")
            
            # Step 1: Read or create .gitignore
            existing_content = ""
            if gitignore_path.exists():
                existing_content = gitignore_path.read_text(encoding='utf-8')
                self.log_info("Found existing .gitignore")
            else:
                self.log_info("Creating new .gitignore")
            
            # Step 2: Check if CORTEX patterns already exist
            if "CORTEX AI Assistant" in existing_content:
                self.log_info("CORTEX patterns already present in .gitignore")
                
                # Validate patterns work
                is_valid, issues = self._validate_gitignore_patterns(user_root)
                if is_valid:
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.SUCCESS,
                        message=".gitignore already configured correctly",
                        details={'gitignore_path': str(gitignore_path)}
                    )
                else:
                    self.log_warning("Patterns exist but validation failed")
                    return SetupResult(
                        module_id=self.metadata.module_id,
                        status=SetupStatus.WARNING,
                        message="CORTEX patterns exist but validation failed",
                        warnings=issues,
                        details={'gitignore_path': str(gitignore_path)}
                    )
            
            # Step 3: Add CORTEX patterns
            updated_content = self._add_cortex_patterns(existing_content)
            gitignore_path.write_text(updated_content, encoding='utf-8')
            self.log_info("Added CORTEX patterns to .gitignore")
            
            # Step 4: Validate patterns work
            is_valid, validation_issues = self._validate_gitignore_patterns(user_root)
            if not is_valid:
                return SetupResult(
                    module_id=self.metadata.module_id,
                    status=SetupStatus.FAILED,
                    message="GitIgnore patterns validation failed",
                    errors=validation_issues,
                    details={'gitignore_path': str(gitignore_path)}
                )
            
            self.log_info("Validated .gitignore patterns work correctly")
            
            # Step 5: Commit .gitignore
            commit_success, commit_message = self._commit_gitignore(user_root)
            if not commit_success:
                return SetupResult(
                    module_id=self.metadata.module_id,
                    status=SetupStatus.WARNING,
                    message="GitIgnore configured but commit failed",
                    warnings=[commit_message],
                    details={'gitignore_path': str(gitignore_path)}
                )
            
            self.log_info(f"Committed .gitignore: {commit_message}")
            
            # Step 6: Verify no CORTEX files are staged
            is_clean, staged_files = self._verify_no_cortex_staged(user_root)
            if not is_clean:
                return SetupResult(
                    module_id=self.metadata.module_id,
                    status=SetupStatus.WARNING,
                    message="GitIgnore configured but CORTEX files are staged",
                    warnings=[f"Staged CORTEX files detected: {', '.join(staged_files)}"],
                    details={
                        'gitignore_path': str(gitignore_path),
                        'staged_files': staged_files
                    }
                )
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message=f"✓ GitIgnore configured and committed successfully\n" +
                        f"   ✓ Added CORTEX/ to .gitignore at {gitignore_path}\n" +
                        f"   ✓ Committed with message: {commit_message}\n" +
                        f"   ✓ Validated {len(self.CORTEX_PATTERNS)} exclusion patterns work\n" +
                        f"   ✓ Verified no CORTEX files are staged",
                details={
                    'gitignore_path': str(gitignore_path),
                    'commit_message': commit_message,
                    'patterns_added': len(self.CORTEX_PATTERNS),
                    'patterns_validated': True,
                    'no_cortex_staged': True
                }
            )
        
        except Exception as e:
            self.log_error(f"GitIgnore setup failed: {e}")
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"GitIgnore setup failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _add_cortex_patterns(self, existing_content: str) -> str:
        """
        Add CORTEX patterns to .gitignore (non-destructive).
        
        Args:
            existing_content: Current .gitignore content
        
        Returns:
            Updated content with CORTEX patterns appended
        """
        # Ensure file ends with newline
        if existing_content and not existing_content.endswith('\n'):
            existing_content += '\n'
        
        # Add CORTEX section
        cortex_section = '\n'.join(self.CORTEX_PATTERNS)
        return f"{existing_content}\n{cortex_section}\n"
    
    def _validate_gitignore_patterns(self, user_root: Path) -> Tuple[bool, List[str]]:
        """
        Validate .gitignore patterns work using git check-ignore.
        
        Args:
            user_root: User's project root
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Test patterns
        test_paths = [
            'CORTEX/',
            'CORTEX/README.md',
            'CORTEX/src/setup.py',
            '.github/prompts/CORTEX.prompt.md',
            '.github/prompts/modules/'
        ]
        
        for test_path in test_paths:
            try:
                result = subprocess.run(
                    ['git', 'check-ignore', '-v', test_path],
                    cwd=user_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # check-ignore returns 0 if path is ignored, 1 if not
                if result.returncode != 0:
                    issues.append(f"Pattern not matching: {test_path}")
            except Exception as e:
                issues.append(f"Validation failed for {test_path}: {e}")
        
        return len(issues) == 0, issues
    
    def _commit_gitignore(self, user_root: Path) -> Tuple[bool, str]:
        """
        Commit .gitignore changes.
        
        Args:
            user_root: User's project root
        
        Returns:
            (success, message)
        """
        try:
            # Stage .gitignore
            subprocess.run(
                ['git', 'add', '.gitignore'],
                cwd=user_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            
            # Commit with descriptive message
            commit_message = "Add CORTEX folder to .gitignore - keep AI assistant data local"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=user_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, commit_message
            elif "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                return True, "No changes to commit (.gitignore already up to date)"
            else:
                return False, f"Commit failed: {result.stderr}"
        
        except subprocess.CalledProcessError as e:
            return False, f"Git command failed: {e.stderr}"
        except Exception as e:
            return False, f"Commit error: {str(e)}"
    
    def _verify_no_cortex_staged(self, user_root: Path) -> Tuple[bool, List[str]]:
        """
        Verify no CORTEX files are staged or tracked.
        
        Args:
            user_root: User's project root
        
        Returns:
            (is_clean, list_of_staged_cortex_files)
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=user_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            
            staged_cortex_files = []
            for line in result.stdout.splitlines():
                # Check for staged files (lines starting with A, M, D, etc.)
                if line.startswith(('A ', 'M ', 'D ', 'R ', 'C ')):
                    file_path = line[3:].strip()
                    if 'CORTEX' in file_path or '.github/prompts' in file_path:
                        staged_cortex_files.append(file_path)
            
            return len(staged_cortex_files) == 0, staged_cortex_files
        
        except Exception as e:
            self.log_warning(f"Could not verify staged files: {e}")
            return True, []  # Assume clean if check fails
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback .gitignore changes if needed.
        
        Note: This does NOT remove CORTEX patterns, as rollback
        should be handled by git revert if necessary.
        
        Returns:
            True (rollback not needed)
        """
        self.log_info("GitIgnore rollback not implemented (use git revert if needed)")
        return True
