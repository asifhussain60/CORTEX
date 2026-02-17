"""
Finance Domain Implementation.
"""


class FinanceDomain:
    """Finance domain implementation."""

    def __init__(self) -> None:
        """Initialize finance domain."""
        self.domain_type = "finance"
        self.capabilities = [
            "budgeting",
            "forecasting",
            "reporting"
        ]

    def get_type(self) -> str:
        """Get domain type."""
        return self.domain_type

    def get_capabilities(self) -> list[str]:
        """Get finance capabilities."""
        return self.capabilities
