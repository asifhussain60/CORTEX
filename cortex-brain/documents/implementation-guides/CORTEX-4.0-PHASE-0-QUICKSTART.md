# 🚀 CORTEX 4.0 Phase 0: Foundation Quick Start

**Timeline:** Week 1-2  
**Goal:** Set up clean infrastructure for incremental migration  
**Status:** 📋 READY TO START

---

## 🎯 Phase 0 Objectives

1. ✅ Create `CORTEX-4.0` branch
2. ✅ Initialize clean directory structure
3. ✅ Implement core infrastructure:
   - Brain engine (unified 4-tier API)
   - MCP server scaffolding
   - Base operation framework
   - Configuration system
4. ✅ Set up testing infrastructure
5. ✅ Create deployment scaffolding

**Validation:** All infrastructure working before orchestrator migration begins.

---

## 📋 Step-by-Step Guide

### Step 1: Branch Creation

```bash
# From CORTEX-3.0 branch
git checkout -b CORTEX-4.0
git push -u origin CORTEX-4.0
```

**Validation:**
```bash
git branch --show-current  # Should output: CORTEX-4.0
```

---

### Step 2: Create Clean Directory Structure

```bash
# Create new structure (parallel to src/)
mkdir -p cortex_4_0/{cortex_core,cortex_orchestrators,cortex_tools,cortex_deployment}

# Core subdirectories
mkdir -p cortex_4_0/cortex_core/{brain,mcp,operations,config}
mkdir -p cortex_4_0/cortex_core/brain/{tier0,tier1,tier2,tier3}
mkdir -p cortex_4_0/cortex_core/mcp/{tools,schemas}

# Orchestrator subdirectories
mkdir -p cortex_4_0/cortex_orchestrators/{planning,tdd,maintenance,sanitization,review,refinement}

# Tools subdirectories
mkdir -p cortex_4_0/cortex_tools/{ast_analyzer,git_ops,file_ops,test_runner,metrics}

# Deployment subdirectories
mkdir -p cortex_4_0/cortex_deployment/{pypi,docker,vscode,github/workflows}

# Tests
mkdir -p cortex_4_0/tests/{unit,integration,e2e,fixtures}

# Documentation
mkdir -p cortex_4_0/docs/{architecture,api,guides,migration}
```

**Validation:**
```bash
tree cortex_4_0 -L 2  # Verify structure
```

---

### Step 3: Implement Brain Engine

**File:** `cortex_4_0/cortex_core/brain/brain_engine.py`

