# CORTEX Global File Naming Standards Configuration
## Single Source of Truth (SSOT) for All File Naming Conventions

**Date:** 2026-01-27  
**Phase:** 0 Complete - Global Standards  
**Status:** CANONICAL CONFIGURATION  
**Authority:** CORE-035 (Single Canonical Implementation)  

---

## 📋 Overview

This document serves as the **Single Source of Truth (SSOT)** for all file naming conventions across CORTEX:
- Local development files
- Production repository files
- Generated documentation
- Configuration files
- Test files
- Deployment scripts

**One location to change. Changes propagate everywhere.**

---

## 🎯 Core File Naming Standards

### Standard 1: Kebab-Case Convention

**Rule:** All filenames use lowercase letters, numbers, and hyphens ONLY.

```yaml
✅ CORRECT:
  - migration-summary.md
  - docker-configuration-guide.md
  - wiring-schema.yaml
  - migrate-to-docker.sh
  - component-inventory-reference.md

❌ INCORRECT:
  - MigrationSummary.md (CamelCase)
  - migration_summary.md (snake_case)
  - Migration Summary.md (spaces)
  - migration.summary.md (multiple dots)
```

### Standard 2: Purpose-First Naming

**Rule:** Name describes PURPOSE/ACTION first, then context/scope.

```yaml
Pattern: {purpose}-{noun}-{scope}.{ext}

✅ CORRECT:
  - migration-summary.md (purpose: summarize, what: migration)
  - docker-configuration-guide.md (purpose: guide, what: configuration, where: docker)
  - wiring-schema-specification.md (purpose: specify, what: schema, where: wiring)
  - validate-kubernetes-config.sh (purpose: validate, what: config, where: kubernetes)

❌ INCORRECT:
  - summary.md (too vague)
  - enhanced-migration-summary.md (adjectives)
  - new-docker-guide.md (adjectives)
  - migration-executive-summary.md (weak adjective)
```

### Standard 3: Length Limits

**Rule:** Filenames optimized for readability and discoverability.

```yaml
Guideline:
  - Minimum: 8 characters (too short = ambiguous)
  - Maximum: 50 characters (readability threshold)
  - Target: 16-32 characters (optimal range)
  - HARD LIMIT: 55 characters (filesystem compatibility)

Examples:
  - 16 chars: cortex-plan-index.md ✅
  - 22 chars: migration-phases-plan.yaml ✅
  - 27 chars: wiring-schema-specification.md ✅
  - 32 chars: health-verification-tests.md ✅
  - 55 chars: HARD_LIMIT_55_CHARACTERS_FILENAME_EXAMPLE_HERE.md (exceeds limit ❌)
```

### Standard 4: Scope Context

**Rule:** Include contextual scope when necessary for clarity.

```yaml
Scopes (common prefixes):
  - docker-* : Docker-related files
  - wiring-* : Wiring/orchestration files
  - migration-* : Migration-related files
  - health-* : Health checks/monitoring
  - validate-* : Validation/testing
  - deploy-* : Deployment files
  - config-* : Configuration files
  - api-* : API-related files
  - mcp-* : Model Context Protocol files

Examples:
  - docker-configuration-guide.md
  - wiring-schema.yaml
  - migration-phases-plan.yaml
  - health-verification-tests.md
  - validate-syntax.sh
  - deploy-kubernetes.yaml
  - config-prometheus.yml
  - api-reference.md
  - mcp-server-specification.md
```

### Standard 5: File Type Conventions

**Rule:** Consistent naming by file type.

