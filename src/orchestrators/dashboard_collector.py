"""
Dashboard Data Collection Orchestrator

Purpose: Generate complete dashboard data for any repository by orchestrating
         all data collectors (tech stack, architecture, security, etc.)

Usage:
    python -m src.orchestrators.dashboard_collector --path "C:\\PROJECTS\\MyRepo"
    python -m src.orchestrators.dashboard_collector --path "C:\\PROJECTS\\MyRepo" --output custom-name

Features:
- Auto-detects repository languages and frameworks
- Runs all collectors in parallel for speed
- Generates complete dashboard data set
- Saves to cortex-brain/dashboards/{repo-name}/
- Supports custom output directory names

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


logger = logging.getLogger(__name__)


class DashboardDataCollector:
    """Orchestrates collection of all dashboard data for a repository."""

    def __init__(self, repo_path: Path, output_name: Optional[str] = None, skip_consolidation: bool = False):
        """
        Initialize collector.

        Args:
            repo_path: Path to repository to analyze
            output_name: Optional custom name for output directory
            skip_consolidation: Skip consolidation/reconciliation steps (faster, raw data only)
        """
        self.repo_path = Path(repo_path)
        self.output_name = output_name or self.repo_path.name.lower().replace('.', '-')
        self.skip_consolidation = skip_consolidation

        # Load configuration
        from src.dashboard_config import get_config
        self.config = get_config()

        # Get output directory from config
        repos_path = self.config.get_path('repos')
        self.output_dir = repos_path / self.output_name

        print(f"\n📂 Repository: {self.repo_path.name}")
        print(f"📍 Path: {self.repo_path}")
        print(f"💾 Output: {self.output_dir}")
        print("")
        logger.info(f"Collecting data for: {self.repo_path}")
        logger.info(f"Output directory: {self.output_dir}")

    def collect_health_data(self) -> Dict[str, Any]:
        """Collect overall health metrics with deep analysis ONLY."""
        print("🏥 Collecting health data...")
        logger.info("Collecting health data with deep analysis...")
        import time
        start = time.time()

        from src.orchestrators.enhanced_collectors import HealthDataCollector
        collector = HealthDataCollector(self.repo_path)
        data = collector.collect()
        data["last_scan"] = datetime.now().isoformat()
        data["trends"] = {
            "health_trend": "stable",
            "velocity_trend": "stable",
            "quality_trend": "stable"
        }
        
        elapsed = time.time() - start
        print(f"   ✓ Health data collected in {elapsed:.1f}s")
        return data

    def collect_tech_stack(self) -> Dict[str, Any]:
        """Collect technology stack information with deep analysis ONLY."""
        print("🔧 Collecting tech stack...")
        logger.info("Collecting tech stack with deep analysis...")
        import time
        start = time.time()

        from src.orchestrators.enhanced_collectors import TechStackCollector
        collector = TechStackCollector(self.repo_path)
        data = collector.collect()
        
        elapsed = time.time() - start
        print(f"   ✓ Tech stack collected in {elapsed:.1f}s")
        return data

    def collect_architecture(self) -> Dict[str, Any]:
        """Collect architecture information with deep analysis ONLY."""
        print("🏗️  Collecting architecture...")
        logger.info("Collecting architecture data...")
        import time
        start = time.time()

        from src.dashboard.data.architecture_collector import ArchitectureCollector
        collector = ArchitectureCollector(self.repo_path)
        data = collector.collect()
        
        elapsed = time.time() - start
        print(f"   ✓ Architecture collected in {elapsed:.1f}s")
        return data

    def collect_security(self) -> Dict[str, Any]:
        """Collect security analysis with deep analysis ONLY."""
        print("🔒 Collecting security data...")
        logger.info("Collecting security data...")
        import time
        start = time.time()

        from src.dashboard.data.security_collector import SecurityCollector
        collector = SecurityCollector(self.repo_path)
        data = collector.collect()
        
        elapsed = time.time() - start
        print(f"   ✓ Security data collected in {elapsed:.1f}s")
        return data

    def collect_code_organization(self) -> Dict[str, Any]:
        """Collect code organization metrics with deep analysis ONLY."""
        print("📋 Collecting code organization...")
        logger.info("Collecting code organization with deep analysis...")
        import time
        start = time.time()

        from src.dashboard.data.code_org_collector import CodeOrganizationCollector
        collector = CodeOrganizationCollector(self.repo_path)
        data = collector.collect()
        
        elapsed = time.time() - start
        print(f"   ✓ Code organization collected in {elapsed:.1f}s")
        return data

    def collect_vendors(self) -> Dict[str, Any]:
        """Collect vendor/dependency information with deep analysis ONLY."""
        print("📦 Collecting vendor data...")
        logger.info("Collecting vendor data with deep analysis...")
        import time
        start = time.time()

        from src.dashboard.data.vendor_collector import VendorCollector
        collector = VendorCollector(self.repo_path)
        data = collector.collect()
        
        elapsed = time.time() - start
        print(f"   ✓ Vendor data collected in {elapsed:.1f}s")
        return data

    def collect_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect all dashboard data using parallel execution.

        Returns:
            Dictionary with all collected data
        """
        logger.info("Starting parallel data collection...")

        collectors = {
            'health-data': self.collect_health_data,
            'tech-stack': self.collect_tech_stack,
            'architecture': self.collect_architecture,
            'security': self.collect_security,
            'code-organization': self.collect_code_organization,
            'vendors': self.collect_vendors
        }

        results = {}

        # Execute collectors in parallel
        print("⚡ Running 7 collectors in parallel (max 4 concurrent)...\n")
        completed = 0
        total = len(collectors)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(func): name for name, func in collectors.items()}

            for future in as_completed(futures):
                name = futures[future]
                completed += 1
                try:
                    results[name] = future.result()
                    logger.info(f"✓ Collected {name}")
                except Exception as e:
                    print(f"   ✗ Failed: {name} - {e}")
                    logger.error(f"✗ Failed to collect {name}: {e}")
                    results[name] = {"error": str(e)}
        
        print(f"\n✅ Completed {completed}/{total} collectors")

        # Add metadata
        results['metadata'] = {
            "repository_path": str(self.repo_path),
            "repository_name": self.repo_path.name,
            "collection_date": datetime.now().isoformat(),
            "cortex_version": self._get_cortex_version(),
            "data_version": "1.0"
        }

        logger.info("Data collection complete!")
        
        # Skip consolidation if requested (for faster iteration/testing)
        if self.skip_consolidation:
            print("\n⚡ Skipping consolidation and reconciliation (--skip-consolidation enabled)")
            print("   Raw collector output will be saved directly")
            logger.info("Consolidation skipped per --skip-consolidation flag")
            return results
        
        # STEP 1: Independent data validation (ground truth verification)
        print("\n🔍 Running independent data validation...")
        logger.info("🔍 Running independent data validation (ground truth check)...")
        import time
        start = time.time()
        results = self._validate_collector_data(results)
        elapsed = time.time() - start
        print(f"✅ Data validation complete in {elapsed:.1f}s")
        if '_validation' in results and results['_validation'].get('corrections_applied'):
            corrections_count = len(results['_validation']['corrections_applied'])
            print(f"   🔧 Applied {corrections_count} corrections")
            logger.info(f"✅ Data validation: {corrections_count} corrections applied")
        
        # STEP 2: Data consolidation and narrative validation
        print("\n🔍 Running data consolidation and validation...")
        logger.info("🔍 Running data consolidation and validation...")
        start = time.time()
        results = self._consolidate_data(results)
        elapsed = time.time() - start
        print(f"✅ Data consolidation complete in {elapsed:.1f}s")
        logger.info("✅ Data consolidation complete")
        
        # Run reconciliation engine
        print("\n🔍 Running reconciliation engine...")
        logger.info("Running reconciliation engine...")
        start = time.time()
        reconciliation_result = self._reconcile_data(results)
        elapsed = time.time() - start
        
        if reconciliation_result:
            results['reconciliation'] = reconciliation_result
            violations_count = len(reconciliation_result.get('violations', []))
            anomalies_count = len(reconciliation_result.get('anomalies', []))
            overall_score = reconciliation_result.get('reconciled_data', {}).get('overall_score', 0)
            
            print(f"✅ Reconciliation complete in {elapsed:.1f}s")
            print(f"   📊 Overall Score: {overall_score}/100")
            print(f"   ⚠️  Violations: {violations_count}")
            print(f"   🔍 Anomalies: {anomalies_count}")
            logger.info(f"✅ Reconciliation complete: {violations_count} violations, {anomalies_count} anomalies")
        else:
            print(f"⚠️  Reconciliation skipped (elapsed: {elapsed:.1f}s)")
            logger.warning("Reconciliation failed or skipped")
        
        return results
    
    def _validate_collector_data(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Independent validation layer - verifies collector data against ground truth.
        
        Fixes common issues:
        - False positive languages (files in Tools/, External/)
        - Version hallucinations (.NET 8.0 when actually Framework 4.7.2)
        - Third-party noise (type definition files, library internals)
        - Incorrect primary language ordering
        - Narrative mismatches (mentioning non-existent languages)
        
        Args:
            results: Raw collector data
            
        Returns:
            Validated and corrected data
        """
        try:
            from src.dashboard.validators.data_validator import validate_dashboard_data
            
            logger.info("  🔍 Scanning repository for ground truth...")
            validated_results = validate_dashboard_data(self.repo_path, results)
            
            # Log corrections applied
            if '_validation' in validated_results:
                validation_info = validated_results['_validation']
                corrections = validation_info.get('corrections_applied', [])
                
                if corrections:
                    logger.info(f"  🔧 Applied {len(corrections)} corrections:")
                    for correction in corrections[:5]:  # Show first 5
                        logger.info(f"     - {correction}")
                    if len(corrections) > 5:
                        logger.info(f"     ... and {len(corrections) - 5} more")
                else:
                    logger.info("  ✅ No corrections needed - data matches ground truth")
                
                # Log ground truth languages
                gt_langs = validation_info.get('ground_truth_languages', [])
                if gt_langs:
                    logger.info(f"  📋 Ground truth languages: {', '.join(gt_langs)}")
            
            return validated_results
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            logger.warning("Continuing with unvalidated collector data")
            import traceback
            logger.debug(traceback.format_exc())
            return results
    
    def _consolidate_data(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Consolidate all collected data to ensure narrative consistency.
        All metrics must tell the same story - no contradictions.
        
        Args:
            results: Raw collected data
            
        Returns:
            Consolidated data with narrative analysis
        """
        try:
            from src.dashboard.data.narrative_consolidator import consolidate_dashboard_data
            
            # Prepare data in format expected by consolidator
            all_data = {
                'healthData': results.get('health-data', {}),
                'security': results.get('security', {}),
                'techStack': results.get('tech-stack', {}),
                'architecture': results.get('architecture', {}),
                'codeOrganization': results.get('code-organization', {}),
                'vendors': results.get('vendors', {})
            }
            
            # Run consolidation
            consolidated = consolidate_dashboard_data(str(self.repo_path), all_data)
            
            # Extract narrative analysis for logging
            narrative = consolidated.get('narrative_analysis', {})
            holistic_score = narrative.get('holistic_score', 0)
            theme = narrative.get('dominant_theme', 'unknown')
            consistency = narrative.get('narrative_consistency', 0)
            contradictions = narrative.get('contradictions', [])
            
            logger.info(f"  📊 Holistic Score: {holistic_score}/100")
            logger.info(f"  📖 Narrative Theme: {theme}")
            logger.info(f"  ✓ Consistency: {consistency}%")
            
            if contradictions:
                logger.warning(f"  ⚠️  Found {len(contradictions)} contradictions:")
                for issue in contradictions[:3]:  # Show top 3
                    logger.warning(f"     - [{issue['severity'].upper()}] {issue['description']}")
            
            # Map back to original structure
            results['health-data'] = consolidated.get('healthData', {})
            results['security'] = consolidated.get('security', {})
            results['tech-stack'] = consolidated.get('techStack', {})
            results['architecture'] = consolidated.get('architecture', {})
            results['code-organization'] = consolidated.get('codeOrganization', {})
            results['vendors'] = consolidated.get('vendors', {})
            
            # Add narrative analysis as separate file
            results['narrative-analysis'] = narrative
            
            return results
            
        except Exception as e:
            logger.error(f"Data consolidation failed: {e}")
            logger.warning("Continuing with unconsolidated data")
            return results
    
    def _reconcile_data(self, results: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Reconcile dashboard data for accuracy and consistency.
        Uses industry standards (CVSS, OWASP) to validate metrics.
        
        Args:
            results: Consolidated dashboard data
            
        Returns:
            Reconciliation result dictionary or None if failed
        """
        try:
            from src.dashboard.reconciliation import ReconciliationEngine
            
            # Extract scores from nested structure and flatten for reconciliation
            health_data = results.get('health-data', {})
            security_data = results.get('security', {})
            architecture_data = results.get('architecture', {})
            
            # Build flat data structure for reconciliation
            flat_data = {
                # Core scores
                'security_score': security_data.get('summary', {}).get('score', 0),
                'quality_score': health_data.get('summary', {}).get('overall_score', 0),
                'maintainability_score': health_data.get('summary', {}).get('maintainability_score', 0),
                'architecture_score': architecture_data.get('summary', {}).get('score', 0),
                'test_coverage': health_data.get('testing', {}).get('coverage_percentage', 0),
                
                # Vulnerability counts
                'critical_vulnerabilities': security_data.get('summary', {}).get('critical_count', 0),
                'high_vulnerabilities': security_data.get('summary', {}).get('high_count', 0),
                'security_hotspots': len(security_data.get('hotspots', [])),
                
                # Quality metrics
                'code_smells': health_data.get('summary', {}).get('code_smells', 0),
                'cyclomatic_complexity': health_data.get('summary', {}).get('average_complexity', 0),
                
                # Architecture metrics (if available)
                'modularity_score': architecture_data.get('summary', {}).get('modularity', 0),
            }
            
            # Run reconciliation engine
            engine = ReconciliationEngine()
            repo_name = self.repo_path.name
            result = engine.reconcile(flat_data, repository=repo_name)
            
            # Convert to serializable dict
            return result.to_dict()
            
        except ImportError as e:
            logger.warning(f"Reconciliation engine not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}")
            logger.debug(f"Reconciliation error details:", exc_info=True)
            return None

    def save_results(self, results: Dict[str, Dict[str, Any]]) -> bool:
        """
        Save collected data to dashboard directory.

        Args:
            results: Collected data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Saving results to: {self.output_dir}")

            # Save each data file
            for name, data in results.items():
                if name == 'metadata':
                    output_file = self.output_dir / 'metadata.json'
                else:
                    output_file = self.output_dir / f"{name}.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"  ✓ Saved {output_file.name}")

            # Post-save: Fix executive summary narrative if needed
            self._fix_executive_summary_narrative(results)

            logger.info(f"\n✅ Dashboard data saved successfully to: {self.output_dir}")
            logger.info(f"\nTo view dashboard, run:")
            logger.info(
                f"  python -m src.orchestrators.dashboard_launcher --source \"{self.repo_path}\"")

            return True

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False

    def _fix_executive_summary_narrative(self, results: Dict[str, Any]):
        """
        Post-save fix: Ensure executive summary narrative uses primary language from tech-stack.
        Fixes issue where consolidation generates narrative before validator runs.
        """
        try:
            # Get primary language from validated tech-stack
            tech_stack = results.get('tech-stack', {})
            backend = tech_stack.get('backend', [])
            
            if not backend:
                return
            
            # Primary language is first in backend list (validator sorted by file count)
            primary_lang = backend[0].get('name', 'C#')
            
            # Check if executive summary exists
            exec_summary_file = self.output_dir / 'executive-summary.json'
            if not exec_summary_file.exists():
                return
            
            # Load executive summary
            with open(exec_summary_file, 'r', encoding='utf-8') as f:
                exec_data = json.load(f)
            
            # Fix narrative if it mentions wrong languages
            wrong_languages = ['Python', 'TypeScript', 'Ruby', 'Go', 'Rust']
            actual_languages = [t['name'] for t in backend]
            fixed = False
            
            # Fix what_it_does.summary
            if 'what_it_does' in exec_data and 'summary' in exec_data['what_it_does']:
                summary = exec_data['what_it_does']['summary']
                for wrong_lang in wrong_languages:
                    if wrong_lang not in actual_languages and wrong_lang in summary:
                        summary = summary.replace(f"built with {wrong_lang}", f"built with {primary_lang}")
                        summary = summary.replace(f"using {wrong_lang}", f"using {primary_lang}")
                        exec_data['what_it_does']['summary'] = summary
                        fixed = True
                        logger.info(f"  🔧 Fixed executive summary: replaced {wrong_lang} with {primary_lang}")
            
            # Fix tagline if needed
            if 'tagline' in exec_data:
                tagline = exec_data['tagline']
                for wrong_lang in wrong_languages:
                    if wrong_lang not in actual_languages and wrong_lang in tagline:
                        tagline = tagline.replace(wrong_lang, primary_lang)
                        exec_data['tagline'] = tagline
                        fixed = True
            
            # Save if fixed
            if fixed:
                with open(exec_summary_file, 'w', encoding='utf-8') as f:
                    json.dump(exec_data, f, indent=2, ensure_ascii=False)
                logger.info(f"  ✓ Updated executive-summary.json with correct language")
        
        except Exception as e:
            logger.warning(f"Failed to fix executive summary narrative: {e}")

    # Helper methods

    def _count_files(self) -> int:
        """Count total files in repository."""
        try:
            return len(list(self.repo_path.rglob('*.*')))
        except Exception:
            return 0

    def _count_lines_of_code(self) -> int:
        """Count total lines of code."""
        # Simplified implementation
        return 0

    def _detect_languages(self) -> list:
        """Detect programming languages in repository."""
        extensions = {
            '.cs': 'C#',
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cfm': 'ColdFusion',
            '.sql': 'SQL'
        }

        lang_counts = {}

        for ext, lang in extensions.items():
            files = list(self.repo_path.rglob(f'*{ext}'))
            if files:
                lang_counts[lang] = len(files)

        # Sort by file count
        return [
            {"name": lang, "file_count": count, "percentage": 0}
            for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
        ]

    def _detect_frameworks(self) -> Dict[str, list]:
        """Detect frameworks in repository."""
        frameworks = {
            'frontend': [],
            'backend': [],
            'databases': [],
            'testing': [],
            'infrastructure': []
        }

        # Check for common framework indicators
        if (self.repo_path / 'package.json').exists():
            frameworks['frontend'].append('Node.js')

        if (self.repo_path / 'requirements.txt').exists():
            frameworks['backend'].append('Python')

        if list(self.repo_path.rglob('*.csproj')):
            frameworks['backend'].append('.NET')

        return frameworks

    def _get_cortex_version(self) -> str:
        """Get CORTEX version."""
        try:
            version_file = Path(__file__).parent.parent.parent / 'VERSION'
            if version_file.exists():
                return version_file.read_text().strip()
        except Exception:
            pass
        return "unknown"
    
    def _consolidate_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate and validate collected data.
        
        This critical step:
        - Validates each collector's output
        - Cross-validates metrics for consistency
        - Detects anomalies and contradictions
        - Triggers specialized deep scans if needed
        - Calculates accurate holistic scores
        - Generates prioritized recommendations
        
        Args:
            results: Raw collected data from all collectors
            
        Returns:
            Consolidated data with validation, scoring, and recommendations
        """
        from src.dashboard.consolidation import DataConsolidator
        
        # Prepare data for consolidator
        consolidated_input = {
            'health_data': results.get('health-data', {}),
            'tech_stack': results.get('tech-stack', {}),
            'security': results.get('security', {}),
            'architecture': results.get('architecture', {}),
            'code_organization': results.get('code-organization', {}),
            'vendors': results.get('vendors', {})
        }
        
        # Run consolidation
        consolidator = DataConsolidator(str(self.repo_path))
        consolidated_data = consolidator.consolidate(consolidated_input)
        
        # Extract consolidation results
        consolidation = consolidated_data.get('consolidation', {})
        holistic_score = consolidation.get('holistic_score', {})
        
        # Update health data with accurate holistic score
        if 'health-data' in results:
            results['health-data']['overall_health_score'] = holistic_score.get('overall_health', 0)
            results['health-data']['score_confidence'] = holistic_score.get('confidence', 1.0)
            results['health-data']['consolidation_applied'] = True
        
        # Add consolidation metadata
        results['consolidation'] = consolidation
        
        # Log key findings
        validation_issues = consolidation.get('validation_issues', [])
        recommendations = consolidation.get('recommendations', [])
        
        logger.info(f"  📊 Holistic Score: {holistic_score.get('overall_health', 0):.1f}")
        logger.info(f"  🔍 Validation Issues: {len(validation_issues)}")
        logger.info(f"  💡 Recommendations: {len(recommendations)}")
        
        if validation_issues:
            critical_issues = [i for i in validation_issues if i['severity'] == 'critical']
            if critical_issues:
                logger.warning(f"  ⚠️  {len(critical_issues)} critical data quality issues detected")
        
        if recommendations:
            critical_recs = [r for r in recommendations if r['priority'] == 'critical']
            if critical_recs:
                logger.warning(f"  🚨 {len(critical_recs)} critical recommendations generated")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate CORTEX dashboard data for any repository"
    )
    parser.add_argument(
        '--path',
        required=True,
        help='Path to repository to analyze'
    )
    parser.add_argument(
        '--output',
        help='Custom name for output directory (default: repo name)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--skip-consolidation',
        action='store_true',
        help='Skip consolidation and reconciliation (save raw collector output only)'
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(message)s'
    )

    print("CORTEX Dashboard Data Collector\n")

    # Validate repository path
    repo_path = Path(args.path)
    if not repo_path.exists():
        logger.error(f"❌ Repository path does not exist: {repo_path}")
        return 1

    if not repo_path.is_dir():
        logger.error(f"❌ Path is not a directory: {repo_path}")
        return 1

    # Create collector and collect data
    collector = DashboardDataCollector(repo_path, args.output, skip_consolidation=args.skip_consolidation)
    results = collector.collect_all()

    # Save results
    if collector.save_results(results):
        print("\n✅ Dashboard data collection complete!")
        return 0
    else:
        print("\n❌ Failed to save dashboard data")
        return 1


if __name__ == '__main__':
    sys.exit(main())
