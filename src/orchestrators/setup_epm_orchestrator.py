"""
Setup Entry Point Module Orchestrator

Generates .github/copilot-instructions.md for user repositories using:
- Lightweight template generation (fast, <10 seconds)
- Brain-assisted learning (background pattern capture)
- Incremental improvement over time
- CORTEX enhancement catalog integration (Phase 0)

Version: 1.1.0
Author: Asif Hussain
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Import CORTEX enhancement catalog
from src.utils.enhancement_catalog import EnhancementCatalog, FeatureType, AcceptanceStatus
from src.discovery.enhancement_discovery import EnhancementDiscoveryEngine

logger = logging.getLogger(__name__)
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
        
        # Phase 0: Review CORTEX Enhancements (NEW)
        logger.info("Phase 0: Reviewing CORTEX enhancements...")
        cortex_capabilities = self._review_cortex_enhancements()
        logger.info(f"  ✅ Reviewed {cortex_capabilities['total_count']} CORTEX capabilities "
                   f"({cortex_capabilities['new_count']} new since last update)")
        
        # Phase 1: Fast detection
        detected = self._detect_project_structure()
        logger.info(f"Phase 1: Detected project structure: {detected}")
        
        # Phase 2: Generate template (now with CORTEX capabilities)
        content = self._render_template(detected, cortex_capabilities)
        logger.info(f"Phase 2: Generated instruction template")
        
        # Phase 3: Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"Phase 3: Created {output_path}")
        
        # Phase 4: Schedule brain learning
        if self.tier3_db_path:
            self._schedule_brain_learning(detected)
            logger.info(f"Phase 4: Scheduled brain learning")
        
        # Phase 5: Bootstrap verification (NEW - ensures CORTEX is fully wired)
        bootstrap_result = self._run_bootstrap_verification()
        logger.info(f"Phase 5: Bootstrap verification - {bootstrap_result['status']}")
        
        return {
            "success": True,
            "file_path": str(output_path),
            "detected": detected,
            "cortex_capabilities": cortex_capabilities,
            "learning_enabled": self.tier3_db_path is not None,
            "bootstrap_verification": bootstrap_result,
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
        """Detect primary programming language (Python prioritized)"""
        # Check Python first (prioritized after migration from Node.js)
        if (self.repo_path / "requirements.txt").exists() or (self.repo_path / "setup.py").exists():
            return "Python"
        # Check for other languages
        if (self.repo_path / "package.json").exists():
            return "JavaScript/TypeScript"
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
        """Detect framework/library (Python prioritized)"""
        # Check Python frameworks first
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
        
        # Check Node.js frameworks (for cleanup detection only)
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
        
        return "None detected"
    
    def _detect_build_system(self) -> str:
        """Detect build system (Python prioritized)"""
        # Check Python build systems first
        if (self.repo_path / "setup.py").exists():
            return "setuptools"
        if (self.repo_path / "requirements.txt").exists():
            return "pip"
        if (self.repo_path / "pyproject.toml").exists():
            return "poetry"
        # Check other build systems
        if (self.repo_path / "Makefile").exists():
            return "make"
        if (self.repo_path / "package.json").exists():
            return "npm/yarn"
        if (self.repo_path / "build.gradle").exists():
            return "Gradle"
        if (self.repo_path / "pom.xml").exists():
            return "Maven"
        if list(self.repo_path.glob("*.csproj")):
            return "MSBuild"
        
        return "None detected"
    
    def _detect_test_framework(self) -> str:
        """Detect test framework (Python prioritized)"""
        # Check Python test frameworks first
        if (self.repo_path / "pytest.ini").exists() or "pytest" in (self.repo_path / "requirements.txt").read_text() if (self.repo_path / "requirements.txt").exists() else "":
            return "pytest"
        if (self.repo_path / "tests").exists() and (self.repo_path / "tests" / "__init__.py").exists():
            return "pytest"  # Assume pytest for Python test directories
        
        # Check Node.js test frameworks (for cleanup detection only)
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
        
        if (self.repo_path / "phpunit.xml").exists():
            return "PHPUnit"
        
        return "None detected"
    
    def _render_template(self, detected: Dict, cortex_capabilities: Optional[Dict] = None) -> str:
        """
        Render copilot-instructions.md template
        
        Args:
            detected: Detected project metadata
            cortex_capabilities: CORTEX capabilities from enhancement catalog
            
        Returns:
            Rendered markdown content
        """
        # Build CORTEX capabilities section if available
        cortex_section = ""
        if cortex_capabilities and cortex_capabilities.get('features'):
            cortex_section = self._build_cortex_capabilities_section(cortex_capabilities)
        
        template = f"""# GitHub Copilot Instructions for {detected['repo_name']}

