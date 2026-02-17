"""
Operations Domain Implementation.
"""


class OperationsDomain:
    """Operations domain implementation."""

    def __init__(self) -> None:
        """Initialize operations domain."""
        self.domain_type = "operations"
        self.capabilities = [
            "planning",
            "scheduling",
            "optimization"
        ]

    def get_type(self) -> str:
        """Get domain type."""
        return self.domain_type

    def get_capabilities(self) -> list[str]:
        """Get operations capabilities."""
        return self.capabilities
