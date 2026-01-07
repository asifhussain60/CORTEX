#!/usr/bin/env python3
"""
CORTEX Toolkit: Plan Progress Tracker Synchronizer

Syncs progress between master plan (00-master-plan.md) and tracker JSON file.
Ensures decomposed plan files stay in sync with visual progress display.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PlanTrackerSync:
    """Synchronizes progress between master plan markdown and tracker JSON."""
    
    def __init__(self, plan_dir: Path):
        """
        Initialize sync for a specific plan directory.
        
        Args:
            plan_dir: Path to plan directory (e.g., cortex-brain/documents/planning/active/my-plan/)
        """
        self.plan_dir = Path(plan_dir)
        self.master_plan = self.plan_dir / "00-master-plan.md"
        self.tracker_file = self.plan_dir / "tracking" / "progress-tracker.json"
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        
    def extract_progress_from_master_plan(self) -> Dict:
        """
        Extract progress information from master plan markdown.
        
        Returns:
            Dict with structure: {
                "overall_progress": 45,
                "phases": [
                    {"num": 1, "name": "Discovery", "progress": 100, "status": "complete"},
                    {"num": 2, "name": "Analysis", "progress": 50, "status": "in_progress"}
                ]
            }
        """
        if not self.master_plan.exists():
            raise FileNotFoundError(f"Master plan not found: {self.master_plan}")
        
        with open(self.master_plan, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract overall progress
        overall_match = re.search(r'\*\*Overall Progress:\*\*\s+`([█░]+)`\s+\*\*(\d+)%\*\*', content)
        overall_progress = int(overall_match.group(2)) if overall_match else 0
        
        # Extract phase table
        phases = []
        phase_pattern = r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*`([█░]+)`\s+(\d+)%\s*\|\s*\d+/\d+\s*\|\s*([^|]+)\|'
        
        for match in re.finditer(phase_pattern, content):
            phase_num = int(match.group(1))
            phase_name = match.group(2).strip()
            progress = int(match.group(4))
            status_text = match.group(5).strip()
            
            # Parse status from emoji
            if "✅" in status_text:
                status = "complete"
            elif "🔄" in status_text:
                status = "in_progress"
            elif "❌" in status_text:
                status = "failed"
            elif "⏸️" in status_text:
                status = "paused"
            else:
                status = "pending"
            
            phases.append({
                "num": phase_num,
                "name": phase_name,
                "progress": progress,
                "status": status
            })
        
        return {
            "overall_progress": overall_progress,
            "phases": phases,
            "last_synced": datetime.now().isoformat()
        }
    
    def load_tracker_json(self) -> Dict:
        """
        Load progress tracker JSON file.
        
        Returns:
            Tracker data or empty structure if file doesn't exist
        """
        if not self.tracker_file.exists():
            return {
                "plan_name": self.plan_dir.name,
                "overall_progress": 0,
                "phases": [],
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        
        with open(self.tracker_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_tracker_json(self, data: Dict):
        """Save tracker data to JSON file."""
        data["last_updated"] = datetime.now().isoformat()
        
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def sync_from_master_to_tracker(self) -> Tuple[bool, str]:
        """
        Sync progress from master plan to tracker JSON.
        
        Returns:
            (success, message)
        """
        try:
            # Extract from master plan
            master_data = self.extract_progress_from_master_plan()
            
            # Load existing tracker
            tracker_data = self.load_tracker_json()
            
            # Update tracker with master plan data
            tracker_data["overall_progress"] = master_data["overall_progress"]
            tracker_data["phases"] = master_data["phases"]
            tracker_data["last_synced_from_master"] = master_data["last_synced"]
            
            # Save updated tracker
            self.save_tracker_json(tracker_data)
            
            return True, f"✅ Synced {len(master_data['phases'])} phases from master plan to tracker"
            
        except Exception as e:
            return False, f"❌ Sync failed: {str(e)}"
    
    def update_master_plan_progress(self, phase_num: int, new_progress: int, new_status: str = None) -> Tuple[bool, str]:
        """
        Update a specific phase's progress in master plan.
        
        Args:
            phase_num: Phase number (1-based)
            new_progress: New progress percentage (0-100)
            new_status: New status (complete, in_progress, pending, failed, paused)
        
        Returns:
            (success, message)
        """
        if not self.master_plan.exists():
            return False, f"❌ Master plan not found: {self.master_plan}"
        
        try:
            with open(self.master_plan, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate progress bar
            bar_width = 10
            filled = int((new_progress / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Status emoji mapping
            status_icons = {
                "complete": "✅",
                "in_progress": "🔄",
                "pending": "⏳",
                "failed": "❌",
                "paused": "⏸️"
            }
            status_emoji = status_icons.get(new_status, "⏳") if new_status else None
            
            # Find and update phase row
            phase_pattern = rf'(\|\s*{phase_num}\s*\|[^|]+\|)\s*`[█░]+`\s+\d+%\s*(\|[^|]+\|)\s*([^|]+)\|'
            
            def replace_phase(match):
                before = match.group(1)
                after = match.group(2)
                old_status = match.group(3).strip()
                
                # Use existing status emoji if new_status not provided
                if not status_emoji:
                    for emoji in status_icons.values():
                        if emoji in old_status:
                            final_status = old_status
                            break
                    else:
                        final_status = old_status
                else:
                    # Replace status emoji
                    final_status = re.sub(r'[✅🔄⏳❌⏸️]', status_emoji, old_status)
                    if not any(emoji in old_status for emoji in status_icons.values()):
                        # No emoji found, prepend
                        final_status = f"{status_emoji} {old_status}"
                
                return f"{before} `{bar}` {new_progress}% {after} {final_status} |"
            
            updated_content = re.sub(phase_pattern, replace_phase, content)
            
            if updated_content == content:
                return False, f"❌ Phase {phase_num} not found in master plan"
            
            # Update overall progress
            tracker_data = self.load_tracker_json()
            if tracker_data["phases"]:
                avg_progress = sum(p["progress"] for p in tracker_data["phases"]) / len(tracker_data["phases"])
                overall_bar = "█" * int((avg_progress / 100) * bar_width) + "░" * (bar_width - int((avg_progress / 100) * bar_width))
                
                updated_content = re.sub(
                    r'\*\*Overall Progress:\*\*\s+`[█░]+`\s+\*\*\d+%\*\*',
                    f"**Overall Progress:** `{overall_bar}` **{int(avg_progress)}%**",
                    updated_content
                )
            
            # Save updated master plan
            with open(self.master_plan, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Sync to tracker
            self.sync_from_master_to_tracker()
            
            return True, f"✅ Updated Phase {phase_num} to {new_progress}% in master plan"
            
        except Exception as e:
            return False, f"❌ Update failed: {str(e)}"
    
    def generate_bidirectional_links(self) -> str:
        """
        Generate markdown links for bidirectional navigation.
        
        Returns:
            Markdown snippet with links
        """
        links = [
            "### 📄 Plan Navigation",
            "",
            f"**Master Plan:** [00-master-plan.md]({self.master_plan.name})",
            f"**Progress Tracker:** [progress-tracker.json](tracking/progress-tracker.json)",
            "",
            "**Context Files:**"
        ]
        
        # Find context files
        context_dir = self.plan_dir / "context"
        if context_dir.exists():
            for file in sorted(context_dir.glob("*.md")):
                links.append(f"- [{file.name}](context/{file.name})")
        
        # Find artifact files
        artifacts_dir = self.plan_dir / "artifacts"
        if artifacts_dir.exists():
            links.append("")
            links.append("**Artifacts:**")
            for file in sorted(artifacts_dir.glob("*.yaml")):
                links.append(f"- [{file.name}](artifacts/{file.name})")
        
        # Find report files
        reports_dir = self.plan_dir / "reports"
        if reports_dir.exists():
            links.append("")
            links.append("**Reports:**")
            for file in sorted(reports_dir.glob("*.md")):
                links.append(f"- [{file.name}](reports/{file.name})")
        
        return "\n".join(links)
    
    def validate_consistency(self) -> Tuple[bool, List[str]]:
        """
        Validate consistency between master plan and tracker.
        
        Returns:
            (is_consistent, list_of_issues)
        """
        issues = []
        
        try:
            master_data = self.extract_progress_from_master_plan()
            tracker_data = self.load_tracker_json()
            
            # Check phase count
            master_phases = len(master_data["phases"])
            tracker_phases = len(tracker_data.get("phases", []))
            
            if master_phases != tracker_phases:
                issues.append(f"Phase count mismatch: Master={master_phases}, Tracker={tracker_phases}")
            
            # Check individual phase progress
            for master_phase in master_data["phases"]:
                tracker_phase = next(
                    (p for p in tracker_data.get("phases", []) if p.get("num", p.get("phase_num")) == master_phase["num"]),
                    None
                )
                
                if not tracker_phase:
                    issues.append(f"Phase {master_phase['num']} missing from tracker")
                    continue
                
                if master_phase["progress"] != tracker_phase["progress"]:
                    issues.append(
                        f"Phase {master_phase['num']} progress mismatch: "
                        f"Master={master_phase['progress']}%, Tracker={tracker_phase['progress']}%"
                    )
                
                if master_phase["status"] != tracker_phase["status"]:
                    issues.append(
                        f"Phase {master_phase['num']} status mismatch: "
                        f"Master={master_phase['status']}, Tracker={tracker_phase['status']}"
                    )
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
            return False, issues


def sync_all_active_plans(cortex_root: Path = None) -> Dict[str, Tuple[bool, str]]:
    """
    Sync all active plans in planning/active/ directory.
    
    Args:
        cortex_root: Path to CORTEX root (defaults to script parent)
    
    Returns:
        Dict mapping plan_name -> (success, message)
    """
    if cortex_root is None:
        cortex_root = Path(__file__).parent.parent
    
    active_plans_dir = cortex_root / "cortex-brain" / "documents" / "planning" / "active"
    
    if not active_plans_dir.exists():
        return {"error": (False, f"Active plans directory not found: {active_plans_dir}")}
    
    results = {}
    
    for plan_dir in active_plans_dir.iterdir():
        if not plan_dir.is_dir():
            continue
        
        master_plan = plan_dir / "00-master-plan.md"
        if not master_plan.exists():
            continue
        
        syncer = PlanTrackerSync(plan_dir)
        success, message = syncer.sync_from_master_to_tracker()
        results[plan_dir.name] = (success, message)
    
    return results


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync plan progress tracker")
    parser.add_argument("plan_dir", help="Path to plan directory")
    parser.add_argument("--update-phase", type=int, help="Update specific phase number")
    parser.add_argument("--progress", type=int, help="New progress percentage (0-100)")
    parser.add_argument("--status", choices=["complete", "in_progress", "pending", "failed", "paused"], help="New status")
    parser.add_argument("--validate", action="store_true", help="Validate consistency")
    parser.add_argument("--sync-all", action="store_true", help="Sync all active plans")
    
    args = parser.parse_args()
    
    if args.sync_all:
        results = sync_all_active_plans()
        print("\n=== Syncing All Active Plans ===\n")
        for plan_name, (success, message) in results.items():
            print(f"{plan_name}: {message}")
        return
    
    syncer = PlanTrackerSync(Path(args.plan_dir))
    
    if args.validate:
        is_consistent, issues = syncer.validate_consistency()
        if is_consistent:
            print("✅ Master plan and tracker are consistent")
        else:
            print("❌ Consistency issues found:")
            for issue in issues:
                print(f"   - {issue}")
        return
    
    if args.update_phase:
        if args.progress is None:
            print("❌ --progress required when using --update-phase")
            return
        
        success, message = syncer.update_master_plan_progress(
            args.update_phase,
            args.progress,
            args.status
        )
        print(message)
        return
    
    # Default: sync from master to tracker
    success, message = syncer.sync_from_master_to_tracker()
    print(message)
    
    # Show bidirectional links
    print("\n" + syncer.generate_bidirectional_links())


if __name__ == "__main__":
    main()
