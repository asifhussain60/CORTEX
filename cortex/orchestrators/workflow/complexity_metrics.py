"""Complexity metrics collection for operations."""

from typing import Any, Dict, Optional


class ComplexityMetrics:
    """Collects and analyzes metrics for complexity scoring."""

    # Operation type complexity factors
    OPERATION_FACTORS = {
        "read": 10,
        "write": 20,
        "api_call": 30,
        "database_query": 25,
        "api_orchestration": 40,
        "distributed_transaction": 80,
        "batch_processing": 35,
        "monitoring": 15,
        "reporting": 25,
        "data_transformation": 35,
        "workflow_execution": 50,
        "critical": 20  # Critical operations get priority reduction
    }

    def collect(
        self,
        operation_type: str,
        data_size_mb: float = 0,
        dependency_count: int = 0,
        parallel_tasks: int = 1,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Collect metrics for an operation.

        Args:
            operation_type: Type of operation
            data_size_mb: Data size in megabytes
            dependency_count: Number of dependencies
            parallel_tasks: Number of parallel tasks
            retry_count: Number of retries configured

        Returns:
            Dictionary of collected metrics
        """
        return {
            "operation_type": operation_type,
            "data_size_mb": data_size_mb,
            "dependency_count": dependency_count,
            "parallel_tasks": parallel_tasks,
            "retry_count": retry_count
        }

    def calculate_factors(
        self,
        operation_type: str,
        data_size_mb: float = 0,
        dependency_count: int = 0,
        parallel_tasks: int = 1,
        retry_count: int = 0
    ) -> Dict[str, float]:
        """Calculate complexity factors from metrics.

        Args:
            operation_type: Type of operation
            data_size_mb: Data size in megabytes
            dependency_count: Number of dependencies
            parallel_tasks: Number of parallel tasks
            retry_count: Number of retries

        Returns:
            Dictionary of factors
        """
        return {
            "operation_type_factor": self.get_operation_factor(operation_type),
            "data_size_factor": self.get_data_size_factor(data_size_mb),
            "dependency_factor": self.get_dependency_factor(dependency_count),
            "parallel_factor": self.get_parallel_factor(parallel_tasks),
            "retry_factor": self.get_retry_factor(retry_count)
        }

    def get_operation_factor(self, operation_type: str) -> float:
        """Get complexity factor for operation type.

        Args:
            operation_type: Type of operation

        Returns:
            Complexity factor (0-100 scale)
        """
        return float(self.OPERATION_FACTORS.get(operation_type, 25))

    def get_data_size_factor(self, data_size_mb: float) -> float:
        """Get complexity factor for data size.

        Args:
            data_size_mb: Data size in megabytes

        Returns:
            Complexity factor based on data size
        """
        if data_size_mb < 1:
            return 5.0
        elif data_size_mb < 10:
            return 15.0
        elif data_size_mb < 100:
            return 30.0
        elif data_size_mb < 1000:
            return 60.0
        else:
            return 90.0

    def get_dependency_factor(self, dependency_count: int) -> float:
        """Get complexity factor for dependencies.

        Args:
            dependency_count: Number of dependencies

        Returns:
            Complexity factor based on dependency count
        """
        if dependency_count <= 1:
            return 5.0
        elif dependency_count <= 3:
            return 15.0
        elif dependency_count <= 5:
            return 35.0
        elif dependency_count <= 10:
            return 65.0
        else:
            return 85.0

    def get_parallel_factor(self, parallel_tasks: int) -> float:
        """Get complexity factor for parallel execution.

        Args:
            parallel_tasks: Number of parallel tasks

        Returns:
            Complexity factor based on parallelism
        """
        if parallel_tasks <= 1:
            return 0.0
        elif parallel_tasks <= 3:
            return 20.0
        elif parallel_tasks <= 5:
            return 40.0
        elif parallel_tasks <= 10:
            return 65.0
        else:
            return 85.0

    def get_retry_factor(self, retry_count: int) -> float:
        """Get complexity factor for retry configuration.

        Args:
            retry_count: Number of retries

        Returns:
            Complexity factor based on retry count
        """
        if retry_count == 0:
            return 0.0
        elif retry_count <= 2:
            return 15.0
        elif retry_count <= 5:
            return 35.0
        else:
            return 55.0