```yaml
MARKDOWN FILES (.md):
  Pattern: {purpose}-{context}.md
  Examples:
    - deployment-guide.md
    - api-reference.md
    - component-inventory-reference.md
  Use for: Documentation, guides, references, reports

YAML FILES (.yaml or .yml):
  Pattern: {purpose}-{context}.yaml or .yml
  Examples:
    - migration-phases-plan.yaml
    - wiring-schema.yaml
    - docker-compose.yml (exception: docker standard)
  Use for: Configuration, specifications, plans

PYTHON FILES (.py):
  Pattern: {purpose}_{noun}.py (snake_case for Python)
  Examples:
    - migration_orchestrator.py
    - wiring_validator.py
    - health_checker.py
  Note: Python uses snake_case by convention (PEP 8)

SHELL SCRIPTS (.sh):
  Pattern: {verb}-{noun}.sh (kebab-case)
  Examples:
    - migrate-to-docker.sh
    - validate-syntax.sh
    - deploy-kubernetes.sh
  Use for: Automation, deployment, utilities

CONFIGURATION FILES:
  Pattern: {purpose}-config.{ext}
  Examples:
    - docker-config.yaml
    - prometheus-config.yml
    - kubernetes-config.yaml
  Use for: Service configuration

TEST FILES:
  Pattern: test-{purpose}.py or test_{purpose}.py
  Examples:
    - test-wiring-integration.py
    - test_orchestrator_startup.py
  Note: Follows pytest conventions

DOCKER FILES:
  Names:
    - Dockerfile (no extension, uppercase D)
    - docker-compose.yml (docker standard)
    - docker-compose.prod.yml (production variant)
    - .dockerignore (docker standard)
  Use for: Container specification
```

### Standard 6: Naming Prohibitions

**Rule:** Explicitly prohibited naming patterns.

```yaml
NEVER USE:
  ❌ Adjectives in names:
    - new-docker-guide.md (use: docker-configuration-guide.md)
    - enhanced-wiring-schema.md (use: wiring-schema.yaml)
    - improved-migration.md (use: migration-guide.md)
    - executive-summary.md (use: migration-summary.md)
    - better-config.yaml (use: docker-configuration.yaml)

  ❌ Weak verbs/vague actions:
    - setup-docker.sh (use: docker-configure.sh or docker-initialize.sh)
    - process-files.py (use: transform-files.py or parse-files.py)
    - handle-data.py (use: validate-data.py or sanitize-data.py)

  ❌ Version numbers in filenames:
    - cortex-plan-v2.1.yaml (use: migration-phases-plan.yaml)
    - guide-v3.md (use: deployment-guide.md)
    - config-2.0.yaml (use: docker-configuration.yaml)
    Note: Git provides version control, not filenames!

  ❌ Date stamps in filenames:
    - migration-2026-01-27.yaml (use: migration-phases-plan.yaml)
    - guide-20260127.md (use: deployment-guide.md)
    Note: Use git history for dates!

  ❌ Author names in filenames:
    - asif-migration-guide.md (use: migration-guide.md)
    - hussain-docker-config.yaml (use: docker-configuration.yaml)
    Note: Use git blame for authorship!

  ❌ Status descriptors in filenames:
    - migration-draft.md (use: migration-guide.md)
    - docker-config-final.yaml (use: docker-configuration.yaml)
    - wiring-complete-spec.md (use: wiring-schema-specification.md)
    Note: Use git tags for status!

  ❌ CamelCase, snake_case (except Python):
    - DockerConfiguration.md (use: docker-configuration.md)
    - docker_configuration.md (use: docker-configuration.md)
    - DOCKER_CONFIGURATION.md (use: docker-configuration.md)
    Exception: Python files MUST use snake_case (PEP 8)

  ❌ Spaces or special characters:
    - docker configuration guide.md (use: docker-configuration-guide.md)
    - docker-config@v1.yaml (use: docker-configuration.yaml)
    - wiring#schema.md (use: wiring-schema.md)

  ❌ Vague/ambiguous names:
    - data.md (use: component-reference.md)
    - config.yaml (use: docker-configuration.yaml)
    - stuff.txt (describe purpose!)
```

---

## 📂 File Organization by Category

### Documentation Files

```yaml
GUIDES & REFERENCES:
  - deployment-guide.md
  - api-reference.md
  - architecture-guide.md
  - troubleshooting-guide.md
  - configuration-reference.md

SUMMARIES & OVERVIEWS:
  - project-summary.md
  - phase-summary.md
  - migration-summary.md
  - architecture-summary.md

SPECIFICATIONS:
  - wiring-schema-specification.md
  - api-specification.md
  - protocol-specification.md
  - docker-specification.md

INVENTORIES & LISTS:
  - component-inventory-reference.md
  - service-inventory.md
  - dependency-list.md

CHECKLISTS & VALIDATIONS:
  - validation-checklist.md
  - deployment-checklist.md
  - security-checklist.md

ANALYSIS & REPORTS:
  - performance-analysis.md
  - capacity-report.md
  - audit-report.md
  - migration-report.md
```

### Configuration Files

