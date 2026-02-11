"""
Tests for Extended Analysis Domain Strategy.

Tests all analysis capabilities (code quality, performance, security) and
integration with unified domain orchestration framework.

AC_START: AC-WAVE7T2-2C-TEST-001
Tests: 18 total (code quality: 5, performance: 5, security: 5, integration: 3)
"""

import pytest
from cortex.orchestrators.unified_analysis_strategy_extended import (
    ExtendedAnalysisDomainStrategy,
    CodeQualityAnalyzer,
    PerformanceAnalyzer,
    SecurityAnalyzer,
    AnalysisRequest,
    AnalysisType,
    Severity,
)


class TestCodeQualityAnalyzer:
    """Tests for code quality analyzer."""

    def test_analyzer_initialization(self):
        """Test initialization."""
        analyzer = CodeQualityAnalyzer()
        assert analyzer is not None
        assert len(analyzer.supported_operations) > 0

    def test_get_supported_operations(self):
        """Test supported operations."""
        analyzer = CodeQualityAnalyzer()
        ops = analyzer.get_supported_operations()
        assert "analyze_code_quality" in ops
        assert "get_quality_metrics" in ops

    def test_analyze_code_quality(self):
        """Test code quality analysis."""
        analyzer = CodeQualityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_QUALITY,
            target_path="/path/to/module.py"
        )
        result = analyzer.analyze_code_quality(request)
        assert result.analysis_type == AnalysisType.CODE_QUALITY
        assert len(result.findings) > 0
        assert len(result.metrics) > 0

    def test_get_quality_metrics(self):
        """Test getting quality metrics."""
        analyzer = CodeQualityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_QUALITY,
            target_path="/path/to/module.py"
        )
        result = analyzer.get_quality_metrics(request)
        assert result.status == "success"
        assert len(result.metrics) > 0

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        analyzer = CodeQualityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_QUALITY,
            target_path="/path/to/module.py"
        )
        result = analyzer.calculate_quality_score(request)
        assert len(result.metrics) > 0
        assert any(m.name == "overall_quality_score" for m in result.metrics)


class TestPerformanceAnalyzer:
    """Tests for performance analyzer."""

    def test_analyzer_initialization(self):
        """Test initialization."""
        analyzer = PerformanceAnalyzer()
        assert analyzer is not None
        assert len(analyzer.supported_operations) > 0

    def test_get_supported_operations(self):
        """Test supported operations."""
        analyzer = PerformanceAnalyzer()
        ops = analyzer.get_supported_operations()
        assert "analyze_performance" in ops
        assert "detect_bottlenecks" in ops

    def test_analyze_performance(self):
        """Test performance analysis."""
        analyzer = PerformanceAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.PERFORMANCE,
            target_path="/path/to/module.py"
        )
        result = analyzer.analyze_performance(request)
        assert result.analysis_type == AnalysisType.PERFORMANCE
        assert len(result.findings) > 0
        assert len(result.metrics) > 0

    def test_profile_execution(self):
        """Test execution profiling."""
        analyzer = PerformanceAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.PERFORMANCE,
            target_path="/path/to/module.py"
        )
        result = analyzer.profile_execution(request)
        assert result.status == "success"
        assert len(result.metrics) > 0

    def test_detect_bottlenecks(self):
        """Test bottleneck detection."""
        analyzer = PerformanceAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.PERFORMANCE,
            target_path="/path/to/module.py"
        )
        result = analyzer.detect_bottlenecks(request)
        assert len(result.findings) > 0
        assert any(f.severity == Severity.CRITICAL for f in result.findings)