```python
"""
Unified Brain Engine for CORTEX 4.0
Provides single interface to all 4 brain tiers
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import yaml
import json

@dataclass
class BrainContext:
    """Complete brain context from all tiers"""
    tier0_rules: Dict[str, Any]  # SKULL rules
    tier1_conversations: List[Dict]  # Recent conversations
    tier2_patterns: Dict[str, Any]  # Learned patterns
    tier3_dev_context: Dict[str, Any]  # Dev metrics/hotspots
    timestamp: datetime

class BrainEngine:
    """Unified interface to CORTEX brain (4-tier system)"""
    
    def __init__(self, brain_path: str = "cortex-brain"):
        self.brain_path = brain_path
        self.tier0 = Tier0Governance(f"{brain_path}/tier0")
        self.tier1 = Tier1Memory(f"{brain_path}/tier1")
        self.tier2 = Tier2Knowledge(f"{brain_path}/tier2")
        self.tier3 = Tier3DevContext(f"{brain_path}/tier3")
    
    def get_context(
        self,
        conversation_id: Optional[str] = None,
        include_patterns: bool = True,
        include_metrics: bool = True
    ) -> BrainContext:
        """
        Get unified context from all brain tiers
        
        Args:
            conversation_id: Specific conversation to retrieve
            include_patterns: Include learned patterns from tier2
            include_metrics: Include dev metrics from tier3
        
        Returns:
            BrainContext with all relevant information
        """
        return BrainContext(
            tier0_rules=self.tier0.get_rules(),
            tier1_conversations=self.tier1.get_conversations(conversation_id),
            tier2_patterns=self.tier2.get_patterns() if include_patterns else {},
            tier3_dev_context=self.tier3.get_context() if include_metrics else {},
            timestamp=datetime.now()
        )
    
    def learn(self, pattern: str, outcome: str, metrics: Dict[str, Any]):
        """
        Record learning in tier2 (knowledge graph)
        
        Args:
            pattern: Pattern name (e.g., "TDD workflow")
            outcome: Success/failure
            metrics: Execution metrics
        """
        self.tier2.record_pattern(pattern, outcome, metrics)
    
    def validate_against_skull(self, action: str, context: Dict) -> tuple[bool, str]:
        """
        Validate action against SKULL rules (tier0)
        
        Args:
            action: Proposed action
            context: Current context
        
        Returns:
            (is_valid, reason)
        """
        return self.tier0.validate(action, context)


class Tier0Governance:
    """SKULL brain protection rules"""
    
    def __init__(self, path: str):
        self.rules_path = f"{path}/brain-protection-rules.yaml"
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        with open(self.rules_path) as f:
            return yaml.safe_load(f)
    
    def get_rules(self) -> Dict:
        return self.rules
    
    def validate(self, action: str, context: Dict) -> tuple[bool, str]:
        """Validate action against SKULL rules"""
        # Implementation: Check action against specific rules
        # For now, stub
        return (True, "No violations detected")


class Tier1Memory:
    """Working memory (70-conversation FIFO)"""
    
    def __init__(self, path: str):
        self.conversations_path = f"{path}/conversation-context.jsonl"
        self.max_conversations = 70
    
    def get_conversations(self, conversation_id: Optional[str] = None) -> List[Dict]:
        """Retrieve conversations from JSONL"""
        conversations = []
        try:
            with open(self.conversations_path) as f:
                for line in f:
                    conv = json.loads(line)
                    if conversation_id is None or conv.get("id") == conversation_id:
                        conversations.append(conv)
        except FileNotFoundError:
            return []
        
        # Return last 70 (FIFO)
        return conversations[-self.max_conversations:]


class Tier2Knowledge:
    """Knowledge graph (pattern learning)"""
    
    def __init__(self, path: str):
        self.graph_path = f"{path}/knowledge-graph.yaml"
    
    def get_patterns(self) -> Dict:
        """Load learned patterns"""
        try:
            with open(self.graph_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def record_pattern(self, pattern: str, outcome: str, metrics: Dict):
        """Record new pattern learning"""
        patterns = self.get_patterns()
        
        if pattern not in patterns:
            patterns[pattern] = {
                "success_count": 0,
                "failure_count": 0,
                "metrics": []
            }
        
        if outcome == "success":
            patterns[pattern]["success_count"] += 1
        else:
            patterns[pattern]["failure_count"] += 1
        
        patterns[pattern]["metrics"].append({
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome,
            **metrics
        })
        
        with open(self.graph_path, "w") as f:
            yaml.dump(patterns, f)


class Tier3DevContext:
    """Development context (metrics, hotspots)"""
    
    def __init__(self, path: str):
        self.context_path = f"{path}/development-context.yaml"
    
    def get_context(self) -> Dict:
        """Load development context"""
        try:
            with open(self.context_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
```

**Validation:**
```python
# Test brain engine
from cortex_core.brain import BrainEngine

brain = BrainEngine()
context = brain.get_context()
print(f"Loaded {len(context.tier1_conversations)} conversations")
```

---

### Step 4: Implement MCP Server Scaffolding

**File:** `cortex_4_0/cortex_core/mcp/server.py`

```python
"""
MCP Server for CORTEX 4.0
Implements Model Context Protocol for tool exposure
"""
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import asyncio
import json

@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable

class CortexMCPServer:
    """MCP Server implementation for CORTEX 4.0"""
    
    def __init__(self, name: str = "cortex-4.0"):
        self.name = name
        self.version = "4.0.0"
        self.tools: Dict[str, MCPTool] = {}
    
    def register_tool(self, tool: MCPTool):
        """Register a new MCP tool"""
        self.tools[tool.name] = tool
        print(f"✅ Registered MCP tool: {tool.name}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools (MCP protocol)"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool (MCP protocol)"""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        tool = self.tools[name]
        return await tool.handler(arguments)
    
    def run(self, host: str = "localhost", port: int = 5000):
        """Start MCP server"""
        print(f"🚀 CORTEX MCP Server v{self.version}")
        print(f"📡 Listening on {host}:{port}")
        print(f"🛠️  Registered tools: {len(self.tools)}")
        
        # TODO: Implement actual server (HTTP/WebSocket)
        # For now, just print info
        for tool_name in self.tools:
            print(f"   - {tool_name}")

# Example tool registration
def create_example_tool():
    """Example: Health check tool"""
    def handler(args: Dict) -> Dict:
        return {
            "status": "healthy",
            "version": "4.0.0",
            "timestamp": "2025-12-17T00:00:00Z"
        }
    
    return MCPTool(
        name="cortex_healthcheck",
        description="Check CORTEX system health",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=handler
    )

if __name__ == "__main__":
    server = CortexMCPServer()
    server.register_tool(create_example_tool())
    server.run()
```

