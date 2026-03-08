"""Tests for GoldenTestGenerator, TestPriorityClassifier, RepoFrameworkDetector (CAPE 136-e).

TDD RED phase — imports fail until implementation exists.
"""
import os
import tempfile

import pytest

from cortex.orchestrators.core.golden_test_generator import GoldenTestGenerator
from cortex.orchestrators.core.test_priority_classifier import (
    TestPriorityClassifier,
    PriorityResult,
)
from cortex.orchestrators.core.repo_framework_detector import (
    RepoFrameworkDetector,
    FrameworkDetectionResult,
)


# ---------------------------------------------------------------------------
# GoldenTestGenerator
# ---------------------------------------------------------------------------

class TestGoldenTestGenerator:

    @pytest.fixture()
    def generator(self) -> GoldenTestGenerator:
        return GoldenTestGenerator()

    def test_generate_sunshine_minimum_30pct(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan = generator.generate(
            domain="general",
            context="Add user login endpoint",
            rca_failures=0,
            total_tests=10,
        )
        sunshine = [t for t in plan if t["category"] == "sunshine"]
        assert len(sunshine) >= 3  # 30% of 10

    def test_generate_rainy_minimum_20pct(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan = generator.generate(
            domain="general",
            context="Add user login endpoint",
            rca_failures=0,
            total_tests=10,
        )
        rainy = [t for t in plan if t["category"] == "rainy"]
        assert len(rainy) >= 2  # 20% of 10

    def test_generate_edge_minimum_2(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan = generator.generate(
            domain="general",
            context="Add user login endpoint",
            rca_failures=0,
            total_tests=10,
        )
        edge = [t for t in plan if t["category"] == "edge"]
        assert len(edge) >= 2

    def test_generate_7_categories(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan = generator.generate(
            domain="general",
            context="Add user login endpoint",
            rca_failures=0,
            total_tests=20,
        )
        categories = {t["category"] for t in plan}
        assert len(categories) >= 5  # at minimum 5 distinct categories present

    def test_generate_rca_informed(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan_with_failures = generator.generate(
            domain="general",
            context="Payment processing",
            rca_failures=5,
            total_tests=10,
        )
        regression_tests = [t for t in plan_with_failures if t["category"] == "regression"]
        assert len(regression_tests) >= 1

    def test_generate_returns_list_of_dicts(
        self, generator: GoldenTestGenerator
    ) -> None:
        plan = generator.generate(
            domain="general",
            context="Any feature",
            rca_failures=0,
            total_tests=5,
        )
        assert isinstance(plan, list)
        assert all(isinstance(t, dict) for t in plan)
        assert all("category" in t for t in plan)
        assert all("description" in t for t in plan)


# ---------------------------------------------------------------------------
# TestPriorityClassifier
# ---------------------------------------------------------------------------

class TestTestPriorityClassifier:

    @pytest.fixture()
    def classifier(self) -> TestPriorityClassifier:
        return TestPriorityClassifier()

    def test_classify_p0_high_impact(
        self, classifier: TestPriorityClassifier
    ) -> None:
        result: PriorityResult = classifier.classify(
            domain="general",
            impact=3,
            likelihood=3,
            detection_difficulty=1,
        )
        assert result.priority == "P0"

    def test_classify_p3_low_impact(
        self, classifier: TestPriorityClassifier
    ) -> None:
        result: PriorityResult = classifier.classify(
            domain="general",
            impact=0,
            likelihood=0,
            detection_difficulty=0,
        )
        assert result.priority == "P3"

    def test_classify_payment_domain_default_high_impact(
        self, classifier: TestPriorityClassifier
    ) -> None:
        result = classifier.classify(
            domain="payment",
            impact=1,
            likelihood=1,
            detection_difficulty=0,
        )
        # payment domain overrides to at least P1
        assert result.priority in ("P0", "P1")

    def test_classify_auth_domain_default_high_impact(
        self, classifier: TestPriorityClassifier
    ) -> None:
        result = classifier.classify(
            domain="auth",
            impact=1,
            likelihood=1,
            detection_difficulty=0,
        )
        assert result.priority in ("P0", "P1")

    def test_classify_returns_priority_result(
        self, classifier: TestPriorityClassifier
    ) -> None:
        result = classifier.classify(domain="general", impact=2, likelihood=2, detection_difficulty=1)
        assert isinstance(result, PriorityResult)
        assert result.priority in ("P0", "P1", "P2", "P3")
        assert 0.0 <= result.score <= 10.0


# ---------------------------------------------------------------------------
# RepoFrameworkDetector
# ---------------------------------------------------------------------------

class TestRepoFrameworkDetector:

    @pytest.fixture()
    def detector(self) -> RepoFrameworkDetector:
        return RepoFrameworkDetector()

    def test_detect_python_from_requirements_txt(
        self, detector: RepoFrameworkDetector
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            req = os.path.join(tmpdir, "requirements.txt")
            with open(req, "w") as f:
                f.write("pytest\nrequests\n")
            result: FrameworkDetectionResult = detector.detect(repo_root=tmpdir)
            assert result.language == "Python"
            assert "pytest" in result.test_runner.lower()

    def test_detect_node_from_package_json(
        self, detector: RepoFrameworkDetector
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg = os.path.join(tmpdir, "package.json")
            with open(pkg, "w") as f:
                f.write('{"devDependencies": {"jest": "^29.0.0"}}')
            result = detector.detect(repo_root=tmpdir)
            assert result.language in ("Node", "JavaScript", "TypeScript")
            assert "jest" in result.test_runner.lower()

    def test_detect_dotnet_from_csproj(
        self, detector: RepoFrameworkDetector
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj = os.path.join(tmpdir, "MyApp.csproj")
            with open(csproj, "w") as f:
                f.write("<Project Sdk=\"Microsoft.NET.Sdk\" />\n")
            result = detector.detect(repo_root=tmpdir)
            assert result.language == "C#"
            assert result.test_runner in ("xunit", "nunit", "mstest", "dotnet-test")

    def test_detect_unknown_fallback(
        self, detector: RepoFrameworkDetector
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detector.detect(repo_root=tmpdir)
            assert isinstance(result, FrameworkDetectionResult)
            assert result.language == "Unknown"

    def test_detect_returns_framework_detection_result(
        self, detector: RepoFrameworkDetector
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detector.detect(repo_root=tmpdir)
            assert isinstance(result, FrameworkDetectionResult)
            assert hasattr(result, "language")
            assert hasattr(result, "test_runner")
