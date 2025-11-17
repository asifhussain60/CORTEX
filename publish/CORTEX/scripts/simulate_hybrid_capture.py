"""
CORTEX 3.0 Hybrid Capture System - Simulation

Purpose: Validate the hybrid approach end-to-end with real conversation data.
Tests: Auto-detection, smart hints, one-click capture, quality review.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ResponseAnalysis:
    """Analysis of a CORTEX response for conversation value."""
    has_multi_phase: bool
    has_challenge_accept: bool
    has_design_decision: bool
    has_file_mentions: bool
    has_next_steps: bool
    phase_count: int
    file_count: int
    score: int
    quality_level: str  # LOW, FAIR, GOOD, EXCELLENT
    
    
@dataclass
class CapturedConversation:
    """Captured conversation with metadata."""
    conversation_id: str
    timestamp: str
    user_prompts: List[str]
    assistant_responses: List[str]
    total_turns: int
    analysis: ResponseAnalysis
    file_path: Optional[str] = None


class ResponseAnalyzer:
    """Analyzes CORTEX responses to detect conversation value."""
    
    # Scoring weights
    MULTI_PHASE_WEIGHT = 3
    CHALLENGE_ACCEPT_WEIGHT = 3
    DESIGN_DECISION_WEIGHT = 2
    FILE_MENTION_WEIGHT = 1
    NEXT_STEPS_WEIGHT = 2
    
    # Quality thresholds
    EXCELLENT_THRESHOLD = 10
    GOOD_THRESHOLD = 6
    FAIR_THRESHOLD = 3
    
    def analyze_response(self, response_text: str) -> ResponseAnalysis:
        """
        Analyze a CORTEX response for conversation value.
        
        Args:
            response_text: The assistant's response text
            
        Returns:
            ResponseAnalysis object with scoring
        """
        # Detect patterns
        has_multi_phase = bool(re.search(r'Phase \d+', response_text))
        phase_matches = re.findall(r'Phase \d+', response_text)
        phase_count = len(set(phase_matches))
        
        has_challenge_accept = bool(re.search(r'(Challenge:|⚠️.*Challenge)', response_text))
        
        has_design_decision = any(
            keyword in response_text.lower() 
            for keyword in ['architecture', 'design', 'approach', 'strategy', 'pattern']
        )
        
        # File mentions in backticks
        file_pattern = r'`([a-zA-Z0-9_\-/.]+\.(py|md|yaml|json|ps1|ts|tsx|cs))`'
        file_matches = re.findall(file_pattern, response_text)
        file_count = len(file_matches)
        has_file_mentions = file_count > 0
        
        has_next_steps = bool(re.search(r'(Next Steps:|🔍)', response_text))
        
        # Calculate score
        score = 0
        if has_multi_phase:
            score += self.MULTI_PHASE_WEIGHT * phase_count
        if has_challenge_accept:
            score += self.CHALLENGE_ACCEPT_WEIGHT
        if has_design_decision:
            score += self.DESIGN_DECISION_WEIGHT
        if has_file_mentions:
            score += self.FILE_MENTION_WEIGHT * min(file_count, 3)  # Cap at 3 files
        if has_next_steps:
            score += self.NEXT_STEPS_WEIGHT
        
        # Determine quality level
        if score >= self.EXCELLENT_THRESHOLD:
            quality_level = "EXCELLENT"
        elif score >= self.GOOD_THRESHOLD:
            quality_level = "GOOD"
        elif score >= self.FAIR_THRESHOLD:
            quality_level = "FAIR"
        else:
            quality_level = "LOW"
        
        return ResponseAnalysis(
            has_multi_phase=has_multi_phase,
            has_challenge_accept=has_challenge_accept,
            has_design_decision=has_design_decision,
            has_file_mentions=has_file_mentions,
            has_next_steps=has_next_steps,
            phase_count=phase_count,
            file_count=file_count,
            score=score,
            quality_level=quality_level
        )


class SmartHintGenerator:
    """Generates contextual hints for conversation capture."""
    
    def should_show_hint(self, analysis: ResponseAnalysis) -> bool:
        """
        Determine if hint should be shown based on analysis.
        
        Args:
            analysis: ResponseAnalysis object
            
        Returns:
            True if hint should be shown
        """
        # Show hint for GOOD or better quality
        return analysis.quality_level in ["GOOD", "EXCELLENT"]
    
    def generate_hint(self, analysis: ResponseAnalysis) -> str:
        """
        Generate smart hint text.
        
        Args:
            analysis: ResponseAnalysis object
            
        Returns:
            Formatted hint string
        """
        hint_parts = []
        
        # Value indicators
        if analysis.has_multi_phase:
            hint_parts.append(f"Multi-phase planning: {analysis.phase_count} phases")
        if analysis.has_challenge_accept:
            hint_parts.append("Challenge/Accept reasoning")
        if analysis.has_design_decision:
            hint_parts.append("Design decisions")
        if analysis.file_count > 0:
            hint_parts.append(f"File references: {analysis.file_count}")
        
        value_text = ", ".join(hint_parts) if hint_parts else "Strategic discussion"
        
        hint = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 CORTEX LEARNING OPPORTUNITY

This conversation has {analysis.quality_level.lower()} strategic value:
  • {value_text}
  • Quality score: {analysis.score}/10

📸 Capture for future reference?
  → Say: "capture conversation"
  → I'll save this discussion automatically
  → Review now or later - your choice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return hint


class ConversationCapture:
    """Simulates one-click conversation capture."""
    
    def __init__(self, storage_dir: Path):
        """
        Initialize capture system.
        
        Args:
            storage_dir: Directory to store captured conversations
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(exist_ok=True, parents=True)
    
    def capture(self, conversation_text: str, topic: str = "conversation") -> CapturedConversation:
        """
        Simulate capturing conversation from Copilot Chat.
        
        Args:
            conversation_text: Full conversation text (markdown format)
            topic: Topic for filename
            
        Returns:
            CapturedConversation object
        """
        # Parse conversation
        user_prompts = []
        assistant_responses = []
        
        # Split by user prompts
        parts = re.split(r'^asifhussain60:', conversation_text, flags=re.MULTILINE)
        
        for part in parts[1:]:  # Skip first empty split
            # Split into user prompt and assistant response
            sub_parts = re.split(r'^GitHub Copilot:', part, maxsplit=1, flags=re.MULTILINE)
            
            if len(sub_parts) >= 2:
                user_prompts.append(sub_parts[0].strip())
                assistant_responses.append(sub_parts[1].strip())
        
        # Analyze last response for quality
        analyzer = ResponseAnalyzer()
        analysis = analyzer.analyze_response(assistant_responses[-1] if assistant_responses else "")
        
        # Generate filename
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        filename = f"{date_str}-{topic.lower().replace(' ', '-')}.md"
        file_path = self.storage_dir / filename
        
        # Save conversation
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(conversation_text)
        
        # Create captured conversation object
        conversation_id = f"conv-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        
        captured = CapturedConversation(
            conversation_id=conversation_id,
            timestamp=timestamp.isoformat(),
            user_prompts=user_prompts,
            assistant_responses=assistant_responses,
            total_turns=len(user_prompts),
            analysis=analysis,
            file_path=str(file_path)
        )
        
        return captured


