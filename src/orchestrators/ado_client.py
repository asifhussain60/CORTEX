"""
Azure DevOps API Client for Code Review

Purpose:
- Fetch Pull Request information from Azure DevOps
- Download PR diffs and changed files
- Extract PR metadata (title, description, work items)
- Handle authentication via Personal Access Token (PAT)

API Documentation:
https://docs.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests

Author: Asif Hussain
Created: 2025-11-26
Version: 1.0 (Phase 2)
"""

import os
import json
import base64
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass, field
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests library not available, ADO integration will be limited")

logger = logging.getLogger(__name__)


@dataclass
class PRMetadata:
    """Pull Request metadata from ADO."""
    pr_id: str
    title: str
    description: str
    author: str
    created_date: datetime
    source_branch: str
    target_branch: str
    status: str
    work_items: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)


@dataclass
class PRDiff:
    """Pull Request diff information."""
    pr_id: str
    changed_files: List[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    file_diffs: Dict[str, str] = field(default_factory=dict)


class ADOClient:
    """
    Azure DevOps API client for Pull Request operations.
    
    Authentication:
    - Uses Personal Access Token (PAT) from config
    - Token stored in cortex.config.json under ado.personal_access_token
    
    Endpoints:
    - GET PR: /git/repositories/{repo}/pullRequests/{prId}
    - GET PR Changes: /git/pullRequests/{prId}/iterations/{iterationId}/changes
    - GET PR Work Items: /git/pullRequests/{prId}/workitems
    """
    
    API_VERSION = "7.0"
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ADO client.
        
        Args:
            config: CORTEX configuration dictionary
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for ADO integration")
        
        self.config = config
        self.ado_config = config.get("ado", {})
        
        # Extract PAT
        self.pat = self.ado_config.get("personal_access_token")
        if not self.pat:
            logger.warning("No ADO PAT found in config (ado.personal_access_token)")
        
        # Setup authentication header
        if self.pat:
            auth_string = f":{self.pat}"
            b64_auth = base64.b64encode(auth_string.encode()).decode()
            self.headers = {
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Content-Type": "application/json"
            }
        
        logger.info("ADOClient initialized")
    
    def parse_pr_url(self, pr_url: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Parse ADO PR URL to extract components.
        
        URL Format:
        https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{prId}
        
        Args:
            pr_url: ADO Pull Request URL
        
        Returns:
            Tuple of (org, project, repo, pr_id) or None if invalid
        """
        try:
            parsed = urlparse(pr_url)
            
            # Check host
            if "dev.azure.com" not in parsed.netloc:
                logger.error(f"Invalid ADO URL (not dev.azure.com): {pr_url}")
                return None
            
            # Parse path
            path_parts = parsed.path.strip('/').split('/')
            
            # Expected format: org/project/_git/repo/pullrequest/prId
            if len(path_parts) < 6:
                logger.error(f"Invalid ADO URL path: {parsed.path}")
                return None
            
            org = path_parts[0]
            project = path_parts[1]
            repo = path_parts[3]
            pr_id = path_parts[5]
            
            logger.info(f"Parsed PR URL: org={org}, project={project}, repo={repo}, pr_id={pr_id}")
            return (org, project, repo, pr_id)
        
        except Exception as e:
            logger.error(f"Failed to parse PR URL: {e}")
            return None
    
    def fetch_pr_metadata(
        self,
        org: str,
        project: str,
        repo: str,
        pr_id: str
    ) -> Optional[PRMetadata]:
        """
        Fetch PR metadata from ADO.
        
        Endpoint:
        GET https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{prId}
        
        Args:
            org: Organization name
            project: Project name
            repo: Repository name
            pr_id: Pull Request ID
        
        Returns:
            PR metadata or None if failed
        """
        if not self.pat:
            logger.error("Cannot fetch PR: No PAT configured")
            return None
        
        url = (
            f"https://dev.azure.com/{org}/{project}/_apis/"
            f"git/repositories/{repo}/pullRequests/{pr_id}"
            f"?api-version={self.API_VERSION}"
        )
        
        try:
            logger.info(f"Fetching PR metadata: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract metadata
            metadata = PRMetadata(
                pr_id=str(data.get("pullRequestId")),
                title=data.get("title", ""),
                description=data.get("description", ""),
                author=data.get("createdBy", {}).get("displayName", ""),
                created_date=datetime.fromisoformat(
                    data.get("creationDate", "").replace('Z', '+00:00')
                ),
                source_branch=data.get("sourceRefName", "").replace("refs/heads/", ""),
                target_branch=data.get("targetRefName", "").replace("refs/heads/", ""),
                status=data.get("status", ""),
                reviewers=[
                    reviewer.get("displayName", "")
                    for reviewer in data.get("reviewers", [])
                ]
            )
            
            logger.info(f"PR metadata fetched: {metadata.title}")
            return metadata
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch PR metadata: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing PR metadata: {e}")
            return None
    
    def fetch_pr_diff(
        self,
        org: str,
        project: str,
        repo: str,
        pr_id: str
    ) -> Optional[PRDiff]:
        """
        Fetch PR diff (changed files) from ADO.
        
        Endpoint:
        GET https://dev.azure.com/{org}/{project}/_apis/git/pullRequests/{prId}/iterations/{iterationId}/changes
        
        Args:
            org: Organization name
            project: Project name
            repo: Repository name
            pr_id: Pull Request ID
        
        Returns:
            PR diff or None if failed
        """
        if not self.pat:
            logger.error("Cannot fetch PR diff: No PAT configured")
            return None
        
        # First get the latest iteration ID
        iteration_id = self._get_latest_iteration(org, project, repo, pr_id)
        if not iteration_id:
            logger.error("Failed to get PR iteration ID")
            return None
        
        url = (
            f"https://dev.azure.com/{org}/{project}/_apis/"
            f"git/pullRequests/{pr_id}/iterations/{iteration_id}/changes"
            f"?api-version={self.API_VERSION}"
        )
        
        try:
            logger.info(f"Fetching PR changes: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract changed files
            changed_files = []
            additions = 0
            deletions = 0
            
            for change in data.get("changeEntries", []):
                item = change.get("item", {})
                path = item.get("path", "").lstrip('/')
                
                if path:
                    changed_files.append(path)
                
                # Count additions/deletions if available
                change_type = change.get("changeType")
                if change_type == "add":
                    additions += 1
                elif change_type == "delete":
                    deletions += 1
            
            diff = PRDiff(
                pr_id=pr_id,
                changed_files=changed_files,
                additions=additions,
                deletions=deletions
            )
            
            logger.info(
                f"PR diff fetched: {len(changed_files)} files, "
                f"+{additions} -{deletions}"
            )
            return diff
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing PR diff: {e}")
            return None
    
    def _get_latest_iteration(
        self,
        org: str,
        project: str,
        repo: str,
        pr_id: str
    ) -> Optional[int]:
        """
        Get latest iteration ID for PR.
        
        Args:
            org: Organization name
            project: Project name
            repo: Repository name
            pr_id: Pull Request ID
        
        Returns:
            Iteration ID or None if failed
        """
        url = (
            f"https://dev.azure.com/{org}/{project}/_apis/"
            f"git/repositories/{repo}/pullRequests/{pr_id}/iterations"
            f"?api-version={self.API_VERSION}"
        )
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            iterations = data.get("value", [])
            
            if iterations:
                # Return the latest iteration ID
                latest = max(iterations, key=lambda x: x.get("id", 0))
                return latest.get("id")
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get iteration ID: {e}")
            return None
    
    def fetch_pr_work_items(
        self,
        org: str,
        project: str,
        pr_id: str
    ) -> List[str]:
        """
        Fetch work items linked to PR.
        
        Endpoint:
        GET https://dev.azure.com/{org}/{project}/_apis/git/pullRequests/{prId}/workitems
        
        Args:
            org: Organization name
            project: Project name
            pr_id: Pull Request ID
        
        Returns:
            List of work item IDs
        """
        if not self.pat:
            logger.warning("Cannot fetch work items: No PAT configured")
            return []
        
        url = (
            f"https://dev.azure.com/{org}/{project}/_apis/"
            f"git/pullRequests/{pr_id}/workitems"
            f"?api-version={self.API_VERSION}"
        )
        
        try:
            logger.info(f"Fetching PR work items: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            work_items = []
            
            for item in data.get("value", []):
                work_item_id = item.get("id")
                if work_item_id:
                    work_items.append(str(work_item_id))
            
            logger.info(f"Fetched {len(work_items)} work items")
            return work_items
        
        except Exception as e:
            logger.error(f"Failed to fetch work items: {e}")
            return []
    
    def fetch_pr_from_url(self, pr_url: str) -> Optional[Tuple[PRMetadata, PRDiff]]:
        """
        Fetch PR metadata and diff from URL.
        
        Convenience method that parses URL and fetches data.
        
        Args:
            pr_url: ADO Pull Request URL
        
        Returns:
            Tuple of (metadata, diff) or None if failed
        """
        # Parse URL
        parsed = self.parse_pr_url(pr_url)
        if not parsed:
            return None
        
        org, project, repo, pr_id = parsed
        
        # Fetch metadata
        metadata = self.fetch_pr_metadata(org, project, repo, pr_id)
        if not metadata:
            return None
        
        # Fetch diff
        diff = self.fetch_pr_diff(org, project, repo, pr_id)
        if not diff:
            return None
        
        # Fetch work items
        work_items = self.fetch_pr_work_items(org, project, pr_id)
        metadata.work_items = work_items
        
        return (metadata, diff)


def main():
    """CLI entry point for testing."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    import os
    from pathlib import Path
    
    cortex_root = os.environ.get('CORTEX_ROOT', os.getcwd())
    config_path = Path(cortex_root) / "cortex.config.json"
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print("Please create cortex.config.json with:")
        print('{')
        print('  "ado": {')
        print('    "personal_access_token": "YOUR_PAT_HERE"')
        print('  }')
        print('}')
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize client
    client = ADOClient(config)
    
    # Test with URL
    if len(sys.argv) > 1:
        pr_url = sys.argv[1]
    else:
        pr_url = "https://dev.azure.com/myorg/myproject/_git/myrepo/pullrequest/1234"
        print(f"Using example URL: {pr_url}")
        print("Provide URL as argument to test with real PR\n")
    
    # Parse URL
    parsed = client.parse_pr_url(pr_url)
    if parsed:
        org, project, repo, pr_id = parsed
        print(f"\nParsed URL:")
        print(f"  Organization: {org}")
        print(f"  Project: {project}")
        print(f"  Repository: {repo}")
        print(f"  PR ID: {pr_id}")
    else:
        print("Failed to parse URL")


if __name__ == "__main__":
    main()
