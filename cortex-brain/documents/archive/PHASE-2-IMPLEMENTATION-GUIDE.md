# Phase 2 Implementation Guide: Repository Auto-Discovery
**Estimated Time:** 4 hours  
**Dependencies:** Phase 1 (Configuration System) ✅ Complete  
**Priority:** HIGH - Enables Phases 4 and 7

---

## 🎯 Objective

Create an automatic repository discovery system that scans, validates, and registers repositories on dashboard launch, eliminating manual configuration.

---

## 📋 Tasks Overview

1. Create Repository Discovery Service (90 minutes)
2. Create Repository Registry System (60 minutes)
3. Update Admin Dashboard Launcher (45 minutes)
4. Update UI Data Loader (45 minutes)

---

## Task 1: Create Repository Discovery Service

**File:** `src/operations/modules/dashboard/repository_discovery_service.py`

```python
"""
Repository Discovery Service

Automatically discovers, validates, and registers repositories for admin dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from src.config.dashboard_config import get_config

logger = logging.getLogger(__name__)


@dataclass
class RepoMetadata:
    """Repository metadata"""
    id: str
    name: str
    path: str
    discovered: str
    last_updated: str
    status: str  # active, inactive, missing
    data_files: int
    data_file_list: List[str]
    file_sizes: Dict[str, int]  # filename -> size in bytes
    total_size: int


class RepositoryDiscoveryService:
    """
    Discovers and validates repositories in the data/repos/ directory.
    """
    
    def __init__(self):
        """Initialize discovery service"""
        self.config = get_config()
        self.repos_path = self.config.get_path('repos')
        self.registry_path = self.config.get_path('repository_registry')
        self.collector_config = self.config.get_collector_config()
        self.discovery_config = self.config.get_discovery_config()
        
        logger.info(f"Repository discovery initialized: {self.repos_path}")
    
    def scan_repositories(self) -> List[RepoMetadata]:
        """
        Scan repos directory for valid repositories.
        
        Returns:
            List of discovered repository metadata
        """
        logger.info("Scanning for repositories...")
        
        if not self.repos_path.exists():
            logger.warning(f"Repos path does not exist: {self.repos_path}")
            self.repos_path.mkdir(parents=True, exist_ok=True)
            return []
        
        discovered = []
        
        for item in self.repos_path.iterdir():
            if not item.is_dir():
                continue
            
            # Skip hidden directories
            if item.name.startswith('.'):
                continue
            
            # Validate repository
            if self.validate_repository(item):
                metadata = self._extract_metadata(item)
                discovered.append(metadata)
                logger.info(f"Discovered: {metadata.name} ({metadata.data_files} files)")
            else:
                logger.debug(f"Skipped invalid repository: {item.name}")
        
        logger.info(f"Discovery complete: {len(discovered)} repositories found")
        return discovered
    
    def validate_repository(self, repo_path: Path) -> bool:
        """
        Validate that directory contains valid repository data.
        
        Args:
            repo_path: Path to repository directory
        
        Returns:
            True if valid, False otherwise
        """
        if not repo_path.exists() or not repo_path.is_dir():
            return False
        
        # Check for required files
        required_files = self.collector_config.required_files
        data_files = list(repo_path.glob('*.json'))
        
        if len(data_files) < self.discovery_config.min_data_files:
            logger.debug(f"{repo_path.name}: Too few data files ({len(data_files)})")
            return False
        
        # Check for metadata if required
        if self.discovery_config.require_metadata:
            metadata_file = repo_path / "metadata.json"
            if not metadata_file.exists():
                logger.debug(f"{repo_path.name}: Missing metadata.json")
                return False
        
        return True
    
    def _extract_metadata(self, repo_path: Path) -> RepoMetadata:
        """Extract metadata from repository directory"""
        data_files = list(repo_path.glob('*.json'))
        
        # Load metadata.json if exists
        metadata_file = repo_path / "metadata.json"
        repo_name = repo_path.name
        last_updated = datetime.now().isoformat()
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    meta = json.load(f)
                    repo_name = meta.get('repository_name', repo_path.name)
                    last_updated = meta.get('collection_date', last_updated)
            except Exception as e:
                logger.warning(f"Failed to load metadata for {repo_path.name}: {e}")
        
        # Calculate file sizes
        file_sizes = {}
        total_size = 0
        for file in data_files:
            size = file.stat().st_size
            file_sizes[file.name] = size
            total_size += size
        
        return RepoMetadata(
            id=repo_path.name,
            name=repo_name,
            path=str(repo_path.relative_to(self.repos_path.parent.parent)),
            discovered=datetime.now().isoformat(),
            last_updated=last_updated,
            status='active',
            data_files=len(data_files),
            data_file_list=[f.name for f in data_files],
            file_sizes=file_sizes,
            total_size=total_size
        )
    
    def register_repositories(self, repositories: List[RepoMetadata]) -> None:
        """
        Register discovered repositories in registry file.
        
        Args:
            repositories: List of repository metadata to register
        """
        logger.info(f"Registering {len(repositories)} repositories...")
        
        # Load existing registry if exists
        existing_registry = self._load_registry()
        
        # Merge with discovered repos
        registry = {
            "repositories": [asdict(repo) for repo in repositories],
            "last_scan": datetime.now().isoformat(),
            "total_repositories": len(repositories),
            "scan_config": {
                "auto_scan": self.discovery_config.auto_scan,
                "min_data_files": self.discovery_config.min_data_files,
                "require_metadata": self.discovery_config.require_metadata
            }
        }
        
        # Save registry
        self._save_registry(registry)
        logger.info(f"Registry updated: {self.registry_path}")
    
    def remove_missing_repositories(self) -> List[str]:
        """
        Remove repositories from registry that no longer exist.
        
        Returns:
            List of removed repository IDs
        """
        logger.info("Checking for missing repositories...")
        
        registry = self._load_registry()
        if not registry or 'repositories' not in registry:
            return []
        
        removed = []
        active_repos = []
        
        for repo in registry['repositories']:
            repo_path = self.repos_path / repo['id']
            
            if repo_path.exists() and self.validate_repository(repo_path):
                active_repos.append(repo)
            else:
                removed.append(repo['id'])
                logger.info(f"Removed missing repository: {repo['id']}")
        
        if removed:
            registry['repositories'] = active_repos
            registry['total_repositories'] = len(active_repos)
            registry['last_scan'] = datetime.now().isoformat()
            self._save_registry(registry)
        
        return removed
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file"""
        if not self.registry_path.exists():
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {}
    
    def _save_registry(self, registry: Dict[str, Any]) -> None:
        """Save registry to file"""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def get_repository_count(self) -> int:
        """Get total count of registered repositories"""
        registry = self._load_registry()
        return registry.get('total_repositories', 0)
    
    def get_repository_by_id(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get specific repository metadata"""
        registry = self._load_registry()
        repos = registry.get('repositories', [])
        
        for repo in repos:
            if repo['id'] == repo_id:
                return repo
        
        return None


# Convenience function
def discover_and_register_repositories() -> List[RepoMetadata]:
    """
    Convenience function to discover and register all repositories.
    
    Returns:
        List of discovered repositories
    """
    service = RepositoryDiscoveryService()
    
    # Scan for repositories
    repos = service.scan_repositories()
    
    # Register them
    service.register_repositories(repos)
    
    # Remove missing
    removed = service.remove_missing_repositories()
    
    if removed:
        logger.info(f"Removed {len(removed)} missing repositories")
    
    return repos


__all__ = ['RepositoryDiscoveryService', 'RepoMetadata', 'discover_and_register_repositories']
```

