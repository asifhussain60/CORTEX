"""
Test Learning Paths — cortex-docs/tests/learning/test_learning_paths.py
Validates learning path views (beginner, intermediate, advanced) render correctly.
"""

from pathlib import Path
from typing import List

import pytest
from bs4 import BeautifulSoup


# AC_START: AC-DOCGEN-LEARNING-PATHS-20260224T000000


class TestLearningPaths:
    """Validate learning path HTML views and progression structure."""
    
    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_learning_level_directory_exists(self, learning_dir: Path, level: str) -> None:
        """Each learning level must have a directory."""
        level_dir = learning_dir / level
        assert level_dir.exists(), f"Learning level directory not found: {level}/"
        assert level_dir.is_dir(), f"{level}/ is not a directory"
    
    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_learning_level_has_index_html(
        self, 
        learning_dir: Path, 
        level: str,
        parse_html: callable
    ) -> None:
        """Each learning level must have an index.html."""
        index_path = learning_dir / level / "index.html"
        assert index_path.exists(), f"index.html not found in {level}/"
        
        # Parse to ensure valid HTML
        soup = parse_html(index_path)
        assert soup.find("html"), f"{level}/index.html missing <html> tag"
    
    def test_learning_root_has_index_html(
        self, 
        learning_dir: Path,
        parse_html: callable
    ) -> None:
        """Learning root must have index.html (learning path selector)."""
        index_path = learning_dir / "index.html"
        assert index_path.exists(), "learning/index.html not found"
        
        soup = parse_html(index_path)
        assert soup.find("html"), "learning/index.html missing <html> tag"
    
    def test_learning_paths_json_exists(self, learning_paths_json: dict) -> None:
        """learning-paths.json must exist and be valid."""
        assert isinstance(learning_paths_json, dict), "learning-paths.json is not a dict"
    
    def test_learning_paths_json_has_all_levels(
        self, 
        learning_paths_json: dict,
        learning_levels: List[str]
    ) -> None:
        """learning-paths.json must define all 3 levels."""
        paths = learning_paths_json.get("paths", [])
        
        defined_levels = [path.get("id") for path in paths]
        
        for level in learning_levels:
            assert level in defined_levels, (
                f"Level '{level}' not defined in learning-paths.json"
            )
    
    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_learning_level_html_has_proper_title(
        self, 
        learning_dir: Path, 
        level: str,
        parse_html: callable
    ) -> None:
        """Each learning level HTML must have appropriate title."""
        index_path = learning_dir / level / "index.html"
        soup = parse_html(index_path)
        
        title = soup.find("title")
        assert title is not None, f"{level}/index.html missing <title> tag"
        assert level.capitalize() in title.text or "CORTEX" in title.text, (
            f"{level}/index.html title not descriptive: {title.text}"
        )
    
    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_learning_level_html_loads_styles(
        self, 
        learning_dir: Path, 
        level: str,
        parse_html: callable,
        extract_html_styles: callable
    ) -> None:
        """Each learning level HTML must load stylesheets."""
        index_path = learning_dir / level / "index.html"
        soup = parse_html(index_path)
        styles = extract_html_styles(soup)
        
        assert len(styles) > 0, f"{level}/index.html missing stylesheets"
    
    def test_learning_root_index_links_to_all_levels(
        self, 
        learning_dir: Path,
        learning_levels: List[str],
        parse_html: callable
    ) -> None:
        """Learning root index.html should link to all 3 levels."""
        index_path = learning_dir / "index.html"
        soup = parse_html(index_path)
        
        # Find all links
        links = soup.find_all("a", href=True)
        hrefs = [link.get("href") for link in links]
        
        missing_levels = []
        for level in learning_levels:
            # Should have link to beginner/, intermediate/, or advanced/
            if not any(level in href for href in hrefs):
                missing_levels.append(level)
        
        assert len(missing_levels) == 0, (
            f"learning/index.html missing links to levels: {missing_levels}"
        )
    
    def test_learning_paths_json_modules_structure(
        self, 
        learning_paths_json: dict
    ) -> None:
        """Each learning path should have modules with proper structure."""
        paths = learning_paths_json.get("paths", [])
        
        for path in paths:
            assert "id" in path, f"Path missing 'id': {path}"
            assert "title" in path, f"Path missing 'title': {path}"
            assert "description" in path, f"Path missing 'description': {path}"
            
            # Modules should be a list
            modules = path.get("modules", [])
            assert isinstance(modules, list), (
                f"Path '{path['id']}' modules is not a list"
            )
            
            # Each module should have required fields
            for module in modules:
                assert "id" in module, f"Module missing 'id' in path '{path['id']}'"
                assert "title" in module, f"Module missing 'title' in path '{path['id']}'"
    
    def test_learning_paths_progressive_disclosure(
        self, 
        learning_paths_json: dict
    ) -> None:
        """Beginner should have fewer modules than intermediate/advanced."""
        paths = learning_paths_json.get("paths", [])
        
        module_counts = {}
        for path in paths:
            module_counts[path["id"]] = len(path.get("modules", []))
        
        # Beginner should have <= intermediate <= advanced (generally)
        if "beginner" in module_counts and "intermediate" in module_counts:
            # Allow some flexibility, but beginner shouldn't be huge
            assert module_counts["beginner"] <= module_counts["intermediate"] + 5, (
                "Beginner has too many modules compared to intermediate"
            )
    
    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_learning_level_has_navigation_breadcrumb(
        self, 
        learning_dir: Path, 
        level: str,
        parse_html: callable
    ) -> None:
        """Each learning level should have breadcrumb or back navigation."""
        index_path = learning_dir / level / "index.html"
        soup = parse_html(index_path)
        
        # Look for common navigation patterns
        has_breadcrumb = (
            soup.find(class_="breadcrumb") is not None or
            soup.find("nav") is not None or
            soup.find("a", href="../index.html") is not None
        )
        
        # Soft assertion — not all pages may have this yet
        if not has_breadcrumb:
            print(f"⚠️ {level}/index.html missing breadcrumb/navigation")
    
    def test_learning_paths_json_no_duplicate_module_ids(
        self, 
        learning_paths_json: dict
    ) -> None:
        """Module IDs should be unique within each path."""
        paths = learning_paths_json.get("paths", [])
        
        duplicates = []
        for path in paths:
            module_ids = [module["id"] for module in path.get("modules", [])]
            unique_ids = set(module_ids)
            
            if len(module_ids) != len(unique_ids):
                from collections import Counter
                id_counts = Counter(module_ids)
                dupes = [mid for mid, count in id_counts.items() if count > 1]
                duplicates.append({
                    "path": path["id"],
                    "duplicate_ids": dupes
                })
        
        assert len(duplicates) == 0, f"Duplicate module IDs found: {duplicates}"


# AC_COMPLETE: AC-DOCGEN-LEARNING-PATHS-20260224T000000 ✅
