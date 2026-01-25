# Quickstart Guide

## Installation

### Prerequisites
- Python 3.9+
- pip or conda
- Git

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/asifhussain60/CORTEX.git
   cd CORTEX
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify installation:
   ```bash
   python3 -m cortex --version
   ```

## First Steps

### 1. Run the Master Orchestrator
   ```python
   from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
   
   orchestrator = MasterOrchestrator()
   result = await orchestrator.execute("Implement a feature")
   ```

### 2. Use Intent Router
   ```python
   from cortex.orchestrators.core.intent_router import IntentRouter
   
   router = IntentRouter()
   intent = router.classify("Fix a bug in authentication module")
   ```

### 3. Access Documentation
   ```bash
   mkdocs serve
   # Visit http://localhost:8000
   ```

## Common Tasks

- **Implement Feature:** `/implement {feature_name}`
- **Fix Bug:** `/fix {issue_description}`
- **Refactor Code:** `/refactor {target_module}`
- **Run Tests:** `/test {module_name}`
- **Generate Docs:** `/doc-fresh-generate`

---

Next: [Architecture Overview](../02-architecture/overview.md)
