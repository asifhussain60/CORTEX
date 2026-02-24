"""COMPAT shim — cortex.core.intelligence moved to cortex.intelligence (Phase 60)."""
from cortex.intelligence.ast_intelligence import *  # noqa: F401, F403
from cortex.intelligence.author_context import *  # noqa: F401, F403
from cortex.intelligence.call_graph import *  # noqa: F401, F403
from cortex.intelligence.change_frequency import *  # noqa: F401, F403
from cortex.intelligence.comment_analyzer import *  # noqa: F401, F403
from cortex.intelligence.dependency_mapper import *  # noqa: F401, F403
from cortex.intelligence.duration_intelligence import *  # noqa: F401, F403
from cortex.intelligence.error_intelligence import *  # noqa: F401, F403
from cortex.intelligence.pattern_detector import *  # noqa: F401, F403
from cortex.intelligence.relationship_traversal import *  # noqa: F401, F403
from cortex.intelligence.routing_intelligence import *  # noqa: F401, F403
