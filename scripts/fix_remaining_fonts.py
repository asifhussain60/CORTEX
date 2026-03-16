#!/usr/bin/env python3
"""Fix remaining font-size violations — Phase 109.3 pass 2."""
import re
from pathlib import Path

docs = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
files = list(docs.rglob('*.html'))
exclude = {'glass-samples.html'}
files = [f for f in files if f.name not in exclude]

fixes = 0
for path in files:
    content = path.read_text()
    original = content

    # text-[10px] → text-[11px] (absolute badge floor = 11px = 0.6875rem)
    content = content.replace('text-[10px]', 'text-[11px]')

    # Breadcrumb separator: .cortex-bc-sep font-size: 0.7rem → 0.6875rem
    content = re.sub(
        r'(\.cortex-bc-sep\s*\{[^}]*font-size:\s*)0\.7rem',
        r'\g<1>0.6875rem', content
    )
    # Breadcrumb separator inline: font-size: 0.7rem; line-height: 1; flex-shrink
    content = re.sub(
        r'(cortex-bc-sep[^;]*?font-size:\s*)0\.7rem',
        r'\g<1>0.6875rem', content
    )

    # Breadcrumb current badge: 0.75rem → 0.875rem (visible label text)
    content = re.sub(
        r'(\.cortex-bc-current[^}]*font-size:\s*)0\.75rem',
        r'\g<1>0.875rem', content
    )
    content = re.sub(
        r'(cortex-bc-current[^;]*?font-size:\s*)0\.75rem',
        r'\g<1>0.875rem', content
    )

    # .concept-number (mono ordinal tag): 0.75rem → 0.8125rem (code floor)
    content = re.sub(
        r'(\.concept-number[^}]*font-size:\s*)0\.75rem',
        r'\g<1>0.8125rem', content
    )

    # .primitive-tag (mono tag): 0.7rem → 0.875rem
    content = re.sub(
        r'(\.primitive-tag[^}]*font-size:\s*)0\.7rem',
        r'\g<1>0.875rem', content, flags=re.DOTALL
    )

    # .cn-label node label: 0.75rem → 0.875rem
    content = re.sub(
        r'(\.cn-label\s*\{[^}]*font-size:\s*)0\.75rem',
        r'\g<1>0.875rem', content
    )

    # Global pass: any remaining font-size: 0.7rem → 0.875rem
    content = re.sub(r'font-size:\s*0\.7rem\b', 'font-size: 0.875rem', content)

    # Global pass: any remaining font-size: 0.75rem outside of code context
    # 0.75rem in code context (.cmd-example, .code-block) already fixed to 0.8125rem
    # Any remaining 0.75rem (likely in text labels) → 0.875rem
    # BUT: .step-num uses 0.6875rem (already done), inline code → 0.8125rem
    # Safe conservative: 0.75rem → 0.875rem for all remaining text uses
    content = re.sub(
        r'(font-size:\s*)0\.75rem(?!.*?(?:code|mono|font-family.*?Mono))',
        r'\g<1>0.875rem', content
    )

    if content != original:
        path.write_text(content)
        fixes += 1
        print(f'Fixed: {path.relative_to(docs)}')

print(f'\nTotal files updated: {fixes}')
