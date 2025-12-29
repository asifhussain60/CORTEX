"""
Dashboard Data Orchestrator - Phase 10.1
Unified data collection pipeline for Dashboard v3

Features:
- Sequential collector execution (Phase 7 → Phase 8 → Phase 9)
- Data enrichment between phases
- Template-ready JSON generation
- Error handling and logging

Phase 7 Collectors:
- OverviewCollector: Repository metrics
- TechStackCollector: Languages & frameworks
- SecurityCollector: Vulnerabilities & CVEs
- BusinessCapabilityDetector: Business narrative
- RecommendationCollector: Actionable recommendations
- UseCaseCollector: Role/domain/process analysis

Phase 8 Collectors:
- SolutionStructureCollector: Solution hierarchy
- TechStackRiskScorer: EOL + CVE risk scoring

Phase 9 Intelligence:
- MigrationRoadmapGenerator: Upgrade paths
- FrameworkHealthHeatmap: Health visualization
- DependencyBloatAnalyzer: Statistical bloat detection

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Phase 7 imports
from src.dashboard.data.overview_collector import OverviewCollector
from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.security_collector import SecurityCollector
from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
from src.dashboard.data.recommendation_collector import RecommendationCollector
from src.dashboard.data.use_case_collector import UseCaseCollector

# Phase 8 imports
from src.dashboard.data.solution_structure_collector import SolutionStructureCollector
from src.dashboard.data.tech_stack_risk_scorer import TechStackRiskScorer

# Phase 9 imports
from src.dashboard.intelligence.migration_roadmap_generator import MigrationRoadmapGenerator
from src.dashboard.intelligence.framework_health_heatmap import FrameworkHealthHeatmap
from src.dashboard.intelligence.dependency_bloat_analyzer import DependencyBloatAnalyzer


class DashboardOrchestrator:
    """
    Orchestrates data collection across all dashboard phases
    
    Execution Order:
    1. Phase 7: Base collectors (overview, tech stack, security, business, recommendations, use cases)
    2. Phase 8: Solution structure + risk scoring (uses Phase 7 tech_stack)
    3. Phase 9: Intelligence features (uses Phase 8 enriched tech_stack)
    """
    
    def __init__(self, repo_path: str, output_dir: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            repo_path: Path to repository root
            output_dir: Optional output directory for dashboard JSON (defaults to cortex-brain/dashboards/data/repos/{repo_name}/)
        """
        self.repo_path = Path(repo_path)
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to production dashboard data directory
            repo_name = self.repo_path.name
            cortex_root = self.repo_path.parent if 'cortex' in str(self.repo_path).lower() else self.repo_path
            self.output_dir = cortex_root / 'cortex-brain' / 'dashboards' / 'data' / 'repos' / repo_name
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Collect data from all phases sequentially
        
        Returns:
            Complete dashboard data dictionary
        """
        print("🚀 Starting Dashboard Data Collection...")
        
        # ===== PHASE 7: Base Collectors =====
        print("\n📊 Phase 7: Base Data Collection")
        
        # Overview
        print("  - Collecting overview metrics...")
        overview_collector = OverviewCollector(str(self.repo_path))
        overview_data = overview_collector.collect()
        
        # Tech Stack
        print("  - Collecting tech stack...")
        tech_stack_collector = TechStackCollector(str(self.repo_path))
        tech_stack_data = tech_stack_collector.collect() or {}
        
        # Security
        print("  - Collecting security data...")
        security_collector = SecurityCollector(str(self.repo_path))
        security_data = security_collector.collect() or {}
        
        # Combine Phase 7 data for dependent collectors
        phase7_combined = {
            'overview': overview_data,
            'tech_stack': tech_stack_data,
            'security': security_data,
            'endpoints': [],  # Would come from API analyzer
            'files': self._get_file_list(),
            'complexity_by_file': {}  # Would come from complexity analyzer
        }
        
        # Business Capabilities
        print("  - Detecting business capabilities...")
        business_detector = BusinessCapabilityDetector()
        # BusinessCapabilityDetector doesn't have collect() - return mock data for now
        business_data = {
            'capabilities': [],
            'entities': [],
            'patterns': {}
        }
        
        # Recommendations
        print("  - Generating recommendations...")
        recommendation_collector = RecommendationCollector(str(self.repo_path))
        recommendations_data = recommendation_collector.collect(phase7_combined)
        
        # Use Cases
        print("  - Extracting use cases...")
        use_case_collector = UseCaseCollector()
        use_cases_data = use_case_collector.collect(phase7_combined)
        
        # ===== PHASE 8: Solution Structure + Risk Scoring =====
        print("\n🏗️  Phase 8: Solution Structure & Risk Analysis")
        
        # Solution Structure
        print("  - Building solution hierarchy...")
        solution_collector = SolutionStructureCollector()
        # Extract solutions from overview (simplified - would scan filesystem)
        solutions = self._extract_solutions_from_overview(overview_data)
        solution_structure_data = solution_collector.collect(solutions)
        
        # Tech Stack Risk Scoring
        print("  - Scoring technology risks...")
        risk_scorer = TechStackRiskScorer()
        enriched_tech_stack = risk_scorer.enrich_tech_stack(tech_stack_data)
        
        # ===== PHASE 9: Intelligence Features =====
        print("\n🧠 Phase 9: Intelligence & Analytics")
        
        # Migration Roadmap
        print("  - Generating migration roadmap...")
        roadmap_generator = MigrationRoadmapGenerator()
        migration_roadmap = roadmap_generator.generate_roadmap(enriched_tech_stack)
        
        # Framework Health Heatmap
        print("  - Analyzing framework health...")
        health_heatmap_generator = FrameworkHealthHeatmap()
        health_heatmap = health_heatmap_generator.generate(enriched_tech_stack)
        
        # Dependency Bloat Analysis
        print("  - Detecting dependency bloat...")
        bloat_analyzer = DependencyBloatAnalyzer()
        bloat_analysis = bloat_analyzer.analyze(enriched_tech_stack)
        
        # ===== Combine All Data =====
        print("\n✅ Combining data from all phases...")
        complete_data = {
            # Phase 7: Base data
            'overview': overview_data,
            'tech_stack': enriched_tech_stack,  # Enriched in Phase 8
            'security': security_data,
            'business': business_data,
            'recommendations': recommendations_data,
            'use_cases': use_cases_data.get('use_cases', []),
            'use_cases_metadata': use_cases_data.get('metadata', {}),
            
            # Phase 8: Structure & risk
            'solution_structure': solution_structure_data,
            
            # Phase 9: Intelligence
            'migration_roadmap': migration_roadmap,
            'health_heatmap': health_heatmap,
            'bloat_analysis': bloat_analysis,
            
            # Metadata
            'generated_at': datetime.now().isoformat(),
            'repo_path': str(self.repo_path),
            'dashboard_version': '3.0.0'
        }
        
        print(f"✨ Data collection complete! ({len(complete_data)} top-level sections)")
        return complete_data
    
    def generate_dashboard_json(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate template-ready dashboard JSON
        
        Args:
            data: Pre-collected data (if None, will collect)
            
        Returns:
            Template-ready dashboard data
        """
        if data is None:
            data = self.collect_all_data()
        
        print("\n🎨 Formatting data for dashboard template...")
        
        # Extract template variables
        template_data = {
            # Header
            'title': data['overview'].get('repository_name', 'Repository Dashboard'),
            'generated_at': data['generated_at'],
            'repo_path': data['repo_path'],
            
            # Overview tab
            'executive_summary': data['business'].get('executive_summary', ''),
            'metrics': self._format_metrics(data['overview']),
            
            # Tech Stack tab
            'languages': data['tech_stack'].get('languages', []),
            'frameworks': data['tech_stack'].get('frameworks', []),
            'dependencies': data['tech_stack'].get('dependencies', {}),
            
            # Security tab
            'vulnerabilities': data['security'].get('vulnerabilities', []),
            'security_score': data['security'].get('score', 0),
            
            # Use Cases tab
            'use_cases': data['use_cases'],
            'roles': data['use_cases_metadata'].get('roles', []),
            'domains': data['use_cases_metadata'].get('domains', []),
            'critical_use_cases_count': len([uc for uc in data['use_cases'] if uc.get('business_value') == 'critical']),
            
            # Recommendations tab
            'recommendations': data['recommendations'].get('recommendations', []),
            'top_recommendations': data['recommendations'].get('top_recommendations', []),
            'critical_high_roi_count': len([r for r in data['recommendations'].get('recommendations', []) if r.get('priority') == 'p0']),
            'important_medium_roi_count': len([r for r in data['recommendations'].get('recommendations', []) if r.get('priority') == 'p1']),
            'optional_low_roi_count': len([r for r in data['recommendations'].get('recommendations', []) if r.get('priority') == 'p2']),
            'deferred_count': len([r for r in data['recommendations'].get('recommendations', []) if r.get('priority') == 'p3']),
            
            # Phase 8 data
            'solution_structure': data['solution_structure'],
            
            # Phase 9 intelligence
            'migration_roadmap': data['migration_roadmap'],
            'health_heatmap': data['health_heatmap'],
            'bloat_analysis': data['bloat_analysis'],
            
            # Raw data for JavaScript
            'raw_data': data
        }
        
        return template_data
    
    def save_dashboard_json(self, data: Optional[Dict[str, Any]] = None, filename: str = 'dashboard-data.json') -> Path:
        """
        Save dashboard JSON to legacy single file
        
        Args:
            data: Dashboard data (if None, will collect and generate)
            filename: Output filename
            
        Returns:
            Path to saved JSON file
        """
        if data is None:
            data = self.generate_dashboard_json()
        
        # Save to legacy .cortex directory
        legacy_dir = self.repo_path / '.cortex'
        legacy_dir.mkdir(parents=True, exist_ok=True)
        output_path = legacy_dir / filename
        
        print(f"\n💾 Saving legacy dashboard data to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dashboard data saved! ({output_path.stat().st_size / 1024:.1f} KB)")
        return output_path
    
    def save_tab_json_files(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
        """
        Save dashboard data as individual tab JSON files for production dashboard
        
        Args:
            data: Dashboard data dict (if None, will collect fresh data)
            
        Returns:
            Dict mapping tab names to saved file paths
        """
        if data is None:
            print("\n📊 Collecting fresh data for production dashboard...")
            raw_data = self.collect_all_data()
            data = self.generate_dashboard_json(raw_data)
        
        saved_files = {}
        print(f"\n💾 Saving tab JSON files to {self.output_dir}...")
        
        # Save Use Cases tab data
        if 'use_cases' in data:
            use_cases = data['use_cases']
            use_cases_data = {
                'use_cases': use_cases,
                'metadata': data.get('use_cases_metadata', {}),
                'roles': self._extract_roles(use_cases),
                'domains': self._extract_domains(use_cases),
                'counts': {
                    'total': len(use_cases),
                    'by_role': self._count_by_field(use_cases, 'target_role'),
                    'by_domain': self._count_by_field(use_cases, 'domain'),
                    'by_complexity': self._count_by_field(use_cases, 'complexity')
                }
            }
            use_cases_path = self.output_dir / 'use-cases.json'
            with open(use_cases_path, 'w', encoding='utf-8') as f:
                json.dump(use_cases_data, f, indent=2, ensure_ascii=False)
            saved_files['use-cases'] = use_cases_path
            print(f"  ✅ use-cases.json ({use_cases_path.stat().st_size / 1024:.1f} KB)")
        
        # Save Recommendations tab data
        if 'recommendations' in data:
            recommendations = data['recommendations']
            recommendations_data = {
                'recommendations': recommendations,
                'top_recommendations': sorted(
                    recommendations, 
                    key=lambda r: r.get('roi_score', 0), 
                    reverse=True
                )[:10],
                'counts': {
                    'total': len(recommendations),
                    'by_priority': self._count_by_field(recommendations, 'priority'),
                    'by_category': self._count_by_field(recommendations, 'category'),
                    'critical_high_roi': data.get('critical_high_roi_count', 0),
                    'important_medium_roi': data.get('important_medium_roi_count', 0),
                    'optional_low_roi': data.get('optional_low_roi_count', 0),
                    'deferred': data.get('deferred_count', 0)
                }
            }
            recommendations_path = self.output_dir / 'recommendations.json'
            with open(recommendations_path, 'w', encoding='utf-8') as f:
                json.dump(recommendations_data, f, indent=2, ensure_ascii=False)
            saved_files['recommendations'] = recommendations_path
            print(f"  ✅ recommendations.json ({recommendations_path.stat().st_size / 1024:.1f} KB)")
        
        # Save Intelligence tab data (Phase 9)
        intelligence_keys = ['migration_roadmap', 'health_heatmap', 'bloat_analysis']
        intelligence_data = {k: data.get(k, {}) for k in intelligence_keys if k in data}
        if intelligence_data:
            intelligence_path = self.output_dir / 'intelligence.json'
            with open(intelligence_path, 'w', encoding='utf-8') as f:
                json.dump(intelligence_data, f, indent=2, ensure_ascii=False)
            saved_files['intelligence'] = intelligence_path
            print(f"  ✅ intelligence.json ({intelligence_path.stat().st_size / 1024:.1f} KB)")
        
        print(f"\n✅ Saved {len(saved_files)} tab JSON files to production dashboard!")
        return saved_files
    
    def _extract_roles(self, use_cases: List[Dict]) -> List[str]:
        """Extract unique roles from use cases"""
        roles = set()
        for uc in use_cases:
            if 'target_role' in uc:
                roles.add(uc['target_role'])
        return sorted(list(roles))
    
    def _extract_domains(self, use_cases: List[Dict]) -> List[str]:
        """Extract unique business domains from use cases"""
        domains = set()
        for uc in use_cases:
            if 'domain' in uc:
                domains.add(uc['domain'])
        return sorted(list(domains))
    
    def _count_by_field(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items grouped by field value"""
        counts = {}
        for item in items:
            value = item.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _get_file_list(self) -> List[str]:
        """Get list of files in repository"""
        files = []
        for ext in ['.cs', '.py', '.js', '.ts', '.java']:
            files.extend([str(f.relative_to(self.repo_path)) for f in self.repo_path.rglob(f'*{ext}')])
        return files[:100]  # Limit for performance
    
    def _extract_solutions_from_overview(self, overview_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Extract solution structure from overview data"""
        # Simplified - in production would scan .sln files
        return None
    
    def _format_metrics(self, overview_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format overview metrics for template"""
        metrics = []
        
        if 'total_files' in overview_data:
            metrics.append({
                'name': 'Total Files',
                'value': overview_data['total_files'],
                'icon': '📁'
            })
        
        if 'total_lines' in overview_data:
            metrics.append({
                'name': 'Lines of Code',
                'value': f"{overview_data['total_lines']:,}",
                'icon': '📝'
            })
        
        if 'languages_count' in overview_data:
            metrics.append({
                'name': 'Languages',
                'value': overview_data['languages_count'],
                'icon': '💻'
            })
        
        return metrics