class TestSecurityAnalyzer:
    """Tests for security analyzer."""

    def test_analyzer_initialization(self):
        """Test initialization."""
        analyzer = SecurityAnalyzer()
        assert analyzer is not None
        assert len(analyzer.supported_operations) > 0

    def test_get_supported_operations(self):
        """Test supported operations."""
        analyzer = SecurityAnalyzer()
        ops = analyzer.get_supported_operations()
        assert "analyze_security" in ops
        assert "scan_vulnerabilities" in ops

    def test_analyze_security(self):
        """Test security analysis."""
        analyzer = SecurityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.SECURITY,
            target_path="/path/to/module.py"
        )
        result = analyzer.analyze_security(request)
        assert result.analysis_type == AnalysisType.SECURITY
        assert len(result.findings) > 0
        assert len(result.metrics) > 0

    def test_scan_vulnerabilities(self):
        """Test vulnerability scanning."""
        analyzer = SecurityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.VULNERABILITY,
            target_path="/path/to/module.py"
        )
        result = analyzer.scan_vulnerabilities(request)
        assert result.analysis_type == AnalysisType.VULNERABILITY
        assert len(result.findings) > 0

    def test_check_compliance(self):
        """Test compliance checking."""
        analyzer = SecurityAnalyzer()
        request = AnalysisRequest(
            analysis_type=AnalysisType.COMPLIANCE,
            target_path="/path/to/module.py"
        )
        result = analyzer.check_compliance(request)
        assert result.analysis_type == AnalysisType.COMPLIANCE
        assert len(result.findings) > 0


class TestExtendedAnalysisStrategy:
    """Tests for extended analysis strategy."""

    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = ExtendedAnalysisDomainStrategy()
        assert strategy is not None
        assert strategy.code_quality_analyzer is not None
        assert strategy.performance_analyzer is not None
        assert strategy.security_analyzer is not None

    def test_get_metadata(self):
        """Test metadata retrieval."""
        strategy = ExtendedAnalysisDomainStrategy()
        metadata = strategy.get_metadata()
        assert metadata["name"] == "ExtendedAnalysisDomainStrategy"
        assert "code_quality" in metadata["analyzers"]

    def test_has_analyzers(self):
        """Test analyzer presence."""
        strategy = ExtendedAnalysisDomainStrategy()
        assert hasattr(strategy, "code_quality_analyzer")
        assert hasattr(strategy, "performance_analyzer")
        assert hasattr(strategy, "security_analyzer")

    def test_analyze_code_quality_route(self):
        """Test routing to code quality analyzer."""
        strategy = ExtendedAnalysisDomainStrategy()
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_QUALITY,
            target_path="/path/to/module.py"
        )
        result = strategy.analyze(request)
        assert result.analysis_type == AnalysisType.CODE_QUALITY
        assert len(result.findings) > 0

    def test_analyze_performance_route(self):
        """Test routing to performance analyzer."""
        strategy = ExtendedAnalysisDomainStrategy()
        request = AnalysisRequest(
            analysis_type=AnalysisType.PERFORMANCE,
            target_path="/path/to/module.py"
        )
        result = strategy.analyze(request)
        assert result.analysis_type == AnalysisType.PERFORMANCE
        assert len(result.findings) > 0

    def test_analyze_security_route(self):
        """Test routing to security analyzer."""
        strategy = ExtendedAnalysisDomainStrategy()
        request = AnalysisRequest(
            analysis_type=AnalysisType.SECURITY,
            target_path="/path/to/module.py"
        )
        result = strategy.analyze(request)
        assert result.analysis_type == AnalysisType.SECURITY
        assert len(result.findings) > 0


class TestAnalysisStrategyIntegration:
    """Integration tests for analysis strategy."""

    def test_all_analysis_types_supported(self):
        """Test all analysis types routed correctly."""
        strategy = ExtendedAnalysisDomainStrategy()
        
        analysis_types = [
            AnalysisType.CODE_QUALITY,
            AnalysisType.PERFORMANCE,
            AnalysisType.SECURITY
        ]
        
        for analysis_type in analysis_types:
            request = AnalysisRequest(
                analysis_type=analysis_type,
                target_path="/path/to/file.py"
            )
            result = strategy.analyze(request)
            assert result.status == "success"
            assert result.analysis_type == analysis_type

    def test_unknown_analysis_type_handling(self):
        """Test handling of unknown analysis type."""
        strategy = ExtendedAnalysisDomainStrategy()
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_DUPLICATION,
            target_path="/path/to/file.py"
        )
        result = strategy.analyze(request)
        assert result.status == "success"

    def test_analysis_request_creation(self):
        """Test analysis request creation."""
        request = AnalysisRequest(
            analysis_type=AnalysisType.CODE_QUALITY,
            target_path="/path/to/file.py",
            language="python"
        )
        assert request.analysis_type == AnalysisType.CODE_QUALITY
        assert request.target_path == "/path/to/file.py"
        assert request.language == "python"


# AC_COMPLETE: AC-WAVE7T2-2C-TEST-001 ✅ 18 test cases for analysis strategy
