"""
ENH-068 Stage 3: KPI Transparency Engine
Transparent KPI calculations with data source traceability
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DataSource:
    """
    Data source for KPI calculation
    
    Attributes:
        name: Source identifier
        path: Path to source file/data
        field: Specific field used
        timestamp: When data was retrieved
    """
    name: str
    path: Optional[Path] = None
    field: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class KPIExplanation:
    """
    Explanation of KPI calculation
    
    Attributes:
        kpi_name: Name of KPI
        value: Calculated value
        calculation_steps: Human-readable calculation steps
        data_sources: Sources used in calculation
        confidence: Confidence score (0.0-1.0)
        metadata: Additional metadata
    """
    kpi_name: str
    value: float
    calculation_steps: str
    data_sources: List[DataSource] = field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class KPITransparencyEngine:
    """
    KPI Transparency Engine
    
    Features:
    - Transparent KPI calculations
    - Data source traceability
    - Confidence scoring
    - Human-readable explanations
    """
    
    def __init__(self) -> None:
        """Initialize transparency engine"""
        self._kpi_calculators = {
            "test_coverage": self._calculate_test_coverage,
            "completion_rate": self._calculate_completion_rate,
            "simple_metric": self._calculate_simple_metric
        }
    
    def explain_kpi(self, kpi_name: str, data: Dict[str, Any]) -> KPIExplanation:
        """
        Generate explanation for KPI calculation
        
        Args:
            kpi_name: Name of KPI to explain
            data: Input data for calculation
        
        Returns:
            KPI explanation with calculation steps and sources
        """
        calculator = self._kpi_calculators.get(kpi_name)
        
        if not calculator:
            # Default calculation for unknown KPIs
            return self._calculate_simple_metric(kpi_name, data)
        
        return calculator(kpi_name, data)
    
    def _calculate_test_coverage(
        self, 
        kpi_name: str, 
        data: Dict[str, Any]
    ) -> KPIExplanation:
        """Calculate test coverage KPI"""
        tests_total = data.get("tests_total", 0)
        tests_passing = data.get("tests_passing", 0)
        
        # Calculate coverage
        if tests_total > 0:
            value = tests_passing / tests_total
        else:
            value = 0.0
        
        # Build calculation steps
        calculation_steps = (
            f"Test Coverage = tests_passing / tests_total\n"
            f"             = {tests_passing} / {tests_total}\n"
            f"             = {value:.2%}"
        )
        
        # Extract data sources
        sources = self._extract_data_sources(data, ["tests_total", "tests_passing"])
        
        # Calculate confidence
        confidence = self._calculate_confidence(data, sources)
        
        return KPIExplanation(
            kpi_name=kpi_name,
            value=value,
            calculation_steps=calculation_steps,
            data_sources=sources,
            confidence=confidence,
            metadata={"tests_total": tests_total, "tests_passing": tests_passing}
        )
    
    def _calculate_completion_rate(
        self, 
        kpi_name: str, 
        data: Dict[str, Any]
    ) -> KPIExplanation:
        """Calculate completion rate KPI"""
        phases_total = data.get("phases_total", 0)
        phases_complete = data.get("phases_complete", 0)
        
        # Calculate rate
        if phases_total > 0:
            value = phases_complete / phases_total
        else:
            value = 0.0
        
        # Build calculation steps
        calculation_steps = (
            f"Completion Rate = phases_complete / phases_total\n"
            f"                = {phases_complete} / {phases_total}\n"
            f"                = {value:.2%}"
        )
        
        # Extract data sources
        sources = self._extract_data_sources(data, ["phases_total", "phases_complete"])
        
        # Calculate confidence
        confidence = self._calculate_confidence(data, sources)
        
        return KPIExplanation(
            kpi_name=kpi_name,
            value=value,
            calculation_steps=calculation_steps,
            data_sources=sources,
            confidence=confidence,
            metadata={"phases_total": phases_total, "phases_complete": phases_complete}
        )
    
    def _calculate_simple_metric(
        self, 
        kpi_name: str, 
        data: Dict[str, Any]
    ) -> KPIExplanation:
        """Calculate simple metric KPI"""
        value = data.get("value", 0.0)
        
        calculation_steps = f"{kpi_name} = {value}"
        
        sources = self._extract_data_sources(data, ["value"])
        confidence = self._calculate_confidence(data, sources)
        
        return KPIExplanation(
            kpi_name=kpi_name,
            value=float(value),
            calculation_steps=calculation_steps,
            data_sources=sources,
            confidence=confidence
        )
    
    def _extract_data_sources(
        self, 
        data: Dict[str, Any], 
        fields: List[str]
    ) -> List[DataSource]:
        """
        Extract data sources from input data
        
        Args:
            data: Input data dictionary
            fields: Fields to extract sources for
        
        Returns:
            List of data sources
        """
        sources = []
        source_map = data.get("_sources", {})
        
        for field in fields:
            if field in source_map:
                path = source_map[field]
                sources.append(DataSource(
                    name=field,
                    path=path if isinstance(path, Path) else Path(str(path)),
                    field=field
                ))
            else:
                # No explicit source - mark as derived
                sources.append(DataSource(
                    name=field,
                    field=field
                ))
        
        return sources
    
    def _calculate_confidence(
        self, 
        data: Dict[str, Any], 
        sources: List[DataSource]
    ) -> float:
        """
        Calculate confidence score based on data quality
        
        Args:
            data: Input data
            sources: Data sources
        
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 1.0
        
        # Reduce confidence if sources not provided
        if "_sources" not in data:
            confidence *= 0.9
        else:
            # If sources provided but files don't exist, only reduce slightly
            # (sources may be references to data that exists but files aren't validated)
            missing_count = sum(1 for s in sources if s.path and not s.path.exists())
            if missing_count > 0 and missing_count == len(sources):
                # All sources missing - significant confidence reduction
                confidence *= 0.75
            elif missing_count > 0:
                # Some sources missing - minor reduction
                confidence *= 0.95
        
        return confidence
