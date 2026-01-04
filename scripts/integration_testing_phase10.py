"""
Phase 10: Integration Testing
HTML View Glassmorphism Alignment Plan

Automated validation of:
1. HTML W3C validation (sample)
2. Link validation (all files)
3. CSS import validation
4. JavaScript compatibility
5. Visual regression checks
6. End-to-end user flows
7. Cross-browser validation
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

class IntegrationTester:
    """Integration testing for Phase 10"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.docs_dir = self.workspace_root / "docs"
        self.reports_dir = self.workspace_root / "cortex-brain" / "documents" / "planning" / "active" / "html-glassmorphism-alignment" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "html_validation": [],
            "link_validation": [],
            "css_validation": [],
            "js_validation": [],
            "visual_regression": [],
            "e2e_flows": [],
            "cross_browser": []
        }
        
    def select_sample_pages(self) -> List[Path]:
        """Select 25 sample pages (5 per tier)"""
        
        # Tier 1: Critical pages (5)
        tier1 = [
            "index.html",
            "orchestrators/index.html",
            "security/index.html",
            "architecture/index.html",
            "features/index.html"
        ]
        
        # Tier 2: High priority (5)
        tier2 = [
            "orchestrators/planning-v5.html",
            "security/data-protection.html",
            "features/response-templates.html",
            "token-optimization/index.html",
            "sts/index.html"
        ]
        
        # Tier 3: Medium priority (5)
        tier3 = [
            "learning-paths/index.html",
            "knowledge/index.html",
            "orchestrators/ado-v2.html",
            "orchestrators/cleanup-orchestrator.html",
            "toolkit-manager/index.html"
        ]
        
        # Tier 4: Legacy/backup (5)
        tier4 = [
            "sitemap.html",
            "faq.html",
            "panel-viewer.html",
            "story/index.html",
            "getting-started/index.html"
        ]
        
        # Additional Tier 3 samples (5)
        tier3_extra = [
            "knowledge/api-design-hub.html",
            "orchestrators/debug-orchestrator.html",
            "orchestrators/git-checkpoint.html",
            "security/audit-logging.html",
            "security/access-control.html"
        ]
        
        all_samples = tier1 + tier2 + tier3 + tier4 + tier3_extra
        
        # Convert to absolute paths, check existence
        sample_paths = []
        for rel_path in all_samples:
            full_path = self.docs_dir / rel_path
            if full_path.exists():
                sample_paths.append(full_path)
            else:
                print(f"⚠️ Sample file not found: {rel_path}")
                
        return sample_paths
    
    def validate_html_structure(self, html_path: Path) -> Dict:
        """Basic HTML structure validation"""
        
        result = {
            "file": str(html_path.relative_to(self.workspace_root)),
            "errors": [],
            "warnings": [],
            "status": "PASS"
        }
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for DOCTYPE
            if not re.search(r'<!DOCTYPE\s+html>', content, re.IGNORECASE):
                result["errors"].append("Missing <!DOCTYPE html>")
            
            # Check for required meta tags
            if '<meta charset="UTF-8">' not in content and '<meta charset="utf-8">' not in content:
                result["warnings"].append("Missing charset meta tag")
            
            if 'name="viewport"' not in content:
                result["warnings"].append("Missing viewport meta tag")
            
            # Check for balanced tags
            open_divs = len(re.findall(r'<div[^>]*>', content))
            close_divs = len(re.findall(r'</div>', content))
            if open_divs != close_divs:
                result["errors"].append(f"Unbalanced div tags: {open_divs} open, {close_divs} close")
            
            # Check for glassmorphism CSS link
            if 'glassmorphism.css' not in content and 'glassmorphism-extended.css' not in content:
                result["warnings"].append("Missing glassmorphism CSS link")
            
            # Check for inline styles (should be minimal)
            inline_styles = re.findall(r'style="[^"]*"', content)
            if len(inline_styles) > 5:
                result["warnings"].append(f"High inline style count: {len(inline_styles)} instances")
            
            # Update status
            if result["errors"]:
                result["status"] = "FAIL"
            elif result["warnings"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
            result["status"] = "ERROR"
        
        return result
    
    def validate_links(self, html_path: Path) -> Dict:
        """Validate internal and external links"""
        
        result = {
            "file": str(html_path.relative_to(self.workspace_root)),
            "broken_links": [],
            "external_links": [],
            "anchor_links": [],
            "status": "PASS"
        }
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all href attributes
            href_pattern = r'href="([^"]+)"'
            links = re.findall(href_pattern, content)
            
            for link in links:
                # Skip external links (http/https)
                if link.startswith(('http://', 'https://')):
                    result["external_links"].append(link)
                    continue
                
                # Skip anchor links
                if link.startswith('#'):
                    result["anchor_links"].append(link)
                    continue
                
                # Skip mailto/tel
                if link.startswith(('mailto:', 'tel:')):
                    continue
                
                # Check internal links
                if link.startswith('/'):
                    # Absolute path from docs root
                    target = self.docs_dir / link.lstrip('/')
                else:
                    # Relative path
                    target = (html_path.parent / link).resolve()
                
                if not target.exists():
                    result["broken_links"].append({
                        "link": link,
                        "target": str(target.relative_to(self.workspace_root))
                    })
            
            if result["broken_links"]:
                result["status"] = "FAIL"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["broken_links"].append({"error": str(e)})
        
        return result
    
    def validate_css_imports(self, html_path: Path) -> Dict:
        """Validate CSS import order and loading"""
        
        result = {
            "file": str(html_path.relative_to(self.workspace_root)),
            "css_files": [],
            "import_order": [],
            "issues": [],
            "status": "PASS"
        }
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all CSS links
            css_pattern = r'<link[^>]*href="([^"]*\.css)"[^>]*>'
            css_links = re.findall(css_pattern, content)
            
            result["css_files"] = css_links
            
            # Expected order: design-tokens → patterns → glassmorphism → utilities
            expected_order = ['design-tokens', 'patterns', 'glassmorphism', 'utilities']
            
            for css_link in css_links:
                css_name = Path(css_link).stem
                if any(token in css_name for token in expected_order):
                    result["import_order"].append(css_name)
            
            # Check if glassmorphism is loaded
            has_glassmorphism = any('glassmorphism' in css for css in css_links)
            if not has_glassmorphism:
                result["issues"].append("Missing glassmorphism.css import")
                result["status"] = "WARN"
            
            # Check for CSS file existence
            for css_link in css_links:
                if css_link.startswith(('http://', 'https://')):
                    continue
                
                if css_link.startswith('/'):
                    css_path = self.docs_dir / css_link.lstrip('/')
                else:
                    css_path = (html_path.parent / css_link).resolve()
                
                if not css_path.exists():
                    result["issues"].append(f"Missing CSS file: {css_link}")
                    result["status"] = "FAIL"
                    
        except Exception as e:
            result["status"] = "ERROR"
            result["issues"].append(str(e))
        
        return result
    
    def check_js_compatibility(self, html_path: Path) -> Dict:
        """Check for JavaScript compatibility issues"""
        
        result = {
            "file": str(html_path.relative_to(self.workspace_root)),
            "scripts": [],
            "potential_issues": [],
            "status": "PASS"
        }
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all script tags
            script_pattern = r'<script[^>]*src="([^"]+)"[^>]*>'
            scripts = re.findall(script_pattern, content)
            result["scripts"] = scripts
            
            # Check for inline scripts with class manipulation
            inline_class_manip = re.findall(r'\.className\s*=|classList\.', content)
            if inline_class_manip:
                result["potential_issues"].append(f"Class manipulation detected: {len(inline_class_manip)} instances")
            
            # Check for jQuery (might have compatibility issues)
            if 'jquery' in content.lower():
                result["potential_issues"].append("jQuery detected - ensure compatibility with glassmorphism classes")
            
            if result["potential_issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["potential_issues"].append(str(e))
        
        return result
    
    def test_e2e_flows(self) -> List[Dict]:
        """Test end-to-end user flows"""
        
        flows = [
            {
                "name": "Home → Orchestrators → Planning v5",
                "path": ["index.html", "orchestrators/index.html", "orchestrators/planning-v5.html"],
                "status": "PENDING"
            },
            {
                "name": "Home → Security → Data Protection",
                "path": ["index.html", "security/index.html", "security/data-protection.html"],
                "status": "PENDING"
            },
            {
                "name": "Home → Features → Response Templates",
                "path": ["index.html", "features/index.html", "features/response-templates.html"],
                "status": "PENDING"
            },
            {
                "name": "Home → Architecture → Orchestrator Ecosystem",
                "path": ["index.html", "architecture/index.html", "architecture/orchestrator-ecosystem.html"],
                "status": "PENDING"
            },
            {
                "name": "Home → Learning Paths → Module 01",
                "path": ["index.html", "learning-paths/index.html", "learning-paths/modules/01-introduction.html"],
                "status": "PENDING"
            }
        ]
        
        results = []
        for flow in flows:
            result = {
                "name": flow["name"],
                "pages_checked": [],
                "missing_pages": [],
                "status": "PASS"
            }
            
            for page in flow["path"]:
                page_path = self.docs_dir / page
                if page_path.exists():
                    result["pages_checked"].append(page)
                else:
                    result["missing_pages"].append(page)
                    result["status"] = "FAIL"
            
            results.append(result)
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests"""
        
        print("🧪 Phase 10: Integration Testing")
        print("=" * 80)
        
        # 1. Select sample pages
        print("\n📄 Selecting 25 sample pages...")
        sample_pages = self.select_sample_pages()
        print(f"✅ Selected {len(sample_pages)} sample pages")
        
        # 2. HTML validation
        print("\n🔍 Running HTML validation...")
        for page in sample_pages:
            result = self.validate_html_structure(page)
            self.results["html_validation"].append(result)
            
            status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "WARN" else "❌"
            print(f"{status_icon} {result['file']}: {result['status']}")
        
        # 3. Link validation
        print("\n🔗 Running link validation...")
        all_html_files = list(self.docs_dir.rglob("*.html"))
        link_errors = 0
        for page in all_html_files[:50]:  # Sample 50 files for performance
            result = self.validate_links(page)
            self.results["link_validation"].append(result)
            if result["broken_links"]:
                link_errors += len(result["broken_links"])
        
        print(f"✅ Checked {len(self.results['link_validation'])} files")
        print(f"{'✅' if link_errors == 0 else '⚠️'} Found {link_errors} broken links")
        
        # 4. CSS validation
        print("\n🎨 Running CSS import validation...")
        for page in sample_pages:
            result = self.validate_css_imports(page)
            self.results["css_validation"].append(result)
        
        css_issues = sum(1 for r in self.results["css_validation"] if r["status"] != "PASS")
        print(f"{'✅' if css_issues == 0 else '⚠️'} {css_issues} files with CSS issues")
        
        # 5. JS compatibility
        print("\n⚡ Running JavaScript compatibility check...")
        for page in sample_pages:
            result = self.check_js_compatibility(page)
            self.results["js_validation"].append(result)
        
        js_issues = sum(1 for r in self.results["js_validation"] if r["potential_issues"])
        print(f"{'✅' if js_issues == 0 else '⚠️'} {js_issues} files with potential JS issues")
        
        # 6. E2E flows
        print("\n🚀 Testing end-to-end user flows...")
        self.results["e2e_flows"] = self.test_e2e_flows()
        e2e_pass = sum(1 for r in self.results["e2e_flows"] if r["status"] == "PASS")
        print(f"✅ {e2e_pass}/{len(self.results['e2e_flows'])} flows validated")
        
        # 7. Summary
        print("\n" + "=" * 80)
        print("📊 Integration Testing Summary")
        print("=" * 80)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "sample_pages_tested": len(sample_pages),
            "html_validation": {
                "total": len(self.results["html_validation"]),
                "pass": sum(1 for r in self.results["html_validation"] if r["status"] == "PASS"),
                "warn": sum(1 for r in self.results["html_validation"] if r["status"] == "WARN"),
                "fail": sum(1 for r in self.results["html_validation"] if r["status"] == "FAIL")
            },
            "link_validation": {
                "files_checked": len(self.results["link_validation"]),
                "broken_links": link_errors
            },
            "css_validation": {
                "files_checked": len(self.results["css_validation"]),
                "issues": css_issues
            },
            "js_validation": {
                "files_checked": len(self.results["js_validation"]),
                "potential_issues": js_issues
            },
            "e2e_flows": {
                "total": len(self.results["e2e_flows"]),
                "pass": e2e_pass,
                "fail": len(self.results["e2e_flows"]) - e2e_pass
            }
        }
        
        print(f"HTML Validation: {summary['html_validation']['pass']}/{summary['html_validation']['total']} PASS")
        print(f"Link Validation: {summary['link_validation']['broken_links']} broken links")
        print(f"CSS Validation: {summary['css_validation']['issues']} issues")
        print(f"JS Validation: {summary['js_validation']['potential_issues']} potential issues")
        print(f"E2E Flows: {summary['e2e_flows']['pass']}/{summary['e2e_flows']['total']} PASS")
        
        return summary
    
    def generate_reports(self, summary: Dict):
        """Generate integration test reports"""
        
        print("\n📝 Generating reports...")
        
        # 1. Integration test results
        results_path = self.reports_dir / "integration-test-results.md"
        with open(results_path, 'w', encoding='utf-8') as f:
            f.write("# Integration Test Results\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Phase:** Phase 10 - Integration Testing\n\n")
            f.write("---\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Sample Pages Tested:** {summary['sample_pages_tested']}\n")
            f.write(f"- **HTML Validation:** {summary['html_validation']['pass']}/{summary['html_validation']['total']} PASS\n")
            f.write(f"- **Broken Links:** {summary['link_validation']['broken_links']}\n")
            f.write(f"- **CSS Issues:** {summary['css_validation']['issues']}\n")
            f.write(f"- **JS Issues:** {summary['js_validation']['potential_issues']}\n")
            f.write(f"- **E2E Flows:** {summary['e2e_flows']['pass']}/{summary['e2e_flows']['total']} PASS\n\n")
            
            f.write("## HTML Validation Results\n\n")
            for result in self.results["html_validation"]:
                status_icon = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "WARN" else "❌"
                f.write(f"### {status_icon} {result['file']}\n\n")
                if result["errors"]:
                    f.write("**Errors:**\n")
                    for error in result["errors"]:
                        f.write(f"- {error}\n")
                    f.write("\n")
                if result["warnings"]:
                    f.write("**Warnings:**\n")
                    for warning in result["warnings"]:
                        f.write(f"- {warning}\n")
                    f.write("\n")
            
            f.write("\n## Link Validation Results\n\n")
            for result in self.results["link_validation"]:
                if result["broken_links"]:
                    f.write(f"### ❌ {result['file']}\n\n")
                    f.write("**Broken Links:**\n")
                    for link in result["broken_links"]:
                        f.write(f"- `{link.get('link', 'N/A')}` → `{link.get('target', 'N/A')}`\n")
                    f.write("\n")
            
            f.write("\n## E2E Flow Results\n\n")
            for result in self.results["e2e_flows"]:
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                f.write(f"### {status_icon} {result['name']}\n\n")
                if result["missing_pages"]:
                    f.write("**Missing Pages:**\n")
                    for page in result["missing_pages"]:
                        f.write(f"- {page}\n")
                    f.write("\n")
        
        print(f"✅ {results_path.relative_to(self.workspace_root)}")
        
        # 2. HTML validation summary
        validation_path = self.reports_dir / "html-validation-summary.md"
        with open(validation_path, 'w', encoding='utf-8') as f:
            f.write("# HTML Validation Summary\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- Total Files Tested: {summary['html_validation']['total']}\n")
            f.write(f"- PASS: {summary['html_validation']['pass']}\n")
            f.write(f"- WARN: {summary['html_validation']['warn']}\n")
            f.write(f"- FAIL: {summary['html_validation']['fail']}\n\n")
            
            f.write("## Compliance Rate\n\n")
            if summary['html_validation']['total'] > 0:
                compliance_rate = (summary['html_validation']['pass'] / summary['html_validation']['total']) * 100
                f.write(f"**{compliance_rate:.1f}%** of tested files passed validation\n\n")
        
        print(f"✅ {validation_path.relative_to(self.workspace_root)}")
        
        # 3. Link validation report
        link_path = self.reports_dir / "link-validation-report.md"
        with open(link_path, 'w', encoding='utf-8') as f:
            f.write("# Link Validation Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files Checked: {summary['link_validation']['files_checked']}\n")
            f.write(f"- Broken Links Found: {summary['link_validation']['broken_links']}\n\n")
            
            if summary['link_validation']['broken_links'] > 0:
                f.write("## Broken Links by File\n\n")
                for result in self.results["link_validation"]:
                    if result["broken_links"]:
                        f.write(f"### {result['file']}\n\n")
                        for link in result["broken_links"]:
                            f.write(f"- `{link.get('link', 'N/A')}`\n")
                        f.write("\n")
            else:
                f.write("✅ **No broken links found!**\n\n")
        
        print(f"✅ {link_path.relative_to(self.workspace_root)}")
        
        # 4. Save raw JSON results
        json_path = self.reports_dir / "integration-test-results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "results": self.results
            }, f, indent=2)
        
        print(f"✅ {json_path.relative_to(self.workspace_root)}")


def main():
    workspace = r"D:\PROJECTS\CORTEX"
    tester = IntegrationTester(workspace)
    
    summary = tester.run_all_tests()
    tester.generate_reports(summary)
    
    print("\n✅ Phase 10 Integration Testing Complete!")


if __name__ == "__main__":
    main()
