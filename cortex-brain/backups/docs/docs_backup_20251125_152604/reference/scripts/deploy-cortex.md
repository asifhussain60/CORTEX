# Deploy Cortex

**Author:** Asif Hussain  

CORTEX Automated Deployment Script
===================================

---

**Source:** `scripts/deploy_cortex.py`

## Classes

### `Colors`

### `CortexDeployer`

Automated CORTEX deployment with validation enforcement

**Methods:**

- **`deploy()`**
  Run full deployment pipeline

- **`phase0_version_management()`**
  Phase 0: Version management and consistency validation

- **`phase1_validation()`**
  Phase 1: Pre-deployment validation

- **`phase2_entry_points()`**
  Phase 2: Entry point module validation

- **`phase3_testing()`**
  Phase 3: Comprehensive test suite

- **`phase4_upgrade()`**
  Phase 4: Upgrade compatibility validation

- **`phase5_package()`**
  Phase 5: Create deployment package - PHYSICALLY CREATES PRODUCTION PACKAGE

- **`phase6_report()`**
  Phase 6: Generate deployment report

- **`check_git_clean()`**
  Check git working directory is clean

- **`check_no_uncommitted()`**
  Check no uncommitted changes

- **`check_version_file()`**
  Check VERSION file exists

- **`check_requirements()`**
  Check requirements.txt present

- **`check_brain_preservation()`**
  Check brain preservation logic exists

- **`check_migration_scripts()`**
  Check migration scripts present

- **`check_rollback_docs()`**
  Check rollback procedure documented

- **`check_gitignore_template()`**
  Check .gitignore template exists

- **`check_gist_uploader_service()`**
  Check Gist uploader service exists

- **`check_feedback_gist_integration()`**
  Check FeedbackCollector has Gist upload integration

- **`check_github_config_schema()`**
  Check cortex.config.json has GitHub section

- **`check_platform_import_resolved()`**
  Check platform import conflict resolved (tests/platform/ renamed)

- **`check_gist_upload_tests()`**
  Check Gist upload integration tests exist

- **`print_summary()`**
  Print deployment summary

## Functions

### `main()`

Run CORTEX deployment
