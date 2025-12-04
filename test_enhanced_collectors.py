"""Test enhanced parallel collectors"""
import sys
sys.path.insert(0, 'src')

from operations.onboarding_orchestrator import OnboardingOrchestrator
from pathlib import Path
import json

orchestrator = OnboardingOrchestrator(project_root=Path('.'), test_mode=True)

repos = [
    ('D:/PROJECTS/KSESSIONS', 'ksessions'),
    ('D:/PROJECTS/KASHKOLE', 'kashkole'),
    ('D:/PROJECTS/ALIST', 'alist')
]

print('🚀 Starting parallel scans with enhanced intelligence\n')

for repo_path, repo_name in repos:
    print(f'=== {repo_name.upper()} ===')
    result = orchestrator._generate_dashboard_data(Path(repo_path), repo_name)
    
    # Read tech stack
    tech_file = Path(result[1]) / 'tech-stack.json'
    with open(tech_file, 'r') as f:
        tech_data = json.load(f)
    
    # Display backend
    print(f'Backend ({len(tech_data["backend"])} technologies):')
    for tech in tech_data['backend']:
        meta = tech.get('metadata', {})
        extra = f" - {meta.get('file_count', 0)} files" if 'file_count' in meta else ""
        print(f'  ✓ {tech["name"]} {tech["version"]}{extra}')
    
    # Display database
    print(f'Database ({len(tech_data["database"])} technologies):')
    for db in tech_data['database']:
        print(f'  ✓ {db["name"]} {db["version"]}')
    
    # Read metadata
    meta_file = Path(result[1]) / 'metadata.json'
    with open(meta_file, 'r') as f:
        metadata = json.load(f)
    
    print(f'Collection time: {metadata["collection_time_seconds"]}s (6 parallel threads)\n')

print('✅ All repositories scanned successfully!')
