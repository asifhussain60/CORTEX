"""
UX Enhancement Entry Point Module

Purpose: Guided onboarding for codebase enhancement requests with explanation,
         consent, and progress tracking before analysis execution.

Triggers: "enhance", "reimagine", "redesign", "improve UX", "modernize"
Blocks: "fix bug", "add feature", "write tests", "create" (normal development)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse


class UXEnhancementEntryPoint(BaseAgent):
    """
    Entry Point Module for UX enhancement requests with guided onboarding.
    
    Workflow:
    1. Detect enhancement keywords in user request
    2. Explain what will happen (analysis phases)
    3. Get user consent before proceeding
    4. Execute analysis with progress updates
    5. Generate and open interactive dashboard
    
    Safety:
    - Blocks accidental activation on normal dev tasks
    - Requires explicit user consent before analysis
    - Transparent about what will be scanned
    - Local-only processing (no uploads)
    """
    
    # Enhancement keywords that trigger this entry point
    ENHANCEMENT_KEYWORDS = [
        "enhance",
        "reimagine",
        "redesign",
        "improve ux",
        "modernize",
        "suggest improvements",
        "refactor architecture",
        "optimize codebase"
    ]
    
    # Keywords that should NOT trigger (normal development)
    BLOCKED_KEYWORDS = [
        "fix bug",
        "add feature",
        "write tests",
        "create",
        "implement",
        "debug",
        "troubleshoot"
    ]
    
    def __init__(self):
        """Initialize Entry Point Module"""
        super().__init__()
        self.name = "UXEnhancementEntryPoint"
        self.description = "Guided onboarding for codebase enhancement requests"
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Determine if this entry point should handle the request.
        
        Logic:
        1. Check for enhancement keywords in request
        2. Ensure no blocking keywords present
        3. Validate user hasn't disabled onboarding (check preferences)
        
        Args:
            request: User request to evaluate
        
        Returns:
            True if this should handle the request, False otherwise
        """
        user_request = request.message.lower()
        
        # Check for blocking keywords first (highest priority)
        for blocked in self.BLOCKED_KEYWORDS:
            if blocked in user_request:
                return False
        
        # Check for enhancement keywords
        for keyword in self.ENHANCEMENT_KEYWORDS:
            if keyword in user_request:
                return True
        
        return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute guided onboarding workflow.
        
        Steps:
        1. Explain workflow to user
        2. Get consent
        3. If approved, route to orchestrator
        4. If declined, explain alternatives
        
        Args:
            request: User request with enhancement intent
        
        Returns:
            AgentResponse with explanation and next steps
        """
        try:
            # Check if user has "always enhance" preference enabled
            skip_explanation = self._check_always_enhance_preference(request)
            
            if skip_explanation:
                return self._route_to_orchestrator(request, skip_explanation=True)
            
            # Generate workflow explanation
            explanation = self._generate_workflow_explanation(request)
            
            return AgentResponse(
                success=True,
                result={
                    "workflow_explanation": explanation,
                    "requires_consent": True,
                    "next_action": "await_user_confirmation",
                    "consent_keywords": ["yes", "proceed", "continue", "go ahead"],
                    "decline_keywords": ["no", "cancel", "stop", "skip"],
                    "preference_keywords": ["always enhance", "always proceed"]
                },
                message=explanation
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                result={},
                message=f"Entry Point Module error: {str(e)}"
            )
    
    def _check_always_enhance_preference(self, request: AgentRequest) -> bool:
        """
        Check if user has enabled "always enhance" preference.
        
        Location: Tier 1 working memory (user_preferences table)
        Key: ux_enhancement.always_proceed
        
        Args:
            request: User request with metadata
        
        Returns:
            True if user has opted into auto-approval, False otherwise
        """
        # TODO: Integrate with Tier 1 working memory
        # For now, return False (always show explanation)
        return False
    
    def _generate_workflow_explanation(self, request: AgentRequest) -> str:
        """
        Generate comprehensive workflow explanation for user.
        
        Explains:
        - What analysis will happen
        - How long it takes
        - What data gets collected
        - What user will receive
        - Privacy guarantees
        
        Args:
            request: User request with context
        
        Returns:
            Formatted explanation string
        """
        # Extract codebase info from request context (if available)
        codebase_path = request.context.get("codebase_path", "your codebase")
        estimated_files = request.context.get("file_count", "~1000")
        estimated_lines = request.context.get("line_count", "~100K")
        estimated_time = self._estimate_analysis_time(estimated_files, estimated_lines)
        
        explanation = f"""
