"""
Custom Exceptions for CORTEX Agents

Defines specific exception types for better error handling.
"""


class CortexAgentError(Exception):
    """Base exception for all CORTEX agent errors"""
    pass


class AgentNotFoundError(CortexAgentError):
    """Raised when no agent can handle a request"""
    pass


class AgentExecutionError(CortexAgentError):
    """Raised when agent execution fails"""
    pass


class InvalidRequestError(CortexAgentError):
    """Raised when agent request is malformed or invalid"""
    pass


class TierConnectionError(CortexAgentError):
    """Raised when connection to a tier (1, 2, or 3) fails"""
    pass


class AgentTimeoutError(CortexAgentError):
    """Raised when agent execution exceeds timeout"""
    pass


class InsufficientContextError(CortexAgentError):
    """Raised when agent lacks required context to proceed"""
    pass


class RuleViolationError(CortexAgentError):
    """Raised when an operation would violate governance rules"""
    pass
