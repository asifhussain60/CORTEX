#!/usr/bin/env python3
"""
Restore 35 Knowledge YAMLs from CORTEX-4.0 commit 6ad2094a5
Places them in cortex_brain/tier3/knowledge/ organized by domain
"""

import os
import subprocess
from pathlib import Path

# Commit hash where YAMLs were originally added
COMMIT_HASH = "6ad2094a5"

# List of all 35 knowledge YAMLs and their target paths
YAML_FILES = {
    # Cloud/Infrastructure
    "cortex-brain/knowledge/cloud/aws-best-practices.yaml": "cortex_brain/tier3/knowledge/DEPLOYMENT/aws-best-practices.yaml",

    # Database
    "cortex-brain/knowledge/database/oracle-best-practices.yaml": "cortex_brain/tier3/knowledge/DATA-MANAGEMENT/oracle-best-practices.yaml",

    # Domain-Driven Design
    "cortex-brain/knowledge/ddd/aggregates-entities.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/aggregates-entities.yaml",
    "cortex-brain/knowledge/ddd/bounded-contexts.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/bounded-contexts.yaml",
    "cortex-brain/knowledge/ddd/domain-events.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/domain-events.yaml",

    # DevOps
    "cortex-brain/knowledge/devops/cicd-pipelines.yaml": "cortex_brain/tier3/knowledge/DEPLOYMENT/cicd-pipelines.yaml",
    "cortex-brain/knowledge/devops/infrastructure-as-code.yaml": "cortex_brain/tier3/knowledge/DEPLOYMENT/infrastructure-as-code.yaml",
    "cortex-brain/knowledge/devops/monitoring-observability.yaml": "cortex_brain/tier3/knowledge/DEPLOYMENT/monitoring-observability.yaml",

    # Knowledge Curation (RAG, Embeddings)
    "cortex-brain/knowledge/domains/domain-rag-integration.yaml": "cortex_brain/tier3/knowledge/KNOWLEDGE-CURATION/domain-rag-integration.yaml",
    "cortex-brain/knowledge/domains/embeddings-strategy.yaml": "cortex_brain/tier3/knowledge/KNOWLEDGE-CURATION/embeddings-strategy.yaml",
    "cortex-brain/knowledge/domains/retrieval-pipeline.yaml": "cortex_brain/tier3/knowledge/KNOWLEDGE-CURATION/retrieval-pipeline.yaml",
    "cortex-brain/knowledge/domains/vector-database-guide.yaml": "cortex_brain/tier3/knowledge/KNOWLEDGE-CURATION/vector-database-guide.yaml",

    # Engineering/Architecture
    "cortex-brain/knowledge/engineering/anti-patterns.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/anti-patterns.yaml",
    "cortex-brain/knowledge/engineering/api-design/api-versioning.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/api-versioning.yaml",
    "cortex-brain/knowledge/engineering/api-design/graphql-best-practices.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/graphql-best-practices.yaml",
    "cortex-brain/knowledge/engineering/api-design/rest-api-design.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/rest-api-design.yaml",
    "cortex-brain/knowledge/engineering/clean-code.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/clean-code.yaml",
    "cortex-brain/knowledge/engineering/code-review.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/code-review.yaml",
    "cortex-brain/knowledge/engineering/design-patterns.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/design-patterns.yaml",
    "cortex-brain/knowledge/engineering/refactoring.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/refactoring.yaml",
    "cortex-brain/knowledge/engineering/solid-principles.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/solid-principles.yaml",

    # Frontend
    "cortex-brain/knowledge/frontend/react-best-practices.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/react-best-practices.yaml",

    # Microservices
    "cortex-brain/knowledge/microservices/resilience-patterns.yaml": "cortex_brain/tier3/knowledge/ARCHITECTURE/resilience-patterns.yaml",

    # Performance
    "cortex-brain/knowledge/performance/caching-strategies.yaml": "cortex_brain/tier3/knowledge/PERFORMANCE/caching-strategies.yaml",
    "cortex-brain/knowledge/performance/optimization-techniques.yaml": "cortex_brain/tier3/knowledge/PERFORMANCE/optimization-techniques.yaml",
    "cortex-brain/knowledge/performance/profiling-analysis.yaml": "cortex_brain/tier3/knowledge/PERFORMANCE/profiling-analysis.yaml",

    # Security
    "cortex-brain/knowledge/security/api-security-checklist.yaml": "cortex_brain/tier3/knowledge/SECURITY/api-security-checklist.yaml",
    "cortex-brain/knowledge/security/owasp-top-10.yaml": "cortex_brain/tier3/knowledge/SECURITY/owasp-top-10.yaml",
    "cortex-brain/knowledge/security/secure-coding-practices.yaml": "cortex_brain/tier3/knowledge/SECURITY/secure-coding-practices.yaml",

    # Testing/TDD
    "cortex-brain/knowledge/testing/selenium-to-playwright-migration.yaml": "cortex_brain/tier3/knowledge/TESTING-VALIDATION/selenium-to-playwright-migration.yaml",
    "cortex-brain/knowledge/testing/tdd-best-practices.yaml": "cortex_brain/tier3/knowledge/TESTING-VALIDATION/tdd-best-practices.yaml",
    "cortex-brain/knowledge/testing/test-doubles.yaml": "cortex_brain/tier3/knowledge/TESTING-VALIDATION/test-doubles.yaml",
    "cortex-brain/knowledge/testing/testing-pyramid.yaml": "cortex_brain/tier3/knowledge/TESTING-VALIDATION/testing-pyramid.yaml",

    # UI/UX
    "cortex-brain/knowledge/ui-ux/glassmorphism-design-standards.yaml": "cortex_brain/tier3/knowledge/DOCUMENTATION/glassmorphism-design-standards.yaml",
    "cortex-brain/knowledge/ui-ux/ui-ux-best-practices.yaml": "cortex_brain/tier3/knowledge/DOCUMENTATION/ui-ux-best-practices.yaml",
}

def restore_yamls():
    """Restore all 35 Knowledge YAMLs from git commit"""

    created = 0
    failed = 0

    for source_path, target_path in YAML_FILES.items():
        try:
            # Create target directory
            target_dir = Path(target_path).parent
            target_dir.mkdir(parents=True, exist_ok=True)

            # Extract file from git commit (use UTF-8 encoding)
            cmd = f'git show {COMMIT_HASH}:{source_path}'
            result = subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8', errors='replace', cwd='d:\\PROJECTS\\CORTEX')

            if result.returncode == 0:
                # Write to target location
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"✓ {target_path}")
                created += 1
            else:
                print(f"✗ Failed to extract {source_path}: {result.stderr[:100]}")
                failed += 1

        except Exception as e:
            print(f"✗ Error processing {source_path}: {str(e)[:100]}")
            failed += 1

    print(f"\n✓ Restored {created}/35 Knowledge YAMLs")
    if failed > 0:
        print(f"✗ Failed: {failed}")

    return created == 35

if __name__ == "__main__":
    if restore_yamls():
        print("\n✓ All 35 Knowledge YAMLs successfully restored!")
    else:
        print("\n✗ Some YAMLs failed to restore")
