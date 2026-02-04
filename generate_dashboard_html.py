#!/usr/bin/env python3
"""
Generate static HTML dashboards for each repository.

This script:
1. Creates repository-specific JSON data (metrics, security, dependencies, etc.)
2. Embeds the JSON directly into HTML files
3. Generates static dashboard pages that work on file:// protocol

Usage:
    python generate_dashboard_html.py [--repo REPO_NAME] [--clean]
    
    --repo REPO_NAME    Generate only specified repo (cortex, ksessions, kashkole)
    --clean             Delete all generated dashboards first
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
import shutil


# Repository configurations with sample data
REPOSITORY_CONFIGS = {
    "cortex": {
        "display_name": "CORTEX",
        "slug": "cortex",
        "description": "Cognitive Real-Time Execution System - AI orchestration platform for enterprise applications",
        "primary_language": "Python",
        "version": "8.2",
        "repo_url": "https://github.com/cortex-ai/cortex",
        "stats": {
            "stars": 2847,
            "forks": 234,
            "issues": 45,
            "pull_requests": 12,
        }
    },
    "ksessions": {
        "display_name": "KSESSIONS",
        "slug": "ksessions",
        "description": "Kubernetes session management and distributed computing framework",
        "primary_language": "Go",
        "version": "3.1",
        "repo_url": "https://github.com/ksessions/ksessions",
        "stats": {
            "stars": 1203,
            "forks": 89,
            "issues": 23,
            "pull_requests": 8,
        }
    },
    "kashkole": {
        "display_name": "KASHKOLE",
        "slug": "kashkole",
        "description": "Modern TypeScript web framework with reactive components and state management",
        "primary_language": "TypeScript",
        "version": "2.4",
        "repo_url": "https://github.com/kashkole/kashkole",
        "stats": {
            "stars": 856,
            "forks": 67,
            "issues": 34,
            "pull_requests": 15,
        }
    }
}


def create_dashboard_data(repo_config):
    """Create comprehensive dashboard data for a repository."""
    
    return {
        "repo": {
            "slug": repo_config["slug"],
            "display_name": repo_config["display_name"],
            "owner": "CORTEX Team",
            "primary_language": repo_config["primary_language"],
            "version": repo_config["version"],
            "last_analyzed_at": datetime.now().isoformat() + "Z"
        },
        "metrics": {
            "health_score": 87,
            "risk_score": 13,
            "loc": 45821,
            "files": 342,
            "coverage_pct": 82.0
        },
        "overview": {
            "summary": repo_config["description"],
            "business_summary": f"Enterprise-grade {repo_config['primary_language']} system providing advanced capabilities for production environments.",
            "total_files": 342,
            "total_lines": 45821,
            "last_commit": "2 hours ago",
            "contributors": 12,
        },
        "use_cases": [
            {
                "title": "Architecture Analysis",
                "description": "Analyze codebase structure and design patterns",
                "category": "analysis",
                "persona": "architect"
            },
            {
                "title": "Security Assessment",
                "description": "Identify and prioritize security issues",
                "category": "security",
                "persona": "security-lead"
            },
            {
                "title": "Quality Metrics",
                "description": "Track code quality and technical debt",
                "category": "quality",
                "persona": "tech-lead"
            }
        ],
        "dependencies": {
            "internal": ["cortex-core", "cortex-lens"],
            "external": ["fastapi", "pydantic", "sqlalchemy"]
        },
        "quality": {
            "issues": [
                {
                    "type": "Long Method",
                    "location": "core/orchestrator.py:245",
                    "severity": "medium",
                    "count": 3
                },
                {
                    "type": "Duplicate Code",
                    "location": "lens/analyzers.py:120-180",
                    "severity": "low",
                    "count": 2
                }
            ],
            "metrics": {
                "cyclomatic_complexity": 3.2,
                "maintainability_index": 78,
                "technical_debt_ratio": 5.2
            }
        },
        "security": {
            "total_count": 2,
            "vulnerabilities": [
                {
                    "id": "CVE-2024-001",
                    "title": "Dependency Update Required",
                    "severity": "medium",
                    "status": "in_progress"
                },
                {
                    "id": "SONAR-2024-045",
                    "title": "SQL Injection Risk",
                    "severity": "high",
                    "status": "open"
                }
            ]
        },
        "testing": {
            "total_tests": 285,
            "pass_rate": 98
        },
        "refactoring": {
            "candidates": [
                {
                    "file": "core/orchestrator.py",
                    "reason": "High complexity",
                    "priority": "high"
                }
            ]
        }
    }


def load_template(template_path):
    """Load the template HTML file."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def inject_dashboard_data(html_content, dashboard_data):
    """Inject dashboard data into HTML template."""
    
    # Convert data to JSON string with indentation
    data_json = json.dumps(dashboard_data, indent=4)
    
    # Find the start and end of the embedded data script
    start_marker = '    <script type="application/json" id="dashboard-data">'
    end_marker = '    </script>'
    
    # Build the replacement with proper indentation
    replacement = f'{start_marker}\n    {data_json}\n    {end_marker}'
    
    # Find the current embedded data section
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find dashboard-data script markers in template")
    
    # Get everything before and after
    before = html_content[:start_idx]
    after = html_content[end_idx + len(end_marker):]
    
    return before + replacement + after


