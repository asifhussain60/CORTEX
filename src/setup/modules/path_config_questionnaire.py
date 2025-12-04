"""
Path Configuration Questionnaire

Interactive questionnaire for configuring user path preferences.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Optional
from pathlib import Path
from src.setup.models.user_path_config import UserPathConfig
from src.setup.modules.path_detector import PathDetector
import logging

logger = logging.getLogger(__name__)


class PathConfigQuestionnaire:
    """
    Interactive questionnaire for path configuration.
    
    Example:
        questionnaire = PathConfigQuestionnaire("/path/to/repo")
        config = questionnaire.run()
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize questionnaire.
        
        Args:
            workspace_root: Repository root (None = current directory)
        """
        self.workspace_root = workspace_root or str(Path.cwd())
        self.detector = PathDetector(self.workspace_root)
        
    def run(self, interactive: bool = True) -> UserPathConfig:
        """
        Run the complete path configuration questionnaire.
        
        Args:
            interactive: If False, uses detected defaults
        
        Returns:
            UserPathConfig instance
        """
        print("\n" + "=" * 60)
        print("  📁 CORTEX Path Configuration")
        print("=" * 60)
        
        if not interactive:
            return self._generate_default_config()
        
        # Scan repository
        print("\n🔍 Scanning repository structure...")
        scan_results = self.detector.scan_repository()
        
        # Configure test directory
        test_dir = self.ask_test_directory(scan_results)
        
        # Configure document directories
        print("\n📄 Document directories can be customized or use defaults.")
        customize_docs = input("   Customize document paths? [y/N]: ").strip().lower()
        
        if customize_docs == 'y':
            reports_dir = self.ask_directory("reports", "cortex-brain/documents/reports")
            analysis_dir = self.ask_directory("analysis", "cortex-brain/documents/analysis")
            summaries_dir = self.ask_directory("summaries", "cortex-brain/documents/summaries")
            planning_dir = self.ask_directory("planning", "cortex-brain/documents/planning")
            investigations_dir = self.ask_directory("investigations", "cortex-brain/documents/investigations")
        else:
            reports_dir = "cortex-brain/documents/reports"
            analysis_dir = "cortex-brain/documents/analysis"
            summaries_dir = "cortex-brain/documents/summaries"
            planning_dir = "cortex-brain/documents/planning"
            investigations_dir = "cortex-brain/documents/investigations"
        
        # Configure temp directory
        temp_dir = self.ask_directory("temporary files", ".cortex-temp", optional=True)
        
        # Build config
        config = UserPathConfig(
            test_directory=test_dir,
            reports_directory=reports_dir,
            documents_directory="cortex-brain/documents",
            planning_directory=planning_dir,
            analysis_directory=analysis_dir,
            summaries_directory=summaries_dir,
            investigations_directory=investigations_dir,
            temp_directory=temp_dir,
            custom_paths={}
        )
        
        # Summary
        self._print_summary(config)
        
        return config
    
    def ask_test_directory(self, scan_results: dict) -> str:
        """
        Ask user for test directory with intelligent suggestions.
        
        Args:
            scan_results: Results from repository scan
        
        Returns:
            Selected test directory path
        """
        print("\n📋 Application Test Directory Configuration")
        print("   (Where should CORTEX create/find your application tests?)")
        
        test_dirs = scan_results["test_directories"]
        suggested = scan_results["suggested_test_directory"]
        
        if not test_dirs:
            print(f"\n   ℹ️  No existing test directories found.")
            print(f"   ℹ️  Suggested: '{suggested}'")
            print("\n   Options:")
            print(f"   1. Use suggested path ('{suggested}')")
            print("   2. Specify custom path")
            
            while True:
                choice = input("\n   Choice (1-2, default: 1): ").strip()
                
                if not choice or choice == '1':
                    return suggested
                elif choice == '2':
                    custom = input("   Enter custom path (relative to repo root): ").strip()
                    if custom:
                        return custom
                    print("   ⚠️  Path cannot be empty.")
                else:
                    print("   ⚠️  Invalid choice. Please enter 1 or 2.")
        
        else:
            print(f"\n   ℹ️  Found {len(test_dirs)} test director{'y' if len(test_dirs) == 1 else 'ies'}:")
            
            for idx, test_dir in enumerate(test_dirs[:5], 1):  # Show top 5
                framework = f" ({test_dir['framework']})" if test_dir['framework'] != 'unknown' else ""
                confidence = f"{test_dir['confidence']:.0%}"
                print(f"   {idx}. {test_dir['path']}{framework} - {test_dir['test_count']} tests (confidence: {confidence})")
            
            print(f"   {len(test_dirs) + 1}. Use suggested path ('{suggested}')")
            print(f"   {len(test_dirs) + 2}. Specify custom path")
            
            max_choice = len(test_dirs) + 2
            
            while True:
                choice = input(f"\n   Choice (1-{max_choice}, default: 1): ").strip()
                
                if not choice or choice == '1':
                    return test_dirs[0]["path"]
                
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(test_dirs):
                        return test_dirs[idx - 1]["path"]
                    elif idx == len(test_dirs) + 1:
                        return suggested
                    elif idx == len(test_dirs) + 2:
                        custom = input("   Enter custom path (relative to repo root): ").strip()
                        if custom:
                            return custom
                        print("   ⚠️  Path cannot be empty.")
                    else:
                        print(f"   ⚠️  Invalid choice. Please enter 1-{max_choice}.")
                except ValueError:
                    print(f"   ⚠️  Invalid input. Please enter a number (1-{max_choice}).")
    
    def ask_directory(self, category: str, default: str, optional: bool = False) -> Optional[str]:
        """
        Ask for a specific directory path.
        
        Args:
            category: Category name (e.g., "reports", "analysis")
            default: Default path
            optional: If True, allows None/empty
        
        Returns:
            Selected path or None if skipped
        """
        prompt = f"\n   {category.capitalize()} directory"
        suffix = " (Enter to skip)" if optional else f" (default: {default})"
        
        user_input = input(f"{prompt}{suffix}: ").strip()
        
        if not user_input:
            return None if optional else default
        
        return user_input
    
    def _generate_default_config(self) -> UserPathConfig:
        """Generate default configuration without user input."""
        scan_results = self.detector.scan_repository()
        suggested_test = scan_results["suggested_test_directory"]
        
        return UserPathConfig(
            test_directory=suggested_test,
            reports_directory="cortex-brain/documents/reports",
            documents_directory="cortex-brain/documents",
            planning_directory="cortex-brain/documents/planning",
            analysis_directory="cortex-brain/documents/analysis",
            summaries_directory="cortex-brain/documents/summaries",
            investigations_directory="cortex-brain/documents/investigations",
            temp_directory=".cortex-temp",
            custom_paths={}
        )
    
    def _print_summary(self, config: UserPathConfig):
        """Print configuration summary."""
        print("\n" + "=" * 60)
        print("  ✅ Path Configuration Complete")
        print("=" * 60)
        print(f"   Test Directory:          {config.test_directory}")
        print(f"   Reports:                 {config.reports_directory}")
        print(f"   Analysis:                {config.analysis_directory}")
        print(f"   Summaries:               {config.summaries_directory}")
        print(f"   Planning:                {config.planning_directory}")
        print(f"   Investigations:          {config.investigations_directory}")
        if config.temp_directory:
            print(f"   Temp Files:              {config.temp_directory}")
        print("=" * 60)