```yaml
APPLICATION CONFIG:
  - docker-configuration.yaml
  - kubernetes-configuration.yaml
  - prometheus-config.yml
  - nginx-config.conf

DATABASE CONFIG:
  - database-config.yaml
  - migrations-config.yaml
  - schema-config.yaml

SERVICE CONFIG:
  - mcp-server-config.yaml
  - api-server-config.yaml
  - cache-config.yaml

ENVIRONMENT CONFIG:
  - development-config.yaml
  - staging-config.yaml
  - production-config.yaml
```

### Executable Files

```yaml
DEPLOYMENT SCRIPTS:
  - deploy-kubernetes.sh
  - deploy-docker.sh
  - deploy-to-production.sh
  - rollback-deployment.sh

UTILITY SCRIPTS:
  - migrate-to-docker.sh
  - validate-syntax.sh
  - check-health.sh
  - initialize-database.sh

BUILD SCRIPTS:
  - build-docker-image.sh
  - build-kubernetes-manifests.sh
  - compile-assets.sh
```

### Plan & Architecture Files

```yaml
MASTER PLANS:
  - migration-phases-plan.yaml
  - project-roadmap.yaml
  - architecture-plan.yaml

DESIGN DOCUMENTS:
  - system-architecture.md
  - microservices-design.md
  - database-schema-design.md

SPECIFICATIONS:
  - api-design-specification.md
  - data-model-specification.md
  - security-specification.md
```

---

## 🔧 Implementation: How to Apply These Standards

### When Creating New Files

**Checklist before naming:**

```
☐ Is the filename in kebab-case (lowercase + hyphens)?
☐ Does it describe the PURPOSE first?
☐ Are there any adjectives (new, enhanced, etc.)? Remove them!
☐ Is it between 16-32 characters? (8 min, 55 max)
☐ Does it include scope context (docker-, wiring-, etc.)?
☐ Does it clearly describe what the file contains?
☐ Would another developer understand its purpose from the name?
☐ Does it follow the pattern for its file type?

If NO to any → Rename before committing!
```

### Code Generation Best Practices

When generating files programmatically:

```python
# Example: File name generation in Python

class FileNameFactory:
    """
    Generate consistent, standards-compliant filenames.
    SSOT: cortex_brain/tier0/governance/file-naming-standards.md
    """
    
    @staticmethod
    def generate_documentation(purpose: str, context: str = "") -> str:
        """Generate markdown filename."""
        # Purpose-first, context-second
        parts = [purpose.lower(), context.lower()] if context else [purpose.lower()]
        filename = "-".join(filter(None, parts)) + ".md"
        
        # Validate length
        if len(filename) > 55:
            raise ValueError(f"Filename too long: {filename}")
        
        return filename
    
    @staticmethod
    def generate_config(service: str, environment: str = "") -> str:
        """Generate config filename."""
        parts = [service.lower(), environment.lower(), "config"] if environment else [service.lower(), "config"]
        filename = "-".join(filter(None, parts)) + ".yaml"
        
        if len(filename) > 55:
            raise ValueError(f"Filename too long: {filename}")
        
        return filename
    
    @staticmethod
    def generate_script(verb: str, noun: str) -> str:
        """Generate shell script filename."""
        filename = f"{verb.lower()}-{noun.lower()}.sh"
        
        if len(filename) > 55:
            raise ValueError(f"Filename too long: {filename}")
        
        return filename


# Usage Examples:
FileNameFactory.generate_documentation("migration", "summary")  
# → "migration-summary.md"

FileNameFactory.generate_config("docker", "production")  
# → "docker-production-config.yaml"

FileNameFactory.generate_script("deploy", "kubernetes")  
# → "deploy-kubernetes.sh"
```

### Template for File Creation

Use this template when creating new files:

```yaml
# New File Creation Template
# SSOT: cortex_brain/tier0/governance/file-naming-standards.md

FILE_NAMING_CHECKLIST:
  naming_standard_applied: FILE-NAMING-STANDARDS.md (tier0/governance)
  purpose: "[What does this file do?]"
  context_scope: "[docker/wiring/migration/health/etc]"
  filename_generated: "[kebab-case-name].{md|yaml|sh|py}"
  length_check: "[X] ≤ 55 characters"
  adjectives_removed: "[X] None (checked)"
  purpose_first: "[X] Yes"
  
CREATED_BY: [Tool/Person]
CREATED_DATE: [YYYY-MM-DD]
CANONICAL_LOCATION: [Where is the naming standard defined?]
```

