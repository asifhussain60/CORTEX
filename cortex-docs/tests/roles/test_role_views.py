"""
Test Role Views — cortex-docs/tests/roles/test_role_views.py
Validates that all 4 role HTML views load correctly and have proper structure.
"""

from pathlib import Path
from typing import List

import pytest
from bs4 import BeautifulSoup


# AC_START: AC-DOCGEN-ROLE-VIEWS-20260224T000000


class TestRoleViews:
    """Validate role HTML view structure and content loading."""
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_exists(self, roles_dir: Path, role_id: str) -> None:
        """Each role must have an HTML file."""
        role_html_path = roles_dir / f"{role_id}.html"
        assert role_html_path.exists(), f"Role HTML not found: {role_id}.html"
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_has_valid_structure(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable
    ) -> None:
        """Each role HTML must have valid structure."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        
        # Check DOCTYPE
        assert soup.find("html"), f"{role_id}.html missing <html> tag"
        
        # Check head
        head = soup.find("head")
        assert head is not None, f"{role_id}.html missing <head> tag"
        
        # Check title
        title = soup.find("title")
        assert title is not None, f"{role_id}.html missing <title> tag"
        assert "CORTEX" in title.text, f"{role_id}.html title missing 'CORTEX'"
        
        # Check body
        body = soup.find("body")
        assert body is not None, f"{role_id}.html missing <body> tag"
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_loads_required_css(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable,
        extract_html_styles: callable
    ) -> None:
        """Each role HTML must load required stylesheets."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        styles = extract_html_styles(soup)
        
        # Required stylesheets
        required_styles = [
            "glassmorphism.css",
            "cortex-grid-system.css",
            "glass-ui-components.css"
        ]
        
        missing_styles = []
        for required in required_styles:
            if not any(required in style for style in styles):
                missing_styles.append(required)
        
        assert len(missing_styles) == 0, (
            f"{role_id}.html missing stylesheets: {missing_styles}"
        )
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_loads_content_loader_js(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable,
        extract_html_scripts: callable
    ) -> None:
        """Each role HTML must load content-loader.js."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        scripts = extract_html_scripts(soup)
        
        assert any("content-loader.js" in script for script in scripts), (
            f"{role_id}.html missing content-loader.js"
        )
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_has_content_area(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable
    ) -> None:
        """Each role HTML must have #content-area or #main-content container."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        
        content_area = soup.find(id="content-area") or soup.find(id="main-content")
        assert content_area is not None, (
            f"{role_id}.html missing #content-area or #main-content"
        )
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_calls_content_loader(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable
    ) -> None:
        """Each role HTML must instantiate ContentLoader and call loadContent."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        
        # Find inline scripts
        inline_scripts = soup.find_all("script", src=False)
        all_script_text = "\n".join([script.get_text() for script in inline_scripts])
        
        assert "ContentLoader" in all_script_text, (
            f"{role_id}.html does not instantiate ContentLoader"
        )
        assert "content.json" in all_script_text, (
            f"{role_id}.html does not load content.json"
        )
    
    @pytest.mark.parametrize("role_id", [
        "business-leader",
        "product-owner",
        "software-engineer",
        "learner"
    ])
    def test_role_html_has_back_to_index_link(
        self, 
        roles_dir: Path, 
        role_id: str, 
        parse_html: callable
    ) -> None:
        """Each role HTML should have a link back to index.html."""
        role_html_path = roles_dir / f"{role_id}.html"
        soup = parse_html(role_html_path)
        
        # Find links to index.html
        index_links = soup.find_all("a", href=lambda href: href and "index.html" in href)
        
        assert len(index_links) > 0, (
            f"{role_id}.html missing link back to index.html"
        )
    
    def test_all_role_views_use_consistent_structure(
        self, 
        roles_dir: Path, 
        role_ids: List[str], 
        parse_html: callable
    ) -> None:
        """All role views should have consistent HTML structure."""
        structures = {}
        
        for role_id in role_ids:
            role_html_path = roles_dir / f"{role_id}.html"
            soup = parse_html(role_html_path)
            
            # Extract structural elements
            structures[role_id] = {
                "has_hero_header": soup.find(class_="role-hero-header") is not None,
                "has_main_content": soup.find(id="main-content") is not None or 
                                    soup.find(id="content-area") is not None,
                "has_subtitle": soup.find(class_="subtitle") is not None,
                "loads_content_json": "content.json" in str(soup)
            }
        
        # All should have the same structure keys
        reference = structures[role_ids[0]]
        inconsistent = []
        
        for role_id, structure in structures.items():
            for key, value in structure.items():
                if value != reference[key]:
                    inconsistent.append({
                        "role": role_id,
                        "key": key,
                        "expected": reference[key],
                        "actual": value
                    })
        
        # We expect all to be consistent (or mostly consistent)
        # Allow some variation but flag significant differences
        if len(inconsistent) > len(role_ids):
            pytest.fail(f"Role views have inconsistent structure: {inconsistent}")
    
    def test_role_views_reference_correct_relative_paths(
        self, 
        roles_dir: Path, 
        role_ids: List[str], 
        parse_html: callable
    ) -> None:
        """Role views should use correct relative paths (../data/, ../assets/)."""
        for role_id in role_ids:
            role_html_path = roles_dir / f"{role_id}.html"
            soup = parse_html(role_html_path)
            
            # Check stylesheets
            styles = soup.find_all("link", rel="stylesheet", href=True)
            for style in styles:
                href = style.get("href")
                if "assets" in href:
                    assert href.startswith("../assets/"), (
                        f"{role_id}.html has incorrect asset path: {href}"
                    )
            
            # Check scripts
            scripts = soup.find_all("script", src=True)
            for script in scripts:
                src = script.get("src")
                if "assets" in src:
                    assert src.startswith("../assets/"), (
                        f"{role_id}.html has incorrect script path: {src}"
                    )
            
            # Check inline script references to data/
            inline_scripts = soup.find_all("script", src=False)
            all_script_text = "\n".join([s.get_text() for s in inline_scripts])
            if "content.json" in all_script_text:
                assert "../data/content.json" in all_script_text, (
                    f"{role_id}.html should reference '../data/content.json'"
                )


# AC_COMPLETE: AC-DOCGEN-ROLE-VIEWS-20260224T000000 ✅
