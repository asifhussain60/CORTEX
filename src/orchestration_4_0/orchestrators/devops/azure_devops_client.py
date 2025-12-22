"""
Azure DevOps Platform Client

Implementation of PlatformClient for Azure DevOps Pipelines.

Author: Asif Hussain
Version: 1.0
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from .platform_client import PlatformClient
from .schemas import PipelineStatus, PipelineRun, BuildLog, PlatformType


class AzureDevOpsClient(PlatformClient):
    """
    Azure DevOps Pipelines client.
    
    Uses Azure DevOps REST API v6.0.
    
    Configuration required:
    - organization: Azure DevOps organization name
    - project: Project name
    - personal_access_token: PAT with pipeline permissions
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.base_url = None
        self.session = None
        super().__init__(config)
    
    def _validate_config(self) -> None:
        """Validate Azure DevOps configuration"""
        required = ["organization", "project", "personal_access_token"]
        missing = [k for k in required if k not in self.config]
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        # Set up base URL and auth
        org = self.config["organization"]
        self.base_url = f"https://dev.azure.com/{org}"
        
        # Create authenticated session
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth("", self.config["personal_access_token"])
        self.session.headers.update({"Content-Type": "application/json"})
        
        self.logger.info(f"✅ Azure DevOps client initialized: {org}")
    
    def trigger_pipeline(
        self,
        pipeline_name: str,
        repository: str,
        branch: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Trigger Azure DevOps pipeline"""
        project = self.config["project"]
        
        # Get pipeline ID from name
        pipeline_id = self._get_pipeline_id(pipeline_name)
        
        # Prepare request body
        body = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": f"refs/heads/{branch}"
                    }
                }
            }
        }
        
        if parameters:
            body["templateParameters"] = parameters
        
        # Trigger pipeline
        url = f"{self.base_url}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0"
        response = self.session.post(url, json=body)
        response.raise_for_status()
        
        data = response.json()
        run_id = str(data["id"])
        
        self.logger.info(f"✅ Pipeline triggered: {pipeline_name} (run_id={run_id})")
        return run_id
    
    def get_pipeline_status(self, run_id: str) -> PipelineStatus:
        """Get Azure DevOps pipeline status"""
        run = self.get_pipeline_run(run_id)
        return run.status
    
    def get_pipeline_run(self, run_id: str) -> PipelineRun:
        """Get Azure DevOps pipeline run details"""
        project = self.config["project"]
        
        # Get run details
        url = f"{self.base_url}/{project}/_apis/pipelines/runs/{run_id}?api-version=6.0"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Map Azure DevOps status to our enum
        status_map = {
            "inProgress": PipelineStatus.RUNNING,
            "completed": PipelineStatus.SUCCESS,
            "cancelling": PipelineStatus.CANCELLED,
            "canceled": PipelineStatus.CANCELLED
        }
        
        status = status_map.get(data.get("state"), PipelineStatus.UNKNOWN)
        
        # Check result for completed pipelines
        if data.get("state") == "completed":
            result = data.get("result", "").lower()
            if result == "failed":
                status = PipelineStatus.FAILED
            elif result == "canceled":
                status = PipelineStatus.CANCELLED
        
        # Parse timestamps
        start_time = datetime.fromisoformat(data["createdDate"].replace("Z", "+00:00"))
        end_time = None
        duration = None
        
        if "finishedDate" in data:
            end_time = datetime.fromisoformat(data["finishedDate"].replace("Z", "+00:00"))
            duration = (end_time - start_time).total_seconds()
        
        return PipelineRun(
            run_id=run_id,
            pipeline_name=data["pipeline"]["name"],
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            platform=PlatformType.AZURE_DEVOPS,
            branch=data["resources"]["repositories"]["self"]["refName"].replace("refs/heads/", ""),
            commit_sha=data["resources"]["repositories"]["self"].get("version"),
            url=data["_links"]["web"]["href"]
        )
    
    def get_build_logs(self, run_id: str) -> BuildLog:
        """Get Azure DevOps build logs"""
        project = self.config["project"]
        
        # Get logs
        url = f"{self.base_url}/{project}/_apis/build/builds/{run_id}/logs?api-version=6.0"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Download all log files
        logs = []
        for log in data.get("value", []):
            log_url = log["url"]
            log_response = self.session.get(log_url)
            if log_response.ok:
                logs.append(log_response.text)
        
        full_logs = "\n".join(logs)
        
        # Parse errors and warnings
        errors = self._parse_errors(full_logs)
        warnings = self._parse_warnings(full_logs)
        
        return BuildLog(
            run_id=run_id,
            platform=PlatformType.AZURE_DEVOPS,
            logs=full_logs,
            errors=errors,
            warnings=warnings
        )
    
    def cancel_pipeline(self, run_id: str) -> bool:
        """Cancel Azure DevOps pipeline"""
        project = self.config["project"]
        
        url = f"{self.base_url}/{project}/_apis/build/builds/{run_id}?api-version=6.0"
        body = {"status": "Cancelling"}
        
        response = self.session.patch(url, json=body)
        success = response.ok
        
        if success:
            self.logger.info(f"✅ Pipeline cancelled: {run_id}")
        else:
            self.logger.error(f"❌ Failed to cancel pipeline: {run_id}")
        
        return success
    
    def get_pipeline_history(
        self,
        pipeline_name: str,
        repository: str,
        limit: int = 10
    ) -> List[PipelineRun]:
        """Get Azure DevOps pipeline history"""
        project = self.config["project"]
        pipeline_id = self._get_pipeline_id(pipeline_name)
        
        url = f"{self.base_url}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0&$top={limit}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        runs = []
        for run in data.get("value", []):
            try:
                pipeline_run = self.get_pipeline_run(str(run["id"]))
                runs.append(pipeline_run)
            except Exception as e:
                self.logger.warning(f"Failed to get run {run['id']}: {e}")
        
        return runs
    
    def _get_pipeline_id(self, pipeline_name: str) -> int:
        """Get pipeline ID from name"""
        project = self.config["project"]
        
        url = f"{self.base_url}/{project}/_apis/pipelines?api-version=6.0"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        for pipeline in data.get("value", []):
            if pipeline["name"] == pipeline_name:
                return pipeline["id"]
        
        raise ValueError(f"Pipeline not found: {pipeline_name}")
    
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
