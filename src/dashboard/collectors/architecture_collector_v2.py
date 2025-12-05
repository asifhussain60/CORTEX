"""
ArchitectureCollectorV2 - Universal architecture collection orchestrator.

This collector orchestrates all language-specific analyzers to extract complete
architecture information from any codebase (C#, TypeScript, ColdFusion, SQL, Python, etc.).

Features:
- Multi-language project analysis
- Cross-file dependency tracking
- Technology stack detection
- Architecture pattern identification
- Comprehensive metrics aggregation
- Parallel processing with caching

Author: Asif Hussain
Version: 2.0.0
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import json

from src.dashboard.collectors.universal_collector_base import (
    UniversalCollectorBase,
    CollectionProgress
)
from src.dashboard.analyzers import (
    get_factory,
    CSharpAnalyzer,
    TypeScriptAnalyzer,
    ColdFusionAnalyzer,
    SQLAnalyzer
)


@dataclass
class ArchitectureData:
    """Complete architecture analysis result."""
    
    # Project metadata
    project_name: str
    project_path: str
    scan_timestamp: str
    
    # Language distribution
    languages: Dict[str, int] = field(default_factory=dict)  # language -> file count
    total_files: int = 0
    total_lines: int = 0
    
    # Technology stack
    frontend: Dict[str, Any] = field(default_factory=dict)
    backend: Dict[str, Any] = field(default_factory=dict)
    database: Dict[str, Any] = field(default_factory=dict)
    
    # Architecture patterns
    architecture_type: str = "Unknown"  # Monolith, N-Tier, Microservices
    layers: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    
    # Code organization
    components: Dict[str, int] = field(default_factory=dict)  # type -> count
    complexity: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    # Quality metrics
    test_coverage: Optional[float] = None
    code_duplication: Optional[float] = None
    tech_debt_hours: Optional[float] = None
    
    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ArchitectureCollectorV2(UniversalCollectorBase):
    """
    Universal architecture collector that orchestrates language-specific analyzers.
    
    Supports:
    - C# / .NET (MVC, Web API, Entity Framework)
    - TypeScript / Angular (Components, Services, Routing)
    - ColdFusion (CFM, CFC, ORM)
    - SQL (T-SQL, PL/SQL schemas)
    - Python (Classes, functions, imports)
    - JavaScript (Modules, classes, React)
    """
    
    def __init__(
        self,
        root_path: Path,
        project_name: Optional[str] = None,
        max_workers: int = 4,
        enable_cache: bool = True
    ):
        """
        Initialize architecture collector.
        
        Args:
            root_path: Root directory of project
            project_name: Optional project name (default: directory name)
            max_workers: Max parallel workers
            enable_cache: Enable file caching
        """
        super().__init__(
            project_root=str(root_path),
            chunk_size=100,
            max_workers=max_workers,
            enable_caching=enable_cache
        )
        
        self.root_path = Path(root_path)
        self.project_name = project_name or self.root_path.name
        
        # Get analyzer factory
        self.factory = get_factory()
        
        # Results storage
        self.language_results: Dict[str, List[Any]] = defaultdict(list)
        self.file_count_by_language: Dict[str, int] = defaultdict(int)
    
    def collect(self) -> ArchitectureData:
        """
        Collect complete architecture data.
        
        Returns:
            ArchitectureData with complete analysis
        """
        from datetime import datetime
        
        print(f"\n{'='*80}")
        print(f"🏗️  CORTEX ArchitectureCollectorV2 - Universal Analysis")
        print(f"{'='*80}")
        print(f"Project: {self.project_name}")
        print(f"Path: {self.root_path}")
        print(f"{'='*80}\n")
        
        # Initialize result
        result = ArchitectureData(
            project_name=self.project_name,
            project_path=str(self.root_path),
            scan_timestamp=datetime.now().isoformat()
        )
        
        try:
            # Step 1: Discover and categorize files
            print("📁 Step 1: Discovering files...")
            files_by_language = self._discover_files()
            result.total_files = sum(len(files) for files in files_by_language.values())
            result.languages = {lang: len(files) for lang, files in files_by_language.items()}
            
            print(f"   Found {result.total_files} files across {len(files_by_language)} languages")
            for lang, count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {lang}: {count} files")
            
            # Step 2: Analyze files by language
            print("\n🔍 Step 2: Analyzing source code...")
            for language, files in files_by_language.items():
                if not files:
                    continue
                
                print(f"\n   Analyzing {language} ({len(files)} files)...")
                self._analyze_language(language, files)
            
            # Step 3: Aggregate results
            print("\n📊 Step 3: Aggregating results...")
            self._aggregate_results(result)
            
            # Step 4: Detect architecture patterns
            print("\n🏛️  Step 4: Detecting architecture patterns...")
            self._detect_architecture(result)
            
            # Step 5: Extract technology stack
            print("\n🔧 Step 5: Extracting technology stack...")
            self._extract_tech_stack(result)
            
            # Step 6: Calculate metrics
            print("\n📈 Step 6: Calculating metrics...")
            self._calculate_metrics(result)
            
            print(f"\n{'='*80}")
            print(f"✅ Analysis Complete!")
            print(f"{'='*80}")
            print(f"Architecture Type: {result.architecture_type}")
            print(f"Total Components: {sum(result.components.values())}")
            print(f"Total Lines: {result.total_lines:,}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            result.errors.append(f"Collection failed: {str(e)}")
            print(f"\n❌ Error: {e}\n")
        
        return result
    
    def _discover_files(self) -> Dict[str, List[Path]]:
        """
        Discover and categorize files by language.
        
        Returns:
            Dictionary mapping language -> list of files
        """
        files_by_language: Dict[str, List[Path]] = defaultdict(list)
        
        # Use factory-supported extensions
        supported_extensions = self.factory.get_supported_extensions()
        
        # Scan directory
        for ext in supported_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.root_path.glob(pattern):
                if not file_path.is_file():
                    continue
                
                # Skip excluded directories
                if self._should_exclude(file_path):
                    continue
                
                # Detect language
                language = self.factory.detect_language(file_path)
                if language:
                    files_by_language[language].append(file_path)
        
        return files_by_language
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded."""
        excluded_dirs = {
            'node_modules', '.git', '.venv', 'venv', '__pycache__',
            'bin', 'obj', '.vs', '.idea', 'dist', 'build',
            'packages', '.nuget', 'vendor'
        }
        
        return any(part in excluded_dirs for part in file_path.parts)
    
    def _analyze_language(self, language: str, files: List[Path]):
        """
        Analyze files for a specific language.
        
        Args:
            language: Language name
            files: List of files to analyze
        """
        analyzer = self.factory.get_analyzer(language)
        if not analyzer:
            return
        
        for i, file_path in enumerate(files, 1):
            try:
                # Analyze file
                result = analyzer.analyze(file_path)
                
                if result and not result.errors:
                    self.language_results[language].append(result)
                    self.file_count_by_language[language] += 1
                
                # Progress indicator
                if i % 10 == 0 or i == len(files):
                    print(f"      Progress: {i}/{len(files)} files", end='\r')
            
            except Exception as e:
                # Log error but continue
                print(f"      Error analyzing {file_path.name}: {e}")
        
        print(f"      Progress: {len(files)}/{len(files)} files - Done!")
    
    def _aggregate_results(self, result: ArchitectureData):
        """Aggregate analysis results into ArchitectureData."""
        
        # Initialize counters
        total_lines = 0
        component_counts = defaultdict(int)
        all_dependencies = defaultdict(set)
        
        # Aggregate C# results
        if 'csharp' in self.language_results:
            for analysis in self.language_results['csharp']:
                total_lines += analysis.metrics.get('loc', 0)
                component_counts['classes'] += analysis.metrics.get('class_count', 0)
                component_counts['methods'] += analysis.metrics.get('method_count', 0)
                
                # Collect dependencies
                for dep in analysis.dependencies:
                    all_dependencies['csharp'].add(dep)
        
        # Aggregate TypeScript results
        if 'typescript' in self.language_results:
            for analysis in self.language_results['typescript']:
                total_lines += analysis.metrics.get('loc', 0)
                component_counts['components'] += analysis.metrics.get('class_count', 0)
                component_counts['services'] += analysis.patterns.get('service', {}).get('is_service', 0)
                
                for dep in analysis.dependencies:
                    all_dependencies['typescript'].add(dep)
        
        # Aggregate ColdFusion results
        if 'coldfusion' in self.language_results:
            for analysis in self.language_results['coldfusion']:
                total_lines += analysis.metrics.get('loc', 0)
                component_counts['cf_components'] += analysis.metrics.get('component_count', 0)
                component_counts['cf_functions'] += analysis.metrics.get('function_count', 0)
        
        # Aggregate SQL results
        if 'sql' in self.language_results:
            for analysis in self.language_results['sql']:
                total_lines += analysis.metrics.get('loc', 0)
                component_counts['tables'] += analysis.metrics.get('table_count', 0)
                component_counts['procedures'] += analysis.metrics.get('procedure_count', 0)
                component_counts['views'] += analysis.metrics.get('view_count', 0)
        
        # Aggregate Python results
        if 'python' in self.language_results:
            for analysis in self.language_results['python']:
                total_lines += analysis.metrics.get('loc', 0)
                component_counts['classes'] += len(analysis.classes)
                component_counts['methods'] += len(analysis.methods)
                
                for dep in analysis.dependencies:
                    all_dependencies['python'].add(dep)
        
        # Update result
        result.total_lines = total_lines
        result.components = dict(component_counts)
        result.dependencies = {k: list(v) for k, v in all_dependencies.items()}
    
    def _detect_architecture(self, result: ArchitectureData):
        """Detect architecture type and patterns."""
        
        has_frontend = 'typescript' in self.language_results or 'javascript' in self.language_results
        has_backend = 'csharp' in self.language_results or 'python' in self.language_results
        has_database = 'sql' in self.language_results
        has_coldfusion = 'coldfusion' in self.language_results
        
        # Detect layers
        layers = []
        if has_frontend:
            layers.append('Presentation')
        if has_backend or has_coldfusion:
            layers.append('Business Logic')
        if has_database:
            layers.append('Data Access')
        
        result.layers = layers
        
        # Detect architecture type
        if has_frontend and has_backend and has_database:
            result.architecture_type = "N-Tier Full-Stack"
            result.patterns.append("Layered Architecture")
        elif has_backend and has_database:
            result.architecture_type = "N-Tier Backend"
            result.patterns.append("Service Layer")
        elif has_coldfusion and has_database:
            result.architecture_type = "ColdFusion Web Application"
            result.patterns.append("CFM/CFC Architecture")
        elif has_frontend:
            result.architecture_type = "Frontend Application"
            result.patterns.append("SPA")
        else:
            result.architecture_type = "Unknown"
        
        # Detect patterns from analysis
        if 'csharp' in self.language_results:
            for analysis in self.language_results['csharp']:
                if analysis.patterns.get('mvc', {}).get('is_controller'):
                    result.patterns.append("MVC Pattern")
                    break
                if analysis.patterns.get('web_api', {}).get('is_api_controller'):
                    result.patterns.append("RESTful API")
                    break
        
        if 'typescript' in self.language_results:
            for analysis in self.language_results['typescript']:
                if analysis.patterns.get('component', {}).get('is_component'):
                    result.patterns.append("Component-Based UI")
                    break
                if analysis.patterns.get('ngrx', {}).get('has_ngrx'):
                    result.patterns.append("State Management (NgRx)")
                    break
        
        # Remove duplicates
        result.patterns = list(set(result.patterns))
    
    def _extract_tech_stack(self, result: ArchitectureData):
        """Extract technology stack information."""
        
        # Frontend technologies
        if 'typescript' in self.language_results:
            frontend_tech = {
                'language': 'TypeScript',
                'frameworks': [],
                'libraries': set()
            }
            
            # Detect Angular
            for analysis in self.language_results['typescript']:
                if '@angular/core' in analysis.dependencies:
                    frontend_tech['frameworks'].append('Angular')
                    break
            
            # Collect unique libraries
            for analysis in self.language_results['typescript']:
                for dep in analysis.dependencies:
                    if dep.startswith('@'):
                        frontend_tech['libraries'].add(dep.split('/')[0])
                    elif '/' not in dep:
                        frontend_tech['libraries'].add(dep)
            
            result.frontend = {
                'language': frontend_tech['language'],
                'frameworks': frontend_tech['frameworks'],
                'libraries': sorted(list(frontend_tech['libraries']))[:20]  # Top 20
            }
        
        # Backend technologies
        if 'csharp' in self.language_results:
            backend_tech = {
                'language': 'C#',
                'frameworks': [],
                'patterns': []
            }
            
            # Detect frameworks
            for analysis in self.language_results['csharp']:
                if any('Microsoft.AspNetCore' in d for d in analysis.dependencies):
                    backend_tech['frameworks'].append('ASP.NET Core')
                    break
                if any('System.Web.Mvc' in d for d in analysis.dependencies):
                    backend_tech['frameworks'].append('ASP.NET MVC')
                    break
            
            # Detect Entity Framework
            for analysis in self.language_results['csharp']:
                if analysis.patterns.get('entity_framework', {}).get('has_dbcontext'):
                    backend_tech['patterns'].append('Entity Framework')
                    break
            
            result.backend = backend_tech
        
        # Database technologies
        if 'sql' in self.language_results:
            db_tech = {
                'type': 'SQL Database',
                'objects': {},
                'complexity': {}
            }
            
            # Count database objects
            total_tables = sum(
                a.metrics.get('table_count', 0) 
                for a in self.language_results['sql']
            )
            total_procs = sum(
                a.metrics.get('procedure_count', 0) 
                for a in self.language_results['sql']
            )
            total_views = sum(
                a.metrics.get('view_count', 0) 
                for a in self.language_results['sql']
            )
            
            db_tech['objects'] = {
                'tables': total_tables,
                'procedures': total_procs,
                'views': total_views
            }
            
            result.database = db_tech
    
    def _calculate_metrics(self, result: ArchitectureData):
        """Calculate complexity and quality metrics."""
        
        # Calculate average complexity
        total_complexity = 0
        complexity_count = 0
        
        for language in self.language_results:
            for analysis in self.language_results[language]:
                if 'cyclomatic' in analysis.complexity:
                    total_complexity += analysis.complexity['cyclomatic']
                    complexity_count += 1
                elif 'total' in analysis.complexity:
                    total_complexity += analysis.complexity['total']
                    complexity_count += 1
        
        avg_complexity = total_complexity / complexity_count if complexity_count > 0 else 0
        
        result.complexity = {
            'average': round(avg_complexity, 2),
            'total': total_complexity,
            'files_analyzed': complexity_count
        }
    
    def save_to_json(self, result: ArchitectureData, output_path: Path):
        """Save architecture data to JSON file."""
        from dataclasses import asdict
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved architecture data to: {output_path}")
