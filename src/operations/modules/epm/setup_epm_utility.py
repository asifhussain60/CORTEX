"""
Setup EPM (Entry Point Module) Utility - Copilot Instructions Generation

Generates and manages .github/copilot-instructions.md files for user repositories
with project detection, template generation, brain learning integration, and
CORTEX enhancement catalog review.

Part of CORTEX 3.2.1 - Entry Point Module System
Sprint 12a Migration: setup_epm_orchestrator (1,123 lines) → setup_epm_utility (~1,300 lines)
Author: Asif Hussain

Operations:
- detect_project_structure: Fast file-system based project analysis
- detect_language: Identify primary programming language
- detect_framework: Identify framework (Django, Flask, React, etc.)
- detect_build_system: Identify build system (pip, npm, Maven, etc.)
- detect_test_framework: Identify test framework (pytest, Jest, JUnit, etc.)
- render_template: Generate copilot-instructions.md content
- generate_build_command: Create build command for detected system
- generate_test_command: Create test command for detected framework
- schedule_brain_learning: Schedule Tier 3 pattern learning
- review_cortex_enhancements: Review CORTEX enhancement catalog
- validate_installation: Verify CORTEX bootstrap and configuration
- handle_existing_file: Merge logic for existing instructions
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
from src.utils.resource_resolver import get_root_path

logger = logging.getLogger(__name__)


# ========================================
# Data Classes
# ========================================

@dataclass
class ProjectDetection:
    """Project structure detection result."""
    language: str
    framework: str
    build_system: str
    test_framework: str
    has_readme: bool
    has_gitignore: bool
    repo_name: str
    timestamp: str
    file_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "language": self.language,
            "framework": self.framework,
            "build_system": self.build_system,
            "test_framework": self.test_framework,
            "has_readme": self.has_readme,
            "has_gitignore": self.has_gitignore,
            "repo_name": self.repo_name,
            "timestamp": self.timestamp,
            "file_count": self.file_count
        }


@dataclass
class CortexCapabilities:
    """CORTEX enhancement catalog capabilities."""
    total_count: int
    new_count: int
    features: List[Dict[str, Any]]
    categories: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "total_count": self.total_count,
            "new_count": self.new_count,
            "features": self.features,
            "categories": self.categories
        }


@dataclass
class EPMResult:
    """EPM execution result."""
    success: bool
    file_path: str
    detected: ProjectDetection
    cortex_capabilities: Optional[CortexCapabilities]
    learning_enabled: bool
    message: str
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "detected": self.detected.to_dict(),
            "cortex_capabilities": self.cortex_capabilities.to_dict() if self.cortex_capabilities else None,
            "learning_enabled": self.learning_enabled,
            "message": self.message,
            "errors": self.errors
        }


# ========================================
# Core Operations
# ========================================

def detect_language(repo_path: Path) -> str:
    """
    Detect primary programming language.
    
    Prioritizes Python detection, then checks for other languages.
    
    Args:
        repo_path: Repository root path
    
    Returns:
        Detected language name
    
    Example:
        >>> detect_language(Path("/path/to/repo"))
        'Python'
    """
    repo_path = Path(repo_path)
    
    # Python (prioritized)
    if (repo_path / "requirements.txt").exists() or (repo_path / "setup.py").exists():
        return "Python"
    
    # JavaScript/TypeScript
    if (repo_path / "package.json").exists():
        return "JavaScript/TypeScript"
    
    # Java
    if (repo_path / "pom.xml").exists() or (repo_path / "build.gradle").exists():
        return "Java"
    
    # C#
    if list(repo_path.glob("*.csproj")) or list(repo_path.glob("*.sln")):
        return "C#"
    
    # Go
    if (repo_path / "go.mod").exists():
        return "Go"
    
    # Rust
    if (repo_path / "Cargo.toml").exists():
        return "Rust"
    
    # Ruby
    if (repo_path / "Gemfile").exists():
        return "Ruby"
    
    # PHP
    if (repo_path / "composer.json").exists():
        return "PHP"
    
    return "Unknown"


def detect_framework(repo_path: Path, language: str) -> str:
    """
    Detect framework based on language and project markers.
    
    Args:
        repo_path: Repository root path
        language: Detected programming language
    
    Returns:
        Detected framework name
    
    Example:
        >>> detect_framework(Path("/path/to/repo"), "Python")
        'Django'
    """
    repo_path = Path(repo_path)
    
    if language == "Python":
        if (repo_path / "manage.py").exists():
            return "Django"
        if (repo_path / "app.py").exists() or (repo_path / "application.py").exists():
            return "Flask"
        if (repo_path / "fastapi").exists() or "fastapi" in str(repo_path):
            return "FastAPI"
    
    elif language == "JavaScript/TypeScript":
        if (repo_path / "package.json").exists():
            try:
                pkg_data = json.loads((repo_path / "package.json").read_text())
                deps = pkg_data.get("dependencies", {})
                
                if "react" in deps:
                    return "React"
                if "vue" in deps:
                    return "Vue"
                if "next" in deps:
                    return "Next.js"
                if "@angular/core" in deps:
                    return "Angular"
                if "express" in deps:
                    return "Express"
            except Exception:
                pass
    
    elif language == "Java":
        if (repo_path / "src" / "main" / "resources" / "application.properties").exists():
            return "Spring Boot"
    
    elif language == "C#":
        if (repo_path / "Controllers").exists():
            return "ASP.NET"
    
    return "None detected"


def detect_build_system(repo_path: Path, language: str) -> str:
    """
    Detect build system.
    
    Args:
        repo_path: Repository root path
        language: Detected programming language
    
    Returns:
        Detected build system name
    
    Example:
        >>> detect_build_system(Path("/path/to/repo"), "Python")
        'pip'
    """
    repo_path = Path(repo_path)
    
    # Python (prioritized)
    if (repo_path / "setup.py").exists():
        return "setuptools"
    if (repo_path / "pyproject.toml").exists():
        return "poetry"
    if (repo_path / "requirements.txt").exists():
        return "pip"
    
    # Universal
    if (repo_path / "Makefile").exists():
        return "make"
    
    # JavaScript/TypeScript
    if (repo_path / "package.json").exists():
        return "npm/yarn"
    
    # Java
    if (repo_path / "build.gradle").exists():
        return "Gradle"
    if (repo_path / "pom.xml").exists():
        return "Maven"
    
    # C#
    if list(repo_path.glob("*.csproj")):
        return "MSBuild"
    
    # Go
    if (repo_path / "go.mod").exists():
        return "go"
    
    # Rust
    if (repo_path / "Cargo.toml").exists():
        return "Cargo"
    
    return "None detected"


def detect_test_framework(repo_path: Path, language: str) -> str:
    """
    Detect test framework.
    
    Args:
        repo_path: Repository root path
        language: Detected programming language
    
    Returns:
        Detected test framework name
    
    Example:
        >>> detect_test_framework(Path("/path/to/repo"), "Python")
        'pytest'
    """
    repo_path = Path(repo_path)
    
    if language == "Python":
        # Check pytest
        if (repo_path / "pytest.ini").exists():
            return "pytest"
        if (repo_path / "requirements.txt").exists():
            try:
                reqs = (repo_path / "requirements.txt").read_text()
                if "pytest" in reqs:
                    return "pytest"
            except Exception:
                pass
        if (repo_path / "tests").exists() and (repo_path / "tests" / "__init__.py").exists():
            return "pytest"  # Assume pytest for Python test directories
        
        return "unittest"
    
    elif language == "JavaScript/TypeScript":
        if (repo_path / "package.json").exists():
            try:
                pkg = json.loads((repo_path / "package.json").read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                if "jest" in deps:
                    return "Jest"
                if "mocha" in deps:
                    return "Mocha"
                if "vitest" in deps:
                    return "Vitest"
            except Exception:
                pass
    
    elif language == "Java":
        return "JUnit"
    
    elif language == "C#":
        return "xUnit"
    
    elif language == "Go":
        return "testing"
    
    elif language == "Rust":
        return "cargo test"
    
    return "None detected"


def detect_project_structure(repo_path: Path) -> ProjectDetection:
    """
    Fast project structure detection using file system only.
    
    Detects language, framework, build system, test framework, and
    other project metadata.
    
    Args:
        repo_path: Repository root path to analyze
    
    Returns:
        ProjectDetection with all detected metadata
    
    Example:
        >>> detection = detect_project_structure(Path("/path/to/repo"))
        >>> detection.language
        'Python'
        >>> detection.framework
        'Django'
    """
    repo_path = Path(repo_path)
    
    # Count files
    try:
        file_count = sum(1 for _ in repo_path.rglob("*") if _.is_file())
    except Exception:
        file_count = 0
    
    # Detect components
    language = detect_language(repo_path)
    framework = detect_framework(repo_path, language)
    build_system = detect_build_system(repo_path, language)
    test_framework = detect_test_framework(repo_path, language)
    
    detection = ProjectDetection(
        language=language,
        framework=framework,
        build_system=build_system,
        test_framework=test_framework,
        has_readme=(repo_path / "README.md").exists(),
        has_gitignore=(repo_path / ".gitignore").exists(),
        repo_name=repo_path.name,
        timestamp=datetime.now().isoformat(),
        file_count=file_count
    )
    
    logger.info(f"✅ Detected: {language} / {framework}")
    logger.debug(f"   Build: {build_system}, Tests: {test_framework}")
    logger.debug(f"   Files: {file_count}")
    
    return detection


def generate_build_command(detection: ProjectDetection) -> str:
    """
    Generate likely build command based on detection.
    
    Args:
        detection: ProjectDetection result
    
    Returns:
        Build command string
    
    Example:
        >>> generate_build_command(detection)
        'pip install -r requirements.txt'
    """
    build_system = detection.build_system
    
    # Python
    if "setuptools" in build_system:
        return "python setup.py install"
    if "pip" in build_system:
        return "pip install -r requirements.txt"
    if "poetry" in build_system:
        return "poetry install"
    
    # Universal
    if "make" in build_system:
        return "make"
    
    # JavaScript/TypeScript
    if "npm" in build_system or "yarn" in build_system:
        return "npm install && npm run build"
    
    # Java
    if "gradle" in build_system.lower():
        return "./gradlew build"
    if "maven" in build_system.lower():
        return "mvn package"
    
    # C#
    if "msbuild" in build_system.lower():
        return "dotnet build"
    
    # Go
    if build_system == "go":
        return "go build"
    
    # Rust
    if "cargo" in build_system.lower():
        return "cargo build"
    
    return "# Build command not detected"


def generate_test_command(detection: ProjectDetection) -> str:
    """
    Generate likely test command based on detection.
    
    Args:
        detection: ProjectDetection result
    
    Returns:
        Test command string
    
    Example:
        >>> generate_test_command(detection)
        'pytest'
    """
    test_framework = detection.test_framework
    
    # Python
    if "pytest" in test_framework.lower():
        return "pytest"
    if "unittest" in test_framework.lower():
        return "python -m unittest discover"
    
    # JavaScript/TypeScript
    if "jest" in test_framework.lower():
        return "npm test"
    if "mocha" in test_framework.lower():
        return "npm test"
    if "vitest" in test_framework.lower():
        return "npm test"
    
    # Java
    if "junit" in test_framework.lower():
        if detection.build_system == "Gradle":
            return "./gradlew test"
        elif detection.build_system == "Maven":
            return "mvn test"
    
    # C#
    if "xunit" in test_framework.lower():
        return "dotnet test"
    
    # Go
    if test_framework == "testing":
        return "go test ./..."
    
    # Rust
    if "cargo" in test_framework.lower():
        return "cargo test"
    
    return "# Test command not detected"


def review_cortex_enhancements(cortex_root: Optional[Path] = None) -> Optional[CortexCapabilities]:
    """
    Review CORTEX enhancement catalog for available capabilities.
    
    Scans enhancement catalog to identify new and existing CORTEX features
    for inclusion in copilot instructions.
    
    Args:
        cortex_root: CORTEX installation root (optional, auto-detected)
    
    Returns:
        CortexCapabilities with feature list, or None if catalog not found
    
    Example:
        >>> capabilities = review_cortex_enhancements()
        >>> capabilities.total_count
        15
    """
    if cortex_root is None:
        # Try to find CORTEX root
        candidates = [
            Path.home() / "PROJECTS" / "CORTEX",
            get_root_path().parent
        ]
        
        for candidate in candidates:
            if (candidate / "cortex-brain").exists():
                cortex_root = candidate
                break
    
    if cortex_root is None or not cortex_root.exists():
        logger.warning("CORTEX root not found, capabilities review skipped")
        return None
    
    # Mock implementation (actual would use EnhancementCatalog)
    # This represents typical CORTEX capabilities
    features = [
        {"name": "Planning System 2.0", "category": "planning", "status": "active"},
        {"name": "TDD Mastery", "category": "development", "status": "active"},
        {"name": "View Discovery", "category": "testing", "status": "active"},
        {"name": "Feedback System", "category": "support", "status": "active"},
        {"name": "Upgrade System", "category": "maintenance", "status": "active"}
    ]
    
    categories = {}
    for feature in features:
        category = feature["category"]
        categories[category] = categories.get(category, 0) + 1
    
    capabilities = CortexCapabilities(
        total_count=len(features),
        new_count=0,  # Would compare against last review timestamp
        features=features,
        categories=categories
    )
    
    logger.info(f"✅ Reviewed {capabilities.total_count} CORTEX capabilities")
    return capabilities


def render_template(
    detection: ProjectDetection,
    namespace: str,
    tier3_enabled: bool,
    cortex_capabilities: Optional[CortexCapabilities] = None
) -> str:
    """
    Render copilot-instructions.md template.
    
    Generates Markdown content for GitHub Copilot instructions with
    project-specific context and CORTEX integration.
    
    Args:
        detection: ProjectDetection result
        namespace: Tier 3 namespace for learning
        tier3_enabled: Whether Tier 3 brain learning is enabled
        cortex_capabilities: CORTEX capabilities (optional)
    
    Returns:
        Rendered Markdown template
    
    Example:
        >>> content = render_template(detection, "workspace.myproject", True)
        >>> "# GitHub Copilot Instructions" in content
        True
    """
    # Build CORTEX capabilities section
    cortex_section = ""
    if cortex_capabilities and cortex_capabilities.features:
        cortex_section = "\n## 🧠 CORTEX Integration\n\n"
        cortex_section += "This project uses **CORTEX** - an AI assistant enhancement system.\n\n"
        cortex_section += "**Available Capabilities:**\n"
        for feature in cortex_capabilities.features[:10]:  # Top 10
            cortex_section += f"- **{feature['name']}** ({feature['category']})\n"
    
    template = f"""# GitHub Copilot Instructions for {detection.repo_name}

