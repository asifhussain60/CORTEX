#!/usr/bin/env python3
"""
CORTEX Architecture Audit: Response Template System Review

Analyzes:
1. All orchestrators for template inheritance compliance
2. GitHub Copilot Chat feedback in sessions
3. Response format standards compliance
4. Header generation patterns
5. Gaps in template system integration

Author: GitHub Copilot (CORTEX Architect Mode)
Date: 2026-02-10
Authority: cortex-architect.prompt.md v15.3
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# ============================================================================
# STAGE 1: ORCHESTRATOR DISCOVERY & ANALYSIS
# ============================================================================

def find_orchestrator_classes() -> Dict[str, Path]:
    """Find all orchestrator classes in codebase."""
    orchestrators = {}
    cortex_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex")
    
    for py_file in cortex_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for class definitions containing "Orchestrator"
                pattern = r'class\s+(\w*Orchestrator\w*)\s*(?:\(|:)'
                matches = re.findall(pattern, content)
                for match in matches:
                    orchestrators[match] = py_file
        except Exception as e:
            pass
    
    return orchestrators

def analyze_template_usage(orchestrator_name: str, file_path: Path) -> Dict:
    """Analyze template usage in a specific orchestrator."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {'error': 'Could not read file'}
    
    analysis = {
        'name': orchestrator_name,
        'file': str(file_path),
        'template_inheritance': False,
        'base_response_template': False,
        'orchestrator_templates': False,
        'has_header_method': False,
        'has_compose_method': False,
        'has_section_methods': False,
        'copilot_chat_ready': False,
        'response_format_violations': [],
        'gaps': [],
    }
    
    # Check inheritance patterns
    if 'BaseResponseTemplate' in content or 'base_response_template' in content.lower():
        analysis['base_response_template'] = True
        analysis['template_inheritance'] = True
    
    if 'OrchestratorTemplates' in content or 'orchestrator_templates' in content.lower():
        analysis['orchestrator_templates'] = True
    
    # Check method presence
    if re.search(r'def\s+header\s*\(', content):
        analysis['has_header_method'] = True
    
    if re.search(r'def\s+compose\s*\(', content):
        analysis['has_compose_method'] = True
    
    if re.search(r'def\s+section\s*\(|def\s+subsection\s*\(|def\s+challenge_box\s*\(', content):
        analysis['has_section_methods'] = True
    
    # Check for GitHub Copilot Chat patterns
    if 'CopilotChat' in content or '## 🧠 CORTEX' in content or '## 🏛️ CORTEX' in content:
        analysis['copilot_chat_ready'] = True
    
    # Identify gaps
    if not analysis['template_inheritance']:
        analysis['gaps'].append('No template inheritance from BaseResponseTemplate')
    
    if not analysis['has_compose_method']:
        analysis['gaps'].append('Missing compose() method for response generation')
    
    if not analysis['has_header_method']:
        analysis['gaps'].append('Missing header() method for CORTEX header generation')
    
    if analysis['has_compose_method'] and not analysis['copilot_chat_ready']:
        analysis['gaps'].append('compose() exists but no GitHub Copilot Chat readiness')
    
    # Check for response format compliance
    if re.search(r'print\s*\(\s*["\'].*proceed', content, re.IGNORECASE):
        analysis['response_format_violations'].append('Narration in silent mode ("proceed" prompt)')
    
    if re.search(r'input\s*\(\s*["\'].*proceed', content, re.IGNORECASE):
        analysis['response_format_violations'].append('User input request for "proceed" confirmation')
    
    if re.search(r'print\s*\(\s*["\'].*Let me|Here\'s what|I will|I\'ll', content):
        analysis['response_format_violations'].append('Narration pattern detected (violates silent mode)')
    
    return analysis

def categorize_orchestrators(orchestrators: Dict[str, Path]) -> Dict[str, List[str]]:
    """Categorize orchestrators by type."""
    categories = {
        'core': [],
        'domain': [],
        'support': [],
        'response': [],
        'other': []
    }
    
    for name, path in orchestrators.items():
        path_str = str(path)
        if 'core' in path_str:
            categories['core'].append(name)
        elif 'domain' in path_str:
            categories['domain'].append(name)
        elif 'support' in path_str:
            categories['support'].append(name)
        elif 'response' in path_str:
            categories['response'].append(name)
        else:
            categories['other'].append(name)
    
    return categories

