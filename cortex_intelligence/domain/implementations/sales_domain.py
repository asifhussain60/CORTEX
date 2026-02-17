"""
Sales Domain Implementation.
"""


class SalesDomain:
    """Sales domain implementation."""

    def __init__(self) -> None:
        """Initialize sales domain."""
        self.domain_type = "sales"
        self.capabilities = [
            "opportunity_management",
            "pipeline_tracking",
            "forecasting"
        ]

    def get_type(self) -> str:
        """Get domain type."""
        return self.domain_type

    def get_capabilities(self) -> list[str]:
        """Get sales capabilities."""
        return self.capabilities
