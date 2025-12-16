"""
CORTEX Package Builder
Builds the distribution package for CORTEX installation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

This script creates a complete, ready-to-distribute package in the publish/ folder.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import zipfile


class CortexPackageBuilder:
    """Builds CORTEX distribution package."""
    
    def __init__(self):
        """Initialize the package builder."""
        self.cortex_root = Path(__file__).parent.parent
        self.publish_dir = self.cortex_root / "publish"
        self.package_dir = self.publish_dir / "cortex-files"
        self.version = "5.2.0"
        
    def clean_publish_directory(self):
        """Clean the publish directory completely."""
        print("🧹 Cleaning publish directory...")
        
        # Files to preserve during cleanup
        preserve_files = ['INSTALL.md', 'install_cortex.py', 'install-cortex-windows.ps1', 'install-cortex-unix.sh']
        
        # Remove EVERYTHING in publish folder except files we want to keep
        if self.publish_dir.exists():
            for item in self.publish_dir.iterdir():
                try:
                    if item.is_file():
                        # Keep installer files
                        if item.name not in preserve_files:
                            item.unlink()
                            print(f"   ✓ Removed file: {item.name}")
                    elif item.is_dir():
                        # Remove all directories (cortex-files, old zips, etc.)
                        shutil.rmtree(item)
                        print(f"   ✓ Removed directory: {item.name}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove {item.name}: {e}")
        
        # Create fresh package directory
        self.package_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Created fresh package directory: {self.package_dir}")
        
    def _ignore_src_admin_files(self, dir, files):
        """Ignore admin files in src directory."""
        ignore = self._ignore_common(dir, files)
        
        # Exclude IMPLEMENTATION-SUMMARY.md files in tier directories
        for f in files:
            if 'IMPLEMENTATION' in f and f.endswith('.md'):
                ignore.append(f)
        
        return ignore
    
    def copy_cortex_files(self):
        """Copy all CORTEX components (src, brain, scripts, docs)."""
        print("\n📦 Copying CORTEX components...")
        
        # Copy source code (exclude admin files)
        source = self.cortex_root / "src"
        target = self.package_dir / "src"
        shutil.copytree(source, target, ignore=self._ignore_src_admin_files)
        print(f"   ✓ Copied src/ (no admin docs)")
        
        # Copy brain system (essential files only)
        brain_source = self.cortex_root / "cortex-brain"
        brain_target = self.package_dir / "cortex-brain"
        shutil.copytree(brain_source, brain_target, ignore=self._ignore_brain_admin_files)
        
        # Create empty conversation files
        (brain_target / "conversation-history.jsonl").touch()
        (brain_target / "conversation-context.jsonl").touch()
        print(f"   ✓ Copied cortex-brain/ (user files only)")
        
        # Copy scripts (no test/admin scripts)
        scripts_source = self.cortex_root / "scripts"
        scripts_target = self.package_dir / "scripts"
        shutil.copytree(scripts_source, scripts_target, ignore=self._ignore_admin_scripts)
        print(f"   ✓ Copied scripts/ (no admin scripts)")
        
        # Copy docs (no architecture/internal docs)
        docs_source = self.cortex_root / "docs"
        if docs_source.exists():
            docs_target = self.package_dir / "docs"
            shutil.copytree(docs_source, docs_target, ignore=self._ignore_admin_docs)
            print(f"   ✓ Copied docs/ (user docs only)")
        else:
            print(f"   ⚠️  docs/ not found, skipping")
        
    def _ignore_common(self, dir, files):
        """Common ignore patterns for all components."""
        return [
            f for f in files 
            if f.endswith('.pyc') or 
            f == '__pycache__' or 
            f == '.pytest_cache' or
            f == '.mypy_cache' or
            f.endswith('.db') or
            f.endswith('.db-journal')
        ]
    
    def _ignore_brain_admin_files(self, dir, files):
        """Ignore admin-only brain files."""
        ignore = self._ignore_common(dir, files)
        
        # Check directory name first - exclude entire directories
        import os
        dir_name = os.path.basename(dir)
        dir_path_lower = dir.lower()
        
        # Exclude test directories entirely (anywhere in the tree)
        if dir_name == 'tests' or '\\tests\\' in dir or '/tests/' in dir or '\\tests' in dir or '/tests' in dir:
            return files  # Ignore entire tests directory
        
        # Exclude planning directories entirely (all planning is internal)
        planning_dirs = ['planning', 'temp-plans', 'active', 'archived', 'completed']
        if any(plan_dir in dir_path_lower for plan_dir in planning_dirs):
            return files  # Ignore entire planning hierarchy
        
        # Exclude implementation guides (all internal)
        if 'implementation-guides' in dir_path_lower:
            return files
        
        # Internal categories to exclude entirely
        internal_categories = [
            'archived-scripts', 'conversation-captures', 'evidence-templates',
            'investigations', 'learning', 'limitations', 'narratives',
            'onboarded-apps', 'pilot-projects', 'rationales', 'reviews', 'scribe',
            'discovery'  # NEW: discovery is internal dev context
        ]
        
        if dir_name in internal_categories:
            return files  # Ignore entire directory
        
        # File-level patterns for remaining files
        admin_patterns = [
            'IMPLEMENTATION', 'STATUS', 'PLAN', 'SESSION', 'PROGRESS',
            'HOLISTIC-REVIEW', 'LEARNING-SYSTEM', 'CLEANUP-ORCHESTRATOR',
            'BRAIN-PROTECTION-TEST', 'CODE-REFACTORING', 'DOC-REFRESH',
            'E2E-WORKFLOW', 'FILE-GENERATION', 'HARDCODED-DATA',
            'HONEST-STATUS', 'IMPLICIT-PART1', 'MAC-TRACK', 'MAC-UNIVERSAL',
            'MACOS-COMPATIBILITY', 'MODULE-INTEGRATION', 'cortex-2.0-design',
            'phase-completions', 'archives', '-summary.md', 'implementation-summary',
            'implementation', 'progress', '-plan', 'holistic', 
            'epm-', 'deploy-', 'feature-9', 'orchestrator-', 'path-cleanup',
            'phase-', 'ra-migration', 'test-intelligence', 'user-profile',
            'capability-driven', 'cleanup-validation', '3-tier-educational',
            'ADO-', 'phased-implementation', 'roadmap', 'cortex-lens'
        ]
        
        # Filter reports directory (keep only essential user-facing reports)
        if 'reports' in dir:
            keep_reports = [
                'deployment-validation-dry-run-analysis'  # Keep this specific report
            ]
            
            for f in files:
                # Keep explicitly listed reports
                if any(keep in f.lower() for keep in keep_reports):
                    continue
                # Exclude all other reports
                ignore.append(f)
        
        # Filter analysis directory (exclude all analysis docs)
        if 'analysis' in dir_path_lower:
            return files  # Exclude entire analysis directory
        
        # Filter files by pattern
        for f in files:
            f_lower = f.lower()
            if any(pattern.lower() in f_lower for pattern in admin_patterns):
                ignore.append(f)
        
        return ignore
    
    def _ignore_admin_scripts(self, dir, files):
        """Ignore admin-only scripts."""
        ignore = self._ignore_common(dir, files)
        
        # Exclude admin, test scripts, and temp folder
        for f in files:
            if (f.startswith('test_') or 
                f.startswith('debug_') or 
                'admin' in f.lower() or
                f == 'temp' or
                dir.endswith('temp')):
                ignore.append(f)
        
        return ignore
    
    def _ignore_admin_docs(self, dir, files):
        """Ignore admin-only documentation."""
        ignore = self._ignore_common(dir, files)
        
        # Exclude patterns
        exclude_patterns = [
            'architecture', 'internal', 'IMPLEMENTATION', 'STATUS',
            'PLAN', 'SESSION', 'PROGRESS', 'operations', 'api',
            'design', 'project', 'TEST-SUITE', 'implementation-notes',
            'doc-refresh'
        ]
        
        # Exclude architecture and internal design docs
        for f in files:
            f_lower = f.lower()
            if any(pattern.lower() in f_lower for pattern in exclude_patterns):
                ignore.append(f)
        
        # Also exclude plugins subfolder entirely (admin docs)
        if dir.endswith('plugins'):
            return files  # Ignore entire plugins doc folder
        
        return ignore
        
    def copy_bootstrap_installers(self):
        """Copy bootstrap installer scripts to publish root."""
        print("\n🚀 Copying bootstrap installers...")
        
        installers = [
            ("install-cortex-windows.ps1", "Windows bootstrap installer (legacy)"),
            ("install-cortex-unix.sh", "Unix/macOS bootstrap installer (legacy)"),
            ("install-cortex-windows-fast.ps1", "Windows fast installer (2-3 min)"),
            ("install-cortex-unix-fast.sh", "Unix/macOS fast installer (2-3 min)"),
        ]
        
        for installer_path, description in installers:
            source = self.cortex_root / installer_path
            target = self.publish_dir / source.name
            if source.exists():
                # Skip if target exists and is the same (file may be in use)
                if target.exists():
                    try:
                        # Try to verify it's the same file
                        if source.stat().st_mtime == target.stat().st_mtime:
                            print(f"   ✓ {source.name}: {description} (already up-to-date)")
                            continue
                    except:
                        pass
                
                try:
                    shutil.copy2(source, target)
                    print(f"   ✓ Copied {source.name}: {description}")
                except PermissionError:
                    print(f"   ⚠️  {source.name}: Skipped (file in use, already exists)")
            else:
                print(f"   ⚠️  {installer_path} not found")
        
    def skip_tests_for_user_package(self):
        """Skip tests directory for user packages (not needed)."""
        print("\n✅ Skipping tests (not needed in user package)...")
        print(f"   ℹ️  Tests remain in developer repository only")
        
    def copy_docs(self):
        """Copy docs directory."""
        print("\n📚 Copying documentation...")
        
        source = self.cortex_root / "docs"
        target = self.package_dir / "docs"
        
        if source.exists():
            shutil.copytree(source, target)
            print(f"   ✓ Copied docs/")
        else:
            print(f"   ⚠️  No docs directory found")
        
    def _ignore_internal_prompts(self, dir, files):
        """Ignore internal prompts and admin planning docs."""
        ignore = []
        
        # Skip entire internal directory
        if 'internal' in dir:
            return files
        
        # Filter out modules directory (internal orchestrator guides)
        if 'modules' in dir:
            return files
        
        # Also filter out specific admin files in user/shared
        admin_files = [
            'plan.md',
            'session-loader.md',
            'limitations-and-status.md',
            'planning-orchestrator-guide.md',  # Internal orchestrator guide
        ]
        
        for f in files:
            if f in admin_files:
                ignore.append(f)
        
        return ignore
    
    def copy_prompts(self):
        """Copy prompts directory."""
        print("\\n💬 Copying prompts...")
        
        # Prompts are in .github/prompts/
        source = self.cortex_root / ".github" / "prompts"
        target = self.package_dir / ".github" / "prompts"
        
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, ignore=self._ignore_internal_prompts)
            print(f"   ✓ Copied .github/prompts/ (CORTEX entry point)")
        else:
            print(f"   ⚠️  .github/prompts/ not found")
        
        # Also copy .github/copilot-instructions.md
        copilot_instructions = self.cortex_root / ".github" / "copilot-instructions.md"
        if copilot_instructions.exists():
            github_dir = self.package_dir / ".github"
            github_dir.mkdir(exist_ok=True)
            shutil.copy2(copilot_instructions, github_dir / "copilot-instructions.md")
            print(f"   ✓ Copied .github/copilot-instructions.md")
        
    def copy_templates(self):
        """Copy D3.js dashboard templates."""
        print("\n🎨 Copying dashboard templates...")
        
        templates_source = self.cortex_root / "templates"
        if templates_source.exists():
            templates_target = self.package_dir / "templates"
            shutil.copytree(templates_source, templates_target)
            print(f"   ✓ Copied templates/ (D3.js dashboards)")
        else:
            print(f"   ⚠️  templates/ not found - dashboard visualization disabled")
    
    def copy_root_files(self):
        """Copy root configuration files."""
        print("\n📄 Copying root files...")
        
        root_files = [
            "requirements.txt",
            "requirements-core.txt",  # NEW: Fast install tier 1
            "requirements-optional.txt",  # NEW: Optional features tier 2
            "pytest.ini",
            "cortex.config.template.json",
            "cortex-operations.yaml",  # CRITICAL: Operations manifest
            "deployment-manifest.yaml",  # NEW: Production deployment manifest
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "setup.py",
            ".gitignore",
        ]
        
        for file in root_files:
            source = self.cortex_root / file
            if source.exists():
                shutil.copy2(source, self.package_dir / file)
                print(f"   ✓ Copied {file}")
            else:
                print(f"   ⚠️  {file} not found")
        
        # Also copy .github/copilot-instructions.md
        copilot_instructions = self.cortex_root / ".github" / "copilot-instructions.md"
        if copilot_instructions.exists():
            github_dir = self.package_dir / ".github"
            github_dir.mkdir(exist_ok=True)
            shutil.copy2(copilot_instructions, github_dir / "copilot-instructions.md")
            print(f"   ✓ Copied .github/copilot-instructions.md")
        
    def create_package_info(self):
        """Create package info file."""
        print("\n📋 Creating package info...")
        
        package_info = {
            "name": "CORTEX AI Enhancement System",
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "author": "Asif Hussain",
            "copyright": "© 2024-2025 Asif Hussain. All rights reserved.",
            "license": "Proprietary",
            "repository": "https://github.com/asifhussain60/CORTEX",
            "description": "AI enhancement system that gives GitHub Copilot long-term memory, context awareness, and strategic planning",
            "installation": "Run bootstrap installer: install-cortex-windows.ps1 (Windows) or install-cortex-unix.sh (Unix)",
            "components": [
                "src - Source code",
                "cortex-brain - Memory and knowledge system (essential files only)",
                "scripts - Automation tools (no admin scripts)",
                "docs - User documentation (no architecture docs)",
                "prompts - AI prompt templates",
            ]
        }
        
        info_path = self.package_dir / "PACKAGE_INFO.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(package_info, f, indent=2)
        
        print(f"   ✓ Created PACKAGE_INFO.json")
        
    def create_zip_archive(self):
        """Create a zip archive of the package."""
        print("\n📦 Creating zip archive...")
        
        zip_path = self.publish_dir / f"cortex-v{self.version}.zip"
        
        # Remove old zip if exists
        if zip_path.exists():
            zip_path.unlink()
        
        # Create zip
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from package directory
            for root, dirs, files in os.walk(self.package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.package_dir.parent)
                    zipf.write(file_path, arcname)
            
            # Add installer scripts
            installer_files = [
                "install_cortex.py",
                "install-cortex-windows.ps1",
                "install-cortex-unix.sh",
                "install-cortex-windows-fast.ps1",  # NEW: Fast installer
                "install-cortex-unix-fast.sh",  # NEW: Fast installer
                "INSTALL.md",
            ]
            
            for installer_file in installer_files:
                installer = self.publish_dir / installer_file
                if installer.exists():
                    zipf.write(installer, installer_file)
                    print(f"   ✓ Added {installer_file}")
        
        print(f"   ✓ Created {zip_path.name}")
        print(f"   📊 Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return zip_path
        
    def build(self):
        """Build the complete package."""
        print("="*80)
        print("CORTEX Package Builder")
        print(f"Version: {self.version}")
        print("="*80)
        
        try:
            self.clean_publish_directory()
            self.copy_cortex_files()
            self.copy_prompts()
            self.copy_templates()
            self.copy_root_files()
            self.copy_bootstrap_installers()
            self.skip_tests_for_user_package()
            self.create_package_info()
            zip_path = self.create_zip_archive()
            
            print("\n" + "="*80)
            print("✅ Package built successfully!")
            print("="*80)
            print(f"\n📦 Package location: {self.package_dir}")
            print(f"🗜️  Archive location: {zip_path}")
            print(f"\n📋 Distribution instructions:")
            print(f"   1. Share the zip file or the entire publish/ folder")
            print(f"   2. Users extract and run bootstrap installer:")
            print(f"      - Windows: install-cortex-windows.ps1")
            print(f"      - Unix/macOS: install-cortex-unix.sh")
            print(f"   3. Bootstrap installer handles Python/Git installation")
            print(f"   4. User runs '/CORTEX setup' in Copilot Chat")
            print("\n" + "="*80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Package build failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    builder = CortexPackageBuilder()
    success = builder.build()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
