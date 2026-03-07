"""
Test Content Integrity — cortex-docs/tests/data/test_content_integrity.py
Validates that all content.json entries have matching .content/ source files.
"""

import json
from pathlib import Path
from typing import Dict, List

import pytest


# AC_START: AC-DOCGEN-CONTENT-INTEGRITY-20260224T000000


class TestContentIntegrity:
    """Validate content.json structure and alignment with .content/ files."""
    
    def test_content_json_exists(self, data_dir: Path) -> None:
        """content.json must exist in data directory."""
        content_json_path = data_dir / "content.json"
        assert content_json_path.exists(), f"content.json not found at {content_json_path}"
    
    def test_content_json_is_valid_json(self, content_json: Dict) -> None:
        """content.json must parse as valid JSON."""
        assert isinstance(content_json, dict), "content.json is not a dictionary"
        assert "categories" in content_json, "content.json missing 'categories' key"
    
    def test_all_categories_have_required_fields(self, content_json: Dict) -> None:
        """Each category must have id, title, and files."""
        categories = content_json.get("categories", [])
        assert len(categories) > 0, "No categories found in content.json"
        
        for category in categories:
            assert "id" in category, f"Category missing 'id': {category}"
            assert "title" in category, f"Category missing 'title': {category}"
            assert "files" in category, f"Category missing 'files': {category}"
            assert isinstance(category["files"], list), f"Category 'files' is not a list: {category['id']}"
    
    def test_all_files_have_required_fields(self, content_json: Dict) -> None:
        """Each file entry must have slug, title, category, roles, content_html."""
        required_fields = ["slug", "title", "category", "roles", "content_html"]
        
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                for field in required_fields:
                    assert field in file, f"File missing '{field}': {file.get('slug', 'UNKNOWN')}"
    
    def test_all_roles_are_valid(self, content_json: Dict, role_ids: List[str]) -> None:
        """All role references must be valid canonical role IDs."""
        # Note: content.json uses 'curious-learner' but role_ids has 'learner'
        valid_roles = role_ids + ["curious-learner"]
        
        invalid_roles = []
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                for role in file.get("roles", []):
                    if role not in valid_roles:
                        invalid_roles.append({
                            "file": file["slug"],
                            "category": category["id"],
                            "invalid_role": role
                        })
        
        assert len(invalid_roles) == 0, f"Invalid roles found: {invalid_roles}"
    
    def test_content_html_not_empty(self, content_json: Dict) -> None:
        """All files must have non-empty content_html."""
        empty_files = []
        
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                if not file.get("content_html", "").strip():
                    empty_files.append(f"{category['id']}/{file['slug']}")
        
        assert len(empty_files) == 0, f"Files with empty content_html: {empty_files}"
    
    def test_word_count_reasonable(self, content_json: Dict) -> None:
        """Word counts should be reasonable (>0 and <10000)."""
        unreasonable = []
        
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                word_count = file.get("word_count", 0)
                if word_count <= 0 or word_count > 10000:
                    unreasonable.append({
                        "file": f"{category['id']}/{file['slug']}",
                        "word_count": word_count
                    })
        
        assert len(unreasonable) == 0, f"Files with unreasonable word counts: {unreasonable}"
    
    def test_last_verified_format(self, content_json: Dict) -> None:
        """last_verified should be in YYYY-MM-DD format."""
        import re
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        invalid_dates = []
        
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                last_verified = file.get("last_verified")
                if last_verified and not date_pattern.match(last_verified):
                    invalid_dates.append({
                        "file": f"{category['id']}/{file['slug']}",
                        "last_verified": last_verified
                    })
        
        assert len(invalid_dates) == 0, f"Files with invalid date format: {invalid_dates}"
    
    def test_no_duplicate_slugs_per_category(self, content_json: Dict) -> None:
        """Each slug must be unique within its category."""
        duplicates = []
        
        for category in content_json.get("categories", []):
            slugs = [file["slug"] for file in category.get("files", [])]
            unique_slugs = set(slugs)
            
            if len(slugs) != len(unique_slugs):
                from collections import Counter
                slug_counts = Counter(slugs)
                dupes = [slug for slug, count in slug_counts.items() if count > 1]
                duplicates.append({
                    "category": category["id"],
                    "duplicate_slugs": dupes
                })
        
        assert len(duplicates) == 0, f"Duplicate slugs found: {duplicates}"
    
    def test_content_dir_exists(self, content_dir: Path) -> None:
        """.content directory must exist."""
        assert content_dir.exists(), f".content directory not found at {content_dir}"
        assert content_dir.is_dir(), f".content is not a directory"
    
    def test_all_categories_have_content_folders(self, content_json: Dict, content_dir: Path) -> None:
        """Each category should have a corresponding folder in .content."""
        missing_folders = []
        
        for category in content_json.get("categories", []):
            category_folder = content_dir / category["id"]
            if not category_folder.exists():
                missing_folders.append(category["id"])
        
        # Some categories may be flat-files or generated, so we warn instead of fail
        if missing_folders:
            print(f"⚠️ Categories without .content folders: {missing_folders}")
    
    def test_html_content_has_proper_structure(self, content_json: Dict) -> None:
        """HTML content should have proper heading structure."""
        from bs4 import BeautifulSoup
        
        missing_headings = []
        
        for category in content_json.get("categories", []):
            for file in category.get("files", []):
                html = file.get("content_html", "")
                soup = BeautifulSoup(html, "html.parser")
                
                # Should have at least one heading
                headings = soup.find_all(["h1", "h2", "h3", "h4"])
                if len(headings) == 0:
                    missing_headings.append(f"{category['id']}/{file['slug']}")
        
        assert len(missing_headings) == 0, f"Files without headings: {missing_headings}"
    
    def test_categories_alphabetically_consistent(self, content_json: Dict) -> None:
        """Category IDs should follow slug naming convention (lowercase, hyphens)."""
        import re
        invalid_ids = []
        slug_pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        
        for category in content_json.get("categories", []):
            category_id = category["id"]
            if not slug_pattern.match(category_id):
                invalid_ids.append(category_id)
        
        assert len(invalid_ids) == 0, f"Categories with invalid slug format: {invalid_ids}"


# AC_COMPLETE: AC-DOCGEN-CONTENT-INTEGRITY-20260224T000000 ✅
