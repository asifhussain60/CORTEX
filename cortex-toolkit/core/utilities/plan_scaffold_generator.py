#!/usr/bin/env python3
"""
CORTEX Plan Scaffold Generator

Automatically creates the standard 4-folder planning structure required by
Planning System 4.0. Eliminates manual directory creation overhead.

Usage:
    python plan_scaffold_generator.py "knowledge-documentation"
    python plan_scaffold_generator.py "feature-name" --description "Feature description"

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class PlanScaffoldGenerator:
    """Generate standard planning folder structure."""
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize generator.
        
        Args:
            cortex_root: Path to CORTEX root (auto-detected if None)
        """
        if cortex_root is None:
            # Auto-detect: Look for cortex-brain/ folder
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "cortex-brain").exists():
                    cortex_root = parent
                    break
            
            if cortex_root is None:
                raise RuntimeError("Cannot detect CORTEX root directory")
        
        self.cortex_root = Path(cortex_root)
        self.planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning" / "active"
        
        # Validate planning root exists (create if missing for clean slate)
        self.planning_root.mkdir(parents=True, exist_ok=True)
    
    def sanitize_name(self, name: str) -> str:
        """
        Sanitize plan name for folder creation.
        
        Rules:
        - Lowercase
        - Replace spaces with hyphens
        - Remove special characters (keep alphanumeric and hyphens)
        - Collapse multiple hyphens
        
        Args:
            name: Raw plan name
            
        Returns:
            Sanitized folder name
            
        Examples:
            >>> gen.sanitize_name("Knowledge Documentation")
            'knowledge-documentation'
            >>> gen.sanitize_name("API v2.0 Migration!")
            'api-v2-0-migration'
        """
        import re
        
        # Lowercase
        sanitized = name.lower()
        
        # Replace spaces and underscores with hyphens
        sanitized = sanitized.replace(' ', '-').replace('_', '-')
        
        # Remove special characters (keep alphanumeric and hyphens)
        sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
        
        # Collapse multiple hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        return sanitized
    
    def create_scaffold(
        self, 
        plan_name: str, 
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        dry_run: bool = False,
        include_security: bool = True
    ) -> Dict:
        """
        Create standard 5-folder planning structure with security documentation.
        
        Structure:
            {plan_name}/
            ├── 00-master-plan.md       # Main plan (created separately)
            ├── context/                 # Context artifacts
            ├── reports/                 # Progress reports
            ├── artifacts/               # Supporting files
            ├── security/                # Security documentation (Phase 3)
            │   └── security-documentation.md  # Threat model, requirements, compliance
            └── tracking/                # progress-tracker.json
        
        Args:
            plan_name: Plan name (will be sanitized)
            description: Optional plan description
            metadata: Optional metadata dictionary
            dry_run: If True, don't create folders (just return structure)
            include_security: If True, include security/ subfolder (default: True)
            
        Returns:
            Dictionary with created paths and metadata
        """
        # Sanitize name
        folder_name = self.sanitize_name(plan_name)
        
        if not folder_name:
            raise ValueError(f"Invalid plan name: '{plan_name}' sanitizes to empty string")
        
        # Define structure (Phase 3: Added security folder)
        plan_dir = self.planning_root / folder_name
        folders = {
            "root": plan_dir,
            "context": plan_dir / "context",
            "reports": plan_dir / "reports",
            "artifacts": plan_dir / "artifacts",
            "security": plan_dir / "security",  # Phase 3: Security documentation
            "tracking": plan_dir / "tracking"
        }
        
        # Check if plan already exists
        if plan_dir.exists() and not dry_run:
            return {
                "status": "exists",
                "plan_name": plan_name,
                "folder_name": folder_name,
                "message": f"Plan already exists: {folder_name}",
                "plan_dir": str(plan_dir),
                "folders": {k: str(v) for k, v in folders.items()}
            }
        
        # Create folders (unless dry run)
        created_folders = []
        if not dry_run:
            for name, path in folders.items():
                path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(path))
        
        # Create progress tracker JSON
        tracker_path = folders["tracking"] / "progress-tracker.json"
        tracker_data = {
            "plan_name": plan_name,
            "folder_name": folder_name,
            "created": datetime.now().isoformat(),
            "description": description or f"Implementation plan for {plan_name}",
            "status": "initialized",
            "phases": [],
            "metadata": metadata or {},
            "statistics": {
                "total_phases": 0,
                "completed_phases": 0,
                "progress_percent": 0
            }
        }
        
        if not dry_run:
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2)
        
        # Phase 3: Create security documentation from template
        security_doc_path = None
        if include_security and not dry_run:
            security_doc_path = self._create_security_documentation(
                folders["security"],
                plan_name,
                description,
                metadata
            )
        
        # Return result
        result = {
            "status": "created" if not dry_run else "dry_run",
            "plan_name": plan_name,
            "folder_name": folder_name,
            "plan_dir": str(plan_dir),
            "folders": {k: str(v) for k, v in folders.items()},
            "security_doc": str(security_doc_path) if security_doc_path else None,
            "tracker": str(tracker_path),
            "created_folders": created_folders if not dry_run else []
        }
        
        return result
    
    def _create_security_documentation(
        self,
        security_folder: Path,
        plan_name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Create security documentation from template.
        
        Phase 3: Security Documentation Automation
        Reference: cortex-brain/documents/planning/active/security-enhancement/00-master-plan.md
        
        Args:
            security_folder: Path to the security subfolder
            plan_name: Name of the plan
            description: Optional plan description
            metadata: Optional metadata dictionary
            
        Returns:
            Path to created security documentation
        """
        security_doc_path = security_folder / "security-documentation.md"
        
        # Try to load template from cortex-brain
        template_path = self.cortex_root / "cortex-brain" / "templates" / "security" / "plan-security-template.md"
        
        if template_path.exists():
            # Load and customize template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace placeholders
            author = metadata.get("author", "CORTEX Planning System") if metadata else "CORTEX Planning System"
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            content = template_content.replace("{PLAN_NAME}", plan_name)
            content = content.replace("{DATE}", current_date)
            content = content.replace("{AUTHOR}", author)
        else:
            # Generate minimal security documentation
            current_date = datetime.now().strftime("%Y-%m-%d")
            author = metadata.get("author", "CORTEX Planning System") if metadata else "CORTEX Planning System"
            
            content = f"""# 🔐 Security Documentation: {plan_name}

**Plan:** {plan_name}  
**Created:** {current_date}  
**Author:** {author}  
**Status:** 📋 Awaiting Security Analysis  

---

## Overview

This document provides security analysis and requirements for the {plan_name} feature.

## Sections to Complete

1. **Threat Model** - STRIDE analysis required
2. **Security Requirements** - Functional and non-functional requirements
3. **Compliance Mapping** - GDPR/HIPAA/PCI-DSS/SOC2 as applicable
4. **Mitigation Strategies** - Security controls and defenses
5. **Security Testing Plan** - SAST/DAST/Penetration testing requirements
6. **Risk Register** - Identified risks and mitigations

## References

- Threat Modeling Framework: `cortex-brain/knowledge-library/security/threat-modeling-framework.md`
- OWASP Top 10 Guide: `cortex-brain/knowledge-library/security/owasp-top-10-guide.md`
- Security Documentation Standards: `cortex-brain/knowledge-library/security/security-documentation-standards.md`

---

**⚠️ IMPORTANT:** Complete security analysis required before implementation.
"""
        
        # Write security documentation
        with open(security_doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return security_doc_path
    
    def list_plans(self) -> list:
        """
        List all existing plans in active folder.
        
        Returns:
            List of plan folder names
        """
        if not self.planning_root.exists():
            return []
        
        plans = []
        for item in self.planning_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                plans.append(item.name)
        
        return sorted(plans)
    
    def validate_structure(self, plan_name: str, require_security: bool = True) -> Dict:
        """
        Validate that a plan has the correct 5-folder structure with security.
        
        Phase 3: Updated to require security/ subfolder by default.
        
        Args:
            plan_name: Plan folder name
            require_security: If True, security folder is required (default: True)
            
        Returns:
            Validation result dictionary
        """
        folder_name = self.sanitize_name(plan_name)
        plan_dir = self.planning_root / folder_name
        
        if not plan_dir.exists():
            return {
                "valid": False,
                "message": f"Plan not found: {folder_name}",
                "missing": ["root"]
            }
        
        # Phase 3: Added security to required folders
        required_folders = ["context", "reports", "artifacts", "tracking"]
        if require_security:
            required_folders.append("security")
        
        missing = []
        
        for folder in required_folders:
            if not (plan_dir / folder).exists():
                missing.append(folder)
        
        # Check for progress tracker
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        has_tracker = tracker_path.exists()
        
        # Phase 3: Check for security documentation
        security_doc_path = plan_dir / "security" / "security-documentation.md"
        has_security_doc = security_doc_path.exists() if require_security else True
        
        # Build validation message
        issues = []
        if missing:
            issues.append(f"Missing folders: {', '.join(missing)}")
        if not has_tracker:
            issues.append("Missing progress-tracker.json")
        if require_security and not has_security_doc and "security" not in missing:
            issues.append("Missing security-documentation.md")
        
        is_valid = len(missing) == 0 and has_tracker and (has_security_doc if require_security else True)
        
        return {
            "valid": is_valid,
            "plan_dir": str(plan_dir),
            "missing_folders": missing,
            "has_tracker": has_tracker,
            "has_security_doc": has_security_doc if require_security else None,
            "require_security": require_security,
            "message": "Valid structure" if is_valid else "; ".join(issues)
        }
    
    def retrofit_security_folder(self, plan_name: str, dry_run: bool = False) -> Dict:
        """
        Add security folder and documentation to an existing plan.
        
        Phase 3: Retrofit existing plans with security documentation.
        
        Args:
            plan_name: Plan folder name
            dry_run: If True, don't create folders (just return what would be created)
            
        Returns:
            Result dictionary with retrofit status
        """
        folder_name = self.sanitize_name(plan_name)
        plan_dir = self.planning_root / folder_name
        
        if not plan_dir.exists():
            return {
                "status": "error",
                "message": f"Plan not found: {folder_name}",
                "plan_name": plan_name
            }
        
        security_folder = plan_dir / "security"
        security_doc_path = security_folder / "security-documentation.md"
        
        # Check if security folder already exists
        if security_folder.exists() and security_doc_path.exists():
            return {
                "status": "already_exists",
                "message": f"Security folder already exists for: {folder_name}",
                "plan_name": plan_name,
                "security_folder": str(security_folder),
                "security_doc": str(security_doc_path)
            }
        
        if dry_run:
            return {
                "status": "dry_run",
                "message": f"Would retrofit security folder for: {folder_name}",
                "plan_name": plan_name,
                "security_folder": str(security_folder),
                "security_doc": str(security_doc_path)
            }
        
        # Create security folder
        security_folder.mkdir(parents=True, exist_ok=True)
        
        # Load metadata from progress tracker if available
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        metadata = {}
        description = None
        
        if tracker_path.exists():
            try:
                with open(tracker_path, 'r', encoding='utf-8') as f:
                    tracker_data = json.load(f)
                    description = tracker_data.get("description")
                    metadata = tracker_data.get("metadata", {})
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create security documentation
        created_doc = self._create_security_documentation(
            security_folder,
            plan_name,
            description,
            metadata
        )
        
        return {
            "status": "retrofitted",
            "message": f"Successfully added security folder to: {folder_name}",
            "plan_name": plan_name,
            "security_folder": str(security_folder),
            "security_doc": str(created_doc)
        }
    
    def retrofit_all_plans(self, dry_run: bool = False) -> Dict:
        """
        Add security folders to ALL existing plans without them.
        
        Phase 3: Batch retrofit for existing plans.
        
        Args:
            dry_run: If True, don't create folders (just report what would be created)
            
        Returns:
            Summary dictionary with all retrofit results
        """
        plans = self.list_plans()
        results = {
            "total_plans": len(plans),
            "retrofitted": [],
            "already_secure": [],
            "errors": [],
            "dry_run": dry_run
        }
        
        for plan in plans:
            validation = self.validate_structure(plan, require_security=True)
            
            if validation["valid"]:
                results["already_secure"].append(plan)
            elif "security" in validation.get("missing_folders", []) or \
                 (validation.get("has_security_doc") is False):
                # Needs security folder/doc
                retrofit_result = self.retrofit_security_folder(plan, dry_run=dry_run)
                
                if retrofit_result["status"] in ["retrofitted", "dry_run"]:
                    results["retrofitted"].append({
                        "plan": plan,
                        "result": retrofit_result
                    })
                else:
                    results["errors"].append({
                        "plan": plan,
                        "result": retrofit_result
                    })
            else:
                # Other validation issues
                results["errors"].append({
                    "plan": plan,
                    "result": {"status": "validation_error", "message": validation["message"]}
                })
        
        results["summary"] = {
            "retrofitted_count": len(results["retrofitted"]),
            "already_secure_count": len(results["already_secure"]),
            "error_count": len(results["errors"])
        }
        
        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Plan Scaffold Generator - Create standard planning folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create plan scaffold
  python plan_scaffold_generator.py "knowledge-documentation"
  
  # Create with description
  python plan_scaffold_generator.py "api-v2-migration" --description "Migrate API to v2"
  
  # Dry run (don't create folders)
  python plan_scaffold_generator.py "test-plan" --dry-run
  
  # List existing plans
  python plan_scaffold_generator.py --list
  
  # Validate existing plan
  python plan_scaffold_generator.py "knowledge-documentation" --validate
  
  # Retrofit security folder to existing plan
  python plan_scaffold_generator.py "knowledge-documentation" --retrofit-security
  
  # Retrofit ALL plans with security folders
  python plan_scaffold_generator.py --retrofit-all
        """
    )
    
    parser.add_argument(
        'plan_name',
        nargs='?',
        help='Plan name (will be sanitized for folder creation)'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Plan description (added to progress tracker)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without creating folders'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all existing plans'
    )
    
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validate existing plan structure'
    )
    
    parser.add_argument(
        '--cortex-root',
        type=Path,
        help='CORTEX root directory (auto-detected if not specified)'
    )
    
    # Phase 3: Security retrofit arguments
    parser.add_argument(
        '--retrofit-security',
        action='store_true',
        help='Add security folder to existing plan'
    )
    
    parser.add_argument(
        '--retrofit-all',
        action='store_true',
        help='Add security folders to ALL existing plans'
    )
    
    parser.add_argument(
        '--no-security',
        action='store_true',
        help='Create plan without security folder (legacy mode)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = PlanScaffoldGenerator(cortex_root=args.cortex_root)
        
        # List mode
        if args.list:
            plans = generator.list_plans()
            if plans:
                print(f"📋 Found {len(plans)} active plans:")
                for plan in plans:
                    print(f"  • {plan}")
            else:
                print("📋 No active plans found")
            return 0
        
        # Retrofit all mode (Phase 3)
        if args.retrofit_all:
            print("🔐 Retrofitting ALL plans with security folders...")
            result = generator.retrofit_all_plans(dry_run=args.dry_run)
            
            print(f"\n📊 Summary:")
            print(f"   Total plans: {result['total_plans']}")
            print(f"   Already secure: {result['summary']['already_secure_count']}")
            print(f"   Retrofitted: {result['summary']['retrofitted_count']}")
            print(f"   Errors: {result['summary']['error_count']}")
            
            if result['retrofitted']:
                print(f"\n✅ Retrofitted plans:")
                for item in result['retrofitted']:
                    print(f"   • {item['plan']}")
            
            if result['already_secure']:
                print(f"\n🔒 Already secure plans:")
                for plan in result['already_secure'][:5]:  # Show first 5
                    print(f"   • {plan}")
                if len(result['already_secure']) > 5:
                    print(f"   ... and {len(result['already_secure']) - 5} more")
            
            if result['errors']:
                print(f"\n❌ Errors:")
                for item in result['errors']:
                    print(f"   • {item['plan']}: {item['result']['message']}")
            
            return 0 if result['summary']['error_count'] == 0 else 1
        
        # Retrofit single plan mode (Phase 3)
        if args.retrofit_security:
            if not args.plan_name:
                print("❌ Error: --retrofit-security requires plan_name", file=sys.stderr)
                return 1
            
            result = generator.retrofit_security_folder(args.plan_name, dry_run=args.dry_run)
            
            if result['status'] == 'retrofitted':
                print(f"✅ Added security folder to: {args.plan_name}")
                print(f"   Security doc: {result['security_doc']}")
            elif result['status'] == 'already_exists':
                print(f"ℹ️  {result['message']}")
            elif result['status'] == 'dry_run':
                print(f"🔍 Would add security folder to: {args.plan_name}")
                print(f"   Security folder: {result['security_folder']}")
            else:
                print(f"❌ Error: {result['message']}")
                return 1
            
            return 0
        
        # Validate mode
        if args.validate:
            if not args.plan_name:
                print("❌ Error: --validate requires plan_name", file=sys.stderr)
                return 1
            
            result = generator.validate_structure(args.plan_name)
            
            if result['valid']:
                print(f"✅ Valid structure: {result['plan_dir']}")
                if result.get('has_security_doc'):
                    print(f"   🔐 Security documentation: Present")
            else:
                print(f"❌ Invalid structure: {result['message']}")
                print(f"   Plan dir: {result.get('plan_dir', 'N/A')}")
                if result.get('has_security_doc') is False:
                    print(f"   🔐 Security documentation: Missing")
                    print(f"   💡 Tip: Run with --retrofit-security to add security folder")
            
            return 0 if result['valid'] else 1
        
        # Create mode
        if not args.plan_name:
            parser.print_help()
            return 1
        
        result = generator.create_scaffold(
            plan_name=args.plan_name,
            description=args.description,
            dry_run=args.dry_run,
            include_security=not args.no_security  # Phase 3: security by default
        )
        
        # Print result
        if result['status'] == 'exists':
            print(f"ℹ️  {result['message']}")
            print(f"   Path: {result['plan_dir']}")
        elif result['status'] == 'dry_run':
            print(f"🔍 Dry run - Would create:")
            print(f"   Plan: {result['plan_name']} → {result['folder_name']}")
            print(f"   Root: {result['plan_dir']}")
            print("   Folders:")
            for name, path in result['folders'].items():
                if name != 'root':
                    emoji = "🔐" if name == "security" else "📁"
                    print(f"     {emoji} {name}/")
            print(f"   Tracker: {result['tracker']}")
            if not args.no_security:
                print(f"   Security doc: {result['folders'].get('security', '')}/security-documentation.md")
        else:
            print(f"✅ Created plan scaffold: {result['folder_name']}")
            print(f"   Path: {result['plan_dir']}")
            print(f"   Folders: {len(result['created_folders'])}")
            print(f"   Tracker: {result['tracker']}")
            if result.get('security_doc'):
                print(f"   🔐 Security: {result['security_doc']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
