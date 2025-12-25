🚨 REPOSITORY ROOT POLLUTION DETECTED - OPERATION BLOCKED

Attempted File: '{file_path}'
Expected Location: CORTEX/cortex-brain/documents/{category}/

❌ ABSOLUTELY FORBIDDEN:
- d:\PROJECTS\CORTEX\summary.md ← ROOT (WRONG)
- d:\PROJECTS\NOOR CANVAS\update.md ← ROOT (WRONG)
- /Users/asifhussain/PROJECTS/CORTEX/report.md ← ROOT (WRONG)
- Any file directly in repository root directory

✅ REQUIRED STRUCTURE:
- Reports → CORTEX/cortex-brain/documents/reports/
- Analysis → CORTEX/cortex-brain/documents/analysis/
- Summaries → CORTEX/cortex-brain/documents/summaries/
- Investigations → CORTEX/cortex-brain/documents/investigations/
- Planning → CORTEX/cortex-brain/documents/planning/

Repository root is STRICTLY RESERVED for:
- README.md (project introduction)
- LICENSE (legal)
- Package files (package.json, requirements.txt, setup.py)
- Configuration (cortex.config.json, .gitignore)
- Build scripts (build.py, Makefile)

This rule applies to:
- Standalone CORTEX installations (CORTEX/ repo)
- Embedded CORTEX installations (NOOR-CANVAS/CORTEX/)
- All development environments