def update_page_title(html_content, repo_name):
    """Update page title to include repository name."""
    return html_content.replace(
        '<title data-bind="repo.display_name">Repository Dashboard</title> | CORTEX',
        f'<title>{repo_name} Dashboard | CORTEX</title>'
    )


def generate_dashboard_html(repo_name, template_path, output_path):
    """Generate a single dashboard HTML file."""
    
    if repo_name not in REPOSITORY_CONFIGS:
        raise ValueError(f"Unknown repository: {repo_name}")
    
    repo_config = REPOSITORY_CONFIGS[repo_name]
    
    # Create dashboard data
    dashboard_data = create_dashboard_data(repo_config)
    
    # Load template
    html_content = load_template(template_path)
    
    # Inject data
    html_content = inject_dashboard_data(html_content, dashboard_data)
    
    # Update title
    html_content = update_page_title(html_content, repo_config["display_name"])
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def main():
    """Generate all dashboard HTML files."""
    
    parser = argparse.ArgumentParser(description='Generate static HTML dashboards')
    parser.add_argument('--repo', help='Generate only specific repository (cortex, ksessions, kashkole)')
    parser.add_argument('--clean', action='store_true', help='Delete existing dashboards first')
    args = parser.parse_args()
    
    # Paths
    cortex_root = Path(__file__).parent
    template_path = cortex_root / 'company' / 'dashboards' / 'repos' / '_template' / 'index.html'
    dashboards_dir = cortex_root / 'company' / 'dashboards' / 'repos'
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return 1
    
    # Clean existing dashboards if requested
    if args.clean:
        for repo_name in REPOSITORY_CONFIGS.keys():
            repo_dir = dashboards_dir / repo_name
            if repo_dir.exists() and repo_name != '_template':
                print(f"🗑️  Removing existing dashboard: {repo_dir}")
                shutil.rmtree(repo_dir)
    
    # Determine which repos to generate
    repos_to_generate = [args.repo] if args.repo else list(REPOSITORY_CONFIGS.keys())
    
    # Generate dashboards
    print("\n" + "="*70)
    print("📊 CORTEX Dashboard HTML Generation")
    print("="*70)
    
    generated_files = []
    
    for repo_name in repos_to_generate:
        if repo_name not in REPOSITORY_CONFIGS:
            print(f"❌ Unknown repository: {repo_name}")
            continue
        
        try:
            repo_config = REPOSITORY_CONFIGS[repo_name]
            output_path = dashboards_dir / repo_name / 'index.html'
            
            # Create directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate HTML
            generated_path = generate_dashboard_html(repo_name, template_path, output_path)
            generated_files.append(generated_path)
            
            print(f"✅ Generated: {repo_config['display_name']}")
            print(f"   Output: {generated_path.relative_to(cortex_root)}")
            print(f"   Size: {generated_path.stat().st_size:,} bytes")
            
        except Exception as e:
            print(f"❌ Failed to generate {repo_name}: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    # Summary
    print("\n" + "="*70)
    print(f"✅ Successfully generated {len(generated_files)} dashboard(s)")
    print("="*70)
    
    # Test instructions
    print("\n📝 Next Steps:")
    print("\n1. Open dashboards in browser:")
    for repo_name in repos_to_generate:
        repo_path = (dashboards_dir / repo_name / 'index.html').relative_to(cortex_root)
        print(f"   - file://{cortex_root}/{repo_path}")
    
    print("\n2. Or serve via HTTP:")
    print(f"   cd {cortex_root}")
    print("   python3 -m http.server 8000")
    print("   Then visit: http://localhost:8000/company/dashboards/repos/cortex/")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