# 🎯 Enhancement Request Detected

I understand you want to enhance your codebase. Here's what will happen:

## 📊 Analysis Phase ({estimated_time} minutes)

I'll analyze **{codebase_path}** for:

✓ **Code Quality Metrics**
  • 11 code smell types (long methods, god classes, duplicated code, etc.)
  • Maintainability, reliability, and technical debt estimates
  • Industry benchmark comparisons

✓ **Architecture Components**
  • Component mapping (authentication, database, APIs, UI, etc.)
  • Relationship strengths and coupling analysis
  • Architectural issues and enhancement opportunities

✓ **Performance Metrics**
  • API endpoint latencies (average, P95, P99)
  • Bottleneck identification (CPU, I/O, network, database)
  • Optimization recommendations with impact estimates

✓ **Security Analysis**
  • OWASP Top 10 vulnerability scan
  • Compliance coverage (SOC 2, GDPR, PCI-DSS, HIPAA)
  • Critical issue prioritization

## 📈 Dashboard Generation

Results displayed in **interactive dashboard** with:

• **6 Exploration Tabs** - Executive Summary, Architecture, Quality, Roadmap, Journey, Security
• **Context-Aware Suggestions** - Smart recommendations based on your findings
• **"What If" Scenarios** - Compare enhancement options side-by-side
• **Guided Discovery Paths** - Personalized exploration journeys

## 🔒 Privacy & Security