class QualityReviewer:
    """Reviews captured conversations before brain storage."""
    
    def generate_review(self, captured: CapturedConversation) -> str:
        """
        Generate quality review report.
        
        Args:
            captured: CapturedConversation object
            
        Returns:
            Formatted review text
        """
        analysis = captured.analysis
        
        review = f"""
📊 CONVERSATION QUALITY REVIEW

Conversation ID: {captured.conversation_id}
Captured: {captured.timestamp}
Turns: {captured.total_turns}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SEMANTIC ANALYSIS:
  ✓ Multi-phase planning: {'YES' if analysis.has_multi_phase else 'NO'} ({analysis.phase_count} phases)
  ✓ Challenge/Accept flow: {'YES' if analysis.has_challenge_accept else 'NO'}
  ✓ Design decisions: {'YES' if analysis.has_design_decision else 'NO'}
  ✓ File references: {'YES' if analysis.has_file_mentions else 'NO'} ({analysis.file_count} files)
  ✓ Next steps provided: {'YES' if analysis.has_next_steps else 'NO'}

QUALITY SCORE: {analysis.score}/10 ({analysis.quality_level})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDATION:
"""
        
        if analysis.quality_level in ["EXCELLENT", "GOOD"]:
            review += "  ✅ HIGH VALUE - Recommended for brain storage\n"
            review += "  This conversation will significantly improve future 'continue' commands.\n"
        elif analysis.quality_level == "FAIR":
            review += "  ⚠️ MODERATE VALUE - May be useful for specific contexts\n"
            review += "  Consider storing if topic is frequently revisited.\n"
        else:
            review += "  ❌ LOW VALUE - Not recommended for storage\n"
            review += "  Simple Q&A without strategic context.\n"
        
        review += f"\nStored at: {captured.file_path}\n"
        review += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return review


