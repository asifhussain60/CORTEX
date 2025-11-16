"""
Discovery Report Generator

Orchestrates crawlers and generates comprehensive project intelligence reports.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.operations.crawlers import (
    FileScannerCrawler,
    GitAnalyzerCrawler,
    TestParserCrawler,
    DocMapperCrawler,
    BrainInspectorCrawler,
    PluginRegistryCrawler,
    HealthAssessorCrawler
)


class DiscoveryReportGenerator:
    """
    Orchestrates discovery crawlers and generates markdown reports.
    
    This class:
    1. Runs all crawlers in parallel
    2. Aggregates results
    3. Generates formatted markdown report
    4. Saves to cortex-brain/discovery-reports/
    """
    
    def __init__(self, project_root: str = None):
        """
        Initialize discovery report generator.
        
        Args:
            project_root: Project root directory (defaults to current directory)
        """
        self.project_root = project_root or os.getcwd()
        self.logger = logging.getLogger("cortex.discovery")
        
        # Initialize Jinja2 environment
        templates_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['format_number'] = self._format_number
        self.jinja_env.filters['format_time'] = self._format_time
        self.jinja_env.filters['enumerate'] = enumerate
        
        self.crawler_results = {}
        self.start_time = None
        self.end_time = None
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate discovery report.
        
        Returns:
            Dict with:
                - success: bool
                - report_path: str (path to generated report)
                - execution_time_ms: float
                - summary: str
        """
        self.start_time = datetime.now()
        self.logger.info("Starting discovery report generation")
        
        try:
            # Step 1: Run all crawlers
            self.logger.info("Executing crawlers...")
            self.crawler_results = self._run_crawlers()
            
            # Step 2: Aggregate data
            self.logger.info("Aggregating crawler data...")
            report_data = self._aggregate_data()
            
            # Calculate execution time for template
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds() * 1000
            report_data['execution_time_ms'] = execution_time
            
            # Step 3: Generate report
            self.logger.info("Generating markdown report...")
            report_content = self._render_template(report_data)
            
            # Step 4: Save report
            self.logger.info("Saving report...")
            report_path = self._save_report(report_content)
            
            # Add report path to data for display
            report_data['report_path'] = str(report_path)
            
            self.logger.info(f"Discovery report complete in {execution_time:.2f}ms")
            
            return {
                "success": True,
                "report_path": str(report_path),
                "execution_time_ms": execution_time,
                "summary": self._generate_summary(report_data),
                "data": report_data
            }
            
        except Exception as e:
            self.logger.error(f"Discovery report generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": 0
            }
    
    def _run_crawlers(self) -> Dict[str, Any]:
        """
        Run all crawlers in parallel.
        
        Returns:
            Dict mapping crawler names to results
        """
        # Initialize all crawlers
        crawlers = [
            FileScannerCrawler(self.project_root),
            GitAnalyzerCrawler(self.project_root),
            TestParserCrawler(self.project_root),
            DocMapperCrawler(self.project_root),
            BrainInspectorCrawler(self.project_root),
            PluginRegistryCrawler(self.project_root),
        ]
        
        results = {}
        
        # Run crawlers in parallel (max 4 workers)
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all crawler tasks
            future_to_crawler = {
                executor.submit(crawler.execute): crawler
                for crawler in crawlers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_crawler):
                crawler = future_to_crawler[future]
                try:
                    result = future.result(timeout=30)
                    results[crawler.get_name()] = result
                    self.logger.info(f"✓ {crawler.get_name()} completed")
                except Exception as e:
                    self.logger.error(f"✗ {crawler.get_name()} failed: {e}")
                    results[crawler.get_name()] = {
                        "success": False,
                        "error": str(e),
                        "data": None
                    }
        
        # Run Health Assessor last (depends on other results)
        health_crawler = HealthAssessorCrawler(self.project_root, results)
        results[health_crawler.get_name()] = health_crawler.execute()
        
        return results
    
    def _aggregate_data(self) -> Dict[str, Any]:
        """
        Aggregate crawler results into template-ready data.
        
        Returns:
            Dict with all data needed for template rendering
        """
        data = {
            # Metadata
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_name': Path(self.project_root).name,
            'platform': platform.system(),
            'os_version': platform.version(),
            'crawlers_executed': len(self.crawler_results),
            
            # Defaults (will be overridden by crawler data)
            'total_files': 0,
            'total_dirs': 0,
            'total_lines': 0,
            'total_commits': 0,
            'total_tests': 0,
            'coverage': 0.0,
            'total_docs': 0,
            'active_plugins': 0,
            'health_score': 0.0,
            'grade': 'N/A',
        }
        
        # Extract File Scanner data
        file_data = self._get_crawler_data('File Scanner')
        if file_data:
            data.update({
                'total_files': file_data.get('total_files', 0),
                'total_dirs': file_data.get('total_directories', 0),
                'total_lines': file_data.get('total_lines', 0),
                'languages': file_data.get('languages', {}),
                'frameworks': file_data.get('frameworks', []),
                'architecture_pattern': file_data.get('architecture_pattern', 'custom'),
                'project_size': file_data.get('project_size', 'unknown'),
            })
        
        # Extract Git Analyzer data
        git_data = self._get_crawler_data('Git Analyzer')
        if git_data:
            data.update({
                'git_available': git_data.get('git_available', False),
                'is_git_repo': git_data.get('is_git_repo', False),
                'total_commits': git_data.get('total_commits', 0),
                'current_branch': git_data.get('current_branch'),
                'total_branches': git_data.get('branches', {}).get('total', 0),
                'active_branches': git_data.get('branches', {}).get('active', 0),
                'stale_branches': git_data.get('branches', {}).get('stale', 0),
                'contributors': git_data.get('contributors', 0),
                'activity_7d': git_data.get('recent_activity', {}).get('last_7_days', 0),
                'activity_30d': git_data.get('recent_activity', {}).get('last_30_days', 0),
                'activity_90d': git_data.get('recent_activity', {}).get('last_90_days', 0),
                'hot_files': git_data.get('hot_files', []),
            })
        
        # Extract Test Parser data
        test_data = self._get_crawler_data('Test Parser')
        if test_data:
            data.update({
                'pytest_available': test_data.get('pytest_available', False),
                'total_tests': test_data.get('total_tests', 0),
                'unit_tests': test_data.get('test_types', {}).get('unit', 0),
                'integration_tests': test_data.get('test_types', {}).get('integration', 0),
                'e2e_tests': test_data.get('test_types', {}).get('e2e', 0),
                'passing_tests': test_data.get('passing', 0),
                'failing_tests': test_data.get('failing', 0),
                'coverage': test_data.get('coverage', 0.0),
                'test_files': test_data.get('test_files', 0),
                'untested_modules': test_data.get('untested_modules', []),
            })
        
        # Extract Doc Mapper data
        doc_data = self._get_crawler_data('Documentation Mapper')
        if doc_data:
            data.update({
                'total_docs': doc_data.get('total_docs', 0),
                'user_guides': doc_data.get('user_guides', 0),
                'api_docs': doc_data.get('api_docs', 0),
                'design_docs': doc_data.get('design_docs', 0),
                'readme_exists': doc_data.get('readme_exists', False),
                'readme_quality': doc_data.get('readme_quality', 0.0),
                'help_system': doc_data.get('help_system'),
                'documented_modules': doc_data.get('documented_modules', 0),
                'undocumented_modules': doc_data.get('undocumented_modules', 0),
                'doc_directories': doc_data.get('doc_directories', []),
            })
        
        # Extract Brain Inspector data
        brain_data = self._get_crawler_data('Brain Inspector')
        if brain_data:
            tier1 = brain_data.get('tier1', {})
            tier2 = brain_data.get('tier2', {})
            tier3 = brain_data.get('tier3', {})
            
            data.update({
                # Tier 1
                'tier1_conversations': tier1.get('conversations', 0),
                'tier1_retention': tier1.get('retention_rate', 0),
                'tier1_oldest': tier1.get('oldest'),
                'tier1_newest': tier1.get('newest'),
                'tier1_db_exists': tier1.get('database_exists', False),
                
                # Tier 2
                'tier2_patterns': tier2.get('knowledge_patterns', 0),
                'tier2_capabilities': tier2.get('capabilities', 0),
                'tier2_architectural': tier2.get('architectural_patterns', 0),
                'tier2_lessons': tier2.get('lessons_learned', 0),
                'tier2_relationships': tier2.get('file_relationships', 0),
                'tier2_files': tier2.get('files_exist', []),
                
                # Tier 3
                'tier3_commits': tier3.get('git_commits_tracked', 0),
                'tier3_coverage': tier3.get('test_coverage', 0.0),
                'tier3_file_rels': tier3.get('file_relationships', 0),
                'tier3_exists': tier3.get('development_context_exists', False),
                
                # Overall
                'brain_health': brain_data.get('brain_health', 0.0),
                'protection_rules': brain_data.get('protection_rules', 0),
            })
        
        # Extract Plugin Registry data
        plugin_data = self._get_crawler_data('Plugin Registry')
        if plugin_data:
            data.update({
                'total_plugins': plugin_data.get('total_plugins', 0),
                'active_plugins': plugin_data.get('active_plugins', 0),
                'plugin_list': plugin_data.get('plugin_list', []),
                'nl_patterns': plugin_data.get('natural_language_patterns', 0),
                'commands_registered': plugin_data.get('commands_registered', 0),
                'init_success_rate': plugin_data.get('initialization_success_rate', 0.0),
            })
        
        # Extract Health Assessor data
        health_data = self._get_crawler_data('Health Assessor')
        if health_data:
            data.update({
                'health_score': health_data.get('health_score', 0.0),
                'grade': health_data.get('grade', 'N/A'),
                'risks': health_data.get('risks', []),
                'opportunities': health_data.get('opportunities', []),
                'strengths': health_data.get('strengths', []),
                'recommendations': health_data.get('recommendations', []),
            })
            
            # Count high priority risks
            high_priority = [r for r in data['risks'] if r.get('severity') == 'high']
            data['high_priority_count'] = len(high_priority)
        
        return data
    
    def _get_crawler_data(self, crawler_name: str) -> Dict[str, Any]:
        """Get data from specific crawler."""
        result = self.crawler_results.get(crawler_name, {})
        return result.get('data') if result.get('success') else None
    
    def _render_template(self, data: Dict[str, Any]) -> str:
        """
        Render markdown report from template.
        
        Args:
            data: Aggregated crawler data
            
        Returns:
            Rendered markdown content
        """
        template = self.jinja_env.get_template('discovery_report.md.j2')
        return template.render(**data)
    
    def _save_report(self, content: str) -> Path:
        """
        Save report to cortex-brain/discovery-reports/.
        
        Args:
            content: Markdown content to save
            
        Returns:
            Path to saved report
        """
        # Create reports directory
        reports_dir = Path(self.project_root) / 'cortex-brain' / 'discovery-reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        report_path = reports_dir / f'discovery-{timestamp}.md'
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create/update 'latest.md' symlink
        latest_path = reports_dir / 'latest.md'
        if latest_path.exists() or latest_path.is_symlink():
            latest_path.unlink()
        
        # Create symlink (cross-platform compatible)
        try:
            latest_path.symlink_to(report_path.name)
        except OSError:
            # Fallback: copy file if symlink not supported
            with open(latest_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return report_path
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        return (
            f"Discovery complete! Analyzed {data['total_files']} files, "
            f"{data['total_tests']} tests, {data['total_docs']} docs. "
            f"Health score: {data['health_score']:.1f}/10 ({data['grade']})"
        )
    
    @staticmethod
    def _format_number(value: int) -> str:
        """Format number with thousand separators."""
        return f"{value:,}"
    
    @staticmethod
    def _format_time(ms: float) -> str:
        """Format time in ms to human-readable."""
        if ms < 1000:
            return f"{ms:.0f}ms"
        else:
            return f"{ms/1000:.2f}s"


def generate_discovery_report(project_root: str = None) -> Dict[str, Any]:
    """
    Convenience function to generate discovery report.
    
    Args:
        project_root: Project root directory (defaults to current directory)
        
    Returns:
        Dict with generation results
    """
    generator = DiscoveryReportGenerator(project_root)
    return generator.generate()


# For testing
if __name__ == '__main__':
    import sys
    
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    result = generate_discovery_report(root)
    
    if result['success']:
        print(f"✅ {result['summary']}")
        print(f"📄 Report: {result['report_path']}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