---

## Task 2: Update Admin Dashboard Launcher

**File:** `src/operations/modules/admin_dashboard_launcher_module.py`

**Changes:**
1. Import discovery service
2. Call discovery on execute()
3. Update repository count display

**Update execute() method:**

```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute admin dashboard launch with auto-discovery"""
    try:
        # Validate admin repository
        if not self._is_admin_repo():
            return {
                "success": False,
                "error": "admin_only_feature",
                "message": "❌ Admin Dashboard only available in CORTEX development repository."
            }
        
        # AUTO-DISCOVERY: Scan and register repositories
        from src.operations.modules.dashboard.repository_discovery_service import discover_and_register_repositories
        
        self.logger.info("🔍 Auto-discovering repositories...")
        discovered_repos = discover_and_register_repositories()
        self.logger.info(f"✅ Discovered {len(discovered_repos)} repositories")
        
        # Get all available repositories (from registry)
        repos = self._discover_repositories()
        
        if not repos:
            return {
                "success": False,
                "error": "no_repositories",
                "message": (
                    "❌ No dashboard data found after discovery.\n\n"
                    "Generate dashboard data:\n"
                    "  python scripts\\collect_dashboard_data_with_progress.py"
                )
            }
        
        # Continue with existing launch logic...
        default_repo = self._get_last_selected_repo() or repos[0]
        
        # ... (rest of launch code)
        
        message = (
            f"✅ Admin Dashboard launched!\n\n"
            f"🔍 Auto-discovered: {len(discovered_repos)} repositories\n"
            f"📊 Total available: {len(repos)} repositories\n\n"
            f"📁 Repositories:\n"
        )
        
        for repo in repos[:5]:  # Show first 5
            message += f"  • {repo['name']}\n"
        
        if len(repos) > 5:
            message += f"  ... and {len(repos) - 5} more\n"
        
        return {
            "success": True,
            "discovered": len(discovered_repos),
            "total_repos": len(repos),
            "message": message
        }
        
    except Exception as e:
        self.logger.error(f"Dashboard launch failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": "launch_failed",
            "message": f"❌ Failed to launch: {e}"
        }
```

