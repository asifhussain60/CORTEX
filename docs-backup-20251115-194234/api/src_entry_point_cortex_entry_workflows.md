# src.entry_point.cortex_entry_workflows

CORTEX Entry Point Integration with Workflow Pipeline

Shows how to integrate the Workflow Pipeline System with the existing
CORTEX entry point and router.

Author: CORTEX Development Team
Version: 1.0

## Functions

### `process_with_workflow(user_message, workflow_id)`

Quick helper to process request with workflow

Args:
    user_message: User's request
    workflow_id: Optional workflow to use

Returns:
    Response string

Example:
    >>> result = process_with_workflow(
    ...     "Add authentication to login page",
    ...     workflow_id="secure_feature_creation"
    ... )
    >>> print(result)
    ✅ Workflow completed successfully
    Duration: 5.8s
    Stages: 8/8 succeeded
    ...
