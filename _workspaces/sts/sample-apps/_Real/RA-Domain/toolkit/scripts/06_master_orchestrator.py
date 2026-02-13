"""
RA Domain Analysis Toolkit: Master Orchestrator

Purpose: Coordinate all 20 batches of RA domain analysis with dashboard integration.

Architecture:
- Extends CORTEX dashboard orchestrator pattern
- Integrates with admin dashboard via repository registry
- Supports batch execution, progress tracking, data transformation

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Add CORTEX paths
CORTEX_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


@dataclass
class BatchDefinition:
    """Definition of a single batch execution"""
    number: str  # "1", "2", "2.5", "3.1", etc.
    name: str
    duration_min: int
    description: str
    collector_class: str  # Python class name
    output_file: str  # Relative to output_dir
    dependencies: List[str]  # Batch numbers this depends on


@dataclass
class BatchResult:
    """Result of batch execution"""
    batch_num: str
    status: str  # 'success', 'failed', 'skipped'
    duration_min: float
    output_file: Optional[str]
    error_message: Optional[str] = None
    data_summary: Optional[Dict[str, Any]] = None


class RADomainOrchestrator:
    """
    Master orchestrator for RA domain analysis
    
    Features:
    - Sequential batch execution (1 → 2 → 2.5 → 3.1 → ... → 20)
    - Progress tracking with real-time updates
    - Dashboard integration via registry
    - Resumable execution (skip completed batches)
    - Data transformation to dashboard.json format
    
    Usage:
        orchestrator = RADomainOrchestrator(
            repo_path='C:/PROJECTS/Product.Example'
        )
        
        # Execute all batches
        orchestrator.execute_all_phases()
        
        # Execute specific batch
        orchestrator.execute_batch('11')  # Test coverage
    """
    
    def __init__(
        self,
        repo_path: str,
        output_dir: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize RA domain orchestrator
        
        Args:
            repo_path: Path to Product.Example repository
            output_dir: Optional output directory (defaults to cortex_brain/dashboards/data/repos/{repo_name}/)
            config_file: Optional config file (defaults to toolkit/config/analysis-config.yaml)
        """
        self.repo_path = Path(repo_path)
        self.repo_name = self.repo_path.name
        
        # Default output directory: CORTEX dashboard data structure
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = (
                CORTEX_ROOT / 
                'cortex_brain' / 
                'dashboards' / 
                'data' / 
                'repos' / 
                self.repo_name
            )
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = (
                CORTEX_ROOT / 
                'cortex_brain' / 
                'admin' / 
                'RA-Domain' / 
                'toolkit' / 
                'config' / 
                'analysis-config.yaml'
            )
        
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
        
        # Load batch definitions
        self.batches = self._load_batch_definitions()
        
        # Progress tracker
        self.progress_file = self.output_dir / 'reports' / 'progress-tracker.json'
        self.progress = self._load_progress()
        
        self.logger.info(f"✅ Orchestrator initialized for {self.repo_name}")
        self.logger.info(f"📁 Output directory: {self.output_dir}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.output_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'ra-domain-orchestrator-{datetime.now():%Y%m%d-%H%M%S}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load analysis configuration"""
        if not self.config_file.exists():
            self.logger.warning(f"⚠️ Config file not found: {self.config_file}")
            return self._get_default_config()
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'repository': {
                'path': str(self.repo_path),
                'name': self.repo_name,
                'type': 'external_csharp'
            },
            'batches': {
                'enabled': list(range(1, 21)),  # All batches
                'batch_size': {
                    'entities': 10,
                    'dtos': 9,
                    'services': 10
                }
            },
            'ast_parser': {
                'language': 'c_sharp',
                'max_file_size_mb': 5,
                'timeout_seconds': 30
            },
            'regulatory': {
                'enabled_validators': ['irs_compliance', 'hipaa_audit', 'pci_dss_scan'],
                'irs_limits': {
                    'fsa_annual_max': 3200,
                    'fsa_carryover_max': 640,
                    'hsa_individual_max': 4150,
                    'hsa_family_max': 8300,
                    'dependent_care_max': 5000
                }
            },
            'test_coverage': {
                'minimum_threshold': 80,
                'critical_paths_required': True
            },
            'dashboard_integration': {
                'auto_register': True,
                'auto_transform': True,
                'refresh_interval_minutes': 5
            }
        }
    
    def _load_batch_definitions(self) -> Dict[str, BatchDefinition]:
        """Load batch definitions from configuration"""
        # TODO: Load from batch-definitions.yaml
        # For now, return key batches manually
        
        return {
            '1': BatchDefinition(
                number='1',
                name='Repository Metrics',
                duration_min=30,
                description='Structural analysis: files, projects, directories',
                collector_class='StructuralAnalyzer',
                output_file='ast-outputs/structural-analysis.json',
                dependencies=[]
            ),
            '2': BatchDefinition(
                number='2',
                name='Business Domain Mapping',
                duration_min=90,
                description='Identify functional areas, workflows, terminology',
                collector_class='BusinessDomainMapper',
                output_file='ast-outputs/business-domain-map.json',
                dependencies=['1']
            ),
            '2.5': BatchDefinition(
                number='2.5',
                name='Regulatory Intelligence',
                duration_min=60,
                description='External research: RegulatoryAgency/PrivacyRegulation/PaymentSecurity requirements',
                collector_class='RegulatoryIntelligenceCollector',
                output_file='regulatory/regulatory-baseline.json',
                dependencies=['2']
            ),
            '11': BatchDefinition(
                number='11',
                name='Test Coverage Analysis',
                duration_min=60,
                description='Map tests to code, identify gaps, generate scenarios',
                collector_class='TestCoverageAnalyzer',
                output_file='test-coverage/coverage-report.json',
                dependencies=['1', '2']
            ),
            '13': BatchDefinition(
                number='13',
                name='Business Logic Extraction',
                duration_min=90,
                description='Extract decision trees, simplify rules, document workflows',
                collector_class='BusinessLogicExtractor',
                output_file='business-logic/business-rules.json',
                dependencies=['2', '2.5']
            ),
            '20': BatchDefinition(
                number='20',
                name='Dashboard Integration',
                duration_min=60,
                description='Transform data to dashboard.json, register with admin dashboard',
                collector_class='DashboardIntegrator',
                output_file='dashboard.json',
                dependencies=['1', '2', '11', '13']
            )
        }
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load execution progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        
        # Initialize new progress tracker
        return {
            'repository': self.repo_name,
            'started_at': None,
            'last_updated': None,
            'batches': {},
            'overall': {
                'completed': 0,
                'total': len(self.batches),
                'percent': 0.0,
                'estimated_remaining_hours': 0.0
            }
        }
    
    def _save_progress(self):
        """Save execution progress"""
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.progress['last_updated'] = datetime.now().isoformat()
        
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, indent=2, fp=f)
    
    def execute_all_phases(self) -> Dict[str, Any]:
        """
        Execute all 20 batches sequentially
        
        Returns:
            Summary of execution results
        """
        self.logger.info("🚀 Starting RA Domain Analysis - All Phases")
        self.logger.info(f"📁 Repository: {self.repo_path}")
        self.logger.info(f"📊 Total Batches: {len(self.batches)}")
        
        self.progress['started_at'] = datetime.now().isoformat()
        
        results = []
        
        # Execute batches in order
        for batch_num in sorted(self.batches.keys(), key=lambda x: float(x.replace('.', ''))):
            batch = self.batches[batch_num]
            
            # Check dependencies
            if not self._check_dependencies(batch):
                self.logger.warning(f"⏭️ Skipping batch {batch_num} - dependencies not met")
                continue
            
            # Execute batch
            result = self.execute_batch(batch_num)
            results.append(result)
            
            # Update progress
            self._update_progress(result)
            
            # Break on failure
            if result.status == 'failed':
                self.logger.error(f"❌ Batch {batch_num} failed - stopping execution")
                break
        
        # Generate final dashboard.json
        self.logger.info("📊 Generating dashboard.json...")
        dashboard_data = self._consolidate_all_phases()
        self._save_dashboard_json(dashboard_data)
        
        # Register with admin dashboard
        if self.config.get('dashboard_integration', {}).get('auto_register', True):
            self._register_with_dashboard()
        
        summary = {
            'repository': self.repo_name,
            'total_batches': len(self.batches),
            'completed': sum(1 for r in results if r.status == 'success'),
            'failed': sum(1 for r in results if r.status == 'failed'),
            'skipped': sum(1 for r in results if r.status == 'skipped'),
            'results': [asdict(r) for r in results]
        }
        
        self.logger.info(f"✅ Analysis complete: {summary['completed']}/{summary['total_batches']} batches")
        
        return summary
    
    def execute_batch(self, batch_num: str) -> BatchResult:
        """
        Execute a single batch
        
        Args:
            batch_num: Batch number (e.g., "1", "2.5", "3.1")
        
        Returns:
            Batch execution result
        """
        if batch_num not in self.batches:
            return BatchResult(
                batch_num=batch_num,
                status='failed',
                duration_min=0,
                output_file=None,
                error_message=f"Batch {batch_num} not defined"
            )
        
        batch = self.batches[batch_num]
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📊 Executing Batch {batch_num}: {batch.name}")
        self.logger.info(f"⏱️ Estimated Duration: {batch.duration_min} min")
        self.logger.info(f"{'='*80}\n")
        
        start_time = datetime.now()
        
        try:
            # TODO: Dynamic collector instantiation
            # For now, return mock result
            
            # Simulate execution
            import time
            time.sleep(2)  # Simulate work
            
            # Mock data
            data_summary = {
                'batch': batch_num,
                'name': batch.name,
                'files_processed': 10,
                'items_extracted': 25
            }
            
            # Save output
            output_path = self.output_dir / batch.output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(data_summary, indent=2, fp=f)
            
            duration = (datetime.now() - start_time).total_seconds() / 60
            
            self.logger.info(f"✅ Batch {batch_num} completed in {duration:.2f} min")
            
            return BatchResult(
                batch_num=batch_num,
                status='success',
                duration_min=duration,
                output_file=str(output_path),
                data_summary=data_summary
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() / 60
            
            self.logger.error(f"❌ Batch {batch_num} failed: {e}")
            
            return BatchResult(
                batch_num=batch_num,
                status='failed',
                duration_min=duration,
                output_file=None,
                error_message=str(e)
            )
    
    def _check_dependencies(self, batch: BatchDefinition) -> bool:
        """Check if batch dependencies are satisfied"""
        for dep_num in batch.dependencies:
            if dep_num not in self.progress.get('batches', {}):
                return False
            
            dep_status = self.progress['batches'][dep_num].get('status')
            if dep_status != 'complete':
                return False
        
        return True
    
    def _update_progress(self, result: BatchResult):
        """Update progress tracker"""
        self.progress['batches'][result.batch_num] = {
            'status': 'complete' if result.status == 'success' else result.status,
            'duration_min': result.duration_min,
            'completed_at': datetime.now().isoformat() if result.status == 'success' else None,
            'output_file': result.output_file,
            'error_message': result.error_message
        }
        
        # Update overall progress
        completed = sum(
            1 for b in self.progress['batches'].values() 
            if b.get('status') == 'complete'
        )
        
        total = len(self.batches)
        
        self.progress['overall'] = {
            'completed': completed,
            'total': total,
            'percent': (completed / total) * 100 if total > 0 else 0,
            'estimated_remaining_hours': self._calculate_remaining_time()
        }
        
        self._save_progress()
    
    def _calculate_remaining_time(self) -> float:
        """Calculate estimated remaining time in hours"""
        completed_batches = [
            b for b in self.progress.get('batches', {}).values()
            if b.get('status') == 'complete'
        ]
        
        pending_batches = [
            batch for batch_num, batch in self.batches.items()
            if batch_num not in self.progress.get('batches', {})
        ]
        
        if not pending_batches:
            return 0.0
        
        total_pending_min = sum(b.duration_min for b in pending_batches)
        
        return total_pending_min / 60
    
    def _consolidate_all_phases(self) -> Dict[str, Any]:
        """Consolidate all batch outputs into dashboard.json format"""
        # TODO: Implement full consolidation
        
        return {
            'metadata': {
                'repository': self.repo_name,
                'analysis_type': 'ra_domain_deep_dive',
                'generated_at': datetime.now().isoformat(),
                'batches_completed': self.progress['overall']['completed']
            },
            'progress': self.progress,
            'outputs': {
                batch_num: result.get('output_file')
                for batch_num, result in self.progress.get('batches', {}).items()
            }
        }
    
    def _save_dashboard_json(self, dashboard_data: Dict[str, Any]):
        """Save dashboard.json"""
        dashboard_file = self.output_dir / 'dashboard.json'
        
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, indent=2, fp=f)
        
        self.logger.info(f"✅ Dashboard data saved: {dashboard_file}")
    
    def _register_with_dashboard(self):
        """Register repository with CORTEX admin dashboard"""
        # TODO: Implement dashboard registration
        
        registry_file = (
            CORTEX_ROOT / 
            'cortex_brain' / 
            'dashboards' / 
            'data' / 
            'repository-registry.json'
        )
        
        if not registry_file.exists():
            registry = {'repositories': []}
        else:
            with open(registry_file, 'r') as f:
                registry = json.load(f)
        
        # Add/update entry
        entry = {
            'id': f'ra-domain-{self.repo_name}',
            'name': self.repo_name,
            'type': 'external_csharp',
            'path': str(self.repo_path),
            'dashboard_data': str(self.output_dir),
            'analysis_version': '2.0',
            'batches_completed': self.progress['overall']['completed'],
            'last_updated': datetime.now().isoformat(),
            'capabilities': [
                'ast_analysis',
                'test_coverage',
                'regulatory_compliance',
                'business_logic_extraction'
            ]
        }
        
        # Remove existing entry
        registry['repositories'] = [
            r for r in registry.get('repositories', [])
            if r.get('id') != entry['id']
        ]
        
        # Add new entry
        registry['repositories'].append(entry)
        
        # Save registry
        with open(registry_file, 'w') as f:
            json.dump(registry, indent=2, fp=f)
        
        self.logger.info(f"✅ Registered with admin dashboard: {entry['id']}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RA Domain Analysis Orchestrator')
    parser.add_argument('--repo-path', required=True, help='Path to Product.Example')
    parser.add_argument('--output-dir', help='Output directory (optional)')
    parser.add_argument('--config', help='Config file (optional)')
    parser.add_argument('--batch', help='Execute specific batch (e.g., "11")')
    parser.add_argument('--execute-all', action='store_true', help='Execute all batches')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = RADomainOrchestrator(
        repo_path=args.repo_path,
        output_dir=args.output_dir,
        config_file=args.config
    )
    
    # Execute
    if args.execute_all:
        summary = orchestrator.execute_all_phases()
        print(f"\n✅ Analysis Complete: {summary['completed']}/{summary['total_batches']} batches")
    elif args.batch:
        result = orchestrator.execute_batch(args.batch)
        print(f"\n{'✅' if result.status == 'success' else '❌'} Batch {args.batch}: {result.status}")
    else:
        print("❌ Error: Specify --execute-all or --batch")
        sys.exit(1)


if __name__ == '__main__':
    main()