---

## Task 3: Update UI Data Loader

**File:** `cortex-brain/dashboards/ui/data-loader.js`

**Add registry loading:**

```javascript
/**
 * Load repository registry
 */
async function loadRepositoryRegistry() {
    try {
        const response = await fetch('/data/repository-registry.json');
        if (!response.ok) {
            console.warn('Registry not found, using default sources');
            return null;
        }
        
        const registry = await response.json();
        console.log(`Loaded registry: ${registry.total_repositories} repositories`);
        
        // Update DATA_SOURCES from registry
        registry.repositories.forEach(repo => {
            DATA_SOURCES[repo.id] = `/data/repos/${repo.id}/`;
        });
        
        return registry;
    } catch (error) {
        console.error('Failed to load registry:', error);
        return null;
    }
}

// Call on page load
window.addEventListener('DOMContentLoaded', async () => {
    await loadRepositoryRegistry();
    // Continue with normal initialization
});
```

---

## Task 4: Create Tests

**File:** `tests/dashboard/unit/test_repository_discovery.py`

```python
"""Tests for repository discovery service"""

import pytest
import json
from pathlib import Path
from src.operations.modules.dashboard.repository_discovery_service import (
    RepositoryDiscoveryService,
    RepoMetadata
)


def test_discovery_service_initialization(tmp_path):
    """Test service initializes correctly"""
    service = RepositoryDiscoveryService()
    assert service.repos_path.exists()


def test_validate_repository_with_minimal_files(tmp_path):
    """Test validation with minimum required files"""
    service = RepositoryDiscoveryService()
    
    # Create test repo
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Create minimal files
    (repo_path / "health-data.json").write_text("{}")
    (repo_path / "metadata.json").write_text("{}")
    (repo_path / "tech-stack.json").write_text("{}")
    
    # Should be valid
    assert service.validate_repository(repo_path)


def test_validate_repository_missing_files(tmp_path):
    """Test validation fails with too few files"""
    service = RepositoryDiscoveryService()
    
    repo_path = tmp_path / "invalid-repo"
    repo_path.mkdir()
    
    # Only one file
    (repo_path / "health-data.json").write_text("{}")
    
    # Should be invalid
    assert not service.validate_repository(repo_path)


def test_scan_repositories_finds_valid_repos(tmp_path, monkeypatch):
    """Test scanning finds valid repositories"""
    # Mock repos path
    repos_path = tmp_path / "repos"
    repos_path.mkdir()
    
    # Create valid repo
    valid_repo = repos_path / "valid-repo"
    valid_repo.mkdir()
    (valid_repo / "health-data.json").write_text("{}")
    (valid_repo / "metadata.json").write_text('{"repository_name": "Valid Repo"}')
    (valid_repo / "tech-stack.json").write_text("{}")
    (valid_repo / "security.json").write_text("{}")
    
    # Create invalid repo
    invalid_repo = repos_path / "invalid-repo"
    invalid_repo.mkdir()
    (invalid_repo / "single-file.json").write_text("{}")
    
    service = RepositoryDiscoveryService()
    monkeypatch.setattr(service, 'repos_path', repos_path)
    
    discovered = service.scan_repositories()
    
    assert len(discovered) == 1
    assert discovered[0].id == "valid-repo"
    assert discovered[0].name == "Valid Repo"


def test_register_repositories_creates_registry(tmp_path, monkeypatch):
    """Test repository registration"""
    registry_path = tmp_path / "registry.json"
    
    service = RepositoryDiscoveryService()
    monkeypatch.setattr(service, 'registry_path', registry_path)
    
    repos = [
        RepoMetadata(
            id="repo1",
            name="Repo 1",
            path="data/repos/repo1",
            discovered="2025-12-06T10:00:00",
            last_updated="2025-12-06T09:00:00",
            status="active",
            data_files=5,
            data_file_list=["health-data.json"],
            file_sizes={"health-data.json": 1024},
            total_size=1024
        )
    ]
    
    service.register_repositories(repos)
    
    assert registry_path.exists()
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    assert registry['total_repositories'] == 1
    assert registry['repositories'][0]['id'] == "repo1"


def test_remove_missing_repositories(tmp_path, monkeypatch):
    """Test removal of missing repositories"""
    # Setup
    repos_path = tmp_path / "repos"
    repos_path.mkdir()
    registry_path = tmp_path / "registry.json"
    
    # Create existing repo
    existing_repo = repos_path / "existing"
    existing_repo.mkdir()
    for i in range(4):
        (existing_repo / f"file{i}.json").write_text("{}")
    
    # Create registry with existing + missing repo
    registry = {
        "repositories": [
            {"id": "existing", "name": "Existing", "data_files": 4},
            {"id": "missing", "name": "Missing", "data_files": 3}
        ],
        "total_repositories": 2
    }
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f)
    
    service = RepositoryDiscoveryService()
    monkeypatch.setattr(service, 'repos_path', repos_path)
    monkeypatch.setattr(service, 'registry_path', registry_path)
    
    removed = service.remove_missing_repositories()
    
    assert len(removed) == 1
    assert "missing" in removed
    
    # Verify registry updated
    with open(registry_path) as f:
        updated = json.load(f)
    
    assert updated['total_repositories'] == 1
    assert updated['repositories'][0]['id'] == "existing"
```

---

## 🧪 Testing Checklist

- [ ] Unit tests pass for discovery service
- [ ] Scanning finds all valid repositories
- [ ] Invalid repositories are skipped
- [ ] Registry file created correctly
- [ ] Missing repositories removed
- [ ] Admin launcher calls discovery
- [ ] UI loads from registry
- [ ] No performance regression (< 1s scan time)

---

## 📊 Success Criteria

1. Dashboard automatically discovers new repositories on launch
2. No manual configuration required for new repos
3. Missing repositories automatically removed
4. Registry file maintained accurately
5. Sub-second discovery performance
6. All tests passing

---

## 🔧 Troubleshooting

**Problem:** Discovery finds no repositories  
**Solution:** Check `cortex-brain/dashboards/data/repos/` exists and has subdirectories with JSON files

**Problem:** Repositories not showing in UI  
**Solution:** Check registry file exists at `data/repository-registry.json` and is valid JSON

**Problem:** Slow discovery  
**Solution:** Check for large number of files in repos, consider caching

---

**Implementation Time:** ~4 hours  
**Next Phase:** Phase 3 (Deep Data Collection)
