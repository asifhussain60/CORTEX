"""
Post-Deployment Validation System

Purpose: Validate CORTEX production readiness after deployment
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

Validates:
- Feature wiring (TDD, Planning, ADO, etc.)
- Response templates completeness
- Documentation synchronization
- Agent functionality
- Database schema integrity
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import sqlite3
import yaml
import importlib.util
from src.utils.resource_resolver import get_root_path

# Add src to path for imports
cortex_root = get_root_path()
sys.path.insert(0, str(cortex_root / "src"))


class PostDeploymentValidator:
    """Comprehensive post-deployment validation for CORTEX production readiness."""
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize validator.
        
        Args:
            cortex_root: Path to CORTEX root directory (default: auto-detect)
        """
        self.cortex_root = cortex_root or get_root_path()
        self.brain_path = self.cortex_root / "cortex-brain"
        self.src_path = self.cortex_root / "src"
        
        self.results = {
            "feature_wiring": {},
            "templates": {},
            "documentation": {},
            "agents": {},
            "databases": {},
            "overall_status": "unknown"
        }
        
        self.issues = []
        self.warnings = []
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (success: bool, results: dict)
        """
        print("=" * 80)
        print("CORTEX POST-DEPLOYMENT VALIDATION")
        print("=" * 80)
        print()
        
        # Run all validation categories
        self._validate_feature_wiring()
        self._validate_response_templates()
        self._validate_documentation()
        self._validate_agents()
        self._validate_databases()
        
        # Determine overall status
        success = len(self.issues) == 0
        self.results["overall_status"] = "PASS" if success else "FAIL"
        self.results["issues"] = self.issues
        self.results["warnings"] = self.warnings
        self.results["timestamp"] = datetime.now().isoformat()
        
        # Print summary
        self._print_summary()
        
        return success, self.results
    
    def _validate_feature_wiring(self):
        """Validate all critical features are wired correctly."""
        print("🔌 Validating Feature Wiring...")
        print("-" * 80)
        
        features_to_check = {
            "TDD Mastery": {
                "orchestrator": "src/workflows/tdd_workflow_orchestrator.py",
                "triggers": ["start tdd", "tdd workflow"],
                "template": "tdd_workflow_start"
            },
            "Planning System": {
                "orchestrator": "src/orchestrators/planning_orchestrator.py",
                "triggers": ["plan", "let's plan"],
                "template": "work_planner_success"
            },
            "ADO Integration": {
                "orchestrator": "src/orchestrators/swagger_entry_point_orchestrator.py",
                "triggers": ["plan ado", "ado story"],
                "template": "ado_planning"
            },
            "View Discovery": {
                "agent": "src/cortex_agents/view_discovery_agent.py",
                "triggers": ["discover views"],
                "template": None  # Integrated with TDD
            },
            "Feedback System": {
                "agent": "src/cortex_agents/feedback_agent.py",
                "triggers": ["feedback", "report issue"],
                "template": "feedback_received"
            },
            "Upgrade System": {
                "orchestrator": "src/orchestrators/upgrade_orchestrator.py",
                "triggers": ["upgrade", "upgrade cortex"],
                "template": "upgrade_cortex"
            },
            "Architecture Intelligence": {
                "agent": "src/cortex_agents/strategic/architecture_intelligence_agent.py",
                "triggers": ["review architecture", "cortex health"],
                "template": "architecture_intelligence"
            }
        }
        
        # Load response templates
        templates = self._load_response_templates()
        
        for feature_name, config in features_to_check.items():
            feature_issues = []
            
            if "orchestrator" in config:
                file_path = self.cortex_root / config["orchestrator"]
                if not file_path.exists():
                    feature_issues.append(f"Orchestrator missing: {config['orchestrator']}")
                else:
                    # Try to import
                    if not self._can_import_module(file_path):
                        feature_issues.append(f"Orchestrator import failed: {config['orchestrator']}")
            
            if "agent" in config:
                file_path = self.cortex_root / config["agent"]
                if not file_path.exists():
                    feature_issues.append(f"Agent missing: {config['agent']}")
                else:
                    # Try to import
                    if not self._can_import_module(file_path):
                        feature_issues.append(f"Agent import failed: {config['agent']}")
            
            if templates and config.get("triggers"):
                triggers_found = False
                for trigger in config["triggers"]:
                    if self._trigger_exists_in_templates(trigger, templates):
                        triggers_found = True
                        break
                
                if not triggers_found:
                    feature_issues.append(f"No triggers found in response-templates.yaml: {config['triggers']}")
            
            if config.get("template"):
                if not templates or config["template"] not in templates.get("templates", {}):
                    feature_issues.append(f"Template missing: {config['template']}")
            
            # Store results
            if feature_issues:
                self.results["feature_wiring"][feature_name] = {
                    "status": "FAIL",
                    "issues": feature_issues
                }
                self.issues.extend([f"{feature_name}: {issue}" for issue in feature_issues])
                print(f"  ❌ {feature_name}: {len(feature_issues)} issue(s)")
            else:
                self.results["feature_wiring"][feature_name] = {
                    "status": "PASS",
                    "issues": []
                }
                print(f"  ✅ {feature_name}")
        
        print()
    
    def _validate_response_templates(self):
        """Validate response templates completeness."""
        print("📋 Validating Response Templates...")
        print("-" * 80)
        
        templates_file = self.brain_path / "response-templates.yaml"
        
        if not templates_file.exists():
            self.issues.append("response-templates.yaml missing")
            self.results["templates"]["status"] = "FAIL"
            print("  ❌ response-templates.yaml not found")
            print()
            return
        
        try:
            templates = self._load_response_templates()
            
            critical_templates = [
                "fallback",
                "help_table",
                "work_planner_success",
                "tdd_workflow_start",
                "feedback_received",
                "upgrade_cortex",
                "architecture_intelligence"
            ]
            
            missing_templates = []
            for template_name in critical_templates:
                if template_name not in templates.get("templates", {}):
                    missing_templates.append(template_name)
            
            if missing_templates:
                self.issues.append(f"Missing critical templates: {', '.join(missing_templates)}")
                self.results["templates"]["status"] = "FAIL"
                self.results["templates"]["missing"] = missing_templates
                print(f"  ❌ {len(missing_templates)} critical template(s) missing")
            else:
                self.results["templates"]["status"] = "PASS"
                self.results["templates"]["count"] = len(templates.get("templates", {}))
                print(f"  ✅ All critical templates present ({len(templates.get('templates', {}))} total)")
        
        except Exception as e:
            self.issues.append(f"response-templates.yaml validation failed: {str(e)}")
            self.results["templates"]["status"] = "FAIL"
            print(f"  ❌ Validation error: {str(e)}")
        
        print()
    
    def _validate_documentation(self):
        """Validate documentation synchronization."""
        print("📚 Validating Documentation...")
        print("-" * 80)
        
        entry_point = self.cortex_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if not entry_point.exists():
            self.issues.append("CORTEX.prompt.md missing")
            self.results["documentation"]["status"] = "FAIL"
            print("  ❌ CORTEX.prompt.md not found")
            print()
            return
        
        modules_path = self.cortex_root / ".github" / "prompts" / "modules"
        critical_modules = [
            "response-format.md",
            "template-guide.md",
            "tdd-mastery-guide.md",
            "planning-orchestrator-guide.md",
            "architecture-intelligence-guide.md",
            "upgrade-guide.md"
        ]
        
        missing_modules = []
        for module in critical_modules:
            if not (modules_path / module).exists():
                missing_modules.append(module)
        
        if missing_modules:
            self.issues.append(f"Missing module guides: {', '.join(missing_modules)}")
            self.results["documentation"]["status"] = "FAIL"
            self.results["documentation"]["missing_modules"] = missing_modules
            print(f"  ❌ {len(missing_modules)} module guide(s) missing")
        else:
            self.results["documentation"]["status"] = "PASS"
            self.results["documentation"]["modules_count"] = len(critical_modules)
            print(f"  ✅ All critical module guides present ({len(critical_modules)} total)")
        
        print()
    
    def _validate_agents(self):
        """Validate all agents are importable."""
        print("🤖 Validating Agents...")
        print("-" * 80)
        
        agents_path = self.src_path / "cortex_agents"
        
        if not agents_path.exists():
            self.issues.append("cortex_agents directory missing")
            self.results["agents"]["status"] = "FAIL"
            print("  ❌ cortex_agents directory not found")
            print()
            return
        
        # Find all agent files
        agent_files = list(agents_path.rglob("*_agent.py"))
        
        failed_imports = []
        for agent_file in agent_files:
            if not self._can_import_module(agent_file):
                relative_path = agent_file.relative_to(self.cortex_root)
                failed_imports.append(str(relative_path))
        
        if failed_imports:
            self.issues.append(f"Agent import failures: {len(failed_imports)}")
            self.results["agents"]["status"] = "FAIL"
            self.results["agents"]["failed_imports"] = failed_imports
            print(f"  ❌ {len(failed_imports)} agent(s) failed import")
            for agent in failed_imports[:5]:  # Show first 5
                print(f"     - {agent}")
            if len(failed_imports) > 5:
                print(f"     ... and {len(failed_imports) - 5} more")
        else:
            self.results["agents"]["status"] = "PASS"
            self.results["agents"]["count"] = len(agent_files)
            print(f"  ✅ All agents importable ({len(agent_files)} total)")
        
        print()
    
    def _validate_databases(self):
        """Validate database tier structure.
        
        NOTE: Does NOT check for specific database files as they are created
        on-demand by Tier classes during initialization. Only validates that
        tier directories exist for cross-platform compatibility.
        """
        print("💾 Validating Database Structure...")
        print("-" * 80)
        
        tier_dirs = {
            "Tier 1": self.brain_path / "tier1",
            "Tier 2": self.brain_path / "tier2",
            "Tier 3": self.brain_path / "tier3"
        }
        
        db_issues = []
        
        for tier_name, tier_path in tier_dirs.items():
            if not tier_path.exists():
                db_issues.append(f"{tier_name} directory missing: {tier_path}")
                continue
            
            # Check if directory is accessible
            if not tier_path.is_dir():
                db_issues.append(f"{tier_name} path exists but is not a directory: {tier_path}")
                continue
            
            # Optional: Check for any .db files (informational, not required)
            db_files = list(tier_path.glob("*.db"))
            if db_files:
                # Database files exist - try to validate schema
                for db_file in db_files:
                    try:
                        conn = sqlite3.connect(str(db_file))
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]
                        conn.close()
                        
                        if not tables:
                            self.warnings.append(f"{tier_name} database {db_file.name} has no tables (will be initialized on first use)")
                    except Exception as e:
                        db_issues.append(f"{tier_name} database {db_file.name} validation failed: {str(e)}")
        
        if db_issues:
            self.issues.extend(db_issues)
            self.results["databases"]["status"] = "FAIL"
            self.results["databases"]["issues"] = db_issues
            print(f"  ❌ {len(db_issues)} database issue(s)")
            for issue in db_issues:
                print(f"     - {issue}")
        else:
            self.results["databases"]["status"] = "PASS"
            self.results["databases"]["count"] = len(tier_dirs)
            print(f"  ✅ All tier directories valid ({len(tier_dirs)} tiers)")
            print(f"     Note: Database files created on-demand during initialization")
        
        print()
    
    def _load_response_templates(self) -> Optional[Dict]:
        """Load response templates YAML."""
        templates_file = self.brain_path / "response-templates.yaml"
        
        if not templates_file.exists():
            return None
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    def _trigger_exists_in_templates(self, trigger: str, templates: Dict) -> bool:
        """Check if trigger exists in any template."""
        for template_name, template_config in templates.get("templates", {}).items():
            triggers = template_config.get("triggers", [])
            if trigger in triggers:
                return True
        
        for route_name, route_triggers in templates.get("routing", {}).items():
            if trigger in route_triggers:
                return True
        
        return False
    
    def _can_import_module(self, file_path: Path) -> bool:
        """Test if module can be imported."""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec is None or spec.loader is None:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception:
            return False
    
    def _print_summary(self):
        """Print validation summary."""
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        # Status indicator
        if self.results["overall_status"] == "PASS":
            print("✅ OVERALL STATUS: PASS")
            print()
            print("   All validation checks passed. CORTEX is production ready.")
        else:
            print("❌ OVERALL STATUS: FAIL")
            print()
            print(f"   {len(self.issues)} issue(s) detected")
        
        print()
        
        # Category summary
        categories = [
            ("Feature Wiring", "feature_wiring"),
            ("Response Templates", "templates"),
            ("Documentation", "documentation"),
            ("Agents", "agents"),
            ("Databases", "databases")
        ]
        
        for category_name, category_key in categories:
            status = self.results[category_key].get("status", "UNKNOWN")
            if status == "PASS":
                print(f"  ✅ {category_name}")
            else:
                print(f"  ❌ {category_name}")
        
        print()
        
        # Issues
        if self.issues:
            print("📋 ISSUES FOUND:")
            print()
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
            print()
        
        # Warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            print()
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()
        
        print("=" * 80)
    
    def generate_html_report(self, output_path: Path):
        """Generate HTML validation report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Post-Deployment Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .status-pass {{ color: #27ae60; font-weight: bold; }}
        .status-fail {{ color: #e74c3c; font-weight: bold; }}
        .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .issue {{ color: #e74c3c; margin: 5px 0; }}
        .warning {{ color: #f39c12; margin: 5px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CORTEX Post-Deployment Validation Report</h1>
        <p>Generated: {self.results.get('timestamp', 'Unknown')}</p>
        <p>Status: <span class="status-{self.results['overall_status'].lower()}">{self.results['overall_status']}</span></p>
    </div>
    
    <div class="category">
        <h2>Feature Wiring</h2>
        <table>
            <tr><th>Feature</th><th>Status</th><th>Issues</th></tr>
"""
        
        for feature_name, result in self.results["feature_wiring"].items():
            status_class = "status-pass" if result["status"] == "PASS" else "status-fail"
            issues_str = "<br>".join(result["issues"]) if result["issues"] else "None"
            html += f"""
            <tr>
                <td>{feature_name}</td>
                <td class="{status_class}">{result["status"]}</td>
                <td>{issues_str}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="category">
        <h2>Response Templates</h2>
        <p>Status: <span class="status-{0}">{1}</span></p>
        <p>Total Templates: {2}</p>
    </div>
    
    <div class="category">
        <h2>Documentation</h2>
        <p>Status: <span class="status-{3}">{4}</span></p>
        <p>Module Guides: {5}</p>
    </div>
    
    <div class="category">
        <h2>Agents</h2>
        <p>Status: <span class="status-{6}">{7}</span></p>
        <p>Total Agents: {8}</p>
    </div>
    
    <div class="category">
        <h2>Databases</h2>
        <p>Status: <span class="status-{9}">{10}</span></p>
        <p>Database Tiers: {11}</p>
    </div>
""".format(
            self.results["templates"]["status"].lower(),
            self.results["templates"]["status"],
            self.results["templates"].get("count", "Unknown"),
            self.results["documentation"]["status"].lower(),
            self.results["documentation"]["status"],
            self.results["documentation"].get("modules_count", "Unknown"),
            self.results["agents"]["status"].lower(),
            self.results["agents"]["status"],
            self.results["agents"].get("count", "Unknown"),
            self.results["databases"]["status"].lower(),
            self.results["databases"]["status"],
            self.results["databases"].get("count", "Unknown")
        )
        
        if self.issues:
            html += """
    <div class="category">
        <h2>Issues</h2>
        <ul>
"""
            for issue in self.issues:
                html += f"            <li class='issue'>{issue}</li>\n"
            html += """
        </ul>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    """Main entry point for post-deployment validation."""
    validator = PostDeploymentValidator()
    success, results = validator.validate_all()
    
    # Generate reports
    reports_dir = validator.cortex_root / "cortex-brain" / "documents" / "reports"
    
    # HTML report
    html_path = reports_dir / "post-deployment-validation.html"
    validator.generate_html_report(html_path)
    print(f"📊 HTML report saved: {html_path}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
