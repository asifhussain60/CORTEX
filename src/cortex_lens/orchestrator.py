"""
CORTEX Lens Main Orchestrator

The central entry point for all CORTEX Lens functionality.
Coordinates the 6-phase analysis workflow.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CortexLens:
    """
    Universal Repository Analyzer
    
    Orchestrates the complete analysis workflow:
    1. Repository Classification
    2. Data Collection
    3. Narrative Generation
    4. Dashboard Generation
    5. Validation
    6. Packaging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CORTEX Lens
        
        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.version = "1.0.0"
        
        # Initialize components (lazy loading)
        self._classifier = None
        self._pipeline = None
        self._narrative_generator = None
        self._dashboard_builder = None
        self._validator = None
        self._packager = None
        
        logger.info(f"🔍 CORTEX Lens v{self.version} initialized")
    
    def analyze(
        self,
        repo_path: str,
        output_dir: Optional[str] = None,
        template: Optional[str] = None,
        export_formats: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze repository and generate adaptive dashboard
        
        Args:
            repo_path: Path to repository to analyze
            output_dir: Output directory (default: cortex-lens-output/{repo_name})
            template: Force specific template (default: auto-detect)
            export_formats: List of export formats ['json', 'yaml', 'csv'] (default: ['html'])
        
        Returns:
            {
                'classification': {...},
                'data': {...},
                'narrative': {...},
                'dashboard_path': Path,
                'package_path': Path,
                'validation_report': {...},
                'export_paths': {...}
            }
        """
        repo_path = Path(repo_path).resolve()
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")
        
        logger.info(f"🎯 Starting analysis: {repo_path.name}")
        start_time = datetime.now()
        
        # Phase 1: Repository Classification
        logger.info("📊 Phase 1: Repository Classification")
        classification = self._classify_repository(repo_path)
        
        # Phase 2: Data Collection
        logger.info("📦 Phase 2: Data Collection")
        collected_data = self._collect_data(repo_path, classification)
        
        # Phase 3: Narrative Generation
        logger.info("📝 Phase 3: Narrative Generation")
        narrative = self._generate_narrative(collected_data, classification)
        
        # Phase 4: Dashboard Generation
        logger.info("🎨 Phase 4: Dashboard Generation")
        dashboard_path = self._generate_dashboard(
            repo_path,
            collected_data,
            narrative,
            classification,
            output_dir,
            template
        )
        
        # Phase 5: Validation
        logger.info("✅ Phase 5: Validation")
        validation_report = self._validate_data(collected_data, classification)
        
        # Phase 6: Packaging & Export
        logger.info("📦 Phase 6: Packaging & Export")
        package_path, export_paths = self._package_and_export(
            dashboard_path,
            collected_data,
            export_formats or ['html']
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'classification': classification,
            'data': collected_data,
            'narrative': narrative,
            'dashboard_path': dashboard_path,
            'package_path': package_path,
            'validation_report': validation_report,
            'export_paths': export_paths,
            'metrics': {
                'duration_seconds': duration,
                'total_files': collected_data.get('metadata', {}).get('total_files', 0),
                'total_loc': collected_data.get('metadata', {}).get('total_loc', 0),
            }
        }
        
        logger.info(f"✅ Analysis complete in {duration:.2f}s")
        logger.info(f"📊 Dashboard: {dashboard_path}")
        logger.info(f"📦 Package: {package_path}")
        
        return result
    
    def scan(self, repo_path: str) -> Dict[str, Any]:
        """
        Quick scan - classification only (no full analysis)
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Classification results
        """
        repo_path = Path(repo_path).resolve()
        logger.info(f"🔍 Quick scan: {repo_path.name}")
        
        classification = self._classify_repository(repo_path)
        
        primary_type = classification['primary_type']
        confidence = classification['confidence_scores'][primary_type]
        
        logger.info(f"✅ Detected: {primary_type} "
                   f"(confidence: {confidence:.1%})")
        
        return classification
    
    def compare(
        self,
        repo_paths: List[str],
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple repositories
        
        Args:
            repo_paths: List of repository paths
            output_dir: Output directory for comparison dashboard
            
        Returns:
            Comparison results
        """
        logger.info(f"🔄 Comparing {len(repo_paths)} repositories")
        
        # Analyze each repo
        analyses = []
        for repo_path in repo_paths:
            analysis = self.analyze(repo_path)
            analyses.append(analysis)
        
        # Generate comparison dashboard
        comparison_data = self._generate_comparison(analyses)
        comparison_path = self._generate_comparison_dashboard(
            comparison_data,
            output_dir
        )
        
        return {
            'analyses': analyses,
            'comparison_data': comparison_data,
            'comparison_path': comparison_path
        }
    
    # Private methods for each phase
    
    def _classify_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Phase 1: Classify repository type"""
        if self._classifier is None:
            from .core.classifier import RepoTypeClassifier
            self._classifier = RepoTypeClassifier()
        
        return self._classifier.classify(repo_path)
    
    def _collect_data(self, repo_path: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Collect data using appropriate collectors"""
        if self._pipeline is None:
            from .core.pipeline import DataCollectionPipeline
            self._pipeline = DataCollectionPipeline()
        
        return self._pipeline.execute(repo_path, classification)
    
    def _generate_narrative(
        self,
        data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 3: Generate business narrative"""
        if self._narrative_generator is None:
            from .generators.narrative_generator import NarrativeGenerator
            self._narrative_generator = NarrativeGenerator()
        
        return self._narrative_generator.generate(data, classification)
    
    def _generate_dashboard(
        self,
        repo_path: Path,
        data: Dict[str, Any],
        narrative: Dict[str, Any],
        classification: Dict[str, Any],
        output_dir: Optional[str],
        template: Optional[str]
    ) -> Path:
        """Phase 4: Generate dashboard from template"""
        if self._dashboard_builder is None:
            from .generators.dashboard_builder import DashboardBuilder
            self._dashboard_builder = DashboardBuilder()
        
        return self._dashboard_builder.build(
            repo_path,
            data,
            narrative,
            classification,
            output_dir,
            template
        )
    
    def _validate_data(
        self,
        data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 5: Validate collected data"""
        if self._validator is None:
            from .validators.schema_validator import SchemaValidator
            self._validator = SchemaValidator()
        
        return self._validator.validate(data, classification)
    
    def _package_and_export(
        self,
        dashboard_path: Path,
        data: Dict[str, Any],
        export_formats: List[str]
    ) -> tuple[Path, Dict[str, Path]]:
        """Phase 6: Package dashboard and export data"""
        if self._packager is None:
            from .generators.packager import Packager
            self._packager = Packager()
        
        package_path = self._packager.package(dashboard_path)
        export_paths = self._packager.export(data, export_formats, dashboard_path.parent)
        
        return package_path, export_paths
    
    def _generate_comparison(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison data from multiple analyses"""
        # Comparison logic deferred to v1.1 (multi-repo intelligence)
        return {
            'repo_count': len(analyses),
            'primary_types': [a['classification']['primary_type'] for a in analyses],
            'metrics_comparison': {},
            'recommendation': "Comparison feature available in v1.1"
        }
    
    def _generate_comparison_dashboard(
        self,
        comparison_data: Dict[str, Any],
        output_dir: Optional[str]
    ) -> Path:
        """Generate comparison dashboard"""
        # Comparison dashboard deferred to v1.1 (multi-repo intelligence)
        output_dir = Path(output_dir or 'cortex-lens-output/comparison')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        comparison_file = output_dir / 'comparison.html'
        comparison_file.write_text('<html><body><h1>Comparison Dashboard</h1><p>Feature available in CORTEX Lens v1.1</p></body></html>')
        
        return comparison_file