**Validation:**
```bash
python cortex_4_0/cortex_core/mcp/server.py
# Should output:
# 🚀 CORTEX MCP Server v4.0.0
# 📡 Listening on localhost:5000
# 🛠️  Registered tools: 1
#    - cortex_healthcheck
```

---

### Step 5: Create Base Operation Framework

**File:** `cortex_4_0/cortex_core/operations/base_operation.py`

```python
"""
Base operation framework for CORTEX 4.0
All orchestrators inherit from BaseOperation
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
from cortex_core.brain import BrainEngine
from cortex_core.mcp.server import MCPTool

@dataclass
class OperationResult:
    """Standard operation result"""
    success: bool
    message: str
    data: Dict[str, Any]
    errors: List[str]

class BaseOperation(ABC):
    """
    Abstract base class for all CORTEX operations
    
    All orchestrators MUST inherit from this class
    """
    
    def __init__(self, brain: BrainEngine):
        self.brain = brain
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, request: Dict[str, Any]) -> OperationResult:
        """
        Execute the operation
        
        Args:
            request: Operation request parameters
        
        Returns:
            OperationResult with success/failure status
        """
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> List[MCPTool]:
        """
        Return MCP tools provided by this operation
        
        Returns:
            List of MCPTool objects
        """
        pass
    
    def validate_request(self, request: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate request against SKULL rules
        
        Args:
            request: Operation request
        
        Returns:
            (is_valid, error_message)
        """
        return self.brain.validate_against_skull(
            action=self.name,
            context=request
        )
    
    def log_execution(self, result: OperationResult):
        """Log execution to brain (tier1)"""
        # TODO: Implement logging to tier1
        pass
```

**Validation:**
```python
# Example orchestrator
from cortex_core.operations.base_operation import BaseOperation, OperationResult

class ExampleOrchestrator(BaseOperation):
    def execute(self, request):
        return OperationResult(
            success=True,
            message="Example executed",
            data={},
            errors=[]
        )
    
    def get_mcp_tools(self):
        return []

# Test
brain = BrainEngine()
orch = ExampleOrchestrator(brain)
result = orch.execute({})
print(f"Success: {result.success}")
```

---

### Step 6: Configuration System

**File:** `cortex_4_0/cortex_core/config/loader.py`

```python
"""
Configuration management for CORTEX 4.0
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Load and validate CORTEX configuration"""
    
    def __init__(self, config_path: str = "cortex.config.json"):
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration file"""
        if not self.config_path.exists():
            return self._create_default()
        
        with open(self.config_path) as f:
            if self.config_path.suffix == ".json":
                return json.load(f)
            else:
                return yaml.safe_load(f)
    
    def _create_default(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "version": "4.0.0",
            "brain_path": "cortex-brain",
            "mcp_server": {
                "host": "localhost",
                "port": 5000,
                "enabled": True
            },
            "logging": {
                "level": "INFO",
                "format": "json"
            },
            "orchestrators": {
                "enabled": []
            }
        }
        
        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load()
```

**Validation:**
```python
from cortex_core.config import ConfigLoader

config = ConfigLoader()
print(f"Brain path: {config.get('brain_path')}")
print(f"MCP enabled: {config.get('mcp_server.enabled')}")
```

---

### Step 7: Testing Infrastructure

**File:** `cortex_4_0/tests/conftest.py`

