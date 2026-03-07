"""cortex.intelligence.repo_intelligence — Universal Repo Intelligence Engine.

Exports all 8 extractors, the BaseExtractor ABC, and the OnboardingManifest
dataclass used by IntelligenceFacade.analyze_repository().

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""

from __future__ import annotations

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor
from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest
from cortex.intelligence.repo_intelligence.solution_topology_extractor import SolutionTopologyExtractor
from cortex.intelligence.repo_intelligence.castle_windsor_extractor import CastleWindsorExtractor
from cortex.intelligence.repo_intelligence.nhibernate_extractor import NHibernateExtractor
from cortex.intelligence.repo_intelligence.nservicebus_extractor import NServiceBusExtractor
from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor
from cortex.intelligence.repo_intelligence.aspnet_route_extractor import AspNetRouteExtractor
from cortex.intelligence.repo_intelligence.bounded_context_extractor import BoundedContextExtractor
from cortex.intelligence.repo_intelligence.tfm_classifier_extractor import TfmClassifierExtractor
from cortex.intelligence.repo_intelligence.universal_repo_intelligence_engine import (
    UniversalRepoIntelligenceEngine,
)

__all__ = [
    "BaseExtractor",
    "OnboardingManifest",
    "SolutionTopologyExtractor",
    "CastleWindsorExtractor",
    "NHibernateExtractor",
    "NServiceBusExtractor",
    "AngularExtractor",
    "AspNetRouteExtractor",
    "BoundedContextExtractor",
    "TfmClassifierExtractor",
    "UniversalRepoIntelligenceEngine",
]
