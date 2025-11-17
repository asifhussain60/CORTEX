"""
CORTEX Optimize Entry Point Orchestrator

⚠️ DEPRECATED: This module is deprecated as of November 17, 2025.
   Use src.operations.modules.optimization.optimize_cortex_orchestrator instead.
   
   This file will be removed in CORTEX 4.0 (targeted for May 2026).

Performs comprehensive system health scans to ensure CORTEX is fully operational.

This orchestrator:
1. Scans all tests and identifies obsolete ones (calling non-existent APIs)
2. Checks code coverage and identifies dead code
3. Validates brain tier integrity (Tier 0, 1, 2, 3)
4. Checks agent health and coordination
5. Validates plugin system integrity
6. Checks dependency health
7. Generates comprehensive health report
8. Marks obsolete tests for cleanup

Natural Language Triggers:
- "optimize cortex"
- "run health check"
- "system scan"
- "check cortex health"
- "optimize workspace"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Date: November 11, 2025
"""

import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
import json
import ast
import logging
import subprocess
import importlib.util
import os
from collections import defaultdict

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationPhase,
    OperationResult,
    OperationModuleMetadata,
    OperationStatus
)

logger = logging.getLogger(__name__)


@dataclass
class HealthIssue:
    """Represents a health issue found during scan"""
    severity: str  # critical, high, medium, low
    category: str  # test, coverage, brain, agent, plugin, dependency
    title: str
    description: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ObsoleteTest:
    """Represents a test file that should be deleted"""
    file_path: Path
    reason: str
    missing_imports: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class SystemHealthReport:
    """Complete system health report"""
    timestamp: datetime
    overall_health: str  # excellent, good, fair, poor, critical
    health_score: float  # 0.0 to 100.0
    issues: List[HealthIssue] = field(default_factory=list)
    obsolete_tests: List[ObsoleteTest] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_health': self.overall_health,
            'health_score': self.health_score,
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'title': issue.title,
                    'description': issue.description,
                    'file_path': str(issue.file_path) if issue.file_path else None,
                    'line_number': issue.line_number,
                    'recommendation': issue.recommendation,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in self.issues
            ],
            'obsolete_tests': [
                {
                    'file_path': str(test.file_path),
                    'reason': test.reason,
                    'missing_imports': test.missing_imports,
                    'confidence': test.confidence
                }
                for test in self.obsolete_tests
            ],
            'statistics': self.statistics,
            'recommendations': self.recommendations
        }


