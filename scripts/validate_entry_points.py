"""
CORTEX Deployment Validation - Entry Point Module Checker
==========================================================

Purpose: Enforce presence of all required entry point modules before deployment
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

Validates:
1. All required entry point modules exist
2. CORTEX.prompt.md references all modules
3. copilot-instructions.md updated
4. Documentation synchronized
5. .gitignore template present

Usage: python scripts/validate_entry_points.py
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # Fallback if encoding setup fails

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class EntryPointValidator:
    """Validates all entry point modules present for deployment"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.modules_dir = self.root / '.github' / 'prompts' / 'modules'
        self.prompt_file = self.root / '.github' / 'prompts' / 'CORTEX.prompt.md'
        self.copilot_instructions = self.root / '.github' / 'copilot-instructions.md'
        self.failures: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print(f"{Colors.BOLD}CORTEX Deployment Validation - Entry Points{Colors.RESET}")
        print("=" * 70)
        
        self.validate_required_modules()
        self.validate_cortex_prompt_references()
        self.validate_copilot_instructions()
        self.validate_gitignore_template()
        self.validate_version_file()
        
        return self.print_summary()
    
    def validate_required_modules(self):
        """Check all required entry point modules exist"""
        print(f"\n{Colors.BLUE}[1/5] Entry Point Module Validation{Colors.RESET}")
        
        required_modules = [
            ('upgrade-guide.md', 'Upgrade automation with brain preservation'),
            ('feedback-guide.md', 'Issue reporting and feedback collection'),
            ('optimize-guide.md', 'Performance optimization and cleanup'),
            ('healthcheck-guide.md', 'System health monitoring'),
            ('view-discovery-guide.md', 'TDD automation - element discovery'),
        ]
        
        for module_name, description in required_modules:
            module_path = self.modules_dir / module_name
            
            if module_path.exists():
                # Check file has content (not empty stub)
                content = module_path.read_text(encoding='utf-8')
                if len(content) > 500:  # Minimum content check
                    print(f"  ✅ {module_name}: {description}")
                else:
                    self.failures.append(f"{module_name} exists but lacks content (<500 chars)")
            else:
                # Only upgrade-guide.md is required initially
                if module_name == 'upgrade-guide.md':
                    self.failures.append(f"Missing required module: {module_name}")
                else:
                    self.warnings.append(f"Optional module not yet created: {module_name}")
    
    def validate_cortex_prompt_references(self):
        """Check CORTEX.prompt.md references all modules"""
        print(f"\n{Colors.BLUE}[2/5] CORTEX.prompt.md Documentation Sync{Colors.RESET}")
        
        if not self.prompt_file.exists():
            self.failures.append(f"CORTEX.prompt.md not found at {self.prompt_file}")
            return
        
        content = self.prompt_file.read_text(encoding='utf-8')
        
        # Check for upgrade section
        if '## 🔄 Upgrade CORTEX' in content or '## 🔄 Upgrade' in content:
            print(f"  ✅ Upgrade section documented")
        else:
            self.failures.append("CORTEX.prompt.md missing Upgrade section")
        
        # Check for module reference syntax
        if '#file:modules/upgrade-guide.md' in content or 'upgrade-guide.md' in content:
            print(f"  ✅ upgrade-guide.md referenced")
        else:
            self.failures.append("upgrade-guide.md not referenced in CORTEX.prompt.md")
        
        # Check for feedback section
        if '## 📢 Feedback' in content or 'feedback bug' in content:
            print(f"  ✅ Feedback section documented")
        else:
            self.warnings.append("Feedback section not documented in CORTEX.prompt.md")
        
        # Check for view discovery section
        if '## 🔍 View Discovery' in content or 'discover views' in content:
            print(f"  ✅ View Discovery section documented")
        else:
            self.warnings.append("View Discovery not documented in CORTEX.prompt.md")
    
    def validate_copilot_instructions(self):
        """Check copilot-instructions.md updated"""
        print(f"\n{Colors.BLUE}[3/5] copilot-instructions.md Validation{Colors.RESET}")
        
        if not self.copilot_instructions.exists():
            self.failures.append(f"copilot-instructions.md not found at {self.copilot_instructions}")
            return
        
        content = self.copilot_instructions.read_text(encoding='utf-8')
        
        # Check entry point reference
        if 'CORTEX.prompt.md' in content:
            print(f"  ✅ References CORTEX.prompt.md entry point")
        else:
            self.failures.append("copilot-instructions.md doesn't reference CORTEX.prompt.md")
        
        # Check for module documentation
        if 'modules/' in content or 'upgrade-guide' in content:
            print(f"  ✅ Documents module system")
        else:
            self.warnings.append("copilot-instructions.md doesn't mention module system")
        
        # Check for version info
        if 'Version' in content or 'v3.' in content:
            print(f"  ✅ Version information present")
        else:
            self.warnings.append("Version information not found in copilot-instructions.md")
    
    def validate_gitignore_template(self):
        """Check .gitignore template exists for user repos"""
        print(f"\n{Colors.BLUE}[4/5] .gitignore Template Validation{Colors.RESET}")
        
        # Check CORTEX internal .gitignore
        internal_gitignore = self.root / '.gitignore'
        if internal_gitignore.exists():
            content = internal_gitignore.read_text(encoding='utf-8')
            
            # Should exclude databases
            if '*.db' in content:
                print(f"  ✅ CORTEX .gitignore excludes databases")
            else:
                self.warnings.append("CORTEX .gitignore doesn't exclude *.db files")
            
            # Should include important files
            if '!documents/' in content or 'documents/' not in content:
                print(f"  ✅ CORTEX .gitignore includes documents")
            else:
                self.warnings.append("documents/ may be excluded from version control")
        else:
            self.warnings.append("CORTEX .gitignore not found")
        
        # Check user repo template
        user_gitignore_template = self.root / '.github' / 'templates' / 'user-gitignore.template'
        if user_gitignore_template.exists():
            print(f"  ✅ User repo .gitignore template exists")
        else:
            self.warnings.append("User repo .gitignore template not found (will be created during upgrade)")
    
    def validate_version_file(self):
        """Check VERSION file exists and is valid"""
        print(f"\n{Colors.BLUE}[5/5] Version File Validation{Colors.RESET}")
        
        version_file = self.root / 'VERSION'
        if version_file.exists():
            version = version_file.read_text(encoding='utf-8').strip()
            
            # Check version format (e.g., v3.1.0)
            if version.startswith('v') and version.count('.') == 2:
                print(f"  ✅ VERSION file present: {version}")
            else:
                self.failures.append(f"VERSION file has invalid format: {version}")
        else:
            self.warnings.append("VERSION file not found (will use git tags)")
    
    def print_summary(self) -> bool:
        """Print validation summary"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}VALIDATION SUMMARY{Colors.RESET}")
        print("=" * 70)
        
        if self.failures:
            print(f"{Colors.RED}❌ FAILURES: {len(self.failures)}{Colors.RESET}")
            for failure in self.failures:
                print(f"  ❌ {failure}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}⚠️  WARNINGS: {len(self.warnings)}{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.failures and not self.warnings:
            print(f"{Colors.GREEN}✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT{Colors.RESET}")
        elif not self.failures:
            print(f"{Colors.YELLOW}✅ VALIDATION PASSED WITH WARNINGS{Colors.RESET}")
            print(f"   Warnings are non-critical but should be addressed")
        else:
            print(f"{Colors.RED}❌ VALIDATION FAILED - FIX FAILURES BEFORE DEPLOYMENT{Colors.RESET}")
        
        print("=" * 70)
        
        return len(self.failures) == 0


def main():
    """Run entry point validation"""
    validator = EntryPointValidator()
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
