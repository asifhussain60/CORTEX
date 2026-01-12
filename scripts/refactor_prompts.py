#!/usr/bin/env python3
"""
CORTEX PROMPT ALIGNMENT REFACTORING ENGINE
Physically refactors all prompts to eliminate conflicts and achieve unified architecture
Version: 1.0.0
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class PromptRefactorer:
    """Unified prompt refactoring orchestrator"""
    
    PROMPTS_DIR = ".github/prompts"
    
    # Unified regression check pattern (v2.0)
    REGRESSION_PATTERN = '''## 🛡️ REGRESSION PREVENTION PROTOCOL (UNIFIED)

**Before any operation, verify critical state files:**

```python
# 🛡️ UNIFIED REGRESSION CHECK
import json, yaml, sys

errors = []
try:
    ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
    if not ac_index.get('schema_version'): errors.append("AC-INDEX missing schema_version")
except Exception as e: errors.append(f"AC-INDEX parse error: {e}")

try:
    tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
    if not tracker.get('current_phase'): errors.append("tracker missing current_phase")
except Exception as e: errors.append(f"tracker parse error: {e}")

try:
    plan = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
    if not plan.get('plan_metadata'): errors.append("master-plan missing plan_metadata")
except Exception as e: errors.append(f"master-plan parse error: {e}")

if errors:
    print("❌ REGRESSION DETECTED:\\n" + "\\n".join([f"  - {e}" for e in errors]))
    sys.exit(1)
print("✅ Regression check passed.")
```'''

    # Unified sync protocol
    SYNC_PROTOCOL = '''## 📊 UNIFIED SYNC PROTOCOL

**After state updates, sync dashboard ONCE per operation:**

```bash
# Sync dashboard (ONE call per command execution)
python3 scripts/sync_plan_viewer_data.py || exit 1
echo "✅ Dashboard synced."
```

**Key Rule:** Call sync ONCE after all state updates, not after each state change.'''

    # MasterOrchestrator delegation section
    ORCHESTRATOR_DELEGATION = '''## 🔗 MASTERORCHESTRATOR DELEGATION

**All implementation delegated to unified orchestrator:**

```bash
# Execute via MasterOrchestrator (central control)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against SKULL rules
- ✅ Create TodoManager tasks
- ✅ Execute tasks in dependency order
- ✅ Update progress-tracker.json (atomic writes)
- ✅ Enforce phase gates
- ✅ Return structured results

**Do NOT:**
- ❌ Directly modify progress-tracker.json
- ❌ Directly modify AC-INDEX.yaml
- ❌ Call sync_plan_viewer_data.py multiple times
- ❌ Manipulate state outside MasterOrchestrator

---'''

    def __init__(self):
        self.stats = {
            'refactored': [],
            'sync_consolidations': 0,
            'regression_standardizations': 0,
            'delegation_additions': 0,
            'errors': []
        }

    def standardize_regression_check(self, content: str) -> Tuple[str, bool]:
        """Replace any regression check variant with unified pattern"""
        # Remove old regression patterns (various formats)
        patterns_to_remove = [
            r'## 🛡️ REGRESSION PREVENTION.*?(?=\n## |\Z)',
            r'### .*?Regression.*?(?=\n## |\n### |\Z)',
        ]
        
        new_content = content
        changed = False
        
        for pattern in patterns_to_remove:
            if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                new_content = re.sub(pattern, '', new_content, flags=re.DOTALL | re.IGNORECASE)
                changed = True
        
        # If regression check doesn't exist or was removed, add unified one
        if '🛡️ REGRESSION PREVENTION PROTOCOL (UNIFIED)' not in new_content:
            # Find the right place to insert (after intro, before execution)
            insert_point = self._find_insert_point(new_content, 'after_intro')
            if insert_point >= 0:
                new_content = (
                    new_content[:insert_point] + 
                    "\n" + self.REGRESSION_PATTERN + "\n\n" +
                    new_content[insert_point:]
                )
                changed = True
        
        return new_content, changed

    def consolidate_sync_calls(self, content: str) -> Tuple[str, int]:
        """Replace multiple sync_plan_viewer_data.py calls with unified protocol"""
        sync_count = len(re.findall(r'sync_plan_viewer_data\.py', content))
        
        if sync_count == 0:
            # No sync calls, add unified protocol section
            return content, 0
        
        # Remove all scattered sync_plan_viewer_data.py calls
        new_content = re.sub(
            r'\n.*?python3\s+scripts/sync_plan_viewer_data\.py.*?\n',
            '\n',
            content,
            flags=re.MULTILINE
        )
        
        # Also remove commented references
        new_content = re.sub(
            r'Run `python3 scripts/sync_plan_viewer_data\.py`.*?\n',
            '',
            new_content,
            flags=re.MULTILINE
        )
        
        # Add unified sync protocol (once) if not already present
        if '📊 UNIFIED SYNC PROTOCOL' not in new_content:
            # Find orchestrator execution section
            orch_pos = new_content.find('## 🔗 MASTERORCHESTRATOR')
            if orch_pos > 0:
                new_content = (
                    new_content[:orch_pos] +
                    self.SYNC_PROTOCOL + "\n\n" +
                    new_content[orch_pos:]
                )
        
        return new_content, sync_count

    def add_orchestrator_delegation(self, content: str) -> Tuple[str, bool]:
        """Add MasterOrchestrator delegation section if missing"""
        if '## 🔗 MASTERORCHESTRATOR DELEGATION' in content:
            return content, False
        
        # Find insertion point (typically after regression check or intro)
        insert_point = self._find_insert_point(content, 'after_intro')
        
        new_content = (
            content[:insert_point] +
            "\n" + self.ORCHESTRATOR_DELEGATION + "\n" +
            content[insert_point:]
        )
        
        return new_content, True

    def _find_insert_point(self, content: str, position: str) -> int:
        """Find logical insertion point in content"""
        lines = content.split('\n')
        
        if position == 'after_intro':
            # After the file intro/metadata, before execution details
            for i, line in enumerate(lines):
                if re.match(r'^## ', line):
                    return len('\n'.join(lines[:i])) + 1
        
        return len(content)

    def remove_direct_state_manipulation(self, content: str) -> Tuple[str, bool]:
        """Remove anti-patterns: direct state file manipulation"""
        anti_patterns = [
            r'json\.dump.*progress-tracker\.json',
            r'json\.dump.*AC-INDEX\.yaml',
            r'yaml\.dump.*master-plan\.yaml',
        ]
        
        changed = False
        for pattern in anti_patterns:
            if re.search(pattern, content):
                changed = True
                # Log but don't auto-remove (requires context)
        
        return content, changed

    def refactor_prompt(self, filepath: str) -> bool:
        """Refactor a single prompt file"""
        try:
            with open(filepath, 'r') as f:
                original_content = f.read()
            
            content = original_content
            
            # STEP 1: Standardize regression check
            content, changed_regression = self.standardize_regression_check(content)
            if changed_regression:
                self.stats['regression_standardizations'] += 1
            
            # STEP 2: Consolidate sync calls
            content, sync_count = self.consolidate_sync_calls(content)
            if sync_count > 0:
                self.stats['sync_consolidations'] += sync_count - 1  # count reduction
            
            # STEP 3: Add orchestrator delegation (if not present)
            content, added_orch = self.add_orchestrator_delegation(content)
            if added_orch:
                self.stats['delegation_additions'] += 1
            
            # STEP 4: Check for direct state manipulation (flag only)
            content, has_anti_pattern = self.remove_direct_state_manipulation(content)
            
            # Write back if changed
            if content != original_content:
                with open(filepath, 'w') as f:
                    f.write(content)
                self.stats['refactored'].append(filepath)
                return True
            
            return False
        
        except Exception as e:
            self.stats['errors'].append(f"{filepath}: {e}")
            return False

    def refactor_all_prompts(self) -> None:
        """Refactor all prompts in directory"""
        prompts = [
            f for f in os.listdir(self.PROMPTS_DIR)
            if f.endswith('.prompt.md')
        ]
        
        print("🔧 CORTEX PROMPT ALIGNMENT ENGINE")
        print("=" * 80)
        print(f"\n📋 Discovered {len(prompts)} prompt files:")
        for p in sorted(prompts):
            print(f"  • {p}")
        
        print("\n" + "=" * 80)
        print("🔄 REFACTORING IN PROGRESS...\n")
        
        for prompt in sorted(prompts):
            filepath = os.path.join(self.PROMPTS_DIR, prompt)
            print(f"Processing: {prompt}")
            
            if self.refactor_prompt(filepath):
                print(f"  ✅ Refactored successfully")
            else:
                print(f"  ✓ Already aligned")
        
        self._report_results()

    def _report_results(self) -> None:
        """Print refactoring results"""
        print("\n" + "=" * 80)
        print("✅ REFACTORING COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 RESULTS:")
        print(f"  • Prompts refactored: {len(self.stats['refactored'])}")
        print(f"  • Sync calls consolidated: {self.stats['sync_consolidations']}")
        print(f"  • Regression checks standardized: {self.stats['regression_standardizations']}")
        print(f"  • Orchestrator delegations added: {self.stats['delegation_additions']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in self.stats['errors']:
                print(f"  • {error}")
        
        if self.stats['refactored']:
            print(f"\n📝 Modified files:")
            for f in self.stats['refactored']:
                print(f"  ✅ {f}")

def main():
    refactorer = PromptRefactorer()
    
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    refactorer.refactor_all_prompts()

if __name__ == '__main__':
    main()
