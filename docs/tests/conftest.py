"""
CORTEX Documentation Test Fixtures
Shared fixtures for all cortex-docs test suites
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest
from bs4 import BeautifulSoup


# AC_START: AC-DOCGEN-TEST-FIXTURES-20260224T000000


@pytest.fixture(scope="session")
def docs_root() -> Path:
    """Return the cortex-docs root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def content_dir(docs_root: Path) -> Path:
    """Return the .content source directory."""
    return docs_root / ".content"


@pytest.fixture(scope="session")
def data_dir(docs_root: Path) -> Path:
    """Return the data directory with JSON files."""
    return docs_root / "data"


@pytest.fixture(scope="session")
def roles_dir(docs_root: Path) -> Path:
    """Return the roles HTML directory."""
    return docs_root / "roles"


@pytest.fixture(scope="session")
def learning_dir(docs_root: Path) -> Path:
    """Return the learning paths directory."""
    return docs_root / "learning"


@pytest.fixture(scope="session")
def content_json(data_dir: Path) -> Dict[str, Any]:
    """Load and parse content.json."""
    content_json_path = data_dir / "content.json"
    if not content_json_path.exists():
        pytest.fail(f"content.json not found at {content_json_path}")
    
    with open(content_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def learning_paths_json(data_dir: Path) -> Dict[str, Any]:
    """Load and parse learning-paths.json."""
    learning_json_path = data_dir / "learning-paths.json"
    if not learning_json_path.exists():
        pytest.fail(f"learning-paths.json not found at {learning_json_path}")
    
    with open(learning_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def knowledge_catalog_json(data_dir: Path) -> Dict[str, Any]:
    """Load and parse knowledge-catalog.json."""
    knowledge_json_path = data_dir / "knowledge-catalog.json"
    if not knowledge_json_path.exists():
        pytest.fail(f"knowledge-catalog.json not found at {knowledge_json_path}")
    
    with open(knowledge_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def mcp_tools_json(data_dir: Path) -> Dict[str, Any]:
    """Load and parse mcp-tools.json."""
    mcp_json_path = data_dir / "mcp-tools.json"
    if not mcp_json_path.exists():
        pytest.fail(f"mcp-tools.json not found at {mcp_json_path}")
    
    with open(mcp_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def orchestrators_json(data_dir: Path) -> Dict[str, Any]:
    """Load and parse orchestrators.json."""
    orchestrators_json_path = data_dir / "orchestrators.json"
    if not orchestrators_json_path.exists():
        pytest.fail(f"orchestrators.json not found at {orchestrators_json_path}")
    
    with open(orchestrators_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def parse_html() -> callable:
    """Return a function to parse HTML files with BeautifulSoup."""
    def _parse(html_path: Path) -> BeautifulSoup:
        if not html_path.exists():
            pytest.fail(f"HTML file not found: {html_path}")
        
        with open(html_path, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "html.parser")
    
    return _parse


@pytest.fixture(scope="session")
def role_ids() -> List[str]:
    """Return canonical role IDs."""
    return ["business-leader", "product-owner", "software-engineer", "learner"]


@pytest.fixture(scope="session")
def learning_levels() -> List[str]:
    """Return learning path levels."""
    return ["beginner", "intermediate", "advanced"]


@pytest.fixture
def validate_json_schema() -> callable:
    """Return a function to validate JSON structure."""
    def _validate(data: Dict[str, Any], required_keys: List[str]) -> List[str]:
        """
        Validate that all required keys exist in JSON data.
        
        Returns:
            List of missing keys (empty if valid)
        """
        missing = []
        for key in required_keys:
            if key not in data:
                missing.append(key)
        return missing
    
    return _validate


@pytest.fixture
def extract_html_scripts() -> callable:
    """Return a function to extract script tags from HTML."""
    def _extract(soup: BeautifulSoup) -> List[str]:
        """Extract all script src attributes."""
        scripts = soup.find_all("script", src=True)
        return [script.get("src") for script in scripts]
    
    return _extract


@pytest.fixture
def extract_html_styles() -> callable:
    """Return a function to extract stylesheet links from HTML."""
    def _extract(soup: BeautifulSoup) -> List[str]:
        """Extract all stylesheet href attributes."""
        links = soup.find_all("link", rel="stylesheet", href=True)
        return [link.get("href") for link in links]
    
    return _extract


@pytest.fixture
def get_all_content_files(content_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all file entries from content.json."""
    files = []
    for category in content_json.get("categories", []):
        for file in category.get("files", []):
            files.append({
                "category": category["id"],
                "slug": file["slug"],
                "title": file["title"],
                "roles": file.get("roles", []),
                "content_html": file.get("content_html", ""),
                "word_count": file.get("word_count", 0),
            })
    return files


# AC_COMPLETE: AC-DOCGEN-TEST-FIXTURES-20260224T000000 ✅
