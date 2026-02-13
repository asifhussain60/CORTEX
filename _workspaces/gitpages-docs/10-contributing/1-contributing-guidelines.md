# Contributing Guidelines

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready  
**Audience:** Contributors, Developers

## Overview

Thank you for your interest in contributing to CORTEX! This document provides guidelines for contributing code, documentation, tests, and other improvements to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Requirements](#documentation-requirements)
7. [Pull Request Process](#pull-request-process)
8. [Review Process](#review-process)
9. [Release Process](#release-process)
10. [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone, regardless of:

- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Our Standards

**Examples of behavior that contributes to a positive environment:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior:**

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project team at [contact email]. All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Python 3.9+** installed
2. **Git 2.20+** configured
3. **Virtual environment** tools (venv or conda)
4. **pytest** for running tests
5. **pre-commit** hooks installed

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/CORTEX.git
cd CORTEX

# Add upstream remote
git remote add upstream https://github.com/asifhussain60/CORTEX.git
```

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
pytest tests/ -v --tb=short
```

### Configuration

```bash
# Copy example configuration
cp cortex-config.example.yaml cortex-config.yaml

# Initialize governance database
cortex governance init

# Verify installation
cortex health check
```

---

## Development Workflow

### Branching Strategy

We use a feature branch workflow:

```
main (protected)
├── feature/your-feature-name
├── bugfix/issue-123-description
├── docs/update-api-reference
└── refactor/improve-governance-engine
```

### Branch Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| **Feature** | `feature/<name>` | `feature/add-postgresql-support` |
| **Bugfix** | `bugfix/<issue>-<name>` | `bugfix/456-fix-audit-trail` |
| **Documentation** | `docs/<name>` | `docs/update-quickstart` |
| **Refactor** | `refactor/<name>` | `refactor/simplify-lens-protocol` |
| **Performance** | `perf/<name>` | `perf/optimize-knowledge-query` |
| **Test** | `test/<name>` | `test/add-integration-tests` |

### Creating a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit frequently
git add .
git commit -m "feat: add initial implementation"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process or tooling changes

**Examples:**

```bash
# Good commit messages
git commit -m "feat(orchestrator): add support for async execution"
git commit -m "fix(governance): resolve rule evaluation deadlock"
git commit -m "docs(api): update REST API authentication guide"
git commit -m "test(lens): add unit tests for intent canonicalization"

# Bad commit messages (avoid these)
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

### Keeping Your Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase on main (preferred over merge)
git rebase upstream/main

# If conflicts occur
git status  # See conflicting files
# Fix conflicts manually
git add .
git rebase --continue

# Force push to your fork
git push origin feature/your-feature-name --force-with-lease
```

---

## Coding Standards

### Python Style Guide

CORTEX follows [PEP 8](https://pep8.org/) with some project-specific conventions:

#### Code Formatting

```bash
# Format code with black
black src/ tests/ --line-length 100

# Sort imports with isort
isort src/ tests/ --profile black

# Check with flake8
flake8 src/ tests/ --max-line-length 100
```

#### Type Hints

Always use type hints:

```python
# Good
def process_intent(
    intent: str, 
    context: Optional[Dict[str, Any]] = None
) -> Result:
    """Process user intent through orchestrator."""
    pass

# Bad - no type hints
def process_intent(intent, context=None):
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def evaluate_rule(self, rule_id: str, intent: str) -> RuleResult:
    """Evaluate a governance rule against an intent.
    
    Args:
        rule_id: Unique identifier for the rule (e.g., "CORE-001")
        intent: User's intent to evaluate
        
    Returns:
        RuleResult containing pass/fail and optional violation details
        
    Raises:
        RuleNotFoundError: If rule_id does not exist
        GovernanceError: If evaluation fails
        
    Example:
        >>> result = engine.evaluate_rule("CORE-001", "delete production data")
        >>> print(result.passed)
        False
    """
    pass
```

#### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Module** | lowercase_underscore | `orchestrator_base.py` |
| **Class** | PascalCase | `OrchestratorBase` |
| **Function** | lowercase_underscore | `evaluate_rule()` |
| **Constant** | UPPERCASE | `MAX_RETRIES = 3` |
| **Private** | _leading_underscore | `_internal_method()` |

#### Project-Specific Conventions

```python
# Always use dataclasses for structured data
from dataclasses import dataclass, field

@dataclass
class OrchestratorResult:
    status: str
    data: Dict[str, Any] = field(default_factory=dict)
    
# Use async/await for I/O operations
async def query_knowledge(self, query: str) -> KnowledgeResult:
    return await self.domain_brain.search(query)
    
# Use context managers for resources
async with transaction() as txn:
    # ... perform operations
    txn.commit()
```

### YAML Style Guide

For configuration files:

```yaml
# Use 2-space indentation
orchestrators:
  master:
    max_turns: 10
    timeout: 30.0
    
# Use lowercase with underscores
governance:
  tier: 0
  audit_enabled: true
  
# Quote strings with special characters
paths:
  database: "/path/to/governance.db"
  
# Use explicit booleans
features:
  mcp_enabled: true  # Not: yes, on, 1
```

---

## Testing Requirements

### Test Coverage

All contributions must maintain or improve test coverage:

- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical paths**: 100% coverage (governance, audit)

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_orchestrator.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v -m integration

# Run fast tests (skip slow)
pytest tests/ -v -m "not slow"
```

### Writing Tests

#### Unit Tests

```python
"""Unit tests for GovernanceEngine."""

import pytest
from src.core.governance import GovernanceEngine, RuleResult


class TestGovernanceEngine:
    """Test suite for GovernanceEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        engine = GovernanceEngine()
        engine.load_rules()
        return engine
    
    def test_evaluate_safe_operation(self, engine):
        """Test that safe operations pass governance."""
        result = engine.evaluate_rule(
            rule_id="CORE-001",
            intent="list files in directory"
        )
        
        assert result.passed is True
        assert result.violation is None
    
    def test_evaluate_unsafe_operation(self, engine):
        """Test that unsafe operations are blocked."""
        result = engine.evaluate_rule(
            rule_id="CORE-001",
            intent="delete production database"
        )
        
        assert result.passed is False
        assert result.violation is not None
        assert "CORE-001" in result.violation.rule_id
```

#### Integration Tests

```python
"""Integration tests for full orchestration flow."""

import pytest


@pytest.mark.integration
class TestOrchestrationFlow:
    """Test complete orchestration pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_flow_with_governance(self):
        """Test intent → LENS → governance → execution."""
        orchestrator = MasterOrchestrator()
        await orchestrator.initialize()
        
        result = await orchestrator.process(
            intent="Analyze repository for security issues",
            context={"repo_url": "https://github.com/example/repo"}
        )
        
        assert result.status == "success"
        assert "security_issues" in result.data
        assert len(result.audit_entries) > 0
```

#### Mocking External Dependencies

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_domain_brain():
    """Mock Domain Brain for testing."""
    brain = MagicMock()
    brain.search = AsyncMock(return_value=KnowledgeResult(
        items=[{"key": "value"}],
        confidence=0.95
    ))
    return brain

async def test_with_mock(mock_domain_brain):
    """Test orchestrator with mocked dependencies."""
    orchestrator = MyOrchestrator(domain_brain=mock_domain_brain)
    
    result = await orchestrator.process("test intent")
    
    mock_domain_brain.search.assert_called_once()
```

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_orchestrator.py
│   ├── test_governance.py
│   └── test_lens.py
├── integration/             # Integration tests
│   ├── test_full_flow.py
│   └── test_api.py
└── fixtures/                # Test data
    ├── sample_rules.yaml
    └── test_knowledge.json
```

---

## Documentation Requirements

### What Needs Documentation

Every code contribution should include:

1. **Inline comments** for complex logic
2. **Docstrings** for all public classes and methods
3. **Type hints** for all function signatures
4. **README updates** if adding new components
5. **User documentation** for user-facing features
6. **API documentation** for new endpoints/tools

### Documentation Structure

```markdown
# Component Name

**Last Updated:** 2026-01-20
**Version:** 1.0.0
**Status:** Production Ready
**Audience:** Target users

## Overview

Brief description of the component.

## Usage

### Basic Example

\`\`\`python
# Code example
\`\`\`

### Advanced Usage

More complex examples.

## Configuration

Configuration options.

## Related Documents

Links to related documentation.
```

### Updating Existing Documentation

When making changes:

```bash
# Find relevant documentation
grep -r "OrchestratorBase" docs/

# Update all references
# Update last modified date
# Test all code examples
# Update cross-references
```

---

## Pull Request Process

### Before Submitting

**Checklist:**

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch rebased on latest main
- [ ] No merge conflicts

### Creating a Pull Request

1. **Push your branch:**
```bash
git push origin feature/your-feature-name
```

2. **Open PR on GitHub:**
- Use descriptive title: `feat(component): add new capability`
- Fill out PR template completely
- Link related issues: `Fixes #123`, `Relates to #456`
- Add appropriate labels

3. **PR Template:**

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe how you tested this:
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Related Issues

Fixes #123
Relates to #456
```

### PR Title Format

```
<type>(<scope>): <description>

Examples:
feat(orchestrator): add PostgreSQL backend support
fix(governance): resolve rule evaluation deadlock
docs(api): update MCP protocol specification
test(lens): add integration tests for comprehension
```

---

## Review Process

### What Reviewers Look For

1. **Code Quality**
   - Follows style guidelines
   - Well-structured and readable
   - No code smells or anti-patterns

2. **Functionality**
   - Solves the stated problem
   - No unintended side effects
   - Edge cases handled

3. **Testing**
   - Adequate test coverage
   - Tests are meaningful
   - Tests pass consistently

4. **Documentation**
   - Clear and complete
   - Examples work correctly
   - Cross-references accurate

5. **Security**
   - No security vulnerabilities
   - Input validation present
   - Sensitive data protected

### Responding to Reviews

```markdown
# Good responses
"Good catch! I've updated the validation logic in commit abc123."
"I added tests for that edge case in commit def456."
"That's a great suggestion. I'll refactor this in the next commit."

# Address all comments
"Resolved" or "Fixed in abc123"

# If you disagree, explain why
"I kept the current approach because [reason]. What do you think?"
```

### Review Turnaround

- **Initial review**: Within 2 business days
- **Follow-up review**: Within 1 business day
- **Final approval**: When all feedback addressed

---

## Release Process

### Version Numbering

CORTEX uses [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features, backwards compatible
- **Patch** (1.0.X): Bug fixes, backwards compatible

### Release Workflow

1. **Feature Freeze**: No new features, only bug fixes
2. **Release Branch**: Create `release/vX.Y.0`
3. **Testing**: Comprehensive testing on release branch
4. **Documentation**: Update changelog, migration guides
5. **Tagging**: Tag release with `vX.Y.0`
6. **Deployment**: Deploy to production
7. **Announcement**: Announce release

### Changelog Format

```markdown
## Version X.Y.0 (2026-MM-DD)

### Features
- New feature description (#PR)

### Bug Fixes
- Bug fix description (#PR)

### Breaking Changes
- Breaking change description (#PR)
- Migration path: ...

### Deprecations
- Deprecated feature (#PR)
- Removal planned for: vX.Y.0
```

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, show & tell
- **Pull Requests**: Code contributions

### Getting Help

1. Check [FAQ](../05-reference/faq.md)
2. Search existing GitHub issues
3. Read [Troubleshooting Guide](../01-getting-started/3-troubleshooting.md)
4. Open a new issue with details

### Reporting Bugs

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command: `cortex orchestrator run ...`
2. See error: ...

**Expected behavior**
What should happen instead.

**Environment**
- CORTEX version: 1.0.0
- Python version: 3.11.4
- OS: macOS 14.2

**Additional context**
Any other relevant information.
```

### Suggesting Features

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Clear description of desired behavior.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other relevant information.
```

---

## Recognition

Contributors are recognized in:

- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing to CORTEX! 🎉

---

**Next Steps:**

1. [Development Setup](2-development-setup.md) - Detailed development environment setup
2. [Testing Strategy](3-testing-strategy.md) - Comprehensive testing approach
3. [Architecture Guidelines](4-architecture-guidelines.md) - Architectural decision guidance
4. [Pull Request Process](5-pull-request-process.md) - Detailed PR workflow