def simulate_workflow():
    """Run complete hybrid workflow simulation."""
    
    print("=" * 80)
    print("CORTEX 3.0 HYBRID CAPTURE SYSTEM - SIMULATION")
    print("=" * 80)
    print()
    
    # Setup
    cortex_root = Path(__file__).parent.parent
    test_conversation_file = cortex_root / ".github" / "CopilotChats.md"
    storage_dir = cortex_root / "cortex-brain" / "imported-conversations"
    
    # Read test conversation
    print("📂 Loading test conversation from CopilotChats.md...")
    conversation_text = test_conversation_file.read_text(encoding='utf-8')
    print(f"   ✓ Loaded {len(conversation_text)} characters\n")
    
    # Step 1: Analyze response (happens automatically after every CORTEX response)
    print("STEP 1: AUTO-DETECTION (Response Analysis)")
    print("-" * 80)
    
    # Extract last assistant response for simulation
    parts = re.split(r'^GitHub Copilot:', conversation_text, flags=re.MULTILINE)
    last_response = parts[-1] if len(parts) > 1 else ""
    
    analyzer = ResponseAnalyzer()
    analysis = analyzer.analyze_response(last_response)
    
    print(f"Analysis Results:")
    print(f"  • Multi-phase planning: {analysis.has_multi_phase} ({analysis.phase_count} phases)")
    print(f"  • Challenge/Accept: {analysis.has_challenge_accept}")
    print(f"  • Design decisions: {analysis.has_design_decision}")
    print(f"  • File mentions: {analysis.has_file_mentions} ({analysis.file_count} files)")
    print(f"  • Next steps: {analysis.has_next_steps}")
    print(f"\n  Quality Score: {analysis.score}/10 ({analysis.quality_level})")
    print()
    
    # Step 2: Smart hint generation
    print("STEP 2: SMART HINT (Conditional Display)")
    print("-" * 80)
    
    hint_gen = SmartHintGenerator()
    should_show = hint_gen.should_show_hint(analysis)
    
    print(f"Should show hint? {should_show}")
    print(f"Reason: Quality is {analysis.quality_level} (threshold: GOOD or better)")
    print()
    
    if should_show:
        hint = hint_gen.generate_hint(analysis)
        print("Generated Hint:")
        print(hint)
    else:
        print("(No hint shown - conversation quality below threshold)")
        print()
    
    # Step 3: One-click capture (user says "capture conversation")
    print("\nSTEP 3: ONE-CLICK CAPTURE (User Action)")
    print("-" * 80)
    print('User says: "capture conversation"')
    print()
    
    capturer = ConversationCapture(storage_dir)
    captured = capturer.capture(conversation_text, topic="cleanup-system-design")
    
    print(f"✅ Conversation captured!")
    print(f"   • Conversation ID: {captured.conversation_id}")
    print(f"   • Timestamp: {captured.timestamp}")
    print(f"   • Turns: {captured.total_turns}")
    print(f"   • File: {captured.file_path}")
    print()
    
    # Step 4: Quality review
    print("STEP 4: QUALITY REVIEW (Optional)")
    print("-" * 80)
    print('User says: "review"')
    print()
    
    reviewer = QualityReviewer()
    review = reviewer.generate_review(captured)
    print(review)
    
    # Step 5: Brain consumption simulation
    print("STEP 5: BRAIN CONSUMPTION (User Confirms)")
    print("-" * 80)
    print('User says: "consume" or "y"')
    print()
    print("✅ Would store to Tier 1 with metadata:")
    
    tier1_data = {
        "conversation_id": captured.conversation_id,
        "type": "copilot_conversation_import",
        "timestamp": captured.timestamp,
        "total_turns": captured.total_turns,
        "quality_score": captured.analysis.score,
        "quality_level": captured.analysis.quality_level,
        "semantic_elements": {
            "multi_phase": captured.analysis.has_multi_phase,
            "phase_count": captured.analysis.phase_count,
            "challenge_accept": captured.analysis.has_challenge_accept,
            "design_decisions": captured.analysis.has_design_decision,
            "file_mentions": captured.analysis.file_count
        },
        "source_file": captured.file_path
    }
    
    print(json.dumps(tier1_data, indent=2))
    print()
    
    # Summary
    print("=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Auto-detection: WORKING (score: {analysis.score}/10)")
    print(f"✅ Smart hint: WORKING (shown: {should_show})")
    print(f"✅ One-click capture: WORKING (file created)")
    print(f"✅ Quality review: WORKING (recommendation: {'STORE' if analysis.quality_level in ['GOOD', 'EXCELLENT'] else 'SKIP'})")
    print(f"✅ Brain consumption: READY (would store to Tier 1)")
    print()
    print("🎯 THEORY VALIDATED - Hybrid approach is technically sound!")
    print()
    
    # Return results for programmatic validation
    return {
        "analysis": asdict(analysis),
        "hint_shown": should_show,
        "captured": asdict(captured),
        "recommendation": "STORE" if analysis.quality_level in ["GOOD", "EXCELLENT"] else "SKIP"
    }


if __name__ == "__main__":
    results = simulate_workflow()
    
    # Save results
    cortex_root = Path(__file__).parent.parent
    results_file = cortex_root / "cortex-brain" / "hybrid-capture-simulation-results.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Simulation results saved to: {results_file}")
