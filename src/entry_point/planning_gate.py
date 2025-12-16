"""
Planning Gate - Automatic Request Triage and Planning Invocation
================================================================

GREEN PHASE - Minimal Implementation to Pass RED Tests

Purpose:
- Intercept ALL user requests before routing to execution
- Classify complexity (Tier 1-4)
- Create temporary plans for Tier 3+ work
- Block execution until plan approved (SKULL enforcement)

Compliance:
- SKULL MANDATORY_PLANNING_ENFORCEMENT
- Master plan requirements (cortex-evolution-v3.9)
- TDD GREEN_PHASE_VALIDATION: Minimal code to pass tests

Author: CORTEX TDD System
Date: December 16, 2025
Status: GREEN PHASE - Implementing to pass tests
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PlanningGate:
    """
    Automatic request triage and planning invocation.
    
    This is the PERMANENT FIX for planning system issues.
    Every user request flows through this gate FIRST.
    
    Workflow:
    1. Receive user request
    2. Classify complexity (Tier 1-4)
    3. Tier 1-2: Execute immediately
    4. Tier 3-4: Create temporary plan, await approval
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize planning gate.
        
        Args:
            cortex_root: Path to CORTEX root (defaults to cwd)
        """
        self.cortex_root = Path(cortex_root) if cortex_root else Path.cwd()
        self.temp_plans_dir = self.cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "temp-plans"
        self.temp_plans_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎭 Planning Gate initialized (cortex_root={self.cortex_root})")
    
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        Process user request through planning triage.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            Dictionary with triage results:
            {
                'requires_planning': bool,
                'complexity_tier': int (1-4),
                'temp_plan_id': str (if Tier 3+),
                'plan_location': str (if Tier 3+),
                'proceed_to_execution': bool
            }
        """
        logger.info(f"🎭 Planning Gate: Processing request")
        
        # Step 1: Classify complexity
        complexity_tier = self._classify_complexity(user_request)
        logger.info(f"🎭 Complexity classified: Tier {complexity_tier}")
        
        # Step 2: Route based on tier
        if complexity_tier <= 2:
            # Tier 1-2: Execute directly (no planning needed)
            return {
                'requires_planning': False,
                'complexity_tier': complexity_tier,
                'proceed_to_execution': True
            }
        
        # Tier 3-4: Create temporary plan
        temp_plan_id = self._create_temporary_plan(user_request, complexity_tier)
        plan_location = str(self.temp_plans_dir / temp_plan_id)
        
        # Show visual indicator
        self._show_planning_indicator(complexity_tier, temp_plan_id)
        
        return {
            'requires_planning': True,
            'complexity_tier': complexity_tier,
            'temp_plan_id': temp_plan_id,
            'plan_location': plan_location,
            'proceed_to_execution': False  # Wait for approval
        }
    
    def _classify_complexity(self, request: str) -> int:
        """
        Classify request complexity into Tier 1-4.
        
        GREEN PHASE: Minimal implementation using keyword matching.
        REFACTOR PHASE: Replace with LLM-based classification.
        
        Tiers:
        - Tier 1 (INSTANT): <2s operations (queries, version checks)
        - Tier 2 (LIGHTWEIGHT): <10s operations (validation, single file)
        - Tier 3 (DOCUMENTED): 10-60 min operations (features, analysis)
        - Tier 4 (COMPLEX): >1h operations (architecture changes, migrations)
        
        Args:
            request: User's request string
            
        Returns:
            Tier number (1-4)
        """
        request_lower = request.lower()
        
        # Tier 4 keywords (COMPLEX)
        tier_4_keywords = [
            'architecture overhaul',
            'complete rewrite',
            'migration',
            'multi-phase',
            'nested plan',
            'comprehensive plan'
        ]
        if any(kw in request_lower for kw in tier_4_keywords):
            return 4
        
        # Tier 3 keywords (DOCUMENTED)
        tier_3_keywords = [
            'comprehensive',
            'holistic',
            'analyze',
            'review',
            'architecture',
            'audit',
            'assessment',
            'deep dive',
            'investigation',
            'identify gaps'
        ]
        if any(kw in request_lower for kw in tier_3_keywords):
            return 3
        
        # Tier 2 keywords (LIGHTWEIGHT)
        tier_2_keywords = [
            'validate',
            'check',
            'verify',
            'lint',
            'format'
        ]
        if any(kw in request_lower for kw in tier_2_keywords):
            return 2
        
        # Default: Tier 1 (INSTANT)
        return 1
    
    def _create_temporary_plan(self, request: str, tier: int) -> str:
        """
        Create temporary plan for Tier 3+ work.
        
        Args:
            request: User's request
            tier: Complexity tier
            
        Returns:
            Temporary plan ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize request for folder name
        request_slug = "".join(c if c.isalnum() or c == '-' else '-' for c in request[:30].lower())
        request_slug = request_slug.strip('-')
        
        temp_plan_id = f"TEMP-PLAN-{timestamp}-{request_slug}"
        
        # Create plan folder
        plan_folder = self.temp_plans_dir / temp_plan_id
        plan_folder.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder README
        readme_path = plan_folder / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Temporary Plan: {temp_plan_id}

**Created:** {datetime.now().isoformat()}
**Tier:** {tier}
**User Request:** {request}

**Status:** ⏳ Awaiting approval

## Next Steps

1. Review this temporary plan
2. Provide feedback or refinements
3. Approve to convert to permanent plan
4. Execution begins with checkpoints
""")
        
        logger.info(f"✅ Temporary plan created: {temp_plan_id}")
        return temp_plan_id
    
    def _show_planning_indicator(self, tier: int, plan_id: str):
        """
        Show visual indicator to user.
        
        Args:
            tier: Complexity tier
            plan_id: Temporary plan ID
        """
        tier_names = {
            1: "INSTANT",
            2: "LIGHTWEIGHT",
            3: "DOCUMENTED",
            4: "COMPLEX"
        }
        
        tier_times = {
            1: "<2 seconds",
            2: "<10 seconds",
            3: "10-60 minutes",
            4: ">1 hour"
        }
        
        print(f"""
## 🎭 Planning System Engaged

**Complexity:** Tier {tier} ({tier_names.get(tier, 'UNKNOWN')})
**Estimated Time:** {tier_times.get(tier, 'Unknown')}
**Temporary Plan:** {plan_id}

**Status:** Creating temporary plan...

### Planning Phases:
⏳ Phase 1: Definition of Ready validation
⏳ Phase 2: Complexity analysis
⏳ Phase 3: Phase decomposition
⏳ Phase 4: Risk assessment
⏳ Phase 5: Approval gate

You'll see the plan shortly for review and approval.
""")
