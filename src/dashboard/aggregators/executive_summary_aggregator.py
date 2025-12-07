"""
Executive Summary Aggregator

Generates project-adaptive executive summary from all collectors

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta


class ExecutiveSummaryAggregator:
    """Generates project-adaptive executive summary"""
    
    def __init__(self, data_dir: Path, repo_path: Path = None):
        self.data_dir = data_dir
        self.repo_path = repo_path or Path(f"C:/PROJECTS/{data_dir.name}")
    
    def aggregate(self) -> Dict[str, Any]:
        """Generate executive-summary.json from all collectors"""
        
        # Load source data
        tech = self._load_json("tech-stack.json")
        architecture = self._load_json("architecture.json")
        health = self._load_json("health-data.json")
        security = self._load_json("security.json")
        code_org = self._load_json("code-organization.json")
        
        # Detect project type
        project_type = self._detect_project_type(tech, architecture)
        
        # Generate adaptive tagline
        tagline = self._generate_tagline(project_type, tech)
        
        # Generate what_it_does
        what_it_does = self._generate_what_it_does(project_type, tech, architecture)
        
        # Get recent activity
        recent_activity = self._get_recent_activity()
        
        # Build composition
        composition = self._build_composition(tech, architecture)
        
        # Build tech stack summary
        tech_stack_summary = self._build_tech_summary(tech)
        
        # Build health indicators
        health_indicators = self._build_health_indicators(health, security, code_org)
        
        return {
            "project_name": self.data_dir.name.replace("-", " ").title(),
            "tagline": tagline,
            "what_it_does": what_it_does,
            "recent_activity": recent_activity,
            "composition": composition,
            "tech_stack_summary": tech_stack_summary,
            "health_indicators": health_indicators
        }
    
    def _detect_project_type(self, tech: Dict, architecture: Dict) -> str:
        """Detect project type for adaptive content"""
        
        # Check for frontend frameworks
        has_frontend = len(tech.get("frontend", [])) > 0
        has_backend = len(tech.get("backend", [])) > 0
        has_database = len(tech.get("database", [])) > 0
        
        app_type = architecture.get("application_type", {})
        detected_type = app_type.get("type", "").lower()
        
        # Check technologies for age
        backend_techs = tech.get("backend", [])
        is_legacy = any(
            ".net framework" in t.get("name", "").lower() or
            "soap" in t.get("name", "").lower() or
            "classic asp" in t.get("name", "").lower()
            for t in backend_techs
        )
        
        if "soap" in detected_type or is_legacy:
            return "legacy_service"
        elif has_frontend and has_backend:
            return "full_stack_app"
        elif has_backend and not has_frontend:
            return "api_service"
        elif "desktop" in detected_type:
            return "desktop_app"
        elif "mobile" in detected_type:
            return "mobile_app"
        else:
            return "application"
    
    def _generate_tagline(self, project_type: str, tech: Dict) -> str:
        """Generate project-adaptive tagline"""
        
        primary_tech = ""
        backend_techs = tech.get("backend", [])
        if backend_techs:
            primary_tech = backend_techs[0].get("name", "")
        
        taglines = {
            "legacy_service": f"Enterprise-grade {primary_tech} SOAP service",
            "full_stack_app": f"Modern web application built with {primary_tech}",
            "api_service": f"RESTful API service powered by {primary_tech}",
            "desktop_app": f"Desktop application built with {primary_tech}",
            "mobile_app": f"Mobile application built with {primary_tech}",
            "application": f"Software application built with {primary_tech}"
        }
        
        return taglines.get(project_type, f"Application built with {primary_tech}")
    
    def _generate_what_it_does(self, project_type: str, tech: Dict, architecture: Dict) -> Dict[str, Any]:
        """Generate what_it_does section"""
        
        app_type = architecture.get("application_type", {})
        evidence = app_type.get("evidence", [])
        
        # Try to extract purpose from README
        readme_content = ""
        for readme_name in ["README.md", "readme.md", "README.txt"]:
            readme_path = self.repo_path / readme_name
            if readme_path.exists():
                try:
                    readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    break
                except:
                    pass
        
        # Extract first meaningful paragraph
        summary = "A software application"
        if readme_content:
            lines = [l.strip() for l in readme_content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if lines:
                summary = lines[0][:500]  # First paragraph, max 500 chars
        
        # Build key points from evidence
        key_points = evidence[:5] if evidence else [
            f"Built with {tech.get('backend', [{}])[0].get('name', 'modern technologies')}",
            f"Uses {tech.get('database', [{}])[0].get('name', 'database')} for data storage" if tech.get('database') else "Database-backed application",
            f"{architecture.get('summary', {}).get('total_components', 0)} components",
            f"{architecture.get('summary', {}).get('total_loc', 0)} lines of code"
        ]
        
        return {
            "summary": summary,
            "key_points": key_points,
            "source": "hybrid"
        }
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent git activity"""
        
        if not self.repo_path.exists() or not (self.repo_path / ".git").exists():
            return []
        
        try:
            # Get last 10 commits
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso", "-10"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            activities = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        activities.append({
                            "commit_hash": parts[0][:8],
                            "author": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
            
            return activities
        except:
            return []
    
    def _build_composition(self, tech: Dict, architecture: Dict) -> Dict[str, Any]:
        """Build composition section"""
        
        arch_style = architecture.get("style", {})
        
        # Build components from architecture tiers
        components = []
        for tier in architecture.get("tiers", [])[:6]:  # Top 6 tiers
            components.append({
                "name": tier.get("name", "Component"),
                "technology": ", ".join(tier.get("technologies", [])[:3]),
                "purpose": tier.get("description", ""),
                "files_count": tier.get("file_count", 0)
            })
        
        return {
            "architecture_style": arch_style.get("name", "Application Architecture"),
            "components": components,
            "relationships": arch_style.get("characteristics", [])[:5]
        }
    
    def _build_tech_summary(self, tech: Dict) -> Dict[str, Any]:
        """Build tech stack summary"""
        
        summary = tech.get("summary", {})
        
        # Get top 5 technologies across all categories
        all_techs = []
        for category in ["frontend", "backend", "database", "devops"]:
            all_techs.extend(tech.get(category, []))
        
        top_techs = [
            {
                "name": t.get("name", ""),
                "version": t.get("version", "unknown"),
                "category": t.get("category", "unknown")
            }
            for t in all_techs[:5]
        ]
        
        return {
            "total_technologies": summary.get("total_technologies", 0),
            "primary_technologies": top_techs,
            "outdated_count": summary.get("outdated_count", 0),
            "critical_updates_needed": summary.get("critical_cves", 0)
        }
    
    def _build_health_indicators(self, health: Dict, security: Dict, code_org: Dict) -> List[Dict[str, Any]]:
        """Build health indicators"""
        
        indicators = []
        
        # Code quality
        quality_score = health.get("metrics", {}).get("code_quality_score", 75)
        indicators.append({
            "name": "Code Quality",
            "value": f"{quality_score}%",
            "status": "healthy" if quality_score >= 70 else "warning",
            "trend": "stable"
        })
        
        # Security
        security_score = security.get("overall_score", 100)
        indicators.append({
            "name": "Security",
            "value": f"{security_score}%",
            "status": "healthy" if security_score >= 90 else "warning",
            "trend": "stable"
        })
        
        # Technical debt
        tech_debt = code_org.get("summary", {}).get("technical_debt_hours", 0)
        indicators.append({
            "name": "Technical Debt",
            "value": f"{tech_debt:.1f}h",
            "status": "healthy" if tech_debt < 50 else "warning",
            "trend": "stable"
        })
        
        return indicators
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except:
                return {}
        return {}


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python executive_summary_aggregator.py <data_dir> [repo_path]")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    aggregator = ExecutiveSummaryAggregator(data_dir, repo_path)
    result = aggregator.aggregate()
    
    output_path = data_dir / "executive-summary.json"
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
