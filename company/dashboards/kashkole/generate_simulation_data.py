#!/usr/bin/env python3
"""
Phase 18.9 — Dashboard Simulation Data Generator

Generates realistic JSON data files for 5 repository simulation tiers:
- repo-S: Small (89 files)
- repo-M: Medium (892 files)
- repo-L: Large (8,500 files)
- repo-XL: Extra Large (35,000 files)
- repo-enterprise: Enterprise (125,000 files)

Usage:
    python3 generate_simulation_data.py
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any


class SimulationDataGenerator:
    """Generates realistic dashboard data for different repository sizes."""
    
    TIERS = {
        'repo-S': {'files': 89, 'commits': 234, 'contributors': 2},
        'repo-M': {'files': 892, 'commits': 2341, 'contributors': 8},
        'repo-L': {'files': 8500, 'commits': 15678, 'contributors': 25},
        'repo-XL': {'files': 35000, 'commits': 67890, 'contributors': 120},
        'repo-enterprise': {'files': 125000, 'commits': 234567, 'contributors': 450}
    }
    
    def __init__(self, tier: str):
        self.tier = tier
        self.tier_config = self.TIERS[tier]
        self.file_count = self.tier_config['files']
        self.commit_count = self.tier_config['commits']
        self.contributor_count = self.tier_config['contributors']
    
    def generate_all(self) -> Dict[str, Any]:
        """Generate complete dashboard data for the tier."""
        return {
            'tier': self.tier,
            'directoryTree': self._generate_directory_tree(),
            'dependencies': self._generate_dependencies(),
            'qualityMetrics': self._generate_quality_metrics(),
            'complexityData': self._generate_complexity_data(),
            'locDistribution': self._generate_loc_distribution(),
            'vulnerabilities': self._generate_vulnerabilities(),
            'dependencyTree': self._generate_dependency_tree(),
            'testingPyramid': self._generate_testing_pyramid(),
            'repoMetrics': self._generate_repo_metrics(),
            'securityFindings': self._generate_security_findings()
        }
    
    def _generate_directory_tree(self) -> Dict[str, Any]:
        """Generate hierarchical directory structure."""
        # Scale complexity with repository size
        max_depth = 3 if self.file_count < 1000 else 5 if self.file_count < 10000 else 7
        
        def create_node(name: str, depth: int = 0) -> Dict[str, Any]:
            if depth >= max_depth or random.random() > 0.7:
                # Leaf node (file)
                return {
                    'name': name,
                    'value': random.randint(50, 5000),
                    'type': 'file'
                }
            else:
                # Directory node
                child_count = random.randint(2, 8)
                return {
                    'name': name,
                    'children': [
                        create_node(f"item_{i}", depth + 1)
                        for i in range(child_count)
                    ],
                    'type': 'directory'
                }
        
        return create_node('root')
    
    def _generate_dependencies(self) -> Dict[str, Any]:
        """Generate dependency graph (force-directed layout)."""
        node_count = min(50, self.file_count // 20)
        nodes = [
            {'id': f'module_{i}', 'group': random.randint(1, 5)}
            for i in range(node_count)
        ]
        
        # Generate links with realistic patterns
        links = []
        for i in range(node_count):
            # Each node has 1-5 dependencies
            dependency_count = random.randint(1, min(5, node_count - 1))
            for _ in range(dependency_count):
                target = random.randint(0, node_count - 1)
                if target != i:
                    links.append({
                        'source': f'module_{i}',
                        'target': f'module_{target}',
                        'value': random.randint(1, 10)
                    })
        
        return {'nodes': nodes, 'links': links}
    
    def _generate_quality_metrics(self) -> Dict[str, Any]:
        """Generate code quality radar metrics."""
        # Quality degrades slightly with scale
        base_quality = 85 if self.file_count < 1000 else 75 if self.file_count < 10000 else 65
        
        return {
            'maintainability': base_quality + random.randint(-10, 5),
            'complexity': max(40, base_quality - random.randint(0, 20)),
            'testCoverage': max(50, base_quality - random.randint(0, 15)),
            'documentation': max(60, base_quality - random.randint(0, 10)),
            'security': max(70, base_quality + random.randint(-5, 10)),
            'performance': base_quality + random.randint(-15, 5)
        }
    
    def _generate_complexity_data(self) -> Dict[str, List[int]]:
        """Generate cyclomatic complexity histogram."""
        total_methods = self.file_count * 5  # ~5 methods per file
        
        # Distribution: most low complexity, some medium, few high
        return {
            'labels': ['1-5 (Simple)', '6-10 (Moderate)', '11-15 (Complex)', '16-20 (High)', '21+ (Very High)'],
            'data': [
                int(total_methods * 0.60),  # 60% simple
                int(total_methods * 0.25),  # 25% moderate
                int(total_methods * 0.10),  # 10% complex
                int(total_methods * 0.04),  # 4% high
                int(total_methods * 0.01)   # 1% very high
            ]
        }
    
    def _generate_loc_distribution(self) -> Dict[str, Any]:
        """Generate lines of code distribution by language."""
        languages = ['Python', 'JavaScript', 'TypeScript', 'CSS', 'HTML', 'SQL', 'YAML', 'JSON']
        total_loc = self.file_count * 150  # ~150 LOC per file
        
        # Generate weighted distribution
        weights = [0.35, 0.25, 0.15, 0.10, 0.08, 0.04, 0.02, 0.01]
        data = [int(total_loc * w) for w in weights]
        
        return {
            'labels': languages,
            'data': data
        }
    
    def _generate_vulnerabilities(self) -> Dict[str, int]:
        """Generate vulnerability counts."""
        # Vulnerabilities scale with codebase size
        scale_factor = self.file_count / 1000
        
        return {
            'codeSmells': max(1, int(9 * scale_factor)),
            'antiPatterns': max(1, int(5 * scale_factor)),
            'securityIssues': max(1, int(3 * scale_factor)),
            'bestPractices': max(1, int(8 * scale_factor))
        }
    
    def _generate_dependency_tree(self) -> Dict[str, Any]:
        """Generate hierarchical dependency tree."""
        def create_dep_node(name: str, depth: int = 0, max_depth: int = 4) -> Dict[str, Any]:
            if depth >= max_depth or random.random() > 0.6:
                return {'name': name}
            else:
                child_count = random.randint(1, 4)
                return {
                    'name': name,
                    'children': [
                        create_dep_node(f"{name}.dep{i}", depth + 1, max_depth)
                        for i in range(child_count)
                    ]
                }
        
        return create_dep_node('root')
    
    def _generate_testing_pyramid(self) -> Dict[str, int]:
        """Generate test distribution (unit, integration, e2e)."""
        total_tests = int(self.file_count * 12)  # ~12 tests per file
        
        # Recommended pyramid: 70% unit, 20% integration, 10% e2e
        return {
            'unit': int(total_tests * 0.70),
            'integration': int(total_tests * 0.20),
            'e2e': int(total_tests * 0.10)
        }
    
    def _generate_repo_metrics(self) -> Dict[str, Any]:
        """Generate repository-level metrics."""
        return {
            'totalFiles': self.file_count,
            'totalCommits': self.commit_count,
            'contributors': self.contributor_count,
            'branches': random.randint(5, 50),
            'pullRequests': int(self.commit_count * 0.3),
            'issues': int(self.commit_count * 0.15),
            'stars': random.randint(10, 10000),
            'forks': random.randint(2, 1000)
        }
    
    def _generate_security_findings(self) -> List[Dict[str, Any]]:
        """Generate security finding details."""
        severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        categories = ['Injection', 'XSS', 'CSRF', 'AuthN/AuthZ', 'Config', 'Crypto', 'Input Validation']
        
        finding_count = max(5, int(self.file_count / 100))
        findings = []
        
        for i in range(finding_count):
            findings.append({
                'id': f'SEC-{i+1:04d}',
                'severity': random.choice(severities),
                'category': random.choice(categories),
                'title': f'Security issue in module {random.randint(1, 100)}',
                'file': f'src/module_{random.randint(1, self.file_count)}.py',
                'line': random.randint(1, 500),
                'description': 'Potential security vulnerability detected by static analysis'
            })
        
        return findings


def main():
    """Generate simulation data for all tiers."""
    print("🚀 Starting Phase 18.9 — Simulation Data Generation\n")
    
    output_dir = Path(__file__).parent / 'repo-simulation'
    output_dir.mkdir(exist_ok=True)
    
    for tier in SimulationDataGenerator.TIERS.keys():
        print(f"📊 Generating data for {tier}...")
        
        generator = SimulationDataGenerator(tier)
        data = generator.generate_all()
        
        # Create tier directory
        tier_dir = output_dir / tier
        tier_dir.mkdir(exist_ok=True)
        
        # Save data.json
        data_file = tier_dir / 'data.json'
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"   ✅ Saved: {data_file}")
        print(f"   📈 Files: {data['repoMetrics']['totalFiles']:,}")
        print(f"   💾 Size: {data_file.stat().st_size / 1024:.1f} KB\n")
    
    print(f"✅ Phase 18.9 Data Generation Complete!")
    print(f"📁 Output: {output_dir.absolute()}")
    print(f"📊 Tiers: {len(SimulationDataGenerator.TIERS)}")


if __name__ == '__main__':
    main()
