"""
Tech Stack Mapper - Maps AST imports to knowledge categories.

Authority: Phase 54 S3 - Tech Stack Detection & Staleness Awareness
Purpose: Route detected framework imports to relevant knowledge YAMLs

Example:
  mapper = TechStackMapper()
  imports = ['fastapi', 'pydantic', 'pytest']
  categories = mapper.map_imports(imports)
  # Returns: [('fastapi', 0.95), ('pydantic', 0.90), ('pytest', 0.88)]
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ImportMapping:
    """Mapping from import name to knowledge categories."""

    import_name: str
    categories: List[str]
    confidence: float = 1.0
    description: str = ""


class TechStackMapper:
    """
    Maps Python imports to knowledge categories.

    Loads tech-stack-mapping.yaml configuration and provides
    intelligent routing of detected imports to relevant knowledge YAMLs.

    CORE Rules:
    - CORE-011: Type hints required ✅
    - CORE-012: Docstrings required ✅
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize TechStackMapper.

        Args:
            config_path: Path to tech-stack-mapping.yaml config file.
                        If None, loads from cortex/knowledge/tech-stack-mapping.yaml
        """
        self.logger = logging.getLogger(f"{__name__}.TechStackMapper")
        self.mappings: Dict[str, ImportMapping] = {}
        self.config_path = config_path

        # Load default config if not specified
        if not config_path:
            self.config_path = (
                Path(__file__).parent.parent.parent
                / "knowledge"
                / "tech-stack-mapping.yaml"
            )

        self._load_config()
        self.logger.info("AC_START: AC-PHASE54-S3-T1 | TechStackMapper initialized")

    def _load_config(self) -> None:
        """Load tech stack mapping configuration from YAML."""
        if not self.config_path.exists():
            self.logger.warning(
                f"Tech stack mapping config not found at {self.config_path}. "
                f"Using built-in defaults."
            )
            self._load_defaults()
            return

        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            if not config or "mappings" not in config:
                self.logger.warning("Invalid tech stack config format. Using defaults.")
                self._load_defaults()
                return

            # Load mappings from config
            for mapping_dict in config["mappings"]:
                import_name = mapping_dict.get("import")
                categories = mapping_dict.get("categories", [])
                confidence = mapping_dict.get("confidence", 1.0)
                description = mapping_dict.get("description", "")

                if import_name:
                    self.mappings[import_name] = ImportMapping(
                        import_name=import_name,
                        categories=categories,
                        confidence=confidence,
                        description=description,
                    )

            self.logger.info(
                f"Loaded {len(self.mappings)} import mappings from config"
            )

        except Exception as e:
            self.logger.error(f"Failed to load tech stack config: {e}")
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load built-in default mappings."""
        defaults = [
            ImportMapping("fastapi", ["fastapi", "python-web", "rest-api", "async"], 0.95),
            ImportMapping("flask", ["flask", "python-web", "rest-api"], 0.95),
            ImportMapping("django", ["django", "python-web", "rest-api", "orm"], 0.95),
            ImportMapping("pydantic", ["pydantic", "validation", "serialization"], 0.90),
            ImportMapping("sqlalchemy", ["sqlalchemy", "database", "orm"], 0.95),
            ImportMapping("pytest", ["pytest", "testing", "tdd"], 0.95),
            ImportMapping("unittest", ["unittest", "testing", "tdd"], 0.90),
            ImportMapping("asyncio", ["asyncio", "async", "concurrency"], 0.90),
            ImportMapping("celery", ["celery", "task-queue", "async"], 0.90),
            ImportMapping("redis", ["redis", "cache", "message-queue"], 0.90),
            ImportMapping("postgres", ["postgres", "database", "sql"], 0.85),
            ImportMapping("mongodb", ["mongodb", "database", "nosql"], 0.85),
            ImportMapping("docker", ["docker", "containers", "devops"], 0.85),
            ImportMapping("kubernetes", ["kubernetes", "orchestration", "devops"], 0.85),
            ImportMapping("requests", ["requests", "http", "api-client"], 0.90),
            ImportMapping("boto3", ["boto3", "aws", "cloud"], 0.90),
            ImportMapping("typing", ["typing", "type-hints"], 0.95),
            ImportMapping("logging", ["logging", "observability"], 0.90),
        ]

        for mapping in defaults:
            self.mappings[mapping.import_name] = mapping

        self.logger.info(f"Loaded {len(defaults)} default tech stack mappings")

    def map_imports(self, imports: List[str]) -> List[Tuple[str, List[str], float]]:
        """
        Map detected imports to knowledge categories.

        Args:
            imports: List of import names (e.g., ['fastapi', 'pydantic'])

        Returns:
            List of tuples: (import_name, categories, confidence)
            Example: [('fastapi', ['fastapi', 'rest-api'], 0.95), ...]
        """
        result = []

        for imp in imports:
            # Exact match
            if imp in self.mappings:
                mapping = self.mappings[imp]
                result.append(
                    (imp, mapping.categories, mapping.confidence)
                )
                continue

            # Fuzzy match: partial import paths
            # e.g., 'from fastapi.security' → match 'fastapi'
            for base_import in self.mappings:
                if imp.startswith(base_import + ".") or imp.startswith(
                    base_import + "."
                ):
                    mapping = self.mappings[base_import]
                    # Slightly lower confidence for partial matches
                    fuzzy_confidence = mapping.confidence * 0.9
                    result.append(
                        (imp, mapping.categories, fuzzy_confidence)
                    )
                    break

        self.logger.debug(
            f"Mapped {len(imports)} imports to {len(result)} categories"
        )
        return result

    def get_categories_for_intent(
        self, imports: List[str], intent: str = "IMPLEMENT"
    ) -> List[str]:
        """
        Get recommended knowledge categories for detected imports.

        Args:
            imports: List of detected imports
            intent: User intent (for future intent-specific filtering)

        Returns:
            List of unique knowledge categories to load
        """
        mapped = self.map_imports(imports)
        categories_set = set()

        for _, categories, _ in mapped:
            categories_set.update(categories)

        return sorted(list(categories_set))

    def get_missing_categories(
        self, imports: List[str], loaded_yamls: List[str]
    ) -> List[str]:
        """
        Identify which tech stack categories are NOT documented.

        Args:
            imports: Detected imports
            loaded_yamls: Already-loaded YAML paths

        Returns:
            List of missing categories
        """
        # Extract categories from loaded YAMLs
        loaded_categories = set()
        for yaml_path in loaded_yamls:
            # Simple heuristic: filename contains category
            yaml_name = Path(yaml_path).stem
            loaded_categories.add(yaml_name)

        # Map imports to expected categories
        expected_categories = set(self.get_categories_for_intent(imports))

        # Find missing
        missing = expected_categories - loaded_categories
        return sorted(list(missing))
