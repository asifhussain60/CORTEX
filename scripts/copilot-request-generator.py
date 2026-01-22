#!/usr/bin/env python3
"""
CORTEX Track:Eval Copilot Request Generator
Creates efficient, minimal-verbosity requests for Copilot execution

Usage:
    python scripts/copilot-request-generator.py
    python scripts/copilot-request-generator.py --format shell
    python scripts/copilot-request-generator.py --format prompt
"""

import sys
from datetime import datetime

class CopilotRequest:
    """Generate efficient Copilot requests for track:eval execution."""
    
    SHELL_COMMAND = """#!/bin/bash
# Auto-generated CORTEX Track:Eval Request - {timestamp}
cd /Users/asifhussain/PROJECTS/CORTEX
python scripts/execute-track-eval-silent.py > eval-results.json 2>eval-progress.log
EXIT_CODE=$?

# Extract summary
PASS=$(jq '.phases | [.[] | select(.status=="PASS")] | length' eval-results.json)
TOTAL=$(jq '.phases | length' eval-results.json)
BLOCKERS=$(jq '.blockers | length' eval-results.json)

echo ""
echo "TRACK:EVAL RESULT: $PASS/$TOTAL phases passed"
[ $BLOCKERS -gt 0 ] && echo "BLOCKERS: $BLOCKERS" || echo "✓ NO BLOCKERS"
echo ""

exit $EXIT_CODE
"""

    PYTHON_REQUEST = """import subprocess
import json
from pathlib import Path

# CORTEX Track:Eval Silent Execution
cortex_root = Path('/Users/asifhussain/PROJECTS/CORTEX')
result = subprocess.run(
    ['{python}', 'scripts/execute-track-eval-silent.py'],
    cwd=str(cortex_root),
    capture_output=True,
    text=True,
    timeout=900
)

# Parse results
try:
    data = json.loads(result.stdout)
    passed = sum(1 for p in data['phases'].values() if p['status'] == 'PASS')
    total = len(data['phases'])
    blockers = len(data['blockers'])
    
    print(f"✓ {passed}/{total} phases passed")
    if blockers > 0:
        print(f"⚠ {blockers} blocker(s) detected")
        for b in data['blockers']:
            print(f"  - {b[0]}")
except:
    print(f"Parse error (exit code {result.returncode})")
    if result.stderr:
        print(result.stderr[:200])

sys.exit(result.returncode)
"""

    COPILOT_PROMPT = """Execute CORTEX track:eval audit phases silently:

@cortex Execute with minimal output:
1. python scripts/execute-track-eval-silent.py
2. Capture all output to eval-results.json
3. Extract only:
   - Total phases executed
   - Number passed/failed/warnings
   - Any blockers
4. Show single-line summary: "✓ 8/8 PASS" or "⚠ Blockers: X"
5. Return exit code 0 if all pass, 1 if any fail
6. No verbose test output, no detailed phase logs
7. JSON available for programmatic processing

Options:
--silent      Minimal stderr output (default)
--save-json   Save full results to eval-results-{timestamp}.json
--commit      Auto-commit results to git
--phase N     Run only phase N for testing (1-8)

Expected runtime: 10-15 minutes
Blocking phases: PHASE-AUDIT-001, PHASE-AUDIT-002
"""

    MAKEFILE_RECIPE = """# Add to Makefile or similar build system

.PHONY: track-eval
track-eval: ## Execute track:eval phases silently
\t@python scripts/execute-track-eval-silent.py > /tmp/eval-$$(date +%s).json 2>eval.log
\t@echo "✓ Track:eval complete. Results: eval-results.json"

.PHONY: track-eval-verbose
track-eval-verbose: ## Execute with detailed output
\t@python scripts/execute-track-eval-silent.py 2>&1 | tee eval.log

.PHONY: track-eval-status
track-eval-status: ## Show last track:eval results
\t@jq '.phases[] | "\\(.phase): \\(.status)"' eval-results.json 2>/dev/null || echo "No results file"
"""

    GITHUB_ACTION = """name: CORTEX Track:Eval
on:
  workflow_dispatch:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Execute track:eval
        run: |
          python scripts/execute-track-eval-silent.py > eval-results.json 2>eval.log
          EXIT_CODE=$?
          echo "EVAL_EXIT_CODE=$EXIT_CODE" >> $GITHUB_ENV
          exit $EXIT_CODE
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: eval-results
          path: eval-results.json
      
      - name: Comment on PR
        if: always()
        run: |
          PASS=$(jq '.summary.passed' eval-results.json)
          TOTAL=$(jq '.summary.total' eval-results.json)
          echo "Track:eval: $PASS/$TOTAL phases passed" >> $GITHUB_STEP_SUMMARY
"""

    @classmethod
    def generate_shell(cls):
        """Generate shell command."""
        return cls.SHELL_COMMAND.format(timestamp=datetime.now().isoformat())
    
    @classmethod
    def generate_python(cls):
        """Generate Python code."""
        python_path = "python3"
        return cls.PYTHON_REQUEST.format(python=python_path)
    
    @classmethod
    def generate_copilot_prompt(cls):
        """Generate Copilot prompt."""
        return cls.COPILOT_PROMPT
    
    @classmethod
    def generate_makefile(cls):
        """Generate Makefile recipes."""
        return cls.MAKEFILE_RECIPE
    
    @classmethod
    def generate_github_action(cls):
        """Generate GitHub Action."""
        return cls.GITHUB_ACTION


def main():
    """Main entry point."""
    format_type = sys.argv[1] if len(sys.argv) > 1 else "shell"
    
    if format_type == "shell":
        print(CopilotRequest.generate_shell())
    elif format_type == "python":
        print(CopilotRequest.generate_python())
    elif format_type == "copilot":
        print(CopilotRequest.generate_copilot_prompt())
    elif format_type == "makefile":
        print(CopilotRequest.generate_makefile())
    elif format_type == "github":
        print(CopilotRequest.generate_github_action())
    else:
        print("Available formats: shell, python, copilot, makefile, github")
        sys.exit(1)


if __name__ == "__main__":
    main()
