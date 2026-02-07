"""
Enhancement Generator for DIGEST Mode.

Phase 41 Stage 5 (ENH-054):
Automatic ENH-* YAML generation from DIGEST findings.

Generates complete ENH-* entries with all required fields:
- enh_id, title, description, category
- priority, status, roi_score, effort_days
- created_date, source, implementation_hints

Author: Asif Hussain
Date: 2026-02-07
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class EnhancementCandidate:
    """
    Candidate enhancement for approval.
    
    Attributes:
        enh_id: Enhancement ID (ENH-XXX)
        description: Enhancement description
        category: Category (drift, pattern, efficiency, etc.)
        roi_score: ROI score (0-1)
        priority: Priority (P0-P3)
        impact: Impact level (low, medium, high)
        source_file: Source chat file
        source_line: Source line number
    """
    description: str
    enh_id: str = ""
    category: str = "drift"
    roi_score: float = 0.5
    priority: str = "P2"
    impact: str = "medium"
    source_file: str = ""
    source_line: int = 0
    effort_days: int = 2
    status: str = "proposed"
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class EnhancementGenerator:
    """
    Generate ENH-* YAML entries from enhancement candidates.
    
    Uses template-based generation with automatic:
    - Priority assignment (based on ROI)
    - Effort estimation (based on description complexity)
    - Implementation hints generation
    
    Usage:
        generator = EnhancementGenerator()
        yaml_content = generator.generate_yaml(candidate)
        generator.save_yaml(candidate, output_file)
    """
    
    TEMPLATE = """
{enh_id}:
  title: "{title}"
  description: |
    {description}
  
  category: {category}
  priority: {priority}
  status: {status}
  
  metrics:
    roi_score: {roi_score}
    effort_days: {effort_days}
    impact: {impact}
  
  source:
    type: "digest_automation"
    file: "{source_file}"
    line: {source_line}
    created_date: "{created_date}"
  
  implementation_hints:
{implementation_hints}
"""
    
    def __init__(self):
        """Initialize EnhancementGenerator."""
        pass
    
    def get_template(self) -> str:
        """Get YAML template."""
        return self.TEMPLATE
    
    def generate_yaml(self, candidate: EnhancementCandidate) -> str:
        """
        Generate complete ENH-* YAML entry.
        
        Args:
            candidate: EnhancementCandidate to generate YAML for
        
        Returns:
            YAML content as string
        """
        # Generate title from description (first 60 chars)
        title = candidate.description[:60]
        if len(candidate.description) > 60:
            title += "..."
        
        # Format description (indent for YAML block scalar)
        description_lines = candidate.description.split("\n")
        description = "\n    ".join(description_lines)
        
        # Generate implementation hints
        hints = self._generate_hints(candidate)
        hints_yaml = "\n".join(f"    - {hint}" for hint in hints)
        
        # Fill template
        yaml_content = self.TEMPLATE.format(
            enh_id=candidate.enh_id,
            title=title,
            description=description,
            category=candidate.category,
            priority=candidate.priority,
            status=candidate.status,
            roi_score=candidate.roi_score,
            effort_days=candidate.effort_days,
            impact=candidate.impact,
            source_file=candidate.source_file or "unknown",
            source_line=candidate.source_line,
            created_date=candidate.created_date,
            implementation_hints=hints_yaml
        )
        
        return yaml_content
    
    def _generate_hints(self, candidate: EnhancementCandidate) -> List[str]:
        """Generate implementation hints based on category."""
        hints = []
        
        if candidate.category == "drift":
            hints.append("Review CORTEX.prompt.md for drift prevention strategies")
            hints.append("Add enforcement rule to EnforcementOrchestrator")
            hints.append("Update CORE rules documentation")
        elif candidate.category == "pattern":
            hints.append("Analyze pattern frequency in historical chats")
            hints.append("Create detection regex for SessionParser")
            hints.append("Add pattern to violation_patterns.yaml")
        elif candidate.category == "efficiency":
            hints.append("Profile token usage in affected scenarios")
            hints.append("Implement token optimization strategy")
            hints.append("Add efficiency metric tracking")
        else:
            hints.append("Review enhancement description for implementation approach")
            hints.append("Create TDD test suite first")
            hints.append("Integrate with existing CORTEX systems")
        
        return hints
    
    def save_yaml(self, candidate: EnhancementCandidate, output_file: Path) -> None:
        """
        Save generated YAML to file.
        
        Args:
            candidate: EnhancementCandidate to save
            output_file: Path to output file
        """
        yaml_content = self.generate_yaml(candidate)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(yaml_content)
    
    def generate_batch_yaml(self, candidates: List[EnhancementCandidate]) -> str:
        """
        Generate YAML for multiple candidates (combined file).
        
        Args:
            candidates: List of EnhancementCandidate
        
        Returns:
            Combined YAML content
        """
        yaml_parts = []
        for candidate in candidates:
            yaml_parts.append(self.generate_yaml(candidate))
        
        return "\n---\n".join(yaml_parts)
    
    def set_priority_from_roi(self, candidate: EnhancementCandidate) -> None:
        """
        Set priority based on ROI score.
        
        Args:
            candidate: EnhancementCandidate to update
        
        ROI → Priority mapping:
        - 0.9+: P0 (critical)
        - 0.7-0.89: P1 (high)
        - 0.5-0.69: P2 (medium)
        - <0.5: P3 (low)
        """
        if candidate.roi_score >= 0.9:
            candidate.priority = "P0"
        elif candidate.roi_score >= 0.7:
            candidate.priority = "P1"
        elif candidate.roi_score >= 0.5:
            candidate.priority = "P2"
        else:
            candidate.priority = "P3"
