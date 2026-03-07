"""Tests for Universal Repo Intelligence Engine — phase-132-a (GAP-132-01).

TDD RED → GREEN cycle. Tests must FAIL before implementation, PASS after.

Coverage:
  - OnboardingManifest dataclass
  - All 8 extractor classes (smoke + empty-repo)
  - IntelligenceFacade.analyze_repository() integration

CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_empty_repo(tmp_path: Path) -> Path:
    """Create a minimal empty-repo structure."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def _make_dotnet_repo(tmp_path: Path) -> Path:
    """Create a minimal .NET repo with a .sln file."""
    (tmp_path / ".git").mkdir()
    sln = tmp_path / "MyApp.sln"
    sln.write_text(
        'Project("{FAE04EC0}") = "MyApp.Api", "src\\MyApp.Api\\MyApp.Api.csproj", "{GUID}"\n'
        "EndProject\n"
    )
    src = tmp_path / "src" / "MyApp.Api"
    src.mkdir(parents=True)
    csproj = src / "MyApp.Api.csproj"
    csproj.write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\">\n"
        "  <PropertyGroup>\n"
        "    <TargetFramework>net8.0</TargetFramework>\n"
        "  </PropertyGroup>\n"
        "</Project>\n"
    )
    return tmp_path


def _make_angular_repo(tmp_path: Path) -> Path:
    """Create a minimal Angular repo."""
    (tmp_path / ".git").mkdir()
    src = tmp_path / "src" / "app"
    src.mkdir(parents=True)
    (src / "app.module.ts").write_text(
        "@NgModule({\n  declarations: [AppComponent],\n  imports: [BrowserModule],\n})\nexport class AppModule {}\n"
    )
    (src / "app.component.ts").write_text(
        "@Component({ selector: 'app-root' })\nexport class AppComponent {}\n"
    )
    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# 1. OnboardingManifest
# ─────────────────────────────────────────────────────────────────────────────


