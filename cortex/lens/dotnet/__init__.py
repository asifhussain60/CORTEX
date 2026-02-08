"""CORTEX LENS: .NET Enterprise Analysis Module."""

from cortex.lens.dotnet.msbuild_resolver import (
    MSBuildProjectReferenceResolver,
    DependencyGraph,
    ProjectNode,
)
from cortex.lens.dotnet.centralized_packages import (
    CentralizedPackageManager,
    CentralizedPackageContext,
)
from cortex.lens.dotnet.enterprise_analysis import (
    DatabaseProjectAnalyzer,
    EntityFrameworkMigrationAnalyzer,
    AzureDevOpsPipelineAnalyzer,
    WCFServiceAnalyzer,
    SolutionArchitectureVisualizer,
    DotNetRepositoryOnboardingIntegration,
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
