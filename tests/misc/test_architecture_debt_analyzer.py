"""
Tests for ArchitectureDebtAnalyzer.

Tests architectural quality analysis and debt detection.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path

from src.operations.modules.analysis.architecture_debt_analyzer import (
    ArchitectureDebtAnalyzer,
    ArchitectureViolation
)
from src.operations.modules.analysis.ast_engine import ASTEngine


class TestArchitectureDebtAnalyzer:
    """Test suite for ArchitectureDebtAnalyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.ast_engine = ASTEngine(self.project_root)
        self.analyzer = ArchitectureDebtAnalyzer(self.ast_engine)
        
    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.ast_engine is not None
        assert len(self.analyzer.layer_hierarchy) == 4
        assert 'presentation' in self.analyzer.layer_hierarchy
        
    def test_layer_hierarchy_order(self):
        """Test layer hierarchy is correctly ordered."""
        expected = ["presentation", "application", "domain", "infrastructure"]
        assert self.analyzer.layer_hierarchy == expected
        
    def test_analyze_empty_project(self):
        """Test analysis on project with no violations."""
        result = self.analyzer.analyze()
        
        assert 'violations' in result
        assert 'total_violations' in result
        assert 'high_severity_count' in result
        assert 'debt_score' in result
        assert 'recommended_actions' in result
        
    def test_identify_layer_presentation(self):
        """Test identifying presentation layer."""
        assert self.analyzer._identify_layer('src/api/controller.py') == 'presentation'
        assert self.analyzer._identify_layer('src/ui/views.py') == 'presentation'
        
    def test_identify_layer_application(self):
        """Test identifying application layer."""
        assert self.analyzer._identify_layer('src/orchestration/workflow.py') == 'application'
        assert self.analyzer._identify_layer('src/service/auth.py') == 'application'
        
    def test_identify_layer_domain(self):
        """Test identifying domain layer."""
        assert self.analyzer._identify_layer('src/domain/user.py') == 'domain'
        assert self.analyzer._identify_layer('src/model/order.py') == 'domain'
        
    def test_identify_layer_infrastructure(self):
        """Test identifying infrastructure layer."""
        assert self.analyzer._identify_layer('src/repository/user_repo.py') == 'infrastructure'
        assert self.analyzer._identify_layer('src/dao/order_dao.py') == 'infrastructure'
        assert self.analyzer._identify_layer('src/db/connection.py') == 'infrastructure'
        
    def test_detect_layer_violations(self):
        """Test layer violation detection."""
        module_graph = [
            {'from': 'infrastructure/db.py', 'to': 'presentation/api.py'},  # Violation
            {'from': 'application/service.py', 'to': 'domain/model.py'}  # OK
        ]
        
        violations = self.analyzer._detect_layer_violations(module_graph)
        
        assert len(violations) == 1
        assert violations[0].violation_type == 'layer_violation'
        assert violations[0].severity == 'high'
        
    def test_detect_circular_dependencies(self):
        """Test circular dependency detection."""
        circular_deps = [
            ['module_a', 'module_b', 'module_c'],
            ['module_x', 'module_y']
        ]
        
        violations = self.analyzer._detect_circular_dependencies(circular_deps)
        
        assert len(violations) == 2
        for v in violations:
            assert v.violation_type == 'circular_dependency'
            assert v.severity == 'high'
            
    def test_detect_tight_coupling(self):
        """Test tight coupling detection."""
        module_graph = [
            {'to': 'popular_module'} for _ in range(15)
        ]
        
        violations = self.analyzer._detect_tight_coupling(module_graph)
        
        assert len(violations) == 1
        assert violations[0].violation_type == 'tight_coupling'
        assert violations[0].severity == 'medium'
        assert '15 incoming dependencies' in violations[0].description
        
    def test_calculate_debt_score_no_violations(self):
        """Test debt score calculation with no violations."""
        score = self.analyzer._calculate_debt_score([])
        
        assert score == 0.0
        
    def test_calculate_debt_score_with_violations(self):
        """Test debt score calculation with violations."""
        violations = [
            ArchitectureViolation('layer_violation', 'high', 'desc', [], 'rec'),
            ArchitectureViolation('circular_dependency', 'high', 'desc', [], 'rec'),
            ArchitectureViolation('tight_coupling', 'medium', 'desc', [], 'rec')
        ]
        
        score = self.analyzer._calculate_debt_score(violations)
        
        # (3+3+2) / 30 * 100 = 26.67
        assert score > 25 and score < 30
        
    def test_calculate_debt_score_cap(self):
        """Test debt score is capped at 100."""
        violations = [
            ArchitectureViolation('layer_violation', 'high', 'desc', [], 'rec')
            for _ in range(20)
        ]
        
        score = self.analyzer._calculate_debt_score(violations)
        
        assert score == 100.0
        
    def test_prioritize_actions(self):
        """Test action prioritization."""
        violations = [
            ArchitectureViolation('type1', 'low', 'desc', [], 'low_priority'),
            ArchitectureViolation('type2', 'high', 'desc', [], 'high_priority'),
            ArchitectureViolation('type3', 'medium', 'desc', [], 'medium_priority')
        ]
        
        actions = self.analyzer._prioritize_actions(violations)
        
        # Should be sorted by severity
        assert actions[0] == 'high_priority'
        assert actions[1] == 'medium_priority'
        assert actions[2] == 'low_priority'
        
    def test_prioritize_actions_limited(self):
        """Test action prioritization limits to top 5."""
        violations = [
            ArchitectureViolation('type', 'high', 'desc', [], f'rec{i}')
            for i in range(10)
        ]
        
        actions = self.analyzer._prioritize_actions(violations)
        
        assert len(actions) == 5


class TestArchitectureViolation:
    """Test suite for ArchitectureViolation dataclass."""
    
    def test_creation(self):
        """Test ArchitectureViolation creation."""
        violation = ArchitectureViolation(
            violation_type='layer_violation',
            severity='high',
            description='Infrastructure depends on presentation',
            affected_modules=['db.py', 'api.py'],
            recommendation='Introduce abstraction layer'
        )
        
        assert violation.violation_type == 'layer_violation'
        assert violation.severity == 'high'
        assert len(violation.affected_modules) == 2
        
    def test_severity_types(self):
        """Test different severity levels."""
        high = ArchitectureViolation('type', 'high', 'desc', [], 'rec')
        medium = ArchitectureViolation('type', 'medium', 'desc', [], 'rec')
        low = ArchitectureViolation('type', 'low', 'desc', [], 'rec')
        
        assert high.severity == 'high'
        assert medium.severity == 'medium'
        assert low.severity == 'low'
