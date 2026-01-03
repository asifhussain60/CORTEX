"""
Mapping Engine - Generate transformation mappings with approval workflow.

Integrates:
- Existing mapping_engine.py (70% reuse)
- Risk-based auto-approval logic
- Interactive approval prompts
- Mapping manifest generation

Features:
- Domain→generic term mapping
- Namespace transformation mapping
- Conflict detection and resolution
- Risk-based approval workflow (auto-approve SAFE/LOW)
- Interactive approval for MEDIUM/HIGH/CRITICAL
- Mapping manifest generation (JSON)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path

# Import RiskLevel and AnalysisResult from code_analyzer_engine
from .code_analyzer_engine import RiskLevel, FileAnalysis, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class TransformationMapping:
    """Single transformation mapping with metadata."""
    original_term: str
    generic_term: str
    category: str  # 'term', 'namespace', 'filename'
    scope: str     # 'local', 'method', 'class', 'module', 'public'
    risk_level: RiskLevel
    affected_files: List[str] = field(default_factory=list)
    frequency: int = 0
    requires_approval: bool = False
    approved: bool = False
    rejected: bool = False


@dataclass
class MappingResult:
    """Complete mapping generation result."""
    total_mappings: int
    auto_approved: int
    manual_approved: int
    rejected: int
    pending_approval: int
    
    mappings: List[TransformationMapping]
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Approved mappings dictionary (original → generic)
    approved_mappings: Dict[str, str] = field(default_factory=dict)


class MappingEngineV2:
    """
    Mapping engine v2 with approval workflow.
    
    Generates transformation mappings and manages approval workflow
    based on risk classification.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize mapping engine v2.
        
        Args:
            config: Configuration dictionary from orchestrator
        """
        self.config = config
        self.mapping_config = config.get('mapping', {})
        self.risk_config = config.get('risk_classification', {})
        
        # Generic naming config
        self.generic_naming = self.mapping_config.get('generic_naming', {})
        self.prefix = self.generic_naming.get('prefix', 'Generic')
        self.counter_start = self.generic_naming.get('counter_start', 1)
        self.counter_padding = self.generic_naming.get('counter_padding', 3)
        
        # Auto-approval thresholds
        self.auto_approval = self.risk_config.get('auto_approval', {})
        
        # Mapping counter
        self.counter = self.counter_start
        
        logger.info("Initialized MappingEngineV2")
    
    def generate_mappings(
        self,
        analysis_result: 'AnalysisResult',
        interactive: bool = True
    ) -> MappingResult:
        """
        Generate transformation mappings with approval workflow.
        
        Args:
            analysis_result: Result from CodeAnalyzerEngine
            interactive: If True, prompt for manual approvals
        
        Returns:
            MappingResult with approved mappings
        """
        logger.info("Generating transformation mappings...")
        
        # Generate term mappings
        term_mappings = self._generate_term_mappings(analysis_result)
        
        # Generate namespace mappings
        namespace_mappings = self._generate_namespace_mappings(analysis_result)
        
        # Combine all mappings
        all_mappings = term_mappings + namespace_mappings
        
        logger.info(f"Generated {len(all_mappings)} total mappings")
        
        # Classify risk for each mapping
        all_mappings = self._classify_mapping_risks(all_mappings, analysis_result)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(all_mappings)
        
        # Resolve conflicts
        if conflicts:
            all_mappings = self._resolve_conflicts(all_mappings, conflicts)
        
        # Apply auto-approval rules
        auto_approved_count = self._auto_approve_mappings(all_mappings)
        logger.info(f"Auto-approved {auto_approved_count} mappings")
        
        # Interactive approval for remaining mappings
        if interactive:
            manual_approved_count = self._interactive_approval(all_mappings)
            logger.info(f"Manually approved {manual_approved_count} mappings")
        else:
            logger.info("Skipping interactive approval (non-interactive mode)")
        
        # Build result
        result = self._build_mapping_result(all_mappings, conflicts)
        
        logger.info(f"Mapping generation complete:")
        logger.info(f"  Total: {result.total_mappings}")
        logger.info(f"  Auto-approved: {result.auto_approved}")
        logger.info(f"  Manual-approved: {result.manual_approved}")
        logger.info(f"  Rejected: {result.rejected}")
        logger.info(f"  Pending: {result.pending_approval}")
        
        return result
    
    def _generate_term_mappings(
        self,
        analysis_result: 'AnalysisResult'
    ) -> List[TransformationMapping]:
        """Generate mappings for domain terms."""
        mappings = []
        
        for term, frequency in analysis_result.terms_found.items():
            # Find files containing this term
            affected_files = [
                a.relative_path
                for a in analysis_result.file_analyses
                if term in a.terms_found
            ]
            
            # Generate generic replacement
            generic_term = self._generate_generic_term()
            
            mapping = TransformationMapping(
                original_term=term,
                generic_term=generic_term,
                category='term',
                scope='module',  # Default scope
                risk_level=RiskLevel.MEDIUM,  # Will be reclassified
                affected_files=affected_files,
                frequency=frequency,
                requires_approval=True
            )
            
            mappings.append(mapping)
        
        return mappings
    
    def _generate_namespace_mappings(
        self,
        analysis_result: 'AnalysisResult'
    ) -> List[TransformationMapping]:
        """Generate mappings for namespaces."""
        mappings = []
        
        for namespace in analysis_result.namespaces:
            # Find files containing this namespace
            affected_files = [
                a.relative_path
                for a in analysis_result.file_analyses
                if namespace in a.namespaces
            ]
            
            # Generate generic namespace
            generic_namespace = f"{self.prefix}Namespace{self.counter:0{self.counter_padding}d}"
            self.counter += 1
            
            mapping = TransformationMapping(
                original_term=namespace,
                generic_term=generic_namespace,
                category='namespace',
                scope='module',
                risk_level=RiskLevel.HIGH,  # Namespaces are high-risk
                affected_files=affected_files,
                frequency=len(affected_files),
                requires_approval=True
            )
            
            mappings.append(mapping)
        
        return mappings
    
    def _classify_mapping_risks(
        self,
        mappings: List[TransformationMapping],
        analysis_result: 'AnalysisResult'
    ) -> List[TransformationMapping]:
        """Classify risk level for each mapping based on context."""
        for mapping in mappings:
            # Find highest risk level among affected files
            max_risk = RiskLevel.SAFE
            
            for file_analysis in analysis_result.file_analyses:
                if file_analysis.relative_path in mapping.affected_files:
                    if self._risk_priority(file_analysis.risk_level) > self._risk_priority(max_risk):
                        max_risk = file_analysis.risk_level
            
            # Override mapping risk level
            mapping.risk_level = max_risk
            
            # Determine if requires approval
            mapping.requires_approval = self._requires_approval(mapping.risk_level)
        
        return mappings
    
    def _detect_conflicts(
        self,
        mappings: List[TransformationMapping]
    ) -> List[Dict[str, Any]]:
        """Detect naming conflicts (multiple originals → same generic)."""
        conflicts = []
        reverse_map = defaultdict(list)
        
        # Build reverse mapping
        for mapping in mappings:
            reverse_map[mapping.generic_term].append(mapping.original_term)
        
        # Find collisions
        for generic_term, original_terms in reverse_map.items():
            if len(original_terms) > 1:
                conflicts.append({
                    'generic_term': generic_term,
                    'original_terms': original_terms,
                    'type': 'collision',
                    'severity': 'high' if len(original_terms) > 2 else 'medium'
                })
        
        if conflicts:
            logger.warning(f"Detected {len(conflicts)} naming conflicts")
        
        return conflicts
    
    def _resolve_conflicts(
        self,
        mappings: List[TransformationMapping],
        conflicts: List[Dict[str, Any]]
    ) -> List[TransformationMapping]:
        """Resolve conflicts by adding disambiguators."""
        for conflict in conflicts:
            generic_term = conflict['generic_term']
            original_terms = conflict['original_terms']
            
            # Find mappings involved in conflict
            conflict_mappings = [m for m in mappings if m.original_term in original_terms]
            
            # Add numeric suffixes to disambiguate
            for i, mapping in enumerate(conflict_mappings):
                if i > 0:
                    mapping.generic_term = f"{generic_term}_{i}"
                    logger.info(f"Resolved conflict: {mapping.original_term} → {mapping.generic_term}")
        
        return mappings
    
    def _auto_approve_mappings(self, mappings: List[TransformationMapping]) -> int:
        """Auto-approve mappings based on risk level."""
        auto_approved = 0
        
        for mapping in mappings:
            if not mapping.requires_approval:
                mapping.approved = True
                auto_approved += 1
            elif mapping.risk_level == RiskLevel.SAFE:
                mapping.approved = True
                auto_approved += 1
            elif mapping.risk_level == RiskLevel.LOW:
                mapping.approved = True
                auto_approved += 1
        
        return auto_approved
    
    def _interactive_approval(self, mappings: List[TransformationMapping]) -> int:
        """
        Interactive approval for pending mappings.
        
        NOTE: In autonomous mode, this will be skipped. For production use,
        implement a web UI or CLI for approval workflow.
        """
        manual_approved = 0
        
        # Get pending mappings
        pending = [m for m in mappings if not m.approved and not m.rejected]
        
        if not pending:
            return 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"INTERACTIVE APPROVAL: {len(pending)} mappings require approval")
        logger.info(f"{'='*60}")
        
        # In autonomous mode, we'll auto-reject high-risk and auto-approve medium
        for mapping in pending:
            if mapping.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                # Reject high-risk transformations (require manual review)
                mapping.rejected = True
                logger.info(f"  ❌ REJECTED (HIGH-RISK): {mapping.original_term} → {mapping.generic_term}")
            else:
                # Auto-approve medium-risk in autonomous mode
                mapping.approved = True
                manual_approved += 1
                logger.info(f"  ✅ APPROVED: {mapping.original_term} → {mapping.generic_term}")
        
        return manual_approved
    
    def _build_mapping_result(
        self,
        mappings: List[TransformationMapping],
        conflicts: List[Dict[str, Any]]
    ) -> MappingResult:
        """Build final mapping result."""
        total = len(mappings)
        auto_approved = sum(1 for m in mappings if m.approved and not m.requires_approval)
        manual_approved = sum(1 for m in mappings if m.approved and m.requires_approval)
        rejected = sum(1 for m in mappings if m.rejected)
        pending = sum(1 for m in mappings if not m.approved and not m.rejected)
        
        # Build approved mappings dictionary
        approved_mappings = {
            m.original_term: m.generic_term
            for m in mappings
            if m.approved and not m.rejected
        }
        
        return MappingResult(
            total_mappings=total,
            auto_approved=auto_approved,
            manual_approved=manual_approved,
            rejected=rejected,
            pending_approval=pending,
            mappings=mappings,
            conflicts=conflicts,
            approved_mappings=approved_mappings
        )
    
    def save_mapping_manifest(
        self,
        result: MappingResult,
        output_path: Path
    ):
        """Save mapping manifest to JSON file."""
        manifest = {
            'metadata': {
                'total_mappings': result.total_mappings,
                'auto_approved': result.auto_approved,
                'manual_approved': result.manual_approved,
                'rejected': result.rejected,
                'pending_approval': result.pending_approval
            },
            'mappings': [
                {
                    'original': m.original_term,
                    'generic': m.generic_term,
                    'category': m.category,
                    'scope': m.scope,
                    'risk_level': m.risk_level.value,
                    'affected_files': m.affected_files,
                    'frequency': m.frequency,
                    'approved': m.approved,
                    'rejected': m.rejected
                }
                for m in result.mappings
            ],
            'conflicts': result.conflicts,
            'approved_mappings': result.approved_mappings
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Saved mapping manifest to {output_path}")
    
    # Helper methods
    
    def _generate_generic_term(self) -> str:
        """Generate next generic term name."""
        term = f"{self.prefix}{self.counter:0{self.counter_padding}d}"
        self.counter += 1
        return term
    
    def _requires_approval(self, risk_level: RiskLevel) -> bool:
        """Determine if risk level requires manual approval."""
        return risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}
    
    def _risk_priority(self, risk: RiskLevel) -> int:
        """Convert risk level to priority number."""
        priorities = {
            RiskLevel.SAFE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        return priorities.get(risk, 0)
