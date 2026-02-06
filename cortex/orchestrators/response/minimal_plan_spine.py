"""
Plan Spine Progress Enhancement (AC-PLAN-SPINE-UX-001)

Refines ASCII plan spine display to show only:
1. Currently Active Phase
2. Next Queued Phase  
3. Upon Completion: Shifts to show Previous → Current → Next

Design Principle: Minimal, rolling display (not cumulative history)

Authority: User feedback (proceed → echo issue), chat02.txt (intelligent progress)
Author: CORTEX Framework
Date: 2026-02-06
Version: 1.1.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class PhaseStatus(str, Enum):
    """Phase execution status"""
    COMPLETED = "completed"
    ACTIVE = "active"
    QUEUED = "queued"


@dataclass
class Phase:
    """Represents a single phase in the plan"""
    
    name: str
    status: PhaseStatus
    index: int  # Position in overall plan
    
    def to_glyph(self) -> str:
        """Convert status to glyph"""
        glyph_map = {
            PhaseStatus.COMPLETED: "[✓]",
            PhaseStatus.ACTIVE: "[→]",
            PhaseStatus.QUEUED: "[ ]",
        }
        return glyph_map.get(self.status, "[ ]")


class MinimalPlanSpine:
    """
    Minimal rolling plan spine - shows only active + next (+ previous on completion)
    
    Design:
    - Active execution: Show current + next only
    - Upon completion: Rotate view to show previous → current → next
    - Never shows full history (keeps it concise)
    """
    
    def __init__(self, all_phases: List[str]):
        """
        Initialize with full phase list
        
        Args:
            all_phases: Complete list of phase names in order
        """
        self.all_phases = all_phases
        self.phases: dict[str, Phase] = {}
        
        # Initialize all phases as queued
        for i, name in enumerate(all_phases):
            self.phases[name] = Phase(
                name=name,
                status=PhaseStatus.QUEUED,
                index=i
            )
    
    def activate_phase(self, phase_name: str) -> None:
        """Mark phase as active"""
        if phase_name not in self.phases:
            raise ValueError(f"Unknown phase: {phase_name}")
        self.phases[phase_name].status = PhaseStatus.ACTIVE
    
    def complete_phase(self, phase_name: str) -> None:
        """Mark phase as completed"""
        if phase_name not in self.phases:
            raise ValueError(f"Unknown phase: {phase_name}")
        self.phases[phase_name].status = PhaseStatus.COMPLETED
    
    def get_display_phases(self) -> List[Phase]:
        """
        Get phases to display (rolling window: active + next, with previous on completion)
        
        Returns:
            List of phases to show (2-3 phases max)
        """
        # Find active phase
        active_idx = None
        for i, phase_name in enumerate(self.all_phases):
            if self.phases[phase_name].status == PhaseStatus.ACTIVE:
                active_idx = i
                break
        
        if active_idx is None:
            # No active phase - show first queued
            active_idx = 0
        
        display = []
        
        # Check if we should show previous (has completed phases before active)
        has_previous = False
        if active_idx > 0:
            prev_phase = self.phases[self.all_phases[active_idx - 1]]
            if prev_phase.status == PhaseStatus.COMPLETED:
                has_previous = True
                display.append(prev_phase)
        
        # Always show active phase
        active_phase = self.phases[self.all_phases[active_idx]]
        display.append(active_phase)
        
        # Always show next phase
        if active_idx + 1 < len(self.all_phases):
            next_phase = self.phases[self.all_phases[active_idx + 1]]
            display.append(next_phase)
        
        return display
    
    def to_minimal_ascii(self) -> str:
        """
        Render to minimal ASCII (2-3 lines only)
        
        Examples:
        - During execution:
          [→] Phase 2 KSESSIONS (active)
          [ ] Phase 3 MCP gateway
          
        - Upon completion:
          [✓] Phase 1 Schema (completed)
          [→] Phase 2 KSESSIONS (active)
          [ ] Phase 3 MCP gateway
        """
        display_phases = self.get_display_phases()
        lines = []
        
        for i, phase in enumerate(display_phases):
            glyph = phase.to_glyph()
            
            # Add status label for clarity
            status_label = ""
            if phase.status == PhaseStatus.COMPLETED:
                status_label = " (completed)"
            elif phase.status == PhaseStatus.ACTIVE:
                status_label = " (active)"
            
            lines.append(f"{glyph} {phase.name}{status_label}")
        
        return "\n".join(lines)
    
    def to_inline_status(self) -> str:
        """
        Render to single-line inline status (for chat embedding)
        
        Examples:
        - During: [→] Phase 2 KSESSIONS | [ ] Phase 3 next
        - Completed: [✓] Phase 1 | [→] Phase 2 KSESSIONS | [ ] Phase 3
        """
        display_phases = self.get_display_phases()
        parts = []
        
        for phase in display_phases:
            glyph = phase.to_glyph()
            parts.append(f"{glyph} {phase.name}")
        
        return " | ".join(parts)


# Example usage
if __name__ == "__main__":
    # Create plan with all phases
    all_phases = [
        "Phase 1 Profile schema & store",
        "Phase 2 KSESSIONS onboarding",
        "Phase 3 MCP gateway",
        "Phase 4 Loose coupling architecture",
    ]
    
    spine = MinimalPlanSpine(all_phases)
    
    print("=== INITIAL STATE ===")
    print(spine.to_minimal_ascii())
    print("\nInline:", spine.to_inline_status())
    
    print("\n=== ACTIVATE PHASE 2 ===")
    spine.activate_phase(all_phases[0])
    spine.complete_phase(all_phases[0])
    spine.activate_phase(all_phases[1])
    print(spine.to_minimal_ascii())
    print("\nInline:", spine.to_inline_status())
    
    print("\n=== COMPLETE PHASE 2 ===")
    spine.complete_phase(all_phases[1])
    spine.activate_phase(all_phases[2])
    print(spine.to_minimal_ascii())
    print("\nInline:", spine.to_inline_status())
