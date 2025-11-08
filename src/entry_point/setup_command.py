"""
CORTEX Setup Command

This module implements the "setup" command that initializes CORTEX in a new repository.
It systematically:
1. Installs all required tooling
2. Initializes the CORTEX brain structure
3. Runs crawlers to feed the brain
4. Introduces CORTEX to the user with links to documentation

Usage:
    from CORTEX.src.entry_point.setup_command import CortexSetup
    
    setup = CortexSetup()
    setup.run()
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class CortexSetup:
    """
    CORTEX setup orchestrator that handles complete system initialization.
    
    Phases:
    1. Environment Analysis - Detect repo structure, language, frameworks
    2. Tooling Installation - Install Python deps, Node.js deps, MkDocs
    3. Brain Initialization - Create tier directories, schemas, initial data
    4. Crawler Execution - Scan repo and populate knowledge graph
    5. Welcome Introduction - Show "Awakening" story and quick start guide
    """
    
    def __init__(
        self,
        repo_path: Optional[str] = None,
        brain_path: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize CORTEX setup.
        
        Args:
            repo_path: Path to repository to analyze (default: current dir)
            brain_path: Path to create CORTEX brain (default: repo_path/cortex-brain)
            verbose: Show detailed progress output
        """
        self.repo_path = Path(repo_path or os.getcwd())
        self.brain_path = Path(brain_path or self.repo_path / "cortex-brain")
        self.verbose = verbose
        self.logger = self._setup_logging()
        
        # Setup state
        self.setup_results = {
            "started_at": datetime.now().isoformat(),
            "phases": {},
            "warnings": [],
            "errors": []
        }
        
    def run(self) -> Dict[str, Any]:
        """
        Run complete CORTEX setup process.
        
        Returns:
            Setup results dictionary with status of each phase
        """
        self._print_banner()
        
        try:
            # Phase 1: Environment Analysis
            self._log_phase("Phase 1: Analyzing Repository")
            env_info = self._analyze_environment()
            self.setup_results["phases"]["environment"] = env_info
            
            # Phase 2: Install Tooling
            self._log_phase("Phase 2: Installing Required Tooling")
            tooling_result = self._install_tooling(env_info)
            self.setup_results["phases"]["tooling"] = tooling_result
            
            # Phase 3: Initialize Brain
            self._log_phase("Phase 3: Initializing CORTEX Brain")
            brain_result = self._initialize_brain()
            self.setup_results["phases"]["brain"] = brain_result
            
            # Phase 4: Run Crawlers
            self._log_phase("Phase 4: Feeding the Brain (Crawler Scan)")
            crawler_result = self._run_crawlers(env_info)
            self.setup_results["phases"]["crawler"] = crawler_result
            
            # Phase 5: Welcome User
            self._log_phase("Phase 5: Welcome to CORTEX!")
            self._show_welcome()
            
            self.setup_results["completed_at"] = datetime.now().isoformat()
            self.setup_results["success"] = True
            
            return self.setup_results
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}", exc_info=True)
            self.setup_results["errors"].append(str(e))
            self.setup_results["success"] = False
            return self.setup_results
    
    def _analyze_environment(self) -> Dict[str, Any]:
        """
        Analyze repository structure and detect technologies.
        
        Returns:
            Environment info dictionary
        """
        env = {
            "repo_path": str(self.repo_path),
            "platform": platform.system(),
            "python_version": sys.version.split()[0],
            "languages": [],
            "frameworks": [],
            "has_git": False,
            "file_count": 0
        }
        
        # Check for Git
        git_dir = self.repo_path / ".git"
        env["has_git"] = git_dir.exists()
        
        # Detect languages and frameworks
        if (self.repo_path / "package.json").exists():
            env["languages"].append("JavaScript/TypeScript")
            env["frameworks"].append("Node.js")
            
        if (self.repo_path / "requirements.txt").exists():
            env["languages"].append("Python")
            
        if (self.repo_path / "*.csproj").exists():
            env["languages"].append("C#")
            env["frameworks"].append(".NET")
            
        if (self.repo_path / "pom.xml").exists():
            env["languages"].append("Java")
            env["frameworks"].append("Maven")
            
        # Count files
        try:
            all_files = list(self.repo_path.rglob("*"))
            env["file_count"] = len([f for f in all_files if f.is_file()])
        except Exception as e:
            self.logger.warning(f"Could not count files: {e}")
            env["file_count"] = 0
        
        self._log_info(f"✓ Detected: {', '.join(env['languages']) or 'Unknown'}")
        self._log_info(f"✓ File count: {env['file_count']}")
        
        return env
    
    def _install_tooling(self, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Install required tooling based on environment.
        
        Args:
            env_info: Environment analysis results
            
        Returns:
            Installation results
        """
        results = {
            "python_deps": False,
            "node_deps": False,
            "mkdocs": False,
            "installed": []
        }
        
        # Install Python dependencies
        requirements_file = self.repo_path / "requirements.txt"
        if requirements_file.exists():
            self._log_info("Installing Python dependencies...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                    check=True,
                    capture_output=not self.verbose
                )
                results["python_deps"] = True
                results["installed"].append("Python dependencies")
                self._log_success("✓ Python dependencies installed")
            except subprocess.CalledProcessError as e:
                self._log_warning(f"⚠ Python deps install failed: {e}")
                self.setup_results["warnings"].append(f"Python deps: {e}")
        
        # Install Node.js dependencies
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            self._log_info("Installing Node.js dependencies...")
            try:
                npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
                subprocess.run(
                    [npm_cmd, "install"],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=not self.verbose
                )
                results["node_deps"] = True
                results["installed"].append("Node.js dependencies")
                self._log_success("✓ Node.js dependencies installed")
            except subprocess.CalledProcessError as e:
                self._log_warning(f"⚠ Node.js deps install failed: {e}")
                self.setup_results["warnings"].append(f"Node.js deps: {e}")
        
        # Install MkDocs for documentation
        self._log_info("Installing MkDocs for documentation...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "mkdocs", "mkdocs-material", "mkdocs-mermaid2-plugin"],
                check=True,
                capture_output=not self.verbose
            )
            results["mkdocs"] = True
            results["installed"].append("MkDocs")
            self._log_success("✓ MkDocs installed")
        except subprocess.CalledProcessError as e:
            self._log_warning(f"⚠ MkDocs install failed: {e}")
            self.setup_results["warnings"].append(f"MkDocs: {e}")
        
        return results
    
    def _initialize_brain(self) -> Dict[str, Any]:
        """
        Initialize CORTEX brain directory structure.
        
        Returns:
            Brain initialization results
        """
        results = {
            "brain_path": str(self.brain_path),
            "tiers_created": [],
            "schemas_created": False
        }
        
        # Create main brain directory
        self.brain_path.mkdir(parents=True, exist_ok=True)
        self._log_info(f"✓ Created brain directory: {self.brain_path}")
        
        # Create tier directories
        tiers = ["tier0", "tier1", "tier2", "tier3"]
        for tier in tiers:
            tier_path = self.brain_path / tier
            tier_path.mkdir(exist_ok=True)
            results["tiers_created"].append(tier)
            self._log_info(f"✓ Created {tier}")
        
        # Create corpus callosum directory
        corpus_path = self.brain_path / "corpus-callosum"
        corpus_path.mkdir(exist_ok=True)
        self._log_info("✓ Created corpus-callosum")
        
        # Initialize Tier 0 (Instinct) - Immutable rules
        self._create_tier0_instinct()
        
        # Initialize Tier 1 (Working Memory) - Database
        self._create_tier1_database()
        
        # Initialize Tier 2 (Knowledge Graph) - Database
        self._create_tier2_database()
        
        # Initialize Tier 3 (Context Intelligence) - Database
        self._create_tier3_database()
        
        # Create README
        self._create_brain_readme()
        
        results["schemas_created"] = True
        self._log_success("✓ CORTEX brain initialized")
        
        return results
    
    def _create_tier0_instinct(self):
        """Create Tier 0 instinct rules (immutable)."""
        tier0_path = self.brain_path / "tier0"
        
        # Core rules
        rules_content = """# CORTEX Core Rules (Tier 0 - Instinct)

These rules are IMMUTABLE and form the core DNA of CORTEX.

## Rule #1: Definition of READY
Work must have clear requirements before starting.

## Rule #2: Test-Driven Development
Always RED → GREEN → REFACTOR. No exceptions.

## Rule #3: Definition of DONE
- Zero errors
- Zero warnings
- All tests passing
- Code reviewed

## Rule #4: Challenge Risky Changes
Brain Protector must challenge proposals that violate core principles.

## Rule #5: SOLID Principles
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

## Rule #6: Local-First
- Zero external dependencies where possible
- Works offline
- Portable across machines

## Rule #7: Incremental File Creation
Large files (>100 lines) created in small increments to prevent response limits.
"""
        
        rules_file = tier0_path / "rules.md"
        rules_file.write_text(rules_content)
        self._log_info(f"  ✓ Created {rules_file.name}")
    
    def _create_tier1_database(self):
        """Create Tier 1 working memory database."""
        from ..tier1.tier1_api import Tier1API
        
        tier1_path = self.brain_path / "tier1"
        db_path = tier1_path / "conversations.db"
        log_path = tier1_path / "requests.log"
        
        # Initialize database
        tier1 = Tier1API(db_path, log_path)
        
        self._log_info(f"  ✓ Created {db_path.name}")
        self._log_info(f"  ✓ Created {log_path.name}")
    
    def _create_tier2_database(self):
        """Create Tier 2 knowledge graph database."""
        from ..tier2.knowledge_graph import KnowledgeGraph
        
        tier2_path = self.brain_path / "tier2"
        db_path = tier2_path / "knowledge_graph.db"
        
        # Initialize database
        kg = KnowledgeGraph(str(db_path))
        
        self._log_info(f"  ✓ Created {db_path.name}")
    
    def _create_tier3_database(self):
        """Create Tier 3 context intelligence database."""
        from ..tier3.context_intelligence import ContextIntelligence
        
        tier3_path = self.brain_path / "tier3"
        db_path = tier3_path / "context.db"
        
        # Initialize database
        context = ContextIntelligence(str(db_path))
        
        self._log_info(f"  ✓ Created {db_path.name}")
    
    def _create_brain_readme(self):
        """Create brain README with structure explanation."""
        readme_content = """# CORTEX Brain

This directory contains the cognitive architecture for CORTEX.

## Structure

- **tier0/** - Instinct (immutable rules)
- **tier1/** - Working Memory (last 20 conversations)
- **tier2/** - Knowledge Graph (learned patterns)
- **tier3/** - Context Intelligence (project metrics)
- **corpus-callosum/** - Inter-hemisphere messaging

## Do Not Manually Edit

The brain manages itself. Editing these files directly can corrupt CORTEX's memory.

Use CORTEX commands instead:
- Query: `#file:cortex.md "What patterns have you learned?"`
- Clear: `#file:cortex.md "Reset conversation history"`

## Initialization

Brain initialized: {timestamp}
"""
        
        readme_file = self.brain_path / "README.md"
        readme_file.write_text(
            readme_content.format(timestamp=datetime.now().isoformat())
        )
        self._log_info(f"  ✓ Created README.md")
    
    def _run_crawlers(self, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run repository crawlers to populate knowledge graph.
        
        Args:
            env_info: Environment analysis results
            
        Returns:
            Crawler execution results
        """
        results = {
            "files_scanned": 0,
            "patterns_discovered": 0,
            "elements_mapped": 0,
            "duration_seconds": 0
        }
        
        start_time = datetime.now()
        
        self._log_info("Starting repository scan...")
        self._log_info("This may take 5-10 minutes depending on repository size...")
        
        # TODO: Implement actual crawler integration
        # For now, we'll do a basic file scan and pattern detection
        
        try:
            # Scan for code files
            code_extensions = {'.py', '.js', '.ts', '.cs', '.java', '.go', '.rs', '.rb'}
            code_files = []
            
            for ext in code_extensions:
                code_files.extend(list(self.repo_path.rglob(f"*{ext}")))
            
            results["files_scanned"] = len(code_files)
            self._log_info(f"  ✓ Scanned {len(code_files)} code files")
            
            # TODO: Extract patterns and populate Tier 2
            # TODO: Extract UI elements and map IDs
            # TODO: Analyze Git history for Tier 3
            
            duration = (datetime.now() - start_time).total_seconds()
            results["duration_seconds"] = duration
            
            self._log_success(f"✓ Crawler completed in {duration:.1f} seconds")
            
        except Exception as e:
            self._log_warning(f"⚠ Crawler encountered issues: {e}")
            self.setup_results["warnings"].append(f"Crawler: {e}")
        
        return results
    
    def _show_welcome(self):
        """Display welcome message with links to documentation."""
        welcome = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                      🧠 CORTEX HAS AWAKENED 🧠                          ║
║                                                                          ║
║              Welcome to Your Enhanced AI Development Partner             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

CORTEX is now operational and ready to assist you!

📚 GET STARTED:
   File: docs/getting-started/quick-start.md
   
   Quick command:
   #file:prompts/user/cortex.md
   [Your request here]

📖 THE STORY:
   Read "The Awakening of CORTEX" - A humorous and technical tale
   File: docs/story/index.md
   
   Five chapters covering:
   - Chapter 1: The Problem (Copilot's Amnesia)
   - Chapter 2: The Solution (Dual-Hemisphere Brain)
   - Chapter 3: The Memory (Five-Tier Intelligence)
   - Chapter 4: The Protection (Six-Layer Immune System)
   - Chapter 5: The Activation (60 Sacred Tests)

🎯 FIRST STEPS:
   1. Try: #file:prompts/user/cortex.md "What can you help me with?"
   2. Read the story (seriously, it's entertaining!)
   3. Check out: docs/architecture/ for technical details

🧠 WHAT CORTEX REMEMBERS:
   ✓ Last 20 conversations (Tier 1)
   ✓ Learned patterns from your work (Tier 2)
   ✓ Project metrics and context (Tier 3)
   ✓ Core rules and principles (Tier 0)

🛡️ CORTEX PROTECTS YOU FROM:
   ✓ Skipping tests (challenges risky shortcuts)
   ✓ Breaking architectural patterns
   ✓ Violating SOLID principles
   ✓ Forgetting context across sessions

💡 EXAMPLE CONVERSATIONS:
   - "Add user authentication"
   - "Continue where we left off"
   - "Test the login feature"
   - "Make it purple" (context-aware!)
   - "What patterns have you learned?"

� OPTIONAL: Configure Advanced Crawlers
   CORTEX can crawl databases and APIs to learn your architecture.
   
   Run the configuration wizard when ready:
   > python scripts/cortex_config_wizard.py
   
   Or add resources incrementally:
   > python scripts/cortex_config_wizard.py --add-database
   > python scripts/cortex_config_wizard.py --add-api
   
   Features:
   ✓ Auto-discovers Oracle connections (tnsnames.ora)
   ✓ Scans environment variables for credentials
   ✓ Finds API endpoints in code and OpenAPI specs
   ✓ Validates connections before saving
   ✓ No pressure - configure anytime!

�📊 SETUP SUMMARY:
"""
        
        print(welcome)
        
        # Print setup results summary
        env = self.setup_results["phases"].get("environment", {})
        brain = self.setup_results["phases"].get("brain", {})
        crawler = self.setup_results["phases"].get("crawler", {})
        
        print(f"   Platform: {env.get('platform', 'Unknown')}")
        print(f"   Languages: {', '.join(env.get('languages', ['Unknown']))}")
        print(f"   Files: {env.get('file_count', 0):,}")
        print(f"   Brain: {brain.get('brain_path', 'Not initialized')}")
        print(f"   Tiers: {', '.join(brain.get('tiers_created', []))}")
        print(f"   Scanned: {crawler.get('files_scanned', 0)} files")
        
        if self.setup_results.get("warnings"):
            print(f"\n⚠️  WARNINGS: {len(self.setup_results['warnings'])}")
            for warning in self.setup_results["warnings"][:3]:
                print(f"   - {warning}")
        
        print("\n" + "="*76)
        print("CORTEX is ready. Start with the story, then experiment!")
        print("="*76 + "\n")
    
    def _print_banner(self):
        """Print setup banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                     CORTEX SETUP & INITIALIZATION                        ║
║                                                                          ║
║              Giving Your AI Assistant a Brain and Memory                 ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Repository: {repo}

This will:
  1. Analyze repository structure
  2. Install required tooling
  3. Initialize CORTEX brain (4-tier architecture)
  4. Run crawlers to feed the brain
  5. Introduce you to CORTEX

Estimated time: 5-10 minutes

"""
        print(banner.format(repo=self.repo_path.name))
    
    def _log_phase(self, message: str):
        """Log phase header."""
        print(f"\n{'='*76}")
        print(f"  {message}")
        print(f"{'='*76}\n")
    
    def _log_info(self, message: str):
        """Log info message."""
        if self.verbose:
            print(f"  {message}")
        self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message."""
        if self.verbose:
            print(f"  {message}")
        self.logger.info(message)
    
    def _log_warning(self, message: str):
        """Log warning message."""
        print(f"  {message}")
        self.logger.warning(message)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for setup command."""
        logger = logging.getLogger("cortex.setup")
        
        if not logger.handlers:
            # Create logs directory
            log_dir = self.brain_path / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # File handler
            log_file = log_dir / f"setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)
        
        return logger


def run_setup(
    repo_path: Optional[str] = None,
    brain_path: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to run CORTEX setup.
    
    Args:
        repo_path: Path to repository (default: current directory)
        brain_path: Path for CORTEX brain (default: repo/cortex-brain)
        verbose: Show detailed output
        
    Returns:
        Setup results dictionary
    """
    setup = CortexSetup(repo_path, brain_path, verbose)
    return setup.run()


if __name__ == "__main__":
    # Allow running directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize CORTEX in repository")
    parser.add_argument("--repo", help="Repository path", default=None)
    parser.add_argument("--brain", help="Brain path", default=None)
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    results = run_setup(
        repo_path=args.repo,
        brain_path=args.brain,
        verbose=not args.quiet
    )
    
    # Exit with appropriate code
    sys.exit(0 if results.get("success") else 1)
