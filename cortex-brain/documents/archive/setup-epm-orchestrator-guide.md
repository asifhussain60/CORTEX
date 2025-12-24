# Setup Entry Point Module Orchestrator Guide

**Version:** 1.0  
**Status:** Production  
**Module:** src/orchestrators/setup_epm_orchestrator.py

---

## Overview

The Setup EPM Orchestrator auto-generates `.github/copilot-instructions.md` for user repositories using lightweight template generation with brain-assisted learning that improves accuracy over time.

## Key Features

- **Fast Detection** - <5 seconds via file system scan (7 languages, 6 frameworks, 6 build systems, 4 test frameworks)
- **Lightweight Template** - ~150 tokens vs 2000+ for semantic analysis (93% token savings)
- **Brain Learning** - Improves accuracy over time (65% initial → 90% after learning)
- **Namespace Isolation** - Each repo gets own Tier 3 storage, prevents cross-contamination

## Commands

```
setup copilot instructions
setup instructions
generate copilot instructions
create copilot instructions
setup epm
copilot instructions
```

## What Gets Generated

- Entry point guidance (how to use CORTEX)
- Architecture overview (detected language/framework)
- Build/test commands (detected from package.json/Makefile/etc.)
- Project conventions (learned over time)
- Critical files reference
- Brain status indicator

## Detection Capabilities

**Languages:** Python, C#, TypeScript, JavaScript, Go, Rust, Java  
**Frameworks:** React, Angular, Vue, Blazor, ASP.NET, Express  
**Build Systems:** npm, yarn, pnpm, dotnet, cargo, maven  
**Test Frameworks:** pytest, jest, xunit, mocha

## GitIgnore Configuration

- ✅ Automatically adds CORTEX/ to `.gitignore`
- ✅ Validates exclusion patterns work with `git check-ignore`
- ✅ Commits changes with descriptive message
- ✅ Confirms no CORTEX files accidentally staged
- ✅ Explicit confirmation message with 5 validation checkmarks

## Brain Learning (Phase 2)

- Observes your coding patterns during normal CORTEX usage
- Stores patterns in Tier 3 (workspace.{repo_name}.copilot_instructions)
- Auto-updates instructions weekly or on-demand via `refresh instructions`
- 30-day TTL prevents brain bloat

## Merge Strategy (Phase 3)

- Detects existing copilot-instructions.md
- Preserves user sections (no 🧠 prefix)
- Updates CORTEX sections (with 🧠 prefix)
- Offers backup before merge

## Workflow

1. **Detection** - Fast file system scan
2. **Template Generation** - Build instructions from detection results
3. **GitIgnore Setup** - Add CORTEX/ exclusion
4. **File Creation** - Write .github/copilot-instructions.md
5. **Validation** - Confirm with 5 checkmarks

## Performance

- Detection: <5 seconds
- Template generation: <1 second
- Total execution: <10 seconds

## Integration

- Tier 3 database for pattern storage
- Response-templates.yaml for triggers
- Git integration for .gitignore management
- Brain learning for continuous improvement

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
