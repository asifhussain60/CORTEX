"""
Migrate all active plans to enhanced progress tracker format.

This script:
1. Scans cortex-brain/documents/planning/active/ for all master plans
2. Parses existing progress tracker sections
3. Regenerates them using the new 3-section format with efficiency metrics
4. Updates files in-place with backup
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class PlanMigrator:
    """Migrates plans to enhanced progress tracker format."""
    
    def __init__(self, dry_run: bool = False):
        self.generator = UnifiedPlanGenerator()
        self.dry_run = dry_run
        self.plans_migrated = 0
        self.plans_skipped = 0
        
    def migrate_all_plans(self, plans_dir: Path):
        """Migrate all master plans in directory."""
        print(f"🔍 Scanning {plans_dir} for master plans...")
        
        # Find all 00-master-plan.md files
        master_plans = list(plans_dir.rglob("00-master-plan.md"))
        print(f"✅ Found {len(master_plans)} master plan(s)")
        
        for plan_path in master_plans:
            try:
                self.migrate_plan(plan_path)
            except Exception as e:
                print(f"❌ Error migrating {plan_path}: {e}")
                
        print(f"\n📊 Migration Summary:")
        print(f"  ✅ Migrated: {self.plans_migrated}")
        print(f"  ⏭️  Skipped: {self.plans_skipped}")
        
    def migrate_plan(self, plan_path: Path):
        """Migrate a single master plan."""
        print(f"\n📝 Processing: {plan_path.relative_to(plan_path.parent.parent.parent)}")
        
        # Read current content
        content = plan_path.read_text(encoding='utf-8')
        
        # Check if already migrated
        if "### 📋 Initial Estimates" in content:
            print("  ⏭️  Already migrated (has 3-section format)")
            self.plans_skipped += 1
            return
            
        # Check if has old format
        if "### Estimates" not in content and "## 📊 Progress" not in content and "## 📊 Visual Progress Tracker" not in content:
            print("  ⏭️  No progress tracker found - skipping")
            self.plans_skipped += 1
            return
            
        # Extract phases from table
        phases = self._extract_phases(content)
        if not phases:
            print("  ⏭️  No phases table found - skipping")
            self.plans_skipped += 1
            return
            
        # Extract baseline tokens
        baseline_tokens, total_files = self._extract_baseline_info(content)
        
        # Generate new progress tracker
        new_tracker = self.generator.generate_progress_tracker(
            phases=phases,
            baseline_tokens=baseline_tokens,
            current_tokens=baseline_tokens,  # Will be recalculated
            total_files=total_files,
            compressed=False
        )
        
        # Replace old tracker with new one
        new_content = self._replace_progress_tracker(content, new_tracker)
        
        # Backup and save
        if not self.dry_run:
            backup_path = plan_path.with_suffix('.md.bak')
            backup_path.write_text(content, encoding='utf-8')
            plan_path.write_text(new_content, encoding='utf-8')
            print(f"  ✅ Migrated (backup: {backup_path.name})")
        else:
            print(f"  ✅ Would migrate (dry run)")
            
        self.plans_migrated += 1
        
    def _extract_phases(self, content: str) -> List[Dict]:
        """Extract phases from table in content."""
        phases = []
        
        # Find phase table
        table_match = re.search(
            r'\| Phase \| Name \| Status \| .*?\n\|[-|]+\|\n(.*?)(?:\n\n|\n---|\Z)',
            content,
            re.DOTALL
        )
        
        if not table_match:
            return []
            
        table_rows = table_match.group(1).strip().split('\n')
        
        for row in table_rows:
            if not row.strip() or row.strip() == '|':
                continue
                
            cols = [c.strip() for c in row.split('|') if c.strip()]
            if len(cols) >= 4:
                phase_id = cols[0]
                name = cols[1].replace('[', '').replace(']', '').split('(')[0].strip()
                status_emoji = cols[2]
                
                # Determine status from emoji
                if '✅' in status_emoji or 'COMPLETE' in status_emoji:
                    status = 'complete'
                elif '🚀' in status_emoji or 'PROGRESS' in status_emoji:
                    status = 'in-progress'
                else:
                    status = 'pending'
                    
                # Extract time values
                estimated = cols[3] if len(cols) > 3 else '-'
                actual = cols[4] if len(cols) > 4 else '-'
                elapsed = cols[5] if len(cols) > 5 else '-'
                tokens_saved = cols[6] if len(cols) > 6 else '-'
                
                phases.append({
                    'id': phase_id,
                    'name': name,
                    'status': status,
                    'estimated': estimated,
                    'actual': actual,
                    'elapsed': elapsed,
                    'tokens_saved': tokens_saved
                })
                
        return phases
        
    def _extract_baseline_info(self, content: str) -> Tuple[int, int]:
        """Extract baseline tokens and file count from content."""
        # Look for baseline info
        baseline_match = re.search(r'Baseline:\s*([0-9.]+[KM]?)\s+tokens.*?([0-9,]+)\s+files', content)
        if baseline_match:
            token_str = baseline_match.group(1)
            file_str = baseline_match.group(2).replace(',', '')
            
            # Convert token string to number
            tokens = 0
            if 'M' in token_str:
                tokens = int(float(token_str.replace('M', '')) * 1_000_000)
            elif 'K' in token_str:
                tokens = int(float(token_str.replace('K', '')) * 1_000)
            else:
                tokens = int(float(token_str))
                
            files = int(file_str)
            return tokens, files
            
        return 0, 0
        
    def _replace_progress_tracker(self, content: str, new_tracker: str) -> str:
        """Replace old progress tracker with new one."""
        # Find and replace the progress tracker section
        # Pattern matches from "## 📊" to the phase table end
        pattern = r'(## 📊 (Visual Progress Tracker|Progress).*?)(---\n\*\*Last Updated:)'
        
        def replace_func(match):
            return new_tracker + "\n\n" + match.group(3)
            
        new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
        
        # Update timestamp
        new_content = re.sub(
            r'\*\*Last Updated:\*\* [^\n]+',
            f"**Last Updated:** {datetime.now().strftime('%B %d, %Y, %I:%M %p')}",
            new_content
        )
        
        return new_content


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate plans to enhanced format')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--plans-dir', type=str, 
                        default='cortex-brain/documents/planning/active',
                        help='Directory containing plans to migrate')
    args = parser.parse_args()
    
    plans_dir = Path(args.plans_dir)
    if not plans_dir.exists():
        print(f"❌ Error: {plans_dir} does not exist")
        return 1
        
    migrator = PlanMigrator(dry_run=args.dry_run)
    migrator.migrate_all_plans(plans_dir)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