class OptimizeCortexOrchestrator(BaseOperationModule):
    """
    ⚠️ DEPRECATED: Use optimization.optimize_cortex_orchestrator instead.
    
    Comprehensive CORTEX optimization and health check orchestrator.
    
    Performs full system scan to ensure CORTEX is operational:
    - Identifies obsolete tests calling non-existent APIs
    - Checks code coverage and dead code
    - Validates brain integrity
    - Checks agent and plugin health
    - Generates actionable health report
    """
    
    def __init__(self, project_root: Path = None):
        super().__init__()
        
        # Emit deprecation warning
        warnings.warn(
            "optimize.optimize_cortex_orchestrator is deprecated and will be removed in CORTEX 4.0. "
            "Use optimization.optimize_cortex_orchestrator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        self.project_root = project_root or Path.cwd()
        self.report = SystemHealthReport(
            timestamp=datetime.now(),
            overall_health="unknown",
            health_score=0.0
        )
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata"""
        return OperationModuleMetadata(
            module_id="optimize_cortex",
            name="CORTEX Optimization Orchestrator",
            description="Comprehensive system health scan and optimization",
            version="1.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['health', 'optimization', 'maintenance', 'testing']
        )
    
    def check_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if optimization can run"""
        issues = []
        
        # Verify project structure
        if not (self.project_root / 'src').exists():
            issues.append("Missing src/ directory")
        
        if not (self.project_root / 'tests').exists():
            issues.append("Missing tests/ directory")
        
        if not (self.project_root / 'cortex-brain').exists():
            issues.append("Missing cortex-brain/ directory")
        
        return {
            'prerequisites_met': len(issues) == 0,
            'issues': issues
        }
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive CORTEX optimization.
        
        Args:
            context: Execution context with optional settings:
                - profile: 'quick' | 'standard' | 'deep' (default: standard)
                - scan_tests: bool (default: True)
                - scan_coverage: bool (default: True)
                - scan_brain: bool (default: True)
                - mark_obsolete: bool (default: True)
        
        Returns:
            OperationResult with health report and recommendations
        """
        try:
            profile = context.get('profile', 'standard')
            start_time = datetime.now()
            
            logger.info("=" * 80)
            logger.info("CORTEX OPTIMIZE ORCHESTRATOR")
            logger.info("=" * 80)
            logger.info(f"Profile: {profile}")
            logger.info(f"Project Root: {self.project_root}")
            logger.info("")
            
            # Phase 1: Scan tests for obsolete ones
            if context.get('scan_tests', True):
                logger.info("Phase 1: Scanning test files...")
                self._scan_obsolete_tests()
                logger.info(f"  Found {len(self.report.obsolete_tests)} obsolete tests")
            
            # Phase 2: Check code coverage
            if context.get('scan_coverage', True) and profile in ['standard', 'deep']:
                logger.info("\nPhase 2: Analyzing code coverage...")
                self._analyze_coverage()
            
            # Phase 3: Validate brain integrity
            if context.get('scan_brain', True):
                logger.info("\nPhase 3: Validating brain integrity...")
                self._validate_brain_integrity()
            
            # Phase 4: Check agent health
            if profile == 'deep':
                logger.info("\nPhase 4: Checking agent health...")
                self._check_agent_health()
            
            # Phase 5: Check plugin system
            if profile == 'deep':
                logger.info("\nPhase 5: Validating plugin system...")
                self._check_plugin_health()
            
            # Phase 6: Comprehensive brain health diagnostics
            logger.info("\nPhase 6: Running brain health diagnostics...")
            self._check_brain_health()
            
            # Phase 7: Calculate health score
            logger.info("\nCalculating system health score...")
            self._calculate_health_score()
            
            # Phase 8: Generate recommendations
            logger.info("Generating recommendations...")
            self._generate_recommendations()
            
            # Phase 9: Mark obsolete tests for cleanup
            if context.get('mark_obsolete', True) and self.report.obsolete_tests:
                logger.info(f"\nMarking {len(self.report.obsolete_tests)} obsolete tests for cleanup...")
                self._mark_tests_for_cleanup()
            
            # Save report
            report_path = self._save_report()
            
            # Duration
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info("\n" + "=" * 80)
            logger.info("OPTIMIZATION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Overall Health: {self.report.overall_health.upper()}")
            logger.info(f"Health Score: {self.report.health_score:.1f}/100")
            logger.info(f"Issues Found: {len(self.report.issues)}")
            logger.info(f"Obsolete Tests: {len(self.report.obsolete_tests)}")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Report: {report_path}")
            logger.info("=" * 80)
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"System health: {self.report.overall_health} ({self.report.health_score:.1f}/100)",
                data={
                    'health_report': self.report.to_dict(),
                    'report_path': str(report_path),
                    'duration_seconds': duration
                }
            )
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Optimization failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _scan_obsolete_tests(self) -> None:
        """Scan test files for obsolete tests calling non-existent APIs"""
        tests_dir = self.project_root / 'tests'
        if not tests_dir.exists():
            return
        
        obsolete_count = 0
        
        for test_file in tests_dir.rglob('test_*.py'):
            try:
                # Parse test file
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Check imports
                missing_imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        module_name = node.module
                        if module_name and module_name.startswith('src.'):
                            # Check if module exists
                            if not self._module_exists(module_name):
                                missing_imports.append(module_name)
                
                # If test imports non-existent modules, mark as obsolete
                if missing_imports:
                    obsolete_test = ObsoleteTest(
                        file_path=test_file,
                        reason=f"Imports non-existent modules: {', '.join(missing_imports)}",
                        missing_imports=missing_imports,
                        confidence=0.9
                    )
                    self.report.obsolete_tests.append(obsolete_test)
                    obsolete_count += 1
                    
                    # Add as issue
                    issue = HealthIssue(
                        severity='medium',
                        category='test',
                        title=f"Obsolete test file: {test_file.name}",
                        description=f"Test imports non-existent modules: {', '.join(missing_imports)}",
                        file_path=test_file,
                        recommendation="Delete this test file as it tests non-existent code",
                        auto_fixable=True
                    )
                    self.report.issues.append(issue)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {test_file}: {e}")
        
        self.report.statistics['obsolete_tests_found'] = obsolete_count
    
    def _module_exists(self, module_name: str) -> bool:
        """Check if a Python module exists"""
        try:
            # Convert module name to file path
            parts = module_name.split('.')
            if parts[0] == 'src':
                module_path = self.project_root / '/'.join(parts) + '.py'
                if module_path.exists():
                    return True
                
                # Check if it's a package
                package_path = self.project_root / '/'.join(parts) / '__init__.py'
                return package_path.exists()
            
            return False
        except Exception:
            return False
    
    def _analyze_coverage(self) -> None:
        """Analyze code coverage"""
        try:
            # Run pytest with coverage
            result = subprocess.run(
                ['pytest', '--cov=src', '--cov-report=json', '--quiet'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Read coverage report
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                self.report.statistics['code_coverage_percent'] = total_coverage
                
                # Flag low coverage files
                for file_path, file_data in coverage_data.get('files', {}).items():
                    coverage = file_data.get('summary', {}).get('percent_covered', 0)
                    if coverage < 50:
                        issue = HealthIssue(
                            severity='low',
                            category='coverage',
                            title=f"Low coverage: {Path(file_path).name}",
                            description=f"Only {coverage:.1f}% coverage",
                            file_path=Path(file_path),
                            recommendation="Add more tests for this file"
                        )
                        self.report.issues.append(issue)
            
        except subprocess.TimeoutExpired:
            logger.warning("Coverage analysis timed out")
        except Exception as e:
            logger.warning(f"Coverage analysis failed: {e}")
    
    def _validate_brain_integrity(self) -> None:
        """Validate brain tier integrity"""
        brain_dir = self.project_root / 'cortex-brain'
        
        # Check tier directories
        required_tiers = ['tier1', 'tier2', 'tier3']
        for tier in required_tiers:
            tier_path = brain_dir / tier
            if not tier_path.exists():
                issue = HealthIssue(
                    severity='critical',
                    category='brain',
                    title=f"Missing brain tier: {tier}",
                    description=f"Required brain tier directory not found: {tier_path}",
                    recommendation=f"Initialize {tier} brain tier"
                )
                self.report.issues.append(issue)
        
        # SKULL-011: Validate distributed database architecture
        # Check for proper tier-specific database usage
        from src.config import config
        
        # Verify tier-specific databases exist (not monolithic)
        expected_dbs = [
            config.tier1_db_path,
            config.tier2_db_path, 
            config.tier3_db_path
        ]
        
        for db_path in expected_dbs:
            if not db_path.exists():
                tier_name = db_path.name.split('-')[0]  # Extract tier1/tier2/tier3
                issue = HealthIssue(
                    severity='medium',
                    category='brain',
                    title=f"Missing {tier_name.upper()} database",
                    description=f"Database file not found: {db_path.name}",
                    file_path=str(db_path),
                    recommendation=f"Initialize {tier_name.upper()} database",
                    auto_fixable=True
                )
                self.report.issues.append(issue)
        
        # Scan source code for monolithic database references
        src_dir = self.project_root / 'src'
        if src_dir.exists():
            monolithic_refs = []
            for py_file in src_dir.rglob('*.py'):
                # Skip test files
                if 'test' in py_file.name.lower() or 'tests' in str(py_file):
                    continue
                
                # Skip scanner files to prevent self-detection
                if any(skip_pattern in str(py_file) for skip_pattern in [
                    'optimize_cortex_orchestrator.py',  # SCANNER-SAFE: Skip self
                    'optimize/',  # SCANNER-SAFE: Skip optimizer directory
                    'health',     # SCANNER-SAFE: Skip health modules
                ]):
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    # Check for legacy monolithic database references
                    legacy_patterns = ['cortex-brain.db', 'cortex-brain/cortex-brain.db']  # SCANNER-SAFE: This is the scanner code itself
                    for pattern in legacy_patterns:
                        if pattern in content:
                            # Find line numbers
                            for line_num, line in enumerate(content.splitlines(), 1):
                                if pattern in line and not line.strip().startswith('#'):  # Skip comments
                                    # Skip scanner code itself
                                    if 'SCANNER-SAFE' in line or 'legacy_patterns' in line:
                                        continue
                                    monolithic_refs.append((py_file, line_num, line.strip()))
                except Exception as e:
                    logger.warning(f"Could not scan {py_file}: {e}")
            
            if monolithic_refs:
                for file_path, line_num, line_content in monolithic_refs:
                    issue = HealthIssue(
                        severity='high',
                        category='brain',
                        title="Monolithic database reference in code (SKULL-011)",
                        description=f"Line {line_num}: {line_content[:80]}",
                        file_path=file_path,
                        line_number=line_num,
                        recommendation="Use ConfigManager.get_tier1_conversations_path() or tier-specific paths",
                        auto_fixable=True
                    )
                    self.report.issues.append(issue)
                
                self.report.statistics['legacy_db_refs'] = len(monolithic_refs)  # SCANNER-SAFE: Statistics tracking
        
        # Check tier-specific brain databases
        tier_dbs = {
            'tier1': ['conversations.db', 'working_memory.db'],
            'tier2': ['knowledge_graph.db'],
            'tier3': ['context.db']
        }
        
        total_size_mb = 0
        for tier, db_names in tier_dbs.items():
            tier_path = brain_dir / tier
            if tier_path.exists():
                for db_name in db_names:
                    db_path = tier_path / db_name
                    if db_path.exists():
                        size_mb = db_path.stat().st_size / (1024 * 1024)
                        total_size_mb += size_mb
                    else:
                        issue = HealthIssue(
                            severity='medium',
                            category='brain',
                            title=f"Missing {tier} database",
                            description=f"Database file not found: {db_name}",
                            recommendation=f"Initialize {tier} brain tier"
                        )
                        self.report.issues.append(issue)
        
        self.report.statistics['brain_db_size_mb'] = total_size_mb
        
        if total_size_mb > 100:
            issue = HealthIssue(
                severity='medium',
                category='brain',
                title="Large brain databases",
                description=f"Total brain database size is {total_size_mb:.1f} MB",
                recommendation="Consider vacuuming or archiving old conversations"
            )
            self.report.issues.append(issue)
    
    def _check_agent_health(self) -> None:
        """Check agent system health"""
        agents_dir = self.project_root / 'src' / 'cortex_agents'
        if not agents_dir.exists():
            return
        
        expected_agents = [
            'intent_detector.py',
            'code_executor.py',
            'test_generator.py',
            'validator.py',
            'work_planner.py',
            'health_validator.py',
            'architect.py',
            'pattern_matcher.py',
            'learner.py',
            'documenter.py'
        ]
        
        missing_agents = []
        for agent_file in expected_agents:
            if not (agents_dir / agent_file).exists():
                missing_agents.append(agent_file)
        
        if missing_agents:
            issue = HealthIssue(
                severity='high',
                category='agent',
                title="Missing agent files",
                description=f"Missing {len(missing_agents)} agent files: {', '.join(missing_agents)}",
                recommendation="Restore missing agent files from backup or repository"
            )
            self.report.issues.append(issue)
        
        self.report.statistics['agents_found'] = len(expected_agents) - len(missing_agents)
        self.report.statistics['agents_missing'] = len(missing_agents)
    
    def _check_plugin_health(self) -> None:
        """Check plugin system health"""
        plugins_dir = self.project_root / 'src' / 'plugins'
        if not plugins_dir.exists():
            return
        
        plugin_files = list(plugins_dir.glob('*_plugin.py'))
        self.report.statistics['plugins_found'] = len(plugin_files)
        
        # Check base plugin exists
        base_plugin = plugins_dir / 'base_plugin.py'
        if not base_plugin.exists():
            issue = HealthIssue(
                severity='critical',
                category='plugin',
                title="Missing base plugin",
                description="BasePlugin class not found",
                recommendation="Restore base_plugin.py"
            )
            self.report.issues.append(issue)
    
    def _check_brain_health(self) -> None:
        """Comprehensive brain health diagnostics (Tier 0-3 + Agents)"""
        brain_health = {
            'tier0_protection': False,
            'tier1_memory': False,
            'tier2_knowledge': False,
            'tier3_context': False,
            'agent_coordination': False,
            'entry_points': False
        }
        
        # Tier 0: Brain Protection Rules
        try:
            from src.tier0.brain_protector import BrainProtector
            bp = BrainProtector()
            protection_layers = bp.protection_layers
            tier0_instincts = bp.TIER0_INSTINCTS
            skull_count = sum(1 for instinct in tier0_instincts if instinct.startswith("SKULL"))
            
            logger.info(f"  Tier 0: {len(protection_layers)} layers, {len(tier0_instincts)} instincts, {skull_count} SKULL rules")
            self.report.statistics['tier0_protection_layers'] = len(protection_layers)
            self.report.statistics['tier0_skull_rules'] = skull_count
            brain_health['tier0_protection'] = True
        except Exception as e:
            logger.warning(f"  Tier 0: Failed to load brain protector - {e}")
            issue = HealthIssue(
                severity='high',
                category='brain',
                title="Tier 0 brain protection unavailable",
                description=str(e)
            )
            self.report.issues.append(issue)
        
        # Tier 1: Working Memory
        db_path = self.project_root / 'cortex-brain' / 'tier1' / 'working_memory.db'
        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                
                cur.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM messages")
                msg_count = cur.fetchone()[0]
                
                logger.info(f"  Tier 1: {conv_count} conversations, {msg_count} messages")
                self.report.statistics['tier1_conversations'] = conv_count
                self.report.statistics['tier1_messages'] = msg_count
                brain_health['tier1_memory'] = True
                
                conn.close()
            except Exception as e:
                logger.warning(f"  Tier 1: Database error - {e}")
        else:
            logger.warning("  Tier 1: Working memory database not initialized")
        
        # Tier 2: Knowledge Graph
        kg_path = self.project_root / 'cortex-brain' / 'knowledge-graph.yaml'
        if kg_path.exists():
            try:
                import yaml
                with open(kg_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                patterns = data.get('patterns', {})
                lessons = data.get('lessons_learned', {})
                
                logger.info(f"  Tier 2: {len(patterns)} patterns, {len(lessons)} lessons")
                self.report.statistics['tier2_patterns'] = len(patterns)
                self.report.statistics['tier2_lessons'] = len(lessons)
                brain_health['tier2_knowledge'] = True
            except Exception as e:
                logger.warning(f"  Tier 2: Failed to load knowledge graph - {e}")
        else:
            logger.warning("  Tier 2: Knowledge graph not initialized")
        
        # Tier 3: Development Context
        dev_ctx_path = self.project_root / 'cortex-brain' / 'development-context.yaml'
        if dev_ctx_path.exists():
            logger.info("  Tier 3: Development context tracking active")
            self.report.statistics['tier3_active'] = True
            brain_health['tier3_context'] = True
        else:
            logger.warning("  Tier 3: Development context not initialized")
        
        # Agent Coordination
        try:
            from src.cortex_agents.intent_router import IntentRouter
            logger.info("  Agents: Intent & Investigation routers operational")
            self.report.statistics['agent_coordination'] = True
            brain_health['agent_coordination'] = True
        except ImportError as e:
            logger.warning(f"  Agents: Router import failed - {e}")
        
        # Entry Points
        cortex_prompt = self.project_root / '.github' / 'prompts' / 'CORTEX.prompt.md'
        if cortex_prompt.exists():
            logger.info("  Entry Points: CORTEX.prompt.md present")
            brain_health['entry_points'] = True
        else:
            logger.warning("  Entry Points: CORTEX.prompt.md not found")
        
        # Store overall brain health status
        healthy_components = sum(brain_health.values())
        total_components = len(brain_health)
        health_percentage = (healthy_components / total_components) * 100
        
        self.report.statistics['brain_health_percentage'] = health_percentage
        logger.info(f"  Brain Health: {healthy_components}/{total_components} components operational ({health_percentage:.1f}%)")
    
    def _calculate_health_score(self) -> None:
        """Calculate overall health score based on issues"""
        base_score = 100.0
        
        # Deduct points for issues
        severity_weights = {
            'critical': 25.0,
            'high': 10.0,
            'medium': 5.0,
            'low': 2.0
        }
        
        for issue in self.report.issues:
            weight = severity_weights.get(issue.severity, 2.0)
            base_score -= weight
        
        # Ensure score is 0-100
        self.report.health_score = max(0.0, min(100.0, base_score))
        
        # Determine overall health
        if self.report.health_score >= 90:
            self.report.overall_health = "excellent"
        elif self.report.health_score >= 75:
            self.report.overall_health = "good"
        elif self.report.health_score >= 50:
            self.report.overall_health = "fair"
        elif self.report.health_score >= 25:
            self.report.overall_health = "poor"
        else:
            self.report.overall_health = "critical"
    
    def _generate_recommendations(self) -> None:
        """Generate actionable recommendations"""
        # Obsolete tests recommendation
        if self.report.obsolete_tests:
            self.report.recommendations.append(
                f"Run 'cleanup workspace' to remove {len(self.report.obsolete_tests)} obsolete test files"
            )
        
        # Coverage recommendation
        coverage = self.report.statistics.get('code_coverage_percent', 0)
        if coverage < 80:
            self.report.recommendations.append(
                f"Increase code coverage from {coverage:.1f}% to at least 80%"
            )
        
        # Critical issues
        critical_issues = [i for i in self.report.issues if i.severity == 'critical']
        if critical_issues:
            self.report.recommendations.append(
                f"Address {len(critical_issues)} critical issues immediately"
            )
        
        # Brain database
        brain_size = self.report.statistics.get('brain_db_size_mb', 0)
        if brain_size > 100:
            self.report.recommendations.append(
                "Vacuum brain database to optimize performance"
            )
    
    def _mark_tests_for_cleanup(self) -> None:
        """Mark obsolete tests for cleanup orchestrator"""
        manifest_file = self.project_root / 'cortex-brain' / 'obsolete-tests-manifest.json'
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'marked_by': 'optimize_cortex_orchestrator',
            'tests': [
                {
                    'file_path': str(test.file_path.relative_to(self.project_root)),
                    'reason': test.reason,
                    'missing_imports': test.missing_imports,
                    'confidence': test.confidence
                }
                for test in self.report.obsolete_tests
            ]
        }
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Created obsolete tests manifest: {manifest_file}")
    
    def _save_report(self) -> Path:
        """Save health report to file"""
        report_dir = self.project_root / 'cortex-brain' / 'health-reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'health-report-{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report.to_dict(), f, indent=2)
        
        return report_file


def register() -> OptimizeCortexOrchestrator:
    """Register the optimize orchestrator module"""
    return OptimizeCortexOrchestrator()
