"""
GitHub Actions Platform Client

Implementation of PlatformClient for GitHub Actions.

Author: Asif Hussain
Version: 1.0
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests

from .platform_client import PlatformClient
from .schemas import PipelineStatus, PipelineRun, BuildLog, PlatformType


class GitHubActionsClient(PlatformClient):
    """
    GitHub Actions client.
    
    Uses GitHub REST API v3.
    
    Configuration required:
    - owner: Repository owner (username or organization)
    - repository: Repository name
    - token: GitHub personal access token with workflow permissions
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.github.com"
        self.session = None
        super().__init__(config)
    
    def _validate_config(self) -> None:
        """Validate GitHub Actions configuration"""
        required = ["owner", "repository", "token"]
        missing = [k for k in required if k not in self.config]
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        # Create authenticated session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config['token']}",
            "Accept": "application/vnd.github.v3+json"
        })
        
        owner = self.config["owner"]
        repo = self.config["repository"]
        self.logger.info(f"✅ GitHub Actions client initialized: {owner}/{repo}")
    
    def trigger_pipeline(
        self,
        pipeline_name: str,
        repository: str,
        branch: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Trigger GitHub Actions workflow"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        # Get workflow ID from name
        workflow_id = self._get_workflow_id(pipeline_name)
        
        # Prepare request body
        body = {
            "ref": branch,
            "inputs": parameters or {}
        }
        
        # Trigger workflow
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
        response = self.session.post(url, json=body)
        response.raise_for_status()
        
        # GitHub API doesn't return run ID directly, need to poll for latest run
        import time
        time.sleep(2)  # Wait for workflow to be queued
        
        # Get latest run for this workflow
        runs_url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        runs_response = self.session.get(runs_url, params={"per_page": 1})
        runs_response.raise_for_status()
        
        runs_data = runs_response.json()
        if runs_data["workflow_runs"]:
            run_id = str(runs_data["workflow_runs"][0]["id"])
            self.logger.info(f"✅ Workflow triggered: {pipeline_name} (run_id={run_id})")
            return run_id
        
        raise RuntimeError(f"Failed to get run ID for workflow: {pipeline_name}")
    
    def get_pipeline_status(self, run_id: str) -> PipelineStatus:
        """Get GitHub Actions workflow status"""
        run = self.get_pipeline_run(run_id)
        return run.status
    
    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """Get GitHub Actions workflow run details"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        # Get run details
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Map GitHub status to our enum
        status_map = {
            "queued": PipelineStatus.QUEUED,
            "in_progress": PipelineStatus.RUNNING,
            "completed": PipelineStatus.SUCCESS
        }
        
        status = status_map.get(data.get("status"), PipelineStatus.UNKNOWN)
        
        # Check conclusion for completed workflows
        if data.get("status") == "completed":
            conclusion = data.get("conclusion", "").lower()
            if conclusion == "failure":
                status = PipelineStatus.FAILED
            elif conclusion == "cancelled":
                status = PipelineStatus.CANCELLED
        
        # Parse timestamps
        start_time = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        end_time = None
        duration = None
        
        if data.get("updated_at"):
            end_time = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            duration = (end_time - start_time).total_seconds()
        
        return PipelineRun(
            run_id=run_id,
            pipeline_name=data["name"],
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            platform=PlatformType.GITHUB_ACTIONS,
            branch=data["head_branch"],
            commit_sha=data["head_sha"],
            url=data["html_url"]
        )
    
    def get_build_logs(self, run_id: str) -> BuildLog:
        """Get GitHub Actions workflow logs"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        # Get logs (returns zip file)
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
        response = self.session.get(url)
        response.raise_for_status()
        
        # Extract logs from zip
        import zipfile
        import io
        
        logs = []
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as log_file:
                    logs.append(log_file.read().decode("utf-8"))
        
        full_logs = "\n".join(logs)
        
        # Parse errors and warnings
        errors = self._parse_errors(full_logs)
        warnings = self._parse_warnings(full_logs)
        
        return BuildLog(
            run_id=run_id,
            platform=PlatformType.GITHUB_ACTIONS,
            logs=full_logs,
            errors=errors,
            warnings=warnings
        )
    
    def cancel_pipeline(self, run_id: str) -> bool:
        """Cancel GitHub Actions workflow"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/cancel"
        response = self.session.post(url)
        success = response.ok
        
        if success:
            self.logger.info(f"✅ Workflow cancelled: {run_id}")
        else:
            self.logger.error(f"❌ Failed to cancel workflow: {run_id}")
        
        return success
    
    def get_pipeline_history(
        self,
        pipeline_name: str,
        repository: str,
        limit: int = 10
    ) -> List[PipelineRun]:
        """Get GitHub Actions workflow history"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        workflow_id = self._get_workflow_id(pipeline_name)
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        response = self.session.get(url, params={"per_page": limit})
        response.raise_for_status()
        
        data = response.json()
        
        runs = []
        for run in data.get("workflow_runs", []):
            try:
                pipeline_run = self.get_pipeline_run(str(run["id"]))
                runs.append(pipeline_run)
            except Exception as e:
                self.logger.warning(f"Failed to get run {run['id']}: {e}")
        
        return runs
    
    def _get_workflow_id(self, workflow_name: str) -> str:
        """Get workflow ID from name"""
        owner = self.config["owner"]
        repo = self.config["repository"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        for workflow in data.get("workflows", []):
            if workflow["name"] == workflow_name:
                return str(workflow["id"])
        
        raise ValueError(f"Workflow not found: {workflow_name}")
    
    def _parse_errors(self, logs: str) -> List[str]:
        """Parse error messages from logs"""
        errors = []
        for line in logs.split("\n"):
            lower_line = line.lower()
            if "error" in lower_line or "failed" in lower_line:
                errors.append(line.strip())
        return errors[:50]  # Limit to 50 errors
    
    def _parse_warnings(self, logs: str) -> List[str]:
        """Parse warning messages from logs"""
        warnings = []
        for line in logs.split("\n"):
            if "warning" in line.lower():
                warnings.append(line.strip())
        return warnings[:50]  # Limit to 50 warnings