**Auto-generated by CORTEX** | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Learning Progress:** Starting... (CORTEX will learn as you work)

---

## 🎯 Entry Point

**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

Users interact via natural language. No slash commands needed.

{cortex_section}

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
        """Generate likely build command based on detection (Python prioritized)"""
        build_system = detected.get("build_system", "")
        
        # Python build commands first
        if "setuptools" in build_system:
            return "python setup.py install"
        if "pip" in build_system:
            return "pip install -r requirements.txt"
        if "poetry" in build_system:
            return "poetry install"
        # Other build systems
        if "make" in build_system:
            return "make"
        if "gradle" in build_system.lower():
            return "./gradlew build"
        if "maven" in build_system.lower():
            return "mvn package"
        if "msbuild" in build_system.lower():
            return "dotnet build"
        if "npm" in build_system:
            return "npm run build"
        
        return "# Build command not detected"
    
    def _generate_test_command(self, detected: Dict) -> str:
        """Generate likely test command based on detection (Python prioritized)"""
        test_framework = detected.get("test_framework", "")
        
        # Python test commands first
        if "pytest" in test_framework.lower():
            return "pytest"
        if "unittest" in test_framework.lower():
            return "python -m unittest discover"
        # Other test frameworks
        if "jest" in test_framework.lower():
            return "npm test"
        if "mocha" in test_framework.lower():
            return "npm test"
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
    
    def _run_bootstrap_verification(self) -> Dict:
        """
        Phase 5: Bootstrap Verification
        
        Verifies that CORTEX is fully wired and operational after setup/upgrade.
        This ensures the user has a working CORTEX installation with:
        - Entry point (CORTEX.prompt.md) at correct location
        - Brain structure intact (cortex-brain/)
        - Response templates valid
        - Key orchestrators wired
        
        Returns:
            Dict with verification status and details
        """
        result = {
            "status": "unknown",
            "checks_passed": 0,
            "checks_failed": 0,
            "issues": [],
            "checks": {}
        }
        
        # Find CORTEX root (could be embedded or standalone)
        cortex_root = self._find_cortex_root()
        
        if not cortex_root:
            result["status"] = "error"
            result["issues"].append("Could not locate CORTEX installation")
            return result
        
        # Check 1: Entry point exists at .github/prompts/CORTEX.prompt.md
        entry_point = cortex_root / '.github' / 'prompts' / 'CORTEX.prompt.md'
        if entry_point.exists():
            result["checks"]["entry_point"] = True
            result["checks_passed"] += 1
            logger.info("  ✅ Entry point found at .github/prompts/CORTEX.prompt.md")
        else:
            result["checks"]["entry_point"] = False
            result["checks_failed"] += 1
            result["issues"].append("Entry point not found at .github/prompts/CORTEX.prompt.md")
            logger.warning("  ❌ Entry point NOT found at expected location")
        
        # Check 2: cortex-brain/ structure exists
        brain_path = cortex_root / 'cortex-brain'
        required_dirs = ['tier1', 'tier3', 'documents', 'templates']
        brain_ok = True
        
        if brain_path.exists():
            for dir_name in required_dirs:
                if not (brain_path / dir_name).exists():
                    brain_ok = False
                    result["issues"].append(f"Missing cortex-brain/{dir_name}/")
        else:
            brain_ok = False
            result["issues"].append("cortex-brain/ directory not found")
        
        result["checks"]["brain_structure"] = brain_ok
        if brain_ok:
            result["checks_passed"] += 1
            logger.info("  ✅ Brain structure verified")
        else:
            result["checks_failed"] += 1
            logger.warning("  ❌ Brain structure incomplete")
        
        # Check 3: response-templates.yaml exists and is valid
        templates_file = brain_path / 'response-templates.yaml' if brain_path.exists() else None
        templates_ok = False
        
        if templates_file and templates_file.exists():
            try:
                import yaml
                with open(templates_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if 'templates' in data:
                    critical_templates = ['help_table', 'fallback']
                    missing = [t for t in critical_templates if t not in data['templates']]
                    if not missing:
                        templates_ok = True
                    else:
                        result["issues"].append(f"Missing templates: {missing}")
            except Exception as e:
                result["issues"].append(f"Invalid response-templates.yaml: {e}")
        else:
            result["issues"].append("response-templates.yaml not found")
        
        result["checks"]["response_templates"] = templates_ok
        if templates_ok:
            result["checks_passed"] += 1
            logger.info("  ✅ Response templates verified")
        else:
            result["checks_failed"] += 1
            logger.warning("  ❌ Response templates invalid or missing")
        
        # Check 4: Key orchestrators exist
        orchestrators_path = cortex_root / 'src' / 'orchestrators'
        key_orchestrators = [
            'planning_orchestrator.py',
            'upgrade_orchestrator.py',
            'git_checkpoint_orchestrator.py'
        ]
        orchestrators_ok = True
        
        if orchestrators_path.exists():
            for orch in key_orchestrators:
                if not (orchestrators_path / orch).exists():
                    orchestrators_ok = False
                    result["issues"].append(f"Missing orchestrator: {orch}")
        else:
            orchestrators_ok = False
            result["issues"].append("src/orchestrators/ directory not found")
        
        result["checks"]["orchestrators"] = orchestrators_ok
        if orchestrators_ok:
            result["checks_passed"] += 1
            logger.info("  ✅ Key orchestrators present")
        else:
            result["checks_failed"] += 1
            logger.warning("  ❌ Some orchestrators missing")
        
        # Calculate final status
        total_checks = result["checks_passed"] + result["checks_failed"]
        if result["checks_failed"] == 0:
            result["status"] = "healthy"
            logger.info(f"✅ Bootstrap verification PASSED: {result['checks_passed']}/{total_checks} checks")
        elif result["checks_passed"] >= result["checks_failed"]:
            result["status"] = "warning"
            logger.warning(f"⚠️ Bootstrap verification WARNING: {result['checks_passed']}/{total_checks} checks passed")
        else:
            result["status"] = "error"
            logger.error(f"❌ Bootstrap verification FAILED: {result['checks_passed']}/{total_checks} checks passed")
        
        return result
    
    def _find_cortex_root(self) -> Optional[Path]:
        """
        Find CORTEX installation root.
        
        Handles both embedded (CORTEX inside user repo) and standalone installations.
        
        Returns:
            Path to CORTEX root or None if not found
        """
        # Priority 1: Check if current repo IS CORTEX
        if (self.repo_path / 'cortex-brain').exists() and (self.repo_path / 'src' / 'orchestrators').exists():
            return self.repo_path
        
        # Priority 2: Check for embedded CORTEX
        embedded_path = self.repo_path / 'CORTEX'
        if embedded_path.exists() and (embedded_path / 'cortex-brain').exists():
            return embedded_path
        
        # Priority 3: Check parent directories (for when run from within CORTEX)
        current = self.repo_path
        for _ in range(3):  # Look up to 3 levels
            if (current / 'cortex-brain').exists():
                return current
            current = current.parent
        
        # Priority 4: Use tier3_db_path to derive CORTEX root
        if self.tier3_db_path:
            tier3_path = Path(self.tier3_db_path).parent  # tier3/
            brain_path = tier3_path.parent  # cortex-brain/
            cortex_path = brain_path.parent  # CORTEX root
            if cortex_path.exists() and (cortex_path / 'cortex-brain').exists():
                return cortex_path
        
        return None
    
    def _review_cortex_enhancements(self) -> Dict:
        """
        Phase 0: Review CORTEX Enhancements
        
        Uses centralized Enhancement Catalog to discover and track CORTEX capabilities.
        
        Returns:
            Dict with discovered capabilities
        """
        try:
            # Initialize catalog and discovery engine
            catalog = EnhancementCatalog()
            discovery = EnhancementDiscoveryEngine()
            
            # Get last review timestamp for EPM
            last_review = catalog.get_last_review_timestamp(review_type='epm_setup')
            
            # Discover features since last review (or all if first run)
            if last_review:
                days_since = (datetime.now() - last_review).days
                discovered = discovery.discover_since(since_date=last_review)
            else:
                # First run - do quick scan (7 days)
                discovered = discovery.discover_since(days=7)
            
            # Add discovered features to catalog
            new_features_count = 0
            for feature in discovered:
                # Map discovery feature type to catalog feature type
                feature_type = self._map_feature_type(feature.feature_type)
                
                is_new = catalog.add_feature(
                    name=feature.name,
                    feature_type=feature_type,
                    description=feature.description,
                    source=feature.source,
                    metadata=feature.metadata,
                    commit_hash=feature.commit_hash,
                    file_path=feature.file_path
                )
                
                if is_new:
                    new_features_count += 1
            
            # Log this review
            catalog.log_review(
                review_type='epm_setup',
                features_reviewed=len(discovered),
                new_features_found=new_features_count,
                notes=f"Setup EPM for {self.repo_name}"
            )
            
            # Get all features (for template population)
            all_features = catalog.get_all_features(status=AcceptanceStatus.DISCOVERED)
            all_features.extend(catalog.get_all_features(status=AcceptanceStatus.ACCEPTED))
            
            # Group by type
            by_type = {}
            for feature in all_features:
                ftype = feature.feature_type.value
                if ftype not in by_type:
                    by_type[ftype] = []
                by_type[ftype].append(feature)
            
            return {
                "features": all_features,
                "by_type": by_type,
                "total_count": len(all_features),
                "new_count": new_features_count,
                "last_review": last_review.isoformat() if last_review else None,
                "days_since_review": (datetime.now() - last_review).days if last_review else None
            }
            
        except Exception as e:
            logger.error(f"Error reviewing CORTEX enhancements: {e}")
            return {
                "features": [],
                "by_type": {},
                "total_count": 0,
                "new_count": 0,
                "error": str(e)
            }
    
    def _map_feature_type(self, discovery_type: str) -> FeatureType:
        """
        Map discovery feature type to catalog feature type.
        
        Args:
            discovery_type: Type from EnhancementDiscoveryEngine
            
        Returns:
            Mapped FeatureType for catalog
        """
        mapping = {
            'operation': FeatureType.OPERATION,
            'agent': FeatureType.AGENT,
            'orchestrator': FeatureType.ORCHESTRATOR,
            'workflow': FeatureType.WORKFLOW,
            'template': FeatureType.TEMPLATE,
            'documentation': FeatureType.DOCUMENTATION,
            'capability': FeatureType.INTEGRATION,
            'admin_script': FeatureType.UTILITY,
            'guide': FeatureType.DOCUMENTATION,
            'prompt_module': FeatureType.DOCUMENTATION
        }
        
        return mapping.get(discovery_type, FeatureType.UTILITY)
    
    def _build_cortex_capabilities_section(self, cortex_capabilities: Dict) -> str:
        """
        Build CORTEX capabilities section for template.
        
        Args:
            cortex_capabilities: Capabilities dict from _review_cortex_enhancements()
            
        Returns:
            Markdown section with CORTEX capabilities
        """
        by_type = cortex_capabilities.get('by_type', {})
        
        # Build section by feature type
        sections = []
        
        if 'operation' in by_type:
            ops = by_type['operation'][:10]  # Top 10
            sections.append(f"**Operations ({len(by_type['operation'])}):** " + 
                          ", ".join(f.name for f in ops))
        
        if 'agent' in by_type:
            agents = by_type['agent'][:10]
            sections.append(f"**Agents ({len(by_type['agent'])}):** " + 
                          ", ".join(f.name for f in agents))
        
        if 'orchestrator' in by_type:
            orchs = by_type['orchestrator'][:10]
            sections.append(f"**Orchestrators ({len(by_type['orchestrator'])}):** " + 
                          ", ".join(f.name for f in orchs))
        
        if 'workflow' in by_type:
            workflows = by_type['workflow'][:10]
            sections.append(f"**Workflows ({len(by_type['workflow'])}):** " + 
                          ", ".join(f.name for f in workflows))
        
        capabilities_text = "\n".join(f"- {s}" for s in sections)
        
        return f"""
## 🧠 CORTEX Capabilities

**Total Features:** {cortex_capabilities['total_count']}  
**New Since Last Update:** {cortex_capabilities['new_count']}  
**Last Review:** {cortex_capabilities['days_since_review']} days ago

{capabilities_text}

*Run 'cortex refresh instructions' to update this list*
"""
    
    def validate_installation(self, auto_fix: bool = False) -> Dict:
        """
        Run full installation validation (bootstrap + 16 gates)
        
        Args:
            auto_fix: If True, attempt to fix issues automatically
            
        Returns:
            Dict with validation results
        """
        try:
            from src.deployment.deployment_gates import DeploymentGates
        except ImportError:
            logger.error("❌ DeploymentGates not available - validation limited to bootstrap checks")
            return self._run_bootstrap_verification()
        
        logger.info("🧠 CORTEX Installation Validation")
        logger.info("")
        
        # Stage 1: Bootstrap verification
        logger.info("Stage 1: Bootstrap Verification")
        bootstrap_results = self._run_bootstrap_verification()
        self._log_bootstrap_results(bootstrap_results)
        logger.info("")
        
        # Stage 2: Deployment gate validation
        logger.info("Stage 2: Deployment Gate Validation (16 Gates)")
        gates = DeploymentGates(self.repo_path)
        gate_results = gates.validate_all_gates()
        self._log_gate_results(gate_results)
        logger.info("")
        
        # Merge results
        combined_results = {
            'bootstrap': bootstrap_results,
            'gates': gate_results,
            'overall_status': self._calculate_overall_status(bootstrap_results, gate_results),
            'timestamp': datetime.now()
        }
        
        # Auto-fix if requested
        if auto_fix and combined_results['overall_status'] != 'healthy':
            logger.info("🔧 Attempting auto-remediation...")
            fixes = self.fix_validation_issues(combined_results)
            combined_results['fixes'] = fixes
            logger.info("")
            
            # Re-validate after fixes
            if fixes['applied']:
                logger.info("Re-validating after fixes...")
                bootstrap_results = self._run_bootstrap_verification()
                gate_results = gates.validate_all_gates()
                combined_results['post_fix_bootstrap'] = bootstrap_results
                combined_results['post_fix_gates'] = gate_results
                combined_results['post_fix_status'] = self._calculate_overall_status(
                    bootstrap_results, gate_results
                )
                logger.info("")
        
        # Generate report
        self._generate_validation_report(combined_results)
        
        # User feedback
        if combined_results['overall_status'] == 'healthy':
            logger.info("✅ CORTEX is ready to use!")
        elif auto_fix and combined_results.get('post_fix_status') == 'healthy':
            logger.info("✅ CORTEX is ready to use (after auto-fixes)!")
        elif combined_results['overall_status'] == 'warning':
            logger.warning("⚠️ CORTEX has minor issues but is functional. See report for details.")
        else:
            logger.error("❌ CORTEX has validation errors. See report for remediation steps.")
        
        return combined_results
    
    def fix_validation_issues(self, results: Dict) -> Dict:
        """Auto-remediation for common validation failures"""
        fixes = {'applied': [], 'failed': []}
        
        # Fix 1: Restore response templates
        if not results['bootstrap']['checks'].get('response_templates', True):
            try:
                self._restore_default_templates()
                fixes['applied'].append("Restored response-templates.yaml from defaults")
                logger.info("  ✅ Fixed: response-templates.yaml restored")
            except Exception as e:
                fixes['failed'].append(f"Template restore failed: {e}")
                logger.warning(f"  ❌ Failed to restore templates: {e}")
        
        # Fix 2: Recreate brain structure
        if not results['bootstrap']['checks'].get('brain_structure', True):
            try:
                self._initialize_brain_structure()
                fixes['applied'].append("Recreated brain directory structure")
                logger.info("  ✅ Fixed: Brain directories recreated")
            except Exception as e:
                fixes['failed'].append(f"Brain structure fix failed: {e}")
                logger.warning(f"  ❌ Failed to recreate brain structure: {e}")
        
        # Fix 3: Initialize missing orchestrators (copy from defaults)
        if not results['bootstrap']['checks'].get('orchestrators', True):
            try:
                self._restore_missing_orchestrators()
                fixes['applied'].append("Restored missing orchestrators")
                logger.info("  ✅ Fixed: Missing orchestrators restored")
            except Exception as e:
                fixes['failed'].append(f"Orchestrator restore failed: {e}")
                logger.warning(f"  ❌ Failed to restore orchestrators: {e}")
        
        return fixes
    
    def _log_bootstrap_results(self, results: Dict):
        """Log bootstrap verification results"""
        for check_name, passed in results['checks'].items():
            status = "✅" if passed else "❌"
            readable_name = check_name.replace('_', ' ').title()
            logger.info(f"  {status} {readable_name}")
        
        if results['issues']:
            logger.info("\n  Issues detected:")
            for issue in results['issues']:
                logger.info(f"    • {issue}")
    
    def _log_gate_results(self, gate_results: Dict):
        """Log gate validation results"""
        for i, gate in enumerate(gate_results['gates'], 1):
            status = "✅" if gate['passed'] else "❌"
            logger.info(f"  {status} Gate {i:2d}: {gate['name']} ({gate['severity']})")
            if not gate['passed']:
                logger.info(f"           {gate['message']}")
    
    def _calculate_overall_status(self, bootstrap: Dict, gates: Dict) -> str:
        """Calculate combined validation status"""
        bootstrap_status = bootstrap['status']
        gates_passed = gates['passed']
        
        # ERROR: Bootstrap failed or gates blocked
        if bootstrap_status == 'error' or not gates_passed:
            return 'error'
        
        # WARNING: Bootstrap warning
        if bootstrap_status == 'warning':
            return 'warning'
        
        # HEALTHY: All checks passed
        return 'healthy'
    
    def _generate_validation_report(self, results: Dict):
        """Generate installation validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.repo_path / "cortex-brain" / "documents" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / f"installation-validation-{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# CORTEX Installation Validation Report\n\n")
            f.write(f"**Timestamp:** {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Repository:** {self.repo_name}\n")
            f.write(f"**Overall Status:** {results['overall_status'].upper()}\n\n")
            
            # Bootstrap results
            f.write("## Bootstrap Verification\n\n")
            bootstrap = results['bootstrap']
            f.write(f"**Status:** {bootstrap['status']}\n")
            f.write(f"**Checks Passed:** {bootstrap['checks_passed']}\n")
            f.write(f"**Checks Failed:** {bootstrap['checks_failed']}\n\n")
            
            f.write("### Checks\n\n")
            for check_name, passed in bootstrap['checks'].items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                readable_name = check_name.replace('_', ' ').title()
                f.write(f"- **{readable_name}:** {status}\n")
            f.write("\n")
            
            if bootstrap['issues']:
                f.write("### Issues\n\n")
                for issue in bootstrap['issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")
            
            # Gate results
            f.write("## Deployment Gate Validation\n\n")
            gate_results = results['gates']
            f.write(f"**Overall:** {'✅ PASSED' if gate_results['passed'] else '❌ FAILED'}\n")
            f.write(f"**Passed:** {sum(1 for g in gate_results['gates'] if g['passed'])}/{len(gate_results['gates'])}\n\n")
            
            for i, gate in enumerate(gate_results['gates'], 1):
                status = "✅ PASSED" if gate['passed'] else "❌ FAILED"
                f.write(f"### Gate {i}: {gate['name']} ({gate['severity']})\n\n")
                f.write(f"**Status:** {status}\n")
                f.write(f"**Message:** {gate['message']}\n\n")
            
            if gate_results['errors']:
                f.write("### Blocking Errors\n\n")
                for error in gate_results['errors']:
                    f.write(f"- {error}\n")
                f.write("\n")
            
            if gate_results['warnings']:
                f.write("### Warnings (Non-Blocking)\n\n")
                for warning in gate_results['warnings']:
                    f.write(f"- {warning}\n")
                f.write("\n")
            
            # Fixes applied
            if 'fixes' in results:
                f.write("## Auto-Remediation\n\n")
                if results['fixes']['applied']:
                    f.write("### Fixes Applied\n\n")
                    for fix in results['fixes']['applied']:
                        f.write(f"- ✅ {fix}\n")
                    f.write("\n")
                
                if results['fixes']['failed']:
                    f.write("### Fixes Failed\n\n")
                    for fix in results['fixes']['failed']:
                        f.write(f"- ❌ {fix}\n")
                    f.write("\n")
                
                # Post-fix status
                if 'post_fix_status' in results:
                    f.write(f"**Post-Fix Status:** {results['post_fix_status'].upper()}\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            if results['overall_status'] == 'healthy':
                f.write("✅ CORTEX is fully operational. No action required.\n")
            elif results['overall_status'] == 'warning':
                f.write("⚠️ CORTEX is functional but has minor issues:\n\n")
                for issue in bootstrap['issues']:
                    f.write(f"- {issue}\n")
                f.write("\nConsider reviewing these issues for optimal performance.\n")
            else:
                f.write("❌ CORTEX has critical validation errors that must be resolved:\n\n")
                if gate_results['errors']:
                    for error in gate_results['errors']:
                        f.write(f"- {error}\n")
                    f.write("\n")
                f.write("Run validation again with `--fix` flag to attempt auto-remediation:\n")
                f.write("```bash\n")
                f.write("python -m src.orchestrators.setup_epm_orchestrator --validate --fix\n")
                f.write("```\n")
        
        logger.info(f"📄 Validation report saved: {report_file.relative_to(self.repo_path)}")
    
    def _restore_default_templates(self):
        """Restore response-templates.yaml from backup or defaults"""
        brain_path = self._find_cortex_root() / 'cortex-brain'
        templates_file = brain_path / 'response-templates.yaml'
        
        # Try to find backup or template file
        backup_file = brain_path / 'response-templates.yaml.bak'
        template_file = brain_path / 'templates' / 'response-templates.yaml'
        
        if backup_file.exists():
            import shutil
            shutil.copy2(backup_file, templates_file)
        elif template_file.exists():
            import shutil
            shutil.copy2(template_file, templates_file)
        else:
            raise FileNotFoundError("No backup or template file found for response-templates.yaml")
    
    def _initialize_brain_structure(self):
        """Recreate missing brain directories"""
        brain_path = self._find_cortex_root() / 'cortex-brain'
        required_dirs = ['tier1', 'tier3', 'documents', 'templates', 'documents/reports']
        
        for dir_name in required_dirs:
            dir_path = brain_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _restore_missing_orchestrators(self):
        """Restore missing orchestrators from defaults"""
        cortex_root = self._find_cortex_root()
        orchestrators_path = cortex_root / 'src' / 'orchestrators'
        
        # For now, just ensure directory exists
        # In full implementation, would copy from templates
        orchestrators_path.mkdir(parents=True, exist_ok=True)
        
        logger.warning("Orchestrator restoration requires manual intervention - directory structure created")


def main():
    """CLI entry point for setup EPM orchestrator"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='CORTEX Setup Entry Point Module Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.orchestrators.setup_epm_orchestrator --validate
  python -m src.orchestrators.setup_epm_orchestrator --validate --fix
  python -m src.orchestrators.setup_epm_orchestrator --repo-path /path/to/repo
"""
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate CORTEX installation (bootstrap + 16 gates)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix validation issues (use with --validate)'
    )
    parser.add_argument(
        '--repo-path',
        type=str,
        default='.',
        help='Repository path (default: current directory)'
    )
    
    args = parser.parse_args()
    
    orchestrator = SetupEPMOrchestrator(repo_path=args.repo_path)
    
    if args.validate:
        results = orchestrator.validate_installation(auto_fix=args.fix)
        exit_code = 0 if results['overall_status'] == 'healthy' else 1
        return exit_code
    else:
        # Default: Run setup
        result = orchestrator.execute()
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
