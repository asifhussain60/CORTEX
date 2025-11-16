"""
Integration modules for Code Review Plugin

Available integrations:
- Azure DevOps: REST API integration for Azure DevOps pull requests
- GitHub: REST API and GraphQL integration for GitHub pull requests
- GitLab: CI webhook integration (coming soon)
- BitBucket: Pipelines integration (coming soon)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .azure_devops_integration import AzureDevOpsIntegration, AzureDevOpsConfig
from .github_integration import GitHubIntegration, GitHubConfig

__all__ = [
    'AzureDevOpsIntegration',
    'AzureDevOpsConfig',
    'GitHubIntegration',
    'GitHubConfig'
]
