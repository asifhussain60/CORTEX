# DevOps Orchestrator Implementation Guide

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 22, 2025

---

## 📋 Overview

The DevOps Orchestrator provides CI/CD pipeline management capabilities for CORTEX 4.0, enabling automated pipeline triggering, monitoring, and log retrieval across multiple platforms.

**Supported Platforms:**
- Azure DevOps Pipelines ✅
- GitHub Actions ✅
- Jenkins (future)
- GitLab CI/CD (future)

**Key Features:**
- Unified API across all platforms
- Async/await support
- Structured output (Pydantic schemas)
- Build log parsing with error extraction
- Pipeline history retrieval
- Pipeline cancellation

---

## 🏗️ Architecture

```
DevOpsOrchestrator
├── Platform Clients (Abstract Interface)
│   ├── AzureDevOpsClient (REST API v6.0)
│   ├── GitHubActionsClient (REST API v3)
│   └── Future: JenkinsClient, GitLabClient
├── Schemas (Pydantic Models)
│   ├── PipelineConfig
│   ├── PipelineRun
│   ├── PipelineStatus
│   ├── BuildLog
│   └── PipelineError
└── Operations
    ├── trigger_pipeline()
    ├── get_pipeline_status()
    ├── get_pipeline_run()
    ├── get_build_logs()
    ├── cancel_pipeline()
    └── get_pipeline_history()
```

---

## 🚀 Quick Start

### Installation

No additional dependencies required - uses standard requests library.

### Configuration

```python
config = {
    "platforms": {
        "azure_devops": {
            "organization": "my-org",
            "project": "my-project",
            "personal_access_token": "pat-token-here"
        },
        "github_actions": {
            "owner": "my-github-username",
            "repository": "my-repo",
            "token": "github-token-here"
        }
    }
}

orchestrator = DevOpsOrchestrator(config=config)
```

### Basic Usage

```python
import asyncio
from src.orchestration_4_0.orchestrators.devops import (
    DevOpsOrchestrator,
    PipelineConfig,
    PlatformType
)

async def main():
    # Initialize orchestrator
    orchestrator = DevOpsOrchestrator(config=config)
    
    # Trigger pipeline
    pipeline_config = PipelineConfig(
        name="CI-Build",
        repository="my-repo",
        branch="main",
        platform=PlatformType.AZURE_DEVOPS,
        parameters={"BUILD_TYPE": "Release"}
    )
    
    run_id = await orchestrator.trigger_pipeline(pipeline_config)
    print(f"Pipeline triggered: {run_id}")
    
    # Monitor status
    import time
    while True:
        status = await orchestrator.get_pipeline_status(
            run_id,
            PlatformType.AZURE_DEVOPS
        )
        print(f"Status: {status}")
        
        if status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED]:
            break
        
        time.sleep(10)
    
    # Get logs
    logs = await orchestrator.get_build_logs(
        run_id,
        PlatformType.AZURE_DEVOPS
    )
    print(f"Errors: {len(logs.errors)}")
    print(f"Warnings: {len(logs.warnings)}")

asyncio.run(main())
```

---

## 📚 API Reference

### trigger_pipeline(config: PipelineConfig) -> str

Trigger a pipeline run on the specified platform.

**Parameters:**
- `config`: PipelineConfig with name, repository, branch, platform, parameters

**Returns:**
- `run_id`: Unique identifier for the pipeline run

**Example:**
```python
config = PipelineConfig(
    name="Deploy-Production",
    repository="my-app",
    branch="release",
    platform=PlatformType.GITHUB_ACTIONS,
    parameters={"ENVIRONMENT": "prod"}
)

run_id = await orchestrator.trigger_pipeline(config)
```

### get_pipeline_status(run_id: str, platform: PlatformType) -> PipelineStatus

Get current status of a pipeline run.

**Returns:** `QUEUED`, `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`, `UNKNOWN`

### get_pipeline_run(run_id: str, platform: PlatformType) -> PipelineRun

