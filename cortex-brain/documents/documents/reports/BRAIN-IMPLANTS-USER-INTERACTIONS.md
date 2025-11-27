# Brain Implants Templates - User Interaction Examples

**Date:** November 18, 2025  
**Purpose:** Demonstrate how users interact with the new Brain Implants templates

---

## Scenario 1: Exporting Brain Patterns

### User Input (Natural Language)
```
export brain
```
*or*
```
share brain
```
*or*
```
export knowledge
```

### CORTEX Response (Template: brain_export_guide)

```markdown
🧠 **CORTEX Brain Implants - Export**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:**
   You want to export CORTEX brain patterns to share knowledge with other 
   developers or backup learned patterns.

⚠️ **Challenge:** ✓ **Accept**
   Brain export is CORTEX's knowledge sharing mechanism. It extracts learned 
   patterns from Tier 2 (Knowledge Graph) into a portable YAML format that 
   other developers can import into their CORTEX instances.

💬 **Response:**
   Brain export creates a timestamped YAML file containing:
   • Learned patterns (workflows, tech stacks, problem solutions)
   • Pattern confidence scores (0.0-1.0)
   • Metadata (source machine, CORTEX version, namespaces)
   • Integrity signature for validation
   
   **What Gets Exported:**
   - Workflow templates from successful implementations
   - Technology stack patterns
   - Problem-solution pairs
   - Architecture decisions
   - Integration patterns
   
   **What Stays Local:**
   - Conversation history (Tier 1 - private)
   - Machine-specific configurations
   - Database connections and credentials

📝 **Your Request:** Export CORTEX brain patterns for sharing

🔍 **Next Steps - Export Workflow:**
   
   **Step 1: Choose Export Scope**
   • Workspace scope (current project only): `export brain --scope=workspace`
   • All patterns (include CORTEX patterns): `export brain --scope=all`
   • Specific namespace: `export brain --namespace=workspace.myproject`
   
   **Step 2: Run Export Command**
   ```bash
   python3 scripts/brain_transfer_cli.py export brain --scope=all
   ```
   
   **Step 3: Review Export File**
   • Location: `cortex-brain/exports/brain-export-YYYYMMDD_HHMMSS.yaml`
   • Size: Typically 5-50 KB depending on patterns learned
   • Format: Human-readable YAML with comments
   
   **Step 4: Share with Team (Optional)**
   • Git commit: Export auto-commits to local git
   • Git push: `git push origin CORTEX-3.0` (share via repository)
   • Direct share: Copy YAML file to shared drive/email/Slack
   
   **Step 5: Documentation**
   • Add export notes: What patterns are included, use cases, version compatibility
   • Create README: `cortex-brain/exports/README.md` with import instructions
   
   **Troubleshooting:**
   • Empty export (0 patterns): Check scope filter matches your pattern namespaces
   • Git push fails: Run `git pull` first if remote has diverged
   • Permission errors: Ensure write access to cortex-brain/exports/
   
   **Example Export Commands:**
   ```bash
   # Export all patterns (recommended for team sharing)
   python3 scripts/brain_transfer_cli.py export brain --scope=all
   
   # Export only current workspace patterns
   python3 scripts/brain_transfer_cli.py export brain --scope=workspace
   
   # Export specific namespace (e.g., authentication patterns)
   python3 scripts/brain_transfer_cli.py export brain --namespace=workspace.myapp.auth
   ```
   
   Ready to export? Choose a scope and I'll execute the export for you.
```

---

## Scenario 2: Importing Brain Patterns

### User Input (Natural Language)
```
import brain
```
*or*
```
load brain
```
*or*
```
import knowledge
```

### CORTEX Response (Template: brain_import_guide)

