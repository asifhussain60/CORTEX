"""Token budget analysis for Phase 15."""
import tiktoken
from pathlib import Path

encoding = tiktoken.get_encoding('cl100k_base')

plans = [
    'cortex-lens-v3/00-master-plan.md',
    'admin-dashboard-enhancement/MASTER-PLAN.md',
    'application-modernization/MASTER-PLAN.md',
    'copilot-ast-enhancement/MASTER-PLAN.md',
    'cortex-ux-design/MASTER-PLAN.md',
    'dashboard-consolidation/MASTER-PLAN.md',
    'dashboard-unified-plan/MASTER-PLAN.md',
    'integration-testing/MASTER-PLAN.md',
    'learning-library/MASTER-PLAN.md',
    'orchestration-master-plan/MASTER-PLAN.md',
    'security-threat-modeling/MASTER-PLAN.md'
]

print('Token Budget Analysis - Phase 15.1')
print('=' * 90)
print(f"{'Plan':<40} | {'Total':>6} | {'Header':>6} | {'Cont.':>6} | {'Tracker':>6}")
print('-' * 90)

total_tokens = 0
total_header = 0
total_cont = 0
total_tracker = 0

for plan in plans:
    path = Path(f'cortex-brain/documents/planning/active/{plan}')
    if path.exists():
        content = path.read_text(encoding='utf-8')
        tokens = len(encoding.encode(content))
        lines = content.split('\n')
        
        # Find section boundaries
        header_end = 0
        cont_start = 0
        cont_end = 0
        tracker_start = 0
        tracker_end = 0
        
        for i, line in enumerate(lines):
            if '---' in line and header_end == 0:
                header_end = i
            elif 'Continuation Prompt' in line:
                cont_start = i
            elif cont_start > 0 and cont_end == 0 and '---' in line:
                cont_end = i
            elif 'Visual Progress Tracker' in line:
                tracker_start = i
            elif tracker_start > 0 and tracker_end == 0 and '---' in line:
                tracker_end = i
        
        # Calculate tokens per section
        header = '\n'.join(lines[:header_end])
        cont = '\n'.join(lines[cont_start:cont_end]) if cont_end > cont_start else ""
        tracker = '\n'.join(lines[tracker_start:tracker_end]) if tracker_end > tracker_start else ""
        
        header_tokens = len(encoding.encode(header))
        cont_tokens = len(encoding.encode(cont)) if cont else 0
        tracker_tokens = len(encoding.encode(tracker)) if tracker else 0
        
        plan_name = plan.split('/')[0]
        print(f"{plan_name:<40} | {tokens:6} | {header_tokens:6} | {cont_tokens:6} | {tracker_tokens:6}")
        
        total_tokens += tokens
        total_header += header_tokens
        total_cont += cont_tokens
        total_tracker += tracker_tokens

print('-' * 90)
print(f"{'TOTAL':<40} | {total_tokens:6} | {total_header:6} | {total_cont:6} | {total_tracker:6}")
print(f"{'AVERAGE':<40} | {total_tokens//11:6} | {total_header//11:6} | {total_cont//11:6} | {total_tracker//11:6}")
print()
print('Optimization Targets:')
print(f"  Header: {total_header//11} → {int((total_header//11) * 0.6)} tokens (40% reduction)")
print(f"  Continuation: {total_cont//11} → {int((total_cont//11) * 0.4)} tokens (60% reduction)")
print(f"  Tracker: {total_tracker//11} → {int((total_tracker//11) * 0.55)} tokens (45% reduction)")
print(f"  TOTAL: {total_tokens//11} → {int((total_tokens//11) * 0.6)} tokens (40% reduction target)")