Get detailed information about a pipeline run.

**Returns:** PipelineRun with full details (start time, duration, commit SHA, URL)

### get_build_logs(run_id: str, platform: PlatformType) -> BuildLog

Retrieve build logs with parsed errors and warnings.

**Returns:** BuildLog with:
- `logs`: Raw log content
- `errors`: List of extracted error messages
- `warnings`: List of extracted warnings

### cancel_pipeline(run_id: str, platform: PlatformType) -> bool

Cancel a running pipeline.

**Returns:** True if cancellation successful

### get_pipeline_history(...) -> List[PipelineRun]

Get recent pipeline runs (default: 10).

---

## 🔌 Platform-Specific Notes

### Azure DevOps

**Authentication:** Personal Access Token (PAT)
- Required scopes: `Build (Read & Execute)`
- Token format: `base64` encoded

**API Endpoints:**
- Base URL: `https://dev.azure.com/{organization}`
- API Version: 6.0

**Rate Limits:** 200 requests per resource per hour per user

### GitHub Actions

**Authentication:** Personal Access Token or GitHub App
- Required scopes: `repo`, `workflow`

**API Endpoints:**
- Base URL: `https://api.github.com`
- API Version: v3 (via Accept header)

**Rate Limits:**
- Authenticated: 5,000 requests per hour
- Unauthenticated: 60 requests per hour

**Note:** GitHub Actions trigger is asynchronous - there's a 2-second delay to retrieve run_id

---

## 🧪 Testing

### Run Tests

```bash
pytest tests/orchestration_4_0/orchestrators/devops/ -v
```

### Test Coverage

- **Total Tests:** 20
- **Platform Clients:** 4 tests (initialization, validation)
- **Orchestrator Operations:** 16 tests (all operations + error cases)
- **Coverage:** 85%+ (estimated)

### Mock Testing

Tests use mocked platform clients to avoid real API calls:

```python
# Example test
mock_client = Mock()
mock_client.trigger_pipeline = Mock(return_value="12345")
orchestrator.clients[PlatformType.AZURE_DEVOPS] = mock_client
```

---

## 🔧 Extending to New Platforms

### 1. Create Platform Client

```python
# src/orchestration_4_0/orchestrators/devops/jenkins_client.py

from .platform_client import PlatformClient

class JenkinsClient(PlatformClient):
    def _validate_config(self) -> None:
        required = ["url", "username", "api_token"]
        # Validate config
    
    def trigger_pipeline(self, ...) -> str:
        # Implement Jenkins-specific logic
        pass
    
    # Implement other abstract methods...
```

### 2. Register in DevOpsOrchestrator

```python
# Add to _initialize_clients()

if "jenkins" in platforms_config:
    self.clients[PlatformType.JENKINS] = JenkinsClient(
        platforms_config["jenkins"]
    )
```

### 3. Add Platform Type

```python
# In schemas.py

class PlatformType(str, Enum):
    AZURE_DEVOPS = "azure_devops"
    GITHUB_ACTIONS = "github_actions"
    JENKINS = "jenkins"  # Add new platform
```

---

## 📊 Metrics & Monitoring

**Performance Targets:**
- Pipeline trigger: <5 seconds
- Status check: <2 seconds
- Log retrieval: <10 seconds (depends on log size)

**Logging:**
- All operations logged at INFO level
- Errors logged at ERROR level
- Debug logging available for troubleshooting

**Example Log Output:**
```
2025-12-22 06:45:20 [INFO] 🎭 Triggering pipeline: CI-Build on azure_devops
2025-12-22 06:45:25 [INFO] ✅ Pipeline triggered: 12345
2025-12-22 06:45:30 [INFO] 📋 Retrieving logs for run: 12345
2025-12-22 06:45:35 [INFO] ✅ Retrieved logs: 15234 chars, 2 errors, 5 warnings
```

---

## 🚨 Error Handling

**Common Errors:**

