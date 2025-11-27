"""
System Alignment Validators

Large validation methods extracted from System Alignment Orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.operations.modules.admin.alignment_models import (
    AlignmentReport,
    IntegrationScore,
    RemediationSuggestion
)
from src.utils.progress_monitor import ProgressMonitor

logger = logging.getLogger(__name__)


class FullValidationRunner:
    """Runs complete system alignment validation with all phases."""
    
    def __init__(
        self,
        project_root: Path,
        config: Dict[str, Any],
        discover_orchestrators_callback: callable,
        discover_agents_callback: callable,
        validate_entry_points_callback: callable,
        calculate_integration_score_callback: callable,
        validate_deployment_readiness_callback: callable,
        validate_gap_remediation_callback: callable,
        validate_file_organization_callback: callable,
        validate_template_headers_callback: callable,
        validate_documentation_governance_callback: callable,
        detect_conflicts_callback: callable,
        generate_fix_templates_callback: callable,
        generate_dashboard_callback: callable,
        generate_remediation_suggestions_callback: callable,
        is_production_feature_callback: callable,
        get_classification_callback: callable,
        get_feature_files_callback: callable,
        score_to_dict_callback: callable,
        dict_to_score_callback: callable
    ):
        """Initialize with all necessary callbacks."""
        self.project_root = project_root
        self.config = config
        self._discover_orchestrators = discover_orchestrators_callback
        self._discover_agents = discover_agents_callback
        self._validate_entry_points = validate_entry_points_callback
        self._calculate_integration_score = calculate_integration_score_callback
        self._validate_deployment_readiness = validate_deployment_readiness_callback
        self._validate_gap_remediation_components = validate_gap_remediation_callback
        self._validate_file_organization = validate_file_organization_callback
        self._validate_template_headers = validate_template_headers_callback
        self._validate_documentation_governance = validate_documentation_governance_callback
        self._detect_conflicts = detect_conflicts_callback
        self._generate_fix_templates = generate_fix_templates_callback
        self._generate_dashboard = generate_dashboard_callback
        self._generate_remediation_suggestions = generate_remediation_suggestions_callback
        self._is_production_feature = is_production_feature_callback
        self._get_classification = get_classification_callback
        self._get_feature_files = get_feature_files_callback
        self._score_to_dict = score_to_dict_callback
        self._dict_to_score = dict_to_score_callback
    
    def run(self, monitor: Optional[ProgressMonitor] = None) -> AlignmentReport:
        """Run complete system alignment validation."""
        from src.tier1.cache_facade import get_cache
        cache = get_cache()
        
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=0
        )
        
        # Phase 1: Discover all features (with caching)
        if monitor:
            monitor.update("Discovering orchestrators and agents")
        
        operations_dir = self.project_root / 'src' / 'operations'
        agents_dir = self.project_root / 'src' / 'agents'
        
        # Try cache for orchestrators
        orchestrators = cache.get('align', 'orchestrators', [operations_dir])
        if orchestrators is None:
            logger.info("Cache MISS: orchestrators - running discovery")
            orchestrators = self._discover_orchestrators()
            cache.set('align', 'orchestrators', orchestrators, [operations_dir], ttl_seconds=0)
        else:
            logger.info("Cache HIT: orchestrators - using cached discovery")
        
        # Try cache for agents
        agents = cache.get('align', 'agents', [agents_dir])
        if agents is None:
            logger.info("Cache MISS: agents - running discovery")
            agents = self._discover_agents()
            cache.set('align', 'agents', agents, [agents_dir], ttl_seconds=0)
        else:
            logger.info("Cache HIT: agents - using cached discovery")
        
        # Phase 1.5: Discover entry points and validate wiring
        if monitor:
            monitor.update("Validating entry point wiring")
        orphaned, ghost = self._validate_entry_points(orchestrators)
        report.orphaned_triggers = orphaned
        report.ghost_features = ghost
        
        # Phase 2: Validate integration depth (with caching)
        total_features = len(orchestrators) + len(agents.get('agents', {}))
        current_idx = 0
        
        for name, metadata in orchestrators.items():
            current_idx += 1
            if monitor:
                monitor.update(f"Scoring integrations", current_idx, total_features)
            
            # Get feature files for cache tracking
            feature_files = self._get_feature_files(name, metadata)
            
            # Try cache for integration score
            cache_key = f'integration_score:{name}'
            score = cache.get('align', cache_key, feature_files)
            
            if score is None:
                logger.debug(f"Cache MISS: {cache_key} - calculating score")
                score = self._calculate_integration_score(name, metadata, "orchestrator")
                # Convert dataclass to dict for JSON serialization
                cache.set('align', cache_key, self._score_to_dict(score), feature_files, ttl_seconds=0)
            else:
                logger.debug(f"Cache HIT: {cache_key} - using cached score")
                score = self._dict_to_score(score)
            
            report.feature_scores[name] = score
            
            # Categorize issues
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        for name, metadata in agents.items():
            current_idx += 1
            if monitor:
                monitor.update(f"Scoring integrations", current_idx, total_features)
            
            feature_files = self._get_feature_files(name, metadata)
            cache_key = f'integration_score:{name}'
            
            score = cache.get('align', cache_key, feature_files)
            if score is None:
                logger.debug(f"Cache MISS: {cache_key} - calculating score")
                score = self._calculate_integration_score(name, metadata, "agent")
                cache.set('align', cache_key, self._score_to_dict(score), feature_files, ttl_seconds=0)
            else:
                logger.debug(f"Cache HIT: {cache_key} - using cached score")
                score = self._dict_to_score(score)
            
            report.feature_scores[name] = score
            
            if score.score < 70:
                report.critical_issues += 1
            elif score.score < 90:
                report.warnings += 1
        
        # Share integration scores with deploy operation
        cache.share_result('align', 'deploy', 'orchestrators')
        cache.share_result('align', 'deploy', 'agents')
        for name in list(orchestrators.keys()) + list(agents.keys()):
            cache.share_result('align', 'deploy', f'integration_score:{name}')
        
        # Phase 3: Validate deployment readiness
        if monitor:
            monitor.update("Validating deployment readiness")
        self._validate_deployment_readiness(report)
        
        # Phase 3.6: Validate gap remediation
        if monitor:
            monitor.update("Validating gap remediation")
        self._validate_gap_remediation_components(report)
        
        # Phase 3.7: Validate file organization
        if monitor:
            monitor.update("Validating file organization")
        org_results = self._validate_file_organization()
        report.organization_violations = org_results.get('violations', [])
        report.organization_score = org_results.get('score', 100)
        
        # Phase 3.8: Validate template headers
        if monitor:
            monitor.update("Validating template headers")
        header_results = self._validate_template_headers()
        report.header_violations = header_results.get('violations', [])
        report.header_compliance_score = header_results.get('score', 100)
        
        # Phase 3.9: Validate documentation governance
        if monitor:
            monitor.update("Checking documentation governance")
        doc_gov_results = self._validate_documentation_governance()
        report.doc_governance_violations = doc_gov_results.get('violations', [])
        report.doc_governance_score = doc_gov_results.get('score', 100)
        
        # Phase 3.10: Detect conflicts (skip if configured)
        skip_duplicate_detection = self.config.get('system_alignment', {}).get('skip_duplicate_detection', False)
        
        if skip_duplicate_detection:
            if monitor:
                monitor.update("Skipping conflict detection (config: skip_duplicate_detection=true)")
            logger.info("Conflict detection skipped per configuration")
            conflicts = []
        else:
            if monitor:
                monitor.update("Detecting ecosystem conflicts")
            conflicts = self._detect_conflicts()
        
        report.conflicts = conflicts
        
        # Update critical/warning counts from conflicts
        for conflict in conflicts:
            if conflict.severity == 'critical':
                report.critical_issues += 1
            elif conflict.severity == 'warning':
                report.warnings += 1
        
        # Phase 3.11: Generate fix templates
        if monitor:
            monitor.update("Generating fix templates")
        fix_templates = self._generate_fix_templates(conflicts)
        report.fix_templates = fix_templates
        
        # Phase 3.12: Generate dashboard
        if monitor:
            monitor.update("Generating health dashboard")
        dashboard = self._generate_dashboard(report, conflicts)
        report.dashboard_report = dashboard
        
        # Phase 4: Generate remediation suggestions
        if monitor:
            monitor.update("Generating remediation suggestions")
        self._generate_remediation_suggestions(report, orchestrators, agents)
        
        # Calculate overall health
        if report.feature_scores:
            production_scores = [
                s for s in report.feature_scores.values()
                if self._is_production_feature(s.feature_name, orchestrators, agents)
            ]
            
            if production_scores:
                total_score = sum(s.score for s in production_scores)
                report.overall_health = total_score // len(production_scores)
                
                # Log classification breakdown
                admin_count = sum(1 for s in report.feature_scores.values() 
                                 if self._get_classification(s.feature_name, orchestrators, agents) == "admin")
                internal_count = sum(1 for s in report.feature_scores.values() 
                                    if self._get_classification(s.feature_name, orchestrators, agents) == "internal")
                production_count = len(production_scores)
                
                logger.info(f"Feature classification: {production_count} production, {admin_count} admin, {internal_count} internal")
            else:
                report.overall_health = 100
        else:
            report.overall_health = 100
        
        return report