# ============================================================================
# STAGE 2: TEMPLATE SYSTEM AUDIT
# ============================================================================

def audit_template_files() -> Dict:
    """Audit response template system files."""
    audit = {
        'template_files': {},
        'missing_files': [],
        'gaps': [],
    }
    
    expected_files = [
        'cortex/orchestrators/response/base_response_template.py',
        'cortex/orchestrators/response/orchestrator_templates.py',
        'cortex/orchestrators/response/copilot_chat_templates.py',
        'cortex/orchestrators/response/unified_response_composer.py',
        'cortex/orchestrators/response/chat_response_policy.py',
        '.github/prompts/response-format-standards.md',
        '.github/prompts/cortex-architect-response-template.md',
    ]
    
    base_path = Path('/Users/asifhussain/PROJECTS/CORTEX')
    
    for file_path_str in expected_files:
        full_path = base_path / file_path_str
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    audit['template_files'][file_path_str] = {
                        'exists': True,
                        'size': len(content),
                        'lines': content.count('\n'),
                    }
            except:
                audit['template_files'][file_path_str] = {'exists': True, 'error': 'Could not read'}
        else:
            audit['missing_files'].append(file_path_str)
    
    if audit['missing_files']:
        audit['gaps'].append(f"Missing template files: {len(audit['missing_files'])}")
    
    return audit

# ============================================================================
# STAGE 3: FEEDBACK ANALYSIS
# ============================================================================

def analyze_feedback_patterns() -> Dict:
    """Analyze GitHub Copilot Chat feedback patterns in codebase."""
    analysis = {
        'feedback_locations': [],
        'patterns_found': defaultdict(int),
        'issues': [],
    }
    
    base_path = Path('/Users/asifhussain/PROJECTS/CORTEX')
    
    # Search for feedback-related code
    feedback_patterns = {
        'session_markers': r'# AC_START|# AC_COMPLETE|## 🧠 CORTEX|## 🏛️ CORTEX',
        'response_headers': r'Author:|Orchestrator:|Phase:',
        'chat_templates': r'CopilotChat|copilot_chat',
        'feedback_agent': r'FeedbackAgent|feedback_agent',
        'response_format': r'ResponseFormat|response.*format',
    }
    
    for pattern_name, pattern in feedback_patterns.items():
        for py_file in base_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    if matches > 0:
                        analysis['patterns_found'][pattern_name] += matches
            except:
                pass
    
    return analysis

# ============================================================================
# STAGE 4: REPORT GENERATION
# ============================================================================

