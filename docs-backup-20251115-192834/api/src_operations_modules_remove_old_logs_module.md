# src.operations.modules.remove_old_logs_module

Remove Old Logs Module

Deletes log files older than specified retention period.

SOLID Principles:
- Single Responsibility: Only handles old log removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
