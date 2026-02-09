"""
Pre-commit hook for governance validation.
Runs automatically before commits to prevent governance violations.
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


class PreCommitValidator:
    """Validates AC-ID format and governance rules in staged changes."""
    
    # AC-ID format: DOMAIN-NNN or DOMAIN-NNN-NN
    AC_ID_PATTERN = r'[A-Z]{2,}[-_]?[0-9]{3}(?:[-_]?[0-9]{2})?'
    
    # Common references to AC-IDs in code
    REFERENCE_PATTERNS = [
        r'@pytest\.mark\.ac\(["\'](' + AC_ID_PATTERN + r')["\']',  # @pytest.mark.ac("AR-001")
        r'#\s*(?Union[AC, GV]|AR|FR|ENH|NFR)[-_]?[0-9]{3}(?:[-_]?[0-9]{2})?',  # # AC-001
        r'/\*.*?(?Union[AC, GV]|AR|FR|ENH|NFR)[-_]?[0-9]{3}(?:[-_]?[0-9]{2})?.*?\*/',  # /* AC-001 */
    ]
    
    def __init__(self):
        """Initialize pre-commit validator."""
        self.violations = []
        self.checked_files = 0
        
    def validate_staged_files(self) -> Tuple[bool, List[str]]:
        """Validate all staged files for governance violations."""
        try:
            # Get staged files from git
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = result.stdout.strip().split('\n')
            staged_files = [f for f in staged_files if f]  # Remove empty strings
            
            violations = []
            
            for file_path in staged_files:
                # Skip non-Python files for now
                if not file_path.endswith(('.py', '.md', '.yaml', '.yml')):
                    continue
                    
                self.checked_files += 1
                file_violations = self._validate_file(file_path)
                violations.extend(file_violations)
                
            return len(violations) == 0, violations
            
        except subprocess.CalledProcessError as e:
            return False, [f"Git error: {e}"]
        except Exception as e:
            return False, [f"Error: {e}"]
            
    def _validate_file(self, file_path: str) -> List[str]:
        """Validate a single file."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Check AC-ID format in pytest markers
                    if '@pytest.mark.ac(' in line:
                        violations.extend(self._check_ac_marker(file_path, line_num, line))
                        
                    # Check for invalid AC-ID patterns
                    violations.extend(self._check_ac_id_format(file_path, line_num, line))
                    
                    # Check for governance rule violations (no direct modifications allowed)
                    violations.extend(self._check_governance_violations(file_path, line_num, line))
                    
        except Exception as e:
            violations.append(f"{file_path}: Error reading file - {e}")
            
        return violations
        
    def _check_ac_marker(self, file_path: str, line_num: int, line: str) -> List[str]:
        """Validate pytest.mark.ac() format."""
        violations = []
        
        # Extract AC-ID from marker
        match = re.search(r'@pytest\.mark\.ac\(["\']([^"\']+)["\']\)', line)
        if match:
            ac_id = match.group(1)
            
            # Validate AC-ID format
            if not re.match(f'^{self.AC_ID_PATTERN}$', ac_id):
                violations.append(
                    f"{file_path}:{line_num}: Invalid AC-ID format '{ac_id}'. "
                    f"Expected format: DOMAIN-NNN or DOMAIN-NNN-NN"
                )
                
        return violations
        
    def _check_ac_id_format(self, file_path: str, line_num: int, line: str) -> List[str]:
        """Check for malformed AC-ID references."""
        violations = []
        
        # Look for common AC-ID prefixes
        for prefix in ['AC-', 'GV-', 'AR-', 'FR-', 'ENH-', 'NFR-', 'S-', 'P-', 'REL-', 'ACC-', 'INT-', 'SC-']:
            if prefix in line:
                # Extract the full reference
                matches = re.finditer(f'{prefix}([0-9]+)(?:-([0-9]+))?', line)
                for match in matches:
                    part1 = match.group(1)
                    part2 = match.group(2)
                    
                    # Check format: should be 3 digits for part 1, 2 for part 2
                    if len(part1) != 3:
                        violations.append(
                            f"{file_path}:{line_num}: Malformed AC-ID reference. "
                            f"Expected {len(part1)} digits to be 3: {prefix}{part1}"
                        )
                        
                    if part2 and len(part2) != 2:
                        violations.append(
                            f"{file_path}:{line_num}: Malformed AC-ID reference. "
                            f"Expected {len(part2)} digits in minor version to be 2: {prefix}{part1}-{part2}"
                        )
                        
        return violations
        
    def _check_governance_violations(self, file_path: str, line_num: int, line: str) -> List[str]:
        """Check for governance rule violations."""
        violations = []
        
        # Check for direct database modifications without audit trail
        if 'UPDATE governance.db' in line or 'DELETE FROM' in line and 'governance' in line:
            if '# @governance-approved' not in line:
                violations.append(
                    f"{file_path}:{line_num}: Direct database modification detected. "
                    f"Add '# @governance-approved' comment to allow."
                )
                
        return violations


def run_pre_commit_hook() -> int:
    """Run the pre-commit hook."""
    validator = PreCommitValidator()
    valid, violations = validator.validate_staged_files()
    
    if not valid:
        print("\n" + "="*70)
        print("GOVERNANCE PRE-COMMIT VALIDATION FAILED")
        print("="*70)
        print(f"\nFiles checked: {validator.checked_files}")
        print(f"Violations found: {len(violations)}\n")
        
        for violation in violations:
            print(f"  ✗ {violation}")
            
        print("\n" + "="*70)
        print("To fix: Review violations and correct AC-ID formats")
        print("To bypass: git commit --no-verify (not recommended)")
        print("="*70 + "\n")
        
        return 1
    else:
        print(f"✓ Pre-commit validation passed ({validator.checked_files} files checked)")
        return 0


if __name__ == "__main__":
    sys.exit(run_pre_commit_hook())