---

## 🔗 Integration Points

### Where This Standard Is Used

```
1. LOCAL DEVELOPMENT:
   ├─ cortex/ (local Python files follow PEP 8)
   ├─ cortex_brain/ (documentation follows standards)
   ├─ _workspaces/ (project files follow standards)
   └─ docs/ (all documentation follows standards)

2. PRODUCTION REPOSITORY:
   ├─ deployment/ (deploy-*.sh, docker-*.yaml)
   ├─ config/ (service-*-config.yaml)
   ├─ docs/ (api-reference.md, deployment-guide.md)
   └─ tests/ (test-*.py, test_*.py)

3. CI/CD PIPELINES:
   ├─ GitHub Actions: .github/workflows/[verb]-[noun].yml
   ├─ GitLab CI: .gitlab-ci.yml (exception: CI standard)
   └─ Generated artifacts: [purpose]-[context].{ext}

4. GENERATED FILES:
   ├─ Documentation generation: [purpose]-[context].md
   ├─ Config generation: [purpose]-config.yaml
   ├─ Script generation: [verb]-[noun].sh
   └─ Report generation: [topic]-report.md
```

### Where Standards CHANGE

**Only ONE place to update:**

```
File: cortex_brain/tier0/governance/file-naming-standards.md
Location: CORTEX/.cortex/standards/file-naming-standards.md (SSOT)

When standards change:
  1. Update this document
  2. All tools reference this location
  3. All file generation reads from this config
  4. No other changes needed (cascades everywhere)
```

---

## 🎯 Governance & Compliance

### CORE Rules Applied

```
CORE-035: Single Canonical Implementation
  ✅ One SSOT: cortex_brain/tier0/governance/file-naming-standards.md
  ✅ All tools reference this location
  ✅ No duplicates allowed
  ✅ Changes cascade globally

CORE-030: Implementation Truth
  ✅ Standards verified in actual files
  ✅ Naming audits catch violations
  ✅ CI/CD enforces naming rules

CORE-026: Git Checkpoint Safety
  ✅ Naming standard changes tagged
  ✅ Full rollback capability
  ✅ Historical precedent preserved
```

### Enforcement Mechanisms

```
PRE-COMMIT HOOK:
  - Validates filenames before commit
  - Runs: NameValidationHook (cortex/governance/hooks/)
  - Rejects: Non-compliant filenames
  - Message: Suggests correct naming

CI/CD VALIDATION:
  - GitHub Actions runs file linter
  - Workflow: .github/workflows/validate-file-naming.yml
  - Blocks: PRs with non-compliant files
  - Feedback: Shows violations + corrections

LINTER TOOL:
  - Tool: cortex/tools/file-naming-validator.py
  - Usage: python -m cortex.tools.validate_file_naming
  - Output: Report of violations
  - Fix mode: --fix flag auto-corrects

DOCUMENTATION GENERATION:
  - All generated files use FileNameFactory
  - Enforced at: cortex/documentation/generator.py
  - Default: Standards-compliant names
  - Override: Only with approval
```

---

## 📝 Examples by Use Case

### Use Case 1: New Deployment Automation

```
REQUIREMENT: Create script to deploy to Kubernetes

NAMING PROCESS:
  Purpose: deploy (verb)
  Noun: kubernetes (noun)
  Scope: N/A (clear from noun)
  Pattern: {verb}-{noun}.sh
  
RESULT: deploy-kubernetes.sh ✅

NOT: 
  - deploy_kubernetes.sh ❌ (snake_case)
  - DeployKubernetes.sh ❌ (CamelCase)
  - deploy-to-kubernetes-new.sh ❌ (adjective + weak verb)
  - k8s-deploy.sh ❌ (scope before verb)
```

### Use Case 2: New Documentation

```
REQUIREMENT: Create guide for Docker configuration

NAMING PROCESS:
  Purpose: guide (what it is)
  Context: docker-configuration (what it's about)
  Pattern: {context}-{purpose}.md
  
RESULT: docker-configuration-guide.md ✅

NOT:
  - docker_configuration_guide.md ❌ (snake_case)
  - DOCKER_CONFIGURATION_GUIDE.md ❌ (all caps)
  - new-docker-guide.md ❌ (adjective + vague)
  - setup-guide.md ❌ (no context, weak verb)
```