1. **Platform Not Configured**
   - Error: `ValueError: Platform not configured: azure_devops`
   - Solution: Add platform configuration to config dict

2. **Invalid Credentials**
   - Error: `401 Unauthorized`
   - Solution: Verify PAT/token has correct permissions

3. **Pipeline Not Found**
   - Error: `ValueError: Pipeline not found: NonExistent`
   - Solution: Check pipeline name spelling

4. **Rate Limit Exceeded**
   - Error: `429 Too Many Requests`
   - Solution: Implement backoff strategy or reduce request frequency

---

## 🔐 Security Best Practices

1. **Never hardcode credentials** - use environment variables or secret management
2. **Use minimum required scopes** for tokens
3. **Rotate tokens regularly** (recommended: every 90 days)
4. **Enable audit logging** on CI/CD platforms
5. **Use separate tokens** for different environments (dev, staging, prod)

---

## 📝 Examples

### Example 1: Deploy on Green Build

```python
async def deploy_on_green_build():
    """Deploy to production when CI build succeeds"""
    orchestrator = DevOpsOrchestrator(config=config)
    
    # Trigger CI build
    ci_config = PipelineConfig(
        name="CI-Build",
        repository="my-app",
        branch="main",
        platform=PlatformType.AZURE_DEVOPS
    )
    
    ci_run_id = await orchestrator.trigger_pipeline(ci_config)
    
    # Wait for completion
    while True:
        status = await orchestrator.get_pipeline_status(
            ci_run_id,
            PlatformType.AZURE_DEVOPS
        )
        
        if status == PipelineStatus.SUCCESS:
            # Trigger deployment
            deploy_config = PipelineConfig(
                name="Deploy-Production",
                repository="my-app",
                branch="main",
                platform=PlatformType.AZURE_DEVOPS,
                parameters={"ENVIRONMENT": "production"}
            )
            
            await orchestrator.trigger_pipeline(deploy_config)
            break
        
        elif status == PipelineStatus.FAILED:
            logs = await orchestrator.get_build_logs(
                ci_run_id,
                PlatformType.AZURE_DEVOPS
            )
            print(f"CI failed with {len(logs.errors)} errors")
            break
        
        await asyncio.sleep(30)
```

### Example 2: Multi-Platform Deployment

```python
async def deploy_to_all_platforms():
    """Deploy to Azure and AWS simultaneously"""
    orchestrator = DevOpsOrchestrator(config=config)
    
    # Azure deployment
    azure_config = PipelineConfig(
        name="Deploy-Azure",
        repository="my-app",
        branch="release",
        platform=PlatformType.AZURE_DEVOPS
    )
    
    # AWS deployment (via GitHub Actions)
    aws_config = PipelineConfig(
        name="Deploy-AWS",
        repository="my-app",
        branch="release",
        platform=PlatformType.GITHUB_ACTIONS
    )
    
    # Trigger both
    azure_run = await orchestrator.trigger_pipeline(azure_config)
    aws_run = await orchestrator.trigger_pipeline(aws_config)
    
    print(f"Azure: {azure_run}, AWS: {aws_run}")
```

---

## 🔄 Integration with CI/CD Self-Healing (Task 6.14)

The DevOps Orchestrator serves as the foundation for Task 6.14 (CI/CD Self-Healing Orchestrator), providing:

1. **Pipeline Monitoring** - Real-time status checks
2. **Log Analysis** - Error extraction and categorization
3. **Pipeline Control** - Trigger retries or rollbacks
4. **Multi-Platform Support** - Unified interface for all platforms

---

## 📖 References

- **Azure DevOps API:** https://learn.microsoft.com/en-us/rest/api/azure/devops/
- **GitHub Actions API:** https://docs.github.com/en/rest/actions
- **Phase 6 Plan:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/phases/phase-06-orchestrator-consolidation.md`

---

**Status:** ✅ Implementation Complete  
**Tests:** 20/20 passing (100%)  
**Next:** Task 6.14 - CI/CD Self-Healing Orchestrator
