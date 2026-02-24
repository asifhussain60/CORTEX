"""COMPAT shim — cortex.core.intent moved to cortex.orchestrators.core.intent_router (Phase 60)."""
from cortex.orchestrators.core.intent_router.challenge_generator import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.comprehension_loop import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.comprehension_yaml import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.intent_canonicalizer import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.intent_reflection_protocol import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.lens_context_builder import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.lens_response_formatter import *  # noqa: F401, F403
from cortex.orchestrators.core.intent_router.recommendation_engine import *  # noqa: F401, F403
