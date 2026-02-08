"""
Pre-scan D:\PROJECTS repositories to identify extraction patterns.

Analyzes all repositories to build comprehensive extraction catalog
for enhancing LENS crawlers.

AC_START: AC-LENS-PRESCAN-001
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def prescan_repositories():
    """Scan all D:\PROJECTS repos and catalog patterns."""
    
    repos_path = Path("D:/PROJECTS")
    results = {
        "scan_date": datetime.now().isoformat(),
        "repositories": {},
        "pattern_catalog": defaultdict(lambda: {"count": 0, "examples": []}),
        "extraction_opportunities": []
    }
    
    exclude_dirs = {'.backup-archive', '.pytest_cache', 'scripts', 'node_modules', '.git', '__pycache__'}
    
    print("=" * 70)
    print("REPOSITORY PRE-SCAN: Pattern Discovery")
    print("=" * 70)
    
    for repo_dir in sorted(repos_path.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name in exclude_dirs:
            continue
        
        print(f"\nScanning: {repo_dir.name}")
        repo_data = scan_repository(repo_dir)
        results["repositories"][repo_dir.name] = repo_data
        
        # Update pattern catalog
        for pattern_type, items in repo_data["patterns"].items():
            results["pattern_catalog"][pattern_type]["count"] += len(items)
            results["pattern_catalog"][pattern_type]["examples"].extend(items[:3])
    
    # Generate extraction opportunities
    results["extraction_opportunities"] = generate_opportunities(results["pattern_catalog"])
    
    # Save results
    output_file = Path("d:/PROJECTS/CORTEX/.cortex/prescan_results.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print_summary(results)
    
    return results

def scan_repository(repo_path: Path) -> dict:
    """Scan single repository for patterns."""
    
    patterns = {
        "config_files": [],
        "api_endpoints": [],
        "ui_components": [],
        "database_models": [],
        "test_files": [],
        "build_configs": [],
        "third_party_configs": [],
        "route_definitions": [],
        "service_classes": [],
        "utility_functions": []
    }
    
    try:
        # Config files
        for pattern in ['*config*.js', '*config*.json', '*config*.yml', '*config*.yaml', '*.config.ts']:
            patterns["config_files"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # Third-party configs (high value for use cases)
        for config_name in ['froalaconfig.js', 'webpack.config.js', 'vite.config.js', 'rollup.config.js', 
                           'jest.config.js', 'eslint.config.js', 'tailwind.config.js', 'next.config.js']:
            matches = list(repo_path.rglob(config_name))
            if matches:
                patterns["third_party_configs"].extend([str(f.relative_to(repo_path)) for f in matches])
        
        # API endpoints
        for pattern in ['*route*.js', '*routes*.py', '*controller*.py', '*api*.cs', '*endpoint*.ts']:
            patterns["api_endpoints"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # UI components
        for pattern in ['*.jsx', '*.tsx', '*.vue', '*.razor', '*.svelte']:
            patterns["ui_components"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # Database models
        for pattern in ['*model*.py', '*schema*.py', '*entity*.cs', '*migration*.sql', '*schema*.sql']:
            patterns["database_models"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # Service classes
        for pattern in ['*service*.py', '*service*.js', '*service*.cs', '*manager*.py', '*handler*.py']:
            patterns["service_classes"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # Tests
        for pattern in ['*test*.py', '*.test.js', '*.spec.js', '*Test.cs']:
            patterns["test_files"].extend([str(f.relative_to(repo_path)) for f in repo_path.rglob(pattern) if is_valid_file(f)])
        
        # Build configs
        for build_file in ['package.json', 'setup.py', 'pyproject.toml', '*.csproj', 'Makefile', 'Dockerfile']:
            matches = list(repo_path.rglob(build_file))
            if matches:
                patterns["build_configs"].extend([str(f.relative_to(repo_path)) for f in matches[:10]])  # Limit to 10
        
    except Exception as e:
        print(f"  Error scanning {repo_path.name}: {e}")
    
    return {
        "patterns": {k: v for k, v in patterns.items() if v},  # Only non-empty
        "file_count": sum(len(v) for v in patterns.values()),
        "languages": detect_languages(repo_path)
    }

def is_valid_file(file_path: Path) -> bool:
    """Check if file should be included in scan."""
    exclude = {'node_modules', '.git', '__pycache__', 'dist', 'build', '.venv', 'venv'}
    return not any(ex in file_path.parts for ex in exclude) and file_path.is_file()

def detect_languages(repo_path: Path) -> list:
    """Detect programming languages in repository."""
    extensions = defaultdict(int)
    
    try:
        for file in repo_path.rglob('*'):
            if file.is_file() and is_valid_file(file):
                ext = file.suffix.lower()
                if ext:
                    extensions[ext] += 1
    except:
        pass
    
    # Map to languages
    ext_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React', '.tsx': 'React', '.vue': 'Vue',
        '.cs': 'C#', '.go': 'Go', '.rs': 'Rust',
        '.java': 'Java', '.rb': 'Ruby', '.php': 'PHP'
    }
    
    return [ext_map.get(ext, ext) for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:5]]

def generate_opportunities(pattern_catalog: dict) -> list:
    """Generate extraction opportunities based on patterns found."""
    
    opportunities = []
    
    # Third-party configs are high-value
    third_party_count = pattern_catalog.get("third_party_configs", {}).get("count", 0)
    if third_party_count > 0:
        opportunities.append({
            "priority": "P0",
            "type": "third_party_config_extractor",
            "rationale": f"Found {third_party_count} third-party configs (froala, webpack, etc.) - each can yield 5-10 use cases",
            "potential_use_cases": third_party_count * 7,
            "examples": pattern_catalog.get("third_party_configs", {}).get("examples", [])[:5]
        })
    
    # API endpoints
    api_count = pattern_catalog.get("api_endpoints", {}).get("count", 0)
    if api_count > 0:
        opportunities.append({
            "priority": "P0",
            "type": "api_endpoint_extractor",
            "rationale": f"Found {api_count} API files - each endpoint is a use case",
            "potential_use_cases": api_count * 3,
            "crawler_enhancement": "Parse route definitions, extract HTTP methods, parameters, responses"
        })
    
    # UI components
    ui_count = pattern_catalog.get("ui_components", {}).get("count", 0)
    if ui_count > 0:
        opportunities.append({
            "priority": "P1",
            "type": "ui_component_extractor",
            "rationale": f"Found {ui_count} UI components - user-facing features",
            "potential_use_cases": ui_count * 2,
            "crawler_enhancement": "Extract component props, events, user interactions"
        })
    
    # Database models
    db_count = pattern_catalog.get("database_models", {}).get("count", 0)
    if db_count > 0:
        opportunities.append({
            "priority": "P1",
            "type": "database_model_extractor",
            "rationale": f"Found {db_count} database models - data operations",
            "potential_use_cases": db_count * 2,
            "crawler_enhancement": "Extract model fields, relationships, CRUD operations"
        })
    
    # Service classes
    service_count = pattern_catalog.get("service_classes", {}).get("count", 0)
    if service_count > 0:
        opportunities.append({
            "priority": "P1",
            "type": "service_class_extractor",
            "rationale": f"Found {service_count} service classes - business logic",
            "potential_use_cases": service_count * 2,
            "crawler_enhancement": "Extract public methods, their purposes, business rules"
        })
    
    return sorted(opportunities, key=lambda x: x["priority"])

def print_summary(results: dict):
    """Print scan summary."""
    
    print(f"\nRepositories Scanned: {len(results['repositories'])}")
    print("\nPattern Catalog:")
    for pattern_type, data in sorted(results["pattern_catalog"].items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"  {pattern_type}: {data['count']} files")
    
    print("\nExtraction Opportunities:")
    total_potential = 0
    for opp in results["extraction_opportunities"]:
        print(f"\n  [{opp['priority']}] {opp['type']}")
        print(f"      Rationale: {opp['rationale']}")
        print(f"      Potential Use Cases: {opp.get('potential_use_cases', 'N/A')}")
        total_potential += opp.get('potential_use_cases', 0)
    
    print(f"\nTOTAL POTENTIAL USE CASES: {total_potential}")
    print(f"Results saved: .cortex/prescan_results.json")

if __name__ == "__main__":
    prescan_repositories()
