"""
Plan Migration Utility - Phase 14

Migrates existing plans to unified format with token tracking.
Supports batch migrations with dry-run mode.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import tiktoken

from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator
from src.operations.modules.planning.token_reduction_tracker import TokenReductionTracker


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Token count
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback to simple estimation
        return len(text) // 4


class PlanMigrationUtility:
    """Migrates plans from legacy/Planning System 2.0 to unified format."""
    
    def __init__(self, generator: Optional[UnifiedPlanGenerator] = None):
        """Initialize migration utility.
        
        Args:
            generator: UnifiedPlanGenerator instance (creates one if None)
        """
        self.generator = generator or UnifiedPlanGenerator()
        self.tracker = TokenReductionTracker()
    
    def detect_plan_format(self, plan_path: Path) -> Dict[str, Any]:
        """Detect format of existing plan.
        
        Args:
            plan_path: Path to plan file
            
        Returns:
            Dictionary with format information:
            {
                'format': 'unified' | 'planning_system_2.0' | 'legacy',
                'has_visual_tracker': bool,
                'has_token_tracking': bool,
                'has_continuation_prompt': bool,
                'has_dor_dod': bool
            }
        """
        content = plan_path.read_text(encoding='utf-8')
        
        # Check for unified format markers
        has_visual_tracker = '## 📊 Visual Progress Tracker' in content
        has_token_tracking = 'Token Reduction' in content or 'tokens saved' in content.lower()
        has_continuation = '## 🔄 Continuation Prompt' in content
        has_author = '**Author:** Asif Hussain' in content
        has_dor_dod = '## 📋 Definition of Ready' in content or 'DoR' in content
        
        # Determine format
        if has_visual_tracker and has_author:
            format_type = 'unified'
        elif has_dor_dod and '## 🎯 Overview' in content:
            format_type = 'planning_system_2.0'
        else:
            format_type = 'legacy'
        
        return {
            'format': format_type,
            'has_visual_tracker': has_visual_tracker,
            'has_token_tracking': has_token_tracking,
            'has_continuation_prompt': has_continuation,
            'has_author': has_author,
            'has_dor_dod': has_dor_dod
        }
    
    def extract_phases(self, plan_path: Path) -> List[Dict[str, Any]]:
        """Extract phase information from existing plan.
        
        Args:
            plan_path: Path to plan file
            
        Returns:
            List of phase dictionaries with name, status, tasks
        """
        content = plan_path.read_text(encoding='utf-8')
        phases = []
        
        # Pattern 1: Unified/Planning System 2.0 format
        # ### Phase 1: Name or ## Phase 1: Name
        phase_pattern = r'###?\s+Phase\s+(\d+(?:\.\d+)?):?\s+([^\n]+)'
        
        for match in re.finditer(phase_pattern, content, re.MULTILINE):
            phase_num = match.group(1)
            phase_name = match.group(2).strip()
            
            # Try to detect status from markers
            status = 'PENDING'
            if '✅' in phase_name or 'COMPLETE' in phase_name.upper():
                status = 'COMPLETE'
            elif '🔄' in phase_name or 'IN PROGRESS' in phase_name.upper():
                status = 'IN PROGRESS'
            
            # Extract tasks for this phase (simple approach)
            phase_section_start = match.end()
            next_phase = re.search(phase_pattern, content[phase_section_start:])
            phase_section_end = phase_section_start + next_phase.start() if next_phase else len(content)
            phase_content = content[phase_section_start:phase_section_end]
            
            # Count tasks (lines starting with - or Task)
            tasks = []
            task_pattern = r'[-•]\s+(?:Task\s+[\d.]+:?\s+)?([^\n]+)'
            for task_match in re.finditer(task_pattern, phase_content):
                task_desc = task_match.group(1).strip()
                tasks.append({
                    'description': task_desc,
                    'status': 'complete' if '✅' in task_desc else 'pending'
                })
            
            phases.append({
                'id': phase_num,
                'name': phase_name.replace('✅', '').replace('🔄', '').strip(),
                'status': status,
                'tasks': tasks
            })
        
        return phases
    
    def migrate_to_unified(
        self,
        source: Path,
        destination: Path,
        plan_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Migrate plan to unified format.
        
        Args:
            source: Source plan file
            destination: Destination file path
            plan_id: Plan identifier
            dry_run: If True, only preview changes
            
        Returns:
            Migration result dictionary
        """
        try:
            # Count tokens before
            original_content = source.read_text(encoding='utf-8')
            tokens_before = count_tokens(original_content)
            
            # Detect current format
            format_info = self.detect_plan_format(source)
            
            # If already unified, skip
            if format_info['format'] == 'unified':
                return {
                    'success': True,
                    'skipped': True,
                    'reason': 'Already in unified format',
                    'tokens_before': tokens_before,
                    'tokens_after': tokens_before,
                    'tokens_delta': 0
                }
            
            # Extract phases
            phases = self.extract_phases(source)
            
            if not phases:
                return {
                    'success': False,
                    'error': 'No phases detected in source plan'
                }
            
            # Extract metadata
            title_match = re.search(r'^#\s+(.+)$', original_content, re.MULTILINE)
            title = title_match.group(1) if title_match else plan_id.replace('-', ' ').title()
            
            # Build metadata
            metadata = {
                'title': title,
                'version': '3.1.0',
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'author': 'Asif Hussain'
            }
            
            # Generate unified format using UnifiedPlanGenerator
            unified_content = self.generator.generate_master_plan(
                plan_id=plan_id,
                phases=phases,
                metadata=metadata,
                compressed=True  # Phase 15: Token optimization
            )
            
            # Count tokens after
            tokens_after = count_tokens(unified_content)
            tokens_delta = tokens_after - tokens_before
            
            result = {
                'success': True,
                'tokens_before': tokens_before,
                'tokens_after': tokens_after,
                'tokens_delta': tokens_delta,
                'format_migrated_from': format_info['format'],
                'phases_migrated': len(phases)
            }
            
            if dry_run:
                result['preview'] = unified_content
            else:
                # Write to destination
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(unified_content, encoding='utf-8')
                result['destination'] = str(destination)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_migration(self, plan_path: Path) -> Dict[str, Any]:
        """Validate migrated plan has all required elements.
        
        Args:
            plan_path: Path to migrated plan
            
        Returns:
            Validation result dictionary
        """
        format_info = self.detect_plan_format(plan_path)
        
        required_elements = {
            'has_visual_tracker': format_info['has_visual_tracker'],
            'has_author': format_info['has_author'],
            'has_continuation_prompt': format_info['has_continuation_prompt']
        }
        
        valid = all(required_elements.values())
        
        return {
            'valid': valid,
            **required_elements,
            'format': format_info['format']
        }
    
    def migrate_batch(
        self,
        source_dir: Path,
        pattern: str = "*.md",
        output_dir: Optional[Path] = None,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Migrate multiple plans in batch.
        
        Args:
            source_dir: Directory containing plans
            pattern: File pattern to match
            output_dir: Output directory (uses source_dir if None)
            dry_run: If True, only preview changes
            
        Returns:
            List of migration results
        """
        output_dir = output_dir or source_dir
        results = []
        
        for plan_file in source_dir.glob(pattern):
            if plan_file.name.startswith('.'):
                continue
            
            plan_id = plan_file.stem
            output_file = output_dir / plan_file.name
            
            result = self.migrate_to_unified(
                source=plan_file,
                destination=output_file,
                plan_id=plan_id,
                dry_run=dry_run
            )
            
            result['source_file'] = str(plan_file)
            results.append(result)
        
        return results


def main():
    """CLI entry point for migration utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate plans to unified format')
    parser.add_argument('source', help='Source plan file or directory')
    parser.add_argument('--output', '-o', help='Output file or directory')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Preview changes only')
    parser.add_argument('--batch', '-b', action='store_true', help='Batch mode (source must be directory)')
    parser.add_argument('--pattern', '-p', default='*.md', help='File pattern for batch mode')
    parser.add_argument('--plan-id', help='Plan ID (required for single file mode)')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    utility = PlanMigrationUtility()
    
    if args.batch:
        if not source_path.is_dir():
            print(f"Error: Source must be directory for batch mode: {source_path}")
            return 1
        
        output_dir = Path(args.output) if args.output else source_path
        results = utility.migrate_batch(
            source_dir=source_path,
            pattern=args.pattern,
            output_dir=output_dir,
            dry_run=args.dry_run
        )
        
        # Print summary
        success_count = sum(1 for r in results if r['success'])
        print(f"\nMigrated {success_count}/{len(results)} plans")
        
        for result in results:
            status = '✅' if result['success'] else '❌'
            file_name = Path(result['source_file']).name
            
            if result['success']:
                if result.get('skipped'):
                    print(f"{status} {file_name}: Skipped ({result['reason']})")
                else:
                    delta = result['tokens_delta']
                    delta_str = f"+{delta}" if delta > 0 else str(delta)
                    print(f"{status} {file_name}: {result['phases_migrated']} phases, {delta_str} tokens")
            else:
                print(f"{status} {file_name}: {result['error']}")
    
    else:
        # Single file mode
        if not source_path.is_file():
            print(f"Error: Source must be file: {source_path}")
            return 1
        
        if not args.plan_id:
            print("Error: --plan-id required for single file mode")
            return 1
        
        output_path = Path(args.output) if args.output else source_path
        result = utility.migrate_to_unified(
            source=source_path,
            destination=output_path,
            plan_id=args.plan_id,
            dry_run=args.dry_run
        )
        
        if result['success']:
            print(f"✅ Migration successful")
            print(f"   Tokens: {result['tokens_before']} → {result['tokens_after']} ({result['tokens_delta']:+d})")
            print(f"   Phases: {result['phases_migrated']}")
            
            if args.dry_run and 'preview' in result:
                print("\n--- Preview ---")
                print(result['preview'][:500])
                print("...")
        else:
            print(f"❌ Migration failed: {result['error']}")
            return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