```markdown
🧠 **CORTEX Brain Implants - Import**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:**
   You want to import shared brain patterns from another developer's export 
   to benefit from their learned knowledge.

⚠️ **Challenge:** ✓ **Accept**
   Brain import is how CORTEX enables knowledge transfer between team members. 
   It intelligently merges imported patterns with your existing patterns using 
   confidence-weighted strategies.

💬 **Response:**
   Brain import reads an exported YAML file and:
   • Validates integrity signature
   • Checks version compatibility
   • Merges patterns using intelligent conflict resolution
   • Preserves your local patterns when appropriate
   • Updates confidence scores based on merge strategy
   
   **Merge Strategies:**
   
   1. **Auto (Recommended)** - Intelligent merge:
      • Keeps higher confidence pattern (local vs imported)
      • Averages confidence if similar
      • Best for team knowledge sharing
   
   2. **Replace** - Import wins:
      • Overwrites local patterns with imported versions
      • Use when importing from senior developer/expert
      • Creates backup of replaced patterns
   
   3. **Keep Local** - Local wins:
      • Keeps your patterns, skips conflicts
      • Only imports new patterns not in your brain
      • Use when testing untrusted exports

📝 **Your Request:** Import shared brain patterns from export file

🔍 **Next Steps - Import Workflow:**
   
   **Step 1: Obtain Export File**
   • Git pull: `git pull origin CORTEX-3.0` (if shared via repo)
   • Direct copy: Place YAML file in `cortex-brain/exports/`
   • Verify file: Check it's named `brain-export-*.yaml`
   
   **Step 2: Preview Import (Dry Run)**
   ```bash
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --dry-run
   ```
   
   **Dry Run Shows:**
   • Number of patterns in export
   • Conflicts with your existing patterns
   • New patterns you'll gain
   • Recommended merge strategy
   • No changes made to your brain
   
   **Step 3: Choose Merge Strategy**
   
   Based on dry run results:
   • **Trust the source?** Use `replace` strategy
   • **Collaborative team?** Use `auto` strategy (default)
   • **Testing/cautious?** Use `keep_local` strategy
   
   **Step 4: Execute Import**
   
   ```bash
   # Auto merge (recommended for teams)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --strategy=auto
   
   # Replace (import wins)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --strategy=replace
   
   # Keep local (your patterns win)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --strategy=keep_local
   ```
   
   **Step 5: Verify Import**
   
   Check imported patterns in database:
   ```bash
   sqlite3 cortex-brain/tier2-knowledge-graph.db \
     "SELECT pattern_id, title, confidence, source FROM patterns 
      ORDER BY created_at DESC LIMIT 10;"
   ```
   
   **Step 6: Test Imported Knowledge**
   
   • Ask CORTEX about imported topics
   • Verify pattern suggestions include imported knowledge
   • Check confidence scores are reasonable
   
   **Troubleshooting:**
   
   • **Version mismatch**: Export from newer CORTEX version may be incompatible
   • **Signature invalid**: File may be corrupted, re-download from source
   • **No patterns imported**: Check merge strategy (keep_local skips all conflicts)
   • **Confidence scores too low**: Imported patterns may need manual confidence boost
   
   **Best Practices:**
   
   1. **Always dry-run first** - Preview before making changes
   2. **Backup your brain** - Export your patterns before importing
   3. **Use auto strategy** - Best for team collaboration
   4. **Review conflicts** - Understand what gets replaced
   5. **Test after import** - Verify CORTEX still works as expected
   
   **Example Import Commands:**
   
   ```bash
   # Preview import (no changes)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --dry-run
   
   # Import with auto-merge (recommended)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --strategy=auto
   
   # Import from senior developer (replace local)
   python3 scripts/brain_transfer_cli.py import brain \
     --file=cortex-brain/exports/brain-export-20251118_040727.yaml \
     --strategy=replace
   ```
   
   Ready to import? I can run the dry-run preview first to show you what will change.
```

---

## Key Features of Brain Implants Templates

### 1. Clear Understanding Section
- Explicitly states what the user wants to achieve
- Confirms CORTEX interpretation is correct
- Sets clear expectations

### 2. Challenge with Accept Rationale
- Validates the approach is sound
- Explains why this feature exists (knowledge sharing mechanism)
- Builds confidence in the functionality

### 3. Detailed Response Section
- Visual formatting with bullet points
- Clear distinction between exported vs private data
- Explains merge strategies for imports
- Provides context about what happens during operation

### 4. Request Echo
- Concise summary of user's intent
- Confirms understanding before proceeding

### 5. Step-by-Step Next Steps
- Numbered workflow (5-6 steps)
- Complete command examples
- Troubleshooting section
- Best practices guidance
- Multiple command examples for different scenarios

---

## Usage Statistics

### Template Sizes
- **Export Guide:** 3,022 characters (~500 words)
- **Import Guide:** 4,812 characters (~800 words)

### Trigger Patterns
- **Export:** 5 natural language triggers
- **Import:** 5 natural language triggers

### Response Type
- Both templates: `detailed` (comprehensive guidance)

---

## Benefits for Users

1. **No Documentation Needed:** All instructions in-context
2. **Multiple Entry Points:** Various natural language triggers
3. **Safety Features:** Dry-run previews, backup recommendations
4. **Troubleshooting:** Common issues addressed proactively
5. **Best Practices:** Learn optimal approaches immediately
6. **Complete Examples:** Copy-paste ready commands

---

## Benefits for Development Team

1. **Reduced Support:** Comprehensive self-service guidance
2. **Consistency:** Standard CORTEX response format
3. **Discoverability:** Natural language makes feature easy to find
4. **Knowledge Propagation:** Enables team-wide pattern sharing
5. **Quality Assurance:** Step-by-step workflow reduces errors

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Repository:** https://github.com/asifhussain60/CORTEX