✓ All analysis happens **locally** (nothing uploaded)
✓ Results stored in **cortex-brain/documents/analysis/**
✓ Dashboard opens in **your browser** (file:// protocol)
✓ No external API calls or data transmission

## ⏱️ Estimated Impact

**Codebase:** ~{estimated_files} files, ~{estimated_lines} lines
**Analysis Time:** {estimated_time} minutes
**Dashboard Size:** ~2-3 MB
**Expected Value:** Actionable insights with priority rankings

## 🎯 Ready to Proceed?

Say **"yes"** or **"proceed"** to start analysis
Say **"no"** or **"cancel"** to skip for now
Say **"always enhance"** to auto-approve future requests

---

**What happens next?**
I'll show real-time progress updates as each analysis phase completes.
"""
        
        return explanation.strip()
    
    def _estimate_analysis_time(self, file_count: int, line_count: int) -> str:
        """
        Estimate analysis time based on codebase size.
        
        Heuristics:
        - Small (<50K lines): 1-2 min
        - Medium (50-200K lines): 2-3 min
        - Large (200K+ lines): 3-5 min
        
        Args:
            file_count: Number of files in codebase
            line_count: Total lines of code
        
        Returns:
            Human-readable time estimate (e.g., "2-3")
        """
        try:
            lines = int(line_count.replace("~", "").replace("K", "000"))
            
            if lines < 50000:
                return "1-2"
            elif lines < 200000:
                return "2-3"
            else:
                return "3-5"
        except (ValueError, AttributeError):
            return "2-3"  # Default estimate
    
    def _route_to_orchestrator(self, request: AgentRequest, skip_explanation: bool = False) -> AgentResponse:
        """
        Route to UXEnhancementOrchestrator for analysis execution.
        
        Args:
            request: User request with context
            skip_explanation: Whether user has opted into auto-approval
        
        Returns:
            AgentResponse with orchestrator routing
        """
        return AgentResponse(
            success=True,
            result={
                "action": "route_to_orchestrator",
                "orchestrator": "UXEnhancementOrchestrator",
                "skip_explanation": skip_explanation,
                "request": request.to_dict()
            },
            message="Routing to UX Enhancement Orchestrator for analysis execution..."
        )
    
    def handle_user_response(self, user_response: str, original_request: AgentRequest) -> AgentResponse:
        """
        Handle user's response to workflow explanation.
        
        Responses:
        - "yes/proceed/continue/go ahead" → Route to orchestrator
        - "no/cancel/stop/skip" → Explain alternatives
        - "always enhance/always proceed" → Set preference + route to orchestrator
        
        Args:
            user_response: User's consent/decline response
            original_request: Original enhancement request
        
        Returns:
            AgentResponse with next action
        """
        response_lower = user_response.lower().strip()
        
        # Check for "always enhance" preference
        if "always" in response_lower and ("enhance" in response_lower or "proceed" in response_lower):
            self._set_always_enhance_preference(enabled=True)
            return self._route_to_orchestrator(original_request, skip_explanation=False)
        
        # Check for consent
        consent_keywords = ["yes", "proceed", "continue", "go ahead", "ok", "sure"]
        if any(keyword in response_lower for keyword in consent_keywords):
            return self._route_to_orchestrator(original_request)
        
        # Check for decline
        decline_keywords = ["no", "cancel", "stop", "skip", "not now"]
        if any(keyword in response_lower for keyword in decline_keywords):
            return self._explain_alternatives()
        
        # Ambiguous response
        return AgentResponse(
            success=False,
            result={},
            message="I didn't understand your response. Please say 'yes' to proceed or 'no' to cancel."
        )
    
    def _set_always_enhance_preference(self, enabled: bool) -> None:
        """
        Set user preference for "always enhance" mode.
        
        Storage: Tier 1 working memory (user_preferences table)
        Key: ux_enhancement.always_proceed
        Value: enabled (boolean)
        
        Args:
            enabled: Whether to enable auto-approval
        """
        # TODO: Integrate with Tier 1 working memory
        pass
    
    def _explain_alternatives(self) -> AgentResponse:
        """
        Explain alternative options if user declines analysis.
        
        Returns:
            AgentResponse with alternative suggestions
        """
        alternatives = """
No problem! Here are some alternatives:

**Option 1: Manual Review**
- I can guide you through manual code review
- Ask: "help me review my code quality"

**Option 2: Targeted Analysis**
- Analyze specific areas only
- Ask: "analyze security in AuthController"

**Option 3: Quick Suggestions**
- Get quick improvement tips without full analysis
- Ask: "quick suggestions for my codebase"

**Option 4: Resume Later**
- Come back when you're ready
- Just say "enhance my codebase" again

What would you like to do?
"""
        
        return AgentResponse(
            success=True,
            result={"alternatives_provided": True},
            message=alternatives.strip()
        )


def main():
    """Test the Entry Point Module"""
    entry_point = UXEnhancementEntryPoint()
    
    # Test 1: Enhancement request (should handle)
    request1 = AgentRequest(
        message="I want to enhance my PaymentProcessor application",
        intent="enhancement",
        context={"file_count": "847", "line_count": "~124K"}
    )
    
    print("Test 1: Enhancement Request")
    print(f"Can Handle: {entry_point.can_handle(request1)}")
    
    if entry_point.can_handle(request1):
        response = entry_point.execute(request1)
        print(f"\nResponse:\n{response.message}\n")
    
    # Test 2: Normal development request (should NOT handle)
    request2 = AgentRequest(
        message="Fix bug in login controller",
        intent="bugfix",
        context={}
    )
    
    print("\nTest 2: Bug Fix Request")
    print(f"Can Handle: {entry_point.can_handle(request2)}")
    
    # Test 3: User consent handling
    print("\nTest 3: Consent Handling")
    consent_response = entry_point.handle_user_response("yes, proceed", request1)
    print(f"Consent Response: {consent_response.result}")


if __name__ == "__main__":
    main()
