"""
Application Health Orchestrator

Coordinates application health analysis by integrating:
- CrawlerOrchestrator (file discovery)
- Language analyzers (code analysis)
- Report generation (formatted output)
- Caching (performance optimization)
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.crawlers.crawler_orchestrator import CrawlerOrchestrator
from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
from src.crawlers.analyzers.csharp_analyzer import CSharpAnalyzer
from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
from src.crawlers.analyzers.coldfusion_analyzer import ColdFusionAnalyzer
from src.crawlers.analyzers.generic_analyzer import GenericAnalyzer


class ApplicationHealthOrchestrator:
    """
    Orchestrates application health analysis
    
    Coordinates scanning, analysis, and reporting for application health assessment.
    Integrates with existing CORTEX crawler infrastructure.
    """
    
    def __init__(self):
        """Initialize orchestrator with language analyzers"""
        self.analyzers = {
            '.py': PythonAnalyzer(),
            '.cs': CSharpAnalyzer(),
            '.js': JavaScriptAnalyzer(),
            '.ts': JavaScriptAnalyzer(),
            '.cfm': ColdFusionAnalyzer(),
            '.cfc': ColdFusionAnalyzer(),
        }
        self.generic_analyzer = GenericAnalyzer()
    
    def analyze(self, project_path: str, scan_level: str = 'standard') -> Dict[str, Any]:
        """
        Analyze application health
        
        Args:
            project_path: Path to project root directory
            scan_level: Scan depth ('overview', 'standard', 'deep')
        
        Returns:
            Dictionary with analysis results:
                - total_files: Total files analyzed
                - languages: Language breakdown with metrics
                - scan_duration: Time taken in seconds
                - scan_level: Level used
                - timestamp: Analysis timestamp
        """
        start_time = time.time()
        
        # Step 1: Discover files using CrawlerOrchestrator
        crawler = CrawlerOrchestrator(scan_level=scan_level)
        scan_result = crawler.scan(project_path)
        
        # Step 2: Analyze files by language
        language_results = {}
        
        for file_path in scan_result.file_paths:
            path_obj = Path(file_path)
            extension = path_obj.suffix.lower()
            
            # Determine language from extension
            language = self._get_language_name(extension)
            
            # Initialize language entry if needed
            if language not in language_results:
                language_results[language] = {
                    'file_count': 0,
                    'total_lines': 0,
                    'functions': 0,
                    'classes': 0,
                    'files': []
                }
            
            # Analyze file
            try:
                analyzer = self.analyzers.get(extension, self.generic_analyzer)
                
                # Read file content for analysis
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as read_error:
                    print(f"Warning: Could not read {file_path}: {read_error}")
                    continue
                
                # Call analyzer with content
                if analyzer == self.generic_analyzer:
                    analysis_result = analyzer.analyze(file_path, content)
                    analysis = {
                        'lines_of_code': analysis_result.lines_of_code,
                        'functions': [],
                        'classes': []
                    }
                else:
                    analysis = analyzer.analyze(file_path)
                
                # Aggregate metrics
                language_results[language]['file_count'] += 1
                language_results[language]['total_lines'] += analysis.get('lines_of_code', 0)
                language_results[language]['functions'] += len(analysis.get('functions', []))
                language_results[language]['classes'] += len(analysis.get('classes', []))
                language_results[language]['files'].append({
                    'path': file_path,
                    'lines': analysis.get('lines_of_code', 0)
                })
            except Exception as e:
                # Log error but continue (graceful degradation)
                print(f"Warning: Error analyzing {file_path}: {e}")
        
        # Step 3: Build result
        duration = time.time() - start_time
        
        return {
            'total_files': scan_result.total_files,
            'languages': language_results,
            'file_types': scan_result.file_types,
            'scan_duration': round(duration, 2),
            'scan_level': scan_level,
            'timestamp': datetime.now().isoformat(),
            'project_path': project_path
        }
    
    def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate formatted text report from analysis results
        
        Args:
            analysis_result: Results from analyze() method
        
        Returns:
            Formatted markdown report string
        """
        lines = []
        
        # Header
        lines.append("# 🏥 Application Health Report")
        lines.append(f"**Generated:** {analysis_result['timestamp']}")
        lines.append(f"**Project:** {analysis_result['project_path']}")
        lines.append(f"**Scan Level:** {analysis_result['scan_level']}")
        lines.append(f"**Duration:** {analysis_result['scan_duration']}s")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Summary
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append(f"**Total Files:** {analysis_result['total_files']}")
        lines.append(f"**Languages Detected:** {len(analysis_result['languages'])}")
        lines.append("")
        
        # File types breakdown
        if analysis_result['file_types']:
            lines.append("**File Types:**")
            for ext, count in sorted(analysis_result['file_types'].items(), 
                                    key=lambda x: x[1], reverse=True):
                lines.append(f"- `{ext}`: {count} files")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Language details
        lines.append("## 🔤 Language Breakdown")
        lines.append("")
        
        # Language display name mapping
        display_names = {
            'python': 'Python',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'csharp': 'C#',
            'coldfusion': 'ColdFusion',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL'
        }
        
        for language, metrics in sorted(analysis_result['languages'].items()):
            display_name = display_names.get(language, language.title())
            lines.append(f"### {display_name}")
            lines.append("")
            lines.append(f"**Files:** {metrics['file_count']}")
            lines.append(f"**Total Lines:** {metrics['total_lines']:,}")
            lines.append(f"**Functions:** {metrics['functions']}")
            lines.append(f"**Classes:** {metrics['classes']}")
            
            if metrics['total_lines'] > 0:
                avg_lines = metrics['total_lines'] // metrics['file_count']
                lines.append(f"**Avg Lines/File:** {avg_lines}")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Footer with feedback prompt
        lines.append("**Report generated by CORTEX Application Health Dashboard**")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📢 Feedback Welcome!")
        lines.append("")
        lines.append("**Help us improve the Application Health Dashboard:**")
        lines.append("")
        lines.append("**What's working well?**")
        lines.append("- Which metrics are most valuable to you?")
        lines.append("- Is the report format clear and actionable?")
        lines.append("- Are scan times acceptable for your project size?")
        lines.append("")
        lines.append("**What's missing?**")
        lines.append("- What additional metrics would help you?")
        lines.append("- Which visualizations would be most useful?")
        lines.append("- What file types/languages need better support?")
        lines.append("")
        lines.append("**Share your feedback:** Say `feedback` in CORTEX or create an issue at github.com/asifhussain60/CORTEX")
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_language_name(self, extension: str) -> str:
        """Map file extension to language name"""
        mapping = {
            '.py': 'python',
            '.cs': 'csharp',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cfm': 'coldfusion',
            '.cfc': 'coldfusion',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.go': 'go',
        }
        return mapping.get(extension, 'other')