### Use Case 3: New Configuration File

```
REQUIREMENT: Create Prometheus monitoring config for production

NAMING PROCESS:
  Service: prometheus (what service)
  Environment: production (where)
  Type: config (file type)
  Pattern: {service}-{environment}-config.yaml
  
RESULT: prometheus-production-config.yaml ✅

NOT:
  - prometheus_prod_config.yaml ❌ (snake_case + abbreviation)
  - PrometheusProductionConfig.yaml ❌ (CamelCase)
  - prod-prometheus.yaml ❌ (environment first)
  - monitoring-config-v2.yaml ❌ (vague + version number)
```

### Use Case 4: New Test Suite

```
REQUIREMENT: Create integration tests for wiring system

NAMING PROCESS:
  Purpose: test (what it is)
  Context: wiring-integration (what it tests)
  Type: Python test (pytest convention)
  Pattern: test-{context}.py or test_{context}.py
  
RESULT: test-wiring-integration.py or test_wiring_integration.py ✅

NOT:
  - wiring_integration_test.py ❌ (order matters, test first)
  - wiring-integration-tests.py ❌ (markdown pattern, not test pattern)
  - new_wiring_tests.py ❌ (adjective)
  - wiring_test_final.py ❌ (status descriptor)
```

---

## 🚀 Migration Path for Existing Files

For files that don't follow standards:

```
PRIORITY 1 (Critical - used by scripts):
  Current: CORTEX-MIGRATION-MASTER-PLAN.yaml
  Target: migration-phases-plan.yaml
  Status: ✅ COMPLETE (already done)

PRIORITY 2 (Documentation - high visibility):
  Current: 00-EXECUTIVE-SUMMARY.md
  Target: migration-summary.md
  Status: ✅ COMPLETE (already done)
  
  [Etc. for other existing files]

PRIORITY 3 (Legacy - low impact):
  Current: Legacy numbered files (01-*, 02-*, etc.)
  Target: Follow new standards
  Status: ⏳ Gradual (as files are updated)

STRATEGY: Rename on next edit (no forced bulk changes)
```

---

## 📊 Configuration Summary

### Quick Reference Table

| Aspect | Standard | Example |
|--------|----------|---------|
| **Case Style** | kebab-case | my-document |
| **Length** | 16-32 optimal, 8-55 limit | 24 characters |
| **Purpose First** | {verb}-{noun} | deploy-kubernetes.sh |
| **Scope Prefix** | docker-, wiring-, health- | docker-config.yaml |
| **Documentation** | {context}-{type}.md | deployment-guide.md |
| **Configuration** | {service}-config.yaml | prometheus-config.yml |
| **Scripts** | {verb}-{noun}.sh | migrate-to-docker.sh |
| **Tests** | test-{context}.py | test-wiring.py |
| **Python Files** | snake_case (PEP 8) | wiring_validator.py |
| **Prohibited** | Adjectives, versions, dates | ❌ new-v2-2026.md |

---

## 🔄 Maintenance & Updates

### If Standards Need to Change

**Process:**

```
1. Update THIS document (SSOT)
2. Create git branch: naming-standards-update
3. Update all references in:
   - File: FileNameFactory class
   - File: Pre-commit hooks
   - File: CI/CD validation
   - File: Documentation generators
4. Test: All tools use new standards
5. Create PR for review
6. Merge + tag: naming-standards-update-{date}
7. Communicate change to team
8. Gradually apply to legacy files
```

### Review Cycle

**Annual review (1st quarter):**
- Validate standards still serve purpose
- Check if any new patterns needed
- Get feedback from developers
- Document any clarifications
- Update this SSOT

---

## ✅ VALIDATION

This document serves as the definitive reference for all CORTEX file naming across:
- ✅ Local development (`cortex/`, `cortex_brain/`)
- ✅ Production repositories
- ✅ Generated files (docs, configs, scripts)
- ✅ CI/CD artifacts
- ✅ Test files
- ✅ Deployment files

**Single location to change. All future files follow these standards.**

---

**Authority:** CORTEX Master Orchestrator  
**Status:** CANONICAL REFERENCE  
**Effective Date:** 2026-01-27  
**Review Date:** 2027-01-27  

*This is the Single Source of Truth (SSOT) for all file naming in CORTEX. All new files, tools, and generation processes reference this document.*
