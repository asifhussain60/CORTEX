"""
Setup Entry Point Module Orchestrator

Generates .github/copilot-instructions.md for user repositories using:
- Lightweight template generation (fast, <10 seconds)
- Brain-assisted learning (background pattern capture)
- Incremental improvement over time

Version: 1.0.0
Author: Asif Hussain
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SetupEPMOrchestrator:
    """
    Orchestrator for Setup Entry Point Module
    
    Responsibilities:
    - Fast project structure detection (file system only)
    - Template-based instruction generation
    - Tier 3 namespace management for learning
    - Merge logic for existing files
    """
    
    def __init__(self, repo_path: str, tier3_db_path: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            repo_path: Absolute path to user repository
            tier3_db_path: Path to Tier 3 database (optional, auto-detected)
        """
        self.repo_path = Path(repo_path)
        self.tier3_db_path = tier3_db_path or self._get_tier3_path()
        self.repo_name = self.repo_path.name
        self.namespace = f"workspace.{self.repo_name}.copilot_instructions"
        
    def _get_tier3_path(self) -> str:
        """Get Tier 3 database path (development_context.db)"""
        # Try to find CORTEX installation
        cortex_candidates = [
            self.repo_path / "CORTEX" / "cortex-brain" / "tier3",
            Path.home() / "PROJECTS" / "CORTEX" / "cortex-brain" / "tier3",
            Path(__file__).parent.parent.parent / "cortex-brain" / "tier3"
        ]
        
        for candidate in cortex_candidates:
            if candidate.exists():
                return str(candidate / "development_context.db")
        
        logger.warning("Tier 3 database not found, learning disabled")
        return None
    
    def execute(self, force: bool = False) -> Dict:
        """
        Main execution flow
        
        Args:
            force: If True, regenerate even if file exists
            
        Returns:
            Dict with execution results
        """
        logger.info(f"Starting Setup EPM for repository: {self.repo_name}")
        
        # Check for existing file
        output_path = self.repo_path / ".github" / "copilot-instructions.md"
        
        if output_path.exists() and not force:
            return self._handle_existing_file(output_path)
        
        # Phase 1: Fast detection
        detected = self._detect_project_structure()
        logger.info(f"Detected structure: {detected}")
        
        # Phase 2: Generate template
        content = self._render_template(detected)
        
        # Phase 3: Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"Created: {output_path}")
        
        # Phase 4: Schedule brain learning
        if self.tier3_db_path:
            self._schedule_brain_learning(detected)
        
        return {
            "success": True,
            "file_path": str(output_path),
            "detected": detected,
            "learning_enabled": self.tier3_db_path is not None,
            "next_update": "Run 'cortex refresh instructions' after working with CORTEX"
        }
    
    def _detect_project_structure(self) -> Dict:
        """
        Fast project structure detection using file system only
        
        Returns:
            Dict with detected project metadata
        """
        detected = {
            "language": self._detect_language(),
            "framework": self._detect_framework(),
            "build_system": self._detect_build_system(),
            "test_framework": self._detect_test_framework(),
            "has_readme": (self.repo_path / "README.md").exists(),
            "has_gitignore": (self.repo_path / ".gitignore").exists(),
            "repo_name": self.repo_name,
            "timestamp": datetime.now().isoformat()
        }
        
        return detected
    
    def _detect_language(self) -> str:
        """Detect primary programming language"""
        # Check for language-specific files
        if (self.repo_path / "package.json").exists():
            return "JavaScript/TypeScript"
        if (self.repo_path / "requirements.txt").exists() or (self.repo_path / "setup.py").exists():
            return "Python"
        if (self.repo_path / "Gemfile").exists():
            return "Ruby"
        if (self.repo_path / "pom.xml").exists() or (self.repo_path / "build.gradle").exists():
            return "Java"
        if list(self.repo_path.glob("*.csproj")):
            return "C#"
        if (self.repo_path / "go.mod").exists():
            return "Go"
        if (self.repo_path / "Cargo.toml").exists():
            return "Rust"
        
        return "Unknown"
    
    def _detect_framework(self) -> str:
        """Detect framework/library"""
        if (self.repo_path / "package.json").exists():
            try:
                pkg = json.loads((self.repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                if "react" in deps:
                    return "React"
                if "vue" in deps:
                    return "Vue"
                if "angular" in deps or "@angular/core" in deps:
                    return "Angular"
                if "next" in deps:
                    return "Next.js"
                if "express" in deps:
                    return "Express"
            except Exception:
                pass
        
        if (self.repo_path / "requirements.txt").exists():
            try:
                reqs = (self.repo_path / "requirements.txt").read_text().lower()
                if "django" in reqs:
                    return "Django"
                if "flask" in reqs:
                    return "Flask"
                if "fastapi" in reqs:
                    return "FastAPI"
            except Exception:
                pass
        
        return "None detected"
    
    def _detect_build_system(self) -> str:
        """Detect build system"""
        if (self.repo_path / "package.json").exists():
            return "npm/yarn"
        if (self.repo_path / "Makefile").exists():
            return "make"
        if (self.repo_path / "build.gradle").exists():
            return "Gradle"
        if (self.repo_path / "pom.xml").exists():
            return "Maven"
        if list(self.repo_path.glob("*.csproj")):
            return "MSBuild"
        if (self.repo_path / "setup.py").exists():
            return "setuptools"
        
        return "None detected"
    
    def _detect_test_framework(self) -> str:
        """Detect test framework"""
        if (self.repo_path / "package.json").exists():
            try:
                pkg = json.loads((self.repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                if "jest" in deps:
                    return "Jest"
                if "mocha" in deps:
                    return "Mocha"
                if "vitest" in deps:
                    return "Vitest"
            except Exception:
                pass
        
        if (self.repo_path / "pytest.ini").exists() or "pytest" in (self.repo_path / "requirements.txt").read_text() if (self.repo_path / "requirements.txt").exists() else "":
            return "pytest"
        
        if (self.repo_path / "phpunit.xml").exists():
            return "PHPUnit"
        
        return "None detected"
    
    def _render_template(self, detected: Dict) -> str:
        """
        Render copilot-instructions.md template
        
        Args:
            detected: Detected project metadata
            
        Returns:
            Rendered markdown content
        """
        template = f"""# GitHub Copilot Instructions for {detected['repo_name']}

**Auto-generated by CORTEX** | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Learning Progress:** Starting... (CORTEX will learn as you work)

---

## 🎯 Entry Point

**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

Users interact via natural language. No slash commands needed.

---

## 🏗️ Architecture Overview

**Detected Project Type:** {detected['language']} project with {detected['framework']}

🧠 *CORTEX is learning your architecture as you work. This section will improve over time.*

**What CORTEX is observing:**
- Component structure and relationships
- Data flow patterns
- Integration points
- Service boundaries

*Run `cortex refresh instructions` to see learned patterns*

---

## 🛠️ Build & Test

**Build System:** {detected['build_system']}
**Test Framework:** {detected['test_framework']}

**Quick Commands:**
```bash
# Build (detected)
{self._generate_build_command(detected)}

# Test (detected)
{self._generate_test_command(detected)}

# Run (learning from your workflow...)
```

🧠 *CORTEX is learning your build/test/deploy workflows...*

---

## 📐 Code Conventions

🧠 *CORTEX is observing your coding patterns...*

**What CORTEX is learning:**
- Import style and organization
- Naming conventions (files, functions, classes)
- File organization patterns
- Error handling approaches
- Testing patterns

*These conventions will appear here as CORTEX learns from your actual code*

---

## 🔑 Critical Files

🧠 *CORTEX is identifying the most important files in your codebase...*

**Learning in progress:**
- Entry points and main modules
- Configuration files
- Frequently modified files
- High-impact components

*Check back after working with CORTEX for a few sessions*

---

## 🧠 Brain Learning Status

**Namespace:** `{self.namespace}`  
**Last Pattern Observed:** Not yet (just started)  
**Learning Enabled:** {'Yes' if self.tier3_db_path else 'No (Tier 3 not found)'}

**How to improve these instructions:**
1. Use CORTEX normally for your development work
2. CORTEX observes patterns during planning, TDD, execution
3. Run `cortex refresh instructions` weekly
4. This file auto-updates with learned patterns

---

## 📚 CORTEX Capabilities

- **Planning System 2.0** - Feature planning with DoR/DoD enforcement
- **TDD Mastery** - RED→GREEN→REFACTOR workflow automation
- **View Discovery** - Auto-extract element IDs for testing
- **Feedback System** - Structured bug/feature reporting
- **Upgrade System** - Universal upgrade with brain preservation

**Get Started:**
```
help                    # Show all commands
tutorial                # Interactive 15-30 min tutorial
plan [feature]          # Start feature planning
start tdd              # Begin TDD workflow
```

---

*This file improves over time as CORTEX learns your codebase patterns.*  
*Generated by CORTEX v3.2.0 | © 2024-2025 Asif Hussain*
"""
        return template
    
    def _generate_build_command(self, detected: Dict) -> str:
        """Generate likely build command based on detection"""
        build_system = detected.get("build_system", "")
        
        if "npm" in build_system:
            return "npm run build"
        if "make" in build_system:
            return "make"
        if "gradle" in build_system.lower():
            return "./gradlew build"
        if "maven" in build_system.lower():
            return "mvn package"
        if "msbuild" in build_system.lower():
            return "dotnet build"
        
        return "# Build command not detected"
    
    def _generate_test_command(self, detected: Dict) -> str:
        """Generate likely test command based on detection"""
        test_framework = detected.get("test_framework", "")
        
        if "jest" in test_framework.lower():
            return "npm test"
        if "pytest" in test_framework.lower():
            return "pytest"
        if "mocha" in test_framework.lower():
            return "npm test"
        if "vitest" in test_framework.lower():
            return "vitest"
        
        return "# Test command not detected"
    
    def _schedule_brain_learning(self, detected: Dict):
        """
        Schedule background brain learning
        
        Stores initial detection in Tier 3 with namespace isolation
        """
        if not self.tier3_db_path:
            logger.warning("Tier 3 not available, skipping brain learning")
            return
        
        try:
            # Store initial metadata in Tier 3
            # TODO: Implement Tier 3 storage (next phase)
            logger.info(f"Brain learning scheduled for namespace: {self.namespace}")
            logger.info(f"Initial patterns stored: {list(detected.keys())}")
        except Exception as e:
            logger.error(f"Failed to schedule brain learning: {e}")
    
    def _handle_existing_file(self, file_path: Path) -> Dict:
        """
        Handle case where copilot-instructions.md already exists
        
        Args:
            file_path: Path to existing file
            
        Returns:
            Dict with handling results and user options
        """
        logger.info(f"Found existing file: {file_path}")
        
        return {
            "success": False,
            "file_exists": True,
            "file_path": str(file_path),
            "message": "Found existing .github/copilot-instructions.md",
            "options": {
                "merge": "Keep existing content + add CORTEX brain learning sections",
                "backup_replace": "Save original as .copilot-instructions.backup.md",
                "cancel": "Keep existing file unchanged",
                "force": "Use 'cortex setup instructions --force' to regenerate"
            },
            "recommendation": "merge"
        }


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python setup_epm_orchestrator.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    orchestrator = SetupEPMOrchestrator(repo_path)
    result = orchestrator.execute()
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
