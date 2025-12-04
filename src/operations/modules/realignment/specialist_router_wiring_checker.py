"""
Specialist Router Wiring Checker for CORTEX Align v2.0

Detects and fixes unwired specialist intent routers (TDD, Strategic, etc.)
that exist but aren't integrated into the main request flow.

Problem:
- Specialist routers exist (TDDIntentRouter, etc) but aren't called
- Main IntentRouter in cortex_agents/intent_router.py doesn't delegate to them
- Result: Features like auto-TDD activation don't work

Solution:
- Detect all specialist router classes
- Check if main IntentRouter imports and uses them
- Auto-generate wiring code to integrate them
- Validate integration after fix

Author: Asif Hussain
Date: December 4, 2025
Version: 1.0.0
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SpecialistRouter:
    """Metadata about a specialist intent router."""
    name: str  # Class name (e.g., "TDDIntentRouter")
    file_path: Path  # Full path to router file
    module_path: str  # Import path (e.g., "src.cortex_agents.test_generator.tdd_intent_router")
    purpose: str  # What it does (extracted from docstring)
    intents_handled: List[str]  # Intent types it handles
    is_wired: bool  # Whether it's integrated into main flow


@dataclass
class WiringIssue:
    """An unwired router that needs integration."""
    router: SpecialistRouter
    severity: str  # "critical", "high", "medium"
    impact: str  # User-facing description of missing functionality
    fix_description: str  # What needs to be done


class SpecialistRouterWiringChecker:
    """Detects and fixes unwired specialist routers."""
    
    # Known specialist router patterns
    SPECIALIST_PATTERNS = [
        "**/tdd_intent_router.py",
        "**/tactical/intent_router.py",
        "**/*_intent_router.py"
    ]
    
    # Main router that should integrate them
    MAIN_ROUTER_PATH = "src/cortex_agents/intent_router.py"
    
    def __init__(self, cortex_root: Path):
        """
        Initialize wiring checker.
        
        Args:
            cortex_root: Root directory of CORTEX installation
        """
        self.cortex_root = cortex_root
        self.main_router = cortex_root / self.MAIN_ROUTER_PATH
        
    def check_wiring(self) -> Dict[str, Any]:
        """
        Check if all specialist routers are properly wired.
        
        Returns:
            Dict with:
                - passed (bool): True if all routers wired
                - specialist_routers (list): All specialist routers found
                - wired_routers (list): Routers properly integrated
                - unwired_routers (list): Routers NOT integrated
                - issues (list): WiringIssue objects for unwired routers
        """
        logger.info("🔍 Scanning for specialist intent routers...")
        
        # Discover all specialist routers
        routers = self._discover_specialist_routers()
        logger.info(f"   Found {len(routers)} specialist router(s)")
        
        # Check which are wired
        wired = []
        unwired = []
        issues = []
        
        for router in routers:
            if router.is_wired:
                wired.append(router)
                logger.info(f"   ✅ {router.name} - Wired")
            else:
                unwired.append(router)
                issue = self._create_wiring_issue(router)
                issues.append(issue)
                logger.warning(f"   ❌ {router.name} - NOT WIRED")
        
        passed = len(unwired) == 0
        
        return {
            "passed": passed,
            "total_specialist_routers": len(routers),
            "wired_count": len(wired),
            "unwired_count": len(unwired),
            "specialist_routers": [
                {
                    "name": r.name,
                    "file": str(r.file_path.relative_to(self.cortex_root)),
                    "purpose": r.purpose,
                    "intents_handled": r.intents_handled,
                    "wired": r.is_wired
                }
                for r in routers
            ],
            "wired_routers": [r.name for r in wired],
            "unwired_routers": [r.name for r in unwired],
            "issues": [
                {
                    "router": issue.router.name,
                    "severity": issue.severity,
                    "impact": issue.impact,
                    "fix": issue.fix_description
                }
                for issue in issues
            ]
        }
    
    def fix_wiring(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Auto-fix unwired specialist routers.
        
        Args:
            dry_run: If True, don't modify files, just report what would change
        
        Returns:
            Dict with:
                - success (bool): True if all fixes applied
                - fixes_applied (list): Fixes that were applied
                - fixes_skipped (list): Fixes that couldn't be applied
                - errors (list): Errors encountered
        """
        check_result = self.check_wiring()
        
        if check_result["passed"]:
            logger.info("✅ All specialist routers already wired")
            return {
                "success": True,
                "fixes_applied": [],
                "fixes_skipped": [],
                "errors": []
            }
        
        logger.info(f"🔧 Fixing {check_result['unwired_count']} unwired router(s)...")
        
        fixes_applied = []
        fixes_skipped = []
        errors = []
        
        for issue_data in check_result["issues"]:
            router_name = issue_data["router"]
            
            try:
                if dry_run:
                    logger.info(f"   [DRY RUN] Would wire {router_name}")
                    fixes_applied.append(f"Wire {router_name} into main IntentRouter")
                else:
                    success = self._apply_wiring_fix(router_name)
                    if success:
                        logger.info(f"   ✅ Wired {router_name}")
                        fixes_applied.append(f"Wired {router_name} into main IntentRouter")
                    else:
                        logger.warning(f"   ⏭️  Skipped {router_name} - manual wiring required")
                        fixes_skipped.append(f"Manual wiring required for {router_name}")
            except Exception as e:
                logger.error(f"   ❌ Failed to wire {router_name}: {e}")
                errors.append(f"Failed to wire {router_name}: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "fixes_applied": fixes_applied,
            "fixes_skipped": fixes_skipped,
            "errors": errors
        }
    
    def _discover_specialist_routers(self) -> List[SpecialistRouter]:
        """Find all specialist router classes in codebase."""
        routers = []
        
        # Search for router files
        for pattern in self.SPECIALIST_PATTERNS:
            for file_path in self.cortex_root.glob(pattern):
                # Skip main router
                if file_path.samefile(self.main_router):
                    continue
                
                # Skip test files
                if "test" in file_path.name or "/tests/" in str(file_path):
                    continue
                
                # Skip archived/obsolete files
                file_str = str(file_path)
                if any(skip in file_str for skip in ['/archives/', '/obsolete-', '/backups/', '/cortex-brain/archives/']):
                    continue
                
                # Only consider files in src/ directory
                if '/src/' not in file_str:
                    continue
                
                # Skip other IntentRouter implementations (not specialist routers)
                # Strategic IntentRouter is a standalone implementation used by src/router.py
                # Components IntentRouter is for entry-point routing
                # Only TDD and similar SPECIALIST routers should be wired
                if file_path.stem == "intent_router" and "strategic" in str(file_path):
                    continue
                
                # Extract router info
                router = self._extract_router_info(file_path)
                if router:
                    routers.append(router)
        
        return routers
    
    def _extract_router_info(self, file_path: Path) -> Optional[SpecialistRouter]:
        """Extract metadata from a router file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Find router class
            router_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if "Router" in node.name and node.name != "IntentRouter":
                        router_class = node
                        break
                    elif node.name == "IntentRouter" and "strategic" in str(file_path):
                        router_class = node
                        break
            
            if not router_class:
                return None
            
            # Extract docstring
            docstring = ast.get_docstring(router_class) or ""
            purpose = docstring.split('\n')[0] if docstring else "Unknown purpose"
            
            # Extract intents handled (look for Intent enums or patterns)
            intents_handled = self._extract_intents(content)
            
            # Check if wired into main router
            is_wired = self._check_if_wired(router_class.name, file_path)
            
            # Build module path
            rel_path = file_path.relative_to(self.cortex_root)
            module_path = str(rel_path.with_suffix('')).replace('/', '.')
            
            return SpecialistRouter(
                name=router_class.name,
                file_path=file_path,
                module_path=module_path,
                purpose=purpose,
                intents_handled=intents_handled,
                is_wired=is_wired
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
    
    def _extract_intents(self, content: str) -> List[str]:
        """Extract intent types handled by router from code."""
        intents = []
        
        # Look for Intent enum usage
        intent_patterns = [
            r"Intent\.(\w+)",
            r"IntentType\.(\w+)",
            r"intent\s*==\s*['\"](\w+)['\"]"
        ]
        
        import re
        for pattern in intent_patterns:
            matches = re.findall(pattern, content)
            intents.extend(matches)
        
        return list(set(intents))[:10]  # Limit to 10 unique intents
    
    def _check_if_wired(self, router_name: str, router_file: Path) -> bool:
        """Check if router is imported and used in main IntentRouter."""
        if not self.main_router.exists():
            return False
        
        main_content = self.main_router.read_text(encoding='utf-8')
        
        # Check for import
        module_name = router_file.stem  # e.g., "tdd_intent_router"
        import_present = (
            f"from .test_generator.{module_name} import" in main_content or
            f"from src.cortex_agents.test_generator.{module_name} import" in main_content or
            f"import {module_name}" in main_content
        )
        
        # Check for usage
        usage_present = (
            f"{router_name}()" in main_content or
            f"self.{router_name.lower()}" in main_content or
            f"self.{module_name}" in main_content
        )
        
        return import_present and usage_present
    
    def _create_wiring_issue(self, router: SpecialistRouter) -> WiringIssue:
        """Create a WiringIssue for an unwired router."""
        # Determine severity and impact
        if "TDD" in router.name:
            severity = "critical"
            impact = "TDD Mastery auto-activation NOT working - users must manually trigger TDD workflow"
        elif "Strategic" in router.name:
            severity = "high"
            impact = "Strategic planning features may not be accessible"
        else:
            severity = "medium"
            impact = f"Specialized routing in {router.name} not available to users"
        
        fix_description = (
            f"Import {router.name} in {self.MAIN_ROUTER_PATH}, "
            f"instantiate in __init__, and delegate appropriate intents to it"
        )
        
        return WiringIssue(
            router=router,
            severity=severity,
            impact=impact,
            fix_description=fix_description
        )
    
    def _apply_wiring_fix(self, router_name: str) -> bool:
        """
        Apply wiring fix for a specific router.
        
        Automatically wires specialist routers into main IntentRouter by:
        1. Adding import statement
        2. Initializing router in __init__
        3. Router is now available for delegation
        
        Args:
            router_name: Name of router class to wire
        
        Returns:
            True if fix applied successfully, False otherwise
        """
        try:
            # Find the router metadata
            routers = self._discover_specialist_routers()
            target_router = None
            for router in routers:
                if router.name == router_name:
                    target_router = router
                    break
            
            if not target_router:
                logger.error(f"Router {router_name} not found in discovered routers")
                return False
            
            # Read main router file
            main_content = self.main_router.read_text(encoding='utf-8')
            lines = main_content.split('\n')
            
            # Step 1: Add import if not present
            import_line = self._generate_import_statement(target_router)
            if import_line not in main_content:
                # Find the last import statement in the file
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')):
                        last_import_idx = i
                
                # Insert after last import
                lines.insert(last_import_idx + 1, import_line)
                logger.info(f"   Added import: {import_line}")
            else:
                logger.info(f"   Import already present")
            
            # Step 2: Add initialization in __init__ if not present
            init_code = self._generate_init_code(target_router)
            if not self._init_code_present(main_content, target_router):
                # Find the __init__ method and Vision orchestrator initialization
                init_insertion_idx = None
                for i, line in enumerate(lines):
                    if 'self.vision_orchestrator = None' in line:
                        init_insertion_idx = i
                        break
                
                if init_insertion_idx:
                    # Insert after vision orchestrator block
                    lines.insert(init_insertion_idx + 1, "")
                    lines.insert(init_insertion_idx + 2, init_code[0])
                    for j, code_line in enumerate(init_code[1:], start=3):
                        lines.insert(init_insertion_idx + j, code_line)
                    logger.info(f"   Added initialization for {router_name}")
                else:
                    logger.warning(f"   Could not find insertion point in __init__")
                    return False
            else:
                logger.info(f"   Initialization already present")
            
            # Write back to file
            self.main_router.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"   ✅ Successfully wired {router_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to wire {router_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _generate_import_statement(self, router: SpecialistRouter) -> str:
        """Generate the import statement for a router."""
        # Build relative import path from main router location
        rel_path = router.file_path.relative_to(self.cortex_root / "src" / "cortex_agents")
        module_parts = list(rel_path.parent.parts) + [rel_path.stem]
        module_path = '.'.join(module_parts)
        
        return f"from .{module_path} import {router.name}"
    
    def _generate_init_code(self, router: SpecialistRouter) -> List[str]:
        """Generate initialization code for a router."""
        router_var = router.name.lower().replace('intentrouter', '_router')
        
        # Determine the appropriate comment based on router type
        if "TDD" in router.name:
            comment = "Initialize TDD Intent Router for TDD Mastery auto-activation (Layer 3 wiring)"
        elif "Strategic" in router.name:
            comment = f"Initialize Strategic Intent Router for enhanced planning (Layer 3 wiring)"
        else:
            comment = f"Initialize {router.name} for specialized routing (Layer 3 wiring)"
        
        return [
            f"        # {comment}",
            f"        try:",
            f"            from .{router.file_path.relative_to(self.cortex_root / 'src' / 'cortex_agents').with_suffix('').as_posix().replace('/', '.')} import {router.name}",
            f"            self.{router_var} = {router.name}()",
            f'            self.logger.info("{router.name} initialized - specialized routing enabled")',
            f"        except Exception as e:",
            f'            self.logger.warning(f"Could not initialize {router.name}: {{e}}")',
            f"            self.{router_var} = None"
        ]
    
    def _init_code_present(self, content: str, router: SpecialistRouter) -> bool:
        """Check if initialization code is already present."""
        router_var = router.name.lower().replace('intentrouter', '_router')
        return f"self.{router_var} =" in content or f"self.{router.name.lower()}" in content
