"""CORTEX LENS: .NET Enterprise Analysis Module."""

from cortex.lens.dotnet.msbuild_resolver import (
    MSBuildProjectReferenceResolver,
    DependencyGraph,
    ProjectNode,
)

__all__ = [
    "MSBuildProjectReferenceResolver",
    "DependencyGraph",
    "ProjectNode",
]