class TestOnboardingManifest:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest  # noqa: F401

    def test_instantiates_with_repo_path(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest

        m = OnboardingManifest(repo_path=tmp_path)
        assert m.repo_path == tmp_path

    def test_serializes_to_dict(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest

        m = OnboardingManifest(repo_path=tmp_path)
        d = m.to_dict()
        assert isinstance(d, dict)
        assert "repo_path" in d

    def test_serializes_to_json(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest

        m = OnboardingManifest(repo_path=tmp_path)
        raw = m.to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_has_extractor_results_field(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest

        m = OnboardingManifest(repo_path=tmp_path)
        assert hasattr(m, "extractor_results")
        assert isinstance(m.extractor_results, dict)

    def test_has_summary_field(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest

        m = OnboardingManifest(repo_path=tmp_path)
        assert hasattr(m, "summary")


# ─────────────────────────────────────────────────────────────────────────────
# 2. BaseExtractor ABC
# ─────────────────────────────────────────────────────────────────────────────


class TestBaseExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence import BaseExtractor  # noqa: F401

    def test_is_abstract(self) -> None:
        from cortex.intelligence.repo_intelligence import BaseExtractor
        import inspect

        assert inspect.isabstract(BaseExtractor)

    def test_abstract_method_is_extract(self) -> None:
        from cortex.intelligence.repo_intelligence import BaseExtractor

        assert "extract" in BaseExtractor.__abstractmethods__


# ─────────────────────────────────────────────────────────────────────────────
# 3. SolutionTopologyExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestSolutionTopologyExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.solution_topology_extractor import SolutionTopologyExtractor  # noqa: F401

    def test_extracts_project_names_from_sln(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.solution_topology_extractor import SolutionTopologyExtractor

        repo = _make_dotnet_repo(tmp_path)
        result = SolutionTopologyExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "projects" in result
        assert len(result["projects"]) >= 1

    def test_empty_repo_returns_empty_projects(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.solution_topology_extractor import SolutionTopologyExtractor

        repo = _make_empty_repo(tmp_path)
        result = SolutionTopologyExtractor().extract(repo)
        assert result["projects"] == []


# ─────────────────────────────────────────────────────────────────────────────
# 4. CastleWindsorExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestCastleWindsorExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.castle_windsor_extractor import CastleWindsorExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.castle_windsor_extractor import CastleWindsorExtractor

        repo = _make_empty_repo(tmp_path)
        result = CastleWindsorExtractor().extract(repo)
        assert isinstance(result, dict)
        assert result.get("registrations") == [] or result.get("registrations") is not None

    def test_detects_castle_registrations(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.castle_windsor_extractor import CastleWindsorExtractor

        repo = _make_empty_repo(tmp_path)
        src = repo / "src"
        src.mkdir()
        (src / "Installer.cs").write_text(
            "container.Register(Component.For<IService>().ImplementedBy<Service>());\n"
        )
        result = CastleWindsorExtractor().extract(repo)
        assert result["registrations_found"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 5. NHibernateExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestNHibernateExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.nhibernate_extractor import NHibernateExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.nhibernate_extractor import NHibernateExtractor

        repo = _make_empty_repo(tmp_path)
        result = NHibernateExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "mappings" in result
        assert result["mappings"] == []

    def test_detects_hbm_mapping_files(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.nhibernate_extractor import NHibernateExtractor

        repo = _make_empty_repo(tmp_path)
        maps = repo / "Mappings"
        maps.mkdir()
        (maps / "Order.hbm.xml").write_text('<hibernate-mapping><class name="Order"/></hibernate-mapping>')
        result = NHibernateExtractor().extract(repo)
        assert len(result["mappings"]) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 6. NServiceBusExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestNServiceBusExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.nservicebus_extractor import NServiceBusExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.nservicebus_extractor import NServiceBusExtractor

        repo = _make_empty_repo(tmp_path)
        result = NServiceBusExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "handlers" in result
        assert result["handlers"] == []

    def test_detects_ihandleof_pattern(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.nservicebus_extractor import NServiceBusExtractor

        repo = _make_empty_repo(tmp_path)
        src = repo / "Handlers"
        src.mkdir()
        (src / "OrderHandler.cs").write_text(
            "public class OrderHandler : IHandleMessages<OrderPlaced> { }\n"
        )
        result = NServiceBusExtractor().extract(repo)
        assert result["handlers_found"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 7. AngularExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestAngularExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor

        repo = _make_empty_repo(tmp_path)
        result = AngularExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "modules" in result
        assert result["modules"] == []

    def test_detects_ngmodule(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor

        repo = _make_angular_repo(tmp_path)
        result = AngularExtractor().extract(repo)
        assert result["modules_found"] >= 1

    def test_detects_components(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor

        repo = _make_angular_repo(tmp_path)
        result = AngularExtractor().extract(repo)
        assert result["components_found"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 8. AspNetRouteExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestAspNetRouteExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.aspnet_route_extractor import AspNetRouteExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.aspnet_route_extractor import AspNetRouteExtractor

        repo = _make_empty_repo(tmp_path)
        result = AspNetRouteExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "routes" in result
        assert result["routes"] == []

    def test_detects_http_attributes(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.aspnet_route_extractor import AspNetRouteExtractor

        repo = _make_empty_repo(tmp_path)
        ctrl = repo / "Controllers"
        ctrl.mkdir()
        (ctrl / "OrdersController.cs").write_text(
            "[HttpGet(\"/api/orders\")]\npublic IActionResult GetOrders() { return Ok(); }\n"
        )
        result = AspNetRouteExtractor().extract(repo)
        assert result["routes_found"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 9. BoundedContextExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestBoundedContextExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.bounded_context_extractor import BoundedContextExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.bounded_context_extractor import BoundedContextExtractor

        repo = _make_empty_repo(tmp_path)
        result = BoundedContextExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "contexts" in result
        assert result["contexts"] == []

    def test_detects_domain_folders_as_contexts(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.bounded_context_extractor import BoundedContextExtractor

        repo = _make_empty_repo(tmp_path)
        for domain in ["Ordering", "Shipping", "Billing"]:
            (repo / domain / "Domain").mkdir(parents=True)
        result = BoundedContextExtractor().extract(repo)
        assert result["contexts_found"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 10. TfmClassifierExtractor
# ─────────────────────────────────────────────────────────────────────────────


class TestTfmClassifierExtractor:
    def test_import(self) -> None:
        from cortex.intelligence.repo_intelligence.tfm_classifier_extractor import TfmClassifierExtractor  # noqa: F401

    def test_empty_repo_returns_empty(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.tfm_classifier_extractor import TfmClassifierExtractor

        repo = _make_empty_repo(tmp_path)
        result = TfmClassifierExtractor().extract(repo)
        assert isinstance(result, dict)
        assert "frameworks" in result
        assert result["frameworks"] == []

    def test_detects_target_framework(self, tmp_path: Path) -> None:
        from cortex.intelligence.repo_intelligence.tfm_classifier_extractor import TfmClassifierExtractor

        repo = _make_dotnet_repo(tmp_path)
        result = TfmClassifierExtractor().extract(repo)
        assert "net8.0" in result["frameworks"]


# ─────────────────────────────────────────────────────────────────────────────
# 11. Package __init__ exports
# ─────────────────────────────────────────────────────────────────────────────


class TestRepoIntelligencePackage:
    def test_package_importable(self) -> None:
        import cortex.intelligence.repo_intelligence  # noqa: F401

    def test_all_extractors_in_package(self) -> None:
        from cortex.intelligence.repo_intelligence import (
            SolutionTopologyExtractor,
            CastleWindsorExtractor,
            NHibernateExtractor,
            NServiceBusExtractor,
            AngularExtractor,
            AspNetRouteExtractor,
            BoundedContextExtractor,
            TfmClassifierExtractor,
        )
        for cls in [
            SolutionTopologyExtractor, CastleWindsorExtractor, NHibernateExtractor,
            NServiceBusExtractor, AngularExtractor, AspNetRouteExtractor,
            BoundedContextExtractor, TfmClassifierExtractor,
        ]:
            assert cls is not None

    def test_onboarding_manifest_in_package(self) -> None:
        from cortex.intelligence.repo_intelligence import OnboardingManifest  # noqa: F401


# ─────────────────────────────────────────────────────────────────────────────
# 12. IntelligenceFacade.analyze_repository
# ─────────────────────────────────────────────────────────────────────────────


class TestFacadeAnalyzeRepository:
    def test_facade_has_analyze_repository(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade

        assert hasattr(IntelligenceFacade, "analyze_repository")

    def test_analyze_repository_returns_dict(self, tmp_path: Path) -> None:
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        result = facade.analyze_repository(tmp_path)
        assert isinstance(result, dict)

    def test_analyze_repository_has_extractor_results(self, tmp_path: Path) -> None:
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        result = facade.analyze_repository(tmp_path)
        assert "extractor_results" in result

    def test_analyze_repository_has_summary(self, tmp_path: Path) -> None:
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        result = facade.analyze_repository(tmp_path)
        assert "summary" in result

    def test_analyze_repository_dotnet_repo(self, tmp_path: Path) -> None:
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        repo = _make_dotnet_repo(tmp_path)
        result = facade.analyze_repository(repo)
        topo = result["extractor_results"].get("solution_topology", {})
        assert len(topo.get("projects", [])) >= 1
