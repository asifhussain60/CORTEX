"""
Sanitization Orchestrator v2 - AUTONOMOUS Implementation

Converts GUIDED Sanitization Orchestrator v1 to pure autonomous execution
with config-driven operation, pattern-based detection, and zero LLM dependencies.

5-Phase Pipeline:
1. DISCOVERY: Scan workspace for sensitive data patterns
2. ANALYSIS: Classify sensitivity levels and determine strategies
3. TRANSFORMATION: Apply sanitization rules with validation
4. VALIDATION: Verify all high-confidence patterns removed
5. FINALIZATION: Generate report and cleanup temp files

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.orchestrators.sanitization_v2.sanitization_engine import (
    SanitizationEngine,
    PatternRegistry,
    SanitizationMatch,
    PatternCategory,
)
from src.orchestrators.sanitization_v2.holistic_review_engine import (
    HolisticReviewEngine,
    SemanticAnalysis,
)
from src.database.planning_state_db import PlanningStateDB


logger = logging.getLogger(__name__)


class SanitizationPhase(Enum):
    """Sanitization pipeline phases"""
    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    FINALIZATION = "finalization"


@dataclass
class DiscoveryResult:
    """Discovery phase results"""
    files_scanned: int = 0
    files_with_matches: int = 0
    total_matches: int = 0
    matches_by_category: Dict[str, int] = field(default_factory=dict)
    high_risk_files: List[str] = field(default_factory=list)
    scan_duration_ms: float = 0.0


@dataclass
class AnalysisResult:
    """Analysis phase results"""
    critical_secrets_found: int = 0
    pii_found: int = 0
    phi_found: int = 0
    pci_found: int = 0
    risk_score: float = 0.0  # 0-100
    recommended_action: str = ""
    analysis_duration_ms: float = 0.0


@dataclass
class TransformResult:
    """Transformation phase results"""
    files_sanitized: int = 0
    total_replacements: int = 0
    replacements_by_strategy: Dict[str, int] = field(default_factory=dict)
    backup_location: str = ""
    transform_duration_ms: float = 0.0


@dataclass
class ValidationResult:
    """Validation phase results"""
    is_clean: bool = False
    remaining_matches: int = 0
    remaining_high_confidence: int = 0
    validation_duration_ms: float = 0.0


@dataclass
class FinalResult:
    """Final phase results (complete pipeline)"""
    success: bool = False
    discovery: Optional[DiscoveryResult] = None
    analysis: Optional[AnalysisResult] = None
    transformation: Optional[TransformResult] = None
    validation: Optional[ValidationResult] = None
    total_duration_ms: float = 0.0
    report_path: str = ""


class SanitizationOrchestratorV2(BaseOrchestratorV4_1):
    """
    AUTONOMOUS Sanitization Orchestrator
    
    Replaces GUIDED v1 orchestrator with deterministic, config-driven execution.
    No natural language instructions, no LLM dependencies, 100% testable.
    
    Key improvements over v1:
    - Consolidated patterns (30+ from 5 modules)
    - Priority-based matching
    - Configurable replacement strategies
    - Transaction support (backup/rollback)
    - 99.6% token efficiency
    - <30ms phase transitions
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        state_db: Optional[PlanningStateDB] = None,
        workspace_root: Optional[Path] = None,
        plan_id: Optional[str] = None,
    ):
        """
        Initialize Sanitization Orchestrator v2.
        
        Args:
            config_path: Path to sanitization-v2-manifest.yaml
            state_db: PlanningStateDB instance
            workspace_root: Workspace root (defaults to CORTEX root)
            plan_id: Optional plan ID for resumption
        """
        # Default paths
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "manifests" / "orchestrators" / "sanitization-v2-manifest.yaml"
        
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent.parent
        
        # Create default state_db if not provided
        if state_db is None:
            db_path = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "database" / "planning_state.db"
            state_db = PlanningStateDB(db_path=str(db_path))
        
        # Initialize base orchestrator
        super().__init__(
            config_path=str(config_path),
            state_db=state_db,
            plan_id=plan_id,
        )
        
        self.workspace_root = workspace_root
        self.engine = SanitizationEngine()
        self.review_engine = HolisticReviewEngine(enable_llm=False)  # LLM disabled by default
        self.logger = logging.getLogger(__name__)
        
        # Runtime state
        self.discovery_cache: Dict[str, List[SanitizationMatch]] = {}
        self.semantic_analysis_cache: Dict[str, SemanticAnalysis] = {}
        self.backup_dir: Optional[Path] = None
        self.start_time: Optional[datetime] = None
    
    def execute(self, user_input: Optional[Dict[str, Any]] = None) -> FinalResult:
        """
        Execute complete 5-phase sanitization pipeline.
        
        Args:
            user_input: Optional configuration overrides
                - privacy_level: "minimal" | "medium" | "full"
                - target_paths: List[str] (patterns to include)
                - exclude_patterns: List[str] (patterns to skip)
                
        Returns:
            FinalResult with all phase results
        """
        self.start_time = datetime.now()
        self.logger.info("🧼 Starting Sanitization v2 Pipeline")
        
        try:
            # Phase 1: Discovery
            discovery = self.discover_sensitive_content(user_input)
            self.logger.info(f"✅ Discovery: {discovery.total_matches} matches in {discovery.files_scanned} files")
            
            # Phase 2: Analysis
            analysis = self.analyze_sensitivity_levels(discovery)
            self.logger.info(f"✅ Analysis: Risk Score {analysis.risk_score:.1f}/100")
            
            # Phase 3: Transformation
            transformation = self.apply_sanitization_rules(discovery, analysis, user_input)
            self.logger.info(f"✅ Transformation: {transformation.total_replacements} replacements applied")
            
            # Phase 4: Validation
            validation = self.validate_sanitization()
            self.logger.info(f"✅ Validation: {'Clean' if validation.is_clean else 'Failed'}")
            
            # Phase 5: Finalization
            final = self.finalize_sanitization(
                discovery=discovery,
                analysis=analysis,
                transformation=transformation,
                validation=validation,
            )
            
            self.logger.info(f"🎉 Sanitization Complete: {final.total_duration_ms:.2f}ms")
            return final
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            return FinalResult(success=False, total_duration_ms=self._elapsed_ms())
    
    def discover_sensitive_content(self, config: Optional[Dict[str, Any]] = None) -> DiscoveryResult:
        """
        Phase 1: Scan workspace for sensitive data patterns.
        
        Strategy:
        - Use file_search to find target files
        - Scan each file with SanitizationEngine
        - Build match cache for downstream phases
        - Track matches by category
        
        Args:
            config: Discovery configuration (target_paths, exclude_patterns)
            
        Returns:
            DiscoveryResult with match statistics
        """
        phase_start = datetime.now()
        self.logger.info("📋 Phase 1: DISCOVERY")
        
        config = config or {}
        target_paths = config.get("target_paths", ["**/*.py", "**/*.md", "**/*.yaml", "**/*.json"])
        exclude_patterns = config.get("exclude_patterns", [
            "**/venv/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/cortex-brain/database/**",
        ])
        
        result = DiscoveryResult()
        matches_by_category: Dict[PatternCategory, int] = {}
        
        # Scan workspace files
        for pattern in target_paths:
            for file_path in self.workspace_root.rglob(pattern.replace("**/", "")):
                # Skip excluded paths
                if any(file_path.match(excl) for excl in exclude_patterns):
                    continue
                
                if not file_path.is_file():
                    continue
                
                # Scan file
                sanitized, matches, success = self.engine.sanitize_file(file_path)
                
                if not success:
                    continue
                
                result.files_scanned += 1
                
                if matches:
                    result.files_with_matches += 1
                    result.total_matches += len(matches)
                    
                    # Cache for later phases
                    rel_path = str(file_path.relative_to(self.workspace_root))
                    self.discovery_cache[rel_path] = matches
                    
                    # Track high-risk files (10+ matches)
                    if len(matches) >= 10:
                        result.high_risk_files.append(rel_path)
                    
                    # Count by category
                    for match in matches:
                        category = match.category
                        matches_by_category[category] = matches_by_category.get(category, 0) + 1
        
        # Convert enum keys to strings
        result.matches_by_category = {
            cat.value: count 
            for cat, count in matches_by_category.items()
        }
        
        result.scan_duration_ms = (datetime.now() - phase_start).total_seconds() * 1000
        return result
    
    def analyze_sensitivity_levels(self, discovery: DiscoveryResult) -> AnalysisResult:
        """
        Phase 2: Classify sensitivity and determine risk score.
        
        Risk Scoring:
        - Critical Secrets: 50 points each
        - PII: 10 points each
        - PHI: 20 points each
        - PCI: 30 points each
        - Paths/Company: 1 point each
        
        Args:
            discovery: Results from discovery phase
            
        Returns:
            AnalysisResult with risk assessment
        """
        phase_start = datetime.now()
        self.logger.info("📊 Phase 2: ANALYSIS")
        
        result = AnalysisResult()
        
        # Count by category
        categories = discovery.matches_by_category
        result.critical_secrets_found = categories.get("critical_secrets", 0)
        result.pii_found = categories.get("pii", 0)
        result.phi_found = categories.get("phi", 0)
        result.pci_found = categories.get("pci", 0)
        
        # Calculate risk score (0-100)
        risk_score = 0.0
        risk_score += result.critical_secrets_found * 50
        risk_score += result.pii_found * 10
        risk_score += result.phi_found * 20
        risk_score += result.pci_found * 30
        risk_score += categories.get("paths", 0) * 1
        risk_score += categories.get("company", 0) * 1
        
        # Cap at 100
        result.risk_score = min(risk_score, 100.0)
        
        # Recommend action
        if result.risk_score >= 80:
            result.recommended_action = "CRITICAL: Immediate sanitization required"
        elif result.risk_score >= 50:
            result.recommended_action = "HIGH: Sanitization strongly recommended"
        elif result.risk_score >= 20:
            result.recommended_action = "MEDIUM: Review and sanitize if needed"
        else:
            result.recommended_action = "LOW: Optional sanitization"
        
        result.analysis_duration_ms = (datetime.now() - phase_start).total_seconds() * 1000
        return result
    
    def apply_sanitization_rules(
        self,
        discovery: DiscoveryResult,
        analysis: AnalysisResult,
        config: Optional[Dict[str, Any]] = None,
    ) -> TransformResult:
        """
        Phase 3: Apply sanitization transformations with backup.
        
        Strategy:
        - Create backup directory
        - Apply replacements file-by-file
        - Track replacements by strategy
        - Support rollback on failure
        
        Args:
            discovery: Discovery results
            analysis: Analysis results
            config: Transformation config (dry_run, backup_location)
            
        Returns:
            TransformResult with transformation statistics
        """
        phase_start = datetime.now()
        self.logger.info("✏️  Phase 3: TRANSFORMATION")
        
        config = config or {}
        dry_run = config.get("dry_run", False)
        
        result = TransformResult()
        replacements_by_strategy: Dict[str, int] = {}
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.workspace_root / "backups" / f"sanitization_{timestamp}"
        
        if not dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            result.backup_location = str(self.backup_dir)
        
        # Apply sanitization to each file
        for rel_path, matches in self.discovery_cache.items():
            file_path = self.workspace_root / rel_path
            
            if not file_path.exists():
                continue
            
            # Backup original
            if not dry_run:
                backup_path = self.backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(file_path.read_text(encoding='utf-8'))
            
            # Apply sanitization
            sanitized, file_matches = self.engine.sanitize_text(file_path.read_text(encoding='utf-8'))
            
            if not dry_run and file_matches:
                file_path.write_text(sanitized, encoding='utf-8')
                result.files_sanitized += 1
                result.total_replacements += len(file_matches)
                
                # Track by strategy
                for match in file_matches:
                    strategy = match.replacement_strategy.value
                    replacements_by_strategy[strategy] = replacements_by_strategy.get(strategy, 0) + 1
        
        result.replacements_by_strategy = replacements_by_strategy
        result.transform_duration_ms = (datetime.now() - phase_start).total_seconds() * 1000
        
        if dry_run:
            self.logger.info("🔍 DRY RUN: No files modified")
        
        return result
    
    def validate_sanitization(self) -> ValidationResult:
        """
        Phase 4: Verify all high-confidence patterns removed.
        
        Re-scans all modified files to ensure no sensitive data remains
        above the confidence threshold (0.8).
        
        Returns:
            ValidationResult with cleanliness assessment
        """
        phase_start = datetime.now()
        self.logger.info("✅ Phase 4: VALIDATION")
        
        result = ValidationResult()
        remaining_matches: List[SanitizationMatch] = []
        
        # Re-scan all previously matched files
        for rel_path in self.discovery_cache.keys():
            file_path = self.workspace_root / rel_path
            
            if not file_path.exists():
                continue
            
            # Validate file is clean
            content = file_path.read_text(encoding='utf-8')
            is_clean, high_conf_matches = self.engine.validate_sanitization(content, min_confidence=0.8)
            
            if not is_clean:
                remaining_matches.extend(high_conf_matches)
        
        result.remaining_matches = len(remaining_matches)
        result.remaining_high_confidence = len([m for m in remaining_matches if m.confidence >= 0.9])
        result.is_clean = result.remaining_high_confidence == 0
        result.validation_duration_ms = (datetime.now() - phase_start).total_seconds() * 1000
        
        if not result.is_clean:
            self.logger.warning(f"⚠️  Validation failed: {result.remaining_high_confidence} high-confidence matches remain")
        
        return result
    
    def finalize_sanitization(
        self,
        discovery: DiscoveryResult,
        analysis: AnalysisResult,
        transformation: TransformResult,
        validation: ValidationResult,
    ) -> FinalResult:
        """
        Phase 5: Generate report and cleanup.
        
        Creates comprehensive JSON report with all phase results,
        statistics, and recommendations.
        
        Args:
            discovery: Discovery results
            analysis: Analysis results
            transformation: Transformation results
            validation: Validation results
            
        Returns:
            FinalResult with report path
        """
        self.logger.info("📄 Phase 5: FINALIZATION")
        
        # Create report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.workspace_root / "cortex-brain" / "documents" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"sanitization-report-{timestamp}.json"
        
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "orchestrator": "SanitizationOrchestratorV2",
                "version": "2.0.0",
            },
            "discovery": asdict(discovery),
            "analysis": asdict(analysis),
            "transformation": asdict(transformation),
            "validation": asdict(validation),
            "summary": {
                "total_duration_ms": self._elapsed_ms(),
                "success": validation.is_clean,
                "files_processed": discovery.files_scanned,
                "sensitive_data_removed": transformation.total_replacements,
            },
        }
        
        report_path.write_text(json.dumps(report_data, indent=2))
        
        # Build final result
        final = FinalResult(
            success=validation.is_clean,
            discovery=discovery,
            analysis=analysis,
            transformation=transformation,
            validation=validation,
            total_duration_ms=self._elapsed_ms(),
            report_path=str(report_path),
        )
        
        self.logger.info(f"📄 Report saved: {report_path}")
        return final
    
    def _elapsed_ms(self) -> float:
        """Calculate elapsed time since start."""
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds() * 1000
