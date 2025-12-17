#!/usr/bin/env python3
"""
CORTEX Prompt Regeneration Script

⚠️  WARNING: MANUAL ENHANCEMENTS PRESENT
    copilot-instructions.md and CORTEX.prompt.md now contain manually crafted
    orchestrator documentation (Planning System 2.0, ADO Operations) with
    manifest references and compliance requirements.
    
    DO NOT regenerate these files unless you want to lose:
    - ADO orchestrator-level integration
    - Manifest reference documentation
    - DoR/DoD compliance instructions
    - Planning System 2.0 enhancements
    
    Regeneration is only needed for version updates or architecture changes.

Deletes existing Copilot instructions and regenerates them from current codebase state.

Usage:
    python scripts/regenerate_cortex_prompts.py
    python scripts/regenerate_cortex_prompts.py --dry-run
    python scripts/regenerate_cortex_prompts.py --force  (override preservation)

Author: Asif Hussain
Version: 1.1
Date: December 8, 2025
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class PromptRegenerator:
    """Regenerates Copilot prompt files from current CORTEX state."""
    
    def __init__(self, cortex_root: Path, dry_run: bool = False, force: bool = False):
        self.cortex_root = cortex_root
        self.dry_run = dry_run
        self.force = force
        self.github_dir = cortex_root / ".github"
        self.prompts_dir = self.github_dir / "prompts"
        self.copilot_instructions = self.github_dir / "copilot-instructions.md"
        self.cortex_prompt = self.prompts_dir / "CORTEX.prompt.md"
        self.brain_dir = cortex_root / "cortex-brain"
        self.preserve_marker = self.github_dir / ".prompt-preserve"
        self.current_backup_dir = None  # Set during backup phase
        
    def _extract_manual_enhancements(self, filename: str) -> str:
        """Extract manual enhancement sections from backed-up file."""
        if not hasattr(self, 'current_backup_dir') or not self.current_backup_dir:
            # Try to find most recent backup
            backups_dir = self.brain_dir / "backups"
            if backups_dir.exists():
                backup_folders = sorted([d for d in backups_dir.glob("prompts_*")], reverse=True)
                if backup_folders:
                    self.current_backup_dir = backup_folders[0]
        
        if not self.current_backup_dir:
            return ""
        
        backup_file = self.current_backup_dir / filename
        if not backup_file.exists():
            return ""
        
        try:
            content = backup_file.read_text(encoding='utf-8')
            
            # Extract protected content comment block
            if filename == 'copilot-instructions.md':
                # Look for protection comment between # title and **Purpose:**
                if '⚠️  PROTECTED FILE' in content:
                    start_marker = '<!--'
                    end_marker = '-->'
                    start_idx = content.find(start_marker)
                    if start_idx != -1:
                        end_idx = content.find(end_marker, start_idx)
                        if end_idx != -1:
                            protected_block = content[start_idx:end_idx + len(end_marker)]
                            print(f"  📋 Preserved manual enhancements from {filename}")
                            return protected_block
            
            elif filename == 'CORTEX.prompt.md':
                # Look for protection comment in opening HTML comment
                if '⚠️  PROTECTED FILE' in content:
                    # Find the protection comment within the first HTML comment
                    first_comment_end = content.find('-->')
                    if first_comment_end != -1:
                        first_comment = content[:first_comment_end]
                        if '⚠️  PROTECTED FILE' in first_comment:
                            # Extract just the protection notice, not the loader directive
                            lines = first_comment.split('\n')
                            protected_lines = []
                            in_protected = False
                            for line in lines:
                                if '⚠️  PROTECTED FILE' in line:
                                    in_protected = True
                                if in_protected and line.strip() and 'GITHUB COPILOT LOADER' not in line:
                                    protected_lines.append(line)
                            if protected_lines:
                                protected_block = '\n'.join(protected_lines)
                                print(f"  📋 Preserved manual enhancements from {filename}")
                                return protected_block
        
        except Exception as e:
            print(f"  ⚠️  Could not extract enhancements from {filename}: {e}")
        
        return ""
        
    def execute(self) -> Dict[str, any]:
        """Execute full regeneration workflow."""
        print("🔄 CORTEX Prompt Regeneration")
        print("=" * 60)
        
        # Check for preservation marker
        if self.preserve_marker.exists() and not self.force:
            print("\n⚠️  PRESERVATION MODE ACTIVE")
            print("   Prompt files contain manual enhancements and are protected.")
            print("   Use --force to override and regenerate anyway.")
            print("\n   Protected files:")
            print("   - .github/copilot-instructions.md (ADO orchestrator integration)")
            print("   - .github/prompts/CORTEX.prompt.md (manifest references)")
            return {
                'success': True,
                'preserved': True,
                'message': 'Files preserved - manual enhancements protected'
            }
        
        results = {
            'success': True,
            'phases': {},
            'errors': []
        }
        
        # Phase 1: Backup existing files
        print("\n📦 Phase 1: Backing up existing files...")
        backup_result = self._backup_existing_files()
        results['phases']['backup'] = backup_result
        
        # Phase 2: Delete existing files
        print("\n🗑️  Phase 2: Deleting existing files...")
        delete_result = self._delete_existing_files()
        results['phases']['delete'] = delete_result
        
        # Phase 3: Scan CORTEX design
        print("\n🔍 Phase 3: Scanning CORTEX architecture...")
        design_data = self._scan_cortex_design()
        results['phases']['scan'] = {'success': True, 'data': design_data}
        
        # Phase 4: Generate copilot-instructions.md
        print("\n📝 Phase 4: Generating copilot-instructions.md...")
        copilot_result = self._generate_copilot_instructions(design_data)
        results['phases']['copilot_instructions'] = copilot_result
        
        # Phase 5: Generate CORTEX.prompt.md
        print("\n📝 Phase 5: Generating CORTEX.prompt.md...")
        cortex_result = self._generate_cortex_prompt(design_data)
        results['phases']['cortex_prompt'] = cortex_result
        
        # Phase 6: Validate
        print("\n✅ Phase 6: Validating generated files...")
        validation_result = self._validate_generated_files()
        results['phases']['validation'] = validation_result
        
        print("\n" + "=" * 60)
        print("✅ Regeneration complete!")
        
        return results
    
    def _backup_existing_files(self) -> Dict[str, any]:
        """Backup existing prompt files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.brain_dir / "backups" / f"prompts_{timestamp}"
        
        if self.dry_run:
            print(f"  [DRY RUN] Would create backup: {backup_dir}")
            return {'success': True, 'backup_path': str(backup_dir), 'files_backed_up': 2}
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        files_backed_up = 0
        
        if self.copilot_instructions.exists():
            shutil.copy2(self.copilot_instructions, backup_dir / "copilot-instructions.md")
            print(f"  ✅ Backed up: copilot-instructions.md")
            files_backed_up += 1
        
        if self.cortex_prompt.exists():
            shutil.copy2(self.cortex_prompt, backup_dir / "CORTEX.prompt.md")
            print(f"  ✅ Backed up: CORTEX.prompt.md")
            files_backed_up += 1
        
        # Store backup path for later reference
        self.current_backup_dir = backup_dir
        
        return {
            'success': True,
            'backup_path': str(backup_dir),
            'files_backed_up': files_backed_up
        }
    
    def _delete_existing_files(self) -> Dict[str, any]:
        """Delete existing prompt files."""
        files_deleted = 0
        
        if self.dry_run:
            print(f"  [DRY RUN] Would delete: {self.copilot_instructions}")
            print(f"  [DRY RUN] Would delete: {self.cortex_prompt}")
            return {'success': True, 'files_deleted': 2}
        
        if self.copilot_instructions.exists():
            self.copilot_instructions.unlink()
            print(f"  ✅ Deleted: copilot-instructions.md")
            files_deleted += 1
        
        if self.cortex_prompt.exists():
            self.cortex_prompt.unlink()
            print(f"  ✅ Deleted: CORTEX.prompt.md")
            files_deleted += 1
        
        return {'success': True, 'files_deleted': files_deleted}
    
    def _scan_cortex_design(self) -> Dict[str, any]:
        """Scan current CORTEX architecture and extract key information."""
        print("  Scanning codebase...")
        
        design_data = {
            'version': self._get_version(),
            'brain_tiers': self._scan_brain_tiers(),
            'agents': self._scan_agents(),
            'orchestrators': self._scan_orchestrators(),
            'operations': self._scan_operations(),
            'workflows': self._scan_workflows(),
            'protection_rules': self._scan_protection_rules(),
            'response_templates': self._scan_response_templates(),
        }
        
        print(f"  ✅ Found: {design_data['version']}")
        print(f"  ✅ Agents: {len(design_data['agents'])}")
        print(f"  ✅ Orchestrators: {len(design_data['orchestrators'])}")
        print(f"  ✅ Operations: {len(design_data['operations'])}")
        print(f"  ✅ Protection Rules: {len(design_data['protection_rules'])}")
        
        return design_data
    
    def _get_version(self) -> str:
        """Get current CORTEX version."""
        version_file = self.cortex_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip().split()[0]
        return "3.8.1"
    
    def _scan_brain_tiers(self) -> List[str]:
        """Scan brain tier directories."""
        brain_src = self.cortex_root / "src"
        tiers = []
        for tier in ["tier0", "tier1", "tier2", "tier3"]:
            if (brain_src / tier).exists():
                tiers.append(tier)
        return tiers
    
    def _scan_agents(self) -> List[Dict[str, str]]:
        """Scan agent files."""
        agents_dir = self.cortex_root / "src" / "cortex_agents"
        agents = []
        
        if agents_dir.exists():
            for subdir in ["strategic", "tactical", "operational"]:
                subdir_path = agents_dir / subdir
                if subdir_path.exists():
                    for file in subdir_path.glob("*_agent.py"):
                        agent_name = file.stem.replace("_agent", "").replace("_", " ").title()
                        agents.append({'name': agent_name, 'type': subdir})
        
        return agents
    
    def _scan_orchestrators(self) -> List[str]:
        """Scan orchestrator files."""
        orchestrators_dir = self.cortex_root / "src" / "orchestrators"
        orchestrators = []
        
        if orchestrators_dir.exists():
            for file in orchestrators_dir.glob("*_orchestrator.py"):
                orchestrators.append(file.stem.replace("_orchestrator", ""))
        
        return orchestrators
    
    def _scan_operations(self) -> List[str]:
        """Scan operations from YAML config."""
        operations_yaml = self.cortex_root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
        operations = []
        
        if operations_yaml.exists():
            with open(operations_yaml, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:
                    operations = list(config.keys())
        
        return operations
    
    def _scan_workflows(self) -> List[str]:
        """Identify key workflows."""
        workflows = [
            "Planning System 2.0",
            "TDD Mastery",
            "Dashboard Launcher",
            "System Maintenance",
            "Cleanup & Organization",
            "Architectural Review",
            "Progress Monitoring"
        ]
        return workflows
    
    def _scan_protection_rules(self) -> List[str]:
        """Scan SKULL protection rules."""
        rules = [
            "TDD_ENFORCEMENT",
            "RED_PHASE_VALIDATION",
            "TDD_TEST_FILE_VALIDATION",
            "TDD_EMPTY_TEST_DETECTION",
            "GIT_ISOLATION_ENFORCEMENT",
            "TEST_LOCATION_SEPARATION"
        ]
        return rules
    
    def _scan_response_templates(self) -> int:
        """Count response templates."""
        return 62  # Current count
    
    def _generate_copilot_instructions(self, design_data: Dict[str, any]) -> Dict[str, any]:
        """Generate lean copilot-instructions.md (entry point)."""
        
        # Check for manual enhancements in backup
        manual_enhancements = self._extract_manual_enhancements('copilot-instructions.md')
        
        content = f'''# GitHub Copilot Instructions for CORTEX

{manual_enhancements}

**Purpose:** AI Assistant enhancement with long-term memory, context awareness, and strategic planning

**Version:** {design_data['version']} | **Updated:** {datetime.now().strftime("%B %d, %Y")}

---

## ⚠️ CRITICAL: Parse User Request FIRST

**Problem:** Meta-directives incorrectly treated as user's request.

**Solution:** Extract actual request BEFORE intent classification.

**Meta-Directive Patterns (REMOVE):**
```regex
^Follow instructions in .+?[;.\\n]
^Use .+?\\.prompt\\.md[;.\\n]
^Reference file:///.+?[;.\\n]
```

**Example:**
- INPUT: `Follow instructions in CORTEX.prompt.md. Should we run align?`
- FILTERED: `Should we run align?`
- ROUTE TO: Strategic planning agent

---

## 🎯 Entry Point

**Load:** `.github/prompts/CORTEX.prompt.md` + `cortex-brain/response-templates.yaml`

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 📋 MANDATORY RESPONSE FORMAT (v3.0)

ALL responses MUST use this 5-part structure:

```markdown
## 🧠 CORTEX {{Title}}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{{what you understood + scope/boundaries}}

### ⚡ Approach & Considerations
{{actual challenge OR "No significant challenges"}}

### 💬 Response
{{your response - NO code unless requested}}

### 📊 Impact & Changes
{{what changed - files, metrics, outcomes}}

### 🔍 Next Steps
{{numbered list OR checkboxes for complex work}}
```

**Rules:**
- ✅ H2 with 🧠, H3 with emojis
- ✅ Author line + one `---` separator
- ✅ Approach: Real challenge OR "No significant challenges"
- ❌ NO extra separators, NO code unless requested

---

## 🚀 Key Workflows

**Planning System 2.0**
- Commands: `plan [feature]`, `execute all phases autonomously`
- AUTO-COMPLEXITY: HIGH→incremental, MEDIUM→conditional, LOW→skeleton
- TDD auto-included in all plans

**TDD Mastery**
- Commands: `start tdd`, `run tests`
- RED→GREEN→REFACTOR mandatory
- Per-layer coverage validation

**System Maintenance**
- Commands: `system maintenance`
- 5 phases: healthcheck → align → cleanup → optimize → healthcheck

**Dashboard Launcher**
- Commands: `load dashboard`, `dashboard`
- HTTP server (port 8080-8089), auto-open browser

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{{category}}/{{filename}}.md`

**Categories:** `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

**4-Tier Brain:**
```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO)
├── tier2/  # Knowledge graph
├── tier3/  # Dev context
└── response-templates.yaml
```

**Code:**
```
src/
├── tier0/, tier1/, tier2/, tier3/
├── cortex_agents/      # {len(design_data['agents'])} agents
├── orchestrators/      # {len(design_data['orchestrators'])} workflows
└── response_templates/
```

**Brain Protection (SKULL):**
- TDD_ENFORCEMENT: RED→GREEN→REFACTOR mandatory
- RED_PHASE_VALIDATION: Tests must fail first
- GIT_ISOLATION_ENFORCEMENT: CORTEX code never in user repos
- TEST_LOCATION_SEPARATION: App tests in user repo, CORTEX in `tests/`

---

## 🛠️ Developer Workflows

**Tests:**
```bash
pytest tests/                    # CORTEX internal only
pytest --cov=src tests/
```

**Setup:**
```bash
python --version                 # Requires 3.8+
pip install -r requirements.txt
python -m src.main
```

**Configuration:** Edit `cortex.config.json` with machine-specific paths

---

## 🗺️ Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Complete instructions |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules |
| `cortex-brain/response-templates.yaml` | {design_data['response_templates']} templates |
| `cortex.config.json` | Machine settings |

---

## 🚨 Common Pitfalls

1. **Don't bypass Tier 0 instincts** - Brain Protector enforces with evidence
2. **Don't skip RED phase** - Tests must fail before implementation
3. **Don't create root-level docs** - All in `cortex-brain/documents/`
4. **Don't mix CORTEX/user code** - Git isolation enforced
5. **Don't bloat responses** - Every section must add value

---

**Quick Start:** Say "help" to see available operations.

**Anti-Bloat:** This file MUST stay under 350 lines.
'''
        
        if self.dry_run:
            print(f"  [DRY RUN] Would generate: {self.copilot_instructions}")
            return {'success': True, 'size': len(content)}
        
        with open(self.copilot_instructions, 'w', encoding='utf-8') as f:
            f.write(content)
        
        lines = len(content.split('\n'))
        print(f"  ✅ Generated: copilot-instructions.md ({lines} lines)")
        
        return {'success': True, 'file_path': str(self.copilot_instructions), 'size': len(content)}
    
    def _generate_cortex_prompt(self, design_data: Dict[str, any]) -> Dict[str, any]:
        """Generate comprehensive CORTEX.prompt.md."""
        
        # Check for manual enhancements in backup
        manual_enhancements = self._extract_manual_enhancements('CORTEX.prompt.md')
        
        content = f'''<!--
GITHUB COPILOT LOADER DIRECTIVE:
Load this ENTIRE file into context. Apply mandatory 5-part response format.
DO NOT provide generic introduction - respond to user's ACTUAL request.

{manual_enhancements}
-->

# 🎯 CORTEX Universal Entry Point

**Version:** {design_data['version']} | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**

---

## ⚠️ CRITICAL: Parse User Request FIRST

**Problem:** Meta-directives incorrectly treated as user's request.

**Solution:** Extract actual request BEFORE intent classification.

**Meta-Directive Patterns to remove:**
- Starts with "Follow instructions in"
- Starts with "Use [filename].prompt.md"
- Starts with "Reference file:///"

**Example:**
- INPUT: `Follow instructions in CORTEX.prompt.md. Should we run align?`
- FILTERED: `Should we run align?`
- ROUTE TO: Strategic planning agent

---

## 📋 MANDATORY RESPONSE FORMAT (v3.0)

ALL responses MUST use this 5-part structure:

```markdown
## 🧠 CORTEX {{Title}}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{{what you understood + boundaries}}

### ⚡ Approach & Considerations
{{actual challenge OR "No significant challenges"}}

### 💬 Response
{{your response - NO code unless requested}}

### 📊 Impact & Changes
{{what changed - files, metrics, outcomes}}

### 🔍 Next Steps
{{numbered list OR checkboxes for complex work}}
```

**Rules:**
- ✅ H2 with 🧠, H3 with emojis: 🎯 ⚡ 💬 📊 🔍
- ✅ Author line + one `---` separator
- ✅ Approach: Real challenge OR "No significant challenges"
- ❌ NO extra separators, NO code unless requested

**Format Exception:** Introduction/business value templates use narrative format.

---

## 🚀 Core Workflows

### Professional Introductions
- **Commands:** `introduce yourself`, `introduce cortex`
- **Variants:** Add "to leadership", "to product", "to engineers"
- **Features:** 5-section format, evidence-based claims

### Planning System 2.0
- **Commands:** `plan [feature]`, `plan ado`, `execute all phases autonomously`
- **AUTO-DETECTION:** Complexity-based routing (HIGH→incremental, LOW→skeleton)
- **Triggers:** Security, auth, migrations, APIs auto-route to incremental
- **TDD:** Auto-included in all plans

### TDD Mastery
- **Commands:** `start tdd`, `run tests`
- **Features:** RED→GREEN→REFACTOR, per-layer coverage, empty test detection
- **Guide:** `cortex-brain/brain-protection-rules.yaml` (TDD_ENFORCEMENT)

### Dashboard Launcher
- **Commands:** `load dashboard`, `dashboard`
- **Features:** HTTP server (8080-8089), auto-open browser, CORS

### System Maintenance
- **Commands:** `system maintenance`, `maintain system`
- **Phases:** Pre-healthcheck → align → cleanup → optimize → post-healthcheck

### Architectural Review
- **Commands:** `review`, `review architecture`
- **Features:** 6-phase analysis (0-100 scoring), git protection

### System Operations
- **Commands:** `align`, `optimize`, `feedback`, `help`
- **Admin-only:** `deploy`

---

## 📋 Quick Command Reference

| Command | Description | Context |
|---------|-------------|---------|
| `plan [feature]` | Interactive planning (auto-TDD) | All |
| `execute all phases autonomously` | Run plan end-to-end | All |
| `start tdd` | Begin TDD workflow | All |
| `review` | Architectural review | All |
| `load dashboard` | Launch dashboard | All |
| `system maintenance` | 5-phase maintenance | Admin |
| `align` | System alignment | Admin/User |
| `optimize` | CORTEX optimization | Admin/User |
| `deploy` | Deploy to publish | Admin only |
| `help` | Show commands | All |

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{{category}}/{{filename}}.md`

**Categories:**
- `reports/` - Status, test results, validation
- `analysis/` - Code/architecture analysis
- `summaries/` - Project/progress summaries
- `investigations/` - Bug investigations
- `planning/` - Feature plans, ADO items
- `implementation-guides/` - How-to guides

**Pre-Flight:** Determine type → Select category → Construct path → Create

---

## 🏗️ Architecture Overview

**4-Tier Brain:**
```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO, <100ms)
├── tier2/  # Knowledge graph (pattern learning)
├── tier3/  # Dev context (metrics, hotspots)
└── response-templates.yaml  # {design_data['response_templates']} templates
```

**Code Structure:**
```
src/
├── tier0/, tier1/, tier2/, tier3/  # Brain tiers
├── cortex_agents/                   # {len(design_data['agents'])} specialist agents
├── orchestrators/                   # {len(design_data['orchestrators'])} workflows
└── response_templates/              # Template rendering
```

**Brain Protection (SKULL):** `cortex-brain/brain-protection-rules.yaml`
- **TDD_ENFORCEMENT:** RED→GREEN→REFACTOR mandatory
- **RED_PHASE_VALIDATION:** Tests must fail before implementation
- **TDD_TEST_FILE_VALIDATION:** All production code must have test files
- **TDD_EMPTY_TEST_DETECTION:** No placeholder/empty tests
- **GIT_ISOLATION_ENFORCEMENT:** CORTEX code never in user repos
- **TEST_LOCATION_SEPARATION:** App tests in user repo, CORTEX in `tests/`

**Response Templates:** Auto-select by intent from `cortex-brain/response-templates.yaml`

---

## 🚀 Quick Start

Say **"help"** in Copilot Chat to see all operations.

**NO Python execution needed** - Template-based response system provides instant responses.

**Developer Setup:**

```bash
pytest tests/                    # CORTEX internal only
pip install -r requirements.txt
python -m src.main
```

**Configuration:** Edit `cortex.config.json` with machine-specific paths

---

## 🚨 Common Pitfalls

1. **Don't bypass Tier 0 instincts** - Brain Protector enforces with evidence
2. **Don't skip RED phase** - Tests must fail before implementation
3. **Don't create root-level docs** - All in `cortex-brain/documents/`
4. **Don't mix CORTEX/user code** - Git isolation enforced
5. **Don't bloat responses** - Every section must add value
6. **Don't treat meta-directives as requests** - Filter them FIRST

---

## 📚 Additional Resources

**Module Guides:**
- `modules/planning-orchestrator-guide.md` - Planning System 2.0
- `modules/tdd-mastery-guide.md` - TDD workflow
- `modules/response-format-v3.md` - Response format spec

**Implementation Guides:**
- `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`
- `cortex-brain/documents/implementation-guides/system-maintenance-orchestrator.md`

**Core Documentation:**
- `cortex-brain/brain-protection-rules.yaml` - Complete SKULL rules
- `cortex-brain/response-templates.yaml` - All response templates
- `src/tier0/README.md` - Governance rules
- `src/cortex_agents/README.md` - Agent framework

---

**Quick Start:** Say "help" in Copilot Chat to see available operations.

**Anti-Bloat:** This file MUST stay under 600 lines. Remove anything that doesn't directly impact Copilot behavior, command execution, or response quality.
'''
        
        if self.dry_run:
            print(f"  [DRY RUN] Would generate: {self.cortex_prompt}")
            return {'success': True, 'size': len(content)}
        
        # Ensure prompts directory exists
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.cortex_prompt, 'w', encoding='utf-8') as f:
            f.write(content)
        
        lines = len(content.split('\n'))
        print(f"  ✅ Generated: CORTEX.prompt.md ({lines} lines)")
        
        return {'success': True, 'file_path': str(self.cortex_prompt), 'size': len(content)}
    
    def _validate_generated_files(self) -> Dict[str, any]:
        """Validate generated files meet requirements."""
        issues = []
        
        if self.dry_run:
            print("  [DRY RUN] Would validate generated files")
            return {'success': True, 'issues': []}
        
        # Check copilot-instructions.md
        if not self.copilot_instructions.exists():
            issues.append("copilot-instructions.md not created")
        else:
            content = self.copilot_instructions.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            if lines > 350:
                issues.append(f"copilot-instructions.md too long ({lines} lines, target <350)")
            print(f"  ✅ copilot-instructions.md: {lines} lines")
        
        # Check CORTEX.prompt.md
        if not self.cortex_prompt.exists():
            issues.append("CORTEX.prompt.md not created")
        else:
            content = self.cortex_prompt.read_text(encoding='utf-8')
            lines = len(content.split('\n'))
            if lines > 600:
                issues.append(f"CORTEX.prompt.md too long ({lines} lines, target <600)")
            print(f"  ✅ CORTEX.prompt.md: {lines} lines")
        
        success = len(issues) == 0
        
        if not success:
            print(f"  ⚠️  Validation issues: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        
        return {'success': success, 'issues': issues}


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Regenerate CORTEX Copilot prompt files")
    parser.add_argument('--dry-run', action='store_true', help="Preview changes without executing")
    parser.add_argument('--force', action='store_true', help="Override preservation and regenerate anyway")
    args = parser.parse_args()
    
    cortex_root = Path(__file__).parent.parent
    regenerator = PromptRegenerator(cortex_root, dry_run=args.dry_run, force=args.force)
    
    try:
        results = regenerator.execute()
        
        if results['success']:
            print("\n✅ SUCCESS")
            if args.dry_run:
                print("  [DRY RUN] No files were modified")
            else:
                print("  Generated files:")
                print(f"    - {regenerator.copilot_instructions}")
                print(f"    - {regenerator.cortex_prompt}")
                
                # Show backup path if available
                if 'phases' in results and 'backup' in results['phases']:
                    backup_dir = results['phases']['backup']['backup_path']
                    print(f"\n  Backups saved to:")
                    print(f"    - {backup_dir}")
        else:
            print("\n❌ FAILED")
            for error in results.get('errors', []):
                print(f"  - {error}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
