"""
Plan Metadata extraction system.

Extracts YAML frontmatter from Markdown plan files and validates required fields.
Supports multiple date formats and comprehensive field validation.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import yaml
import re


class PlanMetadataError(Exception):
    """Raised when plan metadata extraction or validation fails."""
    pass


@dataclass
class PlanMetadata:
    """
    Plan metadata extracted from YAML frontmatter.
    
    Required fields:
    - plan_id: Unique identifier (e.g., CORTEX-SETUP-001)
    - title: Human-readable plan title
    - status: Plan status (proposed, approved, in-progress, completed, cancelled)
    - priority: Priority level (low, medium, high, critical)
    - created_date: When plan was created
    - estimated_hours: Time estimate for completion
    
    Optional fields:
    - updated_date: Last modification date
    - actual_hours: Actual time spent
    - completion_percentage: 0-100 percentage complete
    - assigned_to: Person/team assigned
    - tags: List of tags for categorization
    - dependencies: List of plan IDs this depends on
    - blocked_by: List of plan IDs blocking this
    - related_plans: List of related plan IDs
    """
    plan_id: str
    title: str
    status: str
    priority: str
    created_date: datetime
    estimated_hours: int
    
    # Optional fields
    updated_date: Optional[datetime] = None
    actual_hours: Optional[int] = None
    completion_percentage: Optional[int] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    blocked_by: Optional[List[str]] = None
    related_plans: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        """Convert metadata to dictionary for serialization."""
        return asdict(self)


class PlanMetadataExtractor:
    """
    Extracts and validates plan metadata from Markdown files.
    
    Usage:
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(Path("plan.md"))
    """
    
    # Allowed values for enum fields
    VALID_STATUSES = {"proposed", "approved", "in-progress", "completed", "cancelled"}
    VALID_PRIORITIES = {"low", "medium", "high", "critical"}
    
    # Required fields that must be present
    REQUIRED_FIELDS = {"plan_id", "title", "status", "priority", "created_date", "estimated_hours"}
    
    # Regex pattern for frontmatter extraction
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    
    def extract(self, file_path: Path) -> PlanMetadata:
        """
        Extract metadata from plan file.
        
        Args:
            file_path: Path to Markdown file with YAML frontmatter
            
        Returns:
            PlanMetadata object with validated fields
            
        Raises:
            PlanMetadataError: If extraction or validation fails
        """
        # Validate file exists
        self._validate_file_exists(file_path)
        
        # Read and parse content
        content = file_path.read_text(encoding="utf-8")
        frontmatter = self._extract_frontmatter(content)
        
        if not frontmatter:
            raise PlanMetadataError(f"No YAML frontmatter found in {file_path.name}")
        
        # Parse YAML
        metadata_dict = self._parse_yaml(frontmatter, file_path)
        
        # Validate and convert
        return self._validate_and_convert(metadata_dict, file_path)
    
    def _validate_file_exists(self, file_path: Path) -> None:
        """Validate file exists."""
        if not file_path.exists():
            raise PlanMetadataError(f"File not found: {file_path}")
    
    def _extract_frontmatter(self, content: str) -> Optional[str]:
        """
        Extract YAML frontmatter from Markdown content.
        
        Looks for content between --- delimiters at start of file.
        
        Args:
            content: Full file content
            
        Returns:
            Frontmatter string or None if not found
        """
        match = self.FRONTMATTER_PATTERN.match(content)
        return match.group(1) if match else None
    
    def _parse_yaml(self, frontmatter: str, file_path: Path) -> dict:
        """Parse YAML string to dictionary."""
        try:
            return yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            raise PlanMetadataError(f"Invalid YAML in {file_path.name}: {e}")
    
    def _validate_and_convert(self, data: dict, file_path: Path) -> PlanMetadata:
        """
        Validate metadata dictionary and convert to PlanMetadata.
        
        Args:
            data: Parsed YAML dictionary
            file_path: Original file path (for error messages)
            
        Returns:
            PlanMetadata object
            
        Raises:
            PlanMetadataError: If validation fails
        """
        # Validate required fields
        self._validate_required_fields(data, file_path)
        
        # Validate enum fields
        self._validate_status(data["status"], file_path)
        self._validate_priority(data["priority"], file_path)
        
        # Validate numeric ranges
        if "completion_percentage" in data:
            self._validate_completion_percentage(data["completion_percentage"], file_path)
        
        # Parse dates
        created_date = self._parse_date(data["created_date"], "created_date", file_path)
        updated_date = self._parse_optional_date(data.get("updated_date"), "updated_date", file_path)
        
        # Create PlanMetadata object
        return PlanMetadata(
            plan_id=data["plan_id"],
            title=data["title"],
            status=data["status"],
            priority=data["priority"],
            created_date=created_date,
            estimated_hours=data["estimated_hours"],
            updated_date=updated_date,
            actual_hours=data.get("actual_hours"),
            completion_percentage=data.get("completion_percentage"),
            assigned_to=data.get("assigned_to"),
            tags=data.get("tags"),
            dependencies=data.get("dependencies"),
            blocked_by=data.get("blocked_by"),
            related_plans=data.get("related_plans")
        )
    
    def _validate_required_fields(self, data: dict, file_path: Path) -> None:
        """Validate all required fields are present."""
        missing_fields = self.REQUIRED_FIELDS - set(data.keys())
        if missing_fields:
            raise PlanMetadataError(
                f"Missing required field(s) in {file_path.name}: {', '.join(sorted(missing_fields))}"
            )
    
    def _validate_status(self, status: str, file_path: Path) -> None:
        """Validate status is a valid enum value."""
        if status not in self.VALID_STATUSES:
            raise PlanMetadataError(
                f"Invalid status '{status}' in {file_path.name}. "
                f"Must be one of: {', '.join(sorted(self.VALID_STATUSES))}"
            )
    
    def _validate_priority(self, priority: str, file_path: Path) -> None:
        """Validate priority is a valid enum value."""
        if priority not in self.VALID_PRIORITIES:
            raise PlanMetadataError(
                f"Invalid priority '{priority}' in {file_path.name}. "
                f"Must be one of: {', '.join(sorted(self.VALID_PRIORITIES))}"
            )
    
    def _validate_completion_percentage(self, completion: int, file_path: Path) -> None:
        """Validate completion percentage is in 0-100 range."""
        if not (0 <= completion <= 100):
            raise PlanMetadataError(
                f"Completion percentage must be 0-100, got {completion} in {file_path.name}"
            )
    
    def _parse_optional_date(self, date_value: any, field_name: str, file_path: Path) -> Optional[datetime]:
        """Parse optional date field."""
        if date_value is None:
            return None
        return self._parse_date(date_value, field_name, file_path)
    
    def _parse_date(self, date_value: any, field_name: str, file_path: Path) -> datetime:
        """
        Parse date from various formats.
        
        Supports:
        - datetime objects (passthrough)
        - date objects (YAML parses YYYY-MM-DD as date)
        - ISO 8601 strings: 2025-12-03T00:00:00Z
        - Date-only strings: 2025-12-03
        
        Args:
            date_value: Value to parse
            field_name: Name of field (for error messages)
            file_path: Original file path (for error messages)
            
        Returns:
            datetime object
            
        Raises:
            PlanMetadataError: If date cannot be parsed
        """
        # datetime objects
        if isinstance(date_value, datetime):
            return date_value
        
        # date objects (YAML parses 2025-12-03 as date, not datetime)
        if hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
            return datetime(date_value.year, date_value.month, date_value.day)
        
        # String formats
        if isinstance(date_value, str):
            # ISO 8601 with timezone
            if 'T' in date_value or 'Z' in date_value:
                try:
                    return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            # Date only (YYYY-MM-DD)
            try:
                return datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                pass
        
        raise PlanMetadataError(
            f"Invalid date format for {field_name} in {file_path.name}: {date_value}"
        )
