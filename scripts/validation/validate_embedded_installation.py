"""
CORTEX Embedded Installation Validator

Scans an embedded CORTEX installation for upgrade blockers and common issues.
This validator checks files outside the main CORTEX workspace.

Usage:
    python scripts/validation/validate_embedded_installation.py "D:\\PROJECTS\\NOOR CANVAS\\CORTEX"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
from pathlib import Path
import json
import yaml
import sqlite3

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class EmbeddedInstallationValidator:
    """Validates embedded CORTEX installations for upgrade readiness"""
    
    def __init__(self, cortex_path: Path):
        self.cortex_path = Path(cortex_path)
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print(f"\n{Colors.BOLD}CORTEX Embedded Installation Validator{Colors.RESET}")
        print(f"Target: {self.cortex_path}")
        print("=" * 70)
        
        if not self.cortex_path.exists():
            print(f"{Colors.RED}❌ CORTEX directory not found: {self.cortex_path}{Colors.RESET}")
            return False
        
        checks = [
            ("Installation structure", self.check_installation_structure),
            ("VERSION file", self.check_version_file),
            ("Brain databases", self.check_brain_databases),
            ("Configuration files", self.check_config_files),
            ("Response templates", self.check_response_templates),
            ("Python dependencies", self.check_dependencies),
            ("Embedded marker", self.check_embedded_marker),
            ("Parent project detection", self.check_parent_project),
            ("Upgrade system files", self.check_upgrade_system),
        ]
        
        for check_name, check_func in checks:
            print(f"\n{Colors.BLUE}Checking: {check_name}{Colors.RESET}")
            try:
                result = check_func()
                if result is True:
                    print(f"  {Colors.GREEN}✅ {check_name} OK{Colors.RESET}")
                elif result is False:
                    print(f"  {Colors.RED}❌ {check_name} FAILED{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}⚠️  {check_name} - {result}{Colors.RESET}")
            except Exception as e:
                print(f"  {Colors.RED}❌ {check_name} ERROR: {e}{Colors.RESET}")
                self.issues.append(f"{check_name}: {e}")
        
        return len(self.issues) == 0
    
    def check_installation_structure(self) -> bool:
        """Check basic CORTEX directory structure"""
        required_paths = [
            ".github/prompts/CORTEX.prompt.md",
            "cortex-brain/",
            "scripts/",
            "src/",
        ]
        
        missing = []
        for path in required_paths:
            full_path = self.cortex_path / path
            if not full_path.exists():
                missing.append(path)
        
        if missing:
            self.issues.append(f"Missing paths: {', '.join(missing)}")
            return False
        
        return True
    
    def check_version_file(self) -> bool:
        """Check VERSION file exists and is readable"""
        version_file = self.cortex_path / "VERSION"
        
        if not version_file.exists():
            self.issues.append("VERSION file missing")
            # Try to create it
            try:
                version_file.write_text("v3.3.0\n", encoding='utf-8')
                print(f"  {Colors.GREEN}✅ Created VERSION file with v3.3.0{Colors.RESET}")
                self.fixes_applied.append("Created missing VERSION file")
                return True
            except Exception as e:
                self.issues.append(f"Cannot create VERSION file: {e}")
                return False
        
        try:
            content = version_file.read_text(encoding='utf-8').strip()
            
            if not content:
                self.issues.append("VERSION file is empty")
                version_file.write_text("v3.3.0\n", encoding='utf-8')
                self.fixes_applied.append("Fixed empty VERSION file")
                return True
            
            # Check format
            if content.startswith('{'):
                # JSON format (legacy)
                try:
                    data = json.loads(content)
                    version = data.get('cortex_version')
                    print(f"  📦 Current version (JSON format): {version}")
                    return True
                except json.JSONDecodeError:
                    self.issues.append("VERSION file contains invalid JSON")
                    return False
            else:
                # Plain text format
                print(f"  📦 Current version: {content}")
                return True
                
        except Exception as e:
            self.issues.append(f"Cannot read VERSION file: {e}")
            return False
    
    def check_brain_databases(self) -> bool:
        """Check brain databases exist and are accessible"""
        brain_dir = self.cortex_path / "cortex-brain"
        
        if not brain_dir.exists():
            self.issues.append("cortex-brain directory missing")
            return False
        
        # Check for essential databases
        tier1_db = brain_dir / "tier1" / "working_memory.db"
        tier2_db = brain_dir / "tier2" / "knowledge_graph.db"
        
        issues = []
        
        if tier1_db.exists():
            try:
                conn = sqlite3.connect(str(tier1_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                print(f"  📊 Tier 1 database: {len(tables)} tables")
            except Exception as e:
                self.warnings.append(f"Tier 1 database issue: {e}")
        else:
            self.warnings.append("Tier 1 database not found (will be created on first use)")
        
        if tier2_db.exists():
            try:
                conn = sqlite3.connect(str(tier2_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                print(f"  📊 Tier 2 database: {len(tables)} tables")
            except Exception as e:
                self.warnings.append(f"Tier 2 database issue: {e}")
        else:
            self.warnings.append("Tier 2 database not found (will be created on first use)")
        
        return True  # Non-critical
    
    def check_config_files(self) -> bool:
        """Check configuration files"""
        config_file = self.cortex_path / "cortex.config.json"
        
        if not config_file.exists():
            self.warnings.append("cortex.config.json not found (will use defaults)")
            return True  # Non-critical
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"  ⚙️  Config loaded successfully")
            return True
        except Exception as e:
            self.warnings.append(f"Config file issue: {e}")
            return True  # Non-critical
    
    def check_response_templates(self) -> bool:
        """Check response-templates.yaml"""
        templates_file = self.cortex_path / "cortex-brain" / "response-templates.yaml"
        
        if not templates_file.exists():
            self.issues.append("response-templates.yaml missing")
            return False
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            if not templates:
                self.issues.append("response-templates.yaml is empty")
                return False
            
            # Check format (dict vs array)
            if 'templates' in templates:
                templates_data = templates['templates']
                if isinstance(templates_data, dict):
                    print(f"  📝 Templates format: dictionary ({len(templates_data)} templates)")
                    return True
                elif isinstance(templates_data, list):
                    print(f"  📝 Templates format: array ({len(templates_data)} templates)")
                    return True
                else:
                    self.warnings.append(f"Unexpected templates format: {type(templates_data)}")
                    return True
            else:
                self.warnings.append("No 'templates' key in response-templates.yaml")
                return True
                
        except Exception as e:
            self.issues.append(f"Cannot read response-templates.yaml: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check Python requirements"""
        req_file = self.cortex_path / "requirements.txt"
        
        if not req_file.exists():
            self.warnings.append("requirements.txt not found")
            return True  # Non-critical
        
        try:
            content = req_file.read_text(encoding='utf-8')
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            print(f"  📦 Requirements: {len(lines)} packages")
            return True
        except Exception as e:
            self.warnings.append(f"Cannot read requirements.txt: {e}")
            return True
    
    def check_embedded_marker(self) -> bool:
        """Check for embedded installation marker"""
        marker_file = self.cortex_path / ".cortex-embedded"
        
        if marker_file.exists():
            print(f"  🔒 Embedded marker exists")
            return True
        
        # Check if this looks like an embedded installation
        parent = self.cortex_path.parent
        if (parent / ".git").exists() and not (self.cortex_path / ".git").exists():
            # Create marker
            try:
                marker_file.write_text(f"# CORTEX Embedded Installation\n# Parent Project: {parent.name}\n# Created: 2025-11-25\n", encoding='utf-8')
                print(f"  {Colors.GREEN}✅ Created embedded marker{Colors.RESET}")
                self.fixes_applied.append("Created .cortex-embedded marker")
                return True
            except Exception as e:
                self.warnings.append(f"Cannot create embedded marker: {e}")
        
        self.warnings.append("No embedded marker (may cause upgrade issues)")
        return True  # Non-critical
    
    def check_parent_project(self) -> bool:
        """Check parent project structure"""
        parent = self.cortex_path.parent
        print(f"  📂 Parent project: {parent.name}")
        
        # Check for project indicators
        indicators = [
            (".git", "Git repository"),
            ("package.json", "Node.js project"),
            (".sln", ".NET solution"),
            ("requirements.txt", "Python project"),
        ]
        
        found = []
        for indicator, desc in indicators:
            if (parent / indicator).exists():
                found.append(desc)
        
        if found:
            print(f"  📌 Detected: {', '.join(found)}")
        
        return True
    
    def check_upgrade_system(self) -> bool:
        """Check upgrade system files"""
        scripts_dir = self.cortex_path / "scripts" / "operations"
        
        required_files = [
            "upgrade_orchestrator.py",
            "version_detector.py",
            "config_merger.py",
            "brain_preserver.py",
        ]
        
        missing = []
        for file in required_files:
            if not (scripts_dir / file).exists():
                missing.append(file)
        
        if missing:
            self.issues.append(f"Missing upgrade files: {', '.join(missing)}")
            return False
        
        print(f"  ✅ All upgrade system files present")
        return True
    
    def print_summary(self) -> bool:
        """Print validation summary"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}VALIDATION SUMMARY{Colors.RESET}")
        print("=" * 70)
        
        if self.fixes_applied:
            print(f"\n{Colors.GREEN}Fixes Applied: {len(self.fixes_applied)}{Colors.RESET}")
            for fix in self.fixes_applied:
                print(f"  ✅ {fix}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if self.issues:
            print(f"\n{Colors.RED}Critical Issues: {len(self.issues)}{Colors.RESET}")
            for issue in self.issues:
                print(f"  ❌ {issue}")
        
        print("\n" + "=" * 70)
        
        if not self.issues:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ INSTALLATION READY FOR UPGRADE{Colors.RESET}")
            print(f"{Colors.GREEN}No blockers detected. Safe to run 'upgrade' command.{Colors.RESET}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ BLOCKERS DETECTED{Colors.RESET}")
            print(f"{Colors.RED}Fix issues above before upgrading{Colors.RESET}")
            return False


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate_embedded_installation.py <cortex_path>")
        print("\nExample:")
        print('  python validate_embedded_installation.py "D:\\PROJECTS\\NOOR CANVAS\\CORTEX"')
        sys.exit(1)
    
    cortex_path = Path(sys.argv[1])
    
    validator = EmbeddedInstallationValidator(cortex_path)
    success = validator.validate_all()
    validator.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
