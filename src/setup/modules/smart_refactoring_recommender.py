"""
Smart Refactoring Tool Recommender Module

Analyzes the actual codebase from brain context and recommends
ONLY relevant refactoring tools based on detected languages.

Intelligence Sources:
- Tier 3 development context
- File extension analysis from Tier 1
- Language detection from actual code

SOLID Principles:
- Single Responsibility: Only recommends refactoring tools
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on abstractions (Tier 1, Tier 3)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


class ToolPriority(Enum):
    """Priority levels for tool recommendations."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SKIP = "SKIP"


@dataclass
class ToolRecommendation:
    """Recommendation for a refactoring tool."""
    category: str
    language: str
    tools: List[str]
    relevance_percentage: float
    priority: ToolPriority
    reason: str
    install_commands: List[str]
    check_commands: List[str]


class SmartRefactoringRecommender(BaseSetupModule):
    """
    Intelligent refactoring tool recommender.
    
    Analyzes actual codebase from brain context and recommends
    only relevant tools based on detected languages.
    
    Responsibilities:
    1. Query Tier 3 for development context
    2. Analyze file extensions to detect languages
    3. Calculate language distribution percentages
    4. Generate prioritized tool recommendations
    5. Detect installed tools
    6. Provide installation guidance
    """
    
    # Language to file extension mapping
    LANGUAGE_EXTENSIONS = {
        'csharp': ['.cs', '.csproj', '.sln'],
        'typescript': ['.ts', '.tsx'],
        'javascript': ['.js', '.jsx'],
        'angular': ['.component.ts', '.service.ts', '.module.ts'],
        'react': ['.tsx', '.jsx'],
        'sql': ['.sql'],
        'python': ['.py'],
        'java': ['.java'],
        'cpp': ['.cpp', '.h', '.hpp'],
        'go': ['.go'],
        'rust': ['.rs'],
        'ruby': ['.rb'],
        'php': ['.php']
    }
    
    # Tool recommendations per language
    TOOL_MAPPINGS = {
        'csharp': {
            'tools': ['dotnet format', 'Roslyn analyzers', 'StyleCop'],
            'install_commands': [
                'dotnet tool install -g dotnet-format',
                'dotnet add package StyleCop.Analyzers'
            ],
            'check_commands': ['dotnet --version', 'dotnet tool list -g']
        },
        'typescript': {
            'tools': ['ESLint', 'Prettier', 'TSLint (deprecated)'],
            'install_commands': [
                'npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin',
                'npm install --save-dev prettier'
            ],
            'check_commands': ['node --version', 'npm --version']
        },
        'javascript': {
            'tools': ['ESLint', 'Prettier'],
            'install_commands': [
                'npm install --save-dev eslint',
                'npm install --save-dev prettier'
            ],
            'check_commands': ['node --version', 'npm --version']
        },
        'angular': {
            'tools': ['Angular ESLint', 'Prettier'],
            'install_commands': [
                'ng add @angular-eslint/schematics',
                'npm install --save-dev prettier'
            ],
            'check_commands': ['ng version']
        },
        'react': {
            'tools': ['ESLint (React)', 'Prettier'],
            'install_commands': [
                'npm install --save-dev eslint eslint-plugin-react eslint-plugin-react-hooks',
                'npm install --save-dev prettier'
            ],
            'check_commands': ['node --version', 'npm --version']
        },
        'sql': {
            'tools': ['sqlfluff', 'sql-formatter'],
            'install_commands': [
                'pip install sqlfluff',
                'npm install -g sql-formatter'
            ],
            'check_commands': ['sqlfluff --version']
        },
        'python': {
            'tools': ['black', 'flake8', 'mypy', 'rope', 'isort'],
            'install_commands': [
                'pip install black flake8 mypy rope isort'
            ],
            'check_commands': ['black --version', 'flake8 --version']
        }
    }
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Return module metadata."""
        return SetupModuleMetadata(
            module_id="smart_refactoring_recommender",
            name="Smart Refactoring Tool Recommender",
            description="Analyze codebase and recommend relevant refactoring tools",
            phase=SetupPhase.FEATURES,
            priority=35,  # After codebase_crawler (25)
            dependencies=["brain_initialization", "codebase_crawler"],
            optional=True,
            enabled_by_default=True
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for tool recommendation.
        
        Checks:
        1. Brain is initialized
        2. Codebase has been crawled
        3. File statistics available
        """
        issues = []
        
        # Check brain initialization
        brain_root = context.get('brain_root')
        if not brain_root:
            issues.append("Brain root not found - brain must be initialized first")
        
        # Check if codebase crawled
        # We'll check for file statistics in context or development-context.yaml
        dev_context_file = Path(brain_root) / "development-context.yaml" if brain_root else None
        if dev_context_file and not dev_context_file.exists():
            self._log_warning("Development context not found - will use basic file scanning")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute smart tool recommendation.
        
        Steps:
        1. Analyze codebase to detect languages
        2. Calculate language distribution
        3. Generate prioritized recommendations
        4. Check what's already installed
        5. Display recommendations
        """
        start_time = self._get_timestamp()
        
        try:
            self._log_section_header("Smart Refactoring Tool Recommender")
            
            # Step 1: Analyze codebase
            self._log_info("Analyzing codebase languages...")
            language_stats = self._analyze_codebase_languages(context)
            
            if not language_stats:
                self._log_warning("No languages detected - skipping tool recommendations")
                return SetupResult(
                    module_id=self.get_metadata().module_id,
                    status=SetupStatus.SKIPPED,
                    message="No languages detected in codebase",
                    timestamp=start_time
                )
            
            # Step 2: Generate recommendations
            self._log_info("Generating tool recommendations...")
            recommendations = self._generate_recommendations(language_stats)
            
            # Step 3: Check installed tools
            self._log_info("Checking installed tools...")
            installed_tools = self._detect_installed_tools(recommendations)
            
            # Step 4: Display recommendations
            self._display_recommendations(language_stats, recommendations, installed_tools)
            
            # Step 5: Ask user if they want to install
            if context.get('interactive', True):
                self._offer_installation(recommendations, installed_tools)
            
            # Update context
            context['refactoring_tools'] = {
                'languages': language_stats,
                'recommendations': [
                    {
                        'language': r.language,
                        'tools': r.tools,
                        'priority': r.priority.value,
                        'relevance': r.relevance_percentage
                    }
                    for r in recommendations
                ],
                'installed': installed_tools
            }
            
            return SetupResult(
                module_id=self.get_metadata().module_id,
                status=SetupStatus.SUCCESS,
                message=f"Recommended {len(recommendations)} tool categories based on codebase analysis",
                timestamp=start_time,
                metadata={'languages': language_stats, 'recommendations_count': len(recommendations)}
            )
            
        except Exception as e:
            self._log_error(f"Tool recommendation failed: {e}")
            return SetupResult(
                module_id=self.get_metadata().module_id,
                status=SetupStatus.FAILED,
                message=f"Failed to recommend tools: {e}",
                timestamp=start_time
            )
    
    def _analyze_codebase_languages(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze codebase to detect languages and their distribution.
        
        Returns:
            Dictionary mapping language -> percentage
        """
        project_root = context.get('project_root')
        if not project_root:
            return {}
        
        project_root = Path(project_root)
        
        # Scan for files
        extension_counts = {}
        total_files = 0
        
        # Exclude common non-code directories
        exclude_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            'dist', 'build', '.vs', '.vscode', 'bin', 'obj',
            '.cortex', 'cortex-brain'
        }
        
        for file_path in project_root.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1
                    total_files += 1
        
        if total_files == 0:
            return {}
        
        # Map extensions to languages
        language_counts = {}
        
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            count = sum(extension_counts.get(ext, 0) for ext in extensions)
            if count > 0:
                language_counts[lang] = count
        
        # Calculate percentages
        language_percentages = {
            lang: (count / total_files * 100)
            for lang, count in language_counts.items()
        }
        
        # Sort by percentage (descending)
        return dict(sorted(
            language_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def _generate_recommendations(
        self,
        language_stats: Dict[str, float]
    ) -> List[ToolRecommendation]:
        """
        Generate prioritized tool recommendations based on language distribution.
        
        Args:
            language_stats: Dictionary mapping language -> percentage
            
        Returns:
            List of tool recommendations, sorted by priority
        """
        recommendations = []
        
        for language, percentage in language_stats.items():
            # Calculate priority
            if percentage >= 20:
                priority = ToolPriority.HIGH
            elif percentage >= 5:
                priority = ToolPriority.MEDIUM
            elif percentage >= 1:
                priority = ToolPriority.LOW
            else:
                priority = ToolPriority.SKIP
                continue  # Skip languages below 1%
            
            # Get tool mapping
            tool_info = self.TOOL_MAPPINGS.get(language)
            if not tool_info:
                continue
            
            # Create recommendation
            recommendation = ToolRecommendation(
                category=language.upper(),
                language=language,
                tools=tool_info['tools'],
                relevance_percentage=percentage,
                priority=priority,
                reason=f"{percentage:.1f}% of codebase is {language}",
                install_commands=tool_info['install_commands'],
                check_commands=tool_info['check_commands']
            )
            
            recommendations.append(recommendation)
        
        # Sort by priority then percentage
        priority_order = {
            ToolPriority.HIGH: 0,
            ToolPriority.MEDIUM: 1,
            ToolPriority.LOW: 2
        }
        
        recommendations.sort(
            key=lambda r: (priority_order[r.priority], -r.relevance_percentage)
        )
        
        return recommendations
    
    def _detect_installed_tools(
        self,
        recommendations: List[ToolRecommendation]
    ) -> Dict[str, bool]:
        """
        Detect which tools are already installed.
        
        Returns:
            Dictionary mapping tool_name -> installed (bool)
        """
        installed = {}
        
        for rec in recommendations:
            for check_cmd in rec.check_commands:
                cmd_parts = check_cmd.split()
                try:
                    result = subprocess.run(
                        cmd_parts,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    # Tool is installed if command succeeds
                    tool_name = cmd_parts[0]
                    installed[tool_name] = result.returncode == 0
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    installed[cmd_parts[0]] = False
        
        return installed
    
    def _display_recommendations(
        self,
        language_stats: Dict[str, float],
        recommendations: List[ToolRecommendation],
        installed_tools: Dict[str, bool]
    ):
        """Display formatted recommendations to user."""
        
        print("\n" + "=" * 80)
        print("CORTEX Smart Refactoring Tool Recommender")
        print("=" * 80)
        
        # Codebase analysis summary
        print(f"\nCodebase Analysis Complete:")
        print(f"   Languages detected: {len(language_stats)}")
        
        print("\nLanguage Distribution:")
        for lang, percentage in language_stats.items():
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"   {lang.ljust(15)} {percentage:5.1f}%  {bar}")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("Recommended Refactoring Tools (Priority Order)")
        print("=" * 80)
        
        for rec in recommendations:
            # Priority emoji
            if rec.priority == ToolPriority.HIGH:
                emoji = "🔥 HIGH PRIORITY"
            elif rec.priority == ToolPriority.MEDIUM:
                emoji = "🟡 MEDIUM PRIORITY"
            else:
                emoji = "🟢 LOW PRIORITY"
            
            print(f"\n{emoji} ({rec.relevance_percentage:.1f}% relevance)")
            print(f"   Category: {rec.category}")
            print(f"   Tools:")
            for tool in rec.tools:
                status = "✓ Installed" if any(
                    cmd.startswith(tool.split()[0].lower()) and installed_tools.get(tool.split()[0].lower())
                    for cmd in rec.check_commands
                ) else "○ Not installed"
                print(f"   - {tool} [{status}]")
            
            print(f"\n   Install:")
            for cmd in rec.install_commands:
                print(f"   > {cmd}")
            
            print(f"\n   Reason: {rec.reason}")
        
        print("\n" + "=" * 80)
    
    def _offer_installation(
        self,
        recommendations: List[ToolRecommendation],
        installed_tools: Dict[str, bool]
    ):
        """Offer to install recommended tools."""
        
        # Count missing tools
        missing_count = sum(
            1 for rec in recommendations
            for cmd in rec.check_commands
            if not installed_tools.get(cmd.split()[0], False)
        )
        
        if missing_count == 0:
            print("\n✓ All recommended tools are already installed!")
            return
        
        print(f"\nFound {missing_count} recommended tools not yet installed.")
        print("\nNote: This will NOT install automatically.")
        print("      Copy the install commands above and run them manually.")
        print("      This ensures you control what gets installed on your machine.")


def register() -> BaseSetupModule:
    """Register the smart refactoring recommender module."""
    return SmartRefactoringRecommender()
