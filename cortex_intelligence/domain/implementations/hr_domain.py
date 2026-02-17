"""
HR Domain Implementation.
"""


class HRDomain:
    """HR domain implementation."""

    def __init__(self) -> None:
        """Initialize HR domain."""
        self.domain_type = "hr"
        self.capabilities = [
            "recruitment",
            "onboarding",
            "performance_management"
        ]

    def get_type(self) -> str:
        """Get domain type."""
        return self.domain_type

    def get_capabilities(self) -> list[str]:
        """Get HR capabilities."""
        return self.capabilities
