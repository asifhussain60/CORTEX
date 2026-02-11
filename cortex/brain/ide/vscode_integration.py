"""
VS Code IDE Integration for Governance Diagnostics
Provides real-time governance violation detection and quick fixes.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class GovernanceDiagnosticsProvider:
    """Provides governance diagnostics for VS Code."""

    def __init__(self):
        """Initialize diagnostics provider."""
        self.diagnostics = []

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a file and return diagnostics."""
        diagnostics = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 0):  # 0-based for LSP
                    # Check for AC-ID format violations
                    ac_violations = self._check_ac_id_violations(line, line_num)
                    diagnostics.extend(ac_violations)

                    # Check for governance rule violations
                    rule_violations = self._check_rule_violations(line, line_num)
                    diagnostics.extend(rule_violations)

                    # Check for missing decorators
                    decorator_violations = self._check_decorator_violations(line, line_num, f)
                    diagnostics.extend(decorator_violations)

        except Exception as e:
            diagnostics.append({
                "range": {"start": {"line": 0, "character": 0},
                         "end": {"line": 0, "character": 100}},
                "severity": 1,  # Error
                "source": "governance",
                "message": f"Error analyzing file: {e}",
                "code": "ANALYSIS_ERROR"
            })

        return diagnostics

    def _check_ac_id_violations(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Check for AC-ID format violations."""
        diagnostics = []

        import re

        # Look for malformed AC-ID references
        for prefix in ['AC-', 'GV-', 'AR-', 'FR-', 'ENH-', 'NFR-', 'S-', 'P-', 'REL-', 'ACC-', 'INT-', 'SC-']:
            matches = list(re.finditer(f'{prefix}([0-9]+)(?:-([0-9]+))?', line))

            for match in matches:
                part1 = match.group(1)
                part2 = match.group(2)

                violation_detected = False
                message = ""
                code = ""

                if len(part1) != 3:
                    violation_detected = True
                    message = f"AC-ID major version should be 3 digits, got {len(part1)}"
                    code = "AC_ID_FORMAT_MAJOR"

                elif part2 and len(part2) != 2:
                    violation_detected = True
                    message = f"AC-ID minor version should be 2 digits, got {len(part2)}"
                    code = "AC_ID_FORMAT_MINOR"

                if violation_detected:
                    diagnostics.append({
                        "range": {
                            "start": {"line": line_num, "character": match.start()},
                            "end": {"line": line_num, "character": match.end()}
                        },
                        "severity": 1,  # Error
                        "source": "governance",
                        "message": message,
                        "code": code
                    })

        return diagnostics

    def _check_rule_violations(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Check for governance rule violations."""
        diagnostics = []

        # Check for unvalidated direct database modifications
        if 'DELETE FROM' in line or 'UPDATE' in line and 'governance' in line.lower():
            if '@governance-approved' not in line:
                diagnostics.append({
                    "range": {
                        "start": {"line": line_num, "character": 0},
                        "end": {"line": line_num, "character": len(line)}
                    },
                    "severity": 1,  # Error
                    "source": "governance",
                    "message": "Direct database modification without governance approval",
                    "code": "UNVALIDATED_DB_MOD"
                })

        return diagnostics

    def _check_decorator_violations(self, line: str, line_num: int,
                                   file_obj) -> List[Dict[str, Any]]:
        """Check for missing governance decorators."""
        diagnostics = []

        # If this is a test function definition, check for @pytest.mark.ac decorator
        if line.strip().startswith('def test_'):
            # Look back for decorators
            found_ac_decorator = False

            # This is a simplified check - in real implementation,
            # would need to parse the entire function context
            found_ac_decorator = '@pytest.mark.ac(' in line or (
                hasattr(file_obj, '_prev_line') and
                '@pytest.mark.ac(' in getattr(file_obj, '_prev_line', '')
            )

            if not found_ac_decorator:
                diagnostics.append({
                    "range": {
                        "start": {"line": line_num, "character": 0},
                        "end": {"line": line_num, "character": len(line)}
                    },
                    "severity": 2,  # Warning
                    "source": "governance",
                    "message": "Test function missing @pytest.mark.ac() decorator",
                    "code": "MISSING_AC_DECORATOR"
                })

        return diagnostics

    def get_quick_fixes(self, diagnostic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get quick fixes for a diagnostic."""
        code = diagnostic.get("code", "")
        message = diagnostic.get("message", "")

        quick_fixes = []

        if code == "AC_ID_FORMAT_MAJOR":
            quick_fixes.append({
                "title": "Fix AC-ID major version to 3 digits",
                "kind": "quickfix",
                "isPreferred": True,
                "edit": {
                    "changes": {
                        # Would include proper edit in real implementation
                        "note": "Would fix the AC-ID format"
                    }
                }
            })

        elif code == "MISSING_AC_DECORATOR":
            quick_fixes.append({
                "title": "Add @pytest.mark.ac() decorator",
                "kind": "quickfix",
                "isPreferred": True,
                "edit": {
                    "changes": {
                        "note": "Would add decorator above test function"
                    }
                }
            })

        return quick_fixes


class VSCodeExtensionConfig:
    """Configuration for VS Code extension."""

    @staticmethod
    def generate_extension_json() -> Dict[str, Any]:
        """Generate VS Code extension configuration."""
        return {
            "name": "cortex-governance",
            "displayName": "CORTEX Governance",
            "description": "Real-time governance diagnostics and validation for CORTEX framework",
            "version": "1.0.0",
            "publisher": "cortex",
            "engines": {
                "vscode": "^1.75.0"
            },
            "activationEvents": [
                "onLanguage:python",
                "onLanguage:markdown",
                "onLanguage:yaml"
            ],
            "main": "./extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "cortex-governance.validateFile",
                        "title": "CORTEX: Validate File Against Governance Rules"
                    },
                    {
                        "command": "cortex-governance.queryAC",
                        "title": "CORTEX: Query AC-ID Details"
                    },
                    {
                        "command": "cortex-governance.checkReadiness",
                        "title": "CORTEX: Check Phase Readiness"
                    }
                ],
                "keybindings": [
                    {
                        "command": "cortex-governance.validateFile",
                        "key": "ctrl+alt+g",
                        "mac": "cmd+alt+g",
                        "when": "editorFocus"
                    }
                ],
                "configuration": {
                    "title": "CORTEX Governance",
                    "properties": {
                        "cortex-governance.enableRealTimeValidation": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable real-time governance validation"
                        },
                        "cortex-governance.validateOnSave": {
                            "type": "boolean",
                            "default": True,
                            "description": "Validate file on save"
                        },
                        "cortex-governance.showWarnings": {
                            "type": "boolean",
                            "default": True,
                            "description": "Show governance warnings"
                        },
                        "cortex-governance.databasePath": {
                            "type": "string",
                            "default": "cortex_brain/state/governance.db",
                            "description": "Path to governance database"
                        }
                    }
                },
                "languages": [
                    {
                        "id": "python",
                        "aliases": ["Python"],
                        "extensions": [".py"]
                    }
                ],
                "themes": [
                    {
                        "label": "CORTEX Governance Dark",
                        "uiTheme": "vs-dark",
                        "path": "./themes/governance-dark.json"
                    }
                ]
            }
        }


def generate_vscode_extension_files():
    """Generate all necessary VS Code extension files."""
    config = VSCodeExtensionConfig()
    extension_json = config.generate_extension_json()

    return {
        "package.json": json.dumps(extension_json, indent=2),
        "manifest.json": {
            "version": "1.0.0",
            "diagnostics_version": "1",
            "supported_vscode": "1.75.0+"
        }
    }


if __name__ == "__main__":
    # Generate extension configuration
    provider = GovernanceDiagnosticsProvider()
    files = generate_vscode_extension_files()

    for filename, content in files.items():
        print(f"\n{'='*60}")
        print(f"File: {filename}")
        print(f"{'='*60}")
        print(json.dumps(content, indent=2) if isinstance(content, dict) else content)
