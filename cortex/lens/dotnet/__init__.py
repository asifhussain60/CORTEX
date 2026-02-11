"""CORTEX LENS: .NET Enterprise Analysis Module."""

from cortex.lens.dotnet.centralized_packages import (
    CentralizedPackageContext,
    CentralizedPackageManager,
)
from cortex.lens.dotnet.enterprise_analysis import (
    AzureDevOpsPipelineAnalyzer,
    DatabaseProjectAnalyzer,
    DotNetRepositoryOnboardingIntegration,
    EntityFrameworkMigrationAnalyzer,
    SolutionArchitectureVisualizer,
    WCFServiceAnalyzer,
)
from cortex.lens.dotnet.msbuild_resolver import (
    DependencyGraph,
    MSBuildProjectReferenceResolver,
    ProjectNode,
)

__all__ = [
    "MSBuildProjectReferenceResolver",
    "DependencyGraph",
    "ProjectNode",
    "CentralizedPackageManager",
    "CentralizedPackageContext",
    "DatabaseProjectAnalyzer",
    "EntityFrameworkMigrationAnalyzer",
    "AzureDevOpsPipelineAnalyzer",
    "WCFServiceAnalyzer",
    "SolutionArchitectureVisualizer",
    "DotNetRepositoryOnboardingIntegration",
]
