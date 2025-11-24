"""
Feedback Agent - Issue #3 Fix (P0)
Purpose: Collect structured user feedback about CORTEX issues and improvements
Created: 2025-11-23
Author: Asif Hussain
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid


class FeedbackAgent:
    """
    Handles feedback command routing and structured report generation.
    Implements Issue #3 Fix - Missing feedback entry point.
    """
    
    def __init__(self, brain_path: str = None):
        """Initialize FeedbackAgent with path to CORTEX brain."""
        if brain_path is None:
            # Default to standard CORTEX brain location
            brain_path = Path(__file__).parent.parent.parent / "cortex-brain"
        
        self.brain_path = Path(brain_path)
        self.reports_path = self.brain_path / "documents" / "reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
    def create_feedback_report(
        self, 
        user_input: str, 
        feedback_type: str = "general",
        severity: str = "medium",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create structured feedback report in documents/reports/
        
        Args:
            user_input: User's feedback description
            feedback_type: Type of feedback (bug, gap, improvement, question)
            severity: Severity level (critical, high, medium, low)
            context: Optional context (files, conversation_id, etc.)
            
        Returns:
            Dictionary with report metadata and file path
        """
        # Generate unique feedback ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feedback_id = f"CORTEX-FEEDBACK-{timestamp}"
        
        # Determine feedback type from user input if not specified
        if feedback_type == "general":
            feedback_type = self._detect_feedback_type(user_input)
        
        # Build structured report
        report = self._build_report_structure(
            feedback_id=feedback_id,
            user_input=user_input,
            feedback_type=feedback_type,
            severity=severity,
            context=context or {}
        )
        
        # Save to file
        filename = f"{feedback_id}.md"
        file_path = self.reports_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Return confirmation
        return {
            "success": True,
            "feedback_id": feedback_id,
            "file_path": str(file_path),
            "feedback_type": feedback_type,
            "severity": severity,
            "message": f"Feedback report created: {filename}"
        }
    
    def _detect_feedback_type(self, user_input: str) -> str:
        """Detect feedback type from user input."""
        user_input_lower = user_input.lower()
        
        # Priority detection order
        if any(keyword in user_input_lower for keyword in ['bug', 'error', 'broken', 'crash', 'fail']):
            return "bug"
        elif any(keyword in user_input_lower for keyword in ['missing', 'lacks', 'no', 'cannot', 'doesn\'t']):
            return "gap"
        elif any(keyword in user_input_lower for keyword in ['improve', 'enhance', 'better', 'should', 'could']):
            return "improvement"
        elif any(keyword in user_input_lower for keyword in ['how', 'what', 'why', 'when', 'question']):
            return "question"
        else:
            return "general"
    
    def _build_report_structure(
        self,
        feedback_id: str,
        user_input: str,
        feedback_type: str,
        severity: str,
        context: Dict[str, Any]
    ) -> str:
        """Build markdown report structure."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Severity emoji mapping
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        # Feedback type title mapping
        type_titles = {
            "bug": "Bug Report",
            "gap": "Feature Gap",
            "improvement": "Improvement Suggestion",
            "question": "Question",
            "general": "General Feedback"
        }
        
        report = f"""# CORTEX Feedback Report: {type_titles.get(feedback_type, 'General Feedback')}

**Report ID:** {feedback_id}  
**Date:** {timestamp}  
**Type:** {feedback_type.upper()}  
**Severity:** {severity_emoji.get(severity, '⚪')} {severity.upper()}  
**Status:** New

---

## 📋 User Feedback

{user_input}

---

## 🔍 Context Information

"""
        
        # Add context if available
        if context:
            if "conversation_id" in context:
                report += f"**Conversation ID:** {context['conversation_id']}  \n"
            if "files" in context:
                report += f"**Related Files:**\n"
                for file in context['files']:
                    report += f"- `{file}`\n"
            if "workflow" in context:
                report += f"**Workflow:** {context['workflow']}  \n"
            if "agent" in context:
                report += f"**Agent:** {context['agent']}  \n"
        else:
            report += "*No additional context provided*\n"
        
        report += f"""
---

## 📊 Classification

- **Category:** {feedback_type}
- **Priority:** {self._determine_priority(severity, feedback_type)}
- **Estimated Impact:** {self._estimate_impact(severity, feedback_type)}
- **Estimated Effort:** TBD (requires analysis)

---

## ✅ Next Actions

- [ ] Review feedback report
- [ ] Assign priority and effort estimate
- [ ] Create implementation plan (if applicable)
- [ ] Update user with resolution timeline
- [ ] Track in GitHub Issues (if P0/P1)

---

## 🎯 Resolution Plan

*To be filled during review*

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available - See CORTEX LICENSE
"""
        
        return report
    
    def _determine_priority(self, severity: str, feedback_type: str) -> str:
        """Determine priority based on severity and type."""
        if severity == "critical":
            return "P0 - URGENT"
        elif severity == "high":
            return "P1 - HIGH" if feedback_type == "bug" else "P2 - MEDIUM"
        elif severity == "medium":
            return "P2 - MEDIUM"
        else:
            return "P3 - LOW"
    
    def _estimate_impact(self, severity: str, feedback_type: str) -> str:
        """Estimate impact based on severity and type."""
        if severity == "critical":
            return "BLOCKS core functionality"
        elif severity == "high" and feedback_type == "bug":
            return "Significantly degrades user experience"
        elif severity == "high":
            return "Notable improvement opportunity"
        elif severity == "medium":
            return "Moderate impact on usability"
        else:
            return "Minor improvement"


def handle_feedback_command(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Entry point for feedback command handling.
    
    Args:
        user_input: User's feedback text
        context: Optional context dictionary
        
    Returns:
        Result dictionary with success status and file path
    """
    agent = FeedbackAgent()
    return agent.create_feedback_report(user_input, context=context)
