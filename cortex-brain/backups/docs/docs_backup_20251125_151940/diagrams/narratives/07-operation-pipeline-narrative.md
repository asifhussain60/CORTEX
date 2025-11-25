# CORTEX Operation Pipeline

This diagram shows the standard flow for executing any CORTEX operation.

**Request** arrives with operation type and parameters.

**Validate** checks preconditions (files exist, permissions granted, dependencies available).

**Execute** runs the operation with progress tracking and error handling.

**Report** generates structured results with success/failure status and detailed output.

This pipeline pattern ensures consistency across all operations - whether importing conversations, generating documentation, or crawling databases. Every operation follows the same validate → execute → report cycle for reliability.