```pytest
"""
Pytest configuration for CORTEX 4.0
"""
import pytest
from cortex_core.brain import BrainEngine
from cortex_core.config import ConfigLoader

@pytest.fixture
def brain():
    """Provide brain engine for tests"""
    return BrainEngine(brain_path="cortex-brain")

@pytest.fixture
def config():
    """Provide configuration for tests"""
    return ConfigLoader("cortex.config.json")

@pytest.fixture
def mock_mcp_server():
    """Provide mock MCP server"""
    from cortex_core.mcp.server import CortexMCPServer
    return CortexMCPServer("test-server")
```

**File:** `cortex_4_0/tests/unit/test_brain_engine.py`

```python
"""
Unit tests for Brain Engine
"""
import pytest
from cortex_core.brain import BrainEngine

def test_brain_engine_initialization(brain):
    """Test brain engine can initialize"""
    assert brain is not None
    assert brain.tier0 is not None
    assert brain.tier1 is not None

def test_get_context(brain):
    """Test getting unified context"""
    context = brain.get_context()
    assert context.tier0_rules is not None
    assert context.tier1_conversations is not None

def test_learn(brain):
    """Test recording pattern learning"""
    brain.learn(
        pattern="test_pattern",
        outcome="success",
        metrics={"duration": 100}
    )
    # Verify pattern recorded
    patterns = brain.tier2.get_patterns()
    assert "test_pattern" in patterns
```

**Validation:**
```bash
cd cortex_4_0
pytest tests/ -v
# Should output: All tests passed
```

---

### Step 8: Deployment Scaffolding

**File:** `cortex_4_0/cortex_deployment/pypi/setup.py`

```python
"""
PyPI package setup for CORTEX 4.0
"""
from setuptools import setup, find_packages

setup(
    name="cortex-ai",
    version="4.0.0",
    author="Asif Hussain",
    author_email="your.email@example.com",
    description="GitHub Copilot memory & planning system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    packages=find_packages(where="../../"),
    package_dir={"": "../.."},
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "cortex=cortex_core.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

**File:** `cortex_4_0/cortex_deployment/docker/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY cortex_core/ ./cortex_core/
COPY cortex_orchestrators/ ./cortex_orchestrators/
COPY cortex_tools/ ./cortex_tools/

# Copy brain data
COPY cortex-brain/ ./cortex-brain/

EXPOSE 5000

CMD ["python", "-m", "cortex_core.mcp.server"]
```

**Validation:**
```bash
# Test Docker build
cd cortex_4_0
docker build -t cortex-ai:4.0-dev -f cortex_deployment/docker/Dockerfile .
# Should output: Successfully built ...
```

---

### Step 9: CI/CD Pipeline

**File:** `.github/workflows/cortex-4.0-ci.yml`

```yaml
name: CORTEX 4.0 CI

on:
  push:
    branches: [CORTEX-4.0]
  pull_request:
    branches: [CORTEX-4.0]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd cortex_4_0
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd cortex_4_0
          pytest tests/ --cov=cortex_core --cov=cortex_orchestrators --cov-report=xml
      
      - name: Check coverage
        run: |
          cd cortex_4_0
          coverage report --fail-under=90
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: cortex_4_0/coverage.xml
```

---

## ✅ Phase 0 Validation Checklist

### Infrastructure
- [ ] `CORTEX-4.0` branch created
- [ ] Clean directory structure in place
- [ ] All subdirectories created

### Core Components
- [ ] Brain engine implemented and tested
- [ ] MCP server scaffolding working
- [ ] Base operation framework functional
- [ ] Configuration system operational

### Testing
- [ ] pytest configuration working
- [ ] Example tests passing
- [ ] Coverage reporting functional
- [ ] CI pipeline green

### Deployment
- [ ] setup.py configured
- [ ] Dockerfile builds successfully
- [ ] VS Code extension skeleton created
- [ ] GitHub Actions workflow configured

---

## 🚦 Ready for Phase 1?

Before moving to Phase 1 (orchestrator migration), ensure:

1. ✅ All Phase 0 checklist items complete
2. ✅ CI pipeline passing
3. ✅ Test coverage > 90%
4. ✅ Documentation complete
5. ✅ Team/stakeholder approval

---

## 📞 Questions & Support

**Issue:** Something not working?  
**Action:** Open GitHub issue with `[CORTEX-4.0]` tag

**Question:** Need clarification?  
**Action:** Review `CORTEX-4.0-ARCHITECTURE-DESIGN.md` first, then ask

---

**Next:** Once Phase 0 complete, proceed to Phase 1 (TDD Orchestrator migration).
