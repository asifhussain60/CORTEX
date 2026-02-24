# COMPAT shim — cortex.core.state.optimistic_lock → cortex.core.common.optimistic_lock
# Retained: 2026-02-24 (Phase 68-B) | Expires: 2026-05-24
from cortex.core.common.optimistic_lock import (  # noqa: F401
    MergeStrategy,
    VersionedRow,
    OptimisticLockMetrics,
    OptimisticLockManager,
    ConflictError,
    StaleDataError,
    NotFoundError,
    add_version_column,
)
try:
    from cortex.core.common.optimistic_lock import OptimisticLock  # noqa: F401
except ImportError:
    pass
