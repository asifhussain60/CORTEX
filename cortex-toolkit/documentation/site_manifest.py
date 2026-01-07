#!/usr/bin/env python3
"""
CORTEX Site Manifest Generator

Generates a complete site manifest for the documentation site:
- All pages with metadata
- Missing documentation detection
- Broken link checking
- View hierarchy compliance

Author: Asif Hussain
Version: 1.1.0

Security:
- Path traversal prevention
- Atomic file writes
- Backup rotation
"""

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse


def safe_path(base: Path, user_path: str) -> Path:
    """Validate path is within base directory (prevent path traversal)."""
    resolved = (base / user_path).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        raise ValueError(f"Path traversal detected: {user_path}")
    return resolved


class SiteManifestGenerator:
    """Generate comprehensive site manifest with missing doc detection."""
    
    # Expected sections based on CORTEX architecture
    EXPECTED_SECTIONS = {
        "features": "Core capabilities and features",
        "orchestrators": "8 intelligent workflow orchestrators",
        "governance": "SKULL rules and brain protection",
        "knowledge": "Technical knowledge and patterns",
        "sts": "Sharpen The Saw - Security and quality",
        "story": "The Awakening - CORTEX origin story",
        "future": "4.0 Vision - Future roadmap",
        "architecture": "System architecture documentation"
    }
    
    # Expected orchestrator documentation
    EXPECTED_ORCHESTRATORS = [
        "planning-system",
        "tdd-orchestrator",
        "debug-orchestrator",
        "cleanup-orchestrator",
        "ado-orchestrator",
        "refinement-orchestrator",
        "sanitization-orchestrator",
        "onboarding-orchestrator"
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.pages: List[Dict[str, Any]] = []
        self.missing_docs: List[Dict[str, str]] = []
        self.broken_links: List[Dict[str, str]] = []
        
    def scan_pages(self) -> List[Dict[str, Any]]:
        """Scan all documentation pages."""
        if not self.docs_dir.exists():
            return []
            
        for html_file in self.docs_dir.rglob("*.html"):
            page_info = self._analyze_page(html_file)
            self.pages.append(page_info)
            
        return self.pages
    
    def _analyze_page(self, html_file: Path) -> Dict[str, Any]:
        """Analyze a single documentation page."""
        rel_path = html_file.relative_to(self.docs_dir)
        parts = rel_path.parts
        
        # Determine level and section
        if len(parts) == 1 and parts[0] == "index.html":
            level = "home"
            section = "root"
        elif len(parts) == 2 and parts[1] == "index.html":
            level = "level1"
            section = parts[0]
        elif len(parts) == 2:
            level = "level2"
            section = parts[0]
        else:
            level = "level2" if len(parts) > 2 else "level1"
            section = parts[0]
        
        # Read content for analysis
        try:
            content = html_file.read_text(encoding='utf-8')
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else html_file.stem
            
            # Check for footer (should only be on home page)
            has_footer = bool(re.search(r'<footer|class=".*footer', content, re.IGNORECASE))
            
            # Check for breadcrumb
            has_breadcrumb = bool(re.search(r'breadcrumb|class=".*nav.*back', content, re.IGNORECASE))
            
            # Check for logo and size
            logo_match = re.search(r'cortex.*logo.*?(\d+).*?(\d+)|logo.*?width["\s:]+(\d+)', content, re.IGNORECASE)
            logo_size = None
            if logo_match:
                size = logo_match.group(1) or logo_match.group(3)
                logo_size = int(size) if size else None
            
            # Check compliance
            compliance_issues = self._check_compliance(level, has_footer, has_breadcrumb, logo_size)
            
            # Extract internal links
            internal_links = re.findall(r'href="([^"#]+\.html)"', content)
            
        except Exception as e:
            content = ""
            title = html_file.stem
            has_footer = False
            has_breadcrumb = False
            logo_size = None
            compliance_issues = [f"Could not read file: {e}"]
            internal_links = []
        
        stat = html_file.stat()
        
        return {
            "path": str(rel_path),
            "abs_path": str(html_file),
            "title": title,
            "section": section,
            "level": level,
            "has_footer": has_footer,
            "has_breadcrumb": has_breadcrumb,
            "logo_size": logo_size,
            "internal_links": internal_links,
            "compliance_issues": compliance_issues,
            "is_compliant": len(compliance_issues) == 0,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _check_compliance(self, level: str, has_footer: bool, has_breadcrumb: bool, 
                          logo_size: Optional[int]) -> List[str]:
        """Check page compliance with design standards."""
        issues = []
        
        # Footer rules
        if level == "home" and not has_footer:
            issues.append("Home page should have footer")
        elif level in ("level1", "level2") and has_footer:
            issues.append(f"{level.upper()} pages should NOT have footer")
        
        # Breadcrumb rules
        if level in ("level1", "level2") and not has_breadcrumb:
            issues.append(f"{level.upper()} pages should have breadcrumb navigation")
        
        # Logo size rules
        if level == "level1" and logo_size and logo_size != 200:
            issues.append(f"Level1 logo should be 200x200, found {logo_size}")
        elif level == "level2" and logo_size and logo_size != 150:
            issues.append(f"Level2 logo should be 150x150, found {logo_size}")
        
        return issues
    
    def check_missing_docs(self) -> List[Dict[str, str]]:
        """Detect missing documentation."""
        self.missing_docs = []
        
        # Check for expected sections
        existing_sections = set(p["section"] for p in self.pages)
        for section, description in self.EXPECTED_SECTIONS.items():
            if section not in existing_sections:
                self.missing_docs.append({
                    "type": "section",
                    "name": section,
                    "description": f"Missing section: {description}",
                    "suggested_path": f"{section}/index.html"
                })
        
        # Check for expected orchestrator docs
        orchestrator_pages = [p["path"] for p in self.pages if "orchestrator" in p["path"].lower()]
        orchestrator_names = [Path(p).stem.lower() for p in orchestrator_pages]
        
        for orch in self.EXPECTED_ORCHESTRATORS:
            # Check if any orchestrator page matches
            if not any(orch.replace("-", "") in name.replace("-", "") for name in orchestrator_names):
                self.missing_docs.append({
                    "type": "orchestrator",
                    "name": orch,
                    "description": f"Missing documentation for {orch}",
                    "suggested_path": f"orchestrators/{orch}.html"
                })
        
        return self.missing_docs
    
    def check_broken_links(self) -> List[Dict[str, str]]:
        """Check for broken internal links."""
        self.broken_links = []
        existing_paths = set(p["path"] for p in self.pages)
        
        for page in self.pages:
            for link in page.get("internal_links", []):
                # Resolve relative link
                if link.startswith("/"):
                    resolved = link[1:]  # Remove leading /
                else:
                    # Relative to current page
                    page_dir = Path(page["path"]).parent
                    resolved = str(page_dir / link)
                
                # Normalize path
                resolved = str(Path(resolved))
                
                if resolved not in existing_paths and not resolved.startswith("http"):
                    self.broken_links.append({
                        "source": page["path"],
                        "broken_link": link,
                        "resolved_path": resolved
                    })
        
        return self.broken_links
    
    def generate_manifest(self) -> Dict[str, Any]:
        """Generate complete site manifest."""
        self.scan_pages()
        self.check_missing_docs()
        self.check_broken_links()
        
        # Calculate statistics
        compliant = len([p for p in self.pages if p["is_compliant"]])
        
        manifest = {
            "version": "1.1",
            "generated": datetime.now().isoformat(),
            "generator": "site_manifest.py",
            "site_url": "http://localhost:8000",
            "footer_rules": {
                "home_page_only": True,
                "excluded_levels": ["level1", "level2"]
            },
            "logo_standards": {
                "level1": "200x200",
                "level2": "150x150"
            },
            "statistics": {
                "total_pages": len(self.pages),
                "compliant_pages": compliant,
                "non_compliant_pages": len(self.pages) - compliant,
                "missing_docs": len(self.missing_docs),
                "broken_links": len(self.broken_links),
                "sections": len(set(p["section"] for p in self.pages)),
                "level1_pages": len([p for p in self.pages if p["level"] == "level1"]),
                "level2_pages": len([p for p in self.pages if p["level"] == "level2"])
            },
            "pages": self.pages,
            "missing_docs": self.missing_docs,
            "broken_links": self.broken_links
        }
        
        # Add checksum for integrity verification
        content_for_hash = json.dumps(manifest, sort_keys=True, default=str)
        manifest["_checksum"] = hashlib.sha256(content_for_hash.encode()).hexdigest()[:16]
        
        return manifest
    
    def save_manifest(self, output_path: Path, manifest: Dict[str, Any]) -> None:
        """Save manifest to JSON file with atomic write and backup."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing manifest (keep last 5)
        if output_path.exists():
            backup_dir = output_path.parent / ".backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{output_path.stem}_{timestamp}.json"
            shutil.copy2(output_path, backup_path)
            
            # Rotate old backups (keep 5)
            backups = sorted(backup_dir.glob(f"{output_path.stem}_*.json"), reverse=True)
            for old_backup in backups[5:]:
                old_backup.unlink()
        
        # Atomic write using temp file
        fd, temp_path = tempfile.mkstemp(suffix='.json', dir=output_path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            shutil.move(temp_path, output_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
        
        print(f"✅ Site manifest saved to: {output_path}")
    
    def print_report(self, manifest: Dict[str, Any]) -> None:
        """Print human-readable report."""
        stats = manifest["statistics"]
        
        print("\n" + "="*60)
        print("📄 SITE MANIFEST REPORT")
        print("="*60)
        
        print(f"\n📈 Statistics:")
        print(f"   Total pages:        {stats['total_pages']}")
        print(f"   Compliant:          {stats['compliant_pages']} ✅")
        print(f"   Non-compliant:      {stats['non_compliant_pages']} ⚠️")
        print(f"   Sections:           {stats['sections']}")
        print(f"   Level 1 pages:      {stats['level1_pages']}")
        print(f"   Level 2 pages:      {stats['level2_pages']}")
        
        if manifest["missing_docs"]:
            print(f"\n⚠️  MISSING DOCUMENTATION ({len(manifest['missing_docs'])}):")
            print("-"*60)
            for doc in manifest["missing_docs"]:
                print(f"   • [{doc['type'].upper()}] {doc['name']}")
                print(f"     → Create: {doc['suggested_path']}")
        
        if manifest["broken_links"]:
            print(f"\n🔗 BROKEN LINKS ({len(manifest['broken_links'])}):")
            print("-"*60)
            for link in manifest["broken_links"][:10]:  # Limit output
                print(f"   • {link['source']}")
                print(f"     → {link['broken_link']} (not found)")
        
        # Non-compliant pages
        non_compliant = [p for p in manifest["pages"] if not p["is_compliant"]]
        if non_compliant:
            print(f"\n⚠️  NON-COMPLIANT PAGES ({len(non_compliant)}):")
            print("-"*60)
            for page in non_compliant[:5]:  # Limit output
                print(f"   • {page['path']}")
                for issue in page["compliance_issues"]:
                    print(f"     → {issue}")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Site Manifest Generator")
    parser.add_argument("--output", "-o",
                       default="cortex-brain/documents/site-manifest.json",
                       help="Output manifest file path")
    parser.add_argument("--project-root", "-p", default=None,
                       help="Project root directory (default: auto-detect)")
    parser.add_argument("--check-missing", "-m", action="store_true",
                       help="Check for missing documentation")
    parser.add_argument("--check-links", "-l", action="store_true",
                       help="Check for broken internal links")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Only output JSON, no console report")
    
    args = parser.parse_args()
    
    # Auto-detect project root
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent
        
        if not (project_root / "cortex-brain").exists():
            print("Error: Could not find project root. Use --project-root option.")
            sys.exit(1)
    
    # Validate output path is within project
    try:
        output_path = safe_path(project_root, args.output)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)
    
    if not args.quiet:
        print(f"📄 CORTEX Site Manifest Generator v1.1.0")
        print(f"   Project root: {project_root}")
    
    generator = SiteManifestGenerator(project_root)
    manifest = generator.generate_manifest()
    
    generator.save_manifest(output_path, manifest)
    
    if not args.quiet:
        generator.print_report(manifest)
    
    # Exit with non-zero if issues found
    if manifest["statistics"]["missing_docs"] > 0 or manifest["statistics"]["broken_links"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
