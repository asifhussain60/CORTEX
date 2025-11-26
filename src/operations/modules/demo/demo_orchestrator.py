"""
CORTEX Demo Orchestrator

Handles discovery and demonstration of CORTEX capabilities.
Routes discovery commands to the appropriate demonstration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path
from datetime import datetime


class DemoOrchestrator:
    """
    Orchestrates CORTEX capability discovery and demonstrations.
    
    Handles:
    - Introduction and discovery responses
    - Live feature demonstrations
    - Interactive guided tours
    - Learning path recommendations
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize Demo Orchestrator.
        
        Args:
            brain_path: Path to CORTEX brain directory
        """
        self.brain_path = brain_path or Path("cortex-brain")
        self.logger = logging.getLogger(__name__)
        
    def handle_discovery(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle discovery request with template-based response.
        
        Args:
            user_request: User's discovery request
            context: Additional context for rendering
            
        Returns:
            Response dict with template_id and context
        """
        request_lower = user_request.lower()
        
        # Check for specific demo requests FIRST (more specific than general discovery)
        demo_type = self._detect_demo_type(request_lower)
        if demo_type:
            return self._handle_specific_demo(demo_type, context)
        
        # Main discovery trigger - route to introduction_discovery template
        if any(trigger in request_lower for trigger in [
            'discover', 'explore', 'demo', 'tour', 'capabilities', 
            'what can you do', 'show me what', 'features'
        ]):
            return {
                'template_id': 'introduction_discovery',
                'context': {
                    'user_request': user_request,
                    'timestamp': datetime.now().isoformat(),
                    **(context or {})
                }
            }
        
        # Default to general discovery
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'user_request': user_request,
                'timestamp': datetime.now().isoformat(),
                **(context or {})
            }
        }
    
    def _detect_demo_type(self, request_lower: str) -> Optional[str]:
        """
        Detect specific demo type from request.
        
        Args:
            request_lower: Lowercase user request
            
        Returns:
            Demo type identifier or None
        """
        demo_mappings = {
            'planning': ['demo planning', 'plan demo', 'show planning'],
            'tdd': ['demo tdd', 'tdd demo', 'show tdd', 'test demo'],
            'view_discovery': ['demo view', 'view discovery demo', 'show view discovery'],
            'feedback': ['demo feedback', 'feedback demo', 'show feedback'],
            'upgrade': ['demo upgrade', 'upgrade demo', 'show upgrade'],
            'brain': ['demo brain', 'brain demo', 'show brain', 'brain architecture']
        }
        
        for demo_type, triggers in demo_mappings.items():
            if any(trigger in request_lower for trigger in triggers):
                return demo_type
        
        return None
    
    def _handle_specific_demo(self, demo_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle specific demonstration request.
        
        Args:
            demo_type: Type of demonstration
            context: Additional context
            
        Returns:
            Response dict with demonstration content
        """
        demos = {
            'planning': self._demo_planning,
            'tdd': self._demo_tdd,
            'view_discovery': self._demo_view_discovery,
            'feedback': self._demo_feedback,
            'upgrade': self._demo_upgrade,
            'brain': self._demo_brain_architecture
        }
        
        demo_func = demos.get(demo_type)
        if demo_func:
            return demo_func(context)
        
        # Fallback to general discovery
        return {
            'template_id': 'introduction_discovery',
            'context': context or {}
        }
    
    def _demo_planning(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate Planning System 2.0"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'planning',
                'demo_content': """
## 🚀 Planning System 2.0 Demo

**Key Features:**
- **Vision API** - Extract requirements from screenshots (UI mockups, errors, ADO items)
- **DoR/DoD Enforcement** - Zero-ambiguity requirement validation with OWASP security review
- **File-Based Workflow** - Git-trackable, resumable planning files
- **Unified Core** - ADO/Feature/Vision planning share 80% of code

**Quick Commands:**
- `plan [feature name]` - Start feature planning (attach screenshot for Vision API)
- `plan ado` - ADO work item planning with form template
- `approve plan` - Finalize and hook into pipeline
- `resume plan [name]` - Continue existing plan with context restoration

**Try it now:**
Say `plan user authentication system` to see planning in action!

**Documentation:** [Planning Guide](https://asifhussain60.github.io/CORTEX/planning/) (Coming Soon)
""",
                **(context or {})
            }
        }
    
    def _demo_tdd(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate TDD Mastery workflow"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'tdd',
                'demo_content': """
## 🔴🟢🔵 TDD Mastery Demo

**RED→GREEN→REFACTOR Automation:**
1. **RED Phase** - Write failing test first, Brain Protector validates failure
2. **GREEN Phase** - Minimal implementation to pass tests
3. **REFACTOR Phase** - Clean code with performance-based recommendations

**Features:**
- **Auto-debug** - Debug session starts automatically on test failures
- **Performance refactoring** - Uses timing data to identify bottlenecks
- **Test isolation** - App tests in user repo, CORTEX tests in `tests/`
- **Brain memory** - Remembers patterns and improves over time

**Quick Commands:**
- `start tdd` - Begin TDD workflow
- `run tests` - Execute and analyze tests
- `suggest refactorings` - Get performance recommendations

**Try it now:**
Say `start tdd` to begin test-driven development!

**Documentation:** [TDD Mastery](https://asifhussain60.github.io/CORTEX/tdd/) (Coming Soon)
""",
                **(context or {})
            }
        }
    
    def _demo_view_discovery(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate View Discovery feature"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'view_discovery',
                'demo_content': """
## 🔍 View Discovery Demo

**Auto-extract UI elements for testing:**
- **Time savings** - 60+ min → <5 min (92% reduction)
- **Test accuracy** - 95%+ with real element IDs
- **Integrated** - Works seamlessly with TDD workflow

**How it works:**
1. Scans Razor/Blazor/React files for element IDs
2. Extracts IDs, classes, data attributes
3. Generates accurate test selectors
4. Prevents brittle tests from changing IDs

**Quick Command:**
`discover views in [file]` - Extract elements before test generation

**Try it now:**
Say `discover views in src/Pages/Index.razor` to see extraction!

**Documentation:** [View Discovery](https://asifhussain60.github.io/CORTEX/view-discovery/) (Coming Soon)
""",
                **(context or {})
            }
        }
    
    def _demo_feedback(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate Feedback System"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'feedback',
                'demo_content': """
## 📢 Feedback System Demo

**Structured issue reporting:**
- **Privacy protection** - Auto-redacts sensitive data
- **Auto-context** - Includes system info, logs, environment
- **GitHub Gist upload** - Share feedback with team
- **Categories** - Bug/Feature/Improvement tracking

**What gets captured:**
- CORTEX version and configuration
- Recent conversation context (anonymized)
- System environment (OS, Python version)
- Error logs (if applicable)

**Quick Command:**
`feedback` or `report issue` - Start structured reporting

**Try it now:**
Say `feedback` to see the reporting interface!

**Documentation:** [Feedback System](https://asifhussain60.github.io/CORTEX/feedback/) (Coming Soon)
""",
                **(context or {})
            }
        }
    
    def _demo_upgrade(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate Universal Upgrade System"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'upgrade',
                'demo_content': """
## 🔄 Universal Upgrade System Demo

**One command works everywhere:**
- **Auto-detection** - Detects standalone/embedded installations
- **Brain preservation** - Automatic backup, zero data loss
- **Path validation** - Ensures safe upgrade
- **Post-verification** - Validates successful upgrade

**Safety guarantees:**
✅ Brain data preserved (conversations, patterns, context)
✅ Auto-backup with rollback capability
✅ Config merging (preserves customizations)
✅ Schema migrations for DB upgrades

**Quick Commands:**
- `upgrade cortex` - Universal upgrade for all installations
- `cortex version` - Show current version

**Try it now:**
Say `cortex version` to see your current installation!

**Documentation:** [Upgrade Guide](https://asifhussain60.github.io/CORTEX/upgrade/) (Coming Soon)
""",
                **(context or {})
            }
        }
    
    def _demo_brain_architecture(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Demonstrate Brain Architecture"""
        return {
            'template_id': 'introduction_discovery',
            'context': {
                'demo_type': 'brain',
                'demo_content': """
## 🧠 Brain Architecture Demo

**4-Tier Memory System:**
- **Tier 0** - Immutable governance (SKULL rules in brain-protection-rules.yaml)
- **Tier 1** - Working memory (SQLite, 70-conv FIFO, <100ms queries)
- **Tier 2** - Knowledge graph (SQLite + FTS5, pattern learning)
- **Tier 3** - Dev context (project metrics, hotspots, patterns)

**SKULL Protection Rules:**
- **TDD_ENFORCEMENT** - RED → GREEN → REFACTOR mandatory
- **GIT_ISOLATION_ENFORCEMENT** - CORTEX code never committed to user repos
- **TEST_LOCATION_SEPARATION** - App tests in user repo, CORTEX tests in `tests/`
- **BRAIN_ARCHITECTURE_INTEGRITY** - Protect 4-tier structure

**Token Reduction:**
- **97.2% reduction** (74,047 → 2,078 avg tokens)
- **93.4% cost reduction** with intelligent caching
- **Pattern learning** improves accuracy over time

**Quick Commands:**
- `show context` - See what CORTEX remembers
- `show brain status` - View brain health metrics
- `optimize` - Clean and vacuum databases

**Try it now:**
Say `show context` to see your conversation memory!

**Documentation:** [Brain Architecture](https://asifhussain60.github.io/CORTEX/architecture/) (Coming Soon)
""",
                **(context or {})
            }
        }


# Convenience function for quick access
def handle_discovery_request(user_request: str, brain_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Quick handler for discovery requests.
    
    Args:
        user_request: User's discovery request
        brain_path: Path to CORTEX brain
        
    Returns:
        Response dict with template_id and context
    """
    orchestrator = DemoOrchestrator(brain_path)
    return orchestrator.handle_discovery(user_request)