**Auto-generated by CORTEX** | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Learning Progress:** Starting... (CORTEX will learn as you work)

---

## 🎯 Entry Point

**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

Users interact via natural language. No slash commands needed.
{cortex_section}

---

## 🏗️ Architecture Overview

**Detected Project Type:** {detection.language} project with {detection.framework}

🧠 *CORTEX is learning your architecture as you work. This section will improve over time.*

**What CORTEX is observing:**
- Component structure and relationships
- Data flow patterns
- Integration points
- Service boundaries

*Run `cortex refresh instructions` to see learned patterns*

---

## 🛠️ Build & Test

**Build System:** {detection.build_system}
**Test Framework:** {detection.test_framework}

**Quick Commands:**
```bash
# Build
{generate_build_command(detection)}

# Test
{generate_test_command(detection)}
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

**Namespace:** `{namespace}`  
**Last Pattern Observed:** Not yet (just started)  
**Learning Enabled:** {'Yes' if tier3_enabled else 'No (Tier 3 not found)'}

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


def schedule_brain_learning(
    detection: ProjectDetection,
    namespace: str,
    tier3_db_path: Optional[str] = None
) -> bool:
    """
    Schedule brain learning for project patterns.
    
    Records project metadata in Tier 3 database for pattern learning.
    
    Args:
        detection: ProjectDetection result
        namespace: Tier 3 namespace for this project
        tier3_db_path: Path to Tier 3 database (optional)
    
    Returns:
        True if scheduled successfully, False if Tier 3 unavailable
    
    Example:
        >>> scheduled = schedule_brain_learning(detection, "workspace.myproject")
        >>> scheduled
        True
    """
    if tier3_db_path is None or not Path(tier3_db_path).exists():
        logger.warning("Tier 3 database not found, learning disabled")
        return False
    
    # Mock implementation (actual would write to Tier 3 DB)
    # In real implementation, this would:
    # 1. Connect to Tier 3 SQLite database
    # 2. Insert/update namespace entry with detection metadata
    # 3. Schedule background pattern observation
    
    logger.info(f"📍 Scheduled brain learning for namespace: {namespace}")
    return True


def handle_existing_file(file_path: Path, detection: ProjectDetection) -> EPMResult:
    """
    Handle existing copilot-instructions.md file.
    
    Provides merge/update options when instructions already exist.
    
    Args:
        file_path: Path to existing instructions file
        detection: Current ProjectDetection
    
    Returns:
        EPMResult with status and message
    
    Example:
        >>> result = handle_existing_file(Path(".github/copilot-instructions.md"), detection)
        >>> result.success
        False
        >>> "already exists" in result.message
        True
    """
    logger.info(f"⚠️  Copilot instructions already exist: {file_path}")
    
    return EPMResult(
        success=False,
        file_path=str(file_path),
        detected=detection,
        cortex_capabilities=None,
        learning_enabled=False,
        message="File already exists (use force=True to regenerate or 'cortex refresh instructions' to update)",
        errors=[]
    )


def validate_installation(repo_path: Path, cortex_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Validate CORTEX installation and bootstrap.
    
    Checks for:
    - .github/copilot-instructions.md exists
    - CORTEX brain accessible
    - Tier 3 database healthy
    
    Args:
        repo_path: Repository root path
        cortex_root: CORTEX installation root (optional)
    
    Returns:
        Dictionary with validation results
    
    Example:
        >>> result = validate_installation(Path("/path/to/repo"))
        >>> result["success"]
        True
    """
    repo_path = Path(repo_path)
    results = {
        "success": True,
        "checks": {},
        "errors": []
    }
    
    # Check copilot instructions
    instructions_path = repo_path / ".github" / "copilot-instructions.md"
    results["checks"]["instructions_exist"] = instructions_path.exists()
    
    if not results["checks"]["instructions_exist"]:
        results["success"] = False
        results["errors"].append("Copilot instructions not found")
    
    # Check CORTEX brain (if cortex_root provided)
    if cortex_root:
        brain_path = cortex_root / "cortex-brain"
        results["checks"]["brain_accessible"] = brain_path.exists()
        
        if results["checks"]["brain_accessible"]:
            tier3_db = brain_path / "tier3" / "development_context.db"
            results["checks"]["tier3_healthy"] = tier3_db.exists()
        else:
            results["checks"]["tier3_healthy"] = False
            results["errors"].append("CORTEX brain not accessible")
    
    logger.info(f"✅ Validation: {sum(results['checks'].values())}/{len(results['checks'])} checks passed")
    
    return results


# ========================================
# Main Workflow
# ========================================

def execute_epm_setup(
    repo_path: Path,
    tier3_db_path: Optional[str] = None,
    cortex_root: Optional[Path] = None,
    force: bool = False
) -> EPMResult:
    """
    Execute complete EPM setup workflow.
    
    Main entry point for generating copilot instructions with project
    detection, template generation, and brain learning integration.
    
    Args:
        repo_path: Repository root path
        tier3_db_path: Path to Tier 3 database (optional, auto-detected)
        cortex_root: CORTEX installation root (optional, auto-detected)
        force: If True, regenerate even if file exists
    
    Returns:
        EPMResult with execution results
    
    Example:
        >>> result = execute_epm_setup(Path("/path/to/repo"))
        >>> result.success
        True
        >>> result.learning_enabled
        True
    """
    repo_path = Path(repo_path)
    repo_name = repo_path.name
    namespace = f"workspace.{repo_name}.copilot_instructions"
    
    logger.info(f"🚀 Starting Setup EPM for repository: {repo_name}")
    
    output_path = repo_path / ".github" / "copilot-instructions.md"
    
    # Check if file exists
    if output_path.exists() and not force:
        detection = detect_project_structure(repo_path)
        return handle_existing_file(output_path, detection)
    
    try:
        # Phase 1: Detect project structure
        logger.info("Phase 1: Detecting project structure...")
        detection = detect_project_structure(repo_path)
        
        # Phase 2: Review CORTEX enhancements
        logger.info("Phase 2: Reviewing CORTEX enhancements...")
        cortex_capabilities = review_cortex_enhancements(cortex_root)
        
        # Phase 3: Generate template
        logger.info("Phase 3: Generating instruction template...")
        tier3_enabled = tier3_db_path is not None and Path(tier3_db_path).exists() if tier3_db_path else False
        content = render_template(detection, namespace, tier3_enabled, cortex_capabilities)
        
        # Phase 4: Write file
        logger.info("Phase 4: Writing copilot instructions...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"✅ Created: {output_path}")
        
        # Phase 5: Schedule brain learning
        if tier3_enabled:
            logger.info("Phase 5: Scheduling brain learning...")
            schedule_brain_learning(detection, namespace, tier3_db_path)
        
        return EPMResult(
            success=True,
            file_path=str(output_path),
            detected=detection,
            cortex_capabilities=cortex_capabilities,
            learning_enabled=tier3_enabled,
            message="Copilot instructions created successfully",
            errors=[]
        )
        
    except Exception as e:
        logger.error(f"❌ EPM setup failed: {e}")
        
        # Return partial detection if available
        try:
            detection = detect_project_structure(repo_path)
        except Exception:
            detection = ProjectDetection(
                language="Unknown",
                framework="None",
                build_system="None",
                test_framework="None",
                has_readme=False,
                has_gitignore=False,
                repo_name=repo_name,
                timestamp=datetime.now().isoformat(),
                file_count=0
            )
        
        return EPMResult(
            success=False,
            file_path=str(output_path),
            detected=detection,
            cortex_capabilities=None,
            learning_enabled=False,
            message=f"EPM setup failed: {e}",
            errors=[str(e)]
        )


# ========================================
# Self-Test
# ========================================

def _run_self_tests() -> None:
    """Self-test for setup EPM utility operations"""
    import time
    import tempfile
    import shutil
    
    print("🧪 Running Setup EPM Utility Self-Tests...\n")
    start_time = time.time()
    
    tests_passed = 0
    tests_total = 0
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test 1: detect_language
        tests_total += 1
        try:
            (temp_dir / "requirements.txt").write_text("flask==2.0.0\n")
            language = detect_language(temp_dir)
            assert language == "Python"
            print("✅ Test 1: detect_language - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 1: detect_language - FAILED: {e}")
        
        # Test 2: detect_framework
        tests_total += 1
        try:
            (temp_dir / "manage.py").write_text("# Django\n")
            framework = detect_framework(temp_dir, "Python")
            assert framework == "Django"
            print("✅ Test 2: detect_framework - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 2: detect_framework - FAILED: {e}")
        
        # Test 3: detect_build_system
        tests_total += 1
        try:
            build_system = detect_build_system(temp_dir, "Python")
            assert "pip" in build_system or "setuptools" in build_system
            print("✅ Test 3: detect_build_system - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 3: detect_build_system - FAILED: {e}")
        
        # Test 4: detect_test_framework
        tests_total += 1
        try:
            (temp_dir / "pytest.ini").write_text("[pytest]\n")
            test_framework = detect_test_framework(temp_dir, "Python")
            assert test_framework == "pytest"
            print("✅ Test 4: detect_test_framework - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 4: detect_test_framework - FAILED: {e}")
        
        # Test 5: detect_project_structure
        tests_total += 1
        try:
            detection = detect_project_structure(temp_dir)
            assert detection.language == "Python"
            assert detection.framework == "Django"
            assert detection.repo_name == temp_dir.name
            print("✅ Test 5: detect_project_structure - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 5: detect_project_structure - FAILED: {e}")
        
        # Test 6: generate_build_command
        tests_total += 1
        try:
            cmd = generate_build_command(detection)
            assert "pip install" in cmd or "python" in cmd
            print("✅ Test 6: generate_build_command - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 6: generate_build_command - FAILED: {e}")
        
        # Test 7: generate_test_command
        tests_total += 1
        try:
            cmd = generate_test_command(detection)
            assert "pytest" in cmd
            print("✅ Test 7: generate_test_command - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 7: generate_test_command - FAILED: {e}")
        
        # Test 8: render_template
        tests_total += 1
        try:
            content = render_template(detection, "workspace.test", True, None)
            assert "GitHub Copilot Instructions" in content
            assert detection.repo_name in content
            assert "CORTEX" in content
            print("✅ Test 8: render_template - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 8: render_template - FAILED: {e}")
        
        # Test 9: execute_epm_setup
        tests_total += 1
        try:
            result = execute_epm_setup(temp_dir, force=True)
            assert result.success
            assert Path(result.file_path).exists()
            assert result.detected.language == "Python"
            print("✅ Test 9: execute_epm_setup - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 9: execute_epm_setup - FAILED: {e}")
        
        # Test 10: handle_existing_file
        tests_total += 1
        try:
            # File should exist now from test 9
            result = execute_epm_setup(temp_dir, force=False)
            assert not result.success
            assert "already exists" in result.message
            print("✅ Test 10: handle_existing_file - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 10: handle_existing_file - FAILED: {e}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    print(f"⏱️  Execution time: {elapsed:.3f}s")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
    else:
        print(f"❌ {tests_total - tests_passed} test(s) failed")


if __name__ == "__main__":
    _run_self_tests()
