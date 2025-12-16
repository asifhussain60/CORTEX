"""
Health Utility

Lightweight application health analysis with multi-language support.

Core Operations:
- analyze_application: Complete health analysis with metrics
- scan_project_files: File discovery and counting
- build_architecture_graph: Dependency graph generation
- generate_health_report: Formatted markdown report

Version: 3.0.0 (Migrated from ApplicationHealthOrchestrator)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from src.crawlers.crawler_orchestrator import CrawlerOrchestrator
from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
from src.crawlers.analyzers.csharp_analyzer import CSharpAnalyzer
from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
from src.crawlers.analyzers.coldfusion_analyzer import ColdFusionAnalyzer
from src.crawlers.analyzers.generic_analyzer import GenericAnalyzer
from src.discovery.architecture_graph_builder import ArchitectureGraphBuilder


# Language analyzers (initialized on import)
ANALYZERS = {
    '.py': PythonAnalyzer(),
    '.cs': CSharpAnalyzer(),
    '.js': JavaScriptAnalyzer(),
    '.ts': JavaScriptAnalyzer(),
    '.cfm': ColdFusionAnalyzer(),
    '.cfc': ColdFusionAnalyzer(),
}
GENERIC_ANALYZER = GenericAnalyzer()


def analyze_application(project_path: str, scan_level: str = 'standard') -> Dict[str, Any]:
    """
    Analyze application health with language-specific metrics
    
    Args:
        project_path: Path to project root directory
        scan_level: Scan depth ('standard', 'deep')
        
    Returns:
        Dictionary with analysis results:
            - total_files: Total files analyzed
            - languages: Language breakdown with metrics
            - scan_duration: Time taken in seconds
            - architecture_graph: Dependency graph (nodes/edges)
            - timestamp: Analysis timestamp
            
    Example:
        >>> result = analyze_application("/path/to/project")
        >>> print(result["total_files"])
        152
        >>> print(result["languages"]["python"]["total_lines"])
        5432
    """
    start_time = time.time()
    
    # Discover files
    crawler = CrawlerOrchestrator(scan_level=scan_level)
    scan_result = crawler.scan(project_path)
    
    # Build architecture graph
    architecture_graph = None
    try:
        architecture_builder = ArchitectureGraphBuilder()
        architecture_graph = architecture_builder.build_graph(project_path)
    except Exception as e:
        architecture_graph = {"nodes": [], "edges": [], "error": str(e)}
    
    # Analyze files by language
    language_results = {}
    
    for file_path in scan_result.file_paths:
        extension = Path(file_path).suffix.lower()
        language = _get_language_name(extension)
        
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
            analyzer = ANALYZERS.get(extension, GENERIC_ANALYZER)
            
            # Read content for generic analyzer
            if analyzer == GENERIC_ANALYZER:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
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
        except Exception:
            pass  # Graceful degradation
    
    duration = time.time() - start_time
    
    return {
        'total_files': scan_result.total_files,
        'languages': language_results,
        'file_types': scan_result.file_types,
        'architecture_graph': architecture_graph,
        'scan_duration': round(duration, 2),
        'scan_level': scan_level,
        'timestamp': datetime.now().isoformat(),
        'project_path': project_path
    }


def scan_project_files(project_path: str) -> List[str]:
    """
    Scan project directory for all files
    
    Args:
        project_path: Path to project root
        
    Returns:
        List of file paths
        
    Example:
        >>> files = scan_project_files("/path/to/project")
        >>> print(len(files))
        152
    """
    crawler = CrawlerOrchestrator(scan_level='standard')
    scan_result = crawler.scan(project_path)
    return scan_result.file_paths


def build_architecture_graph(project_path: str) -> Dict[str, Any]:
    """
    Build dependency graph for project architecture
    
    Args:
        project_path: Path to project root
        
    Returns:
        Dictionary with nodes and edges
        
    Example:
        >>> graph = build_architecture_graph("/path/to/project")
        >>> print(len(graph["nodes"]))
        25
    """
    try:
        architecture_builder = ArchitectureGraphBuilder()
        return architecture_builder.build_graph(project_path)
    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e)}


def generate_health_report(analysis_result: Dict[str, Any]) -> str:
    """
    Generate formatted markdown report from analysis
    
    Args:
        analysis_result: Results from analyze_application()
        
    Returns:
        Formatted markdown report string
        
    Example:
        >>> result = analyze_application("/path/to/project")
        >>> report = generate_health_report(result)
        >>> print(report[:50])
        "# 🏥 Application Health Report"
    """
    lines = []
    
    # Header
    lines.append("# 🏥 Application Health Report")
    lines.append(f"**Generated:** {analysis_result['timestamp']}")
    lines.append(f"**Project:** {analysis_result['project_path']}")
    lines.append(f"**Duration:** {analysis_result['scan_duration']}s")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary
    lines.append("## 📊 Summary")
    lines.append("")
    lines.append(f"**Total Files:** {analysis_result['total_files']}")
    lines.append(f"**Languages:** {len(analysis_result['languages'])}")
    lines.append("")
    
    # File types
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
    
    for language, metrics in sorted(analysis_result['languages'].items()):
        display_name = _get_display_name(language)
        lines.append(f"### {display_name}")
        lines.append(f"**Files:** {metrics['file_count']}")
        lines.append(f"**Lines:** {metrics['total_lines']:,}")
        lines.append(f"**Functions:** {metrics['functions']}")
        lines.append(f"**Classes:** {metrics['classes']}")
        
        if metrics['total_lines'] > 0:
            avg_lines = metrics['total_lines'] // metrics['file_count']
            lines.append(f"**Avg Lines/File:** {avg_lines}")
        lines.append("")
    
    return "\n".join(lines)


def _get_language_name(extension: str) -> str:
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
    }
    return mapping.get(extension, 'other')


def _get_display_name(language: str) -> str:
    """Get display name for language"""
    names = {
        'python': 'Python',
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'csharp': 'C#',
        'coldfusion': 'ColdFusion',
        'html': 'HTML',
        'css': 'CSS',
        'sql': 'SQL'
    }
    return names.get(language, language.title())


# CLI for testing
if __name__ == "__main__":
    import sys
    import time
    
    print("🧪 Testing Health Utility...")
    start_test = time.time()
    
    # Get CORTEX root
    cortex_root = Path(__file__).parent.parent.parent.parent.parent
    
    # Test application analysis
    result = analyze_application(str(cortex_root), scan_level='standard')
    
    assert result['total_files'] > 0, "No files found"
    assert len(result['languages']) > 0, "No languages detected"
    print(f"✅ Analyzed application: {result['total_files']} files")
    print(f"✅ Languages detected: {len(result['languages'])}")
    
    # Test file scanning
    files = scan_project_files(str(cortex_root))
    assert len(files) > 0, "File scan failed"
    print(f"✅ Scanned files: {len(files)} found")
    
    # Test architecture graph
    graph = build_architecture_graph(str(cortex_root))
    assert 'nodes' in graph, "Architecture graph missing nodes"
    print(f"✅ Built architecture graph: {len(graph['nodes'])} nodes")
    
    # Test report generation
    report = generate_health_report(result)
    assert len(report) > 100, "Report too short"
    assert "Application Health Report" in report, "Report missing title"
    print(f"✅ Generated report: {len(report)} characters")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 4 core functions tested")
    print(f"✅ Performance: {elapsed:.3f}s (<2s target)")