def generate_gap_report(orchestrators: Dict, analyses: List, template_audit: Dict, feedback_analysis: Dict):
    """Generate comprehensive gap report."""
    
    print("\n" + "="*80)
    print("🏛️  CORTEX ARCHITECTURE HOLISTIC REVIEW - RESPONSE TEMPLATE SYSTEM")
    print("="*80)
    print(f"\nDate: 2026-02-10")
    print(f"Authority: cortex-architect.prompt.md v15.3")
    print(f"Mode: ARCHITECT - Holistic Template System Audit\n")
    
    # ========================================================================
    # SECTION 1: ORCHESTRATOR COMPLIANCE SUMMARY
    # ========================================================================
    print("\n" + "━"*80)
    print("📋 SECTION 1: ORCHESTRATOR COMPLIANCE ANALYSIS")
    print("━"*80)
    
    total = len(orchestrators)
    with_inheritance = sum(1 for a in analyses if a['template_inheritance'])
    with_compose = sum(1 for a in analyses if a['has_compose_method'])
    with_headers = sum(1 for a in analyses if a['has_header_method'])
    copilot_ready = sum(1 for a in analyses if a['copilot_chat_ready'])
    
    print(f"\n📊 Coverage Statistics:")
    print(f"  Total Orchestrators: {total}")
    print(f"  ✅ With Template Inheritance: {with_inheritance}/{total} ({100*with_inheritance/total:.1f}%)")
    print(f"  ✅ With compose() Method: {with_compose}/{total} ({100*with_compose/total:.1f}%)")
    print(f"  ✅ With header() Method: {with_headers}/{total} ({100*with_headers/total:.1f}%)")
    print(f"  ✅ Copilot Chat Ready: {copilot_ready}/{total} ({100*copilot_ready/total:.1f}%)")
    
    # ========================================================================
    # SECTION 2: TEMPLATE SYSTEM AUDIT
    # ========================================================================
    print("\n" + "━"*80)
    print("🔍 SECTION 2: RESPONSE TEMPLATE SYSTEM STATUS")
    print("━"*80)
    
    print(f"\n📂 Template Infrastructure:")
    for file, info in template_audit['template_files'].items():
        if info.get('exists'):
            status = "✅" if 'error' not in info else "⚠️"
            size_kb = info.get('size', 0) / 1024
            print(f"  {status} {file} ({size_kb:.1f}KB, {info.get('lines', 0)} lines)")
    
    if template_audit['missing_files']:
        print(f"\n🔴 Missing Files ({len(template_audit['missing_files'])}):")
        for file in template_audit['missing_files']:
            print(f"  ❌ {file}")
    
    # ========================================================================
    # SECTION 3: GAP IDENTIFICATION
    # ========================================================================
    print("\n" + "━"*80)
    print("🚨 SECTION 3: IDENTIFIED GAPS & VIOLATIONS")
    print("━"*80)
    
    # Collect all gaps
    all_gaps = defaultdict(list)
    all_violations = defaultdict(list)
    
    for analysis in analyses:
        for gap in analysis['gaps']:
            all_gaps[gap].append(analysis['name'])
        for violation in analysis['response_format_violations']:
            all_violations[violation].append(analysis['name'])
    
    if all_gaps:
        print(f"\n🔴 GAPS ({len(all_gaps)}):")
        for gap, orchestrators_list in sorted(all_gaps.items(), key=lambda x: -len(x[1])):
            count = len(orchestrators_list)
            print(f"\n  • {gap}")
            print(f"    Affects: {count} orchestrators")
            if count <= 5:
                for orch in orchestrators_list[:5]:
                    print(f"      - {orch}")
            else:
                for orch in orchestrators_list[:3]:
                    print(f"      - {orch}")
                print(f"      ... and {count - 3} more")
    
    if all_violations:
        print(f"\n🔴 VIOLATIONS ({len(all_violations)}):")
        for violation, orchestrators_list in sorted(all_violations.items(), key=lambda x: -len(x[1])):
            count = len(orchestrators_list)
            print(f"\n  • {violation} (CORE-049)")
            print(f"    Affected: {count} orchestrators")
    
    # ========================================================================
    # SECTION 4: CRITICAL FINDINGS
    # ========================================================================
    print("\n" + "━"*80)
    print("⚠️  SECTION 4: CRITICAL FINDINGS")
    print("━"*80)
    
    print(f"\n🎯 Key Issues:")
    print(f"\n1. 🏗️  TEMPLATE INHERITANCE GAPS")
    print(f"   - {total - with_inheritance} orchestrators lack BaseResponseTemplate inheritance")
    print(f"   - Gap: {100 * (total - with_inheritance) / total:.1f}% of orchestrators")
    print(f"   - Impact: Inconsistent response headers, violates CORE-029")
    
    print(f"\n2. 📝 COMPOSE METHOD COMPLIANCE")
    print(f"   - {total - with_compose} orchestrators missing compose() method")
    print(f"   - Gap: {100 * (total - with_compose) / total:.1f}%")
    print(f"   - Impact: Cannot generate standardized responses")
    
    print(f"\n3. 💬 GITHUB COPILOT CHAT READINESS")
    print(f"   - {total - copilot_ready} orchestrators not Copilot Chat ready")
    print(f"   - Gap: {100 * (total - copilot_ready) / total:.1f}%")
    print(f"   - Impact: Poor Chat UI experience, formatting issues")
    
    print(f"\n4. 🔒 SILENT MODE VIOLATIONS")
    print(f"   - {len(all_violations)} violation types detected")
    print(f"   - Status: CRITICAL - Violates CORE-049 (Silent Autonomous Execution)")
    
    # ========================================================================
    # SECTION 5: NEXT STEPS & RECOMMENDATIONS
    # ========================================================================
    print("\n" + "━"*80)
    print("✅ SECTION 5: REMEDIATION ROADMAP")
    print("━"*80)
    
    print(f"""
🎯 IMMEDIATE ACTIONS (Phase 50 - CRITICAL):

1️⃣  ENFORCE TEMPLATE INHERITANCE
    - Update {total - with_inheritance} orchestrators to inherit from BaseResponseTemplate
    - Priority: ALL orchestrators must have unified header generation
    - Effort: 2-3 hours per 10 orchestrators
    
2️⃣  IMPLEMENT COMPOSE METHODS
    - Add compose() to {total - with_compose} orchestrators
    - Pattern: Use orchestrator_templates.py as reference
    - Effort: 1-2 hours per orchestrator
    
3️⃣  GITHUB COPILOT CHAT MIGRATION
    - Integrate CopilotChatTemplateEngine for chat responses
    - Review: Response format standards compliance
    - Effort: 4-6 hours total for all orchestrators
    
4️⃣  ELIMINATE SILENT MODE VIOLATIONS
    - Remove narration patterns ("Let me...", "I'll...", etc.)
    - Remove input() calls for "proceed" confirmation
    - Enforce: Silent execution by default
    - Effort: 1-2 hours

📊 COMPLIANCE TARGETS:
    ✅ Template Inheritance: 100% (currently {100*with_inheritance/total:.1f}%)
    ✅ Compose Methods: 100% (currently {100*with_compose/total:.1f}%)
    ✅ Copilot Chat Ready: 100% (currently {100*copilot_ready/total:.1f}%)
    ✅ Silent Mode Violations: 0 (currently {len(all_violations)})
""")
    
    print("\n" + "━"*80)
    print(f"Report Generated: 2026-02-10 | Mode: ARCHITECT | Authority: cortex-architect.prompt.md v15.3")
    print("━"*80 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n🔧 Starting CORTEX Architecture Audit...\n")
    
    # Stage 1: Discover orchestrators
    print("📍 Stage 1: Discovering orchestrators...")
    orchestrators = find_orchestrator_classes()
    print(f"   Found {len(orchestrators)} orchestrator classes\n")
    
    # Analyze each
    print("📍 Stage 2: Analyzing template compliance...")
    analyses = []
    for name, path in orchestrators.items():
        analysis = analyze_template_usage(name, path)
        analyses.append(analysis)
    print(f"   Completed analysis for {len(analyses)} orchestrators\n")
    
    # Stage 2: Template audit
    print("📍 Stage 3: Auditing template infrastructure...")
    template_audit = audit_template_files()
    print(f"   Found {len(template_audit['template_files'])} template files\n")
    
    # Stage 3: Feedback analysis
    print("📍 Stage 4: Analyzing feedback patterns...")
    feedback_analysis = analyze_feedback_patterns()
    print(f"   Completed feedback analysis\n")
    
    # Generate report
    print("📍 Stage 5: Generating comprehensive report...\n")
    generate_gap_report(orchestrators, analyses, template_audit, feedback_analysis)
    
    # Optional: Print detailed orchestrator list
    print("\n" + "="*80)
    print("📑 APPENDIX: DETAILED ORCHESTRATOR STATUS")
    print("="*80)
    
    categories = categorize_orchestrators(orchestrators)
    for category, names in categories.items():
        if names:
            print(f"\n🔹 {category.upper()} ({len(names)}):")
            for name in sorted(names)[:10]:
                analysis = next((a for a in analyses if a['name'] == name), {})
                status = "✅" if analysis.get('template_inheritance') else "❌"
                print(f"  {status} {name}")
            if len(names) > 10:
                print(f"  ... and {len(names) - 10} more")
