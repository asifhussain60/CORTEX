"""
CORTEX 4.0 Migration Progress Tracker
Updates CORTEX4-STATUS.md status visualization after phase completion.

Features:
- Progress bar visualization updates
- Milestone tracking
- Metrics updating
- AUTO-DOCUMENTATION: Triggers DocumentationOrchestrator on completions

Author: Asif Hussain
Version: 3.0 (Token-optimized structure - CORTEX4-STATUS.md)
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import logging


class ProgressTracker:
    """Update CORTEX4-STATUS.md progress visualization."""
    
    MASTER_PLAN_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "CORTEX4-STATUS.md"
    
    PHASE_NAMES = {
        "0": "Pre-Migration Cleanup",
        "1": "Foundation",
        "1.5": "Documentation & Visualization",
        "2": "Brain Enhancement + RAG",
        "3": "Orchestrator Consolidation",
        "4": "Operations Simplification",
        "5": "Testing & Validation",
        "6": "Documentation Finalization"
    }
    
    @staticmethod
    def _create_progress_bar(percentage: int, width: int = 12) -> str:
        """Create visual progress bar: [████░░░░] percentage%"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage:3d}%"
    
    @staticmethod
    def _get_status_icon(percentage: int) -> str:
        """Get status icon based on completion."""
        if percentage == 100:
            return "✅ COMPLETE"
        elif percentage > 0:
            return "⏳ ACTIVE"
        else:
            return "☐ PENDING"
    
    @classmethod
    def update_progress(
        cls,
        phase: str,
        week: Optional[str] = None,
        completion_percentage: int = 0,
        week_completion: Optional[int] = None,
        milestone_completed: Optional[str] = None,
        metrics: Optional[Dict[str, any]] = None,
        auto_document: bool = True,
        orchestrator_name: Optional[str] = None
    ) -> bool:
        """
        Update CORTEX4-STATUS.md progress tracker.
        
        Args:
            phase: Phase number (0, 1, 1.5, 2, 3, 4, 5, 6)
            week: Week number within phase (optional)
            completion_percentage: Phase completion % (0-100)
            week_completion: Week completion % if updating specific week
            milestone_completed: Milestone name if achieved
            metrics: Dict with orchestrators_migrated, test_coverage, docs_generated, lines_reduced
            auto_document: If True, triggers DocumentationOrchestrator on completion (default: True)
            orchestrator_name: Name of orchestrator to document (e.g., "execution", "documentation", "tdd")
        
        Returns:
            True if update successful
        """
        if not cls.MASTER_PLAN_PATH.exists():
            print(f"❌ CORTEX4-STATUS.md not found at {cls.MASTER_PLAN_PATH}")
            return False
        
        content = cls.MASTER_PLAN_PATH.read_text(encoding="utf-8")
        
        # Update timestamp and current phase
        timestamp = datetime.now().strftime("%B %d, %Y")
        overall_completion = cls._calculate_overall_completion(content, phase, completion_percentage)
        
        content = re.sub(
            r"\*\*Last Updated:\*\* .+? \| \*\*Current Phase:\*\* .+? \| \*\*Week:\*\* .+? \| \*\*Overall:\*\* .+?%",
            f"**Last Updated:** {timestamp} | **Current Phase:** Phase {phase} ({cls.PHASE_NAMES[phase]}) | **Week:** {week or 'N/A'} | **Overall:** {overall_completion}% Complete",
            content
        )
        
        # Update phase progress bar
        phase_pattern = rf"(│ PHASE {re.escape(phase)}: {re.escape(cls.PHASE_NAMES[phase])}\s+)\[.+?\]\s+\d+%"
        phase_bar = cls._create_progress_bar(completion_percentage)
        content = re.sub(phase_pattern, rf"\1{phase_bar}", content)
        
        # Update phase status icon if 100%
        if completion_percentage == 100:
            status_pattern = rf"(│ PHASE {re.escape(phase)}:.+?)(?:⏳ ACTIVE|☐ PENDING)"
            content = re.sub(status_pattern, r"\1✅ COMPLETE", content)
        
        # Update week progress if specified
        if week and week_completion is not None:
            week_pattern = rf"(│ Week {re.escape(week)}:.+?)\[.+?\]\s+\d+%\s+(?:⏳ ACTIVE|☐ PENDING|✅ COMPLETE)"
            week_bar = cls._create_progress_bar(week_completion, width=5)
            week_status = cls._get_status_icon(week_completion)
            content = re.sub(week_pattern, rf"\1{week_bar}  {week_status}", content)
        
        # Update milestone if completed
        if milestone_completed:
            milestone_pattern = rf"(├─ ☐ {re.escape(milestone_completed)})"
            content = re.sub(milestone_pattern, rf"├─ ✅ {milestone_completed}", content)
        
        # Update metrics if provided
        if metrics:
            if "orchestrators_migrated" in metrics:
                content = re.sub(
                    r"├─ Orchestrators Migrated: \d+/\d+ \(\d+%\)",
                    f"├─ Orchestrators Migrated: {metrics['orchestrators_migrated']}/13 ({int(metrics['orchestrators_migrated']/13*100)}%)",
                    content
                )
            if "test_coverage" in metrics:
                content = re.sub(
                    r"├─ Test Coverage: .+",
                    f"├─ Test Coverage: {metrics['test_coverage']}",
                    content
                )
            if "docs_generated" in metrics:
                content = re.sub(
                    r"├─ Documentation: \d+/\d+\+ docs generated",
                    f"├─ Documentation: {metrics['docs_generated']}/200+ docs generated",
                    content
                )
            if "lines_reduced" in metrics:
                content = re.sub(
                    r"└─ Lines Reduced: .+",
                    f"└─ Lines Reduced: {metrics['lines_reduced']} (Target: -40% bloat)",
                    content
                )
        
        # Write updated content
        cls.MASTER_PLAN_PATH.write_text(content, encoding="utf-8")
        print(f"✅ Updated CORTEX4-STATUS.md progress: Phase {phase} = {completion_percentage}%")
        
        # AUTO-DOCUMENTATION: Trigger if completion detected
        if auto_document and orchestrator_name:
            print(f"🎭 Auto-documentation triggered for: {orchestrator_name}")
            docs_generated = cls._trigger_auto_documentation(orchestrator_name)
            if docs_generated > 0:
                print(f"✅ Auto-generated {docs_generated} documentation files")
            else:
                print(f"⚠️  No documentation generated for {orchestrator_name}")
        
        return True
    
    @staticmethod
    def _calculate_overall_completion(content: str, current_phase: str, phase_completion: int) -> int:
        """Calculate overall migration completion percentage."""
        # Phase weights (based on duration)
        weights = {
            "0": 5,   # 1 week
            "1": 15,  # 3 weeks
            "1.5": 5, # 1 week
            "2": 25,  # 5 weeks
            "3": 25,  # 5 weeks
            "4": 15,  # 3 weeks
            "5": 15,  # 3 weeks
            "6": 5    # 1 week
        }
        
        # Extract all phase percentages from content
        phase_percentages = {}
        for phase in weights.keys():
            match = re.search(rf"PHASE {re.escape(phase)}:.+?\[.+?\]\s+(\d+)%", content)
            if match:
                phase_percentages[phase] = int(match.group(1))
            else:
                phase_percentages[phase] = 0
        
        # Update current phase
        phase_percentages[current_phase] = phase_completion
        
        # Calculate weighted average
        total = sum(phase_percentages[p] * weights[p] for p in weights.keys())
        overall = total // sum(weights.values())
        return overall
    
    @classmethod
    def _trigger_auto_documentation(cls, orchestrator_name: str) -> int:
        """
        Trigger automatic documentation generation for completed orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "execution", "documentation", "tdd")
        
        Returns:
            Number of documentation files generated
        """
        try:
            # Import here to avoid circular dependencies
            from pathlib import Path
            import sys
            
            # Ensure src is in path
            src_path = Path(__file__).parent.parent
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            from orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
                DocumentationOrchestrator,
                DocumentationConfig
            )
            
            # Setup logger
            logger = logging.getLogger(f"auto_docs.{orchestrator_name}")
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            
            # Map orchestrator names to source paths
            orchestrator_paths = {
                "execution": "orchestrators/execution",
                "documentation": "orchestrators/documentation",
                "tdd": "orchestrators/tdd",
                "planning": "orchestrators/planning",
                "sanitization": "orchestrators/sanitization",
                "ado": "orchestrators/ado",
                "maintenance": "orchestrators/maintenance",
                # Base components
                "base": "base",
                "phase_2": "phase_2",  # Autonomous execution framework
                "phase_3": "phase_3",  # Foundation components
            }
            
            if orchestrator_name not in orchestrator_paths:
                logger.warning(f"Unknown orchestrator: {orchestrator_name}")
                return 0
            
            # Determine source and output paths
            source_path = src_path / "orchestration_4_0" / orchestrator_paths[orchestrator_name]
            output_path = src_path.parent / "docs" / "orchestration_4_0" / orchestrator_name
            
            if not source_path.exists():
                logger.error(f"Source path not found: {source_path}")
                return 0
            
            logger.info(f"Generating documentation for {orchestrator_name}")
            logger.info(f"  Source: {source_path}")
            logger.info(f"  Output: {output_path}")
            
            # Create documentation config
            config = DocumentationConfig(
                source_paths=[source_path],
                output_dir=output_path,
                include_private=False,
                generate_diagrams=True,
                generate_quick_ref=True,
                diagram_types=["class_hierarchy", "phase_flow"]
            )
            
            # Execute documentation orchestrator
            doc_orchestrator = DocumentationOrchestrator(logger=logger)
            result = doc_orchestrator.execute({'config': config})
            
            if result.get('status') == 'success':
                doc_result = result.get('result')
                logger.info(f"✅ Documentation generated successfully")
                logger.info(f"  Modules: {doc_result.modules_analyzed}")
                logger.info(f"  Classes: {doc_result.classes_documented}")
                logger.info(f"  Files: {len(doc_result.output_files)}")
                return len(doc_result.output_files)
            else:
                logger.error(f"Documentation generation failed: {result.get('error')}")
                return 0
                
        except Exception as e:
            logging.error(f"Auto-documentation failed for {orchestrator_name}: {e}")
            import traceback
            traceback.print_exc()
            return 0


def update_master_plan_progress(**kwargs):
    """Convenience function for orchestrators to call."""
    return ProgressTracker.update_progress(**kwargs)


if __name__ == "__main__":
    # Test update
    print("Testing progress tracker...")
    success = update_master_plan_progress(
        phase="1",
        week="1",
        completion_percentage=60,
        week_completion=60,
        metrics={
            "orchestrators_migrated": 0,
            "test_coverage": "10/10 foundation prerequisites passing",
            "docs_generated": 0,
            "lines_reduced": 0
        }
    )
    print(f"Update {'successful' if success else 'failed'}")